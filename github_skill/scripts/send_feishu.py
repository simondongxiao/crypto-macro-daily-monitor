from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import requests
from docx import Document


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
    args = parser.parse_args()
    if not args.webhook:
        raise SystemExit("FEISHU_WEBHOOK is required")

    report = Path(args.report)
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
    print(f"Feishu notification accepted: code={body['code']}")


if __name__ == "__main__":
    main()
