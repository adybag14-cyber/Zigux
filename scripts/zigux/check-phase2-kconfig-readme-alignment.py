#!/usr/bin/env python3

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
README = ROOT / "README.md"

CURRENT_BOOTSTRAP_HELPERS_SNIPPET = (
    " - `check-phase2-kconfig-readme-alignment.py` - `check-phase2-tests-readme-alignment.py` "
    "- `check-phase2-tool-manifest-packets.py` - `check-phase2-fixdep-gate.py` "
    "- `check-fixdep-diff.py` - `check-genksyms-bridge.py` - `check-phase2-cross.py` "
    "- `check-phase2-cross-selftest-alignment.py` - `check-phase2-kconfig-selftest-alignment.py` "
    "- `validate-phase2.py` - `validate-phase2-closure.py` "
    "- `check-phase2-toolchain-pin-scope.py` - `validate-phase3.py`"
)
CURRENT_PHASE2_LIVE_SENTENCE = (
    "- `check-zig-toolchain.py`, `install-zig.py`, `validate-phase2.py`, "
    "`validate-phase2-closure.py`, `check-phase2-toolchain-pin-scope.py`, "
    "`check-phase2-tests-readme-alignment.py`, `check-phase2-kconfig-readme-alignment.py`, "
    "`check-phase2-tool-manifest-packets.py`, `check-phase2-fixdep-gate.py`, "
    "`check-fixdep-diff.py`, `check-genksyms-bridge.py`, `check-phase2-cross.py`, "
    "`check-phase2-cross-selftest-alignment.py`, and `check-phase2-kconfig-selftest-alignment.py` "
    "are the live shared scripts-root Phase 2 helpers on current `master`; the broader "
    "`phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, "
    "and `phase2` route inventory plus the dedicated fixdep, genksyms, manifest, cross-target, "
    "and bridge checker packet should stay documented through "
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, "
    "`Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and `zigux/Makefile` "
    "instead of being implied as missing current-`master` surfaces."
)
CURRENT_PHASE2_KCONFIG_SENTENCE = (
    "- `check-phase2-kconfig-readme-alignment.py --self-test` and "
    "`check-phase2-kconfig-readme-alignment.py` keep this scripts index honest by requiring the "
    "live Phase 2 summary to name `check-phase2-tests-readme-alignment.py`, "
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, "
    "`Documentation/zigux/phase2-closure.md`, `zigux/Makefile`, and the Linux-style "
    "`phase2-kconfig` route while keeping the dedicated kconfig bridge checker packet "
    "documented through the shared Phase 2 reminder surface instead of implying that stack is "
    "missing on current `master`."
)
PHASE2_TESTS_ALIGNMENT_SENTENCE = (
    "Phase 2 flow - `check-phase2-tests-readme-alignment.py` keeps `zigux/tests/README.md`, "
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, "
    "`scripts/zigux/README.md`, `zigux/Makefile`, and the Linux-style `make -C zigux phase2-validate` "
    "plus `make -C zigux phase2` replay surface aligned around the same bounded toolchain packet."
)
PHASE2_TOOL_MANIFEST_SENTENCE = (
    "- `check-phase2-tool-manifest-packets.py --self-test` and `check-phase2-tool-manifest-packets.py` "
    "keep the committed `zigux/tests/fixtures/phase2_tool_manifest.json`, "
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, "
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and "
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` packet visible from this scripts "
    "index beside `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, "
    "and `zigux/tests/README.md` instead of letting the shared Phase 2 manifest guard disappear "
    "behind the broader closure note."
)

LEGACY_BOOTSTRAP_HELPERS_SNIPPET = (
    " - `check-phase2-kconfig-readme-alignment.py` - `check-phase2-tests-readme-alignment.py` "
    "- `validate-phase3.py`"
)
LEGACY_PHASE2_LIVE_SENTENCE = (
    "- `check-zig-toolchain.py`, `install-zig.py`, `check-phase2-tests-readme-alignment.py`, and "
    "`check-phase2-kconfig-readme-alignment.py` are the live scripts-root Phase 2 helpers on current "
    "`master`; the broader `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, "
    "`phase2-cross`, and `phase2` route inventory should stay documented through "
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, "
    "`zigux/tests/README.md`, and `zigux/Makefile` until the missing dedicated validator, manifest, "
    "cross-target, pin-scope, and bridge scripts return to the tree."
)
LEGACY_PHASE2_KCONFIG_SENTENCE = (
    "- `check-phase2-kconfig-readme-alignment.py --self-test` and "
    "`check-phase2-kconfig-readme-alignment.py` keep this scripts index honest by requiring the live "
    "Phase 2 summary to name `check-phase2-tests-readme-alignment.py`, "
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, "
    "`zigux/Makefile`, and the Linux-style `phase2-kconfig` route without implying that the older "
    "dedicated kconfig bridge checker stack is still present under `scripts/zigux/` on current `master`."
)

