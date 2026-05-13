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
    "- `PHASE1_STRING_DIRECT_OWNER=string keeps memparse safety, prefix and suffix boundary, C-string list lookup, counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
]

COMPANION_MARKERS = [
    "These four helper-specific owner markers are now exact-checked by `scripts/zigux/check-phase1-direct-owner-markers.py` on current `master`, so nearby Phase 1 follow-through should leave this owner-map packet parked unless a fresh reread shows direct-anchor drift or the dedicated checker itself drifts.",
    "- The next smallest same-lane shared-validation step is closed for this owner-map packet: `scripts/zigux/check-phase1-direct-owner-markers.py` exact-checks the four `PHASE1_*_DIRECT_OWNER` lines in this note before any helper-local replay widening.",
]

NEXT_STEP_MARKERS = [
    "## Next Bounded Step",
    "Start from `zigux/tests/fixtures/phase1_helper_manifest.json` and pick one helper family only.",
    "- If the helper sits in the shared-replay parked set, reread only its shared replay, fixture, build-route, and review-surface packet and land one drift repair if needed.",
    "- If the helper sits in the direct-anchor set, reread only that helper's direct anchors plus any already-committed shared fixture keys it owns and land one bounded follow-up if needed.",
    "- For `tools/lib/bitmap.zig`, do not replay the older closed exact-marker validator cue; current `master` already exact-requires and self-tests `PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW` and `PHASE1_BITMAP_LINUX_ALIAS_REVIEW`, so leave the bitmap closure-validator packet parked unless a fresh reread shows direct-anchor drift or committed shared replay drift.",
    "- For `tools/lib/bitmap.zig`, the earlier validator-summary wording follow-through is also closed on current `master`: `scripts/zigux/validate-phase1.py` already matches the live bitmap `review_packet_summary` in `zigux/tests/fixtures/phase1_helper_manifest.json`, so leave that validator packet parked unless a fresh reread shows new direct-anchor drift or committed shared replay drift.",
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


def collect_exact_count_markers(
    text: str,
    label: str,
    markers: list[str],
    *,
    lstrip: bool = False,
) -> list[str]:
    missing: list[str] = []
    lines = [line.lstrip() if lstrip else line for line in text.splitlines()]
    for marker in markers:
        count = lines.count(marker)
        if count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={count}")
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    lane_note = (root / "Documentation" / "zigux" / "phase1-host-helper-lane-sequencing.md").read_text(
        encoding="utf-8"
    )
    makefile = (root / "zigux" / "Makefile").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    missing: list[str] = []
    missing.extend(collect_exact_count_markers(lane_note, "phase1_direct_owner_marker", DIRECT_OWNER_MARKERS))
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
    lane_note = root / "Documentation" / "zigux" / "phase1-host-helper-lane-sequencing.md"
    lane_note.parent.mkdir(parents=True, exist_ok=True)
    lane_note.write_text(
        "\n".join(
            [
                "# Phase 1 Host-Helper Lane Sequencing",
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

    makefile = root / "zigux" / "Makefile"
    makefile.parent.mkdir(parents=True, exist_ok=True)
    makefile.write_text("\n".join(MAKEFILE_MARKERS) + "\n", encoding="utf-8")

    workflow = root / ".github" / "workflows" / "zigux-bootstrap.yml"
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


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_direct_owner_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 1

        lane_note = root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md"
        lane_note.unlink()
        assert collect_missing_files(root) == ["Documentation/zigux/phase1-host-helper-lane-sequencing.md"]
        case_count += 1

        make_fixture_root(root)
        makefile = root / "zigux/Makefile"
        makefile.unlink()
        assert collect_missing_files(root) == ["zigux/Makefile"]
        case_count += 1

        make_fixture_root(root)
        workflow = root / ".github/workflows/zigux-bootstrap.yml"
        workflow.unlink()
        assert collect_missing_files(root) == [".github/workflows/zigux-bootstrap.yml"]
        case_count += 1

        make_fixture_root(root)
        makefile.writeText = None
        makefile.write_text("".join(f"\t{marker}\n" for marker in MAKEFILE_MARKERS), encoding="utf-8")
        assert collect_missing_markers(root) == []
        case_count += 1

        make_fixture_root(root)
        workflow.write_text(
            "\n".join(f"      {marker}" if marker.startswith("- name:") else f"        {marker}" for marker in WORKFLOW_MARKERS)
            + "\n",
            encoding="utf-8",
        )
        assert collect_missing_markers(root) == []
        case_count += 1

        make_fixture_root(root)
        lane_note.write_text(
            lane_note.read_text(encoding="utf-8").replace(DIRECT_OWNER_MARKERS[0] + "\n", "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"phase1_direct_owner_marker:{DIRECT_OWNER_MARKERS[0]}:expected=1:actual=0" in missing
        )
        case_count += 1

        make_fixture_root(root)
        lane_note.write_text(
            lane_note.read_text(encoding="utf-8").replace(
                DIRECT_OWNER_MARKERS[1],
                DIRECT_OWNER_MARKERS[1] + "\n" + DIRECT_OWNER_MARKERS[1],
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"phase1_direct_owner_marker:{DIRECT_OWNER_MARKERS[1]}:expected=1:actual=2" in missing
        )
        case_count += 1

        make_fixture_root(root)
        lane_note.write_text(
            lane_note.read_text(encoding="utf-8").replace(COMPANION_MARKERS[0] + "\n", "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"phase1_direct_owner_companion:{COMPANION_MARKERS[0]}:expected=1:actual=0" in missing
        )
        case_count += 1

        make_fixture_root(root)
        lane_note.write_text(
            lane_note.read_text(encoding="utf-8").replace(NEXT_STEP_MARKERS[1] + "\n", "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"phase1_direct_owner_next_step:{NEXT_STEP_MARKERS[1]}:expected=1:actual=0" in missing
        )
        case_count += 1

        make_fixture_root(root)
        lane_note.write_text(
            lane_note.read_text(encoding="utf-8").replace(
                NEXT_STEP_MARKERS[4],
                NEXT_STEP_MARKERS[4] + "\n" + NEXT_STEP_MARKERS[4],
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"phase1_direct_owner_next_step:{NEXT_STEP_MARKERS[4]}:expected=1:actual=2"
            in missing
        )
        case_count += 1

        make_fixture_root(root)
        lane_note.write_text(
            lane_note.read_text(encoding="utf-8").replace(NEXT_STEP_MARKERS[5] + "\n", "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"phase1_direct_owner_next_step:{NEXT_STEP_MARKERS[5]}:expected=1:actual=0"
            in missing
        )
        case_count += 1

        make_fixture_root(root)
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace(MAKEFILE_MARKERS[0] + "\n", "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"phase1_direct_owner_makefile:{MAKEFILE_MARKERS[0]}:expected=1:actual=0" in missing
        )
        case_count += 1

        make_fixture_root(root)
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace(
                MAKEFILE_MARKERS[1],
                MAKEFILE_MARKERS[1] + "\n" + MAKEFILE_MARKERS[1],
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"phase1_direct_owner_makefile:{MAKEFILE_MARKERS[1]}:expected=1:actual=2"
            in missing
        )
        case_count += 1

        make_fixture_root(root)
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(WORKFLOW_MARKERS[1] + "\n", "", 1),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"phase1_direct_owner_workflow:{WORKFLOW_MARKERS[1]}:expected=1:actual=0" in missing
        )
        case_count += 1

        make_fixture_root(root)
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                WORKFLOW_MARKERS[3],
                WORKFLOW_MARKERS[3] + "\n        " + WORKFLOW_MARKERS[3],
                1,
            ),
            encoding="utf-8",
        )
        missing = collect_missing_markers(root)
        assert (
            f"phase1_direct_owner_workflow:{WORKFLOW_MARKERS[3]}:expected=1:actual=2" in missing
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
        f"{len(DIRECT_OWNER_MARKERS) + len(COMPANION_MARKERS) + len(NEXT_STEP_MARKERS) + len(MAKEFILE_MARKERS) + len(WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())