#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


FILE_PATH = Path(__file__).resolve()
ROOT = FILE_PATH.parents[2] if len(FILE_PATH.parents) >= 3 else FILE_PATH.parent

DOC_REL = "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"
ATOMIC_REL = "zigux/helpers/atomic.zig"
BARRIER_REL = "zigux/helpers/barrier.zig"
MMIO_REL = "zigux/helpers/mmio.zig"
NARROW_REL = "zigux/unsafe/narrow.zig"
LOW_LEVEL_TEST_REL = "zigux/tests/phase3_low_level_wrappers.zig"
ABI_TEST_REL = "zigux/tests/phase3_abi.zig"
ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
ABI_EXPECTED_REL = "zigux/tests/fixtures/phase3_abi/expected.json"
ABI_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
ABI_HARNESS_REL = "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"
ABI_SLICE_DOC_REL = "Documentation/zigux/phase3-abi-slice.md"
VALIDATOR_REL = "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"

ABI_MANIFEST_PHASE = "Phase 3"
ABI_MANIFEST_STATUS = "active"
ABI_MANIFEST_SLICE = "abi-substrate-skeleton"
SELF_TEST_CASE_COUNT = 17
MMIO_POINTER_AT_CALL_COUNT = 8
MMIO_FORBIDDEN_RAW_POINTER_TOKENS = (
    "@ptrFromInt",
)
DOC_MMIO_SCOPE = "range-range-interop-policy-byte-read8-write8-read16-write16-read32-write32-read64-write64"
DOC_LOW_LEVEL_TEST_SCOPE = "focused-atomic-barrier-mmio-replay-plus-signed-atomic-edges-acq-rel-strong-compare-exchange-mismatch-barrier-locality-barrier-acquire-release-handoff-non-seq-cst-ordering-byte-scoped-mmio-range-raw-pointer-bridge-policy-gates-and-byte-16-bit-32-bit-and-64-bit-mmio-range-replay"
DOC_BOUNDARY_GAP = "focused-low-level-replay-now-covers-signed-fetch-and-min-max-edges-plus-monotonic-and-acq-rel-strong-compare-exchange-mismatch-non-seq-cst-ordering-byte-scoped-mmio-range-raw-pointer-bridge-policy-gates-byte-16-bit-32-bit-and-64-bit-mmio-range-direct-barrier-locality-and-barrier-acquire-release-handoff-while-shared-abi-packet-still-carries-the-broader-compile-layout-and-dump-proof"

ABI_MANIFEST_REQUIRED_FILES = (
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "include/linux/zigux.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    ATOMIC_REL,
    BARRIER_REL,
    MMIO_REL,
    "zigux/kernel/export_shim.zig",
    NARROW_REL,
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    ABI_TEST_REL,
    ABI_DUMP_REL,
    "zigux/tests/phase3_export_uapi.zig",
    "zigux/tests/phase3_export_uapi_build.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    LOW_LEVEL_TEST_REL,
    "zigux/tests/build.zig",
    ABI_EXPECTED_REL,
    ABI_HARNESS_REL,
    "scripts/zigux/run-phase3-checks.py",
    "scripts/zigux/phase3_check_lib.py",
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/validate-phase3.py",
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    "scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    VALIDATOR_REL,
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "scripts/zigux/generate-phase3-check-wrappers.py",
    "Documentation/zigux/README.md",
    ABI_SLICE_DOC_REL,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    DOC_REL,
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "scripts/zigux/README.md",
    ".github/workflows/zigux-bootstrap.yml",
)

LOW_LEVEL_WRAPPER_FOCUSED_MANIFEST_FILES = (
    DOC_REL,
    ATOMIC_REL,
    BARRIER_REL,
    MMIO_REL,
    NARROW_REL,
    LOW_LEVEL_TEST_REL,
    ABI_TEST_REL,
    ABI_DUMP_REL,
    ABI_EXPECTED_REL,
    ABI_HARNESS_REL,
    ABI_SLICE_DOC_REL,
    VALIDATOR_REL,
)

