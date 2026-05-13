#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

FALLBACK_REMINDER = (
    "the repo-local `.zig-toolchain` fallback reused by the Linux-style `phase2-toolchain`, "
    "`phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` "
    "routes when `ZIG` is unset"
)
DOCS_ROOT_PHASE2_REVIEWER_GUARDS_CLAUSE = (
    "including the shipped `scripts/zigux/check-phase2-kconfig-readme-alignment.py` and "
    "`scripts/zigux/check-phase2-tool-manifest-packets.py` reviewer-surface guards"
)
SCRIPTS_PHASE2_LIVE_SENTENCE = (
    "`check-zig-toolchain.py`, `install-zig.py`, `validate-phase2.py`, "
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
SCRIPTS_PHASE2_ALIGNMENT_SENTENCE = (
    "Phase 2 flow - `check-phase2-tests-readme-alignment.py` keeps `zigux/tests/README.md`, "
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, "
    "`scripts/zigux/README.md`, `zigux/Makefile`, and the Linux-style `make -C zigux phase2-validate` "
    "plus `make -C zigux phase2` replay surface aligned around the same bounded toolchain packet."
)
SCRIPTS_PHASE2_KCONFIG_SENTENCE = (
    "`check-phase2-kconfig-readme-alignment.py --self-test` and "
    "`check-phase2-kconfig-readme-alignment.py` keep this scripts index honest by requiring the "
    "live Phase 2 summary to name `check-phase2-tests-readme-alignment.py`, "
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, "
    "`Documentation/zigux/phase2-closure.md`, `zigux/Makefile`, and the Linux-style "
    "`phase2-kconfig` route while keeping the dedicated kconfig bridge checker packet "
    "documented through the shared Phase 2 reminder surface instead of implying that stack is "
    "missing on current `master`."
)
TESTS_README_GENKSYMS_PACKET_SENTENCE = (
    "keep the shipped genksyms bridge direct replay visible in the tests root through the "
    "committed fixture packet instead of reviving a direct tests-root replay command"
)

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-readme-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
]

FILE_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
        "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
        "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test",
        "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py",
        "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
        "run: python3 scripts/zigux/check-kconfig-bridge.py",
        "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
        "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
        "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
        "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
        "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "make -C zigux phase2-cross",
        "repo-local `.zig-toolchain` fallback reused by those Linux-style Phase 2 routes when `ZIG` is unset",
        DOCS_ROOT_PHASE2_REVIEWER_GUARDS_CLAUSE,
        "The broader Phase 2 fixdep, genksyms, kconfig bridge, artifact-tools, manifest, cross-target, and closure-route inventory should stay documented through `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and `zigux/Makefile`",
    ],
    "Documentation/zigux/phase2-closure.md": [
        "PHASE2_LINUX_STYLE_ROUTE_COUNT=6",
        FALLBACK_REMINDER,
        "shared tests README alignment self-test: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`",
        "shared tests README alignment gate: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`",
        "shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`",
        "Linux-style routes: `make -C zigux phase2-toolchain`, `make -C zigux phase2-validate`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, and `make -C zigux phase2`",
    ],
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md": [
        "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
        "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
        "PHASE2_LINUX_STYLE_ROUTE_COUNT=6",
        "make -C zigux phase2-cross",
        "the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin",
        FALLBACK_REMINDER,
    ],
    "Documentation/zigux/review-checklist.md": [
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "scripts/zigux/check-phase2-kconfig-readme-alignment.py",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-genksyms-bridge.py",
        FALLBACK_REMINDER,
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-fixdep-gate.py",
    ],
    "scripts/zigux/README.md": [
        "check-zig-toolchain.py",
        "install-zig.py",
        "check-phase2-kconfig-readme-alignment.py",
        "check-phase2-tests-readme-alignment.py",
        SCRIPTS_PHASE2_LIVE_SENTENCE,
        SCRIPTS_PHASE2_ALIGNMENT_SENTENCE,
        SCRIPTS_PHASE2_KCONFIG_SENTENCE,
    ],
    "zigux/tests/README.md": [
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/review-checklist.md",
        "scripts/zigux/README.md",
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "scripts/zigux/check-phase2-kconfig-readme-alignment.py",
        "scripts/zigux/check-phase2-tool-manifest-packets.py",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "scripts/zigux/check-genksyms-bridge.py",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "python3 scripts/zigux/install-zig.py --self-test",
        "python3 scripts/zigux/check-zig-toolchain.py --self-test",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
        FALLBACK_REMINDER,
        "zig test scripts/zigux/fixdep.zig",
    ],
    "zigux/Makefile": [
        "phase2-toolchain:",
        "phase2-tools:",
        "phase2-kconfig:",
        "phase2-validate:",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
        "scripts/zigux/check-phase2-toolchain-pin-scope.py",
        "scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "phase2-cross:",
        "phase2: phase2-validate phase2-cross",
    ],
}

