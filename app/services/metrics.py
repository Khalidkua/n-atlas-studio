import re
from difflib import SequenceMatcher


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


def token_f1_score(
    generated: str,
    reference: str,
) -> float:
    """Calculate token-level F1 using normalized whitespace tokens."""
    generated_tokens = normalize_text(generated).split()
    reference_tokens = normalize_text(reference).split()

    if not generated_tokens or not reference_tokens:
        return float(
            not generated_tokens and not reference_tokens
        )

    generated_counts = {}

    for token in generated_tokens:
        generated_counts[token] = (
            generated_counts.get(token, 0) + 1
        )

    reference_counts = {}

    for token in reference_tokens:
        reference_counts[token] = (
            reference_counts.get(token, 0) + 1
        )

    overlap = 0

    for token, count in generated_counts.items():
        overlap += min(
            count,
            reference_counts.get(token, 0),
        )

    if overlap == 0:
        return 0.0

    precision = overlap / len(generated_tokens)
    recall = overlap / len(reference_tokens)

    if precision + recall == 0:
        return 0.0

    return (
        2 * precision * recall
        / (precision + recall)
    )


def character_similarity_score(
    generated: str,
    reference: str,
) -> float:
    """Calculate normalized character-level similarity."""
    generated_normalized = normalize_text(generated)
    reference_normalized = normalize_text(reference)

    if not generated_normalized and not reference_normalized:
        return 1.0

    if not generated_normalized or not reference_normalized:
        return 0.0

    return SequenceMatcher(
        None,
        generated_normalized,
        reference_normalized,
    ).ratio()


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