REQUIRED_DOC_MARKERS = (
    f"PHASE3_ATOMIC_PATH={ATOMIC_REL}",
    f"PHASE3_BARRIER_PATH={BARRIER_REL}",
    f"PHASE3_MMIO_PATH={MMIO_REL}",
    f"PHASE3_NARROW_UNSAFE_PATH={NARROW_REL}",
    f"PHASE3_LOW_LEVEL_TEST_PATH={LOW_LEVEL_TEST_REL}",
    f"PHASE3_ABI_TEST_PATH={ABI_TEST_REL}",
    f"PHASE3_ABI_DUMP_PATH={ABI_DUMP_REL}",
    "PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run",
    "PHASE3_ATOMIC_SCOPE=load-store-exchange-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-nand-fetch-min-fetch-max-compare-exchange-compare-exchange-weak",
    "PHASE3_ATOMIC_STATUS=bounded-helper-surface-landed",
    "PHASE3_BARRIER_SCOPE=acquire-release-full-acquire-release-pair",
    "PHASE3_BARRIER_STATUS=local-caller-state-and-handoff-probes-landed",
    f"PHASE3_MMIO_SCOPE={DOC_MMIO_SCOPE}",
    "PHASE3_MMIO_STATUS=byte-16-bit-32-bit-and-64-bit-mmio-through-narrow-pointer-bridge",
    "PHASE3_NARROW_UNSAFE_SCOPE=address-byte-offset-align1-pointer-slice-const-pointer-write-and-interop-policy-unsafe-scope-byte-decoders",
    "PHASE3_NARROW_UNSAFE_STATUS=align1-raw-pointer-bridge-plus-explicit-unsafe-scope-byte-policy",
    f"PHASE3_LOW_LEVEL_TEST_SCOPE={DOC_LOW_LEVEL_TEST_SCOPE}",
    "PHASE3_LOW_LEVEL_TEST_STATUS=dedicated-focused-replay-widened-for-current-helper-surface-and-barrier-handoff",
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "PHASE3_BOUNDARY_SCOPE=focused-low-level-replay-plus-shared-abi-compile-layout-dump-packet",
    f"PHASE3_BOUNDARY_GAP={DOC_BOUNDARY_GAP}",
    "PHASE3_NEXT_BOUNDED_STEP=keep-this-survey-the-focused-replay-and-the-shared-abi-packet-aligned-when-helper-surface-moves",
)

BLOB_MARKERS = (
    ("PHASE3_ATOMIC_BLOB_SHA", ATOMIC_REL),
    ("PHASE3_BARRIER_BLOB_SHA", BARRIER_REL),
    ("PHASE3_MMIO_BLOB_SHA", MMIO_REL),
    ("PHASE3_NARROW_UNSAFE_BLOB_SHA", NARROW_REL),
    ("PHASE3_LOW_LEVEL_TEST_BLOB_SHA", LOW_LEVEL_TEST_REL),
    ("PHASE3_ABI_TEST_BLOB_SHA", ABI_TEST_REL),
    ("PHASE3_ABI_DUMP_BLOB_SHA", ABI_DUMP_REL),
    ("PHASE3_ABI_EXPECTED_BLOB_SHA", ABI_EXPECTED_REL),
    ("PHASE3_ABI_MANIFEST_BLOB_SHA", ABI_MANIFEST_REL),
    ("PHASE3_ABI_SLICE_DOC_BLOB_SHA", ABI_SLICE_DOC_REL),
)

