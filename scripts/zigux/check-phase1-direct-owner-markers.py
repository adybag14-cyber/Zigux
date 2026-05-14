#!/usr/bin/env python3

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()

REQUIRED_FILES = [
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]

DIRECT_OWNER_MARKERS = [
    "- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys and the already-landed shared closure-validator bitmap review markers it already owns`",
    "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, past-nbits, underscore-alias, Linux-style alias, and tail-word skip anchors plus the committed tail-clamped find_bit replay fields already emitted by the shared C harness and consumed by the shared fixture`",
    "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree iterator and cached-root coverage stay helper-local until exactly one dedicated shared iterator or cached-root leftmost-return fixture key lands`",
    "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
]

COMPANION_MARKERS = [
    "These four helper-specific owner markers are now exact-checked by `scripts/zigux/check-phase1-direct-owner-markers.py` on current `master`, so nearby Phase 1 follow-through should leave this owner-map packet parked unless a fresh reread shows direct-anchor drift or the dedicated checker itself drifts.",
]

CURRENT_REPO_REALITY_MARKERS = [
    "- the dedicated owner-map checker itself is now part of the live Phase 1 closure-maintenance packet beside `Documentation/zigux/phase1-closure.md`, the shared `phase1-validate` route, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`, so future reminder surfaces should keep that checker explicit instead of treating the owner-map note as docs-only context",
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=none`",
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=scripts/zigux/check-phase1-installer-companion-checks.py,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md`",
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md and Documentation/zigux/review-checklist.md now both keep the installer companion split explicit: --self-test replays the bounded checker logic, while the live checker route guards the shipped Phase 1 reminder surfaces without widening the counted docs-root packet line; leave that shared-reminder packet parked unless one of those three surfaces drifts`",
]

NEXT_STEP_MARKERS = [
    "## Next Bounded Step",
    "Start from `zigux/tests/fixtures/phase1_helper_manifest.json` and pick one helper family only.",
    "- If the helper sits in the shared-replay parked set, reread only its shared replay, fixture, build-route, and review-surface packet and land one drift repair if needed.",
    "- If the helper sits in the direct-anchor set, reread only that helper's direct anchors plus any already-committed shared fixture keys it owns and land one bounded follow-up if needed.",
    "- For `tools/lib/bitmap.zig`, do not replay the older closed exact-marker validator cue; current `master` already exact-requires and self-tests `PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW` and `PHASE1_BITMAP_LINUX_ALIAS_REVIEW`, so leave the bitmap closure-validator packet parked unless a fresh reread shows direct-anchor drift or committed shared replay drift.",
    "- For `tools/lib/bitmap.zig`, the earlier validator-summary wording follow-through is also closed on current `master`: `scripts/zigux/validate-phase1.py` already matches the live bitmap `review_packet_summary` in `zigux/tests/fixtures/phase1_helper_manifest.json`, so leave that validator packet parked unless a fresh reread shows new direct-anchor drift or committed shared replay drift.",
    "- The next smallest same-lane shared-validation step is closed for this owner-map packet: `scripts/zigux/check-phase1-direct-owner-markers.py` exact-checks the four `PHASE1_*_DIRECT_OWNER` lines in this note before any helper-local replay widening.",
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared reminder packet parked now that Documentation/zigux/review-checklist.md carries the same self-test-versus-live route-role wording as Documentation/zigux/README.md; if a future host-tools-alpha run reopens Phase 1, start from the helper-specific next-safe-step markers below instead of another shared reminder pass`",
    "- Treat the helper-specific next-safe-step markers below as the tie-breaker whenever multiple older saved helper cues still exist in Memory; choose the helper's own next-safe-step marker instead of widening into a neighboring helper family.",
    "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen the already-closed closure-validator or validator-summary packets by default`",
    "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, past-nbits, underscore-alias, Linux-style alias, or tail-word skip anchors, or for committed tail-clamped replay drift`",
    "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens for exactly one next widening only: a dedicated shared iterator fixture key or a dedicated cached-root leftmost-return fixture key, never both in the same run`",
    "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; do not reopen a generic closure-validator pass`",
    "- If those surfaces still agree on current `master`, leave the helper parked and do not widen to a second helper family in the same lane.",
]

MAKEFILE_MARKERS = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-direct-owner-markers.py",
]

