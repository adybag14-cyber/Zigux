#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 base64 corpus determinism packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
FIXTURE_PATH = Path("zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig")
CASEGEN_PATH = Path("zigux/tests/phase6_base64_c_casegen.zig")
PARITY_SCRIPT_PATH = Path("scripts/zigux/check-phase6-base64-c-parity.py")
GENERATED_INCLUDE_PATH = Path("zigux/tests/fixtures/phase6_base64_c_generated_cases.inc")

ARRAY_LABELS = {
    "standard_cases": 4,
    "variant_cases": 4,
    "standard_decode_cases": 4,
    "variant_decode_cases": 4,
    "invalid_decode_cases": 8,
}

FIELD_RE = re.compile(r"\.\{\s*(.*?)\s*\}", re.S)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc


def extract_array_block(text: str, name: str) -> str:
    marker = f"pub const {name} ="
    start = text.find(marker)
    if start == -1:
        raise ValidationError(f"missing fixture array: {name}")
    brace_start = text.find("{", start)
    if brace_start == -1:
        raise ValidationError(f"missing fixture block for: {name}")

    depth = 0
    for index in range(brace_start, len(text)):
        ch = text[index]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[brace_start + 1 : index]
    raise ValidationError(f"unterminated fixture block for: {name}")


def count_entries(block: str) -> int:
    return len(FIELD_RE.findall(block))


def validate_fixture_counts(repo_root: Path) -> None:
    text = read_text(repo_root / FIXTURE_PATH)
    observed = {}
    for label, expected in ARRAY_LABELS.items():
        observed[label] = count_entries(extract_array_block(text, label))
        if observed[label] != expected:
            raise ValidationError(
                f"unexpected {label} count in {FIXTURE_PATH}: "
                f"expected {expected}, got {observed[label]}"
            )

    if "phase6 base64 direct parity corpus stays compact and portable" not in text:
        raise ValidationError(f"missing compact-corpus regression test marker in {FIXTURE_PATH}")

    total_cases = sum(observed.values())
    if total_cases != 24:
        raise ValidationError(f"unexpected total base64 parity case count in {FIXTURE_PATH}: {total_cases}")


def validate_manifest(repo_root: Path) -> None:
    manifest = read_json(repo_root / MANIFEST_PATH)
    if not isinstance(manifest, dict):
        raise ValidationError(f"expected object in {MANIFEST_PATH}")

    determinism = manifest.get("determinism_evidence")
    if not isinstance(determinism, dict):
        raise ValidationError(f"missing determinism_evidence in {MANIFEST_PATH}")

    base64 = determinism.get("base64")
    if not isinstance(base64, dict):
        raise ValidationError(f"missing base64 determinism evidence in {MANIFEST_PATH}")

    expected_counts = {
        "standard_encode_vectors": 4,
        "variant_encode_vectors": 4,
        "standard_decode_vectors": 4,
        "variant_decode_vectors": 4,
        "invalid_decode_vectors": 8,
        "c_parity_cases": 24,
    }
    for key, expected in expected_counts.items():
        if base64.get(key) != expected:
            raise ValidationError(
                f"unexpected {key} in {MANIFEST_PATH}: expected {expected}, got {base64.get(key)!r}"
            )

    if base64.get("transient_generated_include_committed") is not False:
        raise ValidationError(
            f"unexpected transient_generated_include_committed in {MANIFEST_PATH}: "
            f"{base64.get('transient_generated_include_committed')!r}"
        )

    if determinism.get("generated_fixture_artifacts_committed") is not False:
        raise ValidationError(
            f"unexpected generated_fixture_artifacts_committed in {MANIFEST_PATH}: "
            f"{determinism.get('generated_fixture_artifacts_committed')!r}"
        )

    fixture_posture = manifest.get("fixture_posture")
    if not isinstance(fixture_posture, dict):
        raise ValidationError(f"missing fixture_posture in {MANIFEST_PATH}")
    base64_posture = fixture_posture.get("base64")
    if not isinstance(base64_posture, dict):
        raise ValidationError(f"missing base64 fixture_posture in {MANIFEST_PATH}")
    if base64_posture.get("transient_generated_include") != GENERATED_INCLUDE_PATH.as_posix():
        raise ValidationError(
            f"unexpected transient_generated_include path in {MANIFEST_PATH}: "
            f"{base64_posture.get('transient_generated_include')!r}"
        )
    if base64_posture.get("transient_generated_include_committed") is not False:
        raise ValidationError(
            f"unexpected fixture_posture transient_generated_include_committed in {MANIFEST_PATH}: "
            f"{base64_posture.get('transient_generated_include_committed')!r}"
        )


