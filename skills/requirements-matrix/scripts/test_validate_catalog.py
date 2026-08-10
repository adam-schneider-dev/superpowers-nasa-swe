from validate_catalog import validate_catalog

def valid_row(**overrides):
    row = {
        "section": "4.1.5",
        "swe_id": "SWE-053",
        "responsible_role": "Center",
        "classes": {"A": True, "B": True, "C": True, "D": True, "E": False, "F": False},
        "technical_authority": "CIO",
        "ta_required": True,
    }
    row.update(overrides)
    return row

def test_valid_catalog_has_no_errors():
    assert validate_catalog([valid_row()]) == []

def test_missing_required_field_is_reported():
    row = valid_row()
    del row["swe_id"]
    errors = validate_catalog([row])
    assert any("swe_id" in e for e in errors)

def test_bad_swe_id_format_is_reported():
    errors = validate_catalog([valid_row(swe_id="053")])
    assert any("SWE-" in e and "format" in e for e in errors)

def test_classes_must_have_exactly_six_keys():
    row = valid_row(classes={"A": True, "B": True})
    errors = validate_catalog([row])
    assert any("classes" in e for e in errors)

def test_classes_values_must_be_bool():
    row = valid_row(classes={"A": "yes", "B": True, "C": True, "D": True, "E": False, "F": False})
    errors = validate_catalog([row])
    assert any("classes" in e for e in errors)

def test_duplicate_swe_id_is_reported():
    errors = validate_catalog([valid_row(), valid_row(section="4.1.6")])
    assert any("duplicate" in e.lower() for e in errors)

def test_technical_authority_may_be_none():
    row = valid_row(technical_authority=None, ta_required=False)
    assert validate_catalog([row]) == []
