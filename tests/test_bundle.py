"""model.py, the submitted bot, is one self-contained file built from its
sources by tools/bundle_model.py (the form asks for the .pkl and model.py)."""

import ast
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_IMPORTS = {"random", "card_utils", "game_state", "player_action"}


def _bundler():
    path = os.path.join(ROOT, "tools", "bundle_model.py")
    spec = importlib.util.spec_from_file_location("bundle_model", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_model_py_is_the_current_bundle_of_its_sources():
    with open(os.path.join(ROOT, "model.py"), encoding="utf-8") as f:
        shipped = f.read()
    assert shipped == _bundler().build(), (
        "model.py is out of date: run python tools/bundle_model.py")


def test_model_py_needs_no_other_team_file():
    with open(os.path.join(ROOT, "model.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module.split(".")[0])
    assert imported <= ALLOWED_IMPORTS, imported - ALLOWED_IMPORTS