def validate_generated_include_absent(repo_root: Path) -> None:
    if (repo_root / GENERATED_INCLUDE_PATH).exists():
        raise ValidationError(
            f"generated include should stay uncommitted in the current packet: {GENERATED_INCLUDE_PATH}"
        )


def validate_companion_sources(repo_root: Path) -> None:
    casegen_text = read_text(repo_root / CASEGEN_PATH)
    for snippet in [
        'const fixtures = @import("fixtures/phase6_base64_c_parity_vectors.zig");',
        "Generated from zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig.",
        "fixtures.standard_cases",
        "fixtures.variant_cases",
        "fixtures.standard_decode_cases",
        "fixtures.variant_decode_cases",
        "fixtures.invalid_decode_cases",
    ]:
        if snippet not in casegen_text:
            raise ValidationError(f"missing expected casegen marker in {CASEGEN_PATH}: {snippet}")

    parity_script_text = read_text(repo_root / PARITY_SCRIPT_PATH)
    for snippet in [
        'FIXTURE_SOURCE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_parity_vectors.zig"',
        'GENERATED_INCLUDE = ROOT / "zigux" / "tests" / "fixtures" / "phase6_base64_c_generated_cases.inc"',
        'print(f"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}")',
    ]:
        if snippet not in parity_script_text:
            raise ValidationError(f"missing expected parity-script marker in {PARITY_SCRIPT_PATH}: {snippet}")


def run_checks(repo_root: Path) -> None:
    validate_fixture_counts(repo_root)
    validate_manifest(repo_root)
    validate_generated_include_absent(repo_root)
    validate_companion_sources(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "determinism_evidence": {
                    "base64": {
                        "standard_encode_vectors": 4,
                        "variant_encode_vectors": 4,
                        "standard_decode_vectors": 4,
                        "variant_decode_vectors": 4,
                        "invalid_decode_vectors": 8,
                        "c_parity_cases": 24,
                        "transient_generated_include_committed": False,
                    },
                    "generated_fixture_artifacts_committed": False,
                },
                "fixture_posture": {
                    "base64": {
                        "transient_generated_include": GENERATED_INCLUDE_PATH.as_posix(),
                        "transient_generated_include_committed": False,
                    }
                },
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / FIXTURE_PATH,
        """const std = @import(\"std\");

pub const EncodeCase = struct { input: []const u8, expected: []const u8, padding: bool };
pub const VariantCase = struct { input: []const u8, expected: []const u8, padding: bool, variant_name: []const u8 };
pub const DecodeCase = struct { input: []const u8, expected: []const u8, padding: bool, variant_name: []const u8 };
pub const InvalidDecodeCase = struct { input: []const u8, padding: bool, variant_name: []const u8 };
const empty = [_]u8{};
const one_byte_fb = [_]u8{0xfb};
const three_ff = [_]u8{ 0xfb, 0xff, 0xff };
const invalid_with_nul = [_]u8{ 'Z', 'g', 0, '=' };

pub const standard_cases = [_]EncodeCase{
    .{ .input = empty[0..], .expected = \"\", .padding = true },
    .{ .input = \"f\", .expected = \"Zg==\", .padding = true },
    .{ .input = \"fo\", .expected = \"Zm8=\", .padding = true },
    .{ .input = \"foo\", .expected = \"Zm9v\", .padding = true },
};
pub const variant_cases = [_]VariantCase{
    .{ .input = &one_byte_fb, .expected = \"-w\", .padding = false, .variant_name = \"urlsafe\" },
    .{ .input = &one_byte_fb, .expected = \"-w==\", .padding = true, .variant_name = \"urlsafe\" },
    .{ .input = &one_byte_fb, .expected = \"+w==\", .padding = true, .variant_name = \"imap\" },
    .{ .input = &three_ff, .expected = \"+,,,\", .padding = false, .variant_name = \"imap\" },
};
pub const standard_decode_cases = [_]DecodeCase{
    .{ .input = \"\", .expected = empty[0..], .padding = true, .variant_name = \"std\" },
    .{ .input = \"Zg==\", .expected = \"f\", .padding = true, .variant_name = \"std\" },
    .{ .input = \"Zm8=\", .expected = \"fo\", .padding = true, .variant_name = \"std\" },
    .{ .input = \"Zm9v\", .expected = \"foo\", .padding = true, .variant_name = \"std\" },
};
pub const variant_decode_cases = [_]DecodeCase{
    .{ .input = \"-w\", .expected = &one_byte_fb, .padding = false, .variant_name = \"urlsafe\" },
    .{ .input = \"-w==\", .expected = &one_byte_fb, .padding = true, .variant_name = \"urlsafe\" },
    .{ .input = \"+w==\", .expected = &one_byte_fb, .padding = true, .variant_name = \"imap\" },
    .{ .input = \"+,,,\", .expected = &three_ff, .padding = false, .variant_name = \"imap\" },
};
pub const invalid_decode_cases = [_]InvalidDecodeCase{
    .{ .input = \"A\", .padding = false, .variant_name = \"std\" },
    .{ .input = \"AA=A\", .padding = true, .variant_name = \"std\" },
    .{ .input = \"AR==\", .padding = true, .variant_name = \"std\" },
    .{ .input = \"aGl=\", .padding = true, .variant_name = \"std\" },
    .{ .input = \"-___\", .padding = false, .variant_name = \"std\" },
    .{ .input = \"+///\", .padding = false, .variant_name = \"urlsafe\" },
    .{ .input = \"+///\", .padding = false, .variant_name = \"imap\" },
    .{ .input = invalid_with_nul[0..], .padding = true, .variant_name = \"std\" },
};

test \"phase6 base64 direct parity corpus stays compact and portable\" {
    try std.testing.expectEqual(@as(usize, 4), standard_cases.len);
    try std.testing.expectEqual(@as(usize, 4), variant_cases.len);
    try std.testing.expectEqual(@as(usize, 4), standard_decode_cases.len);
    try std.testing.expectEqual(@as(usize, 4), variant_decode_cases.len);
    try std.testing.expectEqual(@as(usize, 8), invalid_decode_cases.len);
}
""",
    )
    write(
        root / CASEGEN_PATH,
        """const fixtures = @import(\"fixtures/phase6_base64_c_parity_vectors.zig\");
/* Generated from zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig. */
pub fn main() void {
    _ = fixtures.standard_cases;
    _ = fixtures.variant_cases;
    _ = fixtures.standard_decode_cases;
    _ = fixtures.variant_decode_cases;
    _ = fixtures.invalid_decode_cases;
}
""",
    )
    write(
        root / PARITY_SCRIPT_PATH,
        """FIXTURE_SOURCE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase6_base64_c_parity_vectors.zig\"
GENERATED_INCLUDE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase6_base64_c_generated_cases.inc\"
print(f\"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}\")
""",
    )


