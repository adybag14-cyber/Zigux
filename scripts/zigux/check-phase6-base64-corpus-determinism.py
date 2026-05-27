#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 base64 corpus packet."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    """Raised when an expected Phase 6 base64 corpus marker is missing."""


SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
SHARED_FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
PARITY_FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig")
PARITY_SHIM_PATH = Path("zigux/tests/phase6_base64_c_parity_vectors.zig")
HELPER_TEST_PATH = Path("zigux/tests/phase6_base64.zig")
PERF_TEST_PATH = Path("zigux/tests/phase6_base64_perf.zig")
C_PARITY_TEST_PATH = Path("zigux/tests/phase6_base64_c_parity.zig")
C_CASEGEN_PATH = Path("zigux/tests/phase6_base64_c_casegen.zig")
C_HARNESS_PATH = Path("zigux/tests/fixtures/phase6_base64_c_harness.c")

EXPECTED_SHARED_COUNTS = {
    "standard_cases": 22,
    "variant_cases": 18,
    "standard_decode_cases": 22,
    "invalid_decode_cases": 16,
    "variant_decode_cases": 18,
    "perf_cases": 6,
}

EXPECTED_PARITY_COUNTS = {
    "encode_cases": 17,
    "decode_cases": 17,
    "invalid_cases": 6,
}

EXPECTED_HARNESS_COUNTS = {
    "encode_cases": 17,
    "decode_cases": 17,
    "invalid_cases": 6,
}

EXPECTED_PERF_LABELS = [
    "STD_PAD",
    "STD_NO_PAD",
    "URLSAFE_PAD",
    "URLSAFE_NO_PAD",
    "IMAP_PAD",
    "IMAP_NO_PAD",
]

EXPECTED_SLICE_SNIPPETS = [
    "- shared kernel-derived encode, decode, and invalid-input fixtures stored in `zigux/tests/fixtures/phase6_base64_vectors.zig` and consumed directly by `zigux/tests/phase6_base64.zig`",
    "- exact fixture-owned corpus counts on current `master`: 22 standard encode cases, 18 variant encode cases, 22 standard decode cases, 18 variant decode cases, 16 invalid decode cases, and 6 perf replay cases, all centralized in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by `zigux/tests/phase6_base64.zig` or `zigux/tests/phase6_base64_perf.zig`",
    "- helper-local corpus checker: `scripts/zigux/check-phase6-base64-corpus-determinism.py`",
    "- a representative external C-vs-Zig portability replay through `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`, covering standard padded and unpadded cases plus URL-safe, IMAP, and malformed decode spot checks",
]

EXPECTED_HELPER_TEST_SNIPPETS = [
    'const fixtures = @import("fixtures/phase6_base64_vectors.zig");',
    "for (fixtures.standard_cases) |case| {",
    "for (fixtures.variant_cases) |case| {",
    "for (fixtures.standard_decode_cases) |case| {",
    "for (fixtures.invalid_decode_cases) |case| {",
    "for (fixtures.variant_decode_cases) |case| {",
]

EXPECTED_PERF_TEST_SNIPPETS = [
    'const fixtures = @import("fixtures/phase6_base64_vectors.zig");',
    "fn validatePerfMatrix() !void {",
    "for (fixtures.perf_cases, 0..) |case, idx| {",
    "try validatePerfMatrix();",
]

EXPECTED_C_PARITY_TEST_SNIPPETS = [
    'const parity = @import("fixtures/phase6_base64_c_parity_vectors.zig");',
    "for (parity.encode_cases) |case| {",
    "for (parity.decode_cases) |case| {",
    "for (parity.invalid_cases) |case| {",
]

EXPECTED_CASEGEN_SNIPPETS = [
    'const shared = @import("fixtures/phase6_base64_vectors.zig");',
    'const parity = @import("fixtures/phase6_base64_c_parity_vectors.zig");',
    "for (parity.encode_cases) |case| {",
    "for (parity.decode_cases) |case| {",
    "for (parity.invalid_cases) |case| {",
    'try std.testing.expectEqual(@as(usize, 40), line_count);',
]

EXPECTED_PARITY_SHIM = 'pub usingnamespace @import("fixtures/phase6_base64_c_parity_vectors.zig");\n'

SELF_TEST_CASES = 6


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected marker in {path.as_posix()}: {snippet}")


