"""Run with `python test.py`; tests cross the real stdio MCP boundary."""

import os
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from workflow import WorkflowError, build_graph, propose, read_with_gemini, review


DATA = Path(__file__).resolve().parent / "data"
CASES = {
    "P001": ({"pain_weeks": 10, "physio_weeks": 8}, "Approve"),
    "P002": ({"pain_weeks": 12, "physio_weeks": 8}, "Deny"),
    "P003": ({"pain_weeks": 9, "physio_weeks": None}, "Need more information"),
}


def run_case(patient_id, facts, expected):
    graph = build_graph(reader=lambda note: facts)
    thread = str(uuid4())
    pending = propose(graph, patient_id, (DATA / f"{patient_id}.txt").read_text(encoding="utf-8"), thread)
    outcome = review(graph, thread, "yes")  # Simulates the human response.
    assert pending["recommendation"] == expected
    assert outcome.startswith(f"{expected}:")


def run_extra():
    graph = build_graph(reader=lambda note: {"pain_weeks": 6, "physio_weeks": 6})
    thread = str(uuid4())
    pending = propose(graph, "P001", "Exactly six weeks for both.", thread)
    assert pending["recommendation"] == "Approve"
    assert review(graph, thread, "no") == "Decision rejected by reviewer"

    graph = build_graph(reader=lambda note: {"pain_weeks": None, "physio_weeks": 0})
    thread = str(uuid4())
    assert propose(graph, "P001", "No physiotherapy was tried.", thread)["recommendation"] == "Deny"
    assert review(graph, thread, "yes").startswith("Deny:")

    graph = build_graph(reader=lambda note: {"pain_weeks": 8, "physio_weeks": 8})
    try:
        propose(graph, "UNKNOWN", "A fictional note.", str(uuid4()))
    except WorkflowError as exc:
        assert "Unknown patient ID" in str(exc)
    else:
        raise AssertionError("Unknown ID produced a recommendation")


def run_gemini_reader_check():
    original = os.environ.get("GEMINI_API_KEY")
    try:
        os.environ["GEMINI_API_KEY"] = "replace-with-your-gemini-api-key"
        try:
            read_with_gemini("A fictional note")
        except WorkflowError as exc:
            assert "placeholder" in str(exc)
        else:
            raise AssertionError("Example key was sent to Gemini")

        os.environ["GEMINI_API_KEY"] = "test-only-never-sent"
        with patch("workflow.genai.Client") as factory:
            factory.return_value.__enter__.return_value.models.generate_content.return_value.text = (
                '{"pain_weeks": 10, "physio_weeks": 8}'
            )
            assert read_with_gemini("Back pain for 10 weeks; physiotherapy for 8 weeks.") == {
                "pain_weeks": 10, "physio_weeks": 8
            }
            assert factory.return_value.__enter__.return_value.models.generate_content.call_count == 1
    finally:
        if original is None:
            os.environ.pop("GEMINI_API_KEY", None)
        else:
            os.environ["GEMINI_API_KEY"] = original


def main():
    failures = 0
    for patient_id, (facts, expected) in CASES.items():
        try:
            run_case(patient_id, facts, expected)
            print(f"{patient_id}: PASS ({expected})")
        except Exception as exc:
            print(f"{patient_id}: FAIL ({exc})")
            failures += 1
    try:
        run_extra()
        print("Boundary, rejection, unknown ID: PASS")
    except Exception as exc:
        print(f"Boundary, rejection, unknown ID: FAIL ({exc})")
        failures += 1
    try:
        run_gemini_reader_check()
        print("Gemini reader and placeholder key: PASS")
    except Exception as exc:
        print(f"Gemini reader and placeholder key: FAIL ({exc})")
        failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
