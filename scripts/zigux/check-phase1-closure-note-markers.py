#!/usr/bin/env python3
"""Check that the Phase 1 closure note still advertises the live closure packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")

REQUIRED_MARKERS = {
    "validator_state": "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "string_review_checker": "scripts/zigux/check-phase1-string-review-packet.py",
    "direct_owner_checker": "scripts/zigux/check-phase1-direct-owner-markers.py",
    "closure_validator": "scripts/zigux/validate-phase1-closure.py",
    "next_step_phrase": "sync one shared reminder surface or one helper-family tie-breaker",
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path) -> str:
    return (root / CLOSURE_NOTE_REL).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    note_path = root / CLOSURE_NOTE_REL
    if not note_path.is_file():
        return [f"missing_file:{CLOSURE_NOTE_REL.as_posix()}"]

    text = load_text(root)
    failures: list[str] = []
    for label, marker in REQUIRED_MARKERS.items():
        count = text.count(marker)
        if count != 1:
            failures.append(
                f"{CLOSURE_NOTE_REL.as_posix()}:{label}:expected_once:actual_count={count}:{marker}"
            )
    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture(root: Path) -> None:
    write_text(
        root / CLOSURE_NOTE_REL,
        "\n".join(
            [
                "# Phase 1 Closure",
                "",
                REQUIRED_MARKERS["validator_state"],
                (
                    "`PHASE1_CURRENT_REMINDER_PACKET="
                    "Documentation/zigux/phase1-closure.md,"
                    "Documentation/zigux/phase1-host-helper-lane-sequencing.md,"
                    "Documentation/zigux/README.md,"
                    "Documentation/zigux/review-checklist.md,"
                    "scripts/zigux/README.md,"
                    "scripts/zigux/check-phase1-string-review-packet.py,"
                    "scripts/zigux/check-phase1-direct-owner-markers.py,"
                    "scripts/zigux/check-phase1-bench.py,"
                    "scripts/zigux/check-phase1-shared-reminder-packet.py,"
                    "scripts/zigux/validate-phase1-closure.py`"
                ),
                (
                    "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one "
                    "helper-family tie-breaker against the restored closure note.`"
                ),
                "",
            ]
        )
        + "\n",
    )


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        (
            "missing_string_review_checker",
            (
                REQUIRED_MARKERS["string_review_checker"],
                "scripts/zigux/check-phase1-bench.py",
            ),
        ),
        (
            "missing_direct_owner_checker",
            (
                REQUIRED_MARKERS["direct_owner_checker"],
                "scripts/zigux/check-phase1-bench.py",
            ),
        ),
        (
            "missing_validator_state",
            (
                REQUIRED_MARKERS["validator_state"],
                "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
            ),
        ),
        (
            "missing_next_step_phrase",
            (
                REQUIRED_MARKERS["next_step_phrase"],
                "restore the missing phase1 closure note first",
            ),
        ),
    ]

    for name, replacement in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-note-markers-") as tmp:
            root = Path(tmp)
            make_fixture(root)
            if replacement is not None:
                old, new = replacement
                write_text(root / CLOSURE_NOTE_REL, load_text(root).replace(old, new, 1))

            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-note-markers-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-note-markers-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_NOTE_MARKERS_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_NOTE_MARKERS_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_NOTE_MARKERS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
