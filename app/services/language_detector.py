import re
from typing import Any


class LanguageDetector:
    """Lightweight heuristic detector for Nigerian benchmark languages."""

    LANGUAGE_MARKERS = {
        "English": {
            "the", "is", "are", "and", "of", "to", "in", "for",
            "with", "this", "that", "what", "how", "an", "as",
            "from", "instead", "over", "instead", "allows",
            "users", "such", "instead",
        },
        "Hausa": {
            "da", "na", "ne", "ce", "shi", "ta", "yana", "tana",
            "suna", "ana", "don", "mai", "wannan", "bayanai",
            "kwamfuta", "sarrafa", "kuma", "idan", "zuwa",
            "akan", "cikin", "domin", "wanda", "waɗanda",
            "wadanda", "suke", "ake", "ba", "daga", "saboda",
            "muhimmanci", "bangare", "tsarin", "bayanan",
            "ayyuka", "sarrafawa", "ajiya", "sabar", "masu",
            "damar", "ingantacciyar", "manufar", "gami",
            "gami da", "kamar", "yayin", "yasa", "yake",
            "shine", "shirin", "shirye-shiryen",
        },
        "Igbo": {
            "bụ", "bụ́", "ị", "anyị", "unu", "ọ", "nke",
            "onye", "dị", "adịghị", "maka", "site", "ya",
            "kọmputa", "ngwa", "ngwaọrụ", "anyị", "ndị",
            "bụkwa", "ọ bụ", "na-enye", "na-ahazi", "ji dị",
            "ihe", "mere", "dị mkpa", "kọwaa",
        },
        "Yoruba": {
            "ni", "jẹ", "àti", "sí", "láti", "ní", "ó", "ẹ",
            "wọn", "kan", "fun", "pẹ̀lú", "kọ̀ǹpútà",
            "kọ̀m̀pútà", "dátà", "ṣiṣẹ́", "èdè", "ọ̀rọ̀",
            "àwọn", "tí", "ó jẹ́", "kí", "nínú", "lórí",
            "báwo", "ṣàlàyé", "ìdí", "pàtàkì", "àtọwọ́dá",
        },
    }

    DISTINCTIVE_MARKERS = {
        "English": {
            "the", "is", "are", "and", "of", "to", "in",
            "for", "with", "this", "that", "from", "users",
            "allows", "such", "instead", "over",
        },
        "Hausa": {
            "kwamfuta", "bayanai", "sarrafa", "cikin",
            "yana", "tana", "wanda", "waɗanda", "wadanda",
            "muhimmanci", "tsarin", "shirye-shiryen",
            "ingantacciyar", "ajiya", "sabar", "masu",
            "damar", "shine", "yake", "yasa", "saboda",
            "gami", "bisa", "domin",
        },
        "Igbo": {
            "bụ", "bụ́", "anyị", "unu", "ọ", "nke",
            "onye", "dị", "adịghị", "kọmputa", "ngwaọrụ",
            "ndị", "kọwaa", "na-ahazi", "na-enye",
        },
        "Yoruba": {
            "àti", "sí", "láti", "ní", "ó", "ẹ", "wọn",
            "pẹ̀lú", "kọ̀ǹpútà", "dátà", "ṣiṣẹ́", "èdè",
            "ọ̀rọ̀", "àwọn", "tí", "ó jẹ́", "lórí",
            "ṣàlàyé", "ìdí", "pàtàkì", "àtọwọ́dá",
        },
    }

    @staticmethod
    def _words(text: str) -> set[str]:
        return set(
            re.findall(
                r"\b[\wÀ-ÖØ-öø-ÿ'-]+\b",
                text.lower(),
            )
        )

    def detect(self, text: str) -> dict[str, Any]:
        """Detect language using weighted marker scoring."""

        if not text or not text.strip():
            return {
                "language": "unknown",
                "confidence": 0.0,
                "scores": {},
            }

        normalized = text.lower()
        words = self._words(normalized)

        scores: dict[str, float] = {}

        for language, markers in self.LANGUAGE_MARKERS.items():
            regular_score = len(words.intersection(markers))

            distinctive = self.DISTINCTIVE_MARKERS[language]
            distinctive_score = len(words.intersection(distinctive))

            phrase_score = sum(
                2
                for phrase in distinctive
                if " " in phrase and phrase in normalized
            )

            scores[language] = (
                regular_score
                + (2 * distinctive_score)
                + phrase_score
            )

        # Generic technical words such as "software", "data",
        # "computer", and "system" should not determine the language.
        generic_words = {
            "software",
            "hardware",
            "data",
            "computer",
            "system",
            "operating",
            "ai",
            "artificial",
            "intelligence",
            "cloud",
            "computing",
            "programming",
        }

        informative_words = words - generic_words

        if not informative_words:
            return {
                "language": "unknown",
                "confidence": 0.0,
                "scores": scores,
            }

        best_language = max(scores, key=scores.get)
        best_score = scores[best_language]
        total_score = sum(scores.values())

        if best_score == 0 or total_score == 0:
            return {
                "language": "unknown",
                "confidence": 0.0,
                "scores": scores,
            }

        confidence = best_score / total_score

        return {
            "language": best_language,
            "confidence": confidence,
            "scores": scores,
        }
