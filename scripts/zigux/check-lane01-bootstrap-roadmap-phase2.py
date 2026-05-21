#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

HEADING = "## Phase 2: Toolchain and Kbuild Enablement"
INTRO_LABEL = "Primary product goal:"
INTRO_BULLET = "- make Zigux buildable, reproducible, and acceptable inside Linux-style workflows"
TARGETS_LABEL = "Primary Linux targets:"
TARGET_BULLETS = (
    "- `scripts/basic/fixdep.c`",
    "- `scripts/genksyms/genksyms.c`",
    "- `scripts/kconfig/conf.c`",
    "- `scripts/kconfig/confdata.c`",
)
FEATURES_LABEL = "Required Zigux features:"
FEATURE_BULLETS = (
    "- compiler pinning and upgrade policy",
    "- deterministic artifact checks",
    "- selected dual implementations",
    "- wrapper-first path for parser-heavy tooling",
    "- cross-arch build matrix",
)
DESTINATIONS_LABEL = "Recommended Zigux destinations:"
DESTINATION_BULLETS = (
    "- `scripts/zigux/fixdep.zig`",
    "- `scripts/zigux/genksyms.zig`",
    "- `scripts/zigux/kconfig/conf_bridge.zig`",
    "- `scripts/zigux/kconfig/confdata_bridge.zig`",
    "- `zigux/Makefile`",
)
WHY_LABEL = "Why ZAR matters here:"
WHY_BULLET = (
    "- ZAR’s insistence on freshness checks, pinned validation, parity gates, "
    "and CI-after-push discipline should become default Zigux behavior."
)
PREVIOUS_HEADING = "## Phase 1: Alpha Host-Side Helpers"
NEXT_HEADING = "## Phase 3: ABI and Interop Substrate"
PHASE2_PACKET_MARKERS = (
    HEADING,
    INTRO_LABEL,
    INTRO_BULLET,
    TARGETS_LABEL,
    *TARGET_BULLETS,
    FEATURES_LABEL,
    *FEATURE_BULLETS,
    DESTINATIONS_LABEL,
    *DESTINATION_BULLETS,
    WHY_LABEL,
    WHY_BULLET,
)


def _read_roadmap(root: Path) -> str:
    return (root / ROADMAP_PATH).read_text(encoding="utf-8")


def _phase2_block(root: Path) -> str:
    roadmap = _read_roadmap(root)
    current_index = roadmap.find(HEADING)
    next_index = roadmap.find(NEXT_HEADING)
    if current_index == -1 or next_index == -1:
        return ""
    return roadmap[current_index:next_index]


def collect_missing_markers(root: Path) -> list[str]:
    roadmap = _read_roadmap(root)
    missing: list[str] = []
    for marker in PHASE2_PACKET_MARKERS:
        if marker not in roadmap:
            missing.append(marker)
    return missing


def has_expected_heading_order(root: Path) -> bool:
    roadmap = _read_roadmap(root)
    previous_index = roadmap.find(PREVIOUS_HEADING)
    current_index = roadmap.find(HEADING)
    next_index = roadmap.find(NEXT_HEADING)
    return previous_index < current_index < next_index


def has_expected_packet_order(root: Path) -> bool:
    block = _phase2_block(root)
    if not block:
        return False

    last_index = -1
    for marker in PHASE2_PACKET_MARKERS:
        marker_index = block.find(marker)
        if marker_index == -1 or marker_index <= last_index:
            return False
        last_index = marker_index
    return True


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Phase 1: Alpha Host-Side Helpers

Primary product goal:
- prove that Zig can live in-tree on low-risk host-side helper code

## Phase 2: Toolchain and Kbuild Enablement

Primary product goal:
- make Zigux buildable, reproducible, and acceptable inside Linux-style workflows

Primary Linux targets:
- `scripts/basic/fixdep.c`
- `scripts/genksyms/genksyms.c`
- `scripts/kconfig/conf.c`
- `scripts/kconfig/confdata.c`