TOKEN_CHECKS = {
    ATOMIC_REL: (
        "pub fn load",
        "pub fn store",
        "pub fn exchange",
        "pub fn fetchAdd",
        "pub fn fetchSub",
        "pub fn fetchAnd",
        "pub fn fetchOr",
        "pub fn fetchXor",
        "pub fn fetchNand",
        "pub fn fetchMin",
        "pub fn fetchMax",
        "pub fn compareExchange",
        "pub fn compareExchangeWeak",
    ),
    BARRIER_REL: ("pub fn acquire", "pub fn release", "pub fn full", "pub fn acquireRelease"),
    MMIO_REL: (
        "pub fn range",
        "pub fn allowsInteropPolicyBytes",
        "pub fn allowsInteropPolicy",
        "pub fn requireInteropPolicyBytes",
        "pub fn requireInteropPolicy",
        "pub fn rangeInteropPolicyBytes",
        "pub fn rangeInteropPolicy",
        "pub fn rangeInteropPolicyByte",
        "pub fn read8",
        "pub fn write8",
        "pub fn read16",
        "pub fn write16",
        "pub fn read32",
        "pub fn write32",
        "pub fn read64",
        "pub fn write64",
        "pub fn read8InteropPolicyBytes",
        "pub fn read8InteropPolicy",
        "pub fn read8InteropPolicyByte",
        "pub fn write8InteropPolicyBytes",
        "pub fn write8InteropPolicy",
        "pub fn write8InteropPolicyByte",
        "pub fn read16InteropPolicyBytes",
        "pub fn read16InteropPolicy",
        "pub fn read16InteropPolicyByte",
        "pub fn write16InteropPolicyBytes",
        "pub fn write16InteropPolicy",
        "pub fn write16InteropPolicyByte",
        "pub fn read32InteropPolicyBytes",
        "pub fn read32InteropPolicy",
        "pub fn read32InteropPolicyByte",
        "pub fn write32InteropPolicyBytes",
        "pub fn write32InteropPolicy",
        "pub fn write32InteropPolicyByte",
        "pub fn read64InteropPolicyBytes",
        "pub fn read64InteropPolicy",
        "pub fn read64InteropPolicyByte",
        "pub fn write64InteropPolicyBytes",
        "pub fn write64InteropPolicy",
        "pub fn write64InteropPolicyByte(",
        'test "phase3 mmio interop policy gates stay explicit"',
        "narrow.pointerAt",
    ),
    NARROW_REL: (
        "pub fn addressOf",
        "pub fn byteOffset",
        "pub fn pointerAt",
        "*align(1) volatile T",
        "pub fn constSliceAt",
        "pub fn constPointerAt",
        "pub fn writeValueAt",
        "pub fn scopeFromInteropPolicyBytes",
        "pub fn scopeFromInteropPolicy",
        "pub fn scopeFromByte",
        "pub fn recognizesInteropPolicyBytes",
        "pub fn recognizesInteropPolicy",
        "pub fn recognizesByte",
        "pub fn permitsNoUnsafePolicyBytes",
        "pub fn permitsNoUnsafeInteropPolicy",
        "pub fn permitsNoUnsafeByte",
        "pub fn permitsVolatileMmioPolicyBytes",
        "pub fn permitsVolatileMmioInteropPolicy",
        "pub fn permitsVolatileMmioByte",
        "pub fn permitsRawPointerBridgePolicyBytes",
        "pub fn permitsRawPointerBridgeInteropPolicy",
        "pub fn permitsRawPointerBridgeByte",
        'test "phase3 narrow unsafe wrappers stay bounded"',
        'test "phase3 narrow unsafe scope bytes stay explicit"',
    ),
    LOW_LEVEL_TEST_REL: (
        'test "phase3 low-level wrappers cover the shipped helper surface directly"',
        'test "phase3 low-level wrappers keep mmio interop policy gates reviewable"',
        'test "phase3 low-level wrappers keep raw pointer bridge policy gates reviewable"',
        'test "phase3 low-level wrappers keep non-seq-cst orderings and signed atomic edges reviewable"',
        'test "phase3 low-level wrappers keep barrier locality reviewable"',
        'test "phase3 low-level wrappers keep barrier handoff reviewable"',
        "atomic.fetchAdd(i32, &signed_arithmetic_value, 5, .seq_cst)",
        "atomic.fetchSub(i32, &signed_arithmetic_value, 7, .seq_cst)",
        "atomic.fetchMin(i32, &signed_value, -3, .seq_cst)",
        "atomic.fetchMax(i32, &signed_value, 6, .seq_cst)",
        "const monotonic_mismatch = atomic.compareExchange(",
        "try std.testing.expectEqual(@as(?u32, 7), monotonic_mismatch);",
        "var monotonic_nand_value: u32 = 0x0000_00ff;",
        "atomic.fetchNand(u32, &monotonic_nand_value, 0x0000_0f0f, .monotonic)",
        "try std.testing.expectEqual(@as(u32, 0xffff_fff0), monotonic_nand_value);",
        "const acq_rel_mismatch = atomic.compareExchange(",
        "try std.testing.expectEqual(@as(?u32, 11), acq_rel_mismatch);",
        "const weak_release_mismatch = atomic.compareExchangeWeak(",
        "try std.testing.expectEqual(@as(?u32, 19), weak_release_mismatch);",
        "const scoped_desc = try mmio.rangeInteropPolicy(base, 16, 4, mmio_policy);",
        "mmio.rangeInteropPolicyByte(base, 12, 2, @intFromEnum(abi.UnsafeScope.volatile_mmio))",
        "const scoped_ptr = try narrow.pointerAtInteropPolicy(u32, base, @sizeOf(u32), raw_policy);",
        "try std.testing.expectError(error.UnsafeScopeDenied, narrow.pointerAtInteropPolicy(u32, base, 0, mmio_policy));",
        "const odd_doubleword: *align(1) const u64 = @ptrCast(&bytes[5]);",
    ),
    ABI_TEST_REL: (
        'const layout_assert = @import("layout_assert");',
        'const panic_policy = @import("panic_policy");',
        'const allocator_policy = @import("allocator_policy");',
        'const atomic = @import("atomic_helpers");',
        'const barrier = @import("barrier_helpers");',
        'const mmio = @import("mmio_helpers");',
    ),
    ABI_DUMP_REL: ('"zigux_mmio_range"', '"zigux_interop_policy"'),
    ABI_EXPECTED_REL: ('"zigux_mmio_range"', '"zigux_interop_policy"'),
    ABI_SLICE_DOC_REL: (
        "`zigux/helpers/atomic.zig`",
        "`zigux/helpers/barrier.zig`",
        "`zigux/helpers/mmio.zig`",
        "`zigux/tests/phase3_low_level_wrappers.zig`",
        "signed `fetchAdd` and `fetchSub`",
        "signed `fetchMin` and `fetchMax`",
        "monotonic strong `compareExchange()`",
        "`acq_rel` strong `compareExchange()` mismatch handling",
        "non-`seq_cst` atomic ordering coverage",
        "byte, 16-bit, 32-bit, and 64-bit MMIO access",
    ),
}


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def doc_payload(line: str) -> str:
    payload = line.strip()
    for prefix in ("- ", "* "):
        if payload.startswith(prefix):
            payload = payload[len(prefix):].strip()
            break
    if payload.startswith("`") and payload.endswith("`") and len(payload) >= 2:
        payload = payload[1:-1]
    return payload


def exact_doc_count(doc: str, expected: str) -> int:
    return sum(1 for line in doc.splitlines() if doc_payload(line) == expected)


