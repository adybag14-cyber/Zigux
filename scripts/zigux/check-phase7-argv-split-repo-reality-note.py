#!/usr/bin/env python3
"""Verify the narrow Phase 7 argv_split repo-reality note."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

NOTE_PATH = Path("Documentation/zigux/phase7-argv-split-repo-reality-note.md")

DIRECT_READABLE_FILES = [
    Path("Documentation/zigux/phase7-rbtree-direct-anchor-note.md"),
    Path("Documentation/zigux/phase7-string-helpers-slice.md"),
    Path("lib/string_helpers.zig"),
    Path("zigux/tests/phase7_string_helpers.zig"),
    Path("zigux/tests/phase7_rbtree_survey.zig"),
]

EXPECTED_MISSING_FILES = [
    Path("Documentation/zigux/phase7-argv-split-slice.md"),
    Path("lib/argv_split.zig"),
    Path("zigux/tests/phase7_argv_split.zig"),
    Path("zigux/tests/phase7_argv_split_survey.zig"),
    Path("zigux/tests/phase7_argv_split_manifest.json"),
    Path("zigux/tests/fixtures/phase7_argv_split_vectors.zig"),
    Path("scripts/zigux/check-phase7-argv-split-packet.py"),
    Path("scripts/zigux/validate-phase7.py"),
    Path("zigux/tests/phase7_build.zig"),
    Path("zigux/Makefile"),
]

REQUIRED_MARKERS = [
    "# Phase 7 Argv Split Repo Reality Note",
    "Lane key: `P7-L02`",
    "Current directly readable sibling anchors on `master`:",
    "`Documentation/zigux/phase7-rbtree-direct-anchor-note.md`",
    "`Documentation/zigux/phase7-string-helpers-slice.md`",
    "`lib/string_helpers.zig`",
    "`zigux/tests/phase7_string_helpers.zig`",
    "`zigux/tests/phase7_rbtree_survey.zig`",
    "Repo-reality warning for the missing dedicated `argv_split` packet on current `master`:",
    "`Documentation/zigux/phase7-argv-split-slice.md`",
    "`lib/argv_split.zig`",
    "`zigux/tests/phase7_argv_split.zig`",
    "`zigux/tests/phase7_argv_split_survey.zig`",
    "`zigux/tests/phase7_argv_split_manifest.json`",
    "`zigux/tests/fixtures/phase7_argv_split_vectors.zig`",
    "`scripts/zigux/check-phase7-argv-split-packet.py`",
    "`scripts/zigux/validate-phase7.py`",
    "`zigux/tests/phase7_build.zig`",
    "`zigux/Makefile`",
    "`string_helpers` stays the only directly readable Phase 7 helper implementation packet on current `master`",
    "`cmdline` stays parked under the current Phase 1 helper packet",
    "`rbtree` stays reviewable through the direct anchor note and survey only",
    "do not present the missing dedicated `argv_split` packet or the broader shared Phase 7 control routes as directly readable current-`master` evidence again until a fresh same-lane reread or republish materializes them",
]


def check_repo(root: Path) -> tuple[int, int, int]:
    note_path = root / NOTE_PATH
    if not note_path.is_file():
        raise SystemExit(f"missing note file: {NOTE_PATH}")

    for rel_path in DIRECT_READABLE_FILES:
        if not (root / rel_path).is_file():
            raise SystemExit(f"missing direct-readable companion: {rel_path}")

    unexpected_present = [str(rel_path) for rel_path in EXPECTED_MISSING_FILES if (root / rel_path).exists()]
    if unexpected_present:
        raise SystemExit(
            "expected-missing Phase 7 argv_split packet files unexpectedly present: "
            + ", ".join(unexpected_present)
        )

    note_text = note_path.read_text(encoding="utf-8")
    missing_markers = [marker for marker in REQUIRED_MARKERS if marker not in note_text]
    if missing_markers:
        raise SystemExit("missing note markers: " + ", ".join(missing_markers))

    return (1 + len(DIRECT_READABLE_FILES), len(EXPECTED_MISSING_FILES), len(REQUIRED_MARKERS))


def run_self_test() -> None:
    workspace = Path(tempfile.mkdtemp(prefix="phase7-argv-split-note-"))
    try:
        for rel_path in [NOTE_PATH, *DIRECT_READABLE_FILES]:
            target = workspace / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            if rel_path == NOTE_PATH:
                target.write_text(
                    """# Phase 7 Argv Split Repo Reality Note

Lane key: `P7-L02`

Current directly readable sibling anchors on `master`:
- `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`
- `Documentation/zigux/phase7-string-helpers-slice.md`
- `lib/string_helpers.zig`
- `zigux/tests/phase7_string_helpers.zig`
- `zigux/tests/phase7_rbtree_survey.zig`

Repo-reality warning for the missing dedicated `argv_split` packet on current `master`:
- `Documentation/zigux/phase7-argv-split-slice.md`
- `lib/argv_split.zig`
- `zigux/tests/phase7_argv_split.zig`
- `zigux/tests/phase7_argv_split_survey.zig`
- `zigux/tests/phase7_argv_split_manifest.json`
- `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
- `scripts/zigux/check-phase7-argv-split-packet.py`
- `scripts/zigux/validate-phase7.py`
- `zigux/tests/phase7_build.zig`
- `zigux/Makefile`

Keep the current Phase 7 reminder surface narrow and truthful:
- `string_helpers` stays the only directly readable Phase 7 helper implementation packet on current `master`
- `cmdline` stays parked under the current Phase 1 helper packet
- `rbtree` stays reviewable through the direct anchor note and survey only
- do not present the missing dedicated `argv_split` packet or the broader shared Phase 7 control routes as directly readable current-`master` evidence again until a fresh same-lane reread or republish materializes them
""",
                    encoding="utf-8",
                )
            else:
                target.write_text("placeholder\n", encoding="utf-8")

        file_count, missing_count, marker_count = check_repo(workspace)
        print("PHASE7_ARGV_SPLIT_REPO_REALITY_NOTE_SELF_TEST=pass")
        print("PHASE7_ARGV_SPLIT_REPO_REALITY_NOTE_SELF_TEST_CASE_COUNT=3")
        print(f"PHASE7_ARGV_SPLIT_REPO_REALITY_NOTE_SELF_TEST_FILE_COUNT={file_count}")
        print(f"PHASE7_ARGV_SPLIT_REPO_REALITY_NOTE_SELF_TEST_EXPECTED_MISSING_COUNT={missing_count}")
        print(f"PHASE7_ARGV_SPLIT_REPO_REALITY_NOTE_SELF_TEST_MARKER_COUNT={marker_count}")
    finally:
        shutil.rmtree(workspace)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    file_count, missing_count, marker_count = check_repo(Path(args.root))
    print("PHASE7_ARGV_SPLIT_REPO_REALITY_NOTE=pass")
    print(f"PHASE7_ARGV_SPLIT_REPO_REALITY_NOTE_FILE_COUNT={file_count}")
    print(f"PHASE7_ARGV_SPLIT_REPO_REALITY_NOTE_EXPECTED_MISSING_COUNT={missing_count}")
    print(f"PHASE7_ARGV_SPLIT_REPO_REALITY_NOTE_MARKER_COUNT={marker_count}")


if __name__ == "__main__":
    main()