FORBIDDEN_FILE_MARKERS = {
    "Documentation/zigux/README.md": [
        "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-genksyms-crc-diff.py",
        "scripts/zigux/check-mk-elfconfig-diff.py",
    ],
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md": [
        "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-genksyms-crc-diff.py",
        "scripts/zigux/check-mk-elfconfig-diff.py",
    ],
    "Documentation/zigux/review-checklist.md": [
        "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
        "scripts/zigux/genksyms_crc.zig",
        "scripts/zigux/mk_elfconfig.zig",
    ],
    "scripts/zigux/README.md": [
        "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-genksyms-crc-diff.py",
        "scripts/zigux/check-mk-elfconfig-diff.py",
    ],
    "zigux/tests/README.md": [
        "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
        "scripts/zigux/check-genksyms-crc-diff.py",
        "scripts/zigux/check-mk-elfconfig-diff.py",
        "zig test scripts/zigux/genksyms_crc.zig",
        "zig test scripts/zigux/kconfig/conf_bridge.zig",
        "zig test scripts/zigux/kconfig/confdata_bridge.zig",
        "zig test scripts/zigux/mk_elfconfig.zig",
    ],
}

EXACT_COUNT_CHECKS = {
    "Documentation/zigux/README.md": {
        DOCS_ROOT_PHASE2_REVIEWER_GUARDS_CLAUSE: 1,
    },
    "Documentation/zigux/review-checklist.md": {
        FALLBACK_REMINDER: 1,
        "scripts/zigux/check-phase2-kconfig-readme-alignment.py": 1,
        "scripts/zigux/check-kconfig-bridge.py": 1,
        "scripts/zigux/check-genksyms-bridge.py": 1,
    },
    "scripts/zigux/README.md": {
        SCRIPTS_PHASE2_LIVE_SENTENCE: 1,
        SCRIPTS_PHASE2_ALIGNMENT_SENTENCE: 1,
        SCRIPTS_PHASE2_KCONFIG_SENTENCE: 1,
    },
    "zigux/tests/README.md": {
        FALLBACK_REMINDER: 1,
        "make -C zigux phase2-validate": 1,
        "make -C zigux phase2": 1,
        "scripts/zigux/check-phase2-kconfig-readme-alignment.py": 1,
        "scripts/zigux/check-phase2-tool-manifest-packets.py": 1,
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
        "scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
        "scripts/zigux/check-genksyms-bridge.py": 1,
        "scripts/zigux/check-kconfig-bridge.py": 1,
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json": 1,
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json": 1,
        "scripts/zigux/kconfig/conf_bridge.zig": 1,
        "scripts/zigux/kconfig/confdata_bridge.zig": 1,
        TESTS_README_GENKSYMS_PACKET_SENTENCE: 1,
    },
    "zigux/Makefile": {
        "phase2-tools:": 1,
        "phase2-kconfig:": 1,
        "phase2: phase2-validate phase2-cross": 1,
    },
}

