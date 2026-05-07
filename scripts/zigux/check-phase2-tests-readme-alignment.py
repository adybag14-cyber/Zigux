#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
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
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
]

DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
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
    "make -C zigux phase2",
]

REVIEW_CHECKLIST_MARKERS = [
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "make -C zigux phase2-validate",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2",
]

TOOLCHAIN_NOTES_MARKERS = [
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/check-genksyms-crc-diff.py",
    "- shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`",
    "- shared kconfig selftest-alignment guard: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`",
    "- shared kconfig bridge parity gate: `python3 scripts/zigux/check-kconfig-bridge.py`",
    "- shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`",
    "- shared tool-manifest packet guard: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "- `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test` and `python3 scripts/zigux/check-phase2-tool-manifest-packets.py` keep this bootstrap note aligned with `zigux/tests/fixtures/phase2_tool_manifest.json`, the dedicated `fixdep`, `genksyms`, `kconfig`, and `confdata` packet links it pins, and the Linux-style `make -C zigux phase2-validate` route instead of leaving that manifest-backed Phase 2 packet implied only by the closure note and shared validator`",
    "zig test scripts/zigux/genksyms_crc.zig",
    "zig test scripts/zigux/kconfig/conf_bridge.zig",
    "zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "make -C zigux phase2-validate",
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
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-genksyms-crc-diff.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "zig test scripts/zigux/genksyms_crc.zig",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "x86_64-linux",
    "three-target compile matrix",
    "kbuild-facing replay surface",
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
    },
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md": {
        "python3 scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
        "python3 scripts/zigux/check-genksyms-crc-diff.py": 1,
        "- shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`": 1,
        "- shared kconfig selftest-alignment guard: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`": 1,
        "- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`": 1,
        "- shared kconfig bridge parity gate: `python3 scripts/zigux/check-kconfig-bridge.py`": 1,
        "- shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`": 1,
        "- shared tool-manifest packet guard: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`": 1,
        "- `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test` and `python3 scripts/zigux/check-phase2-tool-manifest-packets.py` keep this bootstrap note aligned with `zigux/tests/fixtures/phase2_tool_manifest.json`, the dedicated `fixdep`, `genksyms`, `kconfig`, and `confdata` packet links it pins, and the Linux-style `make -C zigux phase2-validate` route instead of leaving that manifest-backed Phase 2 packet implied only by the closure note and shared validator`": 1,
        "zig test scripts/zigux/genksyms_crc.zig": 1,
        "zig test scripts/zigux/kconfig/conf_bridge.zig": 1,
        "zig test scripts/zigux/kconfig/confdata_bridge.zig": 1,
        "python3 scripts/zigux/validate-phase2.py": 1,
        "python3 scripts/zigux/validate-phase2-closure.py": 1,
        "make -C zigux phase2-validate": 1,
        "make -C zigux phase2": 1,
    },
    "Documentation/zigux/review-checklist.md": {
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
        "make -C zigux phase2-kconfig": 1,
    },
    "scripts/zigux/README.md": {
        "check-phase2-genksyms-bridge-selftest-alignment.py": 1,
        "check-phase2-kconfig-selftest-alignment.py": 1,
        "check-phase2-tool-manifest-packets.py": 1,
    },
    "zigux/tests/README.md": {
        "make -C zigux phase2-validate": 1,
        "make -C zigux phase2": 1,
        "scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
        "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py": 1,
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
        "scripts/zigux/check-genksyms-crc-diff.py": 1,
        "zig test scripts/zigux/genksyms_crc.zig": 1,
    },
    "zigux/Makefile": {
        "check-phase2-tests-readme-alignment.py": 1,
        "check-phase2-tool-manifest-packets.py": 1,
        "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross": 1,
    },
}

