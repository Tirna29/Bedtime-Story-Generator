import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import main


def test_save_story_creates_file(tmp_path, monkeypatch):
    stories_dir = tmp_path / "stories"
    stories_dir.mkdir()

    # Patch save_story to write into tmp_path
    def save_story_tmp(story: str, request: str, filename: str = None):
        filename = filename or "test_story.txt"
        path = stories_dir / filename
        path.write_text(f"Request:\n{request}\n\nFinal Story:\n{story}", encoding="utf-8")
        return str(path)

    monkeypatch.setattr(main, "save_story", save_story_tmp, raising=True)

    # Patch other modules to avoid API calls
    monkeypatch.setattr("storyteller.generate_story", lambda req: "draft story ending with sleep.", raising=False)
    monkeypatch.setattr(
        "judge.evaluate_story",
        lambda s, r: {
            "age_appropriate": True,
            "safe": True,
            "clarity": "ok",
            "moral_theme": "present",
            "length": "ok",
            "calming_end": True,
            "suggestions": [],
        },
        raising=False,
    )
    monkeypatch.setattr("safety.safety_check", lambda s: (True, []), raising=False)
    monkeypatch.setattr("revise.revise_story", lambda s, fb, r: s + " (revised)", raising=False)

    # Call save_story and verify file contents
    out_path = main.save_story("final story sleep.", "test request", filename="test_story.txt")
    path = pathlib.Path(out_path)
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "Final Story:" in content
    assert "test request" in content