Required Zigux features:
- compiler pinning and upgrade policy
- deterministic artifact checks
- selected dual implementations
- wrapper-first path for parser-heavy tooling
- cross-arch build matrix

Recommended Zigux destinations:
- `scripts/zigux/fixdep.zig`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `zigux/Makefile`

Why ZAR matters here:
- ZAR’s insistence on freshness checks, pinned validation, parity gates, and CI-after-push discipline should become default Zigux behavior.

## Phase 3: ABI and Interop Substrate

Primary product goal:
- define the permanent C/Zigux boundary
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase2_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_missing_markers(root):
            raise AssertionError("baseline Lane 01 Phase 2 roadmap fixture should pass")
        if not has_expected_heading_order(root):
            raise AssertionError("baseline Lane 01 Phase 2 heading order should pass")
        if not has_expected_packet_order(root):
            raise AssertionError("baseline Lane 01 Phase 2 packet order should pass")
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{HEADING}\n\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [HEADING]:
            raise AssertionError(f"unexpected missing markers for heading case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{INTRO_BULLET}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [INTRO_BULLET]:
            raise AssertionError(f"unexpected missing markers for intro case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{TARGET_BULLETS[3]}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [TARGET_BULLETS[3]]:
            raise AssertionError(f"unexpected missing markers for target case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{FEATURE_BULLETS[4]}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [FEATURE_BULLETS[4]]:
            raise AssertionError(f"unexpected missing markers for feature case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(f"{DESTINATION_BULLETS[4]}\n", "", 1),
        )
        missing = collect_missing_markers(root)
        if missing != [DESTINATION_BULLETS[4]]:
            raise AssertionError(f"unexpected missing markers for destination case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{WHY_BULLET}\n", "", 1))
        missing = collect_missing_markers(root)
        if missing != [WHY_BULLET]:
            raise AssertionError(f"unexpected missing markers for rationale case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                f"{PREVIOUS_HEADING}\n\nPrimary product goal:\n- prove that Zig can live in-tree on low-risk host-side helper code\n\n{HEADING}",
                f"{HEADING}\n\n{PREVIOUS_HEADING}",
                1,
            ),
        )
        if collect_missing_markers(root):
            raise AssertionError("reordered-heading fixture should keep all markers present")
        if has_expected_heading_order(root):
            raise AssertionError("reordered-heading fixture should fail heading order")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                f"{DESTINATIONS_LABEL}\n{DESTINATION_BULLETS[0]}\n{DESTINATION_BULLETS[1]}\n{DESTINATION_BULLETS[2]}\n{DESTINATION_BULLETS[3]}\n{DESTINATION_BULLETS[4]}\n\n{WHY_LABEL}",
                f"{WHY_LABEL}\n{WHY_BULLET}\n\n{DESTINATIONS_LABEL}\n{DESTINATION_BULLETS[0]}\n{DESTINATION_BULLETS[1]}\n{DESTINATION_BULLETS[2]}\n{DESTINATION_BULLETS[3]}\n{DESTINATION_BULLETS[4]}",
                1,
            ),
        )
        if collect_missing_markers(root):
            raise AssertionError("reordered-packet fixture should keep all markers present")
        if has_expected_packet_order(root):
            raise AssertionError("reordered-packet fixture should fail packet order")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE2_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE2_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Lane 01 roadmap Phase 2 packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the zigux-alpha roadmap file",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Lane 01 Phase 2 roadmap fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: missing marker: {item}")
        return 1

    if not has_expected_heading_order(args.root):
        print("ERROR: unexpected heading order for Phase 1, Phase 2, and Phase 3")
        return 1

    if not has_expected_packet_order(args.root):
        print("ERROR: unexpected marker order inside the Phase 2 roadmap packet")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE2=pass")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_PHASE2_REQUIRED_LINE_COUNT="
        f"{len(TARGET_BULLETS) + len(FEATURE_BULLETS) + len(DESTINATION_BULLETS) + 8}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