def collect_missing_markers(text: str, markers: list[str], *, prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def collect_exact_count_issues(text: str, checks: dict[str, int], *, prefix: str) -> list[str]:
    issues: list[str] = []
    for marker, expected_count in checks.items():
        pattern = rf"(?<![A-Za-z0-9_.-]){re.escape(marker)}(?![A-Za-z0-9_.-])"
        count = len(re.findall(pattern, text))
        if count != expected_count:
            issues.append(f"{prefix}:exact_count:{marker}:count={count}:expected={expected_count}")
    return issues


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")

    if issues:
        return issues

    docs_root = (root / "Documentation/zigux/README.md").read_text(encoding="utf-8")
    toolchain_notes = (root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md").read_text(
        encoding="utf-8"
    )
    review = (root / "Documentation/zigux/review-checklist.md").read_text(encoding="utf-8")
    scripts_readme = (root / "scripts/zigux/README.md").read_text(encoding="utf-8")
    tests_readme = (root / "zigux/tests/README.md").read_text(encoding="utf-8")
    makefile = (root / "zigux/Makefile").read_text(encoding="utf-8")
    issues.extend(collect_missing_markers(docs_root, DOCS_ROOT_MARKERS, prefix="docs_root"))
    issues.extend(
        collect_exact_count_issues(
            docs_root,
            EXACT_COUNT_CHECKS["Documentation/zigux/README.md"],
            prefix="docs_root",
        )
    )
    issues.extend(collect_missing_markers(toolchain_notes, TOOLCHAIN_NOTES_MARKERS, prefix="toolchain_notes"))
    issues.extend(
        collect_exact_count_issues(
            toolchain_notes,
            EXACT_COUNT_CHECKS["Documentation/zigux/phase2-toolchain-bootstrap-notes.md"],
            prefix="toolchain_notes",
        )
    )
    issues.extend(collect_missing_markers(review, REVIEW_CHECKLIST_MARKERS, prefix="review_checklist"))
    issues.extend(
        collect_exact_count_issues(
            review,
            EXACT_COUNT_CHECKS["Documentation/zigux/review-checklist.md"],
            prefix="review_checklist",
        )
    )
    issues.extend(collect_missing_markers(scripts_readme, SCRIPTS_README_MARKERS, prefix="scripts_readme"))
    issues.extend(
        collect_exact_count_issues(
            scripts_readme,
            EXACT_COUNT_CHECKS["scripts/zigux/README.md"],
            prefix="scripts_readme",
        )
    )
    issues.extend(collect_missing_markers(tests_readme, TESTS_README_MARKERS, prefix="tests_readme"))
    issues.extend(collect_missing_markers(makefile, MAKEFILE_MARKERS, prefix="makefile"))
    issues.extend(
        collect_exact_count_issues(
            tests_readme,
            EXACT_COUNT_CHECKS["zigux/tests/README.md"],
            prefix="tests_readme",
        )
    )
    issues.extend(
        collect_exact_count_issues(
            makefile,
            EXACT_COUNT_CHECKS["zigux/Makefile"],
            prefix="makefile",
        )
    )
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_docs_root_text(markers: list[str]) -> str:
    rendered: list[str] = []
    for marker in markers:
        if marker in (
            "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
            "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        ):
            rendered.append(f"`{marker}`")
        else:
            rendered.append(marker)
    return "\n".join(rendered) + "\n"


def build_self_test_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        write_text(root / rel, "")

    write_text(
        root / "Documentation/zigux/README.md",
        render_docs_root_text(DOCS_ROOT_MARKERS),
    )
    write_text(
        root / "Documentation/zigux/review-checklist.md",
        "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
    )
    write_text(
        root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "\n".join(TOOLCHAIN_NOTES_MARKERS) + "\n",
    )
    write_text(
        root / "scripts/zigux/README.md",
        "\n".join(SCRIPTS_README_MARKERS) + "\n",
    )
    write_text(
        root / "zigux/tests/README.md",
        "\n".join(TESTS_README_MARKERS) + "\n",
    )
    write_text(
        root / "zigux/Makefile",
        "\n".join(MAKEFILE_MARKERS) + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase2_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)

        assert validate_root(root) == []

        write_text(
            root / "Documentation/zigux/README.md",
            render_docs_root_text(
                [
                    marker
                    for marker in DOCS_ROOT_MARKERS
                    if marker != "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test"
                ]
            ),
        )
        issues = validate_root(root)
        assert "docs_root:python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/README.md",
            render_docs_root_text(
                [
                    marker
                    for marker in DOCS_ROOT_MARKERS
                    if marker != "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py"
                ]
            ),
        )
        issues = validate_root(root)
        assert (
            "docs_root:exact_count:`python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`:count=0:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/README.md",
            render_docs_root_text(DOCS_ROOT_MARKERS)
            + "`python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`\n",
        )
        issues = validate_root(root)
        assert (
            "docs_root:exact_count:`python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/README.md",
            render_docs_root_text(DOCS_ROOT_MARKERS)
            + "`python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`\n",
        )
        issues = validate_root(root)
        assert (
            "docs_root:exact_count:`python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/review-checklist.md",
            "\n".join(
                marker
                for marker in REVIEW_CHECKLIST_MARKERS
                if marker != "scripts/zigux/check-phase2-kconfig-selftest-alignment.py"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "review_checklist:scripts/zigux/check-phase2-kconfig-selftest-alignment.py" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/review-checklist.md",
            "\n".join(REVIEW_CHECKLIST_MARKERS)
            + "\nscripts/zigux/check-phase2-kconfig-selftest-alignment.py\n",
        )
        issues = validate_root(root)
        assert (
            "review_checklist:exact_count:scripts/zigux/check-phase2-kconfig-selftest-alignment.py:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/review-checklist.md",
            "\n".join(
                marker
                for marker in REVIEW_CHECKLIST_MARKERS
                if marker != "make -C zigux phase2-kconfig"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "review_checklist:make -C zigux phase2-kconfig" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/review-checklist.md",
            "\n".join(REVIEW_CHECKLIST_MARKERS)
            + "\nmake -C zigux phase2-kconfig\n",
        )
        issues = validate_root(root)
        assert (
            "review_checklist:exact_count:make -C zigux phase2-kconfig:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(
                marker
                for marker in TOOLCHAIN_NOTES_MARKERS
                if marker != "python3 scripts/zigux/check-genksyms-crc-diff.py"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "toolchain_notes:python3 scripts/zigux/check-genksyms-crc-diff.py" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(TOOLCHAIN_NOTES_MARKERS)
            + "\npython3 scripts/zigux/check-genksyms-crc-diff.py\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:exact_count:python3 scripts/zigux/check-genksyms-crc-diff.py:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(
                marker
                for marker in TOOLCHAIN_NOTES_MARKERS
                if marker != "- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(TOOLCHAIN_NOTES_MARKERS)
            + "\n- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:exact_count:- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(
                marker
                for marker in TOOLCHAIN_NOTES_MARKERS
                if marker != "- shared kconfig bridge parity gate: `python3 scripts/zigux/check-kconfig-bridge.py`"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:- shared kconfig bridge parity gate: `python3 scripts/zigux/check-kconfig-bridge.py`"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(TOOLCHAIN_NOTES_MARKERS)
            + "\n- shared kconfig bridge parity gate: `python3 scripts/zigux/check-kconfig-bridge.py`\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:exact_count:- shared kconfig bridge parity gate: `python3 scripts/zigux/check-kconfig-bridge.py`:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(
                marker
                for marker in TOOLCHAIN_NOTES_MARKERS
                if marker != "zig test scripts/zigux/genksyms_crc.zig"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "toolchain_notes:zig test scripts/zigux/genksyms_crc.zig" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(TOOLCHAIN_NOTES_MARKERS)
            + "\nzig test scripts/zigux/genksyms_crc.zig\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:exact_count:zig test scripts/zigux/genksyms_crc.zig:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(
                marker
                for marker in TOOLCHAIN_NOTES_MARKERS
                if marker != "zig test scripts/zigux/kconfig/conf_bridge.zig"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "toolchain_notes:zig test scripts/zigux/kconfig/conf_bridge.zig" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(TOOLCHAIN_NOTES_MARKERS)
            + "\nzig test scripts/zigux/kconfig/conf_bridge.zig\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:exact_count:zig test scripts/zigux/kconfig/conf_bridge.zig:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(
                marker
                for marker in TOOLCHAIN_NOTES_MARKERS
                if marker != "zig test scripts/zigux/kconfig/confdata_bridge.zig"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "toolchain_notes:zig test scripts/zigux/kconfig/confdata_bridge.zig" in issues

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(TOOLCHAIN_NOTES_MARKERS)
            + "\nzig test scripts/zigux/kconfig/confdata_bridge.zig\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:exact_count:zig test scripts/zigux/kconfig/confdata_bridge.zig:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(
                marker
                for marker in TOOLCHAIN_NOTES_MARKERS
                if marker != "- shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:- shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(TOOLCHAIN_NOTES_MARKERS)
            + "\n- shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:exact_count:- shared tool-manifest packet self-test: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test`:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(
                marker
                for marker in TOOLCHAIN_NOTES_MARKERS
                if marker != "- shared tool-manifest packet guard: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:- shared tool-manifest packet guard: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(TOOLCHAIN_NOTES_MARKERS)
            + "\n- shared tool-manifest packet guard: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:exact_count:- shared tool-manifest packet guard: `python3 scripts/zigux/check-phase2-tool-manifest-packets.py`:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(
                marker
                for marker in TOOLCHAIN_NOTES_MARKERS
                if marker != "- `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test` and `python3 scripts/zigux/check-phase2-tool-manifest-packets.py` keep this bootstrap note aligned with `zigux/tests/fixtures/phase2_tool_manifest.json`, the dedicated `fixdep`, `genksyms`, `kconfig`, and `confdata` packet links it pins, and the Linux-style `make -C zigux phase2-validate` route instead of leaving that manifest-backed Phase 2 packet implied only by the closure note and shared validator`"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:- `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test` and `python3 scripts/zigux/check-phase2-tool-manifest-packets.py` keep this bootstrap note aligned with `zigux/tests/fixtures/phase2_tool_manifest.json`, the dedicated `fixdep`, `genksyms`, `kconfig`, and `confdata` packet links it pins, and the Linux-style `make -C zigux phase2-validate` route instead of leaving that manifest-backed Phase 2 packet implied only by the closure note and shared validator`"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            "\n".join(TOOLCHAIN_NOTES_MARKERS)
            + "\n- `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test` and `python3 scripts/zigux/check-phase2-tool-manifest-packets.py` keep this bootstrap note aligned with `zigux/tests/fixtures/phase2_tool_manifest.json`, the dedicated `fixdep`, `genksyms`, `kconfig`, and `confdata` packet links it pins, and the Linux-style `make -C zigux phase2-validate` route instead of leaving that manifest-backed Phase 2 packet implied only by the closure note and shared validator`\n",
        )
        issues = validate_root(root)
        assert (
            "toolchain_notes:exact_count:- `python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test` and `python3 scripts/zigux/check-phase2-tool-manifest-packets.py` keep this bootstrap note aligned with `zigux/tests/fixtures/phase2_tool_manifest.json`, the dedicated `fixdep`, `genksyms`, `kconfig`, and `confdata` packet links it pins, and the Linux-style `make -C zigux phase2-validate` route instead of leaving that manifest-backed Phase 2 packet implied only by the closure note and shared validator`:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/README.md",
            "\n".join(
                marker
                for marker in SCRIPTS_README_MARKERS
                if marker != "check-phase2-genksyms-bridge-selftest-alignment.py"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "scripts_readme:check-phase2-genksyms-bridge-selftest-alignment.py" in issues

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/README.md",
            "\n".join(SCRIPTS_README_MARKERS)
            + "\ncheck-phase2-genksyms-bridge-selftest-alignment.py\n",
        )
        issues = validate_root(root)
        assert (
            "scripts_readme:exact_count:check-phase2-genksyms-bridge-selftest-alignment.py:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/README.md",
            "\n".join(
                marker
                for marker in SCRIPTS_README_MARKERS
                if marker != "check-phase2-tool-manifest-packets.py"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "scripts_readme:check-phase2-tool-manifest-packets.py" in issues

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/README.md",
            "\n".join(SCRIPTS_README_MARKERS)
            + "\ncheck-phase2-tool-manifest-packets.py\n",
        )
        issues = validate_root(root)
        assert (
            "scripts_readme:exact_count:check-phase2-tool-manifest-packets.py:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        (root / "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py" in issues

        build_self_test_root(root)
        (root / "scripts/zigux/check-genksyms-crc-diff.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/check-genksyms-crc-diff.py" in issues

        build_self_test_root(root)
        (root / "scripts/zigux/check-phase2-tool-manifest-packets.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/check-phase2-tool-manifest-packets.py" in issues

        build_self_test_root(root)
        (root / "zigux/tests/fixtures/phase2_tool_manifest.json").unlink()
        issues = validate_root(root)
        assert "missing_file:zigux/tests/fixtures/phase2_tool_manifest.json" in issues

        build_self_test_root(root)
        (root / "scripts/zigux/genksyms_crc.zig").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/genksyms_crc.zig" in issues

        build_self_test_root(root)
        (root / "scripts/zigux/check-kconfig-bridge.py").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/check-kconfig-bridge.py" in issues

        build_self_test_root(root)
        (root / "scripts/zigux/kconfig/conf_bridge.zig").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/kconfig/conf_bridge.zig" in issues

        build_self_test_root(root)
        (root / "scripts/zigux/kconfig/confdata_bridge.zig").unlink()
        issues = validate_root(root)
        assert "missing_file:scripts/zigux/kconfig/confdata_bridge.zig" in issues

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/README.md",
            "\n".join(
                marker
                for marker in SCRIPTS_README_MARKERS
                if marker != "check-phase2-kconfig-selftest-alignment.py"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "scripts_readme:check-phase2-kconfig-selftest-alignment.py" in issues

        build_self_test_root(root)
        write_text(
            root / "scripts/zigux/README.md",
            "\n".join(SCRIPTS_README_MARKERS)
            + "\ncheck-phase2-kconfig-selftest-alignment.py\n",
        )
        issues = validate_root(root)
        assert (
            "scripts_readme:exact_count:check-phase2-kconfig-selftest-alignment.py:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(
                marker
                for marker in TESTS_README_MARKERS
                if marker != "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "tests_readme:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py" in issues

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(TESTS_README_MARKERS)
            + "\nscripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py\n",
        )
        issues = validate_root(root)
        assert (
            "tests_readme:exact_count:scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(
                marker
                for marker in TESTS_README_MARKERS
                if marker != "scripts/zigux/check-phase2-kconfig-selftest-alignment.py"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "tests_readme:scripts/zigux/check-phase2-kconfig-selftest-alignment.py" in issues

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(TESTS_README_MARKERS)
            + "\nscripts/zigux/check-phase2-kconfig-selftest-alignment.py\n",
        )
        issues = validate_root(root)
        assert (
            "tests_readme:exact_count:scripts/zigux/check-phase2-kconfig-selftest-alignment.py:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(
                marker
                for marker in TESTS_README_MARKERS
                if marker != "scripts/zigux/check-genksyms-crc-diff.py"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "tests_readme:scripts/zigux/check-genksyms-crc-diff.py" in issues

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(TESTS_README_MARKERS)
            + "\nscripts/zigux/check-genksyms-crc-diff.py\n",
        )
        issues = validate_root(root)
        assert (
            "tests_readme:exact_count:scripts/zigux/check-genksyms-crc-diff.py:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(
                marker
                for marker in TESTS_README_MARKERS
                if marker != "zig test scripts/zigux/genksyms_crc.zig"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "tests_readme:zig test scripts/zigux/genksyms_crc.zig" in issues

        build_self_test_root(root)
        write_text(
            root / "zigux/tests/README.md",
            "\n".join(TESTS_README_MARKERS)
            + "\nzig test scripts/zigux/genksyms_crc.zig\n",
        )
        issues = validate_root(root)
        assert (
            "tests_readme:exact_count:zig test scripts/zigux/genksyms_crc.zig:count=2:expected=1"
            in issues
        )

        build_self_test_root(root)
        write_text(
            root / "zigux/Makefile",
            "\n".join(
                marker
                for marker in MAKEFILE_MARKERS
                if marker != "check-phase2-tool-manifest-packets.py"
            )
            + "\n",
        )
        issues = validate_root(root)
        assert "makefile:check-phase2-tool-manifest-packets.py" in issues

        build_self_test_root(root)
        write_text(
            root / "zigux/Makefile",
            "\n".join(MAKEFILE_MARKERS)
            + "\ncheck-phase2-tool-manifest-packets.py\n",
        )
        issues = validate_root(root)
        assert (
            "makefile:exact_count:check-phase2-tool-manifest-packets.py:count=2:expected=1"
            in issues
        )

    print("PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print("PHASE2_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=73")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Phase 2 shared docs, review, and Makefile alignment.")
    parser.add_argument(
        "--self-test", action="store_true", help="Run built-in alignment coverage without a repo checkout."
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

    print("PHASE2_TESTS_README_ALIGNMENT=pass")
    print(
        "PHASE2_TESTS_README_ALIGNMENT_MARKER_COUNT="
        f"{len(DOCS_ROOT_MARKERS) + len(TOOLCHAIN_NOTES_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
