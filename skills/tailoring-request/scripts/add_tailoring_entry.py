import datetime
import yaml


def add_tailoring_entry(matrix_yaml_path, log_md_path, swe_id, rationale, risk, mitigation, approver):
    if not approver:
        raise ValueError("A named approver is required before a tailoring entry can be recorded")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row = next((r for r in rows if r["swe_id"] == swe_id), None)
    if row is None:
        raise KeyError(f"{swe_id} not found in requirements mapping matrix")

    today = datetime.date.today().isoformat()
    row["status"] = "tailored-out"
    row["date"] = today

    with open(matrix_yaml_path, "w") as f:
        yaml.dump(rows, f, sort_keys=False)

    try:
        with open(log_md_path) as f:
            existing = f.read()
    except FileNotFoundError:
        existing = "# Tailoring Log\n\n"

    entry = (
        f"## {swe_id} — {today}\n\n"
        f"- **Rationale:** {rationale}\n"
        f"- **Risk:** {risk}\n"
        f"- **Mitigation:** {mitigation}\n"
        f"- **Approved by:** {approver}\n\n"
    )

    with open(log_md_path, "w") as f:
        f.write(existing + entry)
