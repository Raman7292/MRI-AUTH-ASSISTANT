"""Command-line review interface."""

import argparse
import sys
from pathlib import Path
from uuid import uuid4

from workflow import WorkflowError, build_graph, propose, review


def main() -> int:
    parser = argparse.ArgumentParser(description="Synthetic MRI authorization assistant")
    parser.add_argument("patient_id", help="Fictional patient ID, e.g. P001")
    parser.add_argument("note_file", type=Path, help="Plain-text clinical note file")
    args = parser.parse_args()
    try:
        note = args.note_file.read_text(encoding="utf-8")
        graph = build_graph()
        thread_id = str(uuid4())
        proposal = propose(graph, args.patient_id, note, thread_id)
        print(f'Proposed: {proposal["recommendation"]} — {proposal["reason"]}')
        while True:
            answer = input("Accept this recommendation? (yes/no) ").strip().lower()
            if answer in {"yes", "no"}:
                break
        print(review(graph, thread_id, answer))
        return 0
    except (OSError, WorkflowError, EOFError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

