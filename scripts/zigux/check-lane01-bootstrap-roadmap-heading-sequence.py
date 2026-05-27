#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

EXPECTED_HEADINGS = (
    "## Purpose",
    "## Bootstrap Status Note",
    "## Inputs Reviewed",
    "## Bundle Normalization Notes",
    "## Licensing and Reuse Policy",
    "## Non-Negotiable Product Rules",
    "## How ZAR Should Feed Zigux",
    "## zigux-alpha Scope",
    "## Product Features by Phase",
    "## Phase 1: Alpha Host-Side Helpers",
    "## Phase 2: Toolchain and Kbuild Enablement",
    "## Phase 3: ABI and Interop Substrate",
    "## Phase 4: Differential Validation and Rollback",
    "## Phase 5: Samples and Reference Patterns",
    "## Phase 6: Greenfield Leaf Helpers",
    "## Phase 7: In-Kernel Leaf Libraries",
    "## Phase 8: Userspace-Adjacent Tooling Expansion",
    "## Phase 9: Runtime Pilot Modules",
    "## Phase 10: Virtio and Lab Drivers",
    "## Phase 11: Simple Production Drivers",
    "## Phase 12: Complex Production Drivers and Heavy Helper Consumers",
    "## Phase 13: Shared Subsystem Helpers",
    "## Phase 14: Core-Adjacent Bounded Internals",
    "## Phase 15: Full-Parity Blockers and Long-Term Governance",
    "## Freeze Map for Near- and Mid-Term Planning",
    "## Workstreams and Ownership Model",
    "## Risk Register That Must Drive Prioritization",
    "## First Commit and Push Sequence for Zigux",
    "## Recommended Validation Gates",
    "## What Should Start Next in Zigux",
    "## Final Direction",
)


def extract_headings(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    return [line.strip() for line in roadmap.splitlines() if line.startswith("## ")]


def collect_errors(root: Path) -> list[str]:
    headings = extract_headings(root)
    errors: list[str] = []

    if headings != list(EXPECTED_HEADINGS):
        if len(headings) != len(EXPECTED_HEADINGS):
            errors.append(
                "heading-count:"
                f"expected={len(EXPECTED_HEADINGS)} actual={len(headings)}"
            )

        for index, expected in enumerate(EXPECTED_HEADINGS):
            if index >= len(headings):
                errors.append(f"missing-index:{index + 1}:{expected}")
                continue

            actual = headings[index]
            if actual != expected:
                errors.append(
                    f"heading-mismatch:{index + 1}:expected={expected}:actual={actual}"
                )

        if len(headings) > len(EXPECTED_HEADINGS):
            for index in range(len(EXPECTED_HEADINGS), len(headings)):
                errors.append(f"unexpected-index:{index + 1}:{headings[index]}")

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return "\n".join(
        ["# ZAR to Zigux Product Roadmap", ""]
        + [f"{heading}\n\nplaceholder" for heading in EXPECTED_HEADINGS]
        + [""]
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_heading_sequence_") as tmp_dir:
        root = Path(tmp_dir)
        roadmap_path = root / ROADMAP_PATH

        _write(roadmap_path, _sample_roadmap())
        if collect_errors(root):
            raise AssertionError("baseline heading fixture should pass")
        case_count += 1

        _write(
            roadmap_path,
            _sample_roadmap().replace(
                "## Bootstrap Status Note\n\nplaceholder\n",
                "",
                1,
            ),
        )
        errors = collect_errors(root)
        if not any(error.startswith("heading-count:") for error in errors):
            raise AssertionError(f"missing heading should change heading count: {errors}")
        if not any(
            error.startswith("heading-mismatch:2:expected=## Bootstrap Status Note")
            for error in errors
        ):
            raise AssertionError(f"missing heading should shift heading 2: {errors}")
        case_count += 1

        _write(
            roadmap_path,
            _sample_roadmap().replace(
                "## Inputs Reviewed\n\nplaceholder\n## Bundle Normalization Notes\n\nplaceholder",
                "## Bundle Normalization Notes\n\nplaceholder\n## Inputs Reviewed\n\nplaceholder",
                1,
            ),
        )
        errors = collect_errors(root)
        if not any(
            error.startswith("heading-mismatch:3:expected=## Inputs Reviewed")
            for error in errors
        ):
            raise AssertionError(f"reordered headings should trip index 3: {errors}")
        if not any(
            error.startswith(
                "heading-mismatch:4:expected=## Bundle Normalization Notes"
            )
            for error in errors
        ):
            raise AssertionError(f"reordered headings should trip index 4: {errors}")
        case_count += 1

        _write(
            roadmap_path,
            _sample_roadmap().replace(
                "## Product Features by Phase\n\nplaceholder\n",
                "## Product Features by Phase\n\nplaceholder\n## Surprise Heading\n\nplaceholder\n",
                1,
            ),
        )
        errors = collect_errors(root)
        if not any(error.startswith("heading-count:") for error in errors):
            raise AssertionError(f"extra heading should change heading count: {errors}")
        if not any(
            error.startswith(
                "heading-mismatch:10:expected=## Phase 1: Alpha Host-Side Helpers:actual=## Surprise Heading"
            )
            for error in errors
        ):
            raise AssertionError(f"extra heading should displace Phase 1: {errors}")
        case_count += 1

        _write(
            roadmap_path,
            _sample_roadmap().replace(
                "## Final Direction",
                "## Final Directions",
                1,
            ),
        )
        errors = collect_errors(root)
        if errors != [
            "heading-mismatch:31:expected=## Final Direction:actual=## Final Directions"
        ]:
            raise AssertionError(f"rewritten final heading mismatch: {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_HEADING_SEQUENCE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_HEADING_SEQUENCE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 bootstrap roadmap top-level heading sequence."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the bootstrap roadmap",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic roadmap fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_errors(args.root)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_HEADING_SEQUENCE=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_HEADING_COUNT={len(EXPECTED_HEADINGS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
