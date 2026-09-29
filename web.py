"""Demo web interface; deploy with one worker because review state is in memory."""

from pathlib import Path
from uuid import uuid4

from flask import Flask, render_template, request

from workflow import WorkflowError, build_graph, propose, review


app = Flask(__name__)
graph = build_graph()
DATA = Path(__file__).resolve().parent / "data"


def duration_angle(weeks):
    """Place a duration on a 0–12+ week semicircle; unknown has no needle."""
    return None if weeks is None else -90 + min(weeks, 12) * 15


@app.get("/health")
def health():
    return "ok", 200


@app.get("/")
def index():
    return render_template("index.html", samples={p: (DATA / f"{p}.txt").read_text(encoding="utf-8")
                                                   for p in ("P001", "P002", "P003")})


@app.post("/propose")
def proposal():
    thread_id = str(uuid4())
    try:
        pending = propose(graph, request.form.get("patient_id", "").strip().upper(),
                          request.form.get("note", ""), thread_id)
        return render_template("review.html", pending=pending, thread_id=thread_id,
                               pain_angle=duration_angle(pending["pain_weeks"]),
                               physio_angle=duration_angle(pending["physio_weeks"]))
    except WorkflowError as exc:
        return render_template("result.html", outcome=f"Error: {exc}"), 400
    except Exception:
        app.logger.exception("Unable to propose decision")
        return render_template("result.html", outcome="Error: Request failed. Check the service logs."), 500


@app.post("/review")
def decision():
    try:
        outcome = review(graph, request.form.get("thread_id", ""), request.form.get("answer", ""))
        return render_template("result.html", outcome=outcome)
    except WorkflowError as exc:
        return render_template("result.html", outcome=f"Error: {exc}"), 400
    except Exception:
        app.logger.exception("Unable to resume review")
        return render_template("result.html", outcome="Error: Review failed. Check the service logs."), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
