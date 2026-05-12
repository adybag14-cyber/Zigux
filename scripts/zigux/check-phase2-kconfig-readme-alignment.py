#!/usr/bin/env python3

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
README = ROOT / "README.md"

CURRENT_PHASE2_LIVE_SENTENCE = (
    "- `check-zig-toolchain.py`, `install-zig.py`, `validate-phase2.py`, `validate-phase2-closure.py`, `check-phase2-toolchain-pin-scope.py`, `check-phase2-tests-readme-alignment.py`, `check-phase2-kconfig-readme-alignment.py`, `check-phase2-tool-manifest-packets.py`, `check-phase2-fixdep-gate.py`, `check-fixdep-diff.py`, `check-genksyms-bridge.py`, `check-phase2-cross.py`, `check-phase2-cross-selftest-alignment.py`, and `check-phase2-kconfig-selftest-alignment.py` are the live shared scripts-root Phase 2 helpers on current `master`; the broader `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` route inventory plus the dedicated fixdep, genksyms, manifest, cross-target, and bridge checker packet should stay documented through `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and `zigux/Makefile` instead of being implied as missing current-`master` surfaces."
)
LEGACY_PHASE2_KCONFIG_SENTENCE = (
    "- `check-phase2-kconfig-readme-alignment.py --self-test` and `check-phase2-kconfig-readme-alignment.py` keep this scripts index honest by requiring the live Phase 2 summary to name `check-phase2-tests-readme-alignment.py`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `zigux/Makefile`, and the Linux-style `phase2-kconfig` route without implying that the older dedicated kconfig bridge checker stack is still present under `scripts/zigux/` on current `master`."
)
REFRESHED_PHASE2_KCONFIG_SENTENCE = (
    "- `check-phase2-kconfig-readme-alignment.py --self-test` and `check-phase2-kconfig-readme-alignment.py` keep this scripts index honest by requiring the live Phase 2 summary to name `check-phase2-tests-readme-alignment.py`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `zigux/Makefile`, and the Linux-style `phase2-kconfig` route while keeping the dedicated kconfig bridge checker packet documented through the shared Phase 2 reminder surface instead of implying that stack is missing on current `master`."
)
PHASE2_TOOL_MANIFEST_SENTENCE = (
    "- `check-phase2-tool-manifest-packets.py --self-test` and `check-phase2-tool-manifest-packets.py` keep the committed `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` packet visible from this scripts index beside `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` instead of letting the shared Phase 2 manifest guard disappear behind the broader closure note."
)
FIXED_REQUIRED_SNIPPETS = (
    "Phase 2 flow - `check-phase2-tests-readme-alignment.py` keeps `zigux/tests/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/Makefile`, and the Linux-style `make -C zigux phase2-validate` plus `make -C zigux phase2` replay surface aligned around the same bounded toolchain packet.",
    PHASE2_TOOL_MANIFEST_SENTENCE,
    CURRENT_PHASE2_LIVE_SENTENCE,
)
REQUIRED_VARIANT_SNIPPETS = {
    "PHASE2_KCONFIG_SUMMARY": (
        LEGACY_PHASE2_KCONFIG_SENTENCE,
        REFRESHED_PHASE2_KCONFIG_SENTENCE,
    ),
}

