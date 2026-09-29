"""Fictional patient and rule data, exposed only through MCP tools."""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP


DATA = Path(__file__).resolve().parent / "data"
mcp = FastMCP("Synthetic MRI Prior Authorization", log_level="ERROR")


@mcp.tool()
def get_patient(patient_id: str) -> dict:
    """Return a fictional patient's name and plan status, or an unknown-ID error."""
    patients = json.loads((DATA / "patients.json").read_text(encoding="utf-8"))
    patient = patients.get(patient_id)
    if patient is None:
        return {"error": f"Unknown patient ID: {patient_id}"}
    return {"patient_id": patient_id, "name": patient["name"], "plan_active": patient["plan_active"]}


@mcp.tool()
def get_rule() -> dict:
    """Return the fictional rule, evaluation order, and both six-week thresholds."""
    return json.loads((DATA / "rule.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    mcp.run(transport="stdio")
