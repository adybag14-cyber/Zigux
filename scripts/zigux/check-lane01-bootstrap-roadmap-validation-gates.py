#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

REQUIRED_LINES = (
    "## Recommended Validation Gates",
    "Every approved Zigux slice should declare and satisfy these gates.",
    "1. Build gate",
    "- deterministic artifact generation where applicable",
    "- pinned toolchain version",
    "- reproducible host-side outputs",
    "2. ABI gate",
    "- layout assertions",
    "- calling-convention checks",
    "- one blessed export surface",
    "3. Behavior gate",
    "- differential tests against current C behavior",
    "- fixture or known-vector parity",
    "4. Performance gate",
    "- perf thresholds for algorithmic helpers and driver-sensitive paths",
    "5. Runtime gate",
    "- load/unload behavior for runtime modules",
    "- teardown parity",
    "- queueing and failure-path coverage for drivers",
    "6. Rollback gate",
    "- named owner",
    "- explicit fallback to current C implementation",
    "- clear disable path when regressions appear",
    "## What Should Start Next in Zigux",
)

SECTION_ORDER = (
    "## Recommended Validation Gates",
    "1. Build gate",
    "2. ABI gate",
    "3. Behavior gate",
    "4. Performance gate",
    "5. Runtime gate",
    "6. Rollback gate",
    "## What Should Start Next in Zigux",
)


def read_roadmap(root: Path) -> str:
    return (root / ROADMAP_PATH).read_text(encoding="utf-8")


def collect_missing_lines(text: str) -> list[str]:
    return [line for line in REQUIRED_LINES if line not in text]


def section_order(text: str) -> str:
    positions: list[tuple[int, str]] = []
    for line in SECTION_ORDER:
        pos = text.find(line)
        if pos == -1:
            raise ValueError(f"missing required section marker: {line}")
        positions.append((pos, line))
    ordered = [line for _, line in sorted(positions)]
    return "->".join(
        marker.replace("## ", "").replace(". ", "").replace(" ", "")
        for marker in ordered
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Recommended Validation Gates

Every approved Zigux slice should declare and satisfy these gates.

1. Build gate
- deterministic artifact generation where applicable
- pinned toolchain version
- reproducible host-side outputs

2. ABI gate
- layout assertions
- calling-convention checks
- one blessed export surface

3. Behavior gate
- differential tests against current C behavior
- fixture or known-vector parity

4. Performance gate
- perf thresholds for algorithmic helpers and driver-sensitive paths

5. Runtime gate
- load/unload behavior for runtime modules
- teardown parity
- queueing and failure-path coverage for drivers

6. Rollback gate
- named owner
- explicit fallback to current C implementation
- clear disable path when regressions appear

## What Should Start Next in Zigux
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_validation_gates_") as tmp_dir:
        root = Path(tmp_dir)
        roadmap_path = root / ROADMAP_PATH

        _write(roadmap_path, sample_roadmap())
        text = read_roadmap(root)
        if collect_missing_lines(text):
            raise AssertionError("baseline validation-gates fixture should pass")
        if section_order(text) != (
            "RecommendedValidationGates->1Buildgate->2ABIgate->3Behaviorgate"
            "->4Performancegate->5Runtimegate->6Rollbackgate->WhatShouldStartNextinZigux"
        ):
            raise AssertionError("baseline section order should match")
        case_count += 1

        for missing_line in REQUIRED_LINES[:-1]:
            _write(roadmap_path, sample_roadmap().replace(f"{missing_line}\n", "", 1))
            text = read_roadmap(root)
            missing = collect_missing_lines(text)
            if missing != [missing_line]:
                raise AssertionError(
                    f"unexpected missing lines for {missing_line!r}: {missing!r}"
                )
            _write(roadmap_path, sample_roadmap())
            case_count += 1

        broken_order = sample_roadmap().replace(
            "2. ABI gate\n- layout assertions\n- calling-convention checks\n- one blessed export surface\n\n"
            "3. Behavior gate\n- differential tests against current C behavior\n- fixture or known-vector parity\n\n",
            "3. Behavior gate\n- differential tests against current C behavior\n- fixture or known-vector parity\n\n"
            "2. ABI gate\n- layout assertions\n- calling-convention checks\n- one blessed export surface\n\n",
            1,
        )
        _write(roadmap_path, broken_order)
        text = read_roadmap(root)
        observed = section_order(text)
        expected = (
            "RecommendedValidationGates->1Buildgate->3Behaviorgate->2ABIgate"
            "->4Performancegate->5Runtimegate->6Rollbackgate->WhatShouldStartNextinZigux"
        )
        if observed != expected:
            raise AssertionError(
                f"unexpected section order for reordered ABI/Behavior sections: {observed!r}"
            )
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 roadmap validation-gates packet remains intact."
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
        help="exercise the checker against synthetic fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    text = read_roadmap(args.root)
    missing = collect_missing_lines(text)
    if missing:
        for line in missing:
            print(f"ERROR: missing required line: {line}")
        return 1

    observed_order = section_order(text)
    print("Lane 01 roadmap Recommended Validation Gates check passed.")
    print("LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES=pass")
    print(
        "LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_REQUIRED_LINE_COUNT="
        f"{len(REQUIRED_LINES) - 1}"
    )
    print(
        "LANE01_BOOTSTRAP_ROADMAP_VALIDATION_GATES_SECTION_ORDER="
        f"{observed_order}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
