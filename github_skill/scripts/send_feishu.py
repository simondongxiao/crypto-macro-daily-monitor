from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from docx import Document

BJT = ZoneInfo("Asia/Shanghai")


def extract_summary(path: Path) -> str:
    doc = Document(path)
    paragraphs = [" ".join(p.text.split()) for p in doc.paragraphs if p.text.strip()]
    conclusion = ""
    for i, value in enumerate(paragraphs):
        if value == "今日结论" and i + 1 < len(paragraphs):
            conclusion = paragraphs[i + 1]
            break
    return conclusion[:1800] if conclusion else "日报已生成，请打开 GitHub Actions Artifact 查看完整 Word 文件。"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--webhook", default=os.environ.get("FEISHU_WEBHOOK"))
    parser.add_argument("--report", required=True)
    parser.add_argument("--run-url", default="")
    parser.add_argument("--html-url", default="")
    parser.add_argument("--report-url", default="")
    parser.add_argument("--force", action="store_true", help="send even when this business date was already accepted")
    parser.add_argument("--business-date", default=datetime.now(BJT).date().isoformat())
    parser.add_argument("--dedupe-path", default="audit/feishu_daily.json")
    args = parser.parse_args()
    if not args.webhook:
        raise SystemExit("FEISHU_WEBHOOK is required")

    report = Path(args.report)
    dedupe_path = Path(args.dedupe_path)
    if dedupe_path.name == "feishu_daily.json":
        dedupe_path = dedupe_path.with_name(f"feishu_daily_{args.business_date}.json")
    if dedupe_path.exists() and not args.force:
        try:
            previous = json.loads(dedupe_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = {}
        if previous.get("status") == "ACCEPTED":
            print(f"Feishu notification already accepted for business_date={args.business_date}; duplicate skipped")
            return
    text = (
        f"Crypto日报已生成\n"
        f"文件：{report.name}\n\n"
        f"今日结论：{extract_summary(report)}\n\n"
        f"手机阅读 HTML：{args.html_url or '链接未提供'}\n"
        f"下载 Word 文件：{args.report_url or '链接未提供'}\n"
        f"本次运行审计：{args.run_url or '请打开本次 GitHub Actions 运行记录'}"
    )
    payload = {"msg_type": "text", "content": {"text": text}}
    body: dict[str, object] | None = None
    last_error = ""
    for attempt in range(1, 4):
        try:
            response = requests.post(args.webhook, json=payload, timeout=20)
            response.raise_for_status()
            try:
                parsed = response.json()
            except ValueError as error:
                raise RuntimeError(f"non-JSON response: HTTP {response.status_code}") from error
            if not isinstance(parsed, dict) or "code" not in parsed:
                raise RuntimeError(f"response missing code: {json.dumps(parsed, ensure_ascii=False)}")
            if parsed["code"] != 0:
                raise RuntimeError(f"business rejection: {json.dumps(parsed, ensure_ascii=False)}")
            body = parsed
            print(f"Feishu webhook accepted: http={response.status_code}, code={parsed['code']}, attempt={attempt}")
            break
        except (requests.RequestException, RuntimeError) as error:
            last_error = str(error)
            print(f"Feishu webhook attempt {attempt}/3 failed: {last_error}")
            if attempt < 3:
                time.sleep(attempt * 3)
    if body is None:
        raise SystemExit(f"Feishu notification failed after 3 attempts: {last_error}")
    dedupe_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=dedupe_path.parent, delete=False) as handle:
        json.dump({"business_date": args.business_date, "status": "ACCEPTED", "code": body["code"], "accepted_at_bjt": datetime.now(BJT).isoformat(), "report": report.name, "html_url": args.html_url, "report_url": args.report_url, "run_url": args.run_url}, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, dedupe_path)
    print(f"Feishu notification accepted: code={body['code']}")


if __name__ == "__main__":
    main()
