from anonymizer import OptionalNlp, anonymize_text, detect_language, get_language_warning


def test_replacement_order_and_tokens():
    text = "John Doe emailed john@example.com on 2026-03-01."
    out = anonymize_text(text, ["PERSON", "EMAIL", "DATE"], OptionalNlp())

    assert "[EMAIL_1]" in out["anonymized_text"]
    assert "[DATE_1]" in out["anonymized_text"]


def test_cta_detection_for_immigration_keywords():
    text = "My UKVI visa update includes UAN12345678 details."
    out = anonymize_text(text, ["EMAIL", "PHONE", "DATE"], OptionalNlp())
    assert out["cta_visaprep"] is True


def test_detect_language_flags_spanish_text():
    text = "Hola, me llamo Carlos y vivo en Madrid con mi familia."
    assert detect_language(text) == "es"


def test_get_language_warning_skips_english_text():
    details = get_language_warning("Hello, this is an English sentence with some details.")
    assert details["warning"] is None
    assert details["detected_language"] == "en"


def test_org_suffixes_detect_as_org_and_not_person():
    text = "Horizon Analytics Ltd worked with DataBridge Consulting Ltd and Orbit Systems."
    out = anonymize_text(text, ["PERSON", "ORG"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}

    assert ("Horizon Analytics Ltd", "ORG") in spans
    assert ("DataBridge Consulting Ltd", "ORG") in spans
    assert ("Orbit Systems", "ORG") in spans
    assert all(item["type"] != "PERSON" for item in out["entities"])


def test_org_suffixes_do_not_fall_back_to_person_only_detection():
    text = "Horizon Analytics Ltd"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []


def test_address_grouping_keeps_street_spans_as_location():
    text = "Send it to 12 Bedford Square before heading to Via Roma."
    out = anonymize_text(text, ["PERSON", "ADDRESS"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}

    assert ("12 Bedford Square", "ADDRESS") in spans
    assert ("Via Roma", "ADDRESS") in spans
    assert all(item["type"] != "PERSON" for item in out["entities"])


def test_street_place_names_do_not_fall_back_to_person_only_detection():
    text = "Raffles Place"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []


def test_hyphenated_names_are_detected_as_person():
    text = "Jean-Pierre Martin approved the report."
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Jean-Pierre Martin", "PERSON") in spans


def test_hyphenated_titled_names_are_detected_as_person():
    text = "Dr. Jean-Pierre Martin approved the report."
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Dr. Jean-Pierre Martin", "PERSON") in spans


def test_initial_based_names_are_detected_as_person():
    text = "W. Chen approved the report."
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("W. Chen", "PERSON") in spans


def test_department_phrases_are_ignored_when_org_and_person_are_enabled():
    text = "Department of Environmental Science reviewed the case."
    out = anonymize_text(text, ["PERSON", "ORG"], OptionalNlp())
    assert out["entities"] == []


def test_department_phrases_do_not_fall_back_to_person_only_detection():
    text = "Department of Environmental Science"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []


def test_faculty_phrases_do_not_fall_back_to_person_only_detection():
    text = "Faculty of Environmental Sciences"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []


def test_centre_for_phrases_are_ignored():
    text = "Centre for Applied Linguistics"
    out = anonymize_text(text, ["PERSON", "ORG"], OptionalNlp())
    assert out["entities"] == []


def test_postal_codes_do_not_match_phone_numbers():
    text = "Singapore 048621"
    out = anonymize_text(text, ["PHONE"], OptionalNlp())
    assert out["entities"] == []


def test_ten_digit_numbers_can_match_phone_numbers():
    text = "Call 1234567890 tomorrow."
    out = anonymize_text(text, ["PHONE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("1234567890", "PHONE") in spans
