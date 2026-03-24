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


def test_lowercase_labeled_secrets_are_detected_as_api_keys():
    text = "Service API key: api_key=prod_9fH3mQ7xV2pL5rT8kN1dW4cY Webhook secret: access_token=svc_7aL2nP9xR4mK6vT1qD8eY5"
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("prod_9fH3mQ7xV2pL5rT8kN1dW4cY", "API_KEY") in spans
    assert ("svc_7aL2nP9xR4mK6vT1qD8eY5", "API_KEY") in spans


def test_password_phrase_value_is_detected_as_api_key():
    text = "Assistant note: my password is dfdsfdsfw4r"
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("dfdsfdsfw4r", "API_KEY") in spans


def test_password_phrase_with_symbols_is_captured_fully():
    text = "HEre's my password baby adsdankj3jkkj232kb4k23hn@£@£@@££££$$$"
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("adsdankj3jkkj232kb4k23hn@£@£@@££££$$$", "API_KEY") in spans
    assert out["anonymized_text"] == "HEre's my password baby [API_KEY_1]"


def test_password_trailing_phrase_value_is_detected_as_api_key():
    text = "gfdgg54rfde is my password"
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("gfdgg54rfde", "API_KEY") in spans
    assert out["anonymized_text"] == "[API_KEY_1] is my password"


def test_password_policy_phrase_is_not_misdetected_as_secret():
    text = "Please review the password policy before rollout."
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    assert out["entities"] == []