REQUIRED_SNIPPETS = (
    CURRENT_BOOTSTRAP_HELPERS_SNIPPET,
    CURRENT_PHASE2_LIVE_SENTENCE,
    CURRENT_PHASE2_KCONFIG_SENTENCE,
    PHASE2_TESTS_ALIGNMENT_SENTENCE,
    PHASE2_TOOL_MANIFEST_SENTENCE,
)

FORBIDDEN_MARKERS = (
    LEGACY_BOOTSTRAP_HELPERS_SNIPPET,
    LEGACY_PHASE2_LIVE_SENTENCE,
    LEGACY_PHASE2_KCONFIG_SENTENCE,
    "`check-phase2-genksyms-bridge-selftest-alignment.py`",
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

    for snippet in REQUIRED_SNIPPETS:
        count = readme_text.count(snippet)
        if count != 1:
            issues.append(("REQUIRED_SNIPPET_COUNT_MISMATCH", f"{snippet}:actual={count}:expected=1"))

    for marker in FORBIDDEN_MARKERS:
        count = readme_text.count(marker)
        if count != 0:
            issues.append(("FORBIDDEN_MARKER_PRESENT", f"{marker}:actual={count}:expected=0"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> None:
    print("PHASE2_KCONFIG_README_ALIGNMENT=fail")
    for code, detail in issues:
        print(f"{code}={detail}")


def build_base_text() -> str:
    return "\n".join(
        (
            "# scripts/zigux This directory holds Zigux-specific bootstrap and validation helpers.",
            "Initial responsibilities - Zig toolchain policy checks - bootstrap validation - committed parity fixture generation and checking - future ABI/layout guards - artifact diff helpers for host-side tools Current bootstrap helpers - `check-zig-toolchain.py` - `validate-bootstrap.py` - `install-zig.py` - `check-phase1-installer-review-surfaces.py` - `check-phase1-installer-companion-checks.py` - `validate-phase1.py` - `check-phase1-bench.py` - `validate-phase1-closure.py`" + CURRENT_BOOTSTRAP_HELPERS_SNIPPET,
            PHASE2_TESTS_ALIGNMENT_SENTENCE,
            PHASE2_TOOL_MANIFEST_SENTENCE,
            CURRENT_PHASE2_KCONFIG_SENTENCE,
            CURRENT_PHASE2_LIVE_SENTENCE,
            "",
        )
    )


def run_self_test() -> int:
    checks_run = 0
    current_text = build_base_text()

    assert collect_issues(current_text) == []
    checks_run += 1

    issues = collect_issues(current_text + "\n`check-kconfig-bridge.py`\n")
    assert issues == []
    checks_run += 1

    for snippet in REQUIRED_SNIPPETS:
        issues = collect_issues(current_text.replace(snippet, "", 1))
        assert ("REQUIRED_SNIPPET_COUNT_MISMATCH", f"{snippet}:actual=0:expected=1") in issues
        checks_run += 1

        issues = collect_issues(current_text.replace(snippet, snippet + "\n" + snippet, 1))
        assert ("REQUIRED_SNIPPET_COUNT_MISMATCH", f"{snippet}:actual=2:expected=1") in issues
        checks_run += 1

    for forbidden_marker in FORBIDDEN_MARKERS:
        issues = collect_issues(current_text + "\n" + forbidden_marker)
        assert ("FORBIDDEN_MARKER_PRESENT", f"{forbidden_marker}:actual=1:expected=0") in issues
        checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_readme_alignment_") as tmp_dir_str:
        readme_path = Path(tmp_dir_str) / "README.md"
        readme_path.write_text(current_text, encoding="utf-8")
        issues = collect_issues(read_text(readme_path))
        assert issues == []
        checks_run += 1

    expected_self_test_case_count = 3 + (2 * len(REQUIRED_SNIPPETS)) + len(FORBIDDEN_MARKERS)
    if checks_run != expected_self_test_case_count:
        print("PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST=fail")
        print(f"PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(
            "PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT_EXPECTED="
            f"{expected_self_test_case_count}"
        )
        return 1

    print("PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 2 scripts README summary stays aligned with the live toolchain packet."
    )
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
