#!/usr/bin/env python3
"""Audit Phase 1 bitmap parity coverage against the committed fixture.

This checker stays intentionally narrow: it verifies that every key inside the
`bitmap` section of `zigux/tests/fixtures/phase1_helpers.json` is referenced by
the shared Phase 1 replay in `zigux/tests/phase1_helpers.zig`.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


def repo_root_from_script(script_path: Path) -> Path:
    return script_path.resolve().parent.parent.parent


def load_bitmap_keys(fixture_path: Path) -> list[str]:
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    bitmap = payload.get("bitmap")
    if not isinstance(bitmap, dict):
        raise ValueError(f"{fixture_path} does not contain a JSON object at top-level key 'bitmap'")
    return sorted(bitmap.keys())


def find_missing_bitmap_references(source_text: str, bitmap_keys: list[str]) -> list[str]:
    missing: list[str] = []
    for key in bitmap_keys:
        token = f"fixture.bitmap.{key}"
        if token not in source_text:
            missing.append(key)
    return missing


def run_check(source_path: Path, fixture_path: Path, *, strict: bool) -> int:
    source_text = source_path.read_text(encoding="utf-8")
    bitmap_keys = load_bitmap_keys(fixture_path)
    missing = find_missing_bitmap_references(source_text, bitmap_keys)

    if missing:
        print("Phase 1 bitmap parity coverage is incomplete.")
        print(f"Source: {source_path}")
        print(f"Fixture: {fixture_path}")
        for key in missing:
            print(f"- missing fixture reference: fixture.bitmap.{key}")
        return 1 if strict else 0

    print("Phase 1 bitmap parity coverage references every committed bitmap fixture key.")
    print(f"Source: {source_path}")
    print(f"Fixture: {fixture_path}")
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        fixture_path = tmp / "phase1_helpers.json"
        source_path = tmp / "phase1_helpers.zig"

        fixture_path.write_text(
            json.dumps(
                {
                    "bitmap": {
                        "weight": 3,
                        "or_values": [14, 0],
                        "zero_length_scnprintf_len": 0,
                    }
                }
            ),
            encoding="utf-8",
        )
        source_path.write_text(
            "\n".join(
                [
                    "try std.testing.expectEqual(fixture.bitmap.weight, actual_weight);",
                    "try std.testing.expectEqualSlices(u64, fixture.bitmap.or_values, actual_or);",
                    "try std.testing.expectEqual(fixture.bitmap.zero_length_scnprintf_len, zero_len);",
                ]
            ),
            encoding="utf-8",
        )

        if run_check(source_path, fixture_path, strict=True) != 0:
            print("self-test: expected complete coverage to pass", file=sys.stderr)
            return 1

        source_path.write_text(
            "try std.testing.expectEqual(fixture.bitmap.weight, actual_weight);\n",
            encoding="utf-8",
        )
        if run_check(source_path, fixture_path, strict=True) == 0:
            print("self-test: expected missing coverage to fail", file=sys.stderr)
            return 1

    print("self-test: ok")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        help="Path to zigux/tests/phase1_helpers.zig. Defaults to the repo-root path beside this script.",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        help="Path to zigux/tests/fixtures/phase1_helpers.json. Defaults to the repo-root path beside this script.",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Report missing coverage without exiting non-zero.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in checker self-test and exit.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_test()

    script_path = Path(__file__)
    repo_root = repo_root_from_script(script_path)
    source_path = args.source or repo_root / "zigux/tests/phase1_helpers.zig"
    fixture_path = args.fixture or repo_root / "zigux/tests/fixtures/phase1_helpers.json"
    return run_check(source_path, fixture_path, strict=not args.report_only)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
