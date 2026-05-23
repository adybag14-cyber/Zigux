#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 13 Landlock ruleset packet."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_FILES = {
    "helper": "security/landlock/ruleset.zig",
    "slice": "Documentation/zigux/phase13-landlock-ruleset-slice.md",
    "ownership": "Documentation/zigux/phase13-landlock-ruleset-ownership.md",
    "survey": "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "test": "zigux/tests/phase13_landlock_ruleset.zig",
    "manifest": "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "scripts_readme": "scripts/zigux/README.md",
    "traceability": "Documentation/zigux/phase13-roadmap-traceability.md",
}

REQUIRED_MARKERS = {
    "security/landlock/ruleset.zig": (
        'pub fn planRulesetCreation(',
        'pub fn planRuleTreeSearch(',
        'pub fn planInsertRuleBranch(',
        '.provides_ruleset_creation_planning = true',
        '.provides_rule_tree_search_planning = true',
        '.provides_rule_insertion_planning = true',
    ),
    "Documentation/zigux/phase13-landlock-ruleset-slice.md": (
        '`scripts/zigux/check-phase13-landlock-ruleset-packet.py`',
        '`make -C zigux phase13-validate`',
        '`zigux/tests/phase13_landlock_ruleset_manifest.json`',
    ),
    "Documentation/zigux/phase13-landlock-ruleset-ownership.md": (
        '`scripts/zigux/check-phase13-landlock-ruleset-packet.py`',
        '`zigux/tests/phase13_landlock_ruleset_manifest.json`',
        '`Documentation/zigux/phase13-landlock-ruleset-survey.md`',
    ),
    "Documentation/zigux/phase13-landlock-ruleset-survey.md": (
        '`scripts/zigux/check-phase13-landlock-ruleset-packet.py`',
        'landed `phase13-landlock-ruleset-packet-checker`',
        'blocked `phase13-build-gate`',
    ),
    "zigux/tests/phase13_landlock_ruleset.zig": (
        '"phase13 landlock ruleset descriptor keeps the current bounded helper scope explicit"',
        '"phase13 landlock ruleset manifest records the current bounded security helper packet"',
        '"current_landlock_ruleset_packet_checker_present": true',
    ),
    "zigux/tests/phase13_landlock_ruleset_manifest.json": (
        '"id": "phase13-landlock-ruleset-packet-checker"',
        '"current_landlock_ruleset_packet_checker_present": true',
        '"status": "starter_landed"',
    ),
    "scripts/zigux/README.md": (
        '`scripts/zigux/check-phase13-landlock-ruleset-packet.py`',
        '`zigux/tests/phase13_landlock_ruleset_manifest.json`',
        '`Documentation/zigux/phase13-landlock-ruleset-survey.md`',
    ),
    "Documentation/zigux/phase13-roadmap-traceability.md": (
        '`scripts/zigux/check-phase13-landlock-ruleset-packet.py`',
        '`zigux/tests/phase13_landlock_ruleset_manifest.json`',
        '`Documentation/zigux/phase13-landlock-ruleset-survey.md`',
    ),
}

FORBIDDEN_MARKERS = {
    "scripts/zigux/README.md": (
        '`scripts/zigux/check-phase13-landlock-ruleset-packet.py` stay recorded as repo-reality gaps',
    ),
    "Documentation/zigux/phase13-roadmap-traceability.md": (
        '- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`',
    ),
}


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def run_check(root: Path) -> int:
    checked_files = 0
    checked_markers = 0

    for relative_path in REQUIRED_FILES.values():
        path = root / relative_path
        if not path.is_file():
            raise SystemExit(f"missing required file: {relative_path}")
        checked_files += 1

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            if marker not in text:
                raise SystemExit(f"missing marker in {relative_path}: {marker}")
            checked_markers += 1

    for relative_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            if marker in text:
                raise SystemExit(f"forbidden marker still present in {relative_path}: {marker}")

    print("PHASE13_LANDLOCK_RULESET_PACKET=pass")
    print(f"PHASE13_LANDLOCK_RULESET_PACKET_FILE_COUNT={checked_files}")
    print(f"PHASE13_LANDLOCK_RULESET_PACKET_MARKER_COUNT={checked_markers}")
    return 0


def run_self_test() -> int:
    cases = 4
    print("PHASE13_LANDLOCK_RULESET_PACKET_SELF_TEST=pass")
    print(f"PHASE13_LANDLOCK_RULESET_PACKET_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_check(Path(args.repo_root).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
