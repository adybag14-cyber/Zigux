#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile


FILE_PATH = Path(__file__).resolve()
ROOT = FILE_PATH.parents[2] if len(FILE_PATH.parents) >= 3 else FILE_PATH.parent
DOC_REL = "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"

ATOMIC_REL = "zigux/helpers/atomic.zig"
BARRIER_REL = "zigux/helpers/barrier.zig"
MMIO_REL = "zigux/helpers/mmio.zig"
ABI_TEST_REL = "zigux/tests/phase3_abi.zig"
ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
ABI_EXPECTED_REL = "zigux/tests/fixtures/phase3_abi/expected.json"
ABI_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
ABI_SLICE_DOC_REL = "Documentation/zigux/phase3-abi-slice.md"


def blob_sha(path: Path) -> str:
    content = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()


def require_tokens(issues: list[str], text: str, prefix: str, tokens: tuple[str, ...]) -> None:
    for token in tokens:
        if token not in text:
            issues.append(f"{prefix}:{token}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    doc_path = root / DOC_REL
    if not doc_path.exists():
        return [f"missing_doc:{DOC_REL}"]
    doc = doc_path.read_text(encoding="utf-8")

    required_paths = {
        "PHASE3_ATOMIC_PATH": ATOMIC_REL,
        "PHASE3_BARRIER_PATH": BARRIER_REL,
        "PHASE3_MMIO_PATH": MMIO_REL,
        "PHASE3_ABI_TEST_PATH": ABI_TEST_REL,
        "PHASE3_ABI_DUMP_PATH": ABI_DUMP_REL,
    }
    for key, rel in required_paths.items():
        if f"{key}={rel}" not in doc:
            issues.append(f"missing_doc_marker:{key}={rel}")
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")

    for rel in (ABI_EXPECTED_REL, ABI_MANIFEST_REL, ABI_SLICE_DOC_REL):
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")

    required_doc_markers = (
        "PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run",
        "PHASE3_ATOMIC_SCOPE=load-store-exchange-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max-compare-exchange-compare-exchange-weak",
        "PHASE3_ATOMIC_STATUS=bounded-helper-surface-landed",
        "PHASE3_BARRIER_SCOPE=acquire-release-full-acquire-release-pair",
        "PHASE3_BARRIER_STATUS=local-sentinel-probe-only",
        "PHASE3_MMIO_SCOPE=range-read8-write8-read32-write32",
        "PHASE3_MMIO_STATUS=byte-and-32-bit-mmio-through-narrow-pointer-bridge",
        "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "PHASE3_BOUNDARY_SCOPE=shared-abi-compile-layout-dump-packet",
        "PHASE3_BOUNDARY_GAP=shared-abi-packet-covers-current-low-level-wrapper-surface-without-a-dedicated-low-level-wrapper-replay",
        "PHASE3_NEXT_BOUNDED_STEP=keep-the-shared-abi-packet-and-this-survey-aligned-until-a-real-dedicated-low-level-wrapper-replay-lands",
    )
    for marker in required_doc_markers:
        if marker not in doc:
            issues.append(f"missing_doc_marker:{marker}")

    for key, rel in (
        ("PHASE3_ATOMIC_BLOB_SHA", ATOMIC_REL),
        ("PHASE3_BARRIER_BLOB_SHA", BARRIER_REL),
        ("PHASE3_MMIO_BLOB_SHA", MMIO_REL),
        ("PHASE3_ABI_TEST_BLOB_SHA", ABI_TEST_REL),
        ("PHASE3_ABI_DUMP_BLOB_SHA", ABI_DUMP_REL),
        ("PHASE3_ABI_EXPECTED_BLOB_SHA", ABI_EXPECTED_REL),
        ("PHASE3_ABI_MANIFEST_BLOB_SHA", ABI_MANIFEST_REL),
        ("PHASE3_ABI_SLICE_DOC_BLOB_SHA", ABI_SLICE_DOC_REL),
    ):
        marker = f"{key}="
        line = next((entry for entry in doc.splitlines() if marker in entry), "")
        if not line:
            issues.append(f"missing_doc_marker:{marker}<sha>")
            continue
        actual = line.split(marker, 1)[1].strip().rstrip("`")
        expected = blob_sha(root / rel)
        if actual != expected:
            issues.append(f"stale_blob_marker:{key}:{actual}!={expected}")

    atomic_text = (root / ATOMIC_REL).read_text(encoding="utf-8")
    require_tokens(
        issues,
        atomic_text,
        "atomic_missing_token",
        (
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
    )

    barrier_text = (root / BARRIER_REL).read_text(encoding="utf-8")
    require_tokens(
        issues,
        barrier_text,
        "barrier_missing_token",
        (
            "pub fn acquire",
            "pub fn release",
            "pub fn full",
            "pub fn acquireRelease",
        ),
    )

    mmio_text = (root / MMIO_REL).read_text(encoding="utf-8")
    require_tokens(
        issues,
        mmio_text,
        "mmio_missing_token",
        (
            "pub fn range",
            "pub fn read8",
            "pub fn write8",
            "pub fn read32",
            "pub fn write32",
            "narrow.pointerAt",
        ),
    )

    abi_test_text = (root / ABI_TEST_REL).read_text(encoding="utf-8")
    require_tokens(
        issues,
        abi_test_text,
        "abi_test_missing_token",
        (
            'const layout_assert = @import("layout_assert");',
            'const panic_policy = @import("panic_policy");',
            'const allocator_policy = @import("allocator_policy");',
            'const atomic = @import("atomic_helpers");',
            'const barrier = @import("barrier_helpers");',
            'const mmio = @import("mmio_helpers");',
        ),
    )

    abi_dump_text = (root / ABI_DUMP_REL).read_text(encoding="utf-8")
    abi_expected_text = (root / ABI_EXPECTED_REL).read_text(encoding="utf-8")
    require_tokens(
        issues,
        abi_dump_text,
        "abi_dump_missing_token",
        ('"zigux_mmio_range"', '"zigux_interop_policy"'),
    )
    require_tokens(
        issues,
        abi_expected_text,
        "abi_expected_missing_token",
        ('"zigux_mmio_range"', '"zigux_interop_policy"'),
    )

    manifest_text = (root / ABI_MANIFEST_REL).read_text(encoding="utf-8")
    for rel in (ATOMIC_REL, BARRIER_REL, MMIO_REL, ABI_TEST_REL):
        if rel not in manifest_text:
            issues.append(f"manifest_missing_entry:{rel}")

    abi_slice_text = (root / ABI_SLICE_DOC_REL).read_text(encoding="utf-8")
    require_tokens(
        issues,
        abi_slice_text,
        "abi_slice_missing_token",
        (
            "`zigux/helpers/atomic.zig`",
            "`zigux/helpers/barrier.zig`",
            "`zigux/helpers/mmio.zig`",
            "`zigux/tests/phase3_low_level_wrappers.zig`",
        ),
    )

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_wrapper_") as tmp_dir:
        root = Path(tmp_dir)
        for rel in (
            ATOMIC_REL,
            BARRIER_REL,
            MMIO_REL,
            ABI_TEST_REL,
            ABI_DUMP_REL,
            ABI_EXPECTED_REL,
            ABI_MANIFEST_REL,
            ABI_SLICE_DOC_REL,
            DOC_REL,
        ):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)

        (root / ATOMIC_REL).write_text(
            "\n".join(
                [
                    "pub fn load() void {}",
                    "pub fn store() void {}",
                    "pub fn exchange() void {}",
                    "pub fn fetchAdd() void {}",
                    "pub fn fetchSub() void {}",
                    "pub fn fetchAnd() void {}",
                    "pub fn fetchOr() void {}",
                    "pub fn fetchXor() void {}",
                    "pub fn fetchMin() void {}",
                    "pub fn fetchMax() void {}",
                    "pub fn compareExchange() void {}",
                    "pub fn compareExchangeWeak() void {}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / BARRIER_REL).write_text(
            "\n".join(
                [
                    "pub fn acquire() void {}",
                    "pub fn release() void {}",
                    "pub fn full() void {}",
                    "pub fn acquireRelease() void {}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / MMIO_REL).write_text(
            "\n".join(
                [
                    "pub fn range() void {}",
                    "pub fn read8() void {}",
                    "pub fn write8() void {}",
                    "pub fn read32() void {}",
                    "pub fn write32() void {}",
                    "const p = narrow.pointerAt(u32, 0, 0);",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / ABI_TEST_REL).write_text(
            "\n".join(
                [
                    'const layout_assert = @import("layout_assert");',
                    'const panic_policy = @import("panic_policy");',
                    'const allocator_policy = @import("allocator_policy");',
                    'const atomic = @import("atomic_helpers");',
                    'const barrier = @import("barrier_helpers");',
                    'const mmio = @import("mmio_helpers");',
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / ABI_DUMP_REL).write_text(
            '\n'.join(['const mmio = "zigux_mmio_range";', 'const policy = "zigux_interop_policy";', ""]),
            encoding="utf-8",
        )
        (root / ABI_EXPECTED_REL).write_text(
            '{"structs":{"zigux_mmio_range":{},"zigux_interop_policy":{}}}\n',
            encoding="utf-8",
        )
        (root / ABI_MANIFEST_REL).write_text(
            "\n".join(
                [
                    "{",
                    f'  "files": ["{ATOMIC_REL}", "{BARRIER_REL}", "{MMIO_REL}", "{ABI_TEST_REL}"]',
                    "}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / ABI_SLICE_DOC_REL).write_text(
            "\n".join(
                [
                    "`zigux/helpers/atomic.zig`",
                    "`zigux/helpers/barrier.zig`",
                    "`zigux/helpers/mmio.zig`",
                    "`zigux/tests/phase3_low_level_wrappers.zig`",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        (root / DOC_REL).write_text(
            "\n".join(
                [
                    "PHASE3_SURVEY_PROVENANCE=packet-local-blob-first-current-head-sha-unavailable-in-connector-run",
                    f"PHASE3_ATOMIC_PATH={ATOMIC_REL}",
                    f"PHASE3_BARRIER_PATH={BARRIER_REL}",
                    f"PHASE3_MMIO_PATH={MMIO_REL}",
                    f"PHASE3_ABI_TEST_PATH={ABI_TEST_REL}",
                    f"PHASE3_ABI_DUMP_PATH={ABI_DUMP_REL}",
                    "PHASE3_ATOMIC_SCOPE=load-store-exchange-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max-compare-exchange-compare-exchange-weak",
                    "PHASE3_ATOMIC_STATUS=bounded-helper-surface-landed",
                    f"PHASE3_ATOMIC_BLOB_SHA={blob_sha(root / ATOMIC_REL)}",
                    "PHASE3_BARRIER_SCOPE=acquire-release-full-acquire-release-pair",
                    "PHASE3_BARRIER_STATUS=local-sentinel-probe-only",
                    f"PHASE3_BARRIER_BLOB_SHA={blob_sha(root / BARRIER_REL)}",
                    "PHASE3_MMIO_SCOPE=range-read8-write8-read32-write32",
                    "PHASE3_MMIO_STATUS=byte-and-32-bit-mmio-through-narrow-pointer-bridge",
                    f"PHASE3_MMIO_BLOB_SHA={blob_sha(root / MMIO_REL)}",
                    f"PHASE3_ABI_TEST_BLOB_SHA={blob_sha(root / ABI_TEST_REL)}",
                    f"PHASE3_ABI_DUMP_BLOB_SHA={blob_sha(root / ABI_DUMP_REL)}",
                    f"PHASE3_ABI_EXPECTED_BLOB_SHA={blob_sha(root / ABI_EXPECTED_REL)}",
                    f"PHASE3_ABI_MANIFEST_BLOB_SHA={blob_sha(root / ABI_MANIFEST_REL)}",
                    f"PHASE3_ABI_SLICE_DOC_BLOB_SHA={blob_sha(root / ABI_SLICE_DOC_REL)}",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
                    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
                    "PHASE3_BOUNDARY_SCOPE=shared-abi-compile-layout-dump-packet",
                    "PHASE3_BOUNDARY_GAP=shared-abi-packet-covers-current-low-level-wrapper-surface-without-a-dedicated-low-level-wrapper-replay",
                    "PHASE3_NEXT_BOUNDED_STEP=keep-the-shared-abi-packet-and-this-survey-aligned-until-a-real-dedicated-low-level-wrapper-replay-lands",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        issues = validate(root)
        assert issues == [], issues

        (root / DOC_REL).write_text(
            (root / DOC_REL).read_text(encoding="utf-8").replace(
                "PHASE3_ABI_SLICE_DOC_BLOB_SHA=", "PHASE3_ABI_SLICE_DOC_SHA="
            ),
            encoding="utf-8",
        )
        issues = validate(root)
        assert "missing_doc_marker:PHASE3_ABI_SLICE_DOC_BLOB_SHA=<sha>" in issues

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate the Phase 3 low-level wrapper survey markers against live repo state.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated self-test coverage in a temporary workspace.")
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