from app.agent import fallback_message


def test_fallback_follows_language():
    assert "consult" in fallback_message("English")
    assert "Fachpersonal" in fallback_message("German")


def test_unknown_language_falls_back_to_english():
    assert fallback_message("Spanish") == fallback_message("English")