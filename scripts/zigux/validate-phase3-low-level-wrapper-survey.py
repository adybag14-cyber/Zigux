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
LOW_LEVEL_TEST_REL = "zigux/tests/phase3_low_level_wrappers.zig"
ABI_TEST_REL = "zigux/tests/phase3_abi.zig"
ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
ABI_EXPECTED_REL = "zigux/tests/fixtures/phase3_abi/expected.json"
ABI_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
ABI_HARNESS_REL = "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"
ABI_SLICE_DOC_REL = "Documentation/zigux/phase3-abi-slice.md"

ABI_MANIFEST_PHASE = "Phase 3"
ABI_MANIFEST_STATUS = "active"
ABI_MANIFEST_SLICE = "abi-substrate-skeleton"
SELF_TEST_CASE_COUNT = 4

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
    "zigux/unsafe/narrow.zig",
    "zigux/uapi/version.zig",
    ABI_TEST_REL,
    ABI_DUMP_REL,
    "zigux/tests/phase3_export_uapi_layout.zig",
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
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    ABI_SLICE_DOC_REL,
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    DOC_REL,
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
)

REQUIRED_DOC_MARKERS = (
    f"PHASE3_ATOMIC_PATH={ATOMIC_REL}",
    f"PHASE3_BARRIER_PATH={BARRIER_REL}",
    f"PHASE3_MMIO_PATH={MMIO_REL}",
    f"PHASE3_LOW_LEVEL_TEST_PATH={LOW_LEVEL_TEST_REL}",
    f"PHASE3_ABI_TEST_PATH={ABI_TEST_REL}",
    f"PHASE3_ABI_DUMP_PATH={ABI_DUMP_REL}",
    "PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run",
    "PHASE3_ATOMIC_SCOPE=load-store-exchange-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max-compare-exchange-compare-exchange-weak",
    "PHASE3_ATOMIC_STATUS=bounded-helper-surface-landed",
    "PHASE3_BARRIER_SCOPE=acquire-release-full-acquire-release-pair",
    "PHASE3_BARRIER_STATUS=local-sentinel-probe-only",
    "PHASE3_MMIO_SCOPE=range-read8-write8-read16-write16-read32-write32-read64-write64",
    "PHASE3_MMIO_STATUS=byte-16-bit-32-bit-and-64-bit-mmio-through-narrow-pointer-bridge",
    "PHASE3_LOW_LEVEL_TEST_SCOPE=focused-atomic-barrier-mmio-replay-plus-signed-atomic-edges-acq-rel-strong-compare-exchange-mismatch-barrier-locality-non-seq-cst-ordering-and-byte-16-bit-32-bit-and-64-bit-mmio-range-replay",
    "PHASE3_LOW_LEVEL_TEST_STATUS=dedicated-focused-replay-widened-for-current-helper-surface",
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "PHASE3_BOUNDARY_SCOPE=focused-low-level-replay-plus-shared-abi-compile-layout-dump-packet",
    "PHASE3_BOUNDARY_GAP=focused-low-level-replay-now-covers-signed-fetch-and-min-max-edges-plus-monotonic-and-acq-rel-strong-compare-exchange-mismatch-byte-16-bit-32-bit-and-64-bit-mmio-range-and-barrier-locality-while-shared-abi-packet-still-carries-the-broader-compile-layout-and-dump-proof",
    "PHASE3_NEXT_BOUNDED_STEP=keep-this-survey-the-focused-replay-and-the-shared-abi-packet-aligned-when-helper-surface-moves",
)

