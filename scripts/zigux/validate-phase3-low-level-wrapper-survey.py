#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile


_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) > 2 else _HERE.parent
SURVEY_REL = "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"
DOCS_README_REL = "Documentation/zigux/README.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
MAKEFILE_REL = "zigux/Makefile"
ABI_SLICE_REL = "Documentation/zigux/phase3-abi-slice.md"
MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
ATOMIC_REL = "zigux/helpers/atomic.zig"
BARRIER_REL = "zigux/helpers/barrier.zig"
MMIO_REL = "zigux/helpers/mmio.zig"
LOW_LEVEL_BUILD_REL = "zigux/tests/phase3_low_level_wrappers_build.zig"
LOW_LEVEL_TEST_REL = "zigux/tests/phase3_low_level_wrappers.zig"
POLICY_UNSAFE_MMIO_CONSUMER_REL = "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"
POLICY_UNSAFE_TEST_REL = "zigux/tests/phase3_policy_unsafe.zig"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
PLACEHOLDER_SHA = "0123456789abcdef0123456789abcdef01234567"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run",
    "PHASE3_ATOMIC_PATH=zigux/helpers/atomic.zig",
    "PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-compare-exchange-weak-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max",
    "PHASE3_ATOMIC_STATUS=bounded-helper-surface-and-mismatch-replay-landed",
    "PHASE3_BARRIER_PATH=zigux/helpers/barrier.zig",
    "PHASE3_BARRIER_SCOPE=acquire-release-acquire-release-combined-full",
    "PHASE3_BARRIER_STATUS=throwaway-probe-barriers-landed",
    "PHASE3_MMIO_PATH=zigux/helpers/mmio.zig",
    "PHASE3_MMIO_SCOPE=range-read8-read16-read32-read64-write8-write16-write32-write64-plus-scoped-read8-write8-read16-write16-read32-write32-read64-write64-plus-policy-read8-write8-read16-write16-read32-write32-read64-write64-and-generic-policy-bridges",
    "PHASE3_MMIO_STATUS=scoped-width-specific-mmio-and-policy-bridge-landed",
    "PHASE3_LOW_LEVEL_BUILD_PATH=zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_LOW_LEVEL_TEST_PATH=zigux/tests/phase3_low_level_wrappers.zig",
    "PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_BOUNDARY_GAP=no-relaxed-order-barrier-variants-or-broader-kernel-style-atomic-family-is-shipped-yet",
    "PHASE3_NEXT_BOUNDED_STEP=keep-the-low-level-wrapper-packet-narrow-until-one-roadmap-backed-boundary-slice-needs-another-explicit-atomic-or-mmio-helper",
)

REQUIRED_SURVEY_SNIPPETS = (
    "approved atomic, barrier, and MMIO wrappers",
    "`zigux/helpers/atomic.zig` currently limits the approved helper surface to `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchMin`, `fetchMax`, `compareExchange`, and `compareExchangeWeak`",
    "`zigux/helpers/barrier.zig` currently limits the approved barrier surface to `acquire`, `release`, `acquireRelease`, and `full`",
    "`zigux/helpers/mmio.zig` currently limits the approved MMIO surface to `range`, `read8`, `read16`, `read32`, `read64`, `write8`, `write16`, `write32`, and `write64`, plus the scoped `read8`, `write8`, `read16`, `write16`, `read32`, `write32`, `read64`, and `write64` entry points, the width-specific `read8Policy`, `write8Policy`, `read16Policy`, `write16Policy`, `read32Policy`, `write32Policy`, `read64Policy`, and `write64Policy` entry points, and the generic `readScopedWithPolicy` plus `writeScopedWithPolicy` bridges",
    "`zigux/tests/phase3_low_level_wrappers_build.zig` and `zigux/tests/phase3_low_level_wrappers.zig` keep the atomic, barrier, direct-plus-scoped MMIO, width-specific policy-aware MMIO, and generic decoded-policy MMIO bridge packet reviewable on one focused compile-and-test path, and the focused build now also wires the current `interop_policy` dependency that `zigux/helpers/mmio.zig` imports.",
    "`zigux/tests/phase3_policy_unsafe.zig` and `scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py` keep the broader whole-record interop-policy decode and second-boundary-helper MMIO story reviewable beside that focused low-level gate",
    "no relaxed-order barrier variants are shipped in the current packet",
    "no broader kernel-style atomic helper family is shipped in the current packet",
    "no MMIO family wider than the direct, scoped, and decoded-policy 8-bit, 16-bit, 32-bit, and 64-bit accessors is shipped in the current packet",
    "This is real roadmap-backed progress.",
    "`zigux/tests/phase3_low_level_wrappers.zig` now keeps the strong and weak compare-exchange replay, `fetchMin()` and `fetchMax()` replay, the acquire-only, release-only, combined acquire-plus-release, and full barrier probes, denied-scope checks, width-specific direct, scoped, and policy-aware 8-bit, 16-bit, 32-bit, and 64-bit MMIO coverage, generic decoded-policy bridge coverage across the same widths, denied-scope policy failures, misalignment failures, overflow failures, and the shared `MmioRange` layout assertion reviewable without having to infer them from the broader `phase3_abi` bundle alone.",
)

