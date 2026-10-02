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

def word_count(text: str) -> int:
    """Return the number of normalized whitespace-separated words."""
    normalized = normalize_text(text)

    if not normalized:
        return 0

    return len(normalized.split())


def length_ratio(
    generated: str,
    reference: str,
) -> float:
    """Return generated word count divided by reference word count."""
    reference_count = word_count(reference)

    if reference_count == 0:
        return 0.0

    return word_count(generated) / reference_count