def test_standalone_password_like_token_is_detected_as_api_key():
    text = "NHS referral note\nFollow-up date: 29 March 2026\nsadasdderwr3223"
    out = anonymize_text(text, ["API_KEY", "DATE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("sadasdderwr3223", "API_KEY") in spans
    assert ("29 March 2026", "DATE") in spans


def test_jwt_tokens_are_detected_as_api_keys():
    text = "JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.signatureExampleTokenValue"
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.signatureExampleTokenValue", "API_KEY") in spans


def test_jwt_is_not_misclassified_as_url():
    text = "JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.signatureExampleTokenValue"
    out = anonymize_text(text, ["API_KEY", "URL"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.signatureExampleTokenValue", "API_KEY") in spans
    assert ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.signatureExampleTokenValue", "URL") not in spans


def test_ssh_public_keys_are_detected_as_api_keys():
    text = "GitHub SSH key: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFl2dD9pQm7rX4uN8wE1yT5kL3cB6vR2pH0sJ9n alice@contoso-dev"
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFl2dD9pQm7rX4uN8wE1yT5kL3cB6vR2pH0sJ9n alice@contoso-dev", "API_KEY") in spans


def test_twilio_keys_are_detected_via_plugin_fallback():
    token = "SK1234567890" + "abcdef1234567890abcdef"
    text = f"Twilio key: {token}"
    out = anonymize_text(text, ["API_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert (token, "API_KEY") in spans


def test_crypto_wallets_are_detected():
    text = (
        "ETH 0x742d35Cc6634C0532925a3b844Bc454e4438f44e "
        "BTC 1BoatSLRHtKNngkdXEeobR76b53LETtpyT "
        "Bech32 bc1qw4hr6v2n6z8r2h4j9j0l9w0k3a8r7y5u3m0z8h "
        "TRON TQX8u4jD2J5nR6sA7wB8xC9vD1eF2gH3j4 "
        "XRP rG1QQv2nh2gr7RCZ1P8YYcBUKCCN633jCn"
    )
    out = anonymize_text(text, ["CRYPTO_WALLET"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("0x742d35Cc6634C0532925a3b844Bc454e4438f44e", "CRYPTO_WALLET") in spans
    assert ("1BoatSLRHtKNngkdXEeobR76b53LETtpyT", "CRYPTO_WALLET") in spans
    assert ("bc1qw4hr6v2n6z8r2h4j9j0l9w0k3a8r7y5u3m0z8h", "CRYPTO_WALLET") in spans
    assert ("TQX8u4jD2J5nR6sA7wB8xC9vD1eF2gH3j4", "CRYPTO_WALLET") in spans
    assert ("rG1QQv2nh2gr7RCZ1P8YYcBUKCCN633jCn", "CRYPTO_WALLET") in spans


def test_crypto_wallet_is_extracted_from_labeled_line():
    text = "Wallet Address: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    out = anonymize_text(text, ["CRYPTO_WALLET"], OptionalNlp())
    assert out["anonymized_text"] == "Wallet Address: [CRYPTO_WALLET_1]"


def test_google_analytics_measurement_ids_are_detected():
    text = "Measurement ID G-ZW9TN4SG5T should be hidden."
    out = anonymize_text(text, ["ANALYTICS_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("G-ZW9TN4SG5T", "ANALYTICS_ID") in spans


def test_universal_analytics_ids_are_detected():
    text = "Legacy ID UA-12345678-1 should be hidden."
    out = anonymize_text(text, ["ANALYTICS_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("UA-12345678-1", "ANALYTICS_ID") in spans


def test_region_names_do_not_match_person():
    text = "European Union EU European Economic Area EEA United Kingdom UK United States"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []


def test_region_names_are_not_anonymised_as_locations():
    text = "European Union (EU), European Economic Area (EEA), United Kingdom, UK, United States, USA"
    out = anonymize_text(text, ["ADDRESS", "PERSON"], OptionalNlp())
    assert out["entities"] == []
    assert out["anonymized_text"] == text


def test_script_urls_stay_web_addresses_when_containing_analytics_id():
    text = '<script async src="https://www.googletagmanager.com/gtag/js?id=G-ZW9TN4SG5T"></script>'
    out = anonymize_text(text, ["URL", "ANALYTICS_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ('https://www.googletagmanager.com/gtag/js?id=G-ZW9TN4SG5T', "URL") in spans
    assert all(item["type"] != "ANALYTICS_ID" for item in out["entities"])


def test_html_url_replacement_preserves_quotes_and_closing_tag():
    text = '<script async src="https://www.googletagmanager.com/gtag/js?id=G-ZW9TN4SG5T"></script>'
    out = anonymize_text(text, ["URL"], OptionalNlp())
    assert out["anonymized_text"] == '<script async src="[URL_1]"></script>'


def test_plain_text_keeps_leading_character():
    text = "Installation instructions"
    out = anonymize_text(text, ["PERSON", "ORG", "ADDRESS", "URL"], OptionalNlp())
    assert out["anonymized_text"] == text


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


def test_camel_case_surnames_are_detected_as_person():
    text = "Hi Alberto Garcia,\nPlease coordinate with Wen ONeill from Instituto Verde."
    out = anonymize_text(text, ["PERSON", "ORG"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Alberto Garcia", "PERSON") in spans
    assert ("Wen ONeill", "PERSON") in spans
    assert ("Instituto Verde", "ORG") in spans
    assert ("Wen", "ORG") not in spans


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


def test_subject_lines_are_not_swallowed_as_addresses():
    text = "Subject: Case 0 follow-up for climate infra\n\nHi Alberto Garcia,\nOffice: 28 Bedford Square, London WC1B 3JS"
    out = anonymize_text(text, ["PERSON", "ADDRESS"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert "Subject: Case 0 follow-up for climate infra" in out["anonymized_text"]
    assert ("Alberto Garcia", "PERSON") in spans
    assert ("28 Bedford Square, London WC1B 3JS", "ADDRESS") in spans


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


def test_spaced_iban_values_are_detected():
    text = "IBAN: GB82 WEST 1234 5698 7654 32"
    out = anonymize_text(text, ["BANK_ACCOUNT"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("GB82 WEST 1234 5698 7654 32", "BANK_ACCOUNT") in spans


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
    assert ("Invoice #123456", "INVOICE_NUMBER") in spans
    assert ("INV-AB12CD34", "INVOICE_NUMBER") in spans


def test_numeric_invoice_numbers_are_detected():
    text = "Invoice #10291 and INV-88271 were issued."
    out = anonymize_text(text, ["INVOICE_NUMBER"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Invoice #10291", "INVOICE_NUMBER") in spans
    assert ("INV-88271", "INVOICE_NUMBER") in spans


def test_multi_segment_invoice_numbers_are_detected_as_single_token():
    text = "Invoice reference: INV-2026-0318-778 was approved."
    out = anonymize_text(text, ["INVOICE_NUMBER"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("INV-2026-0318-778", "INVOICE_NUMBER") in spans


def test_numbered_contract_headings_are_skipped():
    text = "2. Confidential Information\n3. Payment Terms"
    out = anonymize_text(text, ["PERSON", "ORG", "ADDRESS"], OptionalNlp())
    assert out["entities"] == []
    assert out["anonymized_text"] == text


def test_common_legal_nouns_do_not_match_person():
    text = "Payment Agreement Invoice Company Consultant Section Signature Background"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["entities"] == []


def test_job_titles_do_not_match_person():
    text = "Kind regards,\nDaniel Hughes\nSenior Analyst"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Daniel Hughes", "PERSON") in spans
    assert ("Senior Analyst", "PERSON") not in spans


def test_referral_letter_heading_does_not_match_person():
    text = "Referral Letter\nDate: 12 March 2026\n\nDaniel Hughes"
    out = anonymize_text(text, ["PERSON", "DATE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Referral Letter", "PERSON") not in spans
    assert ("Daniel Hughes", "PERSON") in spans


def test_employment_template_role_and_contact_labels_do_not_match_person():
    text = (
        "Employment Verification Document\n"
        "Employee: Aisha Rahman\n"
        "Role: Product Designer\n"
        "Contact Number: +44 7700 900245\n"
        "Manager: Sarah Khan\n"
    )
    out = anonymize_text(text, ["PERSON", "PHONE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Aisha Rahman", "PERSON") in spans
    assert ("Sarah Khan", "PERSON") in spans
    assert ("Product Designer", "PERSON") not in spans
    assert ("Employment Verification Document", "PERSON") not in spans
    assert ("Contact Number", "PERSON") not in spans
    assert ("+44 7700 900245", "PHONE") in spans
    assert ("Personal Email", "PERSON") not in spans
    assert ("Email", "PERSON") not in spans


def test_prepared_by_label_detects_single_person_without_duplicate_tokens():
    text = (
        "Project Coordination Memo\n"
        "Prepared by: Anna Carter\n"
        "Contacts\n"
        "- Anna Carter, Green Horizon Research, anna.carter@example.com, +44 7700 900123\n"
    )
    out = anonymize_text(text, ["PERSON", "ORG", "EMAIL", "PHONE"], OptionalNlp())
    assert "Prepared by: [PERSON_1]" in out["anonymized_text"]
    assert "[PERSON_1] [PERSON_1]" not in out["anonymized_text"]


def test_project_title_values_do_not_match_person():
    text = "Project: Regional Sustainability Pilot\nPrepared by: Anna Carter"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Regional Sustainability Pilot", "PERSON") not in spans
    assert ("Anna Carter", "PERSON") in spans


def test_research_org_name_is_detected_as_organisation():
    text = "Anna Carter, Green Horizon Research, anna.carter@example.com"
    out = anonymize_text(text, ["PERSON", "ORG", "EMAIL"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Anna Carter", "PERSON") in spans
    assert ("Green Horizon Research", "ORG") in spans


def test_existing_plain_placeholders_are_not_retokenized():
    text = "Prepared by: Person 1\nContact Number: Phone 1\nPrimary Email: Email 1"
    out = anonymize_text(text, ["PERSON", "PHONE", "EMAIL"], OptionalNlp())
    assert out["entities"] == []
    assert out["anonymized_text"] == text


def test_incident_handover_headings_and_labels_do_not_match_person():
    text = (
        "Incident Handover Note\n"
        "Incident time: 09:42 on 14/03/2026\n"
        "Reporter: Ravi Patel\n"
        "Observed IPs: 203.0.113.27, 198.51.100.18\n"
    )
    out = anonymize_text(text, ["PERSON", "DATE", "IP_ADDRESS"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Ravi Patel", "PERSON") in spans
    assert ("14/03/2026", "DATE") in spans
    assert ("203.0.113.27", "IP_ADDRESS") in spans
    assert ("198.51.100.18", "IP_ADDRESS") in spans
    assert ("Incident Handover Note", "PERSON") not in spans
    assert ("Observed", "PERSON") not in spans
    assert out["anonymized_text"].splitlines()[0] == "Incident Handover Note"
    assert out["anonymized_text"].splitlines()[3].startswith("Observed IPs:")


def test_client_intake_case_id_is_not_phone_and_name_labels_are_person():
    text = (
        "Client Intake Form\n"
        "Case ID: C-UK-2026-00419\n"
        "Submitted: 13/03/2026\n\n"
        "Applicant Name: Sofia Martinez\n"
        "Emergency Contact:\n"
        "Name: Ravi Patel\n"
        "Phone: +44 7700 905112\n"
    )
    out = anonymize_text(text, ["PERSON", "ORDER_ID", "PHONE", "DATE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("C-UK-2026-00419", "ORDER_ID") in spans
    assert ("C-UK-2026-00419", "PHONE") not in spans
    assert ("Sofia Martinez", "PERSON") in spans
    assert ("Ravi Patel", "PERSON") in spans
    assert ("+44 7700 905112", "PHONE") in spans


def test_client_intake_heading_does_not_match_person():
    text = "Client Intake Form\nApplicant Name: Sofia Martinez"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Client Intake Form", "PERSON") not in spans
    assert ("Sofia Martinez", "PERSON") in spans


def test_candidate_shortlist_address_and_current_employer_do_not_misclassify():
    text = (
        "Candidate shortlist note\n"
        "Name: Daniel Hughes\n"
        "Email: daniel.hughes@careersmail.com\n"
        "Phone: 07912 123456\n"
        "Address: 21 Cedar Avenue, Manchester\n"
        "Current employer: Green Horizon Research"
    )
    out = anonymize_text(text, ["PERSON", "EMAIL", "PHONE", "ADDRESS", "ORG"], OptionalNlp())
    assert out["anonymized_text"] == (
        "Candidate shortlist note\n"
        "Name: [PERSON_1]\n"
        "Email: [EMAIL_1]\n"
        "Phone: [PHONE_1]\n"
        "Address: [ADDRESS_1]\n"
        "Current employer: [ORG_1]"
    )


def test_council_tax_table_text_does_not_misclassify_labels_as_people_or_addresses():
    text = (
        "Council Tax Bill 2022/23 Mr Ravish Panduranga & Nima Gourja\n"
        "Account Number : 24311834\n"
        "Reason For Bill : Pay Method\n"
        "Band E Property Reference 00127330113271\n"
        "Increase Croydon Council £1,692.00 2.0\n"
        "12 April 2022 London Borough of Croydon\n"
        "London Borough Of Croydon, Bernard Weatherill House, 8 Mint Walk, CROYDON, CR0 1EA\n"
    )
    out = anonymize_text(text, ["PERSON", "ORG", "ADDRESS", "DATE", "ORDER_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Mr Ravish Panduranga", "PERSON") in spans
    assert ("8 Mint Walk, CROYDON", "ADDRESS") in spans
    assert ("00127330113271", "ORDER_ID") in spans
    assert ("Reason For Bill", "PERSON") not in spans
    assert ("Band E", "PERSON") not in spans
    assert ("Property Reference", "PERSON") not in spans
    assert ("Increase Croydon Council", "ORG") not in spans
    assert ("2022 London Borough", "ADDRESS") not in spans
    assert ("Bernard Weatherill House", "PERSON") not in spans


def test_short_numbered_address_pattern_requires_city_after_comma():
    text = "Service points: 39 PINNACLE APARTMENTS and 8 Mint Walk, CROYDON."
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("39 PINNACLE APARTMENTS", "ADDRESS") not in spans
    assert ("8 Mint Walk, CROYDON", "ADDRESS") in spans


def test_year_city_fragments_do_not_match_address():
    text = "12 April 2022 London Borough of Croydon"
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    spans = {text[item["start"] : item["end"]] for item in out["entities"]}
    assert "2022 London Borough" not in spans


def test_coursework_structured_labels_detect_student_supervisor_and_company():
    text = (
        "Coursework submission context\n"
        "Student: Ravi Patel\n"
        "University email: ravi.patel@studentmail.ac.uk\n"
        "Phone: 07700 905112\n"
        "Placement company: Future Energy Alliance\n"
        "Reference address: 55 Orchard Street, Manchester\n"
        "Supervisor: Emily Foster (emily.foster@coastallab.net)"
    )
    out = anonymize_text(text, ["PERSON", "EMAIL", "PHONE", "ADDRESS", "ORG"], OptionalNlp())
    assert out["anonymized_text"] == (
        "Coursework submission context\n"
        "Student: [PERSON_1]\n"
        "University email: [EMAIL_1]\n"
        "Phone: [PHONE_1]\n"
        "Placement company: [ORG_1]\n"
        "Reference address: [ADDRESS_1]\n"
        "Supervisor: [PERSON_2] ([EMAIL_2])"
    )


def test_immigration_structured_labels_detect_applicant_and_sponsor_organisation():
    text = (
        "Immigration document prep note\n"
        "Applicant: Kamran Ali\n"
        "Sponsor organisation: BrightEdge Consulting\n"
        "Primary contact: kamran.ali@brightedge.co.uk\n"
        "Phone: 07933 449922\n"
        "Correspondence address: 19 Riverside Drive, Birmingham"
    )
    out = anonymize_text(text, ["PERSON", "EMAIL", "PHONE", "ADDRESS", "ORG"], OptionalNlp())
    assert out["anonymized_text"] == (
        "Immigration document prep note\n"
        "Applicant: [PERSON_1]\n"
        "Sponsor organisation: [ORG_1]\n"
        "Primary contact: [EMAIL_1]\n"
        "Phone: [PHONE_1]\n"
        "Correspondence address: [ADDRESS_1]"
    )


def test_non_person_structured_labels_do_not_trigger_person_when_org_disabled():
    text = (
        "Project Coordination Memo\n"
        "Prepared by: Anna Carter\n"
        "Organisation: Green Horizon Research\n"
        "Contact: anna.carter@example.com\n"
        "Phone: +44 7700 900123\n"
        "Address: 14 Willow Lane, Brighton"
    )
    out = anonymize_text(text, ["PERSON", "EMAIL", "ADDRESS"], OptionalNlp())
    assert out["anonymized_text"] == (
        "Project Coordination Memo\n"
        "Prepared by: [PERSON_1]\n"
        "Organisation: Green Horizon Research\n"
        "Contact: [EMAIL_1]\n"
        "Phone: +44 7700 900123\n"
        "Address: [ADDRESS_1]"
    )


def test_case_id_with_prefix_is_not_detected_as_phone():
    text = "Case ID: C-UK-2026-00419"
    out = anonymize_text(text, ["PHONE"], OptionalNlp())
    assert out["entities"] == []


def test_owner_candidate_and_consultant_labels_detect_people():
    text = (
        "Owner: Alice Morgan\n"
        "Candidate: Daniel Hughes\n"
        "Legal contact: Sarah Thompson\n"
        "Consultant: Dr James Holloway\n"
    )
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Alice Morgan", "PERSON") in spans
    assert ("Daniel Hughes", "PERSON") in spans
    assert ("Sarah Thompson", "PERSON") in spans
    assert ("Dr James Holloway", "PERSON") in spans


def test_signatory_labels_detect_people():
    text = (
        "Customer signatory: Hannah Price\n"
        "Vendor signatory: Mark Ellis\n"
    )
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["anonymized_text"] == (
        "Customer signatory: [PERSON_1]\n"
        "Vendor signatory: [PERSON_2]\n"
    )
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Hannah Price", "PERSON") in spans
    assert ("Mark Ellis", "PERSON") in spans


def test_partner_and_associate_labels_detect_people():
    text = (
        "Partner: Olivia Hart\n"
        "Associate: Leo Bennett\n"
    )
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["anonymized_text"] == (
        "Partner: [PERSON_1]\n"
        "Associate: [PERSON_2]\n"
    )
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Olivia Hart", "PERSON") in spans
    assert ("Leo Bennett", "PERSON") in spans


def test_short_numbered_uk_address_with_postcode_is_fully_captured():
    text = "Registered address: 17 Bishopsgate, London EC2N 3AR"
    out = anonymize_text(text, ["ADDRESS"], OptionalNlp())
    assert out["anonymized_text"] == "Registered address: [ADDRESS_1]"
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("17 Bishopsgate, London EC2N 3AR", "ADDRESS") in spans


def test_court_filing_id_is_not_misclassified_as_phone():
    text = "Court filing ID: CF-2026-11873"
    out = anonymize_text(text, ["ORDER_ID", "PHONE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("CF-2026-11873", "ORDER_ID") in spans
    assert ("2026-11873", "PHONE") not in spans


def test_legal_case_caption_entity_is_not_person():
    text = "Matter: Ashton v. Keldon Manufacturing"
    out = anonymize_text(text, ["PERSON", "ORG"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Keldon Manufacturing", "PERSON") not in spans
    assert out["anonymized_text"] == "Matter: [ORG_1]"


def test_engineer_label_detects_person():
    text = "Engineer: Nikhil Rao"
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    assert out["anonymized_text"] == "Engineer: [PERSON_1]"
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Nikhil Rao", "PERSON") in spans


def test_github_user_label_detects_handle_value_only():
    text = "GitHub user: alice-morgan-dev"
    out = anonymize_text(text, ["USERNAME"], OptionalNlp())
    assert out["anonymized_text"] == "GitHub user: [USERNAME_1]"
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("alice-morgan-dev", "USERNAME") in spans
    assert ("user", "USERNAME") not in spans


def test_username_label_detects_handle_value_only():
    text = "Username: nrao_ops"
    out = anonymize_text(text, ["USERNAME"], OptionalNlp())
    assert out["anonymized_text"] == "Username: [USERNAME_1]"
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("nrao_ops", "USERNAME") in spans
    assert ("Username", "USERNAME") not in spans


def test_github_ssh_key_line_does_not_create_username_false_positive():
    text = "GitHub SSH key: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH8G2Ud4h6ZcF1b8Q8kTWX5q2e4w9rjQ7w2L2N2 alice@contoso"
    out = anonymize_text(text, ["USERNAME", "API_KEY"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("SSH", "USERNAME") not in spans
    assert ("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH8G2Ud4h6ZcF1b8Q8kTWX5q2e4w9rjQ7w2L2N2 alice@contoso", "API_KEY") in spans


def test_nhs_paye_and_tax_code_are_government_ids_not_phone():
    text = (
        "NHS no: 943 476 1820\n"
        "Employer PAYE reference: 951/H1234\n"
        "Tax code: 863LX\n"
    )
    out = anonymize_text(text, ["GOVERNMENT_ID", "PHONE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("943 476 1820", "GOVERNMENT_ID") in spans
    assert ("951/H1234", "GOVERNMENT_ID") in spans
    assert ("863LX", "GOVERNMENT_ID") in spans
    assert ("943 476 1820", "PHONE") not in spans


def test_government_id_labels_do_not_trigger_phone_only_detection():
    text = (
        "NHS no: 943 476 1820\n"
        "Employer PAYE reference: 951/H1234\n"
        "Tax code: 863LX\n"
    )
    out = anonymize_text(text, ["PHONE"], OptionalNlp())
    assert out["entities"] == []


def test_consultant_dr_name_is_not_misclassified_as_address():
    text = (
        "NHS referral note\n"
        "Patient: Eleanor Matthews\n"
        "Consultant: Dr James Holloway\n"
        "Email: james.holloway@westbrook-hospital.nhs.uk\n"
    )
    out = anonymize_text(text, ["PERSON", "ADDRESS", "EMAIL"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Eleanor Matthews", "PERSON") in spans
    assert ("Dr James Holloway", "PERSON") in spans
    assert ("Dr James Holloway\nEmail", "ADDRESS") not in spans


def test_medical_report_lines_do_not_trigger_person_and_org_false_positives():
    text = (
        "GP at hand, 139 Lillie Road, London SW6 7SX, E85124, 03303 038000 Mr Nima Mohamad Zade\n"
        "DOB: 20 Mar 1989\n"
        "NHS number: 717 037 4862\n"
        "7 Braybrooke Terrace Hastings E Sussex TN34 1TD\n"
        "Dear N Mohamad Zade\n"
        "Date specimen collected Date filed Battery Headers Result indicator Follow-up action Filing comments 01 Apr 2024 11:32\n"
        "Full blood count Abnormal Make an appointment to see doctor\n"
        "Total white blood count (XaIdY) 6.2 10^9/L\n"
        "Haemoglobin concentration (Xa96v) 142 g/L\n"
    )
    out = anonymize_text(text, ["PERSON", "ORG", "ADDRESS", "PHONE", "DATE", "GOVERNMENT_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("Mr Nima Mohamad Zade", "PERSON") in spans
    assert ("N Mohamad Zade", "PERSON") in spans
    assert ("139 Lillie Road, London SW6 7SX", "ADDRESS") in spans
    assert ("03303 038000", "PHONE") in spans
    assert ("717 037 4862", "GOVERNMENT_ID") in spans
    assert ("Battery Headers Result", "PERSON") not in spans
    assert ("Abnormal Make", "PERSON") not in spans
    assert ("E Sussex", "PERSON") not in spans
    assert ("XaIdY", "ORG") not in spans
    assert ("Xa96v", "ORG") not in spans


def test_initial_firstname_three_part_name_in_greeting_is_detected_as_person():
    text = "Dear N Mohamad Zade, please confirm."
    out = anonymize_text(text, ["PERSON"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("N Mohamad Zade", "PERSON") in spans
    assert ("N Mohamad", "PERSON") not in spans


def test_employee_id_is_detected_from_employee_context():
    text = "Employee ID: HR-11892"
    out = anonymize_text(text, ["EMPLOYEE_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("HR-11892", "EMPLOYEE_ID") in spans


def test_employee_id_is_not_misclassified_as_phone():
    text = "Employee ID: EMP-2026-00419"
    out = anonymize_text(text, ["EMPLOYEE_ID", "PHONE"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("EMP-2026-00419", "EMPLOYEE_ID") in spans
    assert ("EMP-2026-00419", "PHONE") not in spans


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


def test_connection_strings_are_not_split_by_email_detection():
    text = "Connection: mongodb://user:pw1@db1.internal:27017/app"
    out = anonymize_text(text, ["URL", "EMAIL", "CONNECTION_STRING"], OptionalNlp())
    assert out["anonymized_text"] == "Connection: [CONNECTION_STRING_1]"
    assert all(item["type"] != "EMAIL" for item in out["entities"])


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


def test_order_id_context_is_not_misclassified_as_api_key():
    text = "Order ID: AVW-45922159958"
    out = anonymize_text(text, ["API_KEY", "ORDER_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("AVW-45922159958", "ORDER_ID") in spans
    assert ("AVW-45922159958", "API_KEY") not in spans


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


def test_hyphenated_transaction_id_is_detected():
    text = "transaction TXN-98A122"
    out = anonymize_text(text, ["TRANSACTION_ID"], OptionalNlp())
    spans = {(text[item["start"] : item["end"]], item["type"]) for item in out["entities"]}
    assert ("TXN-98A122", "TRANSACTION_ID") in spans


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