def prefixed_doc_values(doc: str, prefix: str) -> list[str]:
    return [payload for line in doc.splitlines() for payload in (doc_payload(line),) if payload.startswith(prefix)]


def require_doc_marker(issues: list[str], doc: str, expected: str) -> None:
    count = exact_doc_count(doc, expected)
    if count == 1:
        return
    if count == 0:
        issues.append(f"missing_doc_marker:{expected}")
    else:
        issues.append(f"duplicate_doc_marker:{expected}:{count}")


def require_tokens(issues: list[str], text: str, prefix: str, tokens: tuple[str, ...]) -> None:
    for token in tokens:
        if token not in text:
            issues.append(f"{prefix}:{token}")


def require_token_count(issues: list[str], text: str, prefix: str, token: str, expected: int) -> None:
    count = text.count(token)
    if count != expected:
        issues.append(f"{prefix}:{token}:{count}!={expected}")


def validate_mmio_pointer_bridge(root: Path, issues: list[str]) -> None:
    path = root / MMIO_REL
    if not path.exists():
        issues.append(f"missing_file:{MMIO_REL}")
        return
    source = path.read_text(encoding="utf-8")
    require_token_count(
        issues,
        source,
        f"mmio_pointer_bridge_count:{MMIO_REL}",
        "narrow.pointerAt(",
        MMIO_POINTER_AT_CALL_COUNT,
    )
    for token in MMIO_FORBIDDEN_RAW_POINTER_TOKENS:
        if token in source:
            issues.append(f"mmio_forbidden_raw_pointer_token:{MMIO_REL}:{token}")


def load_manifest(root: Path, issues: list[str]) -> list[str] | None:
    path = root / ABI_MANIFEST_REL
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(f"invalid_manifest_json:{ABI_MANIFEST_REL}:{exc.msg}")
        return None

    if manifest.get("phase") != ABI_MANIFEST_PHASE:
        issues.append(f"manifest_phase_mismatch:{manifest.get('phase')}!={ABI_MANIFEST_PHASE}")
    if manifest.get("status") != ABI_MANIFEST_STATUS:
        issues.append(f"manifest_status_mismatch:{manifest.get('status')}!={ABI_MANIFEST_STATUS}")
    if manifest.get("slice") != ABI_MANIFEST_SLICE:
        issues.append(f"manifest_slice_mismatch:{manifest.get('slice')}!={ABI_MANIFEST_SLICE}")

    files = manifest.get("files")
    if not isinstance(files, list) or not all(isinstance(entry, str) for entry in files):
        issues.append(f"invalid_manifest_files:{ABI_MANIFEST_REL}")
        return None

    file_count = manifest.get("file_count")
    expected_count = len(ABI_MANIFEST_REQUIRED_FILES)
    if not isinstance(file_count, int):
        issues.append(f"invalid_manifest_file_count:{ABI_MANIFEST_REL}")
    else:
        if file_count != len(files):
            issues.append(f"manifest_file_count_mismatch:{file_count}!={len(files)}")
        if file_count != expected_count:
            issues.append(f"manifest_packet_count_mismatch:{file_count}!={expected_count}")

    focused_count = sum(1 for rel in files if rel in LOW_LEVEL_WRAPPER_FOCUSED_MANIFEST_FILES)
    expected_focused_count = len(LOW_LEVEL_WRAPPER_FOCUSED_MANIFEST_FILES)
    if focused_count != expected_focused_count:
        issues.append(
            f"manifest_focused_packet_count_mismatch:{focused_count}!={expected_focused_count}"
        )
    return files


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    doc_path = root / DOC_REL
    if not doc_path.exists():
        return [f"missing_doc:{DOC_REL}"]
    doc = doc_path.read_text(encoding="utf-8")

    required_files = {
        ATOMIC_REL,
        BARRIER_REL,
        MMIO_REL,
        NARROW_REL,
        LOW_LEVEL_TEST_REL,
        ABI_TEST_REL,
        ABI_DUMP_REL,
        ABI_EXPECTED_REL,
        ABI_MANIFEST_REL,
        ABI_HARNESS_REL,
        ABI_SLICE_DOC_REL,
    }
    for rel in sorted(required_files):
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")

    for marker in REQUIRED_DOC_MARKERS:
        require_doc_marker(issues, doc, marker)

    for key, rel in BLOB_MARKERS:
        prefix = f"{key}="
        matches = prefixed_doc_values(doc, prefix)
        if not matches:
            issues.append(f"missing_doc_marker:{prefix}<sha>")
            continue
        if len(matches) != 1:
            issues.append(f"duplicate_doc_marker:{prefix}<sha>:{len(matches)}")
            continue
        actual = matches[0].split(prefix, 1)[1].strip()
        expected = blob_sha(root / rel)
        if actual != expected:
            issues.append(f"stale_blob_marker:{key}:{actual}!={expected}")

    for rel, tokens in TOKEN_CHECKS.items():
        path = root / rel
        if not path.exists():
            continue
        require_tokens(issues, path.read_text(encoding="utf-8"), f"missing_token:{rel}", tokens)

    validate_mmio_pointer_bridge(root, issues)

    files = load_manifest(root, issues)
    if files is not None:
        for rel in ABI_MANIFEST_REQUIRED_FILES:
            count = files.count(rel)
            if count == 0:
                issues.append(f"manifest_missing_entry:{rel}")
            elif count != 1:
                issues.append(f"manifest_duplicate_entry:{rel}:{count}")
        for rel in files:
            if rel not in ABI_MANIFEST_REQUIRED_FILES:
                issues.append(f"manifest_unexpected_entry:{rel}")

    return issues


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_self_test_doc(root: Path) -> str:
    lines = [
        "PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run",
        f"PHASE3_ATOMIC_PATH={ATOMIC_REL}",
        "PHASE3_ATOMIC_SCOPE=load-store-exchange-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-nand-fetch-min-fetch-max-compare-exchange-compare-exchange-weak",
        "PHASE3_ATOMIC_STATUS=bounded-helper-surface-landed",
        f"PHASE3_BARRIER_PATH={BARRIER_REL}",
        "PHASE3_BARRIER_SCOPE=acquire-release-full-acquire-release-pair",
        "PHASE3_BARRIER_STATUS=local-caller-state-and-handoff-probes-landed",
        f"PHASE3_MMIO_PATH={MMIO_REL}",
        f"PHASE3_MMIO_SCOPE={DOC_MMIO_SCOPE}",
        "PHASE3_MMIO_STATUS=byte-16-bit-32-bit-and-64-bit-mmio-through-narrow-pointer-bridge",
        f"PHASE3_NARROW_UNSAFE_PATH={NARROW_REL}",
        "PHASE3_NARROW_UNSAFE_SCOPE=address-byte-offset-align1-pointer-slice-const-pointer-write-and-interop-policy-unsafe-scope-byte-decoders",
        "PHASE3_NARROW_UNSAFE_STATUS=align1-raw-pointer-bridge-plus-explicit-unsafe-scope-byte-policy",
        f"PHASE3_LOW_LEVEL_TEST_PATH={LOW_LEVEL_TEST_REL}",
        f"PHASE3_LOW_LEVEL_TEST_SCOPE={DOC_LOW_LEVEL_TEST_SCOPE}",
        "PHASE3_LOW_LEVEL_TEST_STATUS=dedicated-focused-replay-widened-for-current-helper-surface-and-barrier-handoff",
        f"PHASE3_ABI_TEST_PATH={ABI_TEST_REL}",
        f"PHASE3_ABI_DUMP_PATH={ABI_DUMP_REL}",
        "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "PHASE3_BOUNDARY_SCOPE=focused-low-level-replay-plus-shared-abi-compile-layout-dump-packet",
        f"PHASE3_BOUNDARY_GAP={DOC_BOUNDARY_GAP}",
        "PHASE3_NEXT_BOUNDED_STEP=keep-this-survey-the-focused-replay-and-the-shared-abi-packet-aligned-when-helper-surface-moves",
    ]
    for key, rel in BLOB_MARKERS:
        lines.append(f"{key}={blob_sha(root / rel)}")
    return "\n".join(lines) + "\n"