FORBIDDEN_MARKERS = (
    "`check-phase2-genksyms-bridge-selftest-alignment.py`",
    "`check-kconfig-bridge.py`",
    "`check-mk-elfconfig-diff.py`",
    "`check-genksyms-crc-diff.py`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def collect_issues(readme_text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for snippet in FIXED_REQUIRED_SNIPPETS:
        count = readme_text.count(snippet)
        if count != 1:
            issues.append(("REQUIRED_SNIPPET_COUNT_MISMATCH", f"{snippet}:actual={count}:expected=1"))

    for label, variants in REQUIRED_VARIANT_SNIPPETS.items():
        counts = [readme_text.count(variant) for variant in variants]
        total = sum(counts)
        if total != 1:
            issues.append(("REQUIRED_VARIANT_COUNT_MISMATCH", f"{label}:counts={counts}:expected_total=1"))

    for marker in FORBIDDEN_MARKERS:
        count = readme_text.count(marker)
        if count != 0:
            issues.append(("FORBIDDEN_MARKER_PRESENT", f"{marker}:actual={count}:expected=0"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> None:
    print("PHASE2_KCONFIG_README_ALIGNMENT=fail")
    for code, detail in issues:
        print(f"{code}={detail}")


def build_base_text(*, use_refreshed_variants: bool) -> str:
    kconfig_sentence = REFRESHED_PHASE2_KCONFIG_SENTENCE if use_refreshed_variants else LEGACY_PHASE2_KCONFIG_SENTENCE
    return "\n".join(
        (
            "# scripts/zigux This directory holds Zigux-specific bootstrap and validation helpers.",
            "Initial responsibilities - Zig toolchain policy checks - bootstrap validation - committed parity fixture generation and checking - future ABI/layout guards - artifact diff helpers for host-side tools Current bootstrap helpers - `check-zig-toolchain.py` - `validate-bootstrap.py` - `install-zig.py` - `check-phase1-installer-review-surfaces.py` - `check-phase1-installer-companion-checks.py` - `validate-phase1.py` - `check-phase1-bench.py` - `validate-phase1-closure.py` - `check-phase2-kconfig-readme-alignment.py` - `check-phase2-tests-readme-alignment.py` - `check-phase2-tool-manifest-packets.py` - `check-phase2-fixdep-gate.py` - `check-fixdep-diff.py` - `check-genksyms-bridge.py` - `check-phase2-cross.py` - `check-phase2-cross-selftest-alignment.py` - `check-phase2-kconfig-selftest-alignment.py` - `validate-phase2.py` - `validate-phase2-closure.py` - `check-phase2-toolchain-pin-scope.py` - `validate-phase3.py`",
            *FIXED_REQUIRED_SNIPPETS,
            kconfig_sentence,
            "",
        )
    )


def run_self_test() -> int:
    checks_run = 0
    legacy_text = build_base_text(use_refreshed_variants=False)
    refreshed_text = build_base_text(use_refreshed_variants=True)

    assert collect_issues(legacy_text) == []
    checks_run += 1
    assert collect_issues(refreshed_text) == []
    checks_run += 1

    for snippet in FIXED_REQUIRED_SNIPPETS:
        missing_snippet = legacy_text.replace(snippet, "", 1)
        issues = collect_issues(missing_snippet)
        assert ("REQUIRED_SNIPPET_COUNT_MISMATCH", f"{snippet}:actual=0:expected=1") in issues
        checks_run += 1

    duplicate_live_snippet = legacy_text + "\n" + CURRENT_PHASE2_LIVE_SENTENCE
    issues = collect_issues(duplicate_live_snippet)
    assert ("REQUIRED_SNIPPET_COUNT_MISMATCH", f"{CURRENT_PHASE2_LIVE_SENTENCE}:actual=2:expected=1") in issues
    checks_run += 1

    missing_kconfig_variant = legacy_text.replace(LEGACY_PHASE2_KCONFIG_SENTENCE, "", 1)
    issues = collect_issues(missing_kconfig_variant)
    assert ("REQUIRED_VARIANT_COUNT_MISMATCH", "PHASE2_KCONFIG_SUMMARY:counts=[0, 0]:expected_total=1") in issues
    checks_run += 1

    duplicate_kconfig_variant = legacy_text + "\n" + REFRESHED_PHASE2_KCONFIG_SENTENCE
    issues = collect_issues(duplicate_kconfig_variant)
    assert ("REQUIRED_VARIANT_COUNT_MISMATCH", "PHASE2_KCONFIG_SUMMARY:counts=[1, 1]:expected_total=1") in issues
    checks_run += 1

    for forbidden_marker in FORBIDDEN_MARKERS:
        issues = collect_issues(legacy_text + "\n" + forbidden_marker)
        assert ("FORBIDDEN_MARKER_PRESENT", f"{forbidden_marker}:actual=1:expected=0") in issues
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_readme_alignment_") as tmp_dir_str:
        readme_path = Path(tmp_dir_str) / "README.md"
        readme_path.write_text(refreshed_text, encoding="utf-8")
        issues = collect_issues(read_text(readme_path))
        assert issues == []
        checks_run += 1

    expected_self_test_case_count = 9 + len(FORBIDDEN_MARKERS)
    if checks_run != expected_self_test_case_count:
        print("PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST=fail")
        print(f"PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT_EXPECTED={expected_self_test_case_count}")
        return 1

    print("PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Phase 2 scripts README summary stays aligned with the live toolchain packet.")
    parser.add_argument("--readme", type=Path, default=README, help="Override README path")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage without repo files")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(read_text(args.readme))
    if issues:
        emit_issues(issues)
        return 1

    print("PHASE2_KCONFIG_README_ALIGNMENT=pass")
    print(f"README={args.readme}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
