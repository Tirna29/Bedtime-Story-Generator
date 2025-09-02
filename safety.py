from typing import Tuple, List
import re

# kept intentionally mild for a 5–10 yrs. audience
BLACKLIST = {
    "kill", "killing", "blood", "bloody", "knife", "gun", "monster", "monsters",
    "terror", "terrifying", "horror", "scare", "scary", "haunt", "haunted",
    "die", "death", "dead", "poison", "explode", "explosion", "violence",
    "ghost", "witch"
}

# Acceptable “calm ending” signals
CALM_ENDING_HINTS = [
    "sleep", "asleep", "drifted to sleep", "rest", "rested", "peaceful", "calm",
    "good night", "goodnight", "cozy", "snuggled", "lights dimmed",
]

MAX_WORDS = 500  # hard cap for this assignment


def _contains_blacklisted(story_lower: str) -> List[str]:
    found = []
    # word-boundary match so "skilling" doesn't trip "kill"
    for w in BLACKLIST:
        if re.search(rf"\b{re.escape(w)}\b", story_lower):
            found.append(w)
    return sorted(found)


def _has_calm_ending(story_lower: str) -> bool:
    # Check last ~2 sentences for a calm signal
    # Simple sentence split:
    sentences = re.split(r"[.!?]\s+", story_lower.strip())
    tail = " ".join(sentences[-2:]) if len(sentences) >= 2 else (sentences[-1] if sentences else "")
    return any(hint in tail for hint in CALM_ENDING_HINTS)


def safety_check(story: str) -> Tuple[bool, List[str]]:
    """
    Returns (is_safe_and_stylish, issues)
    issues: list of human-readable strings describing problems found.
    """
    issues = []
    text = story.strip()
    story_lower = text.lower()

    # Length check
    words = re.findall(r"\b\w+\b", text)
    if len(words) > MAX_WORDS:
        issues.append(f"Story is too long ({len(words)} words). Limit is {MAX_WORDS} words.")

    # Blacklist check
    bad = _contains_blacklisted(story_lower)
    if bad:
        issues.append("Contains sensitive words not suitable for ages 5–10: " + ", ".join(bad))

    # Calm ending check
    if not _has_calm_ending(story_lower):
        issues.append("Story should end with a calm, reassuring bedtime line (mention sleep/rest/peace).")

    return (len(issues) == 0, issues)
