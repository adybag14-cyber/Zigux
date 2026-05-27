#!/usr/bin/env python3
"""Guard the live Phase 1 shared string replay and smoke surfaces against drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent
HELPERS_REL = Path("zigux/tests/phase1_helpers.zig")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")


EXPECTED_HELPERS_MARKERS = [
    'try std.testing.expectEqual(fixture.string.strtobool_y, try string.strtobool("y"));',
    'try std.testing.expectEqual(fixture.string.strtobool_on, try string.strtobool("on"));',
    'try std.testing.expectEqual(fixture.string.strtobool_zero, try string.strtobool("0"));',
    'try std.testing.expectEqual(fixture.string.strtobool_off, try string.strtobool("off"));',
    'try std.testing.expectEqual(fixture.string.strtobool_invalid, @as(u8, @intCast(@intFromError(error.Invalid))));',
    'try std.testing.expectEqual(fixture.string.strlcpy_len, string.strlcpy(copied[0..], "hello"));',
    'try std.testing.expectEqualStrings(fixture.string.strlcpy_buffer, copied[0 .. copied.len - 1]);',
    'try std.testing.expectEqualStrings(fixture.string.skip_spaces, string.skipSpaces(" \\t hello"));',
    'try std.testing.expectEqualStrings(fixture.string.trim_spaces, string.trimSpaces(trim_buf[0..]));',
    'try std.testing.expectEqualStrings(fixture.string.remove_spaces, string.removeSpaces(remove_buf[0..]));',
    'try std.testing.expectEqual(fixture.string.replace_char_end, string.replaceChar(replace_buf[0..], \'-\', \'_\'));',
    'try std.testing.expectEqualStrings(fixture.string.replace_char, replace_buf[0 .. replace_buf.len - 1]);',
    'try std.testing.expectEqual(fixture.string.replace_char_cstr_end, string.replaceChar(replace_cstr_buf[0..], \'-\', \'_\'));',
    'try std.testing.expectEqualSlices(u8, fixture.string.replace_char_cstr_bytes, replace_cstr_buf[0..]);',
    'try std.testing.expectEqual(@as(?usize, fixture.string.memchr_inv_index), string.memchrInv(&[_]u8{ \'x\', \'x\', \'x\', \'x\', \'y\' }, \'x\'));',
    'try std.testing.expectEqual(fixture.string.memchr_inv_none, string.memchrInv(&[_]u8{ \'x\', \'x\', \'x\' }, \'x\') == null);',
]

EXPECTED_SMOKE_MARKERS = [
    'try std.testing.expectEqual(@as(usize, 5), string.strlcat(appended[0..], "all"));',
    'try std.testing.expectEqual(@as(usize, 6), string.strlcat(truncated_append[0..], "cdef"));',
    'try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs, "auto"));',
    'try std.testing.expect(string.sysfs_streq("auto\\n", "auto"));',
    'try std.testing.expectEqual(@as(?usize, 1), string.matchString(&lookup, "manual"));',
    'try std.testing.expectEqual(@as(?usize, 3), string.match_string(&lookup, &lookup_cstr));',
    'try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&counted, counted.len, \'b\'));',
    'try std.testing.expectEqual(@as(usize, 2), string.strnchrNul(&counted, counted.len, \'z\'));',
    'try std.testing.expectEqual(@as(usize, 1), string.strnchrnul(&counted, counted.len, \'b\'));',
    'try std.testing.expectEqual(@as(usize, 4), string.strspn("abba!", "ab"));',
    'try std.testing.expectEqual(@as(usize, 1), string.strchrNul(&terminator_clamped, \'z\'));',
    'try std.testing.expectEqual(@as(usize, 1), string.strchrnul(&terminator_clamped, \'z\'));',
]

EXPECTED_FIXTURE_VALUES = {
    "strtobool_y": True,
    "strtobool_on": True,
    "strtobool_zero": False,
    "strtobool_off": False,
    "strtobool_invalid": 184,
    "strlcpy_len": 5,
    "strlcpy_buffer": "hel",
    "skip_spaces": "hello",
    "trim_spaces": "hi",
    "remove_spaces": "abc",
    "replace_char": "a_b",
    "replace_char_end": 3,
    "replace_char_cstr_end": 2,
    "replace_char_cstr_bytes": [97, 95, 0, 45, 122],
    "memchr_inv_index": 4,
    "memchr_inv_none": True,
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (HELPERS_REL, SMOKE_REL, FIXTURE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helpers_text = load_text(root, HELPERS_REL)
    smoke_text = load_text(root, SMOKE_REL)
    try:
        fixture = json.loads(load_text(root, FIXTURE_REL))
    except json.JSONDecodeError as exc:
        return [f"fixture:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    for marker in EXPECTED_HELPERS_MARKERS:
        failures.extend(require_exact_occurrence(helpers_text, f"helpers:{marker}", marker))

    for marker in EXPECTED_SMOKE_MARKERS:
        failures.extend(require_exact_occurrence(smoke_text, f"smoke:{marker}", marker))

    string_fixture = fixture.get("string")
    if not isinstance(string_fixture, dict):
        return ["fixture:string:expected=dict:actual=missing"]
    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        failures.extend(require_exact_value(f"fixture:string.{key}", string_fixture.get(key), expected))

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_fixture() -> str:
    return json.dumps({"string": EXPECTED_FIXTURE_VALUES}, indent=2) + "\n"


def sample_source(markers: list[str]) -> str:
    return "\n".join(markers) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, HELPERS_REL, sample_source(EXPECTED_HELPERS_MARKERS))
    write_file(root, SMOKE_REL, sample_source(EXPECTED_SMOKE_MARKERS))
    write_file(root, FIXTURE_REL, sample_fixture())


def run_self_test() -> int:
    cases = [
        "missing_file:zigux/tests/phase1_helpers.zig",
        f"helpers:{EXPECTED_HELPERS_MARKERS[0]}:expected=1:actual=0",
        f"smoke:{EXPECTED_SMOKE_MARKERS[0]}:expected=1:actual=0",
        f"fixture:string.strlcpy_len:expected=5:actual=0",
        "fixture:invalid_json:Expecting property name enclosed in double quotes:line=2:column=1",
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_shared_") as tmp_dir:
        tmp_root = Path(tmp_dir)

        if cases[0] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-shared-surfaces:self-test:missing_file")

        build_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("phase1-string-shared-surfaces:self-test:baseline")

        helpers_path = tmp_root / HELPERS_REL
        smoke_path = tmp_root / SMOKE_REL
        fixture_path = tmp_root / FIXTURE_REL

        helpers_path.write_text(
            helpers_path.read_text(encoding="utf-8").replace(EXPECTED_HELPERS_MARKERS[0] + "\n", "", 1),
            encoding="utf-8",
        )
        if cases[1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-shared-surfaces:self-test:helpers_marker")

        build_sample_repo(tmp_root)
        smoke_path.write_text(
            smoke_path.read_text(encoding="utf-8").replace(EXPECTED_SMOKE_MARKERS[0] + "\n", "", 1),
            encoding="utf-8",
        )
        if cases[2] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-shared-surfaces:self-test:smoke_marker")

        build_sample_repo(tmp_root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["string"]["strlcpy_len"] = 0
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        if cases[3] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-shared-surfaces:self-test:fixture_drift")

        build_sample_repo(tmp_root)
        fixture_path.write_text("{\n", encoding="utf-8")
        if cases[4] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-shared-surfaces:self-test:fixture_invalid_json")

    print("PHASE1_STRING_SHARED_SURFACES_SELF_TEST=pass")
    print(f"PHASE1_STRING_SHARED_SURFACES_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-string-shared-surfaces:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
