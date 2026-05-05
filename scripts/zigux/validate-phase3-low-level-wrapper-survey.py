#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
DOC_REL = "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"
ATOMIC_REL = "zigux/helpers/atomic.zig"
BARRIER_REL = "zigux/helpers/barrier.zig"
MMIO_REL = "zigux/helpers/mmio.zig"
ABI_TEST_REL = "zigux/tests/phase3_abi.zig"
ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
ABI_EXPECTED_REL = "zigux/tests/fixtures/phase3_abi/expected.json"
ABI_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"

REQUIRED_DOC_MARKERS = (
    f"PHASE3_ATOMIC_PATH={ATOMIC_REL}",
    "PHASE3_ATOMIC_SCOPE=load-store-exchange-fetch-add-fetch-sub-fetch-and-fetch-or-fetch-xor-fetch-min-fetch-max-compare-exchange-compare-exchange-weak",
    "PHASE3_ATOMIC_STATUS=bounded-helper-surface-landed",
    "PHASE3_ATOMIC_BLOB_SHA=4676896a36610c7c20168aa5ef6a5c68a1b39e45",
    f"PHASE3_BARRIER_PATH={BARRIER_REL}",
    "PHASE3_BARRIER_SCOPE=acquire-release-full-acquire-release-pair",
    "PHASE3_BARRIER_STATUS=local-sentinel-probe-only",
    "PHASE3_BARRIER_BLOB_SHA=1fe0f75696631f3ebf6f97897ba2e648e375458f",
    f"PHASE3_MMIO_PATH={MMIO_REL}",
    "PHASE3_MMIO_SCOPE=range-read8-write8-read32-write32",
    "PHASE3_MMIO_STATUS=byte-and-32-bit-mmio-through-narrow-pointer-bridge",
    "PHASE3_MMIO_BLOB_SHA=b4d56107ff0f3d2845d7c26dac87d5f594602a28",
    f"PHASE3_ABI_TEST_PATH={ABI_TEST_REL}",
    "PHASE3_ABI_TEST_BLOB_SHA=7c3c7887bb23d1acccd835ed3bb71eba3824c45d",
    f"PHASE3_ABI_DUMP_PATH={ABI_DUMP_REL}",
    "PHASE3_ABI_DUMP_BLOB_SHA=77eeb1a928ae2032b72960546277290d5116ab0b",
    "PHASE3_ABI_EXPECTED_BLOB_SHA=891be039615b878e10fda94788bc896ef12aac7b",
    "PHASE3_ABI_MANIFEST_BLOB_SHA=86ca818027f58c85c296cf39214bd1804ca55b4d",
    "PHASE3_ABI_SLICE_DOC_BLOB_SHA=af6903d07186321da167ab6718b7b4810b78c008",
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
    "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "PHASE3_BOUNDARY_SCOPE=shared-abi-compile-layout-dump-packet",
    "PHASE3_BOUNDARY_GAP=shared-abi-packet-covers-current-low-level-wrapper-surface-without-a-dedicated-low-level-wrapper-replay",
)

STALE_DOC_MARKERS = (
    "PHASE3_LOW_LEVEL_BUILD_PATH=",
    "PHASE3_LOW_LEVEL_BUILD_BLOB_SHA=",
    "PHASE3_LOW_LEVEL_TEST_PATH=",
    "PHASE3_LOW_LEVEL_TEST_BLOB_SHA=",
)

ATOMIC_TOKENS = (
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
    "pub fn compareExchange(",
    "pub fn compareExchangeWeak(",
)
BARRIER_TOKENS = ("pub fn acquire", "pub fn release", "pub fn full", "pub fn acquireRelease")
MMIO_TOKENS = ("pub fn range", "pub fn read8", "pub fn write8", "pub fn read32", "pub fn write32", "narrow.pointerAt")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    doc_path = root / DOC_REL
    if not doc_path.exists():
        return [f"missing_doc:{DOC_REL}"]
    doc = _read(doc_path)

    for rel in (ATOMIC_REL, BARRIER_REL, MMIO_REL, ABI_TEST_REL, ABI_DUMP_REL, ABI_EXPECTED_REL, ABI_MANIFEST_REL):
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")

    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc:
            issues.append(f"missing_doc_marker:{marker}")
    for marker in STALE_DOC_MARKERS:
        if marker in doc:
            issues.append(f"stale_doc_marker:{marker}")

    atomic_text = _read(root / ATOMIC_REL)
    for token in ATOMIC_TOKENS:
        if token not in atomic_text:
            issues.append(f"atomic_missing_token:{token}")

    barrier_text = _read(root / BARRIER_REL)
    for token in BARRIER_TOKENS:
        if token not in barrier_text:
            issues.append(f"barrier_missing_token:{token}")

    mmio_text = _read(root / MMIO_REL)
    for token in MMIO_TOKENS:
        if token not in mmio_text:
            issues.append(f"mmio_missing_token:{token}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_boundary_") as tmp_dir:
        root = Path(tmp_dir)
        for rel in (DOC_REL, ATOMIC_REL, BARRIER_REL, MMIO_REL, ABI_TEST_REL, ABI_DUMP_REL, ABI_EXPECTED_REL, ABI_MANIFEST_REL):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("placeholder\n", encoding="utf-8")

        (root / ATOMIC_REL).write_text("\n".join(ATOMIC_TOKENS) + "\n", encoding="utf-8")
        (root / BARRIER_REL).write_text("\n".join(BARRIER_TOKENS) + "\n", encoding="utf-8")
        (root / MMIO_REL).write_text("\n".join(MMIO_TOKENS) + "\n", encoding="utf-8")
        (root / DOC_REL).write_text("\n".join(REQUIRED_DOC_MARKERS) + "\n", encoding="utf-8")
        assert validate(root) == []

        (root / DOC_REL).write_text("\n".join(REQUIRED_DOC_MARKERS + (STALE_DOC_MARKERS[0],)) + "\n", encoding="utf-8")
        issues = validate(root)
        assert f"stale_doc_marker:{STALE_DOC_MARKERS[0]}" in issues

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate the Phase 3 low-level wrapper boundary survey against the live shared ABI packet.")
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
