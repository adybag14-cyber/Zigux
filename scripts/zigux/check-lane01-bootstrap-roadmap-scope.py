#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

SCOPE_HEADING = "## zigux-alpha Scope"
STAGING_HEADING = "`zigux-alpha/` is the staging area for:"
NOT_FINAL_HEADING = "`zigux-alpha/` is not the final home for:"
DESTINATIONS_HEADING = "Those should eventually land in:"

STAGING_BULLETS = (
    "- roadmap and phase sequencing",
    "- source mapping",
    "- validation strategy",
    "- freeze map",
    "- first commit ledger",
    "- workstream ownership",
)

NOT_FINAL_BULLETS = (
    "- subsystem ports",
    "- runtime helpers",
    "- drivers",
    "- bindings",
    "- UAPI shims",
)

DESTINATION_BULLETS = (
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


def _find_required_index(lines: list[str], marker: str, start: int = 0) -> int:
    for idx in range(start, len(lines)):
        if lines[idx] == marker:
            return idx
    raise ValueError(marker)


def collect_errors(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    lines = roadmap.splitlines()
    errors: list[str] = []

    try:
        scope_idx = _find_required_index(lines, SCOPE_HEADING)
    except ValueError:
        return [f"missing:{SCOPE_HEADING}"]

    section_tail = lines[scope_idx + 1 :]

    def _section_index(marker: str, start: int = 0) -> int | None:
        try:
            return _find_required_index(section_tail, marker, start)
        except ValueError:
            errors.append(f"missing:{marker}")
            return None

    staging_idx = _section_index(STAGING_HEADING)
    not_final_idx = _section_index(NOT_FINAL_HEADING, (staging_idx or 0) + 1 if staging_idx is not None else 0)
    destinations_idx = _section_index(
        DESTINATIONS_HEADING, (not_final_idx or 0) + 1 if not_final_idx is not None else 0
    )

    if staging_idx is not None:
        for offset, bullet in enumerate(STAGING_BULLETS, start=1):
            idx = staging_idx + offset
            if idx >= len(section_tail) or section_tail[idx] != bullet:
                errors.append(f"staging:{bullet}")

    if not_final_idx is not None:
        for offset, bullet in enumerate(NOT_FINAL_BULLETS, start=1):
            idx = not_final_idx + offset
            if idx >= len(section_tail) or section_tail[idx] != bullet:
                errors.append(f"not-final:{bullet}")

    if destinations_idx is not None:
        for offset, bullet in enumerate(DESTINATION_BULLETS, start=1):
            idx = destinations_idx + offset
            if idx >= len(section_tail) or section_tail[idx] != bullet:
                errors.append(f"destinations:{bullet}")

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

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
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_scope_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_errors(root):
            raise AssertionError("baseline roadmap scope fixture should pass")
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(SCOPE_HEADING + "\n\n", "", 1))
        errors = collect_errors(root)
        if errors != [f"missing:{SCOPE_HEADING}"]:
            raise AssertionError(f"unexpected missing heading result: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(STAGING_BULLETS[2] + "\n", "", 1))
        errors = collect_errors(root)
        if errors[0] != f"staging:{STAGING_BULLETS[2]}":
            raise AssertionError(f"unexpected staging error result: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(NOT_FINAL_BULLETS[4] + "\n", "", 1))
        errors = collect_errors(root)
        if errors[0] != f"not-final:{NOT_FINAL_BULLETS[4]}":
            raise AssertionError(f"unexpected not-final error result: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace(DESTINATION_BULLETS[3] + "\n", "", 1))
        errors = collect_errors(root)
        if errors[0] != f"destinations:{DESTINATION_BULLETS[3]}":
            raise AssertionError(f"unexpected destination error result: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                STAGING_BULLETS[0] + "\n" + STAGING_BULLETS[1],
                STAGING_BULLETS[1] + "\n" + STAGING_BULLETS[0],
                1,
            ),
        )
        errors = collect_errors(root)
        if errors[:2] != [f"staging:{STAGING_BULLETS[0]}", f"staging:{STAGING_BULLETS[1]}"]:
            raise AssertionError(f"unexpected staging reorder result: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                NOT_FINAL_HEADING + "\n",
                DESTINATIONS_HEADING + "\n",
                1,
            ),
        )
        errors = collect_errors(root)
        if f"missing:{NOT_FINAL_HEADING}" not in errors:
            raise AssertionError(f"unexpected missing not-final heading result: {errors}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(
            root / ROADMAP_PATH,
            _sample_roadmap().replace(
                DESTINATION_BULLETS[-1] + "\n",
                "",
                1,
            ),
        )
        errors = collect_errors(root)
        if errors[0] != f"destinations:{DESTINATION_BULLETS[-1]}":
            raise AssertionError(f"unexpected tail destination error result: {errors}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_SCOPE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_SCOPE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the landed Lane 01 roadmap zigux-alpha scope packet remains aligned."
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
        help="exercise the checker against a synthetic roadmap scope fixture",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_errors(args.root)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1

    print("Lane 01 bootstrap roadmap scope check passed.")
    print(f"LANE01_BOOTSTRAP_ROADMAP_SCOPE_DESTINATION_COUNT={len(DESTINATION_BULLETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