def build_self_test_mmio_source() -> str:
    return "\n".join(
        (
            "pub fn range() void {}",
            "pub fn allowsInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool { _ = unsafe_scope; _ = reserved; return true; }",
            "pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool { _ = policy; return true; }",
            "pub fn requireInteropPolicyBytes(unsafe_scope: u8, reserved: u8) !void { _ = unsafe_scope; _ = reserved; }",
            "pub fn requireInteropPolicy(policy: abi.InteropPolicy) !void { _ = policy; }",
            "pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) !void { _ = base_addr; _ = length; _ = stride; _ = unsafe_scope; _ = reserved; }",
            "pub fn rangeInteropPolicy(base_addr: usize, length: u32, stride: u32, policy: abi.InteropPolicy) !void { _ = base_addr; _ = length; _ = stride; _ = policy; }",
            "pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) !void { _ = base_addr; _ = length; _ = stride; _ = unsafe_scope; }",
            "pub fn read8(base_addr: usize, offset: usize) u8 {",
            "    const ptr = narrow.pointerAt(u8, base_addr, offset);",
            "    return ptr.*;",
            "}",
            "pub fn write8(base_addr: usize, offset: usize, value: u8) void {",
            "    const ptr = narrow.pointerAt(u8, base_addr, offset);",
            "    ptr.* = value;",
            "}",
            "pub fn read16(base_addr: usize, offset: usize) u16 {",
            "    const ptr = narrow.pointerAt(u16, base_addr, offset);",
            "    return ptr.*;",
            "}",
            "pub fn write16(base_addr: usize, offset: usize, value: u16) void {",
            "    const ptr = narrow.pointerAt(u16, base_addr, offset);",
            "    ptr.* = value;",
            "}",
            "pub fn read32(base_addr: usize, offset: usize) u32 {",
            "    const ptr = narrow.pointerAt(u32, base_addr, offset);",
            "    return ptr.*;",
            "}",
            "pub fn write32(base_addr: usize, offset: usize, value: u32) void {",
            "    const ptr = narrow.pointerAt(u32, base_addr, offset);",
            "    ptr.* = value;",
            "}",
            "pub fn read64(base_addr: usize, offset: usize) u64 {",
            "    const ptr = narrow.pointerAt(u64, base_addr, offset);",
            "    return ptr.*;",
            "}",
            "pub fn write64(base_addr: usize, offset: usize, value: u64) void {",
            "    const ptr = narrow.pointerAt(u64, base_addr, offset);",
            "    ptr.* = value;",
            "}",
            "pub fn read8InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) !u8 { _ = unsafe_scope; _ = reserved; return read8(base_addr, offset); }",
            "pub fn read8InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) !u8 { _ = policy; return read8(base_addr, offset); }",
            "pub fn read8InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) !u8 { _ = unsafe_scope; return read8(base_addr, offset); }",
            "pub fn write8InteropPolicyBytes(base_addr: usize, offset: usize, value: u8, unsafe_scope: u8, reserved: u8) !void { _ = unsafe_scope; _ = reserved; write8(base_addr, offset, value); }",
            "pub fn write8InteropPolicy(base_addr: usize, offset: usize, value: u8, policy: abi.InteropPolicy) !void { _ = policy; write8(base_addr, offset, value); }",
            "pub fn write8InteropPolicyByte(base_addr: usize, offset: usize, value: u8, unsafe_scope: u8) !void { _ = unsafe_scope; write8(base_addr, offset, value); }",
            "pub fn read16InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) !u16 { _ = unsafe_scope; _ = reserved; return read16(base_addr, offset); }",
            "pub fn read16InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) !u16 { _ = policy; return read16(base_addr, offset); }",
            "pub fn read16InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) !u16 { _ = unsafe_scope; return read16(base_addr, offset); }",
            "pub fn write16InteropPolicyBytes(base_addr: usize, offset: usize, value: u16, unsafe_scope: u8, reserved: u8) !void { _ = unsafe_scope; _ = reserved; write16(base_addr, offset, value); }",
            "pub fn write16InteropPolicy(base_addr: usize, offset: usize, value: u16, policy: abi.InteropPolicy) !void { _ = policy; write16(base_addr, offset, value); }",
            "pub fn write16InteropPolicyByte(base_addr: usize, offset: usize, value: u16, unsafe_scope: u8) !void { _ = unsafe_scope; write16(base_addr, offset, value); }",
            "pub fn read32InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) !u32 { _ = unsafe_scope; _ = reserved; return read32(base_addr, offset); }",
            "pub fn read32InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) !u32 { _ = policy; return read32(base_addr, offset); }",
            "pub fn read32InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) !u32 { _ = unsafe_scope; return read32(base_addr, offset); }",
            "pub fn write32InteropPolicyBytes(base_addr: usize, offset: usize, value: u32, unsafe_scope: u8, reserved: u8) !void { _ = unsafe_scope; _ = reserved; write32(base_addr, offset, value); }",
            "pub fn write32InteropPolicy(base_addr: usize, offset: usize, value: u32, policy: abi.InteropPolicy) !void { _ = policy; write32(base_addr, offset, value); }",
            "pub fn write32InteropPolicyByte(base_addr: usize, offset: usize, value: u32, unsafe_scope: u8) !void { _ = unsafe_scope; write32(base_addr, offset, value); }",
            "pub fn read64InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) !u64 { _ = unsafe_scope; _ = reserved; return read64(base_addr, offset); }",
            "pub fn read64InteropPolicy(base_addr: usize, offset: usize, policy: abi.InteropPolicy) !u64 { _ = policy; return read64(base_addr, offset); }",
            "pub fn read64InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) !u64 { _ = unsafe_scope; return read64(base_addr, offset); }",
            "pub fn write64InteropPolicyBytes(base_addr: usize, offset: usize, value: u64, unsafe_scope: u8, reserved: u8) !void { _ = unsafe_scope; _ = reserved; write64(base_addr, offset, value); }",
            "pub fn write64InteropPolicy(base_addr: usize, offset: usize, value: u64, policy: abi.InteropPolicy) !void { _ = policy; write64(base_addr, offset, value); }",
            "pub fn write64InteropPolicyByte(base_addr: usize, offset: usize, value: u64, unsafe_scope: u8) !void { _ = unsafe_scope; write64(base_addr, offset, value); }",
            'test "phase3 mmio interop policy gates stay explicit" {}',
        )
    ) + "\n"