def extract_array_body(content: str, marker: str) -> str:
    start = content.find(marker)
    if start == -1:
        raise ValidationError(f"missing expected array marker: {marker}")
    brace_start = content.find("{", start)
    if brace_start == -1:
        raise ValidationError(f"missing opening brace for array marker: {marker}")

    depth = 0
    for idx in range(brace_start, len(content)):
        char = content[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return content[brace_start + 1 : idx]

    raise ValidationError(f"unterminated array marker: {marker}")


def count_entries(body: str) -> int:
    return len(re.findall(r"\.\{", body))


def count_parity_entries(body: str) -> int:
    return len(re.findall(r"\.input =", body))


def count_harness_entries(body: str) -> int:
    return len(re.findall(r"\{\s*BASE64_", body))


def validate_shared_fixtures(content: str) -> None:
    for name, expected in EXPECTED_SHARED_COUNTS.items():
        body = extract_array_body(content, f"pub const {name} =")
        actual = count_entries(body)
        if actual != expected:
            raise ValidationError(
                f"{SHARED_FIXTURES_PATH.as_posix()} {name} count drift: expected {expected}, found {actual}"
            )

    perf_body = extract_array_body(content, "pub const perf_cases =")
    labels = re.findall(r'\.label = "([^"]+)"', perf_body)
    if labels != EXPECTED_PERF_LABELS:
        raise ValidationError(
            f"{SHARED_FIXTURES_PATH.as_posix()} perf label order drift: expected {EXPECTED_PERF_LABELS}, found {labels}"
        )


def validate_parity_fixtures(content: str) -> None:
    for name, expected in EXPECTED_PARITY_COUNTS.items():
        body = extract_array_body(content, f"pub const {name} =")
        actual = count_parity_entries(body)
        if actual != expected:
            raise ValidationError(
                f"{PARITY_FIXTURES_PATH.as_posix()} {name} count drift: expected {expected}, found {actual}"
            )

    for snippet in [
        "try std.testing.expectEqual(@as(usize, 17), encode_cases.len);",
        "try std.testing.expectEqual(@as(usize, 17), decode_cases.len);",
        "try std.testing.expectEqual(@as(usize, 6), invalid_cases.len);",
    ]:
        if snippet not in content:
            raise ValidationError(
                f"missing expected marker in {PARITY_FIXTURES_PATH.as_posix()}: {snippet}"
            )


def validate_harness(content: str) -> None:
    markers = {
        "encode_cases": "static const struct encode_case encode_cases[] =",
        "decode_cases": "static const struct decode_case decode_cases[] =",
        "invalid_cases": "static const struct invalid_case invalid_cases[] =",
    }
    for name, expected in EXPECTED_HARNESS_COUNTS.items():
        body = extract_array_body(content, markers[name])
        actual = count_harness_entries(body)
        if actual != expected:
            raise ValidationError(
                f"{C_HARNESS_PATH.as_posix()} {name} count drift: expected {expected}, found {actual}"
            )


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SLICE_PATH, EXPECTED_SLICE_SNIPPETS)
    require_snippets(repo_root / HELPER_TEST_PATH, EXPECTED_HELPER_TEST_SNIPPETS)
    require_snippets(repo_root / PERF_TEST_PATH, EXPECTED_PERF_TEST_SNIPPETS)
    require_snippets(repo_root / C_PARITY_TEST_PATH, EXPECTED_C_PARITY_TEST_SNIPPETS)
    require_snippets(repo_root / C_CASEGEN_PATH, EXPECTED_CASEGEN_SNIPPETS)

    shared_fixtures = read_text(repo_root / SHARED_FIXTURES_PATH)
    validate_shared_fixtures(shared_fixtures)

    parity_fixtures = read_text(repo_root / PARITY_FIXTURES_PATH)
    validate_parity_fixtures(parity_fixtures)

    shim = read_text(repo_root / PARITY_SHIM_PATH)
    if shim != EXPECTED_PARITY_SHIM:
        raise ValidationError(f"{PARITY_SHIM_PATH.as_posix()} drifted away from the fixture re-export shim")

    validate_harness(read_text(repo_root / C_HARNESS_PATH))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / SLICE_PATH, "\n".join(["# Phase 6 Base64 Slice", *EXPECTED_SLICE_SNIPPETS]) + "\n")
    write(root / HELPER_TEST_PATH, "\n".join(EXPECTED_HELPER_TEST_SNIPPETS) + "\n")
    write(root / PERF_TEST_PATH, "\n".join(EXPECTED_PERF_TEST_SNIPPETS) + "\n")
    write(root / C_PARITY_TEST_PATH, "\n".join(EXPECTED_C_PARITY_TEST_SNIPPETS) + "\n")
    write(root / C_CASEGEN_PATH, "\n".join(EXPECTED_CASEGEN_SNIPPETS) + "\n")
    write(root / PARITY_SHIM_PATH, EXPECTED_PARITY_SHIM)
    write(
        root / SHARED_FIXTURES_PATH,
        """pub const standard_cases = [_]EncodeCase{
""" + "\n".join(["    .{}," for _ in range(22)]) + """
};
pub const variant_cases = [_]VariantCase{
""" + "\n".join(["    .{}," for _ in range(18)]) + """
};
pub const standard_decode_cases = [_]DecodeCase{
""" + "\n".join(["    .{}," for _ in range(22)]) + """
};
pub const invalid_decode_cases = [_]InvalidDecodeCase{
""" + "\n".join(["    .{}," for _ in range(16)]) + """
};
pub const variant_decode_cases = [_]DecodeCase{
""" + "\n".join(["    .{}," for _ in range(18)]) + """
};
pub const perf_cases = [_]PerfCase{
    .{ .label = "STD_PAD" },
    .{ .label = "STD_NO_PAD" },
    .{ .label = "URLSAFE_PAD" },
    .{ .label = "URLSAFE_NO_PAD" },
    .{ .label = "IMAP_PAD" },
    .{ .label = "IMAP_NO_PAD" },
};
""",
    )
    write(
        root / PARITY_FIXTURES_PATH,
        """pub const encode_cases = [_]CParityEncodeCase{
""" + "\n".join(["    .{ .input = x }," for _ in range(17)]) + """
};
pub const decode_cases = [_]CParityDecodeCase{
""" + "\n".join(["    .{ .input = x }," for _ in range(17)]) + """
};
pub const invalid_cases = [_]CParityInvalidCase{
""" + "\n".join(["    .{ .input = x }," for _ in range(6)]) + """
};
try std.testing.expectEqual(@as(usize, 17), encode_cases.len);
try std.testing.expectEqual(@as(usize, 17), decode_cases.len);
try std.testing.expectEqual(@as(usize, 6), invalid_cases.len);
""",
    )
    write(
        root / C_HARNESS_PATH,
        """static const struct encode_case encode_cases[] = {
""" + "\n".join(["    { BASE64_STD, true, empty_input, 0 }," for _ in range(17)]) + """
};
static const struct decode_case decode_cases[] = {
""" + "\n".join(["    { BASE64_STD, true, empty_input, 0 }," for _ in range(17)]) + """
};
static const struct invalid_case invalid_cases[] = {
""" + "\n".join(["    { BASE64_STD, true, empty_input, 0 }," for _ in range(6)]) + """
};
""",
    )


