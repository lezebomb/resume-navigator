from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.analysis.pipeline import analyze_resume_against_jd


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic local resume analysis.")
    parser.add_argument("--resume", required=True, help="Path to a PDF or DOCX resume file.")
    parser.add_argument("--jd-file", help="Path to a text file that contains the target JD.")
    parser.add_argument("--jd-text", help="Raw JD text passed directly on the command line.")
    parser.add_argument("--output", help="Optional path to write the JSON result.")
    return parser


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = build_argument_parser().parse_args()
    resume_path = Path(args.resume)
    if not resume_path.exists():
        raise SystemExit(f"Resume file does not exist: {resume_path}")

    if args.jd_file:
        jd_text = Path(args.jd_file).read_text(encoding="utf-8")
    elif args.jd_text:
        jd_text = args.jd_text
    else:
        raise SystemExit("Either --jd-file or --jd-text must be provided.")

    result = analyze_resume_against_jd(
        filename=resume_path.name,
        file_bytes=resume_path.read_bytes(),
        jd_text=jd_text,
    )
    payload = result.model_dump()
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
        print(f"Saved analysis result to: {args.output}")
    else:
        try:
            print(rendered)
        except UnicodeEncodeError:
            print(rendered.encode("utf-8", errors="replace").decode("utf-8"))


if __name__ == "__main__":
    main()
