#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

SECTION_ORDER = (
    "## How ZAR Should Feed Zigux",
    "## zigux-alpha Scope",
    "## Product Features by Phase",
)

SCOPE_MARKERS = (
    "`zigux-alpha/` is the staging area for:",
    "- roadmap and phase sequencing",
    "- source mapping",
    "- validation strategy",
    "- freeze map",
    "- first commit ledger",
    "- workstream ownership",
    "`zigux-alpha/` is not the final home for:",
    "- subsystem ports",
    "- runtime helpers",
    "- drivers",
    "- bindings",
    "- UAPI shims",
    "Those should eventually land in:",
    "- `tools/lib/*.zig`",
    "- `scripts/zigux/`",
    "- `zigux/`",
    "- `Documentation/zigux/`",
    "- `samples/zigux/`",
    "- `lib/*.zig`",
    "- `drivers/*/*.zig`",
    "- `fs/*.zig`",
    "- `security/*/*.zig`",
)


def collect_missing_markers(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")

    missing: list[str] = []
    positions: list[int] = []
    for heading in SECTION_ORDER:
        position = roadmap.find(heading)
        if position == -1:
            missing.append(f"roadmap-heading:{heading}")
        positions.append(position)

    if all(position != -1 for position in positions) and positions != sorted(positions):
        missing.append("roadmap-section-order:HowZARShouldFeedZigux->ziguxAlphaScope->ProductFeaturesByPhase")

    for marker in SCOPE_MARKERS:
        if marker not in roadmap:
            missing.append(f"roadmap-scope:{marker}")

    return missing


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## How ZAR Should Feed Zigux

ZAR should not try to become Zigux.

## zigux-alpha Scope

`zigux-alpha/` is the staging area for:
- roadmap and phase sequencing
- source mapping
- validation strategy
- freeze map
- first commit ledger
- workstream ownership

`zigux-alpha/` is not the final home for:
- subsystem ports
- runtime helpers
- drivers
- bindings
- UAPI shims

Those should eventually land in:
- `tools/lib/*.zig`
- `scripts/zigux/`
- `zigux/`
- `Documentation/zigux/`
- `samples/zigux/`
- `lib/*.zig`
- `drivers/*/*.zig`
- `fs/*.zig`
- `security/*/*.zig`

## Product Features by Phase

## Phase 1: Alpha Host-Side Helpers
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_alpha_scope_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_missing_markers(root):
            raise AssertionError("baseline zigux-alpha scope fixture should pass")
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("## zigux-alpha Scope\n\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-heading:## zigux-alpha Scope"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for scope heading case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        ordered = _sample_roadmap()
        product_features = "\n## Product Features by Phase\n\n## Phase 1: Alpha Host-Side Helpers\n"
        misordered = ordered.replace(product_features, "\n", 1).replace(
            "## zigux-alpha Scope",
            "## Product Features by Phase\n\n## Phase 1: Alpha Host-Side Helpers\n\n## zigux-alpha Scope",
            1,
        )
        _write(root / ROADMAP_PATH, misordered)
        missing = collect_missing_markers(root)
        expected = ["roadmap-section-order:HowZARShouldFeedZigux->ziguxAlphaScope->ProductFeaturesByPhase"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for section-order case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("- roadmap and phase sequencing\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-scope:- roadmap and phase sequencing"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for staging case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("- workstream ownership\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-scope:- workstream ownership"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for ownership case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("`zigux-alpha/` is not the final home for:\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-scope:`zigux-alpha/` is not the final home for:"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for not-final-home case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("- UAPI shims\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-scope:- UAPI shims"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for uapi case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("- `Documentation/zigux/`\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-scope:- `Documentation/zigux/`"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for docs destination case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("- `security/*/*.zig`\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-scope:- `security/*/*.zig`"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for security destination case: {missing}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_ZIGUX_ALPHA_SCOPE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_ZIGUX_ALPHA_SCOPE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 roadmap zigux-alpha Scope packet."
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
        help="exercise the checker against synthetic roadmap fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: {item}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_ZIGUX_ALPHA_SCOPE=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_ZIGUX_ALPHA_SCOPE_REQUIRED_LINE_COUNT={len(SCOPE_MARKERS)}")
    print("LANE01_BOOTSTRAP_ROADMAP_ZIGUX_ALPHA_SCOPE_SECTION_ORDER=ZARFeed->ziguxAlphaScope->ProductFeatures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
