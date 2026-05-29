#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=scripts_root_productization_gap

Fail-closed checker for the current Phase 14 scripts-root productization gap.

This guard records that the shared Phase 14 productization packet is present in
notes, manifests, and validator-side scripts, while the scripts-root README has
not yet grown a dedicated Phase 14 reminder section. It should be retired or
rewired when that README section is intentionally added.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=scripts_root_productization_gap"
README_PATH = Path("scripts/zigux/README.md")
NOTE_PATH = Path("Documentation/zigux/phase14-scripts-root-productization-gap.md")

README_REQUIRED_MARKERS = [
    "## Phase 13",
    "## Phase 15",
]

README_FORBIDDEN_MARKERS = [
    "## Phase 14",
    "scripts/zigux/check-phase14-shared-smoke-route.py` keep the current Phase 14",
]

NOTE_REQUIRED_MARKERS = [
    "PHASE14_GAP_KIND=scripts_root_productization_gap",
    "PHASE14_LANE_KEY=P14-L01",
    "Phase 14 stays bounded to study-only, wrapper-first, or stay-in-C evidence",
    "`scripts/zigux/README.md` currently jumps from `## Phase 13` to `## Phase 15`",
    "`scripts/zigux/check-phase14-shared-smoke-route.py`",
    "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py`",
    "`scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py`",
    "`scripts/zigux/check-phase14-skbuff-compile-route.py`",
    "`scripts/zigux/check-phase14-rcu-compile-route.py`",
    "`scripts/zigux/check-phase14-rcu-rollback-guardrail.py`",
    "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "`make -C zigux phase14-validate`",
    "do not restore `phase14-smoke`, `phase14-test`, or `phase14` as shipped wrapper claims",
]


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel.as_posix())
    return path.read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def require_absent(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden_marker:{rel.as_posix()}:{marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        readme = read_text(root, README_PATH)
    except FileNotFoundError as exc:
        return [f"missing_file:{exc.args[0]}"]
    try:
        note = read_text(root, NOTE_PATH)
    except FileNotFoundError as exc:
        return [f"missing_file:{exc.args[0]}"]

    require_markers(errors, README_PATH, readme, README_REQUIRED_MARKERS)
    require_absent(errors, README_PATH, readme, README_FORBIDDEN_MARKERS)
    require_markers(errors, NOTE_PATH, note, NOTE_REQUIRED_MARKERS)
    return errors


def self_test() -> None:
    root = Path(tempfile.mkdtemp(prefix="phase14-scripts-root-gap-"))
    try:
        readme = """# scripts/zigux\n\n## Phase 13\n\n- Phase 13 reminder.\n\n## Phase 15\n\n- Phase 15 reminder.\n"""
        note = """# Phase 14 Scripts-Root Productization Gap\n\n- `PHASE14_GAP_KIND=scripts_root_productization_gap`\n- `PHASE14_LANE_KEY=P14-L01`\n\nPhase 14 stays bounded to study-only, wrapper-first, or stay-in-C evidence.\n\n`scripts/zigux/README.md` currently jumps from `## Phase 13` to `## Phase 15`.\n\nRequired current packet reminders:\n\n- `scripts/zigux/check-phase14-shared-smoke-route.py`\n- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`\n- `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py`\n- `scripts/zigux/check-phase14-skbuff-compile-route.py`\n- `scripts/zigux/check-phase14-rcu-compile-route.py`\n- `scripts/zigux/check-phase14-rcu-rollback-guardrail.py`\n- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`\n- `make -C zigux phase14-validate`\n\nWhen the README is repaired, do not restore `phase14-smoke`, `phase14-test`, or `phase14` as shipped wrapper claims.\n"""
        write_text(root, README_PATH, readme)
        write_text(root, NOTE_PATH, note)
        assert check(root) == []

        write_text(
            root,
            README_PATH,
            readme.replace("## Phase 15", "## Phase 14\n\n- stale claim.\n\n## Phase 15"),
        )
        assert any(error.startswith("forbidden_marker:") for error in check(root))

        write_text(root, README_PATH, readme)
        write_text(
            root,
            NOTE_PATH,
            note.replace("`scripts/zigux/check-phase14-skbuff-compile-route.py`\n", ""),
        )
        assert any("check-phase14-skbuff-compile-route.py" in error for error in check(root))
    finally:
        shutil.rmtree(root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    errors = check(Path(args.root))
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
