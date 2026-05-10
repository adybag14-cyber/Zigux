#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-genksyms-crc-diff.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/check-mk-elfconfig-diff.py",
    "scripts/zigux/mk_elfconfig.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
]

DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2",
]

REVIEW_CHECKLIST_MARKERS = [
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2",
]

TOOLCHAIN_NOTES_MARKERS = [
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "python3 scripts/zigux/check-fixdep-diff.py",
    "python3 scripts/zigux/check-genksyms-crc-diff.py",
    "- shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`",
    "- shared kconfig selftest-alignment guard: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`",
    "- shared kconfig bridge parity gate: `python3 scripts/zigux/check-kconfig-bridge.py`",
    "- shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`",
    "- shared tool-manifest packet guard: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "- `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test` and `python3 scripts/zigux/check-phase2-tool-manifest-packets.py` keep this bootstrap note aligned with `zigux/tests/fixtures/phase2_tool_manifest.json`, the dedicated `fixdep`, `genksyms`, `artifact_tools` (`genksyms_crc` plus `mk_elfconfig`), `kconfig`, and `confdata` packet links it pins, `.github/workflows/zigux-bootstrap.yml`, and the Linux-style `make -C zigux phase2-validate` route instead of leaving that manifest-backed Phase 2 packet implied only by the closure note and shared validator",
    "zig test scripts/zigux/genksyms_crc.zig",
    "zig test scripts/zigux/kconfig/conf_bridge.zig",
    "zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2",
]

SCRIPTS_README_MARKERS = [
    "check-zig-toolchain.py",
    "install-zig.py",
    "check-phase2-genksyms-bridge-selftest-alignment.py",
    "check-phase2-tests-readme-alignment.py",
    "check-phase2-cross-selftest-alignment.py",
    "check-phase2-kconfig-selftest-alignment.py",
    "check-phase2-toolchain-pin-scope.py",
    "check-phase2-tool-manifest-packets.py",
    "validate-phase2.py",
    "validate-phase2-closure.py",
    "check-phase2-cross.py",
    "check-mk-elfconfig-diff.py",
]

TESTS_README_MARKERS = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-genksyms-crc-diff.py",
    "scripts/zigux/check-mk-elfconfig-diff.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "zig test scripts/zigux/fixdep.zig",
    "zig test scripts/zigux/genksyms.zig",
    "zig test scripts/zigux/genksyms_crc.zig",
    "zig test scripts/zigux/kconfig/conf_bridge.zig",
    "zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "zig test scripts/zigux/mk_elfconfig.zig",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "x86_64-linux",
    "three-target compile matrix",
    "the shipped genksyms bridge direct replay",
    "the shipped direct kconfig bridge replays",
    "the shipped direct `mk_elfconfig` replay",
    "kbuild-facing replay surface",
    "the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset",
]

MAKEFILE_MARKERS = [
    "phase2-validate:",
    "check-phase2-tests-readme-alignment.py",
    "check-phase2-tool-manifest-packets.py",
    "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
]

