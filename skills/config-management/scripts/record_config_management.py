import datetime
import yaml

DEFAULT_HEADER = "# Software Configuration Management (NPR 7150.2D §5.1)\n\n"


def record_config_management(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [s for s in swe_ids if s not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in requirements mapping matrix: {', '.join(missing)}")

    for swe_id in swe_ids:
        if row_by_id[swe_id]["status"] == "tailored-out":
            raise ValueError(
                f"{swe_id} is already tailored-out — see tailoring-log.md; do not mark it "
                f"satisfied without first reviewing/reversing that tailoring entry"
            )

    today = datetime.date.today().isoformat()
    for swe_id in swe_ids:
        row_by_id[swe_id]["status"] = "satisfied"
        row_by_id[swe_id]["evidence"] = evidence
        row_by_id[swe_id]["date"] = today

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
    lines.append(f"- **Satisfies:** {', '.join(swe_ids)}")
    lines.append(f"- **Evidence:** {evidence}\n")
    entry = "\n".join(lines) + "\n"

    with open(record_md_path, "w") as f:
        f.write(existing + entry)