def build_valid_workspace(root: Path) -> None:
    for rel in ABI_MANIFEST_REQUIRED_FILES + (DOC_REL, ABI_MANIFEST_REL, ABI_HARNESS_REL, ABI_SLICE_DOC_REL):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("// placeholder\n", encoding="utf-8", newline="\n")

    write(root / ATOMIC_REL, "\n".join(TOKEN_CHECKS[ATOMIC_REL]) + "\n")
    write(root / BARRIER_REL, "\n".join(TOKEN_CHECKS[BARRIER_REL]) + "\n")
    write(root / MMIO_REL, build_self_test_mmio_source())
    write(root / NARROW_REL, "\n".join(TOKEN_CHECKS[NARROW_REL]) + "\n")
    write(root / LOW_LEVEL_TEST_REL, "\n".join(TOKEN_CHECKS[LOW_LEVEL_TEST_REL]) + "\n")
    write(root / ABI_TEST_REL, "\n".join(TOKEN_CHECKS[ABI_TEST_REL]) + "\n")
    write(root / ABI_DUMP_REL, '"zigux_mmio_range" "zigux_interop_policy"\n')
    write(root / ABI_EXPECTED_REL, '{"structs":{"zigux_mmio_range":{},"zigux_interop_policy":{}}}\n')
    write(root / ABI_SLICE_DOC_REL, "\n".join(TOKEN_CHECKS[ABI_SLICE_DOC_REL]) + "\n")
    write(
        root / ABI_MANIFEST_REL,
        json.dumps(
            {
                "phase": ABI_MANIFEST_PHASE,
                "status": ABI_MANIFEST_STATUS,
                "slice": ABI_MANIFEST_SLICE,
                "file_count": len(ABI_MANIFEST_REQUIRED_FILES),
                "files": list(ABI_MANIFEST_REQUIRED_FILES),
            },
            indent=2,
        )
        + "\n",
    )
    write(root / DOC_REL, build_self_test_doc(root))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_wrapper_") as tmp_dir:
        root = Path(tmp_dir)
        build_valid_workspace(root)
        assert validate(root) == [], validate(root)

        manifest = json.loads((root / ABI_MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["files"] = [rel for rel in manifest["files"] if rel != "zigux/tests/phase3_export_uapi_layout.zig"]
        manifest["file_count"] = len(manifest["files"])
        write(root / ABI_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate(root)
        assert "manifest_missing_entry:zigux/tests/phase3_export_uapi_layout.zig" in issues, issues

        build_valid_workspace(root)
        manifest = json.loads((root / ABI_MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["files"] = [rel for rel in manifest["files"] if rel != "scripts/zigux/validate_phase3_selftest.py"]
        manifest["file_count"] = len(manifest["files"])
        write(root / ABI_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate(root)
        assert "manifest_missing_entry:scripts/zigux/validate_phase3_selftest.py" in issues, issues

        build_valid_workspace(root)
        manifest = json.loads((root / ABI_MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["files"] = [rel for rel in manifest["files"] if rel != "zigux/uapi/dev_t.zig"]
        manifest["file_count"] = len(manifest["files"])
        write(root / ABI_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate(root)
        assert "manifest_missing_entry:zigux/uapi/dev_t.zig" in issues, issues

        build_valid_workspace(root)
        manifest = json.loads((root / ABI_MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["files"] = [rel for rel in manifest["files"] if rel != DOC_REL]
        manifest["files"].append("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")
        manifest["file_count"] = len(manifest["files"])
        write(root / ABI_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate(root)
        assert (
            f"manifest_focused_packet_count_mismatch:{len(LOW_LEVEL_WRAPPER_FOCUSED_MANIFEST_FILES) - 1}!={len(LOW_LEVEL_WRAPPER_FOCUSED_MANIFEST_FILES)}"
            in issues
        ), issues

        build_valid_workspace(root)
        manifest = json.loads((root / ABI_MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["files"] = [rel for rel in manifest["files"] if rel != "scripts/zigux/run-phase3-checks.py"]
        manifest["files"].append(ATOMIC_REL)
        manifest["file_count"] = len(manifest["files"])
        write(root / ABI_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate(root)
        assert (
            f"manifest_focused_packet_count_mismatch:{len(LOW_LEVEL_WRAPPER_FOCUSED_MANIFEST_FILES) + 1}!={len(LOW_LEVEL_WRAPPER_FOCUSED_MANIFEST_FILES)}"
            in issues
        ), issues

        build_valid_workspace(root)
        write(root / LOW_LEVEL_TEST_REL, (root / LOW_LEVEL_TEST_REL).read_text(encoding="utf-8").replace(
            "const weak_release_mismatch = atomic.compareExchangeWeak(\n", "", 1
        ))
        issues = validate(root)
        assert (
            "missing_token:zigux/tests/phase3_low_level_wrappers.zig:const weak_release_mismatch = atomic.compareExchangeWeak(" in issues
        ), issues

        build_valid_workspace(root)
        write(root / LOW_LEVEL_TEST_REL, (root / LOW_LEVEL_TEST_REL).read_text(encoding="utf-8").replace(
            'test "phase3 low-level wrappers keep barrier handoff reviewable"\n', '', 1
        ))
        issues = validate(root)
        assert (
            'missing_token:zigux/tests/phase3_low_level_wrappers.zig:test "phase3 low-level wrappers keep barrier handoff reviewable"' in issues
        ), issues

        build_valid_workspace(root)
        write(root / LOW_LEVEL_TEST_REL, (root / LOW_LEVEL_TEST_REL).read_text(encoding="utf-8").replace(
            "const scoped_desc = try mmio.rangeInteropPolicy(base, 16, 4, mmio_policy);\n", "", 1
        ))
        issues = validate(root)
        assert (
            "missing_token:zigux/tests/phase3_low_level_wrappers.zig:const scoped_desc = try mmio.rangeInteropPolicy(base, 16, 4, mmio_policy);" in issues
        ), issues

        build_valid_workspace(root)
        write(root / LOW_LEVEL_TEST_REL, (root / LOW_LEVEL_TEST_REL).read_text(encoding="utf-8").replace(
            "atomic.fetchNand(u32, &monotonic_nand_value, 0x0000_0f0f, .monotonic)", "", 1
        ))
        issues = validate(root)
        assert (
            "missing_token:zigux/tests/phase3_low_level_wrappers.zig:atomic.fetchNand(u32, &monotonic_nand_value, 0x0000_0f0f, .monotonic)" in issues
        ), issues

        build_valid_workspace(root)
        stale_doc = (root / DOC_REL).read_text(encoding="utf-8").replace(
            "PHASE3_ABI_MANIFEST_BLOB_SHA=", "PHASE3_ABI_MANIFEST_BLOB_SHA=stale-", 1
        )
        write(root / DOC_REL, stale_doc)
        issues = validate(root)
        assert any(issue.startswith("stale_blob_marker:PHASE3_ABI_MANIFEST_BLOB_SHA:") for issue in issues), issues

        build_valid_workspace(root)
        stale_doc = (root / DOC_REL).read_text(encoding="utf-8").replace(
            "PHASE3_LOW_LEVEL_TEST_STATUS=dedicated-focused-replay-widened-for-current-helper-surface-and-barrier-handoff",
            "PHASE3_LOW_LEVEL_TEST_STATUS=dedicated-focused-replay-widened-for-current-helper-surface",
            1,
        )
        write(root / DOC_REL, stale_doc)
        issues = validate(root)
        assert (
            "missing_doc_marker:PHASE3_LOW_LEVEL_TEST_STATUS=dedicated-focused-replay-widened-for-current-helper-surface-and-barrier-handoff" in issues
        ), issues

        build_valid_workspace(root)
        write(root / NARROW_REL, (root / NARROW_REL).read_text(encoding="utf-8").replace(
            "pub fn scopeFromInteropPolicyBytes\n", "", 1
        ))
        issues = validate(root)
        assert (
            "missing_token:zigux/unsafe/narrow.zig:pub fn scopeFromInteropPolicyBytes" in issues
        ), issues

        build_valid_workspace(root)
        write(root / MMIO_REL, (root / MMIO_REL).read_text(encoding="utf-8").replace(
            "narrow.pointerAt(", "pointerAt(", 1
        ))
        issues = validate(root)
        assert (
            f"mmio_pointer_bridge_count:{MMIO_REL}:narrow.pointerAt(:7!={MMIO_POINTER_AT_CALL_COUNT}" in issues
        ), issues

        build_valid_workspace(root)
        write(
            root / MMIO_REL,
            (root / MMIO_REL).read_text(encoding="utf-8") + "const raw = @ptrFromInt(0);\n",
        )
        issues = validate(root)
        assert (
            f"mmio_forbidden_raw_pointer_token:{MMIO_REL}:@ptrFromInt" in issues
        ), issues

        build_valid_workspace(root)
        write(root / MMIO_REL, (root / MMIO_REL).read_text(encoding="utf-8").replace(
            "pub fn read64InteropPolicyBytes", "", 1
        ))
        issues = validate(root)
        assert (
            "missing_token:zigux/helpers/mmio.zig:pub fn read64InteropPolicyBytes" in issues
        ), issues

        build_valid_workspace(root)
        write(root / MMIO_REL, (root / MMIO_REL).read_text(encoding="utf-8").replace(
            "pub fn write64InteropPolicyByte(base_addr: usize, offset: usize, value: u64, unsafe_scope: u8) !void { _ = unsafe_scope; write64(base_addr, offset, value); }",
            "",
            1,
        ))
        issues = validate(root)
        assert (
            "missing_token:zigux/helpers/mmio.zig:pub fn write64InteropPolicyByte(" in issues
        ), issues

        build_valid_workspace(root)
        write(root / NARROW_REL, (root / NARROW_REL).read_text(encoding="utf-8").replace(
            "pub fn permitsVolatileMmioInteropPolicy\n", "", 1
        ))
        issues = validate(root)
        assert (
            "missing_token:zigux/unsafe/narrow.zig:pub fn permitsVolatileMmioInteropPolicy" in issues
        ), issues

        build_valid_workspace(root)
        write(root / MMIO_REL, (root / MMIO_REL).read_text(encoding="utf-8").replace(
            'test "phase3 mmio interop policy gates stay explicit"', '', 1
        ))
        issues = validate(root)
        assert (
            'missing_token:zigux/helpers/mmio.zig:test "phase3 mmio interop policy gates stay explicit"' in issues
        ), issues

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 3 low-level-wrapper survey against current repo state.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated self-test coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=fail")
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_ISSUES_END")
        return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
