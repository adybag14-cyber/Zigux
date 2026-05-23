#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

REQUIRED_MARKERS = (
    "## zigux-alpha Scope",
    "`zigux-alpha/` is the staging area for:",
    "- roadmap and phase sequencing",
    "- first commit ledger",
    "- workstream ownership",
    "`zigux-alpha/` is not the final home for:",
    "- subsystem ports",
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

PREVIOUS_HEADING = "## How ZAR Should Feed Zigux"
NEXT_HEADING = "## Product Features by Phase"


def collect_missing_markers(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    missing: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in roadmap:
            missing.append(marker)
    return missing


def check_section_order(root: Path) -> tuple[int, int, int]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    previous_index = roadmap.find(PREVIOUS_HEADING)
    scope_index = roadmap.find("## zigux-alpha Scope")
    next_index = roadmap.find(NEXT_HEADING)
    if previous_index == -1 or scope_index == -1 or next_index == -1:
        raise AssertionError("required section heading missing while checking order")
    if not previous_index < scope_index < next_index:
        raise AssertionError(
            "unexpected section order for roadmap zigux-alpha scope packet"
        )
    return previous_index, scope_index, next_index


def count_scope_destinations(root: Path) -> int:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    scope_index = roadmap.find("## zigux-alpha Scope")
    next_index = roadmap.find(NEXT_HEADING)
    scope_section = roadmap[scope_index:next_index]
    return scope_section.count("- `")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## How ZAR Should Feed Zigux

The rule is simple:
- If a ZAR slice reduces Zigux product risk, keep it.
- If it only expands ZAR's own experimental surface, do not let it consume Zigux product bandwidth.

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
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_scope_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_missing_markers(root):
            raise AssertionError("baseline roadmap scope fixture should pass")
        check_section_order(root)
        if count_scope_destinations(root) != 9:
            raise AssertionError("expected nine destination entries in baseline fixture")
        case_count += 1

        for marker in (
            "## zigux-alpha Scope",
            "- roadmap and phase sequencing",
            "- first commit ledger",
            "- workstream ownership",
            "- UAPI shims",
            "- `security/*/*.zig`",
        ):
            _write(root / ROADMAP_PATH, _sample_roadmap().replace(f"{marker}\n", "", 1))
            missing = collect_missing_markers(root)
            if missing != [marker]:
                raise AssertionError(f"unexpected missing markers for {marker}: {missing}")
            _write(root / ROADMAP_PATH, _sample_roadmap())
            case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                "## How ZAR Should Feed Zigux\n\n"
                "The rule is simple:\n"
                "- If a ZAR slice reduces Zigux product risk, keep it.\n"
                "- If it only expands ZAR's own experimental surface, do not let it consume Zigux product bandwidth.\n\n"
                "## zigux-alpha Scope\n\n",
                "## zigux-alpha Scope\n\n"
                "The rule is simple:\n"
                "- If a ZAR slice reduces Zigux product risk, keep it.\n"
                "- If it only expands ZAR's own experimental surface, do not let it consume Zigux product bandwidth.\n\n"
                "## How ZAR Should Feed Zigux\n\n",
                1,
            ),
        )
        try:
            check_section_order(root)
        except AssertionError:
            pass
        else:
            raise AssertionError("expected section-order self-test case to fail")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

    print("LANE01_ROADMAP_ZIGUX_ALPHA_SCOPE_SELF_TEST=pass")
    print(f"LANE01_ROADMAP_ZIGUX_ALPHA_SCOPE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 roadmap zigux-alpha scope packet on current master."
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
        help="exercise the checker against a synthetic roadmap fixture",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    if missing:
        for marker in missing:
            print(f"MISSING_MARKER={marker}")
        return 1

    previous_index, scope_index, next_index = check_section_order(args.root)
    print("LANE01_ROADMAP_ZIGUX_ALPHA_SCOPE=pass")
    print(f"LANE01_ROADMAP_ZIGUX_ALPHA_SCOPE_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("LANE01_ROADMAP_ZIGUX_ALPHA_SCOPE_SECTION_ORDER=HowZARShouldFeedZigux->ziguxAlphaScope->ProductFeaturesByPhase")
    print(f"LANE01_ROADMAP_ZIGUX_ALPHA_SCOPE_SECTION_INDEXES={previous_index}:{scope_index}:{next_index}")
    print(f"LANE01_ROADMAP_ZIGUX_ALPHA_SCOPE_DESTINATION_COUNT={count_scope_destinations(args.root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
