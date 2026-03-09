from anonymizer import OptionalNlp, anonymize_text, detect_language, get_language_warning


def test_replacement_order_and_tokens():
    text = "John Doe emailed john@example.com on 2026-03-01."
    out = anonymize_text(text, ["PERSON", "EMAIL", "DATE"], OptionalNlp())

    assert "[EMAIL_1]" in out["anonymized_text"]
    assert "[DATE_1]" in out["anonymized_text"]


def test_api_keys_are_detected():
    text = "Keys: sk-AbCdEfGhIjKlMnOpQrStUv1234 ghp_AbCdEfGhIjKlMnOpQrStUvWxYz0123456789 AIza12345678901234567890123456789012345"
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("sk-AbCdEfGhIjKlMnOpQrStUv1234", "API_KEY") in spans
    assert ("ghp_AbCdEfGhIjKlMnOpQrStUvWxYz0123456789", "API_KEY") in spans
    assert ("AIza12345678901234567890123456789012345", "API_KEY") in spans


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


def test_pronoun_reversal_runs_after_anonymization_for_english_text():
    text = "You can reach him at alex@example.com. His notebook is here. The spare badge is hers."
    out = anonymize_text(text, ["EMAIL"], OptionalNlp(), reverse_pronouns=True)
    assert out["anonymized_text"] == "You can reach her at [EMAIL_1]. Her notebook is here. The spare badge is his."


def test_pronoun_reversal_is_optional():
    text = "You can reach him at alex@example.com."
    out = anonymize_text(text, ["EMAIL"], OptionalNlp(), reverse_pronouns=False)
    assert out["anonymized_text"] == "You can reach him at [EMAIL_1]."


def test_pronoun_reversal_handles_short_english_phrases():
    text = "His office phone"
    out = anonymize_text(text, ["PHONE"], OptionalNlp(), reverse_pronouns=True)
    assert out["anonymized_text"] == "Her office phone"


def test_pronoun_reversal_distinguishes_object_and_possessive_her():
    text = "You can reach her at alex@example.com or on her mobile 1234567890."
    out = anonymize_text(text, ["EMAIL", "PHONE"], OptionalNlp(), reverse_pronouns=True)
    assert out["anonymized_text"] == "You can reach him at [EMAIL_1] or on his mobile [PHONE_1]."


def test_pronoun_reversal_keeps_possessive_her_before_office_nouns():
    text = "Her office address is 28 Bedford Square."
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp(), reverse_pronouns=True)
    assert out["anonymized_text"] == "His office address is [ADDRESS_1]."


def test_pronoun_reversal_skips_non_english_text():
    text = "Hola, puedes llamarlo a alex@example.com. Her agenda stays in English."
    out = anonymize_text(text, ["EMAIL"], OptionalNlp(), reverse_pronouns=True)
    assert out["anonymized_text"] == "Hola, puedes llamarlo a [EMAIL_1]. Her agenda stays in English."


def test_pronoun_reversal_skips_tokens_urls_emails_and_code():
    text = (
        "She said he should email her via support@example.com and review https://example.com/her-guide. "
        "Token [Person 1] stays untouched. Inline `her = value` stays. "
        "```python\nhis = 'sample'\n```"
    )
    out = anonymize_text(text, ["PERSON"], OptionalNlp(), reverse_pronouns=True)
    assert "He said she should email him via support@example.com" in out["anonymized_text"]
    assert "https://example.com/her-guide" in out["anonymized_text"]
    assert "[Person 1]" in out["anonymized_text"]
    assert "`her = value`" in out["anonymized_text"]
    assert "```python\nhis = 'sample'\n```" in out["anonymized_text"]


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


def test_firstname_initial_is_consumed_as_full_person_entity():
    text = "Daniel H. approved the draft."
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["anonymized_text"] == "[PERSON_1] approved the draft."


def test_firstname_initial_and_initial_surname_alias_to_same_person():
    text = "Daniel Hughes met Daniel H. after D. Hughes called."
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["anonymized_text"] == "[PERSON_1] met [PERSON_1] after [PERSON_1] called."


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


def test_three_word_names_are_detected_as_person():
    text = "Sarah Jane Ahmed approved the report."
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Sarah Jane Ahmed", "PERSON") in spans


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


def test_address_numbers_are_not_detected_as_dates():
    text = "25 Marina View"
    out = anonymize_text(text, ["DATE"], OptionalNlp())
    assert out["entities"] == []


