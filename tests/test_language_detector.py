from app.services.language_detector import LanguageDetector


def test_detect_english():
    detector = LanguageDetector()

    result = detector.detect(
        "The computer processes data quickly."
    )

    assert result["language"] == "English"


def test_detect_hausa():
    detector = LanguageDetector()

    result = detector.detect(
        "Kwamfuta tana sarrafa bayanai cikin sauri."
    )

    assert result["language"] == "Hausa"


def test_detect_igbo():
    detector = LanguageDetector()

    result = detector.detect(
        "Kọmputa na-ahazi data ngwa ngwa."
    )

    assert result["language"] == "Igbo"


def test_detect_yoruba():
    detector = LanguageDetector()

    result = detector.detect(
        "Kọ̀m̀pútà ń ṣiṣẹ́ lórí dátà ní kíákíá."
    )

    assert result["language"] == "Yoruba"


def test_empty_text_returns_unknown():
    detector = LanguageDetector()

    result = detector.detect("")

    assert result["language"] == "unknown"
    assert result["confidence"] == 0.0
