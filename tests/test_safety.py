import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from safety import safety_check, MAX_WORDS


def test_safe_story_passes():
    story = """
    Luna the bunny shared her carrots with friends at the garden.
    Everyone felt happy and calm. As the moon rose, they drifted to sleep.
    """.strip()
    ok, issues = safety_check(story)
    assert ok, f"Expected safe story, got issues: {issues}"


def test_blacklist_blocks_words():
    story = """
    The knight waved a toy knife around and scared everyone.
    They went to sleep peacefully afterwards.
    """.strip()
    ok, issues = safety_check(story)
    assert not ok
    assert any("sensitive words" in i.lower() for i in issues)


def test_length_cap_enforced():
    too_long = ("word " * (MAX_WORDS + 10)).strip() + ". sleep."
    ok, issues = safety_check(too_long)
    assert not ok
    assert any("too long" in i.lower() for i in issues)


def test_calm_ending_required():
    story = """
    A cheerful picnic happened in the park with songs and games.
    Everyone went home afterwards.
    """.strip()  # no explicit sleep/rest cue
    ok, issues = safety_check(story)
    assert not ok
    assert any("calm" in i.lower() for i in issues)