REQUIRED_SURVEY_PATHS = (
    DOCS_README_REL,
    SCRIPTS_README_REL,
    MAKEFILE_REL,
    ATOMIC_REL,
    BARRIER_REL,
    MMIO_REL,
    LOW_LEVEL_BUILD_REL,
    LOW_LEVEL_TEST_REL,
    POLICY_UNSAFE_MMIO_CONSUMER_REL,
    POLICY_UNSAFE_TEST_REL,
    MANIFEST_REL,
    ABI_SLICE_REL,
)

REQUIRED_DOCS_README_SNIPPETS = (
    "`Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`",
    "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
    "`make -C zigux phase3-validate`",
)

REQUIRED_SCRIPTS_README_SNIPPETS = (
    "`validate-phase3-low-level-wrapper-survey.py`",
    "focused low-level wrapper gate",
)

REQUIRED_MAKEFILE_SNIPPETS = (
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "$(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
)

REQUIRED_ATOMIC_SNIPPETS = (
    "pub fn load(comptime T: type, ptr: *const T, comptime order: std.builtin.AtomicOrder) T {",
    "pub fn fetchAdd(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
    "pub fn fetchSub(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
    "pub fn fetchAnd(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
    "pub fn fetchOr(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
    "pub fn fetchXor(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
    "pub fn fetchMin(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
    "pub fn fetchMax(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {",
    "pub fn compareExchange(",
    "pub fn compareExchangeWeak(",
)

REQUIRED_BARRIER_SNIPPETS = (
    "pub fn acquire() void {",
    "pub fn release() void {",
    "pub fn acquireRelease() void {",
    "pub fn full() void {",
)

REQUIRED_MMIO_SNIPPETS = (
    "fn scopeFromPolicy(policy: interop_policy.DecodedInteropPolicy) narrow.ScopeError!narrow.UnsafeScopeTag {",
    "pub fn readScopedWithPolicy(",
    "pub fn writeScopedWithPolicy(",
    "pub fn read8Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u8 {",
    "pub fn write8Policy(",
    "pub fn read16Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u16 {",
    "pub fn write16Policy(",
    "pub fn read32Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u32 {",
    "pub fn write32Policy(",
    "pub fn read64Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u64 {",
    "pub fn write64Policy(",
    'test "phase3 mmio wrapper consumes decoded interop policy"',
)

REQUIRED_LOW_LEVEL_BUILD_SNIPPETS = (
    "const interop_policy_module = b.createModule(.{",
    'interop_policy_module.addImport("abi_bindings", abi_bindings_module);',
    'interop_policy_module.addImport("panic_policy", panic_policy_module);',
    'interop_policy_module.addImport("allocator_policy", allocator_policy_module);',
    'interop_policy_module.addImport("narrow_unsafe", narrow_unsafe_module);',
    'mmio_helpers_module.addImport("interop_policy", interop_policy_module);',
)