WORKFLOW_MARKERS = [
    "- name: Self-test Phase 1 direct-owner markers",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "- name: Check Phase 1 direct-owner markers",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
]


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_exact_count_markers(text: str, label: str, markers: list[str], *, lstrip: bool = False) -> list[str]:
    lines = [line.lstrip() if lstrip else line for line in text.splitlines()]
    missing: list[str] = []
    for marker in markers:
        count = lines.count(marker)
        if count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={count}")
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    lane_note = (root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md").read_text(encoding="utf-8")
    makefile = (root / "zigux/Makefile").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    missing: list[str] = []
    missing.extend(collect_exact_count_markers(lane_note, "phase1_direct_owner_marker", DIRECT_OWNER_MARKERS))
    missing.extend(
        collect_exact_count_markers(
            lane_note,
            "phase1_direct_owner_current_repo_reality",
            CURRENT_REPO_REALITY_MARKERS,
        )
    )
    missing.extend(collect_exact_count_markers(lane_note, "phase1_direct_owner_companion", COMPANION_MARKERS))
    missing.extend(collect_exact_count_markers(lane_note, "phase1_direct_owner_next_step", NEXT_STEP_MARKERS))
    missing.extend(
        collect_exact_count_markers(
            makefile,
            "phase1_direct_owner_makefile",
            MAKEFILE_MARKERS,
            lstrip=True,
        )
    )
    missing.extend(
        collect_exact_count_markers(
            workflow,
            "phase1_direct_owner_workflow",
            WORKFLOW_MARKERS,
            lstrip=True,
        )
    )
    return missing


def make_fixture_root(root: Path) -> None:
    lane_note = root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md"
    lane_note.parent.mkdir(parents=True, exist_ok=True)
    lane_note.write_text(
        "\n".join(
            [
                "# Phase 1 Host-Helper Lane Sequencing",
                "",
                "## Current Repo Reality",
                "",
                *CURRENT_REPO_REALITY_MARKERS,
                "",
                "## Direct-Anchor Owner Map",
                "",
                *DIRECT_OWNER_MARKERS,
                "",
                *COMPANION_MARKERS,
                "",
                *NEXT_STEP_MARKERS,
                "",
                "## Footer",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    makefile = root / "zigux/Makefile"
    makefile.parent.mkdir(parents=True, exist_ok=True)
    makefile.write_text("\n".join(MAKEFILE_MARKERS) + "\n", encoding="utf-8")

    workflow = root / ".github/workflows/zigux-bootstrap.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text(
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test Phase 1 direct-owner markers",
                "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
                "      - name: Check Phase 1 direct-owner markers",
                "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def expect_missing_exact_count(root: Path, path: Path, original_text: str, label: str, marker: str, replacement: str, expected_count: int) -> None:
    path.write_text(original_text.replace(marker, replacement, 1), encoding="utf-8")
    missing = collect_missing_markers(root)
    assert f"{label}:{marker}:expected=1:actual={expected_count}" in missing
    path.write_text(original_text, encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_direct_owner_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        lane_note = root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md"
        makefile = root / "zigux/Makefile"
        workflow = root / ".github/workflows/zigux-bootstrap.yml"

        lane_note.unlink()
        assert collect_missing_files(root) == ["Documentation/zigux/phase1-host-helper-lane-sequencing.md"]
        case_count += 1

        make_fixture_root(root)
        makefile.unlink()
        assert collect_missing_files(root) == ["zigux/Makefile"]
        case_count += 1

        make_fixture_root(root)
        workflow.unlink()
        assert collect_missing_files(root) == [".github/workflows/zigux-bootstrap.yml"]
        case_count += 1

        make_fixture_root(root)
        makefile.write_text("".join(f"\t{marker}\n" for marker in MAKEFILE_MARKERS), encoding="utf-8")
        assert collect_missing_markers(root) == []
        case_count += 1

        make_fixture_root(root)
        workflow.write_text(
            "\n".join(
                f"      {marker}" if marker.startswith("- name:") else f"        {marker}"
                for marker in WORKFLOW_MARKERS
            )
            + "\n",
            encoding="utf-8",
        )
        assert collect_missing_markers(root) == []
        case_count += 1

        make_fixture_root(root)
        lane_note_text = lane_note.read_text(encoding="utf-8")
        for marker in DIRECT_OWNER_MARKERS:
            expect_missing_exact_count(
                root,
                lane_note,
                lane_note_text,
                "phase1_direct_owner_marker",
                marker,
                "",
                0,
            )
            case_count += 1
            expect_missing_exact_count(
                root,
                lane_note,
                lane_note_text,
                "phase1_direct_owner_marker",
                marker,
                marker + "\n" + marker,
                2,
            )
            case_count += 1

        make_fixture_root(root)
        lane_note_text = lane_note.read_text(encoding="utf-8")
        expect_missing_exact_count(
            root,
            lane_note,
            lane_note_text,
            "phase1_direct_owner_current_repo_reality",
            CURRENT_REPO_REALITY_MARKERS[1],
            "",
            0,
        )
        case_count += 1

        make_fixture_root(root)
        lane_note_text = lane_note.read_text(encoding="utf-8")
        expect_missing_exact_count(
            root,
            lane_note,
            lane_note_text,
            "phase1_direct_owner_current_repo_reality",
            CURRENT_REPO_REALITY_MARKERS[2],
            "",
            0,
        )
        case_count += 1

        make_fixture_root(root)
        lane_note_text = lane_note.read_text(encoding="utf-8")
        expect_missing_exact_count(
            root,
            lane_note,
            lane_note_text,
            "phase1_direct_owner_current_repo_reality",
            CURRENT_REPO_REALITY_MARKERS[3],
            CURRENT_REPO_REALITY_MARKERS[3] + "\n" + CURRENT_REPO_REALITY_MARKERS[3],
            2,
        )
        case_count += 1

        make_fixture_root(root)
        lane_note_text = lane_note.read_text(encoding="utf-8")
        expect_missing_exact_count(
            root,
            lane_note,
            lane_note_text,
            "phase1_direct_owner_next_step",
            NEXT_STEP_MARKERS[7],
            "",
            0,
        )
        case_count += 1

        make_fixture_root(root)
        lane_note_text = lane_note.read_text(encoding="utf-8")
        expect_missing_exact_count(
            root,
            lane_note,
            lane_note_text,
            "phase1_direct_owner_next_step",
            NEXT_STEP_MARKERS[7],
            NEXT_STEP_MARKERS[7] + "\n" + NEXT_STEP_MARKERS[7],
            2,
        )
        case_count += 1

        make_fixture_root(root)
        makefile_text = makefile.read_text(encoding="utf-8")
        for marker in MAKEFILE_MARKERS:
            expect_missing_exact_count(
                root,
                makefile,
                makefile_text,
                "phase1_direct_owner_makefile",
                marker,
                marker + "\n" + marker,
                2,
            )
            case_count += 1

        make_fixture_root(root)
        workflow_text = workflow.read_text(encoding="utf-8")
        for marker in WORKFLOW_MARKERS:
            expect_missing_exact_count(
                root,
                workflow,
                workflow_text,
                "phase1_direct_owner_workflow",
                marker,
                marker + "\n" + marker,
                2,
            )
            case_count += 1

        make_fixture_root(root)
        workflow_text = workflow.read_text(encoding="utf-8")
        expect_missing_exact_count(
            root,
            workflow,
            workflow_text,
            "phase1_direct_owner_workflow",
            WORKFLOW_MARKERS[1],
            "",
            0,
        )
        case_count += 1

    print("PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the dedicated Phase 1 direct-owner markers in the lane sequencing note and workflow."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_DIRECT_OWNER_MARKERS=fail")
        print("MISSING_PHASE1_DIRECT_OWNER_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_DIRECT_OWNER_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_DIRECT_OWNER_MARKERS=fail")
        print("MISSING_PHASE1_DIRECT_OWNER_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_DIRECT_OWNER_MARKERS_END")
        return 1

    print("PHASE1_DIRECT_OWNER_MARKERS=pass")
    print(f"PHASE1_DIRECT_OWNER_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_DIRECT_OWNER_REQUIRED_MARKER_COUNT="
        f"{len(DIRECT_OWNER_MARKERS) + len(CURRENT_REPO_REALITY_MARKERS) + len(COMPANION_MARKERS) + len(NEXT_STEP_MARKERS) + len(MAKEFILE_MARKERS) + len(WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
