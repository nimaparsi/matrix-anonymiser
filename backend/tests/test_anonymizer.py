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


def test_heading_phrases_do_not_match_person_entities():
    text = "Coordination Meeting\nInfrastructure Review"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []


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


def test_accented_and_apostrophe_names_are_detected_as_person():
    text = "Prof. Alberto Sánchez met Michael O’Connor."
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Prof. Alberto Sánchez", "PERSON") in spans
    assert ("Michael O’Connor", "PERSON") in spans


def test_person_coreference_reuses_full_name_token():
    text = "Daniel Hughes met Daniel yesterday."
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["anonymized_text"] == "[PERSON_1] met [PERSON_1] yesterday."


def test_initial_alias_reuses_existing_person_token():
    text = "Emily Foster wrote the note. E. Foster approved it."
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["anonymized_text"] == "[PERSON_1] wrote the note. [PERSON_1] approved it."


def test_titled_and_untitled_person_mentions_share_token():
    text = "Dr. Emily Foster joined later. Emily Foster sent the follow-up."
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["anonymized_text"] == "[PERSON_1] joined later. [PERSON_1] sent the follow-up."


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


def test_instituto_prefix_detects_as_org():
    text = "Instituto Verde"
    out = anonymize_text(text, ["PERSON", "ORG"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Instituto Verde", "ORG") in spans
    assert all(item["type"] != "PERSON" for item in out["entities"])


def test_person_names_are_not_reclassified_as_address():
    text = "Please loop in Sarah Ahmed at 28 Bedford Square."
    out = anonymize_text(text, ["PERSON", "ADDRESS"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Sarah Ahmed", "PERSON") in spans
    assert ("28 Bedford Square", "ADDRESS") in spans


def test_postal_codes_do_not_match_phone_numbers():
    text = "Singapore 048621"
    out = anonymize_text(text, ["PHONE"], OptionalNlp())
    assert out["entities"] == []


def test_ipv4_addresses_do_not_match_phone_numbers():
    text = "Server IP 192.168.1.45"
    out = anonymize_text(text, ["PHONE"], OptionalNlp())
    assert out["entities"] == []


def test_ip_addresses_are_detected_as_ip_address_entities():
    text = "Server IP 192.168.1.45 and backup 2001:0db8:85a3:0000:0000:8a2e:0370:7334"
    out = anonymize_text(text, ["IP_ADDRESS"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("192.168.1.45", "IP_ADDRESS") in spans
    assert ("2001:0db8:85a3:0000:0000:8a2e:0370:7334", "IP_ADDRESS") in spans


def test_ten_digit_numbers_can_match_phone_numbers():
    text = "Call 1234567890 tomorrow."
    out = anonymize_text(text, ["PHONE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("1234567890", "PHONE") in spans


def test_phone_regex_captures_full_number():
    text = "Call me on +44 7700 900123 tomorrow."
    out = anonymize_text(text, ["PHONE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("+44 7700 900123", "PHONE") in spans


def test_phone_regex_captures_parenthesized_numbers():
    text = "Backup contact is (020) 7946 0958."
    out = anonymize_text(text, ["PHONE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("(020) 7946 0958", "PHONE") in spans


def test_usernames_are_detected_from_handles_and_platform_lines():
    text = "Slack: @daniel.hughes\nGitHub: ravi-patel-dev"
    out = anonymize_text(text, ["USERNAME"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("@daniel.hughes", "USERNAME") in spans
    assert ("ravi-patel-dev", "USERNAME") in spans


def test_coordinates_are_detected():
    text = "Coordinates: 51.5074° N, 0.1278° W"
    out = anonymize_text(text, ["COORDINATE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("51.5074° N, 0.1278° W", "COORDINATE") in spans


def test_file_paths_are_detected():
    text = "Stored at /mnt/data/projects/climate/reports/2026/"
    out = anonymize_text(text, ["FILE_PATH"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("/mnt/data/projects/climate/reports/2026/", "FILE_PATH") in spans


def test_eu_addresses_are_detected():
    text = "Meet at 14 Rue de Rivoli, 75004 Paris or Calle de Alcalá 42, 28014 Madrid."
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("14 Rue de Rivoli, 75004 Paris", "ADDRESS") in spans
    assert ("Calle de Alcalá 42, 28014 Madrid", "ADDRESS") in spans


def test_address_replacement_preserves_spacing():
    text = "Send it to 21 Bedford Square."
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    assert out["anonymized_text"] == "Send it to [ADDRESS_1]."