EXACT_COUNT_CHECKS = {
    "Documentation/zigux/README.md": {
        "`python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`": 1,
        "`python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`": 1,
        "scripts/zigux/check-phase2-tool-manifest-packets.py": 1,
    },
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md": {
        "- shared tests README alignment self-test: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`": 1,
        "- shared tests README alignment gate: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`": 1,
        "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test": 1,
        "python3 scripts/zigux/check-phase2-fixdep-gate.py": 2,
        "python3 scripts/zigux/check-fixdep-diff.py --self-test": 1,
        "python3 scripts/zigux/check-fixdep-diff.py": 2,
        "python3 scripts/zigux/check-genksyms-crc-diff.py": 1,
        "- shared mk_elfconfig parity self-test: `python3 scripts/zigux/check-mk-elfconfig-diff.py --self-test`": 1,
        "- shared mk_elfconfig parity gate: `python3 scripts/zigux/check-mk-elfconfig-diff.py`": 1,
        "zig test scripts/zigux/mk_elfconfig.zig": 1,
        "- shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`": 1,
        "- shared kconfig selftest-alignment guard: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`": 1,
        "- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`": 1,
        "- shared kconfig bridge parity gate: `python3 scripts/zigux/check-kconfig-bridge.py`": 1,
        "- shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`": 1,
        "- shared tool-manifest packet guard: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`": 1,
        "- the shared tests README alignment self-test and gate keep this dedicated bootstrap note aligned with `zigux/tests/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/Makefile`, and the Linux-style `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, and `make -C zigux phase2` replay surface instead of leaving this note coupled to the broader Phase 2 packet by implication alone": 1,
        "- `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test` and `python3 scripts/zigux/check-phase2-tool-manifest-packets.py` keep this bootstrap note aligned with `zigux/tests/fixtures/phase2_tool_manifest.json`, the dedicated `fixdep`, `genksyms`, `artifact_tools` (`genksyms_crc` plus `mk_elfconfig`), `kconfig`, and `confdata` packet links it pins, `.github/workflows/zigux-bootstrap.yml`, and the Linux-style `make -C zigux phase2-validate` route instead of leaving that manifest-backed Phase 2 packet implied only by the closure note and shared validator": 1,
        "zig test scripts/zigux/genksyms_crc.zig": 1,
        "zig test scripts/zigux/kconfig/conf_bridge.zig": 1,
        "zig test scripts/zigux/kconfig/confdata_bridge.zig": 1,
        "the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin": 1,
        "python3 scripts/zigux/validate-phase2.py": 1,
        "python3 scripts/zigux/validate-phase2-closure.py": 1,
        "make -C zigux phase2-toolchain": 2,
        "make -C zigux phase2-validate": 3,
        "make -C zigux phase2-tools": 2,
        "make -C zigux phase2-kconfig": 2,
        "make -C zigux phase2-cross": 2,
        "make -C zigux phase2": 2,
    },
    "Documentation/zigux/review-checklist.md": {
        "zigux/tests/fixtures/phase2_tool_manifest.json": 1,
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json": 1,
        "scripts/zigux/check-phase2-fixdep-gate.py": 1,
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
        "scripts/zigux/check-phase2-tool-manifest-packets.py": 1,
        "the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset": 1,
        "make -C zigux phase2-tools": 1,
        "make -C zigux phase2-kconfig": 1,
        "make -C zigux phase2-cross": 1,
    },
    "scripts/zigux/README.md": {
        "check-phase2-genksyms-bridge-selftest-alignment.py": 1,
        "check-phase2-kconfig-selftest-alignment.py": 1,
        "check-phase2-tool-manifest-packets.py": 1,
    },
    "zigux/tests/README.md": {
        "make -C zigux phase2-validate": 1,
        "make -C zigux phase2": 1,
        "scripts/zigux/check-phase2-fixdep-gate.py": 1,
        "scripts/zigux/check-fixdep-diff.py": 1,
        "scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
        "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
        "scripts/zigux/check-genksyms-bridge.py": 1,
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
        "scripts/zigux/check-kconfig-bridge.py": 1,
        "scripts/zigux/check-phase2-tool-manifest-packets.py": 1,
        "scripts/zigux/check-genksyms-crc-diff.py": 1,
        "scripts/zigux/check-mk-elfconfig-diff.py": 1,
        "zigux/tests/fixtures/phase2_tool_manifest.json": 1,
        "zigux/tests/fixtures/phase2_artifact_tools_manifest.json": 1,
        "zig test scripts/zigux/fixdep.zig": 1,
        "zig test scripts/zigux/genksyms.zig": 1,
        "zig test scripts/zigux/genksyms_crc.zig": 1,
        "zig test scripts/zigux/kconfig/conf_bridge.zig": 1,
        "zig test scripts/zigux/kconfig/confdata_bridge.zig": 1,
        "zig test scripts/zigux/mk_elfconfig.zig": 1,
        "the shipped genksyms bridge direct replay": 1,
        "the shipped direct kconfig bridge replays": 1,
        "the shipped direct `mk_elfconfig` replay": 1,
        "the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` routes when `ZIG` is unset": 1,
    },
    "zigux/Makefile": {
        "check-phase2-tests-readme-alignment.py": 2,
        "check-phase2-tool-manifest-packets.py": 1,
        "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross": 1,
    },
}

FILE_MARKERS = {
    "Documentation/zigux/README.md": DOCS_ROOT_MARKERS,
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md": TOOLCHAIN_NOTES_MARKERS,
    "Documentation/zigux/review-checklist.md": REVIEW_CHECKLIST_MARKERS,
    "scripts/zigux/README.md": SCRIPTS_README_MARKERS,
    "zigux/tests/README.md": TESTS_README_MARKERS,
    "zigux/Makefile": MAKEFILE_MARKERS,
}