REQUIRED_LOW_LEVEL_TEST_SNIPPETS = (
    'test "phase3 low-level wrappers stay inside the documented ABI surface"',
    "atomic.fetchAdd(u32, &value, 2, .seq_cst)",
    "atomic.fetchMax(u32, &value, 29, .seq_cst)",
    "atomic.fetchMin(u32, &value, 17, .seq_cst)",
    "const mismatch = atomic.compareExchange(u32, &value, 9, 19, .seq_cst, .seq_cst);",
    "atomic.compareExchangeWeak(u32, &weak_value, 31, 34, .seq_cst, .seq_cst)",
    "barrier.acquireRelease();",
    "barrier.full();",
    "mmio.write8(base, 1, 0x5a);",
    "mmio.write16(base, 2, 0xabcd);",
    "mmio.write32(base, 8, 0x12345678);",
    "mmio.write64(base64, @sizeOf(u64), 0x0123_4567_89ab_cdef);",
    "try mmio.write8Policy(mmio_policy, base, 0, 0x2a);",
    "try std.testing.expectEqual(@as(u8, 0x2a), try mmio.read8Policy(mmio_policy, base, 0));",
    "try mmio.write16Policy(mmio_policy, base, 2, 0x7bcd);",
    "try std.testing.expectEqual(@as(u16, 0x7bcd), try mmio.read16Policy(mmio_policy, base, 2));",
    "try mmio.write32Policy(mmio_policy, base, 8, 0xdecafbad);",
    "try std.testing.expectEqual(@as(u32, 0xdecafbad), regs[2]);",
    "try std.testing.expectEqual(@as(u32, 0xdecafbad), try mmio.read32Policy(mmio_policy, base, 8));",
    "try mmio.write64Policy(mmio_policy, base64, @sizeOf(u64), 0x1111_2222_3333_4444);",
    "try std.testing.expectEqual(@as(u64, 0x1111_2222_3333_4444), try mmio.read64Policy(mmio_policy, base64, @sizeOf(u64)));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8Policy(raw_pointer_policy, base, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8Policy(raw_pointer_policy, base, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8Policy(none_policy, base, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read8Policy(none_policy, base, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Policy(raw_pointer_policy, base, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read16Policy(raw_pointer_policy, base, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write16Policy(none_policy, base, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read16Policy(none_policy, base, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(raw_pointer_policy, base, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(raw_pointer_policy, base, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(none_policy, base, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(none_policy, base, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Policy(raw_pointer_policy, base64, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read64Policy(raw_pointer_policy, base64, 0));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write64Policy(none_policy, base64, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read64Policy(none_policy, base64, 0));",
    'test "phase3 low-level wrappers keep the narrow unsafe scope contract explicit"',
)

REQUIRED_POLICY_UNSAFE_MMIO_CONSUMER_SNIPPETS = (
    "PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig",
    "PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay",
    "PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer",
    'test "phase3 mmio wrapper consumes decoded interop policy"',
)

REQUIRED_POLICY_UNSAFE_TEST_SNIPPETS = (
    'test "phase3 policy gate reaches a second boundary helper through decoded policy"',
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(raw_pointer_policy, base32, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(raw_pointer_policy, base32, 0));",
)

REQUIRED_ABI_SLICE_SNIPPETS = (
    "PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-compare-exchange-weak-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max",
    "PHASE3_BARRIER_SCOPE=acquire-release-acquire-release-combined-full",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "atomic reality today: `zigux/helpers/atomic.zig` currently limits the approved wrapper set to `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchMin`, `fetchMax`, `compareExchange`, and `compareExchangeWeak`",
    "barrier reality today: `zigux/helpers/barrier.zig` currently limits the approved barrier surface to `acquire`, `release`, `acquireRelease`, and `full`",
    "PHASE3_MMIO_SCOPE=range-read8-read16-read32-read64-write8-write16-write32-write64-plus-scoped-read8-write8-read16-write16-read32-write32-read64-write64-plus-policy-read8-write8-read16-write16-read32-write32-read64-write64-and-generic-policy-bridges",
    "`zigux/tests/phase3_policy_unsafe.zig` and `scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py` keep the decoded-policy MMIO bridge reviewable beside the focused low-level gate",
    "broader kernel-style atomic or barrier families plus MMIO expansion beyond the current direct, scoped, and decoded-policy 8-bit, 16-bit, 32-bit, and 64-bit helpers still stay deferred until a roadmap-backed boundary slice really needs them",
)

