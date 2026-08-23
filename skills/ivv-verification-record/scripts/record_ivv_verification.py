import datetime
import yaml

DEFAULT_HEADER = "# IV&V Verification Record (NASA-STD-8739.8B §4.4.2)\n\n"


def record_ivv_verification(matrix_yaml_path, record_md_path, ivv_ids, fields, evidence):
    if not ivv_ids:
        raise ValueError("at least one ivv_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["ivv_id"]: r for r in rows}
    missing = [i for i in ivv_ids if i not in row_by_id]
    if missing:
        raise KeyError(f"unknown ivv_id(s) in IV&V verification matrix: {', '.join(missing)}")

    for ivv_id in ivv_ids:
        if row_by_id[ivv_id]["status"] == "tailored-out":
            raise ValueError(
                f"{ivv_id} is already tailored-out — see tailoring-log.md; do not mark it "
                f"satisfied without first reviewing/reversing that tailoring entry"
            )

    today = datetime.date.today().isoformat()
    for ivv_id in ivv_ids:
        row_by_id[ivv_id]["status"] = "satisfied"
        row_by_id[ivv_id]["evidence"] = evidence
        row_by_id[ivv_id]["date"] = today

    with open(matrix_yaml_path, "w") as f:
        yaml.dump(rows, f, sort_keys=False)

    try:
        with open(record_md_path) as f:
            existing = f.read()
    except FileNotFoundError:
        existing = DEFAULT_HEADER

    lines = [f"## Recorded {today}\n"]
    for key, value in fields.items():
        lines.append(f"- **{key}:** {value}")
    lines.append(f"- **Satisfies:** {', '.join(ivv_ids)}")
    lines.append(f"- **Evidence:** {evidence}\n")
    entry = "\n".join(lines) + "\n"

    with open(record_md_path, "w") as f:
        f.write(existing + entry)
