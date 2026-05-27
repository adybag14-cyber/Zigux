#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HELPER_PATH = Path("lib/devres_scatterlist.zig")
NOTE_PATH = Path("Documentation/zigux/phase13-devres-scatterlist-planner.md")
SLICE_PATH = Path("Documentation/zigux/phase13-devres-scatterlist-slice.md")
MANIFEST_PATH = Path("zigux/tests/phase13_devres_scatterlist_planner_manifest.json")
REPLAY_PATH = Path("zigux/tests/phase13_devres_scatterlist.zig")
BUILD_PATH = Path("zigux/tests/phase13_devres_scatterlist_build.zig")

REQUIRED_MARKERS = {
    HELPER_PATH: [
        ".provides_scatterlist_lifetime_planning = true",
        ".provides_scatterlist_table_teardown_planning = true",
        ".touches_live_dma = false",
        ".touches_live_scatterlist = false",
        "pub fn planManagedScatterlistMap",
        "pub fn scatterlistReleaseMatches",
        "pub fn planManagedScatterlistUnmap",
        "pub fn planManagedScatterlistTableTeardown",
    ],
    NOTE_PATH: [
        "pure scatterlist lifetime planning surface",
        "`Documentation/zigux/phase13-devres-scatterlist-slice.md` keeps the helper-local scope and non-goals aligned with this planner note, the manifest, and the replay",
        "`zigux/tests/phase13_devres_scatterlist_build.zig` keeps the dedicated build shard aligned with the helper-first scatterlist replay",
        "retains detach-time unmap ownership on success",
        "failed mapping frees the release record",
        "warn-on-release-miss outcome",
        "helper-first `sg_table` free eligibility stays reviewable",
        "requires unmap-before-free planning",
        "warn rather than claiming live `sg_table` lifecycle mutation",
        "dma_map_sgtable()",
        "sg_table",
        "zig build test --build-file zigux/tests/phase13_devres_scatterlist_build.zig",
    ],
    SLICE_PATH: [
        "helper-first scatterlist planner beside the existing `lib/devres.zig` and `lib/devres_dma_coherent.zig` packet",
        "focused replay: `zigux/tests/phase13_devres_scatterlist.zig`",
        "provides_scatterlist_table_teardown_planning = true",
        "`planManagedScatterlistTableTeardown()` models helper-first `sg_table` teardown readiness",
        "no live `dma_map_sgtable()` or `dma_unmap_sgtable()` execution",
        "no `struct scatterlist`, `sg_table`, or `sg_*` iteration helpers",
        "no live `sg_free_table()` lifecycle mutation or `sg_alloc_table()` ownership claims",
    ],
    MANIFEST_PATH: [
        "\"packet\": \"phase13-devres-scatterlist-planner\"",
        "\"status\": \"starter_landed\"",
        "\"scatterlist_lifetime_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\"",
        "\"scatterlist_table_teardown_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\"",
        "\"slice_note_owner\": \"Documentation/zigux/phase13-devres-scatterlist-slice.md\"",
        "\"build_shard_owner\": \"zigux/tests/phase13_devres_scatterlist_build.zig\"",
        "\"validation_guard\": \"scripts/zigux/check-phase13-devres-scatterlist-planner.py\"",
        "planManagedScatterlistTableTeardown",
        "helper-first `sg_table` free eligibility stays reviewable",
        "\"id\": \"phase13-devres-live-scatterlist-ownership\"",
        "\"id\": \"phase13-devres-live-sg-table-lifecycle\"",
        "\"id\": \"phase13-devres-generic-dma-map-family\"",
    ],
    REPLAY_PATH: [
        "phase13 devres descriptor records helper-first scatterlist planning",
        "phase13 devres scatterlist table teardown becomes free-ready once mapped entries drain",
        "phase13 devres scatterlist table teardown requires unmap before free when mapped entries remain",
        "phase13 devres scatterlist table teardown warns when the release record is missing",
        "phase13 devres scatterlist table teardown warns on overmapped release drift",
        "phase13 devres scatterlist planner checker stays packet-local",
    ],
    BUILD_PATH: [
        "phase13-devres-scatterlist-tests",
        "Run Phase 13 devres scatterlist helper tests",
        "../../lib/devres_scatterlist.zig",
        "phase13_devres_scatterlist.zig",
    ],
}

FORBIDDEN_HELPER_MARKERS = [
    "dma_map_sg(",
    "dma_unmap_sg(",
    "dma_map_sgtable(",
    "sg_alloc_table(",
    "sg_free_table(",
    "sg_dma_address(",
    "sg_dma_len(",
    "struct scatterlist",
    "sg_table",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_MARKERS:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel.as_posix()}")
    if issues:
        return issues

    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker not in text:
                issues.append(f"{rel.as_posix()}:missing_marker:{marker}")

    helper_text = read_text(root / HELPER_PATH)
    for marker in FORBIDDEN_HELPER_MARKERS:
        if marker in helper_text:
            issues.append(f"helper:unexpected_marker:{marker}")

    return issues


def seed_fixture_tree(root: Path) -> None:
    for rel, markers in REQUIRED_MARKERS.items():
        write_text(root / rel, "\n".join(markers) + "\n")


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase13-devres-scatterlist-planner-") as tmp:
        root = Path(tmp)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        (root / NOTE_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing_file:{NOTE_PATH.as_posix()}"],
            "missing_note_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        (root / BUILD_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing_file:{BUILD_PATH.as_posix()}"],
            "missing_build_shard_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / HELPER_PATH, "\n".join(REQUIRED_MARKERS[HELPER_PATH] + ["dma_map_sg("]) + "\n")
        assert_only(
            validate(root),
            ["helper:unexpected_marker:dma_map_sg("],
            "unexpected_live_dma_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / MANIFEST_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[MANIFEST_PATH]
                if marker != "\"scatterlist_table_teardown_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\""
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "zigux/tests/phase13_devres_scatterlist_planner_manifest.json:missing_marker:\"scatterlist_table_teardown_owner\": \"zigux/tests/phase13_devres_scatterlist.zig\""
            ],
            "missing_table_owner_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / REPLAY_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[REPLAY_PATH]
                if marker != "phase13 devres scatterlist table teardown warns on overmapped release drift"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "zigux/tests/phase13_devres_scatterlist.zig:missing_marker:phase13 devres scatterlist table teardown warns on overmapped release drift"
            ],
            "missing_replay_case_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_SCATTERLIST_PLANNER_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_SCATTERLIST_PLANNER_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(issue)
        print("PHASE13_DEVRES_SCATTERLIST_PLANNER=fail")
        return 1

    print("PHASE13_DEVRES_SCATTERLIST_PLANNER=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