MISSING_FILE_CASES = [
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-genksyms-crc-diff.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-mk-elfconfig-diff.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/mk_elfconfig.zig",
]


def count_occurrences(text: str, marker: str) -> int:
    pattern = rf"(?<![A-Za-z0-9_.-]){re.escape(marker)}(?![A-Za-z0-9_.-])"
    return len(re.findall(pattern, text))


def collect_missing_markers(text: str, markers: list[str], *, prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def collect_exact_count_issues(text: str, checks: dict[str, int], *, prefix: str) -> list[str]:
    issues: list[str] = []
    for marker, expected_count in checks.items():
        count = count_occurrences(text, marker)
        if count != expected_count:
            issues.append(f"{prefix}:exact_count:{marker}:count={count}:expected={expected_count}")
    return issues


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            issues.append(f"missing_file:{rel_path}")
    if issues:
        return issues

    for rel_path, markers in FILE_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        issues.extend(collect_missing_markers(text, markers, prefix=rel_path))
        exact_checks = EXACT_COUNT_CHECKS.get(rel_path)
        if exact_checks:
            issues.extend(collect_exact_count_issues(text, exact_checks, prefix=rel_path))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_docs_root_text(markers: list[str]) -> str:
    rendered: list[str] = []
    quoted = {
        "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
        "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    }
    for marker in markers:
        rendered.append(f"`{marker}`" if marker in quoted else marker)
    return "\n".join(rendered) + "\n"


def render_marker_text_for_self_test(rel_path: str, markers: list[str]) -> str:
    if rel_path == "Documentation/zigux/README.md":
        return render_docs_root_text(markers)

    rendered = list(markers)
    exact_checks = EXACT_COUNT_CHECKS.get(rel_path, {})
    for marker, expected_count in exact_checks.items():
        current_count = count_occurrences("\n".join(rendered), marker)
        if expected_count > current_count:
            rendered.extend([marker] * (expected_count - current_count))
    return "\n".join(rendered) + "\n"


def build_self_test_root(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, "")
    for rel_path, markers in FILE_MARKERS.items():
        write_text(root / rel_path, render_marker_text_for_self_test(rel_path, markers))


def remove_marker_once(text: str, marker: str) -> str:
    needle = marker + "\n"
    if needle in text:
        return text.replace(needle, "", 1)
    return text.replace(marker, "", 1)


def duplicate_marker(text: str, marker: str) -> str:
    return text + marker + "\n"


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert validate_root(root) == []
        case_count += 1

        for rel_path, checks in EXACT_COUNT_CHECKS.items():
            for marker in checks:
                build_self_test_root(root)
                path = root / rel_path
                original = path.read_text(encoding="utf-8")
                path.write_text(remove_marker_once(original, marker), encoding="utf-8")
                issues = validate_root(root)
                assert f"{rel_path}:exact_count:{marker}:count={checks[marker] - 1}:expected={checks[marker]}" in issues
                case_count += 1

                build_self_test_root(root)
                path = root / rel_path
                original = path.read_text(encoding="utf-8")
                path.write_text(duplicate_marker(original, marker), encoding="utf-8")
                issues = validate_root(root)
                assert f"{rel_path}:exact_count:{marker}:count={checks[marker] + 1}:expected={checks[marker]}" in issues
                case_count += 1

        for rel_path in MISSING_FILE_CASES:
            build_self_test_root(root)
            (root / rel_path).unlink()
            issues = validate_root(root)
            assert f"missing_file:{rel_path}" in issues
            case_count += 1

    expected_case_count = 1 + 2 * sum(len(checks) for checks in EXACT_COUNT_CHECKS.values()) + len(MISSING_FILE_CASES)
    assert case_count == expected_case_count
    print("PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Phase 2 shared docs, review, and Makefile alignment.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in alignment coverage without a repo checkout.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(ROOT)
    if issues:
        print("PHASE2_TESTS_README_ALIGNMENT=fail")
        print("PHASE2_TESTS_README_ALIGNMENT_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_TESTS_README_ALIGNMENT_ISSUES_END")
        return 1

    marker_count = sum(len(markers) for markers in FILE_MARKERS.values())
    print("PHASE2_TESTS_README_ALIGNMENT=pass")
    print(f"PHASE2_TESTS_README_ALIGNMENT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
