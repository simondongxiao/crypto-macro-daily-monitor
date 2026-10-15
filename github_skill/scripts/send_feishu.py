from __future__ import annotations

import argparse
import json
import os
import tempfile
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
    parser.add_argument("--business-date", default=datetime.now(BJT).date().isoformat())
    parser.add_argument("--dedupe-path", default="audit/feishu_daily.json")
    args = parser.parse_args()
    if not args.webhook:
        raise SystemExit("FEISHU_WEBHOOK is required")

    report = Path(args.report)
    dedupe_path = Path(args.dedupe_path)
    if dedupe_path.name == "feishu_daily.json":
        dedupe_path = dedupe_path.with_name(f"feishu_daily_{args.business_date}.json")
    if dedupe_path.exists():
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
        f"完整 Word 报告与历史 Artifact：{args.run_url or '请打开本次 GitHub Actions 运行记录'}"
    )
    if args.html_url:
        text += f"\n\n手机阅读 HTML：{args.html_url}"
    response = requests.post(
        args.webhook,
        json={"msg_type": "text", "content": {"text": text}},
        timeout=20,
    )
    response.raise_for_status()
    try:
        body = response.json()
    except ValueError as error:
        raise SystemExit(f"Feishu webhook returned non-JSON response: HTTP {response.status_code}") from error
    if not isinstance(body, dict) or "code" not in body:
        raise SystemExit(f"Feishu webhook response missing code: {json.dumps(body, ensure_ascii=False)}")
    if body["code"] != 0:
        raise SystemExit(f"Feishu webhook rejected request: {json.dumps(body, ensure_ascii=False)}")
    dedupe_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=dedupe_path.parent, delete=False) as handle:
        json.dump({"business_date": args.business_date, "status": "ACCEPTED", "code": body["code"], "accepted_at_bjt": datetime.now(BJT).isoformat(), "report": report.name}, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, dedupe_path)
    print(f"Feishu notification accepted: code={body['code']}")


if __name__ == "__main__":
    main()
