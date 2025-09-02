import sys, pathlib, inspect
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import storyteller, judge, revise


def _source_has_model(mod):
    src = inspect.getsource(mod)
    return "gpt-3.5-turbo" in src


def test_storyteller_model_locked():
    assert _source_has_model(storyteller), "storyteller must use gpt-3.5-turbo"


def test_judge_model_locked():
    assert _source_has_model(judge), "judge must use gpt-3.5-turbo"


def test_revise_model_locked():
    assert _source_has_model(revise), "revise must use gpt-3.5-turbo"