def test_address_spans_win_before_dates_on_overlap():
    text = "Meet at 25 Marina View on 12 March 2026."
    out = anonymize_text(text, ["ADDRESS", "DATE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("25 Marina View", "ADDRESS") in spans
    assert ("12 March 2026", "DATE") in spans


def test_initial_aliases_are_fully_consumed_when_full_name_exists():
    text = 'Wen Chen will join later. Sometimes signs emails as "W. Chen".'
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["anonymized_text"] == '[PERSON_1] will join later. Sometimes signs emails as "[PERSON_1]".'


def test_singapore_multiline_address_block_is_captured_as_one_address():
    text = "office:\nMarina Bay Financial Centre\nTower 3 #15-01\nSingapore 048621"
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    assert out["anonymized_text"] == "office:\n[ADDRESS_1]"


def test_supported_date_formats_still_match():
    text = "Dates: 12 March 2026, 14 Mar 2026, 2026-03-12, 12/03/2026, March 12, 2026."
    out = anonymize_text(text, ["DATE"], OptionalNlp())
    spans = {text[item["start"] : item["end"]] for item in out["entities"]}
    assert "12 March 2026" in spans
    assert "14 Mar 2026" in spans
    assert "2026-03-12" in spans
    assert "12/03/2026" in spans
    assert "March 12, 2026" in spans


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


def test_credit_cards_are_detected_with_luhn_validation():
    text = "Valid 4111 1111 1111 1111 invalid 4111 1111 1111 1112"
    out = anonymize_text(text, ["CREDIT_CARD"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("4111 1111 1111 1111", "CREDIT_CARD") in spans
    assert ("4111 1111 1111 1112", "CREDIT_CARD") not in spans


def test_government_ids_are_detected():
    text = "SSN 123-45-6789 and NI QQ123456C"
    out = anonymize_text(text, ["GOVERNMENT_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("123-45-6789", "GOVERNMENT_ID") in spans
    assert ("QQ123456C", "GOVERNMENT_ID") in spans


def test_bank_accounts_are_detected():
    text = "IBAN GB82WEST12345698765432"
    out = anonymize_text(text, ["BANK_ACCOUNT"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("GB82WEST12345698765432", "BANK_ACCOUNT") in spans


def test_private_keys_are_detected():
    text = "-----BEGIN PRIVATE KEY-----\nABCDEF\n-----END PRIVATE KEY-----"
    out = anonymize_text(text, ["PRIVATE_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("-----BEGIN PRIVATE KEY-----\nABCDEF\n-----END PRIVATE KEY-----", "PRIVATE_KEY") in spans


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


def test_plain_hyphenated_usernames_are_detected():
    text = "Use handle ravi-patel-dev for the repo."
    out = anonymize_text(text, ["USERNAME"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("ravi-patel-dev", "USERNAME") in spans


def test_api_keys_do_not_fall_back_to_username_detection():
    text = "OPENAI_KEY=sk-AbCdEfGhIjKlMnOpQrStUv1234"
    out = anonymize_text(text, ["API_KEY", "USERNAME"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("sk-AbCdEfGhIjKlMnOpQrStUv1234", "API_KEY") in spans
    assert all(item["type"] != "USERNAME" for item in out["entities"])


def test_bare_orgs_are_detected_in_from_context():
    text = "Ravi Patel from DataBridge confirmed the plan."
    out = anonymize_text(text, ["PERSON", "ORG"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Ravi Patel", "PERSON") in spans
    assert ("DataBridge", "ORG") in spans


def test_bare_orgs_are_detected_in_parentheses():
    text = "Person 2 (DataBridge) will join later."
    out = anonymize_text(text, ["ORG"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("DataBridge", "ORG") in spans


def test_aws_api_keys_are_detected():
    text = "AWS key AKIA1234567890ABCDEF"
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("AKIA1234567890ABCDEF", "API_KEY") in spans


def test_labeled_generic_secrets_are_detected_as_api_keys():
    text = "OPENAI_KEY=abcDEF1234567890_secretTOKEN API_KEY=ZXCVbnm1234567890_qwerty"
    out = anonymize_text(text, ["API_KEY", "USERNAME"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("abcDEF1234567890_secretTOKEN", "API_KEY") in spans
    assert ("ZXCVbnm1234567890_qwerty", "API_KEY") in spans
    assert all(item["type"] != "USERNAME" for item in out["entities"])


def test_conversational_from_prefers_person_for_names():
    text = "random infra notes from Daniel"
    out = anonymize_text(text, ["PERSON", "ORG"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Daniel", "PERSON") in spans
    assert all(item["type"] != "ORG" for item in out["entities"])


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


def test_windows_file_paths_are_detected():
    text = r"Stored at C:\Users\daniel\Documents\climate\notes.txt"
    out = anonymize_text(text, ["FILE_PATH"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert (r"C:\Users\daniel\Documents\climate\notes.txt", "FILE_PATH") in spans


def test_financial_centre_tower_does_not_match_person():
    text = "Financial Centre Tower"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []


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


def test_booking_reference_is_detected_from_ticket_context():
    text = "Ticket Number CPBBLG9T8LQ"
    out = anonymize_text(text, ["BOOKING_REFERENCE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("CPBBLG9T8LQ", "BOOKING_REFERENCE") in spans


def test_order_id_is_detected_and_not_as_phone():
    text = "Order ID 45922159958"
    out = anonymize_text(text, ["ORDER_ID", "PHONE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("45922159958", "ORDER_ID") in spans
    assert ("45922159958", "PHONE") not in spans


def test_transport_codes_are_not_treated_as_locations():
    text = "Travel from MKC to SOT."
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    assert out["entities"] == []


def test_concatenated_transport_company_detects_as_org():
    text = "Avantiwestcoast cancelled the service."
    out = anonymize_text(text, ["ORG"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Avantiwestcoast", "ORG") in spans


def test_named_month_dates_capture_full_year():
    text = "Departure date 03 January 2026."
    out = anonymize_text(text, ["DATE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("03 January 2026", "DATE") in spans


def test_coach_letters_do_not_match_people():
    text = "Coach B Gate C Platform D Row E Seat F"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []
