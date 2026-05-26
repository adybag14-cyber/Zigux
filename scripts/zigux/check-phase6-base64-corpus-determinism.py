#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 base64 corpus-determinism packet."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    """Raised when an expected Phase 6 base64 corpus marker is missing."""


SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
HELPER_TEST_PATH = Path("zigux/tests/phase6_base64.zig")
PERF_TEST_PATH = Path("zigux/tests/phase6_base64_perf.zig")
C_PARITY_TEST_PATH = Path("zigux/tests/phase6_base64_c_parity.zig")
C_HARNESS_PATH = Path("zigux/tests/fixtures/phase6_base64_c_harness.c")

EXPECTED_COUNTS = {
    "standard_cases": 22,
    "variant_cases": 18,
    "standard_decode_cases": 22,
    "invalid_decode_cases": 16,
    "variant_decode_cases": 18,
    "perf_cases": 6,
}

EXPECTED_C_PARITY_COUNTS = {
    "c_parity_encode_cases": 17,
    "c_parity_decode_cases": 17,
    "c_parity_invalid_cases": 6,
}

EXPECTED_C_HARNESS_COUNTS = {
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
    "- helper-local corpus checker: `scripts/zigux/check-phase6-base64-corpus-determinism.py`",
    "- exact fixture-owned corpus counts on current `master`: 22 standard encode cases, 18 variant encode cases, 22 standard decode cases, 18 variant decode cases, 16 invalid decode cases, and 6 perf replay cases, all centralized in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by `zigux/tests/phase6_base64.zig` or `zigux/tests/phase6_base64_perf.zig`",
    "- exact helper-local perf replay packet: ordered labels `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`, each with `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, owned once in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by the helper-local perf gate",
    "- invalid-input rejection for malformed, embedded-NUL, and variant-mismatched decode inputs",
]

EXPECTED_HELPER_TEST_SNIPPETS = [
    'for (fixtures.standard_cases) |case| {',
    'for (fixtures.variant_cases) |case| {',
    'for (fixtures.standard_decode_cases) |case| {',
    'for (fixtures.invalid_decode_cases) |case| {',
    'for (fixtures.variant_decode_cases) |case| {',
    'try std.testing.expectError(base64.DecodeError.InvalidInput, base64.bytes(case.input, case.padding, variant));',
    'try std.testing.expectError(base64.DecodeError.InvalidInput, base64.decode(buf[0..], case.input, case.padding, variant));',
]

EXPECTED_INVALID_FIXTURE_SNIPPETS = [
    "const invalid_with_nul = [_]u8{ 'Z', 'g', 0, '=' };",
    '.{ .input = "Zg=!", .padding = true, .variant_name = "std" },',
    '.{ .input = "Zm$=", .padding = true, .variant_name = "std" },',
    '.{ .input = invalid_with_nul[0..], .padding = true, .variant_name = "std" },',
    '.{ .input = invalid_with_nul[0..], .padding = false, .variant_name = "std" },',
    '.{ .input = "Zg==", .padding = false, .variant_name = "urlsafe" },',
    '.{ .input = "Zg==", .padding = false, .variant_name = "imap" },',
]

EXPECTED_C_PARITY_FIXTURE_SNIPPETS = [
    "pub const CParityEncodeCase = struct {",
    "pub const CParityDecodeCase = struct {",
    "pub const CParityInvalidCase = struct {",
    "pub const c_parity_encode_cases = [_]CParityEncodeCase{",
    '    .{ .variant_name = "std", .padding = standard_cases[17].padding, .input = standard_cases[17].input },',
    '    .{ .variant_name = variant_cases[14].variant_name, .padding = variant_cases[14].padding, .input = variant_cases[14].input },',
    "pub const c_parity_decode_cases = [_]CParityDecodeCase{",
    "pub const c_parity_invalid_cases = [_]CParityInvalidCase{",
]

EXPECTED_PERF_TEST_SNIPPETS = [
    "fn validatePerfMatrix() !void {",
    "if (fixtures.perf_payload.len != fixtures.perf_payload_buf_size) {",
    "if (fixtures.perf_encoded_buf_size < base64.chars(case.payload.len, case.padding)) {",
    "for (fixtures.perf_cases, 0..) |case, idx| {",
    "try validatePerfMatrix();",
]

EXPECTED_C_PARITY_SNIPPETS = [
    'const fixtures = @import("fixtures/phase6_base64_vectors.zig");',
    "for (fixtures.c_parity_encode_cases) |case| {",
    "for (fixtures.c_parity_decode_cases) |case| {",
    "for (fixtures.c_parity_invalid_cases) |case| {",
    'const bytes_result = base64.bytes(case.input, case.padding, variant);',
    'try writer.print("inv\\t{s}\\t{}\\t", .{ case.variant_name, @intFromBool(case.padding) });',
]

EXPECTED_C_HARNESS_SNIPPETS = [
    "static const unsigned char invalid_with_nul[] = { 'Z', 'g', 0, '=' };",
    "{ BASE64_STD, true, empty_input, 0 },",
    "{ BASE64_STD, false, foobar, 6 },",
    "{ BASE64_STD, true, invalid_with_nul, sizeof(invalid_with_nul) },",
    "{ BASE64_URLSAFE, false, variant_sample, sizeof(variant_sample) },",
    "{ BASE64_URLSAFE, true, variant_two_byte, sizeof(variant_two_byte) },",
    "{ BASE64_IMAP, false, variant_one_byte, sizeof(variant_one_byte) },",
    "{ BASE64_IMAP, true, variant_two_byte, sizeof(variant_two_byte) },",
    '{ BASE64_URLSAFE, false, (const unsigned char *)"Zg==", 4 },',
    '{ BASE64_IMAP, false, (const unsigned char *)"Zg==", 4 },',
]

SELF_TEST_CASES = 15


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 6 base64 corpus marker in {path.as_posix()}: {snippet}"
            )


def extract_array_body(content: str, name: str) -> str:
    marker = f"pub const {name} ="
    start = content.find(marker)
    if start == -1:
        raise ValidationError(
            f"missing expected Phase 6 base64 corpus array in {FIXTURES_PATH.as_posix()}: {name}"
        )

    brace_start = content.find("{", start)
    if brace_start == -1:
        raise ValidationError(
            f"missing opening brace for Phase 6 base64 corpus array in {FIXTURES_PATH.as_posix()}: {name}"
        )

    depth = 0
    for idx in range(brace_start, len(content)):
        char = content[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return content[brace_start + 1 : idx]

    raise ValidationError(
        f"unterminated Phase 6 base64 corpus array in {FIXTURES_PATH.as_posix()}: {name}"
    )


def extract_c_array_body(content: str, name: str) -> str:
    marker = f"{name}[] = {{"
    start = content.find(marker)
    if start == -1:
        raise ValidationError(
            f"missing expected Phase 6 base64 harness array in {C_HARNESS_PATH.as_posix()}: {name}"
        )

    brace_start = content.find("{", start)
    if brace_start == -1:
        raise ValidationError(
            f"missing opening brace for Phase 6 base64 harness array in {C_HARNESS_PATH.as_posix()}: {name}"
        )

    depth = 0
    for idx in range(brace_start, len(content)):
        char = content[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return content[brace_start + 1 : idx]

    raise ValidationError(
        f"unterminated Phase 6 base64 harness array in {C_HARNESS_PATH.as_posix()}: {name}"
    )


def count_entries(body: str) -> int:
    return len(re.findall(r"\.\{", body))


def count_c_parity_entries(body: str) -> int:
    return len(re.findall(r"\.input =", body))


def count_c_harness_entries(body: str) -> int:
    return len(re.findall(r"\{\s*BASE64_", body))


def validate_fixture_counts(content: str) -> None:
    for name, expected in EXPECTED_COUNTS.items():
        body = extract_array_body(content, name)
        actual = count_entries(body)
        if actual != expected:
            raise ValidationError(
                f"{FIXTURES_PATH.as_posix()} {name} count drift: expected {expected}, found {actual}"
            )


def validate_c_parity_fixture_counts(content: str) -> None:
    for name, expected in EXPECTED_C_PARITY_COUNTS.items():
        body = extract_array_body(content, name)
        actual = count_c_parity_entries(body)
        if actual != expected:
            raise ValidationError(
                f"{FIXTURES_PATH.as_posix()} {name} count drift: expected {expected}, found {actual}"
            )


def validate_c_harness_counts(content: str) -> None:
    for name, expected in EXPECTED_C_HARNESS_COUNTS.items():
        body = extract_c_array_body(content, name)
        actual = count_c_harness_entries(body)
        if actual != expected:
            raise ValidationError(
                f"{C_HARNESS_PATH.as_posix()} {name} count drift: expected {expected}, found {actual}"
            )


def validate_perf_labels(content: str) -> None:
    body = extract_array_body(content, "perf_cases")
    labels = re.findall(r'\.label = "([^"]+)"', body)
    if labels != EXPECTED_PERF_LABELS:
        raise ValidationError(
            f"{FIXTURES_PATH.as_posix()} perf label order drift: expected {EXPECTED_PERF_LABELS}, found {labels}"
        )

    iterations = re.findall(r"\.iterations = (\d+)", body)
    if iterations != ["12000"] * len(EXPECTED_PERF_LABELS):
        raise ValidationError(
            f"{FIXTURES_PATH.as_posix()} perf iteration drift: expected six 12000 entries, found {iterations}"
        )

    encode_thresholds = re.findall(r"\.max_encode_slowdown_pct = (\d+)", body)
    if encode_thresholds != ["150"] * len(EXPECTED_PERF_LABELS):
        raise ValidationError(
            f"{FIXTURES_PATH.as_posix()} encode threshold drift: expected six 150 entries, found {encode_thresholds}"
        )

    decode_thresholds = re.findall(r"\.max_decode_slowdown_pct = (\d+)", body)
    if decode_thresholds != ["325"] * len(EXPECTED_PERF_LABELS):
        raise ValidationError(
            f"{FIXTURES_PATH.as_posix()} decode threshold drift: expected six 325 entries, found {decode_thresholds}"
        )

    if (
        'test "phase 6 base64 perf fixture packet stays bounded to the documented matrix" {'
        not in content
    ):
        raise ValidationError(
            f"missing expected Phase 6 base64 corpus self-test in {FIXTURES_PATH.as_posix()}"
        )


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SLICE_PATH, EXPECTED_SLICE_SNIPPETS)
    require_snippets(repo_root / HELPER_TEST_PATH, EXPECTED_HELPER_TEST_SNIPPETS)
    require_snippets(repo_root / PERF_TEST_PATH, EXPECTED_PERF_TEST_SNIPPETS)
    require_snippets(repo_root / C_PARITY_TEST_PATH, EXPECTED_C_PARITY_SNIPPETS)

    fixtures_content = read_text(repo_root / FIXTURES_PATH)
    validate_fixture_counts(fixtures_content)
    validate_c_parity_fixture_counts(fixtures_content)
    validate_perf_labels(fixtures_content)
    for snippet in EXPECTED_INVALID_FIXTURE_SNIPPETS:
        if snippet not in fixtures_content:
            raise ValidationError(
                f"missing expected Phase 6 base64 corpus marker in {FIXTURES_PATH.as_posix()}: {snippet}"
            )
    for snippet in EXPECTED_C_PARITY_FIXTURE_SNIPPETS:
        if snippet not in fixtures_content:
            raise ValidationError(
                f"missing expected Phase 6 base64 c-parity marker in {FIXTURES_PATH.as_posix()}: {snippet}"
            )

    c_harness_content = read_text(repo_root / C_HARNESS_PATH)
    validate_c_harness_counts(c_harness_content)
    for snippet in EXPECTED_C_HARNESS_SNIPPETS:
        if snippet not in c_harness_content:
            raise ValidationError(
                f"missing expected Phase 6 base64 harness marker in {C_HARNESS_PATH.as_posix()}: {snippet}"
            )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(
        root / SLICE_PATH,
        "\n".join(
            [
                "# Phase 6 Base64 Slice",
                *EXPECTED_SLICE_SNIPPETS,
            ]
        )
        + "\n",
    )
    write(
        root / HELPER_TEST_PATH,
        "\n".join(EXPECTED_HELPER_TEST_SNIPPETS) + "\n",
    )
    write(
        root / PERF_TEST_PATH,
        "\n".join(EXPECTED_PERF_TEST_SNIPPETS) + "\n",
    )
    write(
        root / C_PARITY_TEST_PATH,
        "\n".join(EXPECTED_C_PARITY_SNIPPETS) + "\n",
    )
    write(
        root / C_HARNESS_PATH,
        """static const unsigned char invalid_with_nul[] = { 'Z', 'g', 0, '=' };
static const struct encode_case encode_cases[] = {
    { BASE64_STD, true, empty_input, 0 },
    { BASE64_STD, true, one_byte, 1 },
    { BASE64_STD, true, two_bytes, 2 },
    { BASE64_STD, false, foobar, 6 },
    { BASE64_STD, true, hello_world, 13 },
    { BASE64_URLSAFE, false, variant_sample, sizeof(variant_sample) },
    { BASE64_URLSAFE, true, variant_sample, sizeof(variant_sample) },
    { BASE64_URLSAFE, false, variant_one_byte, sizeof(variant_one_byte) },
    { BASE64_URLSAFE, true, variant_one_byte, sizeof(variant_one_byte) },
    { BASE64_URLSAFE, false, variant_two_byte, sizeof(variant_two_byte) },
    { BASE64_URLSAFE, true, variant_two_byte, sizeof(variant_two_byte) },
    { BASE64_IMAP, false, variant_sample, sizeof(variant_sample) },
    { BASE64_IMAP, true, variant_sample, sizeof(variant_sample) },
    { BASE64_IMAP, false, variant_one_byte, sizeof(variant_one_byte) },
    { BASE64_IMAP, true, variant_one_byte, sizeof(variant_one_byte) },
    { BASE64_IMAP, false, variant_two_byte, sizeof(variant_two_byte) },
    { BASE64_IMAP, true, variant_two_byte, sizeof(variant_two_byte) },
};
static const struct decode_case decode_cases[] = {
    { BASE64_STD, true, (const unsigned char *)"", 0 },
    { BASE64_STD, true, (const unsigned char *)"Zg==", 4 },
    { BASE64_STD, true, (const unsigned char *)"Zm8=", 4 },
    { BASE64_STD, false, (const unsigned char *)"Zm9vYmFy", 8 },
    { BASE64_STD, true, (const unsigned char *)"SGVsbG8sIHdvcmxkIQ==", 20 },
    { BASE64_URLSAFE, false, (const unsigned char *)"APv_f4A", 7 },
    { BASE64_URLSAFE, true, (const unsigned char *)"APv_f4A=", 8 },
    { BASE64_URLSAFE, false, (const unsigned char *)"-w", 2 },
    { BASE64_URLSAFE, true, (const unsigned char *)"-w==", 4 },
    { BASE64_URLSAFE, false, (const unsigned char *)"__A", 3 },
    { BASE64_URLSAFE, true, (const unsigned char *)"__A=", 4 },
    { BASE64_IMAP, false, (const unsigned char *)"APv,f4A", 7 },
    { BASE64_IMAP, true, (const unsigned char *)"APv,f4A=", 8 },
    { BASE64_IMAP, false, (const unsigned char *)"+w", 2 },
    { BASE64_IMAP, true, (const unsigned char *)"+w==", 4 },
    { BASE64_IMAP, false, (const unsigned char *)",,A", 3 },
    { BASE64_IMAP, true, (const unsigned char *)",,A=", 4 },
};
static const struct invalid_case invalid_cases[] = {
    { BASE64_STD, true, (const unsigned char *)"Zg=!", 4 },
    { BASE64_STD, true, (const unsigned char *)"Z===", 4 },
    { BASE64_STD, false, (const unsigned char *)"Zm9v====", 8 },
    { BASE64_STD, true, invalid_with_nul, sizeof(invalid_with_nul) },
    { BASE64_URLSAFE, false, (const unsigned char *)"Zg==", 4 },
    { BASE64_IMAP, false, (const unsigned char *)"Zg==", 4 },
};
""",
    )
    write(
        root / FIXTURES_PATH,
        """pub const CParityEncodeCase = struct {
};
pub const CParityDecodeCase = struct {
};
pub const CParityInvalidCase = struct {
};
pub const standard_cases = [_]EncodeCase{
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
    .{},
};
pub const variant_cases = [_]VariantCase{
    .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{},
    .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{},
};
pub const standard_decode_cases = [_]DecodeCase{
    .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{},
    .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{},
};
const invalid_with_nul = [_]u8{ 'Z', 'g', 0, '=' };
pub const invalid_decode_cases = [_]InvalidDecodeCase{
    .{ .input = "Zg=!", .padding = true, .variant_name = "std" },
    .{ .input = "Zm$=", .padding = true, .variant_name = "std" },
    .{}, .{}, .{}, .{},
    .{ .input = invalid_with_nul[0..], .padding = true, .variant_name = "std" },
    .{}, .{}, .{}, .{}, .{}, .{},
    .{ .input = invalid_with_nul[0..], .padding = false, .variant_name = "std" },
    .{ .input = "Zg==", .padding = false, .variant_name = "urlsafe" },
    .{ .input = "Zg==", .padding = false, .variant_name = "imap" },
};
pub const variant_decode_cases = [_]DecodeCase{
    .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{},
    .{}, .{}, .{}, .{}, .{}, .{},
};
pub const c_parity_encode_cases = [_]CParityEncodeCase{
    .{ .variant_name = "std", .padding = standard_cases[17].padding, .input = standard_cases[17].input },
    .{ .variant_name = variant_cases[14].variant_name, .padding = variant_cases[14].padding, .input = variant_cases[14].input },
    .{ .input = standard_cases[0].input }, .{ .input = standard_cases[1].input }, .{ .input = standard_cases[2].input },
    .{ .input = standard_cases[7].input }, .{ .input = variant_cases[2].input }, .{ .input = variant_cases[3].input },
    .{ .input = variant_cases[8].input }, .{ .input = variant_cases[9].input }, .{ .input = variant_cases[15].input },
    .{ .input = variant_cases[4].input }, .{ .input = variant_cases[5].input }, .{ .input = variant_cases[10].input },
    .{ .input = variant_cases[11].input }, .{ .input = variant_cases[16].input }, .{ .input = variant_cases[17].input },
};
pub const c_parity_decode_cases = [_]CParityDecodeCase{
    .{ .input = standard_decode_cases[0].input }, .{ .input = standard_decode_cases[1].input }, .{ .input = standard_decode_cases[2].input },
    .{ .input = standard_decode_cases[16].input }, .{ .input = standard_decode_cases[7].input }, .{ .input = variant_decode_cases[2].input },
    .{ .input = variant_decode_cases[3].input }, .{ .input = variant_decode_cases[8].input }, .{ .input = variant_decode_cases[9].input },
    .{ .input = variant_decode_cases[14].input }, .{ .input = variant_decode_cases[15].input }, .{ .input = variant_decode_cases[4].input },
    .{ .input = variant_decode_cases[5].input }, .{ .input = variant_decode_cases[10].input }, .{ .input = variant_decode_cases[11].input },
    .{ .input = variant_decode_cases[16].input }, .{ .input = variant_decode_cases[17].input },
};
pub const c_parity_invalid_cases = [_]CParityInvalidCase{
    .{ .input = invalid_decode_cases[0].input }, .{ .input = invalid_decode_cases[2].input }, .{ .input = invalid_decode_cases[11].input },
    .{ .input = invalid_decode_cases[6].input }, .{ .input = invalid_decode_cases[14].input }, .{ .input = invalid_decode_cases[15].input },
};
pub const perf_cases = [_]PerfCase{
    .{ .label = "STD_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "STD_NO_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "URLSAFE_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "URLSAFE_NO_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "IMAP_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
    .{ .label = "IMAP_NO_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },
};
test "phase 6 base64 perf fixture packet stays bounded to the documented matrix" {
}
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
    except ValidationError as exc:
        if rel_path.as_posix() not in str(exc):
            raise AssertionError(
                f"expected failure mentioning {rel_path.as_posix()}, got {exc}"
            ) from exc
    else:
        raise AssertionError(f"expected validation failure for {rel_path.as_posix()}")
    finally:
        write(path, original)


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_base64_corpus_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        expect_failure(
            root,
            SLICE_PATH,
            EXPECTED_SLICE_SNIPPETS[0],
            "- helper-local corpus checker: `scripts/zigux/check-phase6-base64-corpus-proof.py`",
        )
        expect_failure(
            root,
            SLICE_PATH,
            EXPECTED_SLICE_SNIPPETS[1],
            "- exact fixture-owned corpus counts on current `master`: 21 standard encode cases only",
        )
        expect_failure(
            root,
            FIXTURES_PATH,
            '.{ .label = "IMAP_NO_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
            '.{ .label = "IMAP_NO_PAD", .iterations = 9000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        )
        expect_failure(
            root,
            FIXTURES_PATH,
            '.{ .label = "URLSAFE_NO_PAD", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
            '.{ .label = "URLSAFE_NO_PADDING", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        )
        expect_failure(
            root,
            FIXTURES_PATH,
            'test "phase 6 base64 perf fixture packet stays bounded to the documented matrix" {',
            'test "phase 6 base64 fixture packet" {',
        )
        expect_failure(
            root,
            HELPER_TEST_PATH,
            EXPECTED_HELPER_TEST_SNIPPETS[4],
            'for (fixtures.variant_decode_matrix) |case| {',
        )
        expect_failure(
            root,
            PERF_TEST_PATH,
            EXPECTED_PERF_TEST_SNIPPETS[1],
            "if (fixtures.perf_payload.len != fixtures.perf_payload_buf_size + 1) {",
        )
        expect_failure(
            root,
            FIXTURES_PATH,
            "pub const invalid_decode_cases = [_]InvalidDecodeCase{",
            "pub const invalid_cases = [_]InvalidDecodeCase{",
        )
        expect_failure(
            root,
            FIXTURES_PATH,
            '.{ .input = invalid_with_nul[0..], .padding = true, .variant_name = "std" },',
            '.{ .input = "Zg==", .padding = true, .variant_name = "std" },',
        )
        expect_failure(
            root,
            FIXTURES_PATH,
            '.{ .input = "Zg==", .padding = false, .variant_name = "urlsafe" },',
            '.{ .input = "Zg==", .padding = false, .variant_name = "std" },',
        )
        expect_failure(
            root,
            C_PARITY_TEST_PATH,
            EXPECTED_C_PARITY_SNIPPETS[0],
            'const fixtures = @import("fixtures/phase6_base64_c_parity_vectors.zig");',
        )
        expect_failure(
            root,
            FIXTURES_PATH,
            "pub const c_parity_encode_cases = [_]CParityEncodeCase{",
            "pub const c_parity_encode_selection = [_]CParityEncodeCase{",
        )
        expect_failure(
            root,
            FIXTURES_PATH,
            '    .{ .variant_name = variant_cases[14].variant_name, .padding = variant_cases[14].padding, .input = variant_cases[14].input },',
            '    .{ .variant_name = variant_cases[13].variant_name, .padding = variant_cases[13].padding, .input = variant_cases[13].input },',
        )
        expect_failure(
            root,
            C_HARNESS_PATH,
            "static const struct encode_case encode_cases[] = {",
            "static const struct encode_case encode_selection[] = {",
        )
        expect_failure(
            root,
            C_HARNESS_PATH,
            '{ BASE64_IMAP, false, (const unsigned char *)"Zg==", 4 },',
            '{ BASE64_IMAP, false, (const unsigned char *)"Zm9v", 4 },',
        )

    print("PHASE6_BASE64_CORPUS_DETERMINISM_SELF_TEST=pass")
    print(f"PHASE6_BASE64_CORPUS_DETERMINISM_SELF_TEST_CASE_COUNT={SELF_TEST_CASES}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root to validate (default: current directory)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in self-test instead of validating a repository",
    )
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