LINE_EXACT_COUNT_CHECKS = {
    ".github/workflows/zigux-bootstrap.yml": {
        "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test": 1,
        "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
        "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test": 1,
        "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py": 1,
        "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test": 1,
        "run: python3 scripts/zigux/check-kconfig-bridge.py": 1,
    },
    "zigux/Makefile": {
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test": 1,
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test": 1,
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py": 1,
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test": 1,
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py": 1,
    },
}

MISSING_FILE_CASES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-kconfig-readme-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/Makefile",
]


def count_occurrences(text: str, marker: str) -> int:
    pattern = rf"(?<![A-Za-z0-9_.-]){re.escape(marker)}(?![A-Za-z0-9_.-])"
    return len(re.findall(pattern, text))


def collect_missing_markers(text: str, markers: list[str], *, prefix: str) -> list[str]:
    return [f"{prefix}:missing:{marker}" for marker in markers if marker not in text]


def collect_forbidden_marker_issues(text: str, markers: list[str], *, prefix: str) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = count_occurrences(text, marker)
        if count != 0:
            issues.append(f"{prefix}:forbidden:{marker}:count={count}:expected=0")
    return issues


def collect_exact_count_issues(text: str, checks: dict[str, int], *, prefix: str) -> list[str]:
    issues: list[str] = []
    for marker, expected in checks.items():
        count = count_occurrences(text, marker)
        if count != expected:
            issues.append(f"{prefix}:exact_count:{marker}:count={count}:expected={expected}")
    return issues


def collect_line_exact_count_issues(text: str, checks: dict[str, int], *, prefix: str) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    for marker, expected in checks.items():
        count = sum(1 for line in lines if line == marker or line.strip() == marker)
        if count != expected:
            issues.append(f"{prefix}:line_exact_count:{marker}:count={count}:expected={expected}")
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
        if rel_path in FORBIDDEN_FILE_MARKERS:
            issues.extend(
                collect_forbidden_marker_issues(
                    text,
                    FORBIDDEN_FILE_MARKERS[rel_path],
                    prefix=rel_path,
                )
            )
        if rel_path in EXACT_COUNT_CHECKS:
            issues.extend(collect_exact_count_issues(text, EXACT_COUNT_CHECKS[rel_path], prefix=rel_path))
        if rel_path in LINE_EXACT_COUNT_CHECKS:
            issues.extend(collect_line_exact_count_issues(text, LINE_EXACT_COUNT_CHECKS[rel_path], prefix=rel_path))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_file_text(rel_path: str) -> str:
    if rel_path == ".github/workflows/zigux-bootstrap.yml":
        return "\n".join([f"        {marker}" for marker in FILE_MARKERS[rel_path]] + [""])

    if rel_path == "zigux/Makefile":
        return "\n".join(
            [
                "PYTHON ?= python3",
                "ZIGUX_ROOT := /tmp/zigux-root",
                "phase2-toolchain:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "phase2-tools: phase2-toolchain",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
                "phase2-kconfig: phase2-toolchain",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
                "phase2-validate: phase2-tools phase2-kconfig",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
                "phase2-cross: phase2-toolchain",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
                "phase2: phase2-validate phase2-cross",
                "",
            ]
        )

    markers = list(FILE_MARKERS.get(rel_path, []))
    exact_checks = EXACT_COUNT_CHECKS.get(rel_path, {})
    for marker, expected in exact_checks.items():
        current = count_occurrences("\n".join(markers), marker)
        if current < expected:
            markers.extend([marker] * (expected - current))
    if not markers:
        return "placeholder\n"
    return "\n".join(markers) + "\n"


def build_self_test_root(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, render_file_text(rel_path))


def remove_marker_once(text: str, marker: str) -> str:
    needle = marker + "\n"
    if needle in text:
        return text.replace(needle, "", 1)
    return text.replace(marker, "", 1)


