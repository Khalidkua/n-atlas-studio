import re


def normalize_text(text: str) -> str:
    """Normalize text for basic comparison."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def exact_match_score(
    generated: str,
    reference: str,
) -> float:
    """Return 1.0 if normalized texts match, otherwise 0.0."""
    return float(
        normalize_text(generated)
        == normalize_text(reference)
    )


def word_overlap_score(
    generated: str,
    reference: str,
) -> float:
    """Calculate simple reference-word coverage."""
    generated_words = set(
        normalize_text(generated).split()
    )

    reference_words = set(
        normalize_text(reference).split()
    )

    if not reference_words:
        return 0.0

    overlap = generated_words.intersection(reference_words)

    return len(overlap) / len(reference_words)