def expect_failure(root: Path, rel_path: Path, old: str, new: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    if old not in original:
        raise AssertionError(f"self-test marker missing in {rel_path}: {old}")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        run_checks(root)
    except ValidationError:
        pass
    else:
        raise AssertionError(f"expected failure for {rel_path}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        run_checks(root)

        expect_failure(
            root,
            MANIFEST_PATH,
            '"variant_encode_vectors": 4',
            '"variant_encode_vectors": 3',
        )
        expect_failure(
            root,
            MANIFEST_PATH,
            '"transient_generated_include_committed": false',
            '"transient_generated_include_committed": true',
        )
        expect_failure(
            root,
            MANIFEST_PATH,
            '"generated_fixture_artifacts_committed": false',
            '"generated_fixture_artifacts_committed": true',
        )
        expect_failure(
            root,
            FIXTURE_PATH,
            "pub const invalid_decode_cases = [_]InvalidDecodeCase{",
            "pub const invalid_cases = [_]InvalidDecodeCase{",
        )
        expect_failure(
            root,
            FIXTURE_PATH,
            '.{ .input = \"+///\", .padding = false, .variant_name = \"imap\" },',
            "",
        )
        expect_failure(
            root,
            CASEGEN_PATH,
            "fixtures.invalid_decode_cases",
            "fixtures.invalid_cases",
        )
        expect_failure(
            root,
            PARITY_SCRIPT_PATH,
            'GENERATED_INCLUDE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase6_base64_c_generated_cases.inc\"',
            'GENERATED_INCLUDE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase6_base64_generated.inc\"',
        )

        generated_include = root / GENERATED_INCLUDE_PATH
        generated_include.parent.mkdir(parents=True, exist_ok=True)
        generated_include.write_text("transient", encoding="utf-8")
        try:
            run_checks(root)
        except ValidationError as exc:
            if GENERATED_INCLUDE_PATH.as_posix() not in str(exc):
                raise AssertionError(f"unexpected generated-include failure: {exc}") from exc
        else:
            raise AssertionError("expected generated-include failure")

    print("PHASE6_BASE64_CORPUS_DETERMINISM_SELF_TEST=pass")
    print("PHASE6_BASE64_CORPUS_DETERMINISM_SELF_TEST_CASE_COUNT=8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    run_checks(Path(args.repo_root).resolve())
    print("PHASE6_BASE64_CORPUS_DETERMINISM=pass")
    print("PHASE6_BASE64_CORPUS_DETERMINISM_COUNTS=4/4/4/4/8")
    print("PHASE6_BASE64_CORPUS_DETERMINISM_CASES=24")
    print("PHASE6_BASE64_CORPUS_DETERMINISM_GENERATED_INCLUDE_COMMITTED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
