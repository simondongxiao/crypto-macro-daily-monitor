from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests

BJT = ZoneInfo("Asia/Shanghai")
UTC = timezone.utc
REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]
API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}


def api(method: str, path: str, **kwargs: Any) -> requests.Response:
    response = requests.request(method, f"{API}/repos/{REPO}/{path}", headers=HEADERS, timeout=20, **kwargs)
    response.raise_for_status()
    return response


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def runs(workflow: str, event: str | None = None) -> list[dict[str, Any]]:
    params = {"per_page": 100}
    if event:
        params["event"] = event
    return api("GET", f"actions/workflows/{workflow}/runs", params=params).json().get("workflow_runs", [])


def current_business_audit(date_text: str) -> dict[str, Any] | None:
    try:
        response = api("GET", f"contents/audit/daily_review_{date_text}.json", params={"ref": "main"})
        return json.loads(base64.b64decode(response.json()["content"]))
    except requests.RequestException:
        return None


def current_business_notification(date_text: str) -> dict[str, Any] | None:
    try:
        response = api("GET", f"contents/audit/feishu_daily_{date_text}.json", params={"ref": "main"})
        return json.loads(base64.b64decode(response.json()["content"]))
    except requests.RequestException:
        return None


def expected_daily_windows(now: datetime) -> list[datetime]:
    return [
        datetime.combine((now.date() - timedelta(days=offset + 1)), datetime.min.time(), tzinfo=UTC).replace(hour=21, minute=3)
        for offset in range(7)
    ]


def expected_monitor_windows(now: datetime) -> list[datetime]:
    end = now.astimezone(UTC).replace(second=0, microsecond=0)
    start = end - timedelta(days=7)
    cursor = start.replace(minute=(start.minute // 10) * 10)
    result = []
    while cursor <= end:
        result.append(cursor)
        cursor += timedelta(minutes=10)
    return result


def schedule_stats(workflow: str, expected: list[datetime], now: datetime) -> dict[str, Any]:
    actual = []
    for run in runs(workflow, "schedule"):
        created = parse_time(run["created_at"])
        if now.astimezone(UTC) - timedelta(days=7) <= created <= now.astimezone(UTC) + timedelta(minutes=5):
            actual.append({
                "run_id": run["id"],
                "created_at": run["created_at"],
                "run_started_at": run.get("run_started_at"),
                "completed_at": run.get("updated_at"),
                "status": run.get("status"),
                "conclusion": run.get("conclusion"),
            })
    delays = []
    for item in actual:
        created = parse_time(item["created_at"])
        nearest = min(expected, key=lambda point: abs((created - point).total_seconds())) if expected else created
        delay = (created - nearest).total_seconds() / 60
        item["nearest_theoretical_utc"] = nearest.isoformat()
        item["delay_minutes"] = round(delay, 2)
        item["queue_minutes"] = round(max(0, (parse_time(item["run_started_at"]) - created).total_seconds() / 60), 2) if item.get("run_started_at") else None
        item["execution_minutes"] = round(max(0, (parse_time(item["completed_at"]) - parse_time(item["run_started_at"])).total_seconds() / 60), 2) if item.get("completed_at") and item.get("run_started_at") else None
        delays.append(delay)
    return {
        "workflow": workflow,
        "theoretical_windows": len(expected),
        "actual_scheduled_runs": len(actual),
        "missing_windows_estimate": max(0, len(expected) - len(actual)),
        "delayed_runs_over_2m": sum(delay > 2 for delay in delays),
        "max_delay_minutes": round(max(delays), 2) if delays else None,
        "runs": actual,
        "note": "A scheduled run is matched to the nearest theoretical window; GitHub does not expose a separate scheduler-enqueue timestamp.",
    }


def dispatch_daily() -> dict[str, Any]:
    response = api("POST", "actions/workflows/daily_review_cloud.yml/dispatches", json={"ref": "main"})
    return {"status": "COMPENSATION_DISPATCHED", "http_status": response.status_code}


def notify_watchdog_failure(business_date: str, actions: list[dict[str, Any]]) -> dict[str, Any] | None:
    webhook = os.environ.get("FEISHU_WEBHOOK_URL")
    failed = [action for action in actions if action.get("status") in {"COMPENSATION_FAILED", "RUN_FAILED"}]
    if not failed:
        return None
    if not webhook:
        return {"status": "NOTIFICATION_FAILED", "reason": "WEBHOOK_MISSING"}
    response = requests.post(
        webhook,
        json={"msg_type": "text", "content": {"text": f"Crypto 日报调度补偿失败\n业务日期：{business_date}\n详情：{json.dumps(failed, ensure_ascii=False)}"}},
        timeout=20,
    )
    response.raise_for_status()
    body = response.json()
    if not isinstance(body, dict) or body.get("code") != 0:
        raise RuntimeError(f"Feishu watchdog failure alert rejected: {body}")
    return {"status": "SENT_AND_ACCEPTED", "code": body["code"]}


def main() -> None:
    now = datetime.now(BJT)
    business_date = now.date().isoformat()
    daily_runs = [run for run in runs("daily_review_cloud.yml") if parse_time(run["created_at"]).astimezone(BJT).date().isoformat() == business_date]
    audit = current_business_audit(business_date)
    notification = current_business_notification(business_date)
    active = [run for run in daily_runs if run.get("status") in {"queued", "in_progress"}]
    actions: list[dict[str, Any]] = []
    if audit and audit.get("generation_status") == "SUCCESS" and notification and notification.get("status") == "ACCEPTED":
        actions.append({"status": "ALREADY_COMPLETE", "report": audit.get("report")})
    elif active:
        actions.append({"status": "WAITING_FOR_CURRENT_RUN", "run_ids": [run["id"] for run in active]})
    else:
        if audit and audit.get("generation_status") == "SUCCESS" and not notification:
            actions.append({"status": "NOTIFICATION_COMPENSATION_REQUIRED", "report": audit.get("report")})
        failed_runs = [run for run in daily_runs if run.get("status") == "completed" and run.get("conclusion") not in {"success", "skipped", "cancelled"}]
        if failed_runs:
            actions.append({"status": "RUN_FAILED", "run_ids": [run["id"] for run in failed_runs], "conclusions": [run.get("conclusion") for run in failed_runs]})
        try:
            actions.append(dispatch_daily())
        except Exception as error:
            actions.append({"status": "COMPENSATION_FAILED", "error": str(error)[:500]})

    stats = {
        "generated_at_bjt": now.isoformat(),
        "business_date": business_date,
        "daily_review": schedule_stats("daily_review_cloud.yml", expected_daily_windows(now), now),
        "price_monitor": schedule_stats("price_monitor.yml", expected_monitor_windows(now), now),
        "actions": actions,
        "dedupe_rule": "One successful daily_review audit per Asia/Shanghai business date; cloud_run skips subsequent successful rebuilds.",
    }
    stats["failure_notification"] = notify_watchdog_failure(business_date, actions)
    output = Path("audit") / f"schedule_health_{business_date}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))
    if any(action.get("status") == "COMPENSATION_FAILED" for action in actions):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
