#!/usr/bin/env python3
"""Reject stale Phase 1 bitmap zero-bit regression markers."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
BITMAP_REL = Path("tools/lib/bitmap.zig")

REQUIRED_MARKERS = {
    "zero_bit_test_anchor": 'test "bitmap zero-bit logical helpers stay explicit" {',
    "zero_bit_equal_expect": "try std.testing.expect(equal(lhs[0..0], rhs[0..0], 0));",
    "zero_bit_subset_expect": "try std.testing.expect(subset(lhs[0..0], rhs[0..0], 0));",
    "zero_bit_scnprintf_len": "const len = scnprintf(lhs[0..0], 0, &buffer);",
    "zero_bit_scnprintf_untouched": "try std.testing.expectEqualSlices(u8, &[_]u8{ 0xcc, 0xcc, 0xcc }, &buffer);",
}

FORBIDDEN_MARKERS = {
    "stale_one_argument_expect_equal": "try std.testing.expectEqual(equal(lhs[0..0], rhs[0..0], 0));",
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def collect_count_failures(text: str, markers: dict[str, str], expected: int) -> list[str]:
    failures: list[str] = []
    for label, marker in markers.items():
        count = text.count(marker)
        if count != expected:
            failures.append(f"{label}:expected={expected}:actual={count}")
    return failures


def validate_bitmap_text(text: str) -> tuple[str, list[str]]:
    required_failures = collect_count_failures(text, REQUIRED_MARKERS, 1)
    if required_failures:
        return ("missing_or_duplicated_required_markers", required_failures)

    forbidden_failures = collect_count_failures(text, FORBIDDEN_MARKERS, 0)
    if forbidden_failures:
        return ("forbidden_stale_markers", forbidden_failures)

    return ("pass", [])


def load_and_validate(root: Path) -> tuple[str, object]:
    path = root / BITMAP_REL
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ("missing_file", path)
    return validate_bitmap_text(text)


def sample_bitmap_text(
    omit_label: str | None = None,
    duplicate_label: str | None = None,
    forbidden_label: str | None = None,
) -> str:
    lines = list(REQUIRED_MARKERS.values())
    if omit_label is not None:
        lines.remove(REQUIRED_MARKERS[omit_label])
    if duplicate_label is not None:
        lines.append(REQUIRED_MARKERS[duplicate_label])
    if forbidden_label is not None:
        lines.append(FORBIDDEN_MARKERS[forbidden_label])
    return "\n".join(lines) + "\n"


def run_self_test() -> int:
    cases = 0

    kind, failures = validate_bitmap_text(sample_bitmap_text())
    assert kind == "pass", (kind, failures)
    cases += 1

    for label in REQUIRED_MARKERS:
        kind, failures = validate_bitmap_text(sample_bitmap_text(omit_label=label))
        assert kind == "missing_or_duplicated_required_markers", (label, kind, failures)
        assert failures == [f"{label}:expected=1:actual=0"], (label, failures)
        cases += 1

        kind, failures = validate_bitmap_text(sample_bitmap_text(duplicate_label=label))
        assert kind == "missing_or_duplicated_required_markers", (label, kind, failures)
        assert failures == [f"{label}:expected=1:actual=2"], (label, failures)
        cases += 1

    for label in FORBIDDEN_MARKERS:
        kind, failures = validate_bitmap_text(sample_bitmap_text(forbidden_label=label))
        assert kind == "forbidden_stale_markers", (label, kind, failures)
        assert failures == [f"{label}:expected=0:actual=1"], (label, failures)
        cases += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bitmap-zero-bit-") as tmp:
        root = Path(tmp)
        kind, payload = load_and_validate(root)
        assert kind == "missing_file", (kind, payload)
        assert payload == root / BITMAP_REL
        cases += 1

        path = root / BITMAP_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(sample_bitmap_text(), encoding="utf-8")
        kind, payload = load_and_validate(root)
        assert kind == "pass", (kind, payload)
        cases += 1

    print("PHASE1_BITMAP_ZERO_BIT_REGRESSION_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_ZERO_BIT_REGRESSION_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    kind, payload = load_and_validate(repo_root(args.root))
    if kind != "pass":
        print("PHASE1_BITMAP_ZERO_BIT_REGRESSION=fail")
        if isinstance(payload, list):
            print("PHASE1_BITMAP_ZERO_BIT_REGRESSION_REASON=" + kind)
            for failure in payload:
                print(failure)
        else:
            print(f"PHASE1_BITMAP_ZERO_BIT_REGRESSION_REASON={kind}")
            print(payload)
        return 1

    print("PHASE1_BITMAP_ZERO_BIT_REGRESSION=pass")
    print(f"PHASE1_BITMAP_ZERO_BIT_REGRESSION_HELPER={BITMAP_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
