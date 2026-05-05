#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
DOC_REL = "Documentation/zigux/phase3-low-level-wrapper-survey.md"

ATOMIC_REL = "zigux/helpers/atomic.zig"
BARRIER_REL = "zigux/helpers/barrier.zig"
MMIO_REL = "zigux/helpers/mmio.zig"
ABI_TEST_REL = "zigux/tests/phase3_abi.zig"
ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
ABI_EXPECTED_REL = "zigux/tests/fixtures/phase3_abi/expected.json"
ABI_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
ABI_SLICE_DOC_REL = "Documentation/zigux/phase3-abi-slice.md"


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
    }
    for key, rel in required_paths.items():
        if f"{key}={rel}" not in doc:
            issues.append(f"missing_doc_marker:{key}={rel}")
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")

    required_doc_markers = [
        "PHASE3_ATOMIC_BLOB_SHA=647275db7988f5cb53506ad3bc689336e7d1be80",
        "PHASE3_BARRIER_BLOB_SHA=d3f5db5ad00737c2d0a480cac775aeb26d5f9bd9",
        "PHASE3_MMIO_BLOB_SHA=51cbee2b49cf551b051eb5427c4917b2fe74e6a9",
        "PHASE3_ABI_TEST_BLOB_SHA=7c3c7887bb23d1acccd835ed3bb71eba3824c45d",
        "PHASE3_ABI_DUMP_BLOB_SHA=77eeb1a928ae2032b72960546277290d5116ab0b",
        "PHASE3_ABI_MANIFEST_BLOB_SHA=86ca818027f58c85c296cf39214bd1804ca55b4d",
        "PHASE3_ABI_SLICE_DOC_BLOB_SHA=7b9e7f33bfb4024e0c7e761d64c4920dfb92dc83",
        "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "PHASE3_LOW_LEVEL_WRAPPER_SCOPE=atomic-barrier-mmio-shared-abi-packet",
        "PHASE3_LOW_LEVEL_WRAPPER_GAP=shared-dump-covers-mmio-range-while-atomic-and-barrier-remain-helper-local-only",
    ]
    for marker in required_doc_markers:
        if marker not in doc:
            issues.append(f"missing_doc_marker:{marker}")

    atomic_text = (root / ATOMIC_REL).read_text(encoding="utf-8")
    for token in ("pub fn load", "pub fn store", "pub fn exchange", "pub fn compareExchange"):
        if token not in atomic_text:
            issues.append(f"atomic_missing_token:{token}")

    barrier_text = (root / BARRIER_REL).read_text(encoding="utf-8")
    for token in ("pub fn acquire", "pub fn release", "pub fn full"):
        if token not in barrier_text:
            issues.append(f"barrier_missing_token:{token}")

    mmio_text = (root / MMIO_REL).read_text(encoding="utf-8")
    for token in ("pub fn range", "pub fn read32", "pub fn write32", 'narrow.pointerAt'):
        if token not in mmio_text:
            issues.append(f"mmio_missing_token:{token}")

    abi_test_text = (root / ABI_TEST_REL).read_text(encoding="utf-8")
    for token in (
        'const atomic = @import("atomic_helpers");',
        'const barrier = @import("barrier_helpers");',
        'const mmio = @import("mmio_helpers");',
    ):
        if token not in abi_test_text:
            issues.append(f"abi_test_missing_token:{token}")

    manifest_text = (root / ABI_MANIFEST_REL).read_text(encoding="utf-8")
    for rel in (ATOMIC_REL, BARRIER_REL, MMIO_REL, ABI_TEST_REL):
        if rel not in manifest_text:
            issues.append(f"manifest_missing_entry:{rel}")

    abi_dump_text = (root / ABI_DUMP_REL).read_text(encoding="utf-8")
    expected_text = (root / ABI_EXPECTED_REL).read_text(encoding="utf-8")
    for token in ('"zigux_mmio_range"', '"zigux_interop_policy"'):
        if token not in abi_dump_text:
            issues.append(f"abi_dump_missing_token:{token}")
        if token not in expected_text:
            issues.append(f"abi_expected_missing_token:{token}")

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
                    "pub fn compareExchange() void {}",
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
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / MMIO_REL).write_text(
            "\n".join(
                [
                    "pub fn range() void {}",
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
        (root / ABI_SLICE_DOC_REL).write_text("slice\n", encoding="utf-8")
        (root / DOC_REL).write_text(
            "\n".join(
                [
                    f"PHASE3_ATOMIC_PATH={ATOMIC_REL}",
                    f"PHASE3_BARRIER_PATH={BARRIER_REL}",
                    f"PHASE3_MMIO_PATH={MMIO_REL}",
                    f"PHASE3_ABI_TEST_PATH={ABI_TEST_REL}",
                    "PHASE3_ATOMIC_BLOB_SHA=647275db7988f5cb53506ad3bc689336e7d1be80",
                    "PHASE3_BARRIER_BLOB_SHA=d3f5db5ad00737c2d0a480cac775aeb26d5f9bd9",
                    "PHASE3_MMIO_BLOB_SHA=51cbee2b49cf551b051eb5427c4917b2fe74e6a9",
                    "PHASE3_ABI_TEST_BLOB_SHA=7c3c7887bb23d1acccd835ed3bb71eba3824c45d",
                    "PHASE3_ABI_DUMP_BLOB_SHA=77eeb1a928ae2032b72960546277290d5116ab0b",
                    "PHASE3_ABI_MANIFEST_BLOB_SHA=86ca818027f58c85c296cf39214bd1804ca55b4d",
                    "PHASE3_ABI_SLICE_DOC_BLOB_SHA=7b9e7f33bfb4024e0c7e761d64c4920dfb92dc83",
                    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
                    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
                    "PHASE3_LOW_LEVEL_WRAPPER_SCOPE=atomic-barrier-mmio-shared-abi-packet",
                    "PHASE3_LOW_LEVEL_WRAPPER_GAP=shared-dump-covers-mmio-range-while-atomic-and-barrier-remain-helper-local-only",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        issues = validate(root)
        assert issues == [], issues

        (root / ABI_EXPECTED_REL).write_text('{"structs":{"zigux_interop_policy":{}}}\n', encoding="utf-8")
        issues = validate(root)
        assert 'abi_expected_missing_token:"zigux_mmio_range"' in issues

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