SURVEYED_PACKET_BLOB_MARKERS = {
    "PHASE3_ATOMIC_BLOB_SHA": ATOMIC_REL,
    "PHASE3_BARRIER_BLOB_SHA": BARRIER_REL,
    "PHASE3_MMIO_BLOB_SHA": MMIO_REL,
    "PHASE3_LOW_LEVEL_BUILD_BLOB_SHA": LOW_LEVEL_BUILD_REL,
    "PHASE3_LOW_LEVEL_TEST_BLOB_SHA": LOW_LEVEL_TEST_REL,
    "PHASE3_ABI_SLICE_DOC_BLOB_SHA": ABI_SLICE_REL,
    "PHASE3_ABI_MANIFEST_BLOB_SHA": MANIFEST_REL,
}


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _check_snippets(text: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"{prefix}:{snippet}")


def _marker_value_from_text(text: str, marker: str) -> str | None:
    prefix = f"{marker}="
    for line in text.splitlines():
        stripped = line.strip().strip("- ").strip("`")
        if stripped.startswith(prefix):
            return stripped[len(prefix) :]
    return None


def _packet_drift_by_blob_sha(root: Path, survey: str) -> list[str]:
    if not (root / ".git").exists():
        return []

    issues: list[str] = []
    for marker, rel in SURVEYED_PACKET_BLOB_MARKERS.items():
        expected_blob = _marker_value_from_text(survey, marker)
        if expected_blob is None or not HEX40.fullmatch(expected_blob):
            continue

        path = root / rel
        if not path.exists():
            issues.append(f"current_blob_unavailable:{rel}")
            continue

        result = subprocess.run(
            ["git", "hash-object", "--no-filters", str(path)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            issues.append(f"current_blob_unavailable:{rel}")
            continue

        current_blob = result.stdout.strip()
        if not HEX40.fullmatch(current_blob):
            issues.append(f"invalid_current_blob_sha:{rel}:{current_blob}")
        elif current_blob != expected_blob:
            issues.append(f"surveyed_blob_drift:{rel}")

    return issues


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = _read_text(root, SURVEY_REL, issues)
    docs_readme = _read_text(root, DOCS_README_REL, issues)
    scripts_readme = _read_text(root, SCRIPTS_README_REL, issues)
    makefile = _read_text(root, MAKEFILE_REL, issues)
    atomic = _read_text(root, ATOMIC_REL, issues)
    barrier = _read_text(root, BARRIER_REL, issues)
    mmio = _read_text(root, MMIO_REL, issues)
    low_level_build = _read_text(root, LOW_LEVEL_BUILD_REL, issues)
    low_level_test = _read_text(root, LOW_LEVEL_TEST_REL, issues)
    policy_unsafe_mmio_consumer = _read_text(root, POLICY_UNSAFE_MMIO_CONSUMER_REL, issues)
    policy_unsafe_test = _read_text(root, POLICY_UNSAFE_TEST_REL, issues)
    abi_slice = _read_text(root, ABI_SLICE_REL, issues)

    if survey:
        _check_snippets(survey, REQUIRED_SURVEY_MARKERS, "missing_survey_marker", issues)
        for marker in SURVEYED_PACKET_BLOB_MARKERS:
            value = _marker_value_from_text(survey, marker)
            if value is None:
                issues.append(f"missing_survey_marker:{marker}=")
            elif not HEX40.fullmatch(value):
                issues.append(f"invalid_survey_blob_sha:{marker}:{value}")
        issues.extend(_packet_drift_by_blob_sha(root, survey))
        _check_snippets(survey, REQUIRED_SURVEY_SNIPPETS, "missing_survey_snippet", issues)

    for rel in REQUIRED_SURVEY_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_repo_path:{rel}")

    if docs_readme:
        _check_snippets(docs_readme, REQUIRED_DOCS_README_SNIPPETS, "missing_docs_readme_snippet", issues)
    if scripts_readme:
        _check_snippets(scripts_readme, REQUIRED_SCRIPTS_README_SNIPPETS, "missing_scripts_readme_snippet", issues)
    if makefile:
        _check_snippets(makefile, REQUIRED_MAKEFILE_SNIPPETS, "missing_makefile_snippet", issues)
    if atomic:
        _check_snippets(atomic, REQUIRED_ATOMIC_SNIPPETS, "missing_atomic_snippet", issues)
    if barrier:
        _check_snippets(barrier, REQUIRED_BARRIER_SNIPPETS, "missing_barrier_snippet", issues)
    if mmio:
        _check_snippets(mmio, REQUIRED_MMIO_SNIPPETS, "missing_mmio_snippet", issues)
    if low_level_build:
        _check_snippets(low_level_build, REQUIRED_LOW_LEVEL_BUILD_SNIPPETS, "missing_low_level_build_snippet", issues)
    if low_level_test:
        _check_snippets(low_level_test, REQUIRED_LOW_LEVEL_TEST_SNIPPETS, "missing_low_level_test_snippet", issues)
    if policy_unsafe_mmio_consumer:
        _check_snippets(
            policy_unsafe_mmio_consumer,
            REQUIRED_POLICY_UNSAFE_MMIO_CONSUMER_SNIPPETS,
            "missing_policy_unsafe_mmio_consumer_snippet",
            issues,
        )
    if policy_unsafe_test:
        _check_snippets(
            policy_unsafe_test,
            REQUIRED_POLICY_UNSAFE_TEST_SNIPPETS,
            "missing_policy_unsafe_test_snippet",
            issues,
        )
    if abi_slice:
        _check_snippets(abi_slice, REQUIRED_ABI_SLICE_SNIPPETS, "missing_abi_slice_snippet", issues)
    return issues


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _blob_marker_lines() -> list[str]:
    return [f"- `{marker}={PLACEHOLDER_SHA}`" for marker in SURVEYED_PACKET_BLOB_MARKERS]


def _replace_blob_markers_with_head(root: Path, survey_path: Path) -> None:
    survey_text = survey_path.read_text(encoding="utf-8")
    for marker, rel in SURVEYED_PACKET_BLOB_MARKERS.items():
        blob_sha = subprocess.run(
            ["git", "hash-object", "--no-filters", str(root / rel)],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        survey_text = survey_text.replace(f"{marker}={PLACEHOLDER_SHA}", f"{marker}={blob_sha}")
    survey_path.write_text(survey_text, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_wrapper_survey_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        _write(
            root,
            SURVEY_REL,
            "\n".join([
                "# Phase 3 Low-Level Wrapper Boundary Survey",
                "",
                *[f"- `{marker}`" for marker in REQUIRED_SURVEY_MARKERS],
                "",
                *REQUIRED_SURVEY_SNIPPETS,
                "",
                *_blob_marker_lines(),
            ]) + "\n",
        )
        _write(root, DOCS_README_REL, "\n".join(REQUIRED_DOCS_README_SNIPPETS) + "\n")
        _write(root, SCRIPTS_README_REL, "\n".join(REQUIRED_SCRIPTS_README_SNIPPETS) + "\n")
        _write(root, MAKEFILE_REL, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
        _write(root, ATOMIC_REL, "\n".join(REQUIRED_ATOMIC_SNIPPETS) + "\n")
        _write(root, BARRIER_REL, "\n".join(REQUIRED_BARRIER_SNIPPETS) + "\n")
        _write(root, MMIO_REL, "\n".join(REQUIRED_MMIO_SNIPPETS) + "\n")
        _write(root, LOW_LEVEL_BUILD_REL, "\n".join(REQUIRED_LOW_LEVEL_BUILD_SNIPPETS) + "\n")
        _write(root, LOW_LEVEL_TEST_REL, "\n".join(REQUIRED_LOW_LEVEL_TEST_SNIPPETS) + "\n")
        _write(
            root,
            POLICY_UNSAFE_MMIO_CONSUMER_REL,
            "\n".join(REQUIRED_POLICY_UNSAFE_MMIO_CONSUMER_SNIPPETS) + "\n",
        )
        _write(root, POLICY_UNSAFE_TEST_REL, "\n".join(REQUIRED_POLICY_UNSAFE_TEST_SNIPPETS) + "\n")
        _write(root, ABI_SLICE_REL, "\n".join(REQUIRED_ABI_SLICE_SNIPPETS) + "\n")
        _write(root, MANIFEST_REL, "{}\n")

        assert validate(root) == []

        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True, text=True)
        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Codex",
            "GIT_AUTHOR_EMAIL": "codex@example.com",
            "GIT_COMMITTER_NAME": "Codex",
            "GIT_COMMITTER_EMAIL": "codex@example.com",
        }
        subprocess.run(["git", "commit", "-m", "self-test snapshot"], cwd=root, check=True, capture_output=True, text=True, env=env)
        survey_path = root / SURVEY_REL
        _replace_blob_markers_with_head(root, survey_path)
        assert validate(root) == []

        survey_text = survey_path.read_text(encoding="utf-8")
        current = _marker_value_from_text(survey_text, "PHASE3_MMIO_BLOB_SHA")
        assert current is not None
        survey_path.write_text(survey_text.replace(current, "not-a-sha", 1), encoding="utf-8", newline="\n")
        issues = validate(root)
        assert "invalid_survey_blob_sha:PHASE3_MMIO_BLOB_SHA:not-a-sha" in issues

        _write(
            root,
            SURVEY_REL,
            "\n".join([
                "# Phase 3 Low-Level Wrapper Boundary Survey",
                "",
                *[f"- `{marker}`" for marker in REQUIRED_SURVEY_MARKERS],
                "",
                *REQUIRED_SURVEY_SNIPPETS,
                "",
                *[
                    line for line in _blob_marker_lines()
                    if line != f"- `PHASE3_MMIO_BLOB_SHA={PLACEHOLDER_SHA}`"
                ],
            ]) + "\n",
        )
        issues = validate(root)
        assert "missing_survey_marker:PHASE3_MMIO_BLOB_SHA=" in issues

        _write(root, SURVEY_REL, "\n".join([
            "# Phase 3 Low-Level Wrapper Boundary Survey",
            "",
            *[f"- `{marker}`" for marker in REQUIRED_SURVEY_MARKERS],
            "",
            *REQUIRED_SURVEY_SNIPPETS,
            "",
            *_blob_marker_lines(),
        ]) + "\n")
        _replace_blob_markers_with_head(root, survey_path)
        _write(root, MMIO_REL, (root / MMIO_REL).read_text(encoding="utf-8") + "// drift\n")
        issues = validate(root)
        assert f"surveyed_blob_drift:{MMIO_REL}" in issues

        _write(root, MMIO_REL, "\n".join(REQUIRED_MMIO_SNIPPETS) + "\n")
        _write(
            root,
            MAKEFILE_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_MAKEFILE_SNIPPETS
                if snippet != "scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"
            ) + "\n",
        )
        issues = validate(root)
        assert (
            "missing_makefile_snippet:scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"
            in issues
        )

        _write(root, MAKEFILE_REL, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
        _write(
            root,
            ATOMIC_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_ATOMIC_SNIPPETS
                if snippet
                != "pub fn fetchMin(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {"
            ) + "\n",
        )
        issues = validate(root)
        assert (
            "missing_atomic_snippet:pub fn fetchMin(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {"
            in issues
        )

        _write(root, ATOMIC_REL, "\n".join(REQUIRED_ATOMIC_SNIPPETS) + "\n")
        _write(
            root,
            LOW_LEVEL_TEST_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_LOW_LEVEL_TEST_SNIPPETS
                if snippet != "atomic.fetchMax(u32, &value, 29, .seq_cst)"
            ) + "\n",
        )
        issues = validate(root)
        assert "missing_low_level_test_snippet:atomic.fetchMax(u32, &value, 29, .seq_cst)" in issues

        _write(
            root,
            SURVEY_REL,
            "\n".join([
                "# Phase 3 Low-Level Wrapper Boundary Survey",
                "",
                *[f"- `{marker}`" for marker in REQUIRED_SURVEY_MARKERS],
                "",
                *[
                    snippet
                    for snippet in REQUIRED_SURVEY_SNIPPETS
                    if snippet
                    != "`zigux/tests/phase3_low_level_wrappers_build.zig` and `zigux/tests/phase3_low_level_wrappers.zig` keep the atomic, barrier, direct-plus-scoped MMIO, width-specific policy-aware MMIO, and generic decoded-policy MMIO bridge packet reviewable on one focused compile-and-test path, and the focused build now also wires the current `interop_policy` dependency that `zigux/helpers/mmio.zig` imports."
                ],
                "",
                *_blob_marker_lines(),
            ]) + "\n",
        )
        issues = validate(root)
        assert (
            "missing_survey_snippet:`zigux/tests/phase3_low_level_wrappers_build.zig` and `zigux/tests/phase3_low_level_wrappers.zig` keep the atomic, barrier, direct-plus-scoped MMIO, width-specific policy-aware MMIO, and generic decoded-policy MMIO bridge packet reviewable on one focused compile-and-test path, and the focused build now also wires the current `interop_policy` dependency that `zigux/helpers/mmio.zig` imports."
            in issues
        )

        _write(root, LOW_LEVEL_TEST_REL, "\n".join(REQUIRED_LOW_LEVEL_TEST_SNIPPETS) + "\n")
        _write(
            root,
            BARRIER_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_BARRIER_SNIPPETS
                if snippet != "pub fn acquireRelease() void {"
            ) + "\n",
        )
        issues = validate(root)
        assert "missing_barrier_snippet:pub fn acquireRelease() void {" in issues

        _write(root, BARRIER_REL, "\n".join(REQUIRED_BARRIER_SNIPPETS) + "\n")
        _write(
            root,
            POLICY_UNSAFE_MMIO_CONSUMER_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_POLICY_UNSAFE_MMIO_CONSUMER_SNIPPETS
                if snippet != 'test "phase3 mmio wrapper consumes decoded interop policy"'
            ) + "\n",
        )
        issues = validate(root)
        assert (
            'missing_policy_unsafe_mmio_consumer_snippet:test "phase3 mmio wrapper consumes decoded interop policy"'
            in issues
        )

        _write(
            root,
            POLICY_UNSAFE_MMIO_CONSUMER_REL,
            "\n".join(REQUIRED_POLICY_UNSAFE_MMIO_CONSUMER_SNIPPETS) + "\n",
        )
        _write(
            root,
            POLICY_UNSAFE_TEST_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_POLICY_UNSAFE_TEST_SNIPPETS
                if snippet
                != "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(raw_pointer_policy, base32, 0));"
            ) + "\n",
        )
        issues = validate(root)
        assert (
            "missing_policy_unsafe_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(raw_pointer_policy, base32, 0));"
            in issues
        )

        _write(
            root,
            LOW_LEVEL_BUILD_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_LOW_LEVEL_BUILD_SNIPPETS
                if snippet != 'mmio_helpers_module.addImport("interop_policy", interop_policy_module);'
            ) + "\n",
        )
        issues = validate(root)
        assert (
            'missing_low_level_build_snippet:mmio_helpers_module.addImport("interop_policy", interop_policy_module);'
            in issues
        )
        _write(root, LOW_LEVEL_BUILD_REL, "\n".join(REQUIRED_LOW_LEVEL_BUILD_SNIPPETS) + "\n")

        _write(
            root,
            POLICY_UNSAFE_TEST_REL,
            "\n".join(REQUIRED_POLICY_UNSAFE_TEST_SNIPPETS) + "\n",
        )
        _write(
            root,
            ABI_SLICE_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_ABI_SLICE_SNIPPETS
                if snippet
                != "PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-compare-exchange-weak-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max"
            ) + "\n",
        )
        issues = validate(root)
        assert (
            "missing_abi_slice_snippet:PHASE3_ATOMIC_SCOPE=load-store-exchange-compare-exchange-compare-exchange-weak-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max"
            in issues
        )

        _write(
            root,
            ABI_SLICE_REL,
            "\n".join(REQUIRED_ABI_SLICE_SNIPPETS) + "\n",
        )
        _write(
            root,
            ABI_SLICE_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_ABI_SLICE_SNIPPETS
                if snippet != "PHASE3_BARRIER_SCOPE=acquire-release-acquire-release-combined-full"
            ) + "\n",
        )
        issues = validate(root)
        assert (
            "missing_abi_slice_snippet:PHASE3_BARRIER_SCOPE=acquire-release-acquire-release-combined-full"
            in issues
        )

        _write(
            root,
            ABI_SLICE_REL,
            "\n".join(REQUIRED_ABI_SLICE_SNIPPETS) + "\n",
        )
        _write(
            root,
            LOW_LEVEL_TEST_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_LOW_LEVEL_TEST_SNIPPETS
                if snippet != "try mmio.write16Policy(mmio_policy, base, 2, 0x7bcd);"
            ) + "\n",
        )
        issues = validate(root)
        assert "missing_low_level_test_snippet:try mmio.write16Policy(mmio_policy, base, 2, 0x7bcd);" in issues

        _write(
            root,
            LOW_LEVEL_TEST_REL,
            "\n".join(REQUIRED_LOW_LEVEL_TEST_SNIPPETS) + "\n",
        )
        _write(
            root,
            LOW_LEVEL_TEST_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_LOW_LEVEL_TEST_SNIPPETS
                if snippet != "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8Policy(raw_pointer_policy, base, 0, 1));"
            ) + "\n",
        )
        issues = validate(root)
        assert (
            "missing_low_level_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.write8Policy(raw_pointer_policy, base, 0, 1));"
            in issues
        )

        _write(
            root,
            LOW_LEVEL_TEST_REL,
            "\n".join(REQUIRED_LOW_LEVEL_TEST_SNIPPETS) + "\n",
        )
        _write(
            root,
            LOW_LEVEL_TEST_REL,
            "\n".join(
                snippet
                for snippet in REQUIRED_LOW_LEVEL_TEST_SNIPPETS
                if snippet != "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(none_policy, base, 0));"
            ) + "\n",
        )
        issues = validate(root)
        assert (
            "missing_low_level_test_snippet:try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(none_policy, base, 0));"
            in issues
        )

        _write(
            root,
            LOW_LEVEL_TEST_REL,
            "\n".join(REQUIRED_LOW_LEVEL_TEST_SNIPPETS) + "\n",
        )
        _write(
            root,
            SURVEY_REL,
            "\n".join([
                "# Phase 3 Low-Level Wrapper Boundary Survey",
                "",
                *[f"- `{marker}`" for marker in REQUIRED_SURVEY_MARKERS],
                "",
                *[
                    snippet
                    for snippet in REQUIRED_SURVEY_SNIPPETS
                    if snippet
                    != "`zigux/tests/phase3_low_level_wrappers.zig` now keeps the strong and weak compare-exchange replay, `fetchMin()` and `fetchMax()` replay, the acquire-only, release-only, combined acquire-plus-release, and full barrier probes, denied-scope checks, width-specific direct, scoped, and policy-aware 8-bit, 16-bit, 32-bit, and 64-bit MMIO coverage, generic decoded-policy bridge coverage across the same widths, denied-scope policy failures, misalignment failures, overflow failures, and the shared `MmioRange` layout assertion reviewable without having to infer them from the broader `phase3_abi` bundle alone."
                ],
                "",
                *_blob_marker_lines(),
            ]) + "\n",
        )
        issues = validate(root)
        assert (
            "missing_survey_snippet:`zigux/tests/phase3_low_level_wrappers.zig` now keeps the strong and weak compare-exchange replay, `fetchMin()` and `fetchMax()` replay, the acquire-only, release-only, combined acquire-plus-release, and full barrier probes, denied-scope checks, width-specific direct, scoped, and policy-aware 8-bit, 16-bit, 32-bit, and 64-bit MMIO coverage, generic decoded-policy bridge coverage across the same widths, denied-scope policy failures, misalignment failures, overflow failures, and the shared `MmioRange` layout assertion reviewable without having to infer them from the broader `phase3_abi` bundle alone."
            in issues
        )

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the dedicated Phase 3 low-level wrapper boundary survey.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator checks.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(Path(args.root).resolve() if args.root else ROOT)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
