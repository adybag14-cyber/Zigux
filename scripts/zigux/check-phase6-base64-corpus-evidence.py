#!/usr/bin/env python3
"""Fail-closed exact evidence checks for the Phase 6 base64 corpus packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")
MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
PERF_SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
GENERATED_INCLUDE_PATH = Path("zigux/tests/fixtures/phase6_base64_c_generated_cases.inc")

EXPECTED_ARRAY_COUNTS = {
    "standard_cases": 22,
    "variant_cases": 4,
    "standard_decode_cases": 22,
    "variant_decode_cases": 4,
    "invalid_decode_cases": 24,
    "perf_cases": 4,
}

EXPECTED_PERF_LABELS = [
    "STD_PAD",
    "STD_NO_PAD",
    "URLSAFE_PAD",
    "URLSAFE_NO_PAD",
]

EXPECTED_MANIFEST_BASE64 = {
    "standard_encode_vectors": 22,
    "variant_encode_vectors": 4,
    "standard_decode_vectors": 22,
    "variant_decode_vectors": 4,
    "invalid_decode_vectors": 24,
    "perf_payload_cases": 1,
    "perf_replay_cases": 4,
    "c_parity_cases": 24,
    "transient_generated_include_committed": False,
}

REQUIRED_PERF_SNIPPETS = [
    'const fixtures = @import("fixtures/phase6_base64_vectors.zig");',
    'const PerfCase = fixtures.PerfCase;',
    'try std.testing.expectEqual(expected_perf_cases.len, fixtures.perf_cases.len);',
    'test "phase 6 base64 perf matrix keeps all shipped variant-and-padding replays" {',
    'test "phase 6 base64 perf cases keep helper and reference codecs aligned before timing" {',
]

REQUIRED_SLICE_SNIPPETS = [
    "- current `master` keeps `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig`",
    "- direct focused perf route: `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`",
]

REQUIRED_PERF_SURVEY_SNIPPETS = [
    "* base64 shared posture: `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig` are directly readable on current `master`, and current `zigux/tests/phase6_build.zig` defines the dedicated `phase6-base64-perf` build step again",
    "* base64 exact thresholds: `zigux/tests/fixtures/phase6_base64_vectors.zig` still pins four perf cases (`STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, and `URLSAFE_NO_PAD`) at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`",
]


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


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected marker in {path}: {snippet}")


def array_body(text: str, array_name: str) -> str:
    pattern = re.compile(
        rf"pub const {re.escape(array_name)} = \[_\][^{{]*\{{(?P<body>.*?)\n\}};",
        re.S,
    )
    match = pattern.search(text)
    if match is None:
        raise ValidationError(f"could not find array {array_name} in {VECTORS_PATH}")
    return match.group("body")


def count_array_entries(text: str, array_name: str) -> int:
    body = array_body(text, array_name)
    return len(re.findall(r"^\s*\.\{", body, re.M))


def validate_vectors(repo_root: Path) -> None:
    vectors_text = read_text(repo_root / VECTORS_PATH)

    for array_name, expected_count in EXPECTED_ARRAY_COUNTS.items():
        actual_count = count_array_entries(vectors_text, array_name)
        if actual_count != expected_count:
            raise ValidationError(
                f"unexpected {array_name} count in {VECTORS_PATH}: expected {expected_count}, got {actual_count}"
            )

    if "pub const perf_payload =" not in vectors_text:
        raise ValidationError(f"missing perf payload in {VECTORS_PATH}")

    for label in EXPECTED_PERF_LABELS:
        if f'.label = "{label}"' not in array_body(vectors_text, "perf_cases"):
            raise ValidationError(f"missing base64 perf label {label} in {VECTORS_PATH}")



def validate_perf(repo_root: Path) -> None:
    perf_text = read_text(repo_root / PERF_PATH)
    for snippet in REQUIRED_PERF_SNIPPETS:
        if snippet not in perf_text:
            raise ValidationError(f"missing expected marker in {PERF_PATH}: {snippet}")

    for label in EXPECTED_PERF_LABELS:
        if f'.label = "{label}"' not in perf_text:
            raise ValidationError(f"missing expected perf case label {label} in {PERF_PATH}")



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

    for key, expected_value in EXPECTED_MANIFEST_BASE64.items():
        if base64.get(key) != expected_value:
            raise ValidationError(
                f"unexpected base64 determinism_evidence.{key} in {MANIFEST_PATH}: "
                f"expected {expected_value!r}, got {base64.get(key)!r}"
            )

    if determinism.get("generated_fixture_artifacts_committed") is not False:
        raise ValidationError(
            f"unexpected determinism_evidence.generated_fixture_artifacts_committed in {MANIFEST_PATH}"
        )

    tests_root_present = manifest.get("tests_root_present_entrypoints")
    if not isinstance(tests_root_present, list):
        raise ValidationError(f"missing tests_root_present_entrypoints in {MANIFEST_PATH}")
    if PERF_PATH.as_posix() not in tests_root_present:
        raise ValidationError(f"missing {PERF_PATH} from tests_root_present_entrypoints in {MANIFEST_PATH}")

    public_tree_gaps = manifest.get("tests_root_public_tree_gaps")
    if not isinstance(public_tree_gaps, list):
        raise ValidationError(f"missing tests_root_public_tree_gaps in {MANIFEST_PATH}")
    if PERF_PATH.as_posix() in public_tree_gaps:
        raise ValidationError(f"{PERF_PATH} should not be listed in tests_root_public_tree_gaps")



def validate_docs(repo_root: Path) -> None:
    require_snippets(repo_root / SLICE_PATH, REQUIRED_SLICE_SNIPPETS)
    require_snippets(repo_root / PERF_SURVEY_PATH, REQUIRED_PERF_SURVEY_SNIPPETS)



def validate_absence(repo_root: Path) -> None:
    if (repo_root / GENERATED_INCLUDE_PATH).exists():
        raise ValidationError(
            f"generated include should stay absent from the committed tree: {GENERATED_INCLUDE_PATH}"
        )



def run_checks(repo_root: Path) -> None:
    validate_vectors(repo_root)
    validate_perf(repo_root)
    validate_manifest(repo_root)
    validate_docs(repo_root)
    validate_absence(repo_root)



def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def scaffold_repo(root: Path) -> None:
    write(
        root / VECTORS_PATH,
        """pub const standard_cases = [_]u8{
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
pub const variant_cases = [_]u8{
    .{},
    .{},
    .{},
    .{},
};
pub const standard_decode_cases = [_]u8{
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
pub const variant_decode_cases = [_]u8{
    .{},
    .{},
    .{},
    .{},
};
pub const invalid_decode_cases = [_]u8{
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
    .{},
    .{},
};
pub const perf_payload = "payload";
pub const perf_cases = [_]struct{
    label: []const u8,
}{
    .{ .label = "STD_PAD" },
    .{ .label = "STD_NO_PAD" },
    .{ .label = "URLSAFE_PAD" },
    .{ .label = "URLSAFE_NO_PAD" },
};
""",
    )
    write(
        root / PERF_PATH,
        """const fixtures = @import("fixtures/phase6_base64_vectors.zig");
const PerfCase = fixtures.PerfCase;
test "phase 6 base64 perf matrix keeps all shipped variant-and-padding replays" {
    try std.testing.expectEqual(expected_perf_cases.len, fixtures.perf_cases.len);
    _ = fixtures;
}
test "phase 6 base64 perf cases keep helper and reference codecs aligned before timing" {
    _ = fixtures;
}
const expected_perf_cases = [_]PerfCase{
    .{ .label = "STD_PAD" },
    .{ .label = "STD_NO_PAD" },
    .{ .label = "URLSAFE_PAD" },
    .{ .label = "URLSAFE_NO_PAD" },
};
""",
    )
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "tests_root_present_entrypoints": [
                    "zigux/tests/phase6_base64_perf.zig",
                ],
                "tests_root_public_tree_gaps": [
                    "lib/checksum.zig",
                ],
                "determinism_evidence": {
                    "base64": dict(EXPECTED_MANIFEST_BASE64),
                    "generated_fixture_artifacts_committed": False,
                },
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / SLICE_PATH,
        "\n".join(REQUIRED_SLICE_SNIPPETS) + "\n",
    )
    write(
        root / PERF_SURVEY_PATH,
        "\n".join(REQUIRED_PERF_SURVEY_SNIPPETS) + "\n",
    )



def assert_failure(root: Path, path: Path, old: str, new: str) -> None:
    original = path.read_text(encoding="utf-8")
    if old not in original:
        raise AssertionError(f"self-test marker not found in {path}: {old}")
    rel_path = path.relative_to(root).as_posix()
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        run_checks(root)
    except ValidationError as exc:
        if rel_path not in str(exc):
            raise AssertionError(f"unexpected failure for {path}: {exc}") from exc
    else:
        raise AssertionError(f"expected failure for {path}")
    path.write_text(original, encoding="utf-8")



def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        run_checks(root)
        assert_failure(root, root / VECTORS_PATH, '.{ .label = "URLSAFE_NO_PAD" }', '.{ .label = "IMAP_NO_PAD" }')
        assert_failure(root, root / PERF_PATH, 'try std.testing.expectEqual(expected_perf_cases.len, fixtures.perf_cases.len);', 'try std.testing.expectEqual(@as(usize, 3), fixtures.perf_cases.len);')
        assert_failure(root, root / MANIFEST_PATH, '"perf_replay_cases": 4', '"perf_replay_cases": 3')
        assert_failure(root, root / SLICE_PATH, "zigux/tests/phase6_base64_perf.zig", "zigux/tests/phase6_base64_perf_missing.zig")
        write(root / GENERATED_INCLUDE_PATH, "generated\n")
        try:
            run_checks(root)
        except ValidationError as exc:
            if GENERATED_INCLUDE_PATH.as_posix() not in str(exc):
                raise AssertionError(f"unexpected generated-include failure: {exc}") from exc
        else:
            raise AssertionError("expected generated-include failure")
    print("self-test passed")



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    run_checks(Path(args.repo_root).resolve())
    print("Phase 6 base64 corpus evidence looks aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
