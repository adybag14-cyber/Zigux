#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE2_MARKERS = (
    "## Phase 2: Toolchain and Kbuild Enablement",
    "Primary product goal:",
    "- make Zigux buildable, reproducible, and acceptable inside Linux-style workflows",
    "Primary Linux targets:",
    "- `scripts/basic/fixdep.c`",
    "- `scripts/genksyms/genksyms.c`",
    "- `scripts/kconfig/conf.c`",
    "- `scripts/kconfig/confdata.c`",
    "Required Zigux features:",
    "- compiler pinning and upgrade policy",
    "- deterministic artifact checks",
    "- selected dual implementations",
    "- wrapper-first path for parser-heavy tooling",
    "- cross-arch build matrix",
    "Recommended Zigux destinations:",
    "- `scripts/zigux/fixdep.zig`",
    "- `scripts/zigux/genksyms.zig`",
    "- `scripts/zigux/kconfig/conf_bridge.zig`",
    "- `scripts/zigux/kconfig/confdata_bridge.zig`",
    "- `zigux/Makefile`",
    "Why ZAR matters here:",
    "- ZAR’s insistence on freshness checks, pinned validation, parity gates, and CI-after-push discipline should become default Zigux behavior.",
)

PHASE2_SECTION_ORDER = (
    "## Product Features by Phase",
    "## Phase 2: Toolchain and Kbuild Enablement",
    "## Phase 3: ABI and Interop Substrate",
)


def _phase2_slice(roadmap: str) -> str:
    start = roadmap.find(PHASE2_SECTION_ORDER[1])
    end = roadmap.find(PHASE2_SECTION_ORDER[2])
    if start == -1 or end == -1 or end <= start:
        return roadmap
    return roadmap[start:end]


def collect_phase2_drift(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    missing: list[str] = []
    for marker in PHASE2_MARKERS:
        if marker not in roadmap:
            missing.append(marker)

    order_positions: list[int] = []
    for marker in PHASE2_SECTION_ORDER:
        position = roadmap.find(marker)
        if position == -1:
            missing.append(f"section-order:{marker}")
        else:
            order_positions.append(position)
    if len(order_positions) == len(PHASE2_SECTION_ORDER) and order_positions != sorted(order_positions):
        missing.append("section-order:ProductFeaturesByPhase->Phase2->Phase3")

    return missing


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Product Features by Phase

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
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase2_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_phase2_drift(root):
            raise AssertionError("baseline roadmap Phase 2 fixture should pass")
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("## Phase 2: Toolchain and Kbuild Enablement\n\n", "", 1),
        )
        missing = collect_phase2_drift(root)
        if "## Phase 2: Toolchain and Kbuild Enablement" not in missing:
            raise AssertionError(f"missing Phase 2 heading not reported: {missing}")
        if "section-order:## Phase 2: Toolchain and Kbuild Enablement" not in missing:
            raise AssertionError(f"missing Phase 2 order anchor not reported: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- `scripts/kconfig/confdata.c`\n", "", 1),
        )
        missing = collect_phase2_drift(root)
        expected = ["- `scripts/kconfig/confdata.c`"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for Linux targets case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace("- `scripts/zigux/kconfig/confdata_bridge.zig`\n", "", 1),
        )
        missing = collect_phase2_drift(root)
        expected = ["- `scripts/zigux/kconfig/confdata_bridge.zig`"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for destinations case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "- ZAR’s insistence on freshness checks, pinned validation, parity gates, and CI-after-push discipline should become default Zigux behavior.\n",
                "",
                1,
            ),
        )
        missing = collect_phase2_drift(root)
        expected = [
            "- ZAR’s insistence on freshness checks, pinned validation, parity gates, and CI-after-push discipline should become default Zigux behavior."
        ]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for Why ZAR matters case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "## Product Features by Phase\n\n## Phase 2: Toolchain and Kbuild Enablement\n\n",
                "## Phase 2: Toolchain and Kbuild Enablement\n\n## Product Features by Phase\n\n",
                1,
            ),
        )
        missing = collect_phase2_drift(root)
        expected = ["section-order:ProductFeaturesByPhase->Phase2->Phase3"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for section order case: {missing}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE2_TOOLCHAIN_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE2_TOOLCHAIN_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap Phase 2 toolchain packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic roadmap Phase 2 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_phase2_drift(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: {item}")
        return 1

    roadmap = (args.root / ROADMAP_PATH).read_text(encoding="utf-8")
    phase2 = _phase2_slice(roadmap)
    print("Lane 01 roadmap Phase 2 toolchain check passed.")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE2_TOOLCHAIN_REQUIRED_LINE_COUNT={len(PHASE2_MARKERS)}")
    print("LANE01_BOOTSTRAP_ROADMAP_PHASE2_TOOLCHAIN_SECTION_ORDER=ProductFeaturesByPhase->Phase2->Phase3")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_PHASE2_TOOLCHAIN_PRIMARY_TARGET_COUNT="
        f"{phase2.count('- `scripts/basic/') + phase2.count('- `scripts/genksyms/') + phase2.count('- `scripts/kconfig/')}"
    )
    print(
        "LANE01_BOOTSTRAP_ROADMAP_PHASE2_TOOLCHAIN_DESTINATION_COUNT="
        f"{phase2.count('- `scripts/zigux/') + phase2.count('- `zigux/Makefile`')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
