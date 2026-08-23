from validate_catalog import validate_catalog


def valid_row(**overrides):
    row = {
        "section": "4.1.5",
        "swe_id": "SWE-053",
        "class_ae_authority": "Center",
        "classes": {"A": True, "B": True, "C": True, "D": True, "E": False, "F": True},
        "class_f_authority": "CIO",
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
    row = valid_row(classes={"A": "yes", "B": True, "C": True, "D": True, "E": False, "F": True})
    errors = validate_catalog([row])
    assert any("classes" in e for e in errors)

def test_duplicate_swe_id_is_reported():
    errors = validate_catalog([valid_row(), valid_row(section="4.1.6")])
    assert any("duplicate" in e.lower() for e in errors)

def test_class_f_authority_may_be_none_when_class_f_does_not_apply():
    row = valid_row(
        classes={"A": True, "B": True, "C": True, "D": True, "E": False, "F": False},
        class_f_authority=None,
    )
    assert validate_catalog([row]) == []

def test_class_ae_authority_must_be_a_non_empty_string():
    assert any("class_ae_authority" in e for e in validate_catalog([valid_row(class_ae_authority="")]))
    assert any("class_ae_authority" in e for e in validate_catalog([valid_row(class_ae_authority=None)]))

def test_class_f_authority_must_be_a_string_or_null():
    errors = validate_catalog([valid_row(class_f_authority=7)])
    assert any("class_f_authority" in e for e in errors)

def test_class_f_authority_without_a_class_f_mark_is_reported():
    """The column-mismapping regression: an authority read out of the wrong column."""
    row = valid_row(
        classes={"A": True, "B": True, "C": True, "D": True, "E": False, "F": False},
        class_f_authority="CIO",
    )
    errors = validate_catalog([row])
    assert any("classes.F is false" in e for e in errors)

def test_class_f_mark_without_an_authority_is_accepted():
    """NPR 7150.2D §3.2.1 / SWE-015 genuinely has this shape in Appendix C."""
    row = valid_row(
        section="3.2.1", swe_id="SWE-015",
        classes={"A": True, "B": True, "C": True, "D": True, "E": False, "F": True},
        class_f_authority=None,
    )
    assert validate_catalog([row]) == []