def expect_failure(root: Path, rel_path: Path, old: str, new: str) -> None:
    path = root / rel_path
    original = read_text(path)
    if old not in original:
        raise AssertionError(f"self-test marker not found in {rel_path.as_posix()}: {old}")
    write(path, original.replace(old, new, 1))
    try:
        validate(root)
    except ValidationError:
        pass
    else:
        raise AssertionError(f"expected validation failure for {rel_path.as_posix()}")
    finally:
        write(path, original)


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_base64_corpus_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        expect_failure(root, C_PARITY_TEST_PATH, EXPECTED_C_PARITY_TEST_SNIPPETS[0], 'const parity = @import("fixtures/phase6_base64_vectors.zig");')
        expect_failure(root, C_CASEGEN_PATH, EXPECTED_CASEGEN_SNIPPETS[1], 'const parity = @import("phase6_base64_c_parity_vectors.zig");')
        expect_failure(root, PARITY_SHIM_PATH, EXPECTED_PARITY_SHIM, "")
        expect_failure(root, PARITY_FIXTURES_PATH, "try std.testing.expectEqual(@as(usize, 17), encode_cases.len);", "try std.testing.expectEqual(@as(usize, 16), encode_cases.len);")
        expect_failure(root, SHARED_FIXTURES_PATH, '.{ .label = "IMAP_NO_PAD" },', '.{ .label = "IMAP_NO_PADDING" },')
        expect_failure(root, C_HARNESS_PATH, "static const struct invalid_case invalid_cases[] = {", "static const struct invalid_case invalid_selection[] = {")

    print("PHASE6_BASE64_CORPUS_DETERMINISM_SELF_TEST=pass")
    print(f"PHASE6_BASE64_CORPUS_DETERMINISM_SELF_TEST_CASE_COUNT={SELF_TEST_CASES}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    validate(args.repo_root)
    print("PHASE6_BASE64_CORPUS_DETERMINISM=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
