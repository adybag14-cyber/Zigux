#!/usr/bin/env python3
"""Guard the focused Phase 1 helper replay packet against direct-readback drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

REQUIRED_FILES = (
    Path("zigux/tests/phase1_helpers.zig"),
    Path("zigux/tests/phase1_helpers_build.zig"),
    Path("zigux/tests/fixtures/phase1_helpers.json"),
    Path("zigux/tests/phase1_host_tools_smoke.zig"),
)

HELPERS_REL = Path("zigux/tests/phase1_helpers.zig")
BUILD_REL = Path("zigux/tests/phase1_helpers_build.zig")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")

HELPER_MARKERS = {
    "bitmap_import": 'const bitmap = @import("bitmap");',
    "find_bit_import": 'const find_bit = @import("find_bit");',
    "rbtree_import": 'const rbtree = @import("rbtree");',
    "string_import": 'const string = @import("string");',
    "fixture_embed": 'const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");',
    "replay_test": 'test "phase 1 helper ports match committed parity fixture" {',
    "find_bit_replay": "try std.testing.expectEqual(fixture.find_bit.tail_clamped_last, find_bit.findLastBit(&tail_clamped_bits, tail_nbits));",
    "bitmap_replay": "try std.testing.expectEqualSlices(u64, fixture.bitmap.partial_xor_masked_values, &[_]u64{",
    "string_replay": "try std.testing.expectEqualSlices(u8, fixture.string.replace_char_cstr_bytes, &replace_char_cstr_bytes);",
    "rbtree_replay": "try std.testing.expectEqualSlices(i32, fixture.rbtree.cached_leftmost_return_serials, &cached_leftmost_return_serials);",
}

BUILD_MARKERS = {
    "root_source": '.root_source_file = b.path("phase1_helpers.zig"),',
    "find_bit_module": '.root_source_file = b.path("../../tools/lib/find_bit.zig"),',
    "bitmap_module": '.root_source_file = b.path("../../tools/lib/bitmap.zig"),',
    "rbtree_module": '.root_source_file = b.path("../../tools/lib/rbtree.zig"),',
    "string_module": '.root_source_file = b.path("../../tools/lib/string.zig"),',
    "find_bit_import": 'root_module.addImport("find_bit", find_bit_module);',
    "bitmap_import": 'root_module.addImport("bitmap", bitmap_module);',
    "rbtree_import": 'root_module.addImport("rbtree", rbtree_module);',
    "string_import": 'root_module.addImport("string", string_module);',
    "step_name": '.name = "phase1-helpers",',
    "step_route": '"Run the focused Phase 1 helper replay anchor from zigux/tests",',
}

SMOKE_MARKERS = {
    "find_bit_decl": 'try std.testing.expect(@hasDecl(find_bit, "findFirstBit"));',
    "bitmap_decl": 'try std.testing.expect(@hasDecl(bitmap, "setRange"));',
    "rbtree_decl": 'try std.testing.expect(@hasDecl(rbtree, "matchIterator"));',
    "string_decl": 'try std.testing.expect(@hasDecl(string, "strnchrNul"));',
    "smoke_test": 'test "phase1 host-tools smoke exercises live helper behavior" {',
}

EXPECTED_FIXTURE_VALUES = {
    ("find_bit", "tail_clamped_last"): 67,
    ("find_bit", "tail_clamped_empty_last"): 69,
    ("bitmap", "partial_xor_nbits"): 4,
    ("bitmap", "partial_xor_masked_values"): [14],
    ("string", "replace_char_cstr_bytes"): [97, 95, 0, 45, 122],
    ("rbtree", "cached_leftmost_return_serials"): [0, -1, 2, -1],
    ("rbtree", "cached_root_transition_serials"): [0, 0, 4, 2],
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def nested_value(data: object, path: tuple[str, str]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helpers_text = read_text(root, HELPERS_REL)
    for label, marker in HELPER_MARKERS.items():
        failures.extend(require_exact_occurrence(helpers_text, f"{HELPERS_REL.as_posix()}:{label}", marker))

    build_text = read_text(root, BUILD_REL)
    for label, marker in BUILD_MARKERS.items():
        failures.extend(require_exact_occurrence(build_text, f"{BUILD_REL.as_posix()}:{label}", marker))

    smoke_text = read_text(root, SMOKE_REL)
    for label, marker in SMOKE_MARKERS.items():
        failures.extend(require_exact_occurrence(smoke_text, f"{SMOKE_REL.as_posix()}:{label}", marker))

    try:
        fixture = json.loads(read_text(root, FIXTURE_REL))
    except json.JSONDecodeError as exc:
        return [f"{FIXTURE_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    for path, expected in EXPECTED_FIXTURE_VALUES.items():
        actual = nested_value(fixture, path)
        if actual != expected:
            failures.append(
                f"{FIXTURE_REL.as_posix()}:{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )

    return failures


def write_text(root: Path, relative_path: Path, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root, HELPERS_REL, "\n".join(HELPER_MARKERS.values()) + "\n")
    write_text(root, BUILD_REL, "\n".join(BUILD_MARKERS.values()) + "\n")
    write_text(root, SMOKE_REL, "\n".join(SMOKE_MARKERS.values()) + "\n")

    fixture = {
        "find_bit": {
            "tail_clamped_last": 67,
            "tail_clamped_empty_last": 69,
        },
        "bitmap": {
            "partial_xor_nbits": 4,
            "partial_xor_masked_values": [14],
        },
        "string": {
            "replace_char_cstr_bytes": [97, 95, 0, 45, 122],
        },
        "rbtree": {
            "cached_leftmost_return_serials": [0, -1, 2, -1],
            "cached_root_transition_serials": [0, 0, 4, 2],
        },
    }
    write_text(root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")


def mutate_remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, relative_path: Path, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def mutate_fixture_value(root: Path, path: tuple[str, str], replacement: object) -> None:
    target = root / FIXTURE_REL
    data = json.loads(target.read_text(encoding="utf-8"))
    data[path[0]][path[1]] = replacement
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", ("remove_file", relative_path)))

    for label, marker in HELPER_MARKERS.items():
        cases.append((f"missing_helper_marker:{label}", ("remove_marker", HELPERS_REL, marker)))
        cases.append((f"duplicate_helper_marker:{label}", ("duplicate_marker", HELPERS_REL, marker)))

    for label, marker in BUILD_MARKERS.items():
        cases.append((f"missing_build_marker:{label}", ("remove_marker", BUILD_REL, marker)))

    for label, marker in SMOKE_MARKERS.items():
        cases.append((f"missing_smoke_marker:{label}", ("remove_marker", SMOKE_REL, marker)))

    for path, expected in EXPECTED_FIXTURE_VALUES.items():
        replacement = expected + 1 if isinstance(expected, int) else []
        cases.append((f"fixture_drift:{'.'.join(path)}", ("mutate_fixture", path, replacement)))

    cases.append(("invalid_fixture_json", ("invalid_fixture_json",)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-helper-replay-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mutation is not None:
                mode = mutation[0]
                if mode == "remove_file":
                    _, relative_path = mutation
                    (root / relative_path).unlink()
                elif mode == "remove_marker":
                    _, relative_path, marker = mutation
                    mutate_remove_marker(root, relative_path, marker)
                elif mode == "duplicate_marker":
                    _, relative_path, marker = mutation
                    mutate_duplicate_marker(root, relative_path, marker)
                elif mode == "mutate_fixture":
                    _, path, replacement = mutation
                    mutate_fixture_value(root, path, replacement)
                elif mode == "invalid_fixture_json":
                    write_text(root, FIXTURE_REL, "{\n")

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print(f"self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_HELPER_REPLAY_PRESENCE_SELF_TEST=pass")
    print(f"PHASE1_HELPER_REPLAY_PRESENCE_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root used for checks")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_HELPER_REPLAY_PRESENCE=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_HELPER_REPLAY_PRESENCE=pass")
    print(f"PHASE1_HELPER_REPLAY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_HELPER_REPLAY_REQUIRED_MARKER_COUNT="
        f"{len(HELPER_MARKERS) + len(BUILD_MARKERS) + len(SMOKE_MARKERS) + len(EXPECTED_FIXTURE_VALUES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())