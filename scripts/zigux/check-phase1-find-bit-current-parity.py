#!/usr/bin/env python3
"""Check the current Phase 1 find_bit parity values and build-route anchors."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

HELPER_REL = Path("tools/lib/find_bit.zig")
REPLAY_REL = Path("zigux/tests/phase1_helpers.zig")
BUILD_REL = Path("zigux/tests/phase1_helpers_build.zig")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

EXPECTED_FIXTURE = {
    "bits_per_long": 64,
    "first": 5,
    "next_after_6": 9,
    "next_after_word": 66,
    "first_zero": 3,
    "next_zero": 68,
    "first_and": 9,
    "next_and": 66,
    "last": 71,
}
EXPECTED_PARITY_KEYS = list(EXPECTED_FIXTURE.keys())

HELPER_ANCHORS = [
    'test "find first and next set bits across words, with andnot gaps explicit"',
    'test "single-word next scans honor start masks"',
    'test "tail-word next set scans skip earlier in-range matches before clamping"',
    'test "tail-word next zero and shared scans skip earlier in-range matches before clamping"',
    'test "find last bit clamps tail words to nbits"',
    'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
    'test "Linux-style aliases mirror the primary find helpers, including andnot"',
]

REPLAY_MARKERS = [
    "const nbits = fixture.find_bit.bits_per_long * 2 + 8;",
    "try std.testing.expectEqual(fixture.find_bit.first, find_bit.findFirstBit(&bitmap_a, nbits));",
    "try std.testing.expectEqual(fixture.find_bit.next_after_6, find_bit.findNextBit(&bitmap_a, nbits, 6));",
    "try std.testing.expectEqual(fixture.find_bit.next_after_word, find_bit.findNextBit(&bitmap_a, nbits, fixture.find_bit.bits_per_long));",
    "try std.testing.expectEqual(fixture.find_bit.first_zero, find_bit.findFirstZeroBit(&bitmap_b, nbits));",
    "try std.testing.expectEqual(fixture.find_bit.next_zero, find_bit.findNextZeroBit(&bitmap_b, nbits, fixture.find_bit.bits_per_long));",
    "try std.testing.expectEqual(fixture.find_bit.first_and, find_bit.findFirstAndBit(&bitmap_a, &bitmap_and, nbits));",
    "try std.testing.expectEqual(fixture.find_bit.next_and, find_bit.findNextAndBit(&bitmap_a, &bitmap_and, nbits, fixture.find_bit.bits_per_long));",
    "try std.testing.expectEqual(fixture.find_bit.last, find_bit.findLastBit(&bitmap_a, nbits));",
]

BUILD_MARKERS = [
    'const find_bit_module = b.createModule(.{',
    '.root_source_file = b.path("../../tools/lib/find_bit.zig"),',
    'root_module.addImport("find_bit", find_bit_module);',
    'const phase1_helpers = b.step(',
    '"phase1-helpers",',
]

NEXT_SAFE_STEP = (
    "If this helper lane reopens, keep find_bit parked unless a fresh reread finds drift in the "
    "manifest-backed same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, "
    "past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage "
    "including the shipped andnot scan entry points, or tail-word skip anchors, or committed shared "
    "replay drift in the live `bits_per_long`, `first`, `next_after_6`, `next_after_word`, "
    "`first_zero`, `next_zero`, `first_and`, `next_and`, or `last` fixture keys; do not reopen older "
    "saved validator cues or neighboring helper families."
)


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> Any:
    return json.loads(load_text(root, relative_path), object_pairs_hook=DuplicateTrackingDict)


def duplicate_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        paths.extend(".".join(prefix + (key,)) for key in data.duplicate_keys)
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(duplicate_key_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(duplicate_key_paths(item, prefix))
    return paths


def require_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (HELPER_REL, REPLAY_REL, BUILD_REL, FIXTURE_REL, MANIFEST_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, HELPER_REL)
    replay_text = load_text(root, REPLAY_REL)
    build_text = load_text(root, BUILD_REL)

    try:
        fixture = load_json(root, FIXTURE_REL)
        manifest = load_json(root, MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [f"invalid_json:line={exc.lineno}:column={exc.colno}:{exc.msg}"]

    for path in duplicate_key_paths(fixture):
        failures.append(f"fixture:duplicate_json_key:{path}")
    for path in duplicate_key_paths(manifest):
        failures.append(f"manifest:duplicate_json_key:{path}")

    for marker in HELPER_ANCHORS:
        failures.extend(require_once(helper_text, f"helper_anchor:{marker}", marker))
    for marker in REPLAY_MARKERS:
        failures.extend(require_once(replay_text, f"replay_marker:{marker}", marker))
    for marker in BUILD_MARKERS:
        failures.extend(require_once(build_text, f"build_marker:{marker}", marker))

    if fixture.get("find_bit") != EXPECTED_FIXTURE:
        failures.append("fixture:find_bit:expected_current_nine_key_parity_values")

    review_anchors = manifest.get("review_anchors") if isinstance(manifest, dict) else None
    packet = review_anchors.get("tools/lib/find_bit.zig") if isinstance(review_anchors, dict) else None
    if not isinstance(packet, dict):
        failures.append("manifest:review_anchors:tools/lib/find_bit.zig")
    else:
        if packet.get("parity_fixture_keys") != EXPECTED_PARITY_KEYS:
            failures.append("manifest:parity_fixture_keys:expected_current_nine_key_order")
        if packet.get("next_safe_step_note") != NEXT_SAFE_STEP:
            failures.append("manifest:next_safe_step_note:expected_current_reopen_rule")

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root, HELPER_REL, "\n".join(HELPER_ANCHORS) + "\n")
    write_text(root, REPLAY_REL, "\n".join(REPLAY_MARKERS) + "\n")
    write_text(root, BUILD_REL, "\n".join(BUILD_MARKERS) + "\n")
    write_text(root, FIXTURE_REL, json.dumps({"find_bit": EXPECTED_FIXTURE}, indent=2) + "\n")
    write_text(
        root,
        MANIFEST_REL,
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/find_bit.zig": {
                        "parity_fixture_keys": EXPECTED_PARITY_KEYS,
                        "next_safe_step_note": NEXT_SAFE_STEP,
                    }
                }
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        build_sample_repo(root)
        if failures := collect_failures(root):
            raise SystemExit(f"self-test:expected_pass:{failures}")

        fixture = load_json(root, FIXTURE_REL)
        fixture["find_bit"]["next_after_word"] = 67
        write_text(root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")
        failures = collect_failures(root)
        if "fixture:find_bit:expected_current_nine_key_parity_values" not in failures:
            raise SystemExit("self-test:fixture_drift_not_detected")

        build_sample_repo(root)
        replay_path = root / REPLAY_REL
        replay_path.write_text(replay_path.read_text(encoding="utf-8").replace(REPLAY_MARKERS[0], "", 1), encoding="utf-8")
        failures = collect_failures(root)
        if f"replay_marker:{REPLAY_MARKERS[0]}:expected=1:actual=0" not in failures:
            raise SystemExit("self-test:replay_marker_drift_not_detected")

        build_sample_repo(root)
        manifest = load_json(root, MANIFEST_REL)
        manifest["review_anchors"]["tools/lib/find_bit.zig"]["parity_fixture_keys"] = EXPECTED_PARITY_KEYS[:-1]
        write_text(root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        failures = collect_failures(root)
        if "manifest:parity_fixture_keys:expected_current_nine_key_order" not in failures:
            raise SystemExit("self-test:manifest_key_drift_not_detected")

    print("PHASE1_FIND_BIT_CURRENT_PARITY_SELF_TEST=pass")
    print("PHASE1_FIND_BIT_CURRENT_PARITY_SELF_TEST_CASES=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_FIND_BIT_CURRENT_PARITY=fail")
        for failure in failures:
            print(failure)
        return 1

    print("phase1-find-bit-current-parity:ok")
    print(f"PHASE1_FIND_BIT_CURRENT_PARITY_HELPER={HELPER_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_CURRENT_PARITY_REPLAY={REPLAY_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_CURRENT_PARITY_BUILD={BUILD_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_CURRENT_PARITY_FIXTURE={FIXTURE_REL.as_posix()}")
    print(f"PHASE1_FIND_BIT_CURRENT_PARITY_MANIFEST={MANIFEST_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