BLOB_MARKERS = (
    ("PHASE3_ATOMIC_BLOB_SHA", ATOMIC_REL),
    ("PHASE3_BARRIER_BLOB_SHA", BARRIER_REL),
    ("PHASE3_MMIO_BLOB_SHA", MMIO_REL),
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
        "pub fn fetchMin",
        "pub fn fetchMax",
        "pub fn compareExchange",
        "pub fn compareExchangeWeak",
    ),
    BARRIER_REL: ("pub fn acquire", "pub fn release", "pub fn full", "pub fn acquireRelease"),
    MMIO_REL: (
        "pub fn range",
        "pub fn read8",
        "pub fn write8",
        "pub fn read16",
        "pub fn write16",
        "pub fn read32",
        "pub fn write32",
        "pub fn read64",
        "pub fn write64",
        "narrow.pointerAt",
    ),
    LOW_LEVEL_TEST_REL: (
        'test "phase3 low-level wrappers cover the shipped helper surface directly"',
        'test "phase3 low-level wrappers keep non-seq-cst orderings and signed atomic edges reviewable"',
        'test "phase3 low-level wrappers keep barrier locality reviewable"',
        "atomic.fetchAdd(i32, &signed_arithmetic_value, 5, .seq_cst)",
        "atomic.fetchSub(i32, &signed_arithmetic_value, 7, .seq_cst)",
        "atomic.fetchMin(i32, &signed_value, -3, .seq_cst)",
        "atomic.fetchMax(i32, &signed_value, 6, .seq_cst)",
        "const monotonic_mismatch = atomic.compareExchange(",
        "try std.testing.expectEqual(@as(?u32, 7), monotonic_mismatch);",
        "const acq_rel_mismatch = atomic.compareExchange(",
        "try std.testing.expectEqual(@as(?u32, 11), acq_rel_mismatch);",
        "const weak_release_mismatch = atomic.compareExchangeWeak(",
        "try std.testing.expectEqual(@as(?u32, 19), weak_release_mismatch);",
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
        "PHASE3_ATOMIC_SCOPE=load-store-exchange-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max-compare-exchange-compare-exchange-weak",
        "PHASE3_ATOMIC_STATUS=bounded-helper-surface-landed",
        f"PHASE3_BARRIER_PATH={BARRIER_REL}",
        "PHASE3_BARRIER_SCOPE=acquire-release-full-acquire-release-pair",
        "PHASE3_BARRIER_STATUS=local-sentinel-probe-only",
        f"PHASE3_MMIO_PATH={MMIO_REL}",
        "PHASE3_MMIO_SCOPE=range-read8-write8-read16-write16-read32-write32-read64-write64",
        "PHASE3_MMIO_STATUS=byte-16-bit-32-bit-and-64-bit-mmio-through-narrow-pointer-bridge",
        f"PHASE3_LOW_LEVEL_TEST_PATH={LOW_LEVEL_TEST_REL}",
        "PHASE3_LOW_LEVEL_TEST_SCOPE=focused-atomic-barrier-mmio-replay-plus-signed-atomic-edges-acq-rel-strong-compare-exchange-mismatch-barrier-locality-non-seq-cst-ordering-and-byte-16-bit-32-bit-and-64-bit-mmio-range-replay",
        "PHASE3_LOW_LEVEL_TEST_STATUS=dedicated-focused-replay-widened-for-current-helper-surface",
        f"PHASE3_ABI_TEST_PATH={ABI_TEST_REL}",
        f"PHASE3_ABI_DUMP_PATH={ABI_DUMP_REL}",
        "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "PHASE3_BOUNDARY_SCOPE=focused-low-level-replay-plus-shared-abi-compile-layout-dump-packet",
        "PHASE3_BOUNDARY_GAP=focused-low-level-replay-now-covers-signed-fetch-and-min-max-edges-plus-monotonic-and-acq-rel-strong-compare-exchange-mismatch-byte-16-bit-32-bit-and-64-bit-mmio-range-and-barrier-locality-while-shared-abi-packet-still-carries-the-broader-compile-layout-and-dump-proof",
        "PHASE3_NEXT_BOUNDED_STEP=keep-this-survey-the-focused-replay-and-the-shared-abi-packet-aligned-when-helper-surface-moves",
    ]
    for key, rel in BLOB_MARKERS:
        lines.append(f"{key}={blob_sha(root / rel)}")
    return "\n".join(lines) + "\n"


def build_valid_workspace(root: Path) -> None:
    for rel in ABI_MANIFEST_REQUIRED_FILES + (DOC_REL, ABI_MANIFEST_REL, ABI_HARNESS_REL, ABI_SLICE_DOC_REL):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("// placeholder\n", encoding="utf-8", newline="\n")

    write(root / ATOMIC_REL, "\n".join(TOKEN_CHECKS[ATOMIC_REL]) + "\n")
    write(root / BARRIER_REL, "\n".join(TOKEN_CHECKS[BARRIER_REL]) + "\n")
    write(root / MMIO_REL, "\n".join(TOKEN_CHECKS[MMIO_REL]) + "\n")
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
        write(root / LOW_LEVEL_TEST_REL, (root / LOW_LEVEL_TEST_REL).read_text(encoding="utf-8").replace(
            "const weak_release_mismatch = atomic.compareExchangeWeak(\n", "", 1
        ))
        issues = validate(root)
        assert (
            "missing_token:zigux/tests/phase3_low_level_wrappers.zig:const weak_release_mismatch = atomic.compareExchangeWeak(" in issues
        ), issues

        build_valid_workspace(root)
        stale_doc = (root / DOC_REL).read_text(encoding="utf-8").replace(
            "PHASE3_ABI_MANIFEST_BLOB_SHA=", "PHASE3_ABI_MANIFEST_BLOB_SHA=stale-", 1
        )
        write(root / DOC_REL, stale_doc)
        issues = validate(root)
        assert any(issue.startswith("stale_blob_marker:PHASE3_ABI_MANIFEST_BLOB_SHA:") for issue in issues), issues

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
