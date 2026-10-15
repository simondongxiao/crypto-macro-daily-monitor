from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BJT = ZoneInfo("Asia/Shanghai")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--business-date", required=True)
    parser.add_argument("--pages-status", default="SUCCESS")
    parser.add_argument("--pages-url", default="https://simondongxiao.github.io/crypto-macro-daily-monitor/")
    args = parser.parse_args()

    path = Path("audit") / f"daily_review_{args.run_id}.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    notification_path = Path("audit") / f"feishu_daily_{args.business_date}.json"
    notification = json.loads(notification_path.read_text(encoding="utf-8")) if notification_path.exists() else None
    record.update(
        {
            "pages_deployment_status": args.pages_status,
            "pages_url": args.pages_url,
            "notification_status": notification.get("status") if notification else "NOT_FOUND",
            "notification_code": notification.get("code") if notification else None,
            "finalized_at_bjt": datetime.now(BJT).isoformat(),
            "final_status": "SUCCESS" if args.pages_status == "SUCCESS" and notification and notification.get("status") == "ACCEPTED" else "PARTIAL_FAILURE",
        }
    )
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    canonical = Path("audit") / f"daily_review_{args.business_date}.json"
    canonical.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    main()
