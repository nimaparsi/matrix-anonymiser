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


def test_shorter_google_style_api_keys_are_detected():
    text = "Maps key AIzaSyA1b2C3d4E5f6G7h8I9j0K1L2M3N4O must be hidden."
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("AIzaSyA1b2C3d4E5f6G7h8I9j0K1L2M3N4O", "API_KEY") in spans


def test_google_analytics_measurement_ids_are_detected():
    text = "Measurement ID G-ZW9TN4SG5T should be hidden."
    out = anonymize_text(text, ["ANALYTICS_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("G-ZW9TN4SG5T", "ANALYTICS_ID") in spans


def test_region_names_do_not_match_person():
    text = "European Union EU European Economic Area EEA United Kingdom UK United States"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []


def test_script_urls_stay_web_addresses_when_containing_analytics_id():
    text = '<script async src="https://www.googletagmanager.com/gtag/js?id=G-ZW9TN4SG5T"></script>'
    out = anonymize_text(text, ["URL", "ANALYTICS_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ('https://www.googletagmanager.com/gtag/js?id=G-ZW9TN4SG5T', "URL") in spans
    assert all(item["type"] != "ANALYTICS_ID" for item in out["entities"])


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


def test_quoted_full_names_are_detected_as_person():
    text = 'The audit note reads \"John Smith\" and should still anonymize the name.'
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("John Smith", "PERSON") in spans


def test_trailing_quoted_full_names_are_detected_as_person():
    text = 'Compliance refs: Company No AB12CD34; note \"John Smith '
    out = anonymize_text(text, ["PERSON", "COMPANY_REGISTRATION_NUMBER"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("John Smith", "PERSON") in spans


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


def test_city_names_in_from_context_detect_as_address():
    text = "Finance sync reports from Paris and sends alerts from London."
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Paris", "ADDRESS") in spans
    assert ("London", "ADDRESS") in spans


def test_initial_aliases_are_fully_consumed_when_full_name_exists():
    text = 'Wen Chen will join later. Sometimes signs emails as "W. Chen".'
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["anonymized_text"] == '[PERSON_1] will join later. Sometimes signs emails as "[PERSON_1]".'


def test_singapore_multiline_address_block_is_captured_as_one_address():
    text = "office:\nMarina Bay Financial Centre\nTower 3 #15-01\nSingapore 048621"
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    assert out["anonymized_text"] == "office:\n[ADDRESS_1]"


def test_address_lines_merge_with_country_into_single_block():
    text = "28 Bedford Square\nLondon WC1B 3JS\nUK"
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    assert out["anonymized_text"] == "[ADDRESS_1]"


def test_short_numbered_city_address_is_detected():
    text = "120 Holborn, London"
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("120 Holborn, London", "ADDRESS") in spans


def test_tower_block_address_is_detected():
    text = "Centre Tower 2 #18-03, Singapore 018987"
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Centre Tower 2 #18-03, Singapore 018987", "ADDRESS") in spans


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


def test_generic_handles_are_not_detected_without_platform_context():
    text = "Use handle ravi-patel-dev for the repo."
    out = anonymize_text(text, ["USERNAME"], OptionalNlp())
    assert out["entities"] == []


def test_api_keys_do_not_fall_back_to_username_detection():
    text = "OPENAI_KEY=sk-AbCdEfGhIjKlMnOpQrStUv1234"
    out = anonymize_text(text, ["API_KEY", "USERNAME"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("sk-AbCdEfGhIjKlMnOpQrStUv1234", "API_KEY") in spans
    assert all(item["type"] != "USERNAME" for item in out["entities"])


def test_short_github_tokens_are_detected_as_api_keys():
    text = "DATABASE_TOKEN=ghp_s8k2K9kK2kjs88"
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("ghp_s8k2K9kK2kjs88", "API_KEY") in spans


def test_plain_underscore_handles_are_not_detected_without_platform_label():
    text = "Person 6 signs as the username chenwei_dev on GitHub."
    out = anonymize_text(text, ["USERNAME"], OptionalNlp())
    assert out["entities"] == []


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


def test_explicit_secret_labels_are_detected_as_api_keys():
    text = "OPENAI_KEY=sk-AbCdEfGhIjKlMnOpQrStUv1234 AWS_SECRET=AKIA1234567890ABCDEF DATABASE_TOKEN=ghp_s8k2K9kK2kjs88 GITHUB_TOKEN=github_pat_abcdefghijklmnopqrstuvwxyz123456"
    out = anonymize_text(text, ["API_KEY", "USERNAME"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("sk-AbCdEfGhIjKlMnOpQrStUv1234", "API_KEY") in spans
    assert ("AKIA1234567890ABCDEF", "API_KEY") in spans
    assert ("ghp_s8k2K9kK2kjs88", "API_KEY") in spans
    assert ("github_pat_abcdefghijklmnopqrstuvwxyz123456", "API_KEY") in spans
    assert all(item["type"] != "USERNAME" for item in out["entities"])


def test_config_keys_do_not_fall_back_to_username_detection():
    text = "Infrastructure:\nprimary_ip\nbackup_ip\nserver_ip\ndatabase_host\nredis_url"
    out = anonymize_text(text, ["USERNAME"], OptionalNlp())
    assert out["entities"] == []


def test_structural_labels_are_preserved_while_username_value_is_replaced():
    text = "Slack: @daniel.hughes\nInfrastructure: primary_ip\nRepo: github: ravi-patel-dev\nFiles: alex_dev"
    out = anonymize_text(text, ["USERNAME"], OptionalNlp())
    assert out["anonymized_text"] == "Slack: [USERNAME_1]\nInfrastructure: primary_ip\nRepo: github: [USERNAME_2]\nFiles: alex_dev"


def test_platform_qualified_usernames_are_detected():
    text = "GitHub username chenwei_dev\nSlack username @alex.dev"
    out = anonymize_text(text, ["USERNAME"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("chenwei_dev", "USERNAME") in spans
    assert ("@alex.dev", "USERNAME") in spans


def test_compact_platform_handles_are_detected():
    text = "Handles and repos: Slack infra.ops, GitHub javierm"
    out = anonymize_text(text, ["USERNAME"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("infra.ops", "USERNAME") in spans
    assert ("javierm", "USERNAME") in spans


def test_structural_section_labels_remain_unchanged():
    text = "Slack thread from earlier:\nInfrastructure:\nRepositories:\nFiles:\nMonitoring:\nMeeting schedule:"
    out = anonymize_text(text, ["PERSON", "ORG", "USERNAME", "URL", "ADDRESS", "DATE"], OptionalNlp())
    assert out["anonymized_text"] == text
    assert out["entities"] == []


def test_weekday_and_month_abbreviations_do_not_match_person():
    text = "21:39 Mon Jan 5"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []


def test_invoice_numbers_are_detected():
    text = "Invoice #123456 and INV-AB12CD34 were issued."
    out = anonymize_text(text, ["INVOICE_NUMBER"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("invoice #123456", "INVOICE_NUMBER") in spans
    assert ("INV-AB12CD34", "INVOICE_NUMBER") in spans


def test_numeric_invoice_numbers_are_detected():
    text = "Invoice #10291 and INV-88271 were issued."
    out = anonymize_text(text, ["INVOICE_NUMBER"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Invoice #10291", "INVOICE_NUMBER") in spans
    assert ("INV-88271", "INVOICE_NUMBER") in spans


def test_numbered_contract_headings_are_skipped():
    text = "2. Confidential Information\n3. Payment Terms"
    out = anonymize_text(text, ["PERSON", "ORG", "ADDRESS"], OptionalNlp())
    assert out["entities"] == []
    assert out["anonymized_text"] == text


def test_common_legal_nouns_do_not_match_person():
    text = "Payment Agreement Invoice Company Consultant Section Signature Background"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []


def test_address_lines_merge_with_jurisdiction_into_single_block():
    text = "28 Bedford Square\nLondon WC1B 3JS\nEngland and Wales"
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    assert out["anonymized_text"] == "[ADDRESS_1]"


def test_internal_hostnames_are_detected_as_web_addresses():
    text = "server_host=analytics-prod-3.internal.local db_host=postgres-cluster-2.aws.internal"
    out = anonymize_text(text, ["URL"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("analytics-prod-3.internal.local", "URL") in spans
    assert ("postgres-cluster-2.aws.internal", "URL") in spans


def test_connection_strings_are_detected_when_url_detection_is_enabled():
    text = "postgres://admin:adminpass@10.0.0.54:5432/app mysql://root:password@localhost/db mongodb://user:pass@host:27017/db"
    out = anonymize_text(text, ["URL"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("postgres://admin:adminpass@10.0.0.54:5432/app", "CONNECTION_STRING") in spans
    assert ("mysql://root:password@localhost/db", "CONNECTION_STRING") in spans
    assert ("mongodb://user:pass@host:27017/db", "CONNECTION_STRING") in spans


def test_date_time_fragments_do_not_fall_back_to_address():
    text = "Meeting scheduled: Tuesday 14 March 2026 @ 10:30 AM GMT.\nBackup slot: Wednesday 15 March 2026 @ 09:00 UTC."
    out = anonymize_text(text, ["DATE", "ADDRESS"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("14 March 2026", "DATE") in spans
    assert ("15 March 2026", "DATE") in spans
    assert all(item["type"] != "ADDRESS" for item in out["entities"])


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
    text = "Booking ID: AVW-45922159958"
    out = anonymize_text(text, ["BOOKING_REFERENCE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("AVW-45922159958", "BOOKING_REFERENCE") in spans


def test_ticket_reference_is_detected_from_ticket_context():
    text = "Ticket reference CPBBLG9T8LQ"
    out = anonymize_text(text, ["TICKET_REFERENCE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("CPBBLG9T8LQ", "TICKET_REFERENCE") in spans


def test_order_id_is_detected_and_not_as_phone():
    text = "Order ID 45922159958"
    out = anonymize_text(text, ["ORDER_ID", "PHONE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("45922159958", "ORDER_ID") in spans
    assert ("45922159958", "PHONE") not in spans


def test_transaction_id_is_detected():
    text = "Transaction ID 3J7H29F9K2"
    out = anonymize_text(text, ["TRANSACTION_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("3J7H29F9K2", "TRANSACTION_ID") in spans


def test_charge_id_is_detected_as_transaction_id():
    text = "Charge ID 4HG8329SL00921"
    out = anonymize_text(text, ["TRANSACTION_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("4HG8329SL00921", "TRANSACTION_ID") in spans


def test_txn_shorthand_is_detected_as_transaction_id():
    text = "txn 3J7H29F9K2 and alt txn 4HG8329SL00921"
    out = anonymize_text(text, ["TRANSACTION_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("3J7H29F9K2", "TRANSACTION_ID") in spans
    assert ("4HG8329SL00921", "TRANSACTION_ID") in spans


def test_transport_codes_are_not_treated_as_locations():
    text = "Travel from MKC to SOT."
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    assert out["entities"] == []


def test_concatenated_transport_company_detects_as_org():
    text = "Avantiwestcoast cancelled the service."
    out = anonymize_text(text, ["ORG"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Avantiwestcoast", "ORG") in spans


def test_payment_providers_detect_as_org():
    text = "Apple Pay, Google Pay, Visa, Mastercard, PayPal and Stripe processed the payment."
    out = anonymize_text(text, ["ORG"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    for value in ("Apple Pay", "Google Pay", "Visa", "Mastercard", "PayPal", "Stripe"):
        assert (value, "ORG") in spans


def test_payment_provider_phrase_does_not_fall_back_to_person():
    text = "Apple Pay transaction ID ch_1Q2W3E4R5T"
    out = anonymize_text(text, ["PERSON", "ORG", "TRANSACTION_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Apple Pay", "ORG") in spans
    assert ("Apple Pay", "PERSON") not in spans


def test_named_month_dates_capture_full_year():
    text = "Departure date 03 January 2026."
    out = anonymize_text(text, ["DATE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("03 January 2026", "DATE") in spans


def test_coach_letters_do_not_match_people():
    text = "Coach B Gate C Platform D Row E Seat F"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []


def test_person_labels_prefer_person_detection():
    text = "assistant: Claire Dubois\nmanager: Daniel Hughes"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Claire Dubois", "PERSON") in spans
    assert ("Daniel Hughes", "PERSON") in spans


def test_contact_and_director_labels_prefer_person_detection():
    text = "contact: Claire Dubois\ndirector: Sarah Ahmed"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Claire Dubois", "PERSON") in spans
    assert ("Sarah Ahmed", "PERSON") in spans


def test_double_initial_surname_detects_as_person():
    text = "A.B. Smith approved the request."
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("A.B. Smith", "PERSON") in spans


def test_company_registration_numbers_are_detected():
    text = "Company No AB12CD34 GST ZXCV1234 Registration A1B2C3D4"
    out = anonymize_text(text, ["COMPANY_REGISTRATION_NUMBER"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("AB12CD34", "COMPANY_REGISTRATION_NUMBER") in spans
    assert ("ZXCV1234", "COMPANY_REGISTRATION_NUMBER") in spans
    assert ("A1B2C3D4", "COMPANY_REGISTRATION_NUMBER") in spans


def test_company_registration_number_variants_are_detected():
    text = "Company Number 201613701E GST Reg No M90360072X Registration No AB12CD34"
    out = anonymize_text(text, ["COMPANY_REGISTRATION_NUMBER"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("201613701E", "COMPANY_REGISTRATION_NUMBER") in spans
    assert ("M90360072X", "COMPANY_REGISTRATION_NUMBER") in spans
    assert ("AB12CD34", "COMPANY_REGISTRATION_NUMBER") in spans


def test_charge_and_txn_ids_are_detected_as_transaction_ids():
    text = "Gateway returned ch_1Q2W3E4R5T and txn_A1B2C3D4"
    out = anonymize_text(text, ["TRANSACTION_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("ch_1Q2W3E4R5T", "TRANSACTION_ID") in spans
    assert ("txn_A1B2C3D4", "TRANSACTION_ID") in spans


def test_existing_order_id_tokens_are_not_retokenized():
    text = "Existing [Order ID 1] stays as is."
    out = anonymize_text(text, ["ORDER_ID"], OptionalNlp())
    assert out["entities"] == []
    assert out["anonymized_text"] == text


def test_username_detection_skips_file_paths():
    text = "/mnt/data/ravi-patel-dev/reports/output.txt"
    out = anonymize_text(text, ["FILE_PATH", "USERNAME"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("/mnt/data/ravi-patel-dev/reports/output.txt", "FILE_PATH") in spans
    assert ("ravi-patel-dev", "USERNAME") not in spans


def test_masked_cards_remain_unchanged():
    text = "Card **** **** **** 9599 should stay masked."
    out = anonymize_text(text, ["CREDIT_CARD"], OptionalNlp())
    assert out["entities"] == []
    assert out["anonymized_text"] == text


def test_org_detects_after_at_context():
    text = "Person 2 @ DataBridge will join."
    out = anonymize_text(text, ["ORG"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("DataBridge", "ORG") in spans


def test_payment_provider_before_masked_card_remains_visible():
    text = "Visa **** **** **** 9599"
    out = anonymize_text(text, ["ORG"], OptionalNlp())
    assert out["entities"] == []
    assert out["anonymized_text"] == text


def test_payment_provider_before_transaction_id_detects_as_org():
    text = "Stripe transaction ID ch_1Q2W3E4R5T"
    out = anonymize_text(text, ["ORG", "TRANSACTION_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Stripe", "ORG") in spans
    assert ("ch_1Q2W3E4R5T", "TRANSACTION_ID") in spans


def test_duplicate_order_ids_reuse_same_token():
    text = "Order ID 45922159958 appears again: Order ID 45922159958."
    out = anonymize_text(text, ["ORDER_ID"], OptionalNlp())
    assert out["anonymized_text"].count("[ORDER_ID_1]") == 2


def test_duplicate_api_keys_reuse_same_token():
    text = "OPENAI_KEY=sk-AbCdEfGhIjKlMnOpQrStUv1234 and again sk-AbCdEfGhIjKlMnOpQrStUv1234"
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    assert out["anonymized_text"].count("[API_KEY_1]") == 2


def test_pte_ltd_with_punctuation_detects_as_org():
    text = "Trip.com Travel Singapore Pte. Ltd."
    out = anonymize_text(text, ["ORG"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Trip.com Travel Singapore Pte. Ltd", "ORG") in spans