def duplicate_marker(text: str, marker: str) -> str:
    return text + marker + "\n"


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_tests_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert validate_root(root) == []
        case_count += 1

        for rel_path, markers in FILE_MARKERS.items():
            build_self_test_root(root)
            path = root / rel_path
            original = path.read_text(encoding="utf-8")
            marker = next((candidate for candidate in markers if original.count(candidate) == 1), markers[0])
            path.write_text(remove_marker_once(original, marker), encoding="utf-8")
            issues = validate_root(root)
            assert f"{rel_path}:missing:{marker}" in issues
            case_count += 1

        build_self_test_root(root)
        path = root / "zigux/tests/README.md"
        original = path.read_text(encoding="utf-8")
        marker = "scripts/zigux/check-phase2-kconfig-readme-alignment.py"
        path.write_text(remove_marker_once(original, marker), encoding="utf-8")
        issues = validate_root(root)
        assert f"zigux/tests/README.md:missing:{marker}" in issues
        case_count += 1

        for rel_path, checks in EXACT_COUNT_CHECKS.items():
            for marker, expected in checks.items():
                build_self_test_root(root)
                path = root / rel_path
                original = path.read_text(encoding="utf-8")
                path.write_text(remove_marker_once(original, marker), encoding="utf-8")
                issues = validate_root(root)
                assert f"{rel_path}:exact_count:{marker}:count={expected - 1}:expected={expected}" in issues
                case_count += 1

                build_self_test_root(root)
                path = root / rel_path
                original = path.read_text(encoding="utf-8")
                path.write_text(duplicate_marker(original, marker), encoding="utf-8")
                issues = validate_root(root)
                assert f"{rel_path}:exact_count:{marker}:count={expected + 1}:expected={expected}" in issues
                case_count += 1

        for rel_path, checks in LINE_EXACT_COUNT_CHECKS.items():
            for marker, expected in checks.items():
                build_self_test_root(root)
                path = root / rel_path
                original = path.read_text(encoding="utf-8")
                path.write_text(remove_marker_once(original, marker), encoding="utf-8")
                issues = validate_root(root)
                assert f"{rel_path}:line_exact_count:{marker}:count={expected - 1}:expected={expected}" in issues
                case_count += 1

                build_self_test_root(root)
                path = root / rel_path
                original = path.read_text(encoding="utf-8")
                path.write_text(duplicate_marker(original, marker), encoding="utf-8")
                issues = validate_root(root)
                assert f"{rel_path}:line_exact_count:{marker}:count={expected + 1}:expected={expected}" in issues
                case_count += 1

        for rel_path, markers in FORBIDDEN_FILE_MARKERS.items():
            for marker in markers:
                build_self_test_root(root)
                path = root / rel_path
                original = path.read_text(encoding="utf-8")
                path.write_text(duplicate_marker(original, marker), encoding="utf-8")
                issues = validate_root(root)
                assert f"{rel_path}:forbidden:{marker}:count=1:expected=0" in issues
                case_count += 1

        for rel_path in MISSING_FILE_CASES:
            build_self_test_root(root)
            (root / rel_path).unlink()
            issues = validate_root(root)
            assert f"missing_file:{rel_path}" in issues
            case_count += 1

    expected_case_count = (
        1
        + len(FILE_MARKERS)
        + 1
        + 2 * sum(len(checks) for checks in EXACT_COUNT_CHECKS.values())
        + 2 * sum(len(checks) for checks in LINE_EXACT_COUNT_CHECKS.values())
        + sum(len(markers) for markers in FORBIDDEN_FILE_MARKERS.values())
        + len(MISSING_FILE_CASES)
    )
    assert case_count == expected_case_count
    print("PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 2 shared reminder packet stays aligned with the live docs, scripts, tests, workflow, and Makefile surfaces."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in coverage without a repo checkout.")
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
