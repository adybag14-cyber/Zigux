#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import tempfile


SCRIPT_PATH = Path(__file__).resolve()

REQUIRED_FILES = {
    "tests_readme": "zigux/tests/README.md",
    "toolchain_notes": "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "review_checklist": "Documentation/zigux/review-checklist.md",
    "scripts_readme": "scripts/zigux/README.md",
    "phase2_validator": "scripts/zigux/validate-phase2.py",
    "phase2_closure_validator": "scripts/zigux/validate-phase2-closure.py",
    "cross_targets": "zigux/tests/fixtures/phase2_cross_targets.json",
    "makefile": "zigux/Makefile",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
}

TESTS_README_MARKERS = [
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "same three-target compile matrix, direct cross gate, alignment guard, and kbuild-facing replay surface",
]

TOOLCHAIN_NOTES_MARKERS = [
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "x86_64-linux",
    "same kbuild-facing replay surface named by the shared validators, the closure note, and the shared review checklist",
]

REVIEW_CHECKLIST_MARKERS = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
]

SCRIPTS_README_MARKERS = [
    "check-phase2-cross-selftest-alignment.py --self-test",
    "check-phase2-cross-selftest-alignment.py",
    "check-phase2-cross.py --self-test",
    "check-phase2-cross.py",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/review-checklist.md",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "kbuild-facing review path",
]

PHASE2_VALIDATOR_MARKERS = [
    "PHASE2_CROSS_ALIGNMENT_REQUIRED_SOURCE_MARKERS",
    "PHASE2_TESTS_README_REQUIRED_SOURCE_MARKERS",
    "phase2_tests_readme",
    "PHASE2_TESTS_README_ALIGNMENT_CHECKER = (",
]

PHASE2_VALIDATOR_EXACT_COUNTS = {
    'ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"': 1,
    "[sys.executable, str(PHASE2_TESTS_README_ALIGNMENT_CHECKER)],": 1,
}

PHASE2_CLOSURE_VALIDATOR_MARKERS = [
    "check-phase2-toolchain-pin-scope.py --self-test",
    "check-phase2-toolchain-pin-scope.py",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/review-checklist.md",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
    "x86_64-linux",
]

MAKEFILE_MARKERS = [
    "phase2-validate:",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "phase2-cross:",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-cross.py --self-test",
    "scripts/zigux/check-phase2-cross.py",
    "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
]

WORKFLOW_MARKERS = [
    "Self-test Phase 2 cross-target alignment checker",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "Check Phase 2 cross-target alignment",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "Validate Phase 2 fixdep files",
    "python3 scripts/zigux/validate-phase2.py",
    "Self-test Phase 2 tests README alignment checker",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "Check Phase 2 tests README alignment",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "Validate Phase 2 closure",
    "python3 scripts/zigux/validate-phase2-closure.py",
    "Self-test bounded Phase 2 cross-target checker",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "Check bounded Phase 2 cross-target compile",
    "python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
]

WORKFLOW_EXACT_RUN_COUNTS = {
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
}

MAKEFILE_EXACT_RUN_COUNTS = {
    "scripts/zigux/check-phase2-tests-readme-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
}


def repo_root_from_script(script_path: Path) -> Path:
    return script_path.resolve().parents[2]


def resolve_root() -> Path:
    args = sys.argv[1:]
    if "--root" in args:
        index = args.index("--root")
        try:
            return Path(args[index + 1]).resolve()
        except IndexError as exc:
            raise SystemExit("--root requires a path") from exc
    env_root = os.environ.get("ZIGUX_PHASE2_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return repo_root_from_script(SCRIPT_PATH)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate_exact_marker_counts(
    text: str,
    *,
    label: str,
    expected_counts: dict[str, int],
) -> list[str]:
    issues: list[str] = []
    for marker, expected_count in expected_counts.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            issues.append(f"{label}:{marker}:count={actual_count}:expected={expected_count}")
    return issues


def validate_exact_workflow_runs(text: str) -> list[str]:
    issues: list[str] = []
    for command, expected_count in WORKFLOW_EXACT_RUN_COUNTS.items():
        expected_line = f"run: {command}"
        count = sum(1 for line in text.splitlines() if line.strip() == expected_line)
        if count != expected_count:
            issues.append(f"workflow_exact_run:{command}:count={count}:expected={expected_count}")
    return issues


def validate_exact_makefile_runs(text: str) -> list[str]:
    issues: list[str] = []
    stripped_lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in MAKEFILE_EXACT_RUN_COUNTS.items():
        count = sum(1 for line in stripped_lines if line.endswith(command))
        if count != expected_count:
            issues.append(f"makefile_exact_run:{command}:count={count}:expected={expected_count}")
    return issues


def validate(root: Path) -> list[str]:
    missing: list[str] = []
    for label, rel_path in REQUIRED_FILES.items():
        if not (root / rel_path).exists():
            missing.append(f"missing:{label}:{rel_path}")
    if missing:
        return missing

    tests_readme = read_text(root, REQUIRED_FILES["tests_readme"])
    toolchain_notes = read_text(root, REQUIRED_FILES["toolchain_notes"])
    review_checklist = read_text(root, REQUIRED_FILES["review_checklist"])
    scripts_readme = read_text(root, REQUIRED_FILES["scripts_readme"])
    phase2_validator = read_text(root, REQUIRED_FILES["phase2_validator"])
    phase2_closure_validator = read_text(root, REQUIRED_FILES["phase2_closure_validator"])
    makefile = read_text(root, REQUIRED_FILES["makefile"])
    workflow = read_text(root, REQUIRED_FILES["workflow"])

    for marker in TESTS_README_MARKERS:
        if marker not in tests_readme:
            missing.append(f"tests_readme:{marker}")
    for marker in TOOLCHAIN_NOTES_MARKERS:
        if marker not in toolchain_notes:
            missing.append(f"toolchain_notes:{marker}")
    for marker in REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            missing.append(f"review_checklist:{marker}")
    for marker in SCRIPTS_README_MARKERS:
        if marker not in scripts_readme:
            missing.append(f"scripts_readme:{marker}")
    for marker in PHASE2_VALIDATOR_MARKERS:
        if marker not in phase2_validator:
            missing.append(f"phase2_validator:{marker}")
    missing.extend(
        validate_exact_marker_counts(
            phase2_validator,
            label="phase2_validator",
            expected_counts=PHASE2_VALIDATOR_EXACT_COUNTS,
        )
    )
    for marker in PHASE2_CLOSURE_VALIDATOR_MARKERS:
        if marker not in phase2_closure_validator:
            missing.append(f"phase2_closure_validator:{marker}")
    for marker in MAKEFILE_MARKERS:
        if marker not in makefile:
            missing.append(f"makefile:{marker}")
    missing.extend(validate_exact_makefile_runs(makefile))
    for marker in WORKFLOW_MARKERS:
        if marker not in workflow:
            missing.append(f"workflow:{marker}")
    missing.extend(validate_exact_workflow_runs(workflow))

    return missing


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/check-phase2-tests-readme-alignment.py")],
        capture_output=True,
        text=True,
        check=False,
    )


def write_file(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def clone_fixture_root(destination_root: Path) -> None:
    write_file(
        destination_root,
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        SCRIPT_PATH.read_text(encoding="utf-8"),
    )
    write_file(
        destination_root,
        REQUIRED_FILES["tests_readme"],
        "\n".join(
            [
                "# zigux/tests",
                "",
                "- zigux/tests/fixtures/phase2_cross_targets.json",
                "- python3 scripts/zigux/check-phase2-cross.py --self-test",
                "- python3 scripts/zigux/check-phase2-cross.py",
                "- python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
                "- python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
                "- python3 scripts/zigux/validate-phase2.py",
                "- python3 scripts/zigux/validate-phase2-closure.py",
                "- make -C zigux phase2-validate",
                "- `make -C zigux phase2` so the tests root names the same three-target compile matrix, direct cross gate, alignment guard, and kbuild-facing replay surface",
                "",
            ]
        ),
    )
    write_file(
        destination_root,
        REQUIRED_FILES["toolchain_notes"],
        "\n".join(
            [
                "# Phase 2 Toolchain Bootstrap Notes",
                "",
                "- zigux/tests/fixtures/phase2_cross_targets.json",
                "- python3 scripts/zigux/check-phase2-cross.py --self-test",
                "- python3 scripts/zigux/check-phase2-cross.py",
                "- python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
                "- python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
                "- python3 scripts/zigux/validate-phase2.py",
                "- python3 scripts/zigux/validate-phase2-closure.py",
                "- make -C zigux phase2-validate",
                "- make -C zigux phase2",
                "- x86_64-linux",
                "- same kbuild-facing replay surface named by the shared validators, the closure note, and the shared review checklist",
                "",
            ]
        ),
    )
    write_file(
        destination_root,
        REQUIRED_FILES["review_checklist"],
        "\n".join(
            [
                "# Zigux Review Checklist",
                "",
                "- Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
                "- scripts/zigux/zig-toolchain-policy.json",
                "- scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "- zigux/tests/fixtures/phase2_cross_targets.json",
                "- scripts/zigux/check-phase2-cross.py",
                "- scripts/zigux/check-phase2-cross-selftest-alignment.py",
                "- scripts/zigux/validate-phase2.py",
                "- scripts/zigux/validate-phase2-closure.py",
                "- .github/workflows/zigux-bootstrap.yml",
                "- zigux/Makefile",
                "- make -C zigux phase2-validate",
                "- make -C zigux phase2",
                "",
            ]
        ),
    )
    write_file(
        destination_root,
        REQUIRED_FILES["scripts_readme"],
        "\n".join(
            [
                "# scripts/zigux",
                "",
                "- check-phase2-cross-selftest-alignment.py --self-test",
                "- check-phase2-cross-selftest-alignment.py",
                "- check-phase2-cross.py --self-test",
                "- check-phase2-cross.py",
                "- Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
                "- Documentation/zigux/review-checklist.md",
                "- make -C zigux phase2-validate",
                "- make -C zigux phase2",
                "- kbuild-facing review path",
                "",
            ]
        ),
    )
    write_file(
        destination_root,
        REQUIRED_FILES["phase2_validator"],
        "\n".join(
            [
                "PHASE2_CROSS_ALIGNMENT_REQUIRED_SOURCE_MARKERS = []",
                "PHASE2_TESTS_README_REQUIRED_SOURCE_MARKERS = []",
                "phase2_tests_readme = True",
                "PHASE2_TESTS_README_ALIGNMENT_CHECKER = (",
                '    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"',
                ")",
                "subprocess.run(",
                "    [sys.executable, str(PHASE2_TESTS_README_ALIGNMENT_CHECKER)],",
                ")",
                "",
            ]
        ),
    )
    write_file(
        destination_root,
        REQUIRED_FILES["phase2_closure_validator"],
        "\n".join(
            [
                "required_toolchain_notes_markers = [",
                "    'scripts/zigux/zig-toolchain-policy.json',",
                "    'check-phase2-toolchain-pin-scope.py --self-test',",
                "    'check-phase2-toolchain-pin-scope.py',",
                "    'Documentation/zigux/phase2-toolchain-bootstrap-notes.md',",
                "    'Documentation/zigux/review-checklist.md',",
                "    'make -C zigux phase2-validate',",
                "    'make -C zigux phase2',",
                "    'x86_64-linux',",
                "]",
                "required_readme_markers = [",
                "    'Documentation/zigux/phase2-toolchain-bootstrap-notes.md',",
                "    'Documentation/zigux/review-checklist.md',",
                "    'make -C zigux phase2-validate',",
                "    'make -C zigux phase2',",
                "    'kbuild-facing review path',",
                "]",
                "required_workflow_markers = [",
                "    'python3 scripts/zigux/validate-phase2.py',",
                "    'python3 scripts/zigux/validate-phase2-closure.py',",
                "]",
                "",
            ]
        ),
    )
    write_file(destination_root, REQUIRED_FILES["cross_targets"], '{"targets":["x86_64-linux-musl"]}\n')
    write_file(
        destination_root,
        REQUIRED_FILES["makefile"],
        "\n".join(
            [
                "phase2-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
                "phase2-cross:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross-selftest-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
                "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
                "",
            ]
        ),
    )
    write_file(
        destination_root,
        REQUIRED_FILES["workflow"],
        "\n".join(
            [
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Validate Phase 2 fixdep files",
                "        run: python3 scripts/zigux/validate-phase2.py",
                "      - name: Self-test Phase 2 cross-target alignment checker",
                "        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
                "      - name: Check Phase 2 cross-target alignment",
                "        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
                "      - name: Self-test Phase 2 tests README alignment checker",
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
                "      - name: Check Phase 2 tests README alignment",
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
                "      - name: Validate Phase 2 closure",
                "        run: python3 scripts/zigux/validate-phase2-closure.py",
                "  phase2-cross:",
                "    steps:",
                "      - name: Self-test bounded Phase 2 cross-target checker",
                "        run: python3 scripts/zigux/check-phase2-cross.py --self-test",
                "      - name: Check bounded Phase 2 cross-target compile",
                "        run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
                "",
            ]
        ),
    )


def expect_missing(label: str, root: Path, needle: str) -> None:
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"phase2-tests-readme-self-test:{label}:unexpected_pass")
    if needle not in result.stdout:
        actual = result.stdout.strip() or "none"
        raise SystemExit(
            f"phase2-tests-readme-self-test:{label}:expected:{needle}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tests_readme_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        baseline = run_validator(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase2-tests-readme-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        tests_readme_path = tmp_root / REQUIRED_FILES["tests_readme"]
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- zigux/tests/fixtures/phase2_cross_targets.json\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_cross_targets",
            tmp_root,
            "tests_readme:zigux/tests/fixtures/phase2_cross_targets.json",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "- python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_cross_alignment_self_test",
            tmp_root,
            "tests_readme:python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "`make -C zigux phase2`",
                "`make -C zigux phase2-removed`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "tests_readme_phase2_make",
            tmp_root,
            "tests_readme:make -C zigux phase2",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        toolchain_notes_path = tmp_root / REQUIRED_FILES["toolchain_notes"]
        original_toolchain_notes = toolchain_notes_path.read_text(encoding="utf-8")
        toolchain_notes_path.write_text(
            original_toolchain_notes.replace("- x86_64-linux\n", "", 1),
            encoding="utf-8",
        )
        expect_missing("toolchain_notes_pin", tmp_root, "toolchain_notes:x86_64-linux")
        toolchain_notes_path.write_text(original_toolchain_notes, encoding="utf-8")

        toolchain_notes_path.write_text(
            original_toolchain_notes.replace(
                "- same kbuild-facing replay surface named by the shared validators, the closure note, and the shared review checklist\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "toolchain_notes_replay_surface",
            tmp_root,
            "toolchain_notes:same kbuild-facing replay surface named by the shared validators, the closure note, and the shared review checklist",
        )
        toolchain_notes_path.write_text(original_toolchain_notes, encoding="utf-8")

        review_checklist_path = tmp_root / REQUIRED_FILES["review_checklist"]
        original_review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(
            original_review_checklist.replace("- scripts/zigux/check-phase2-cross-selftest-alignment.py\n", "", 1),
            encoding="utf-8",
        )
        expect_missing(
            "review_checklist_cross_alignment",
            tmp_root,
            "review_checklist:scripts/zigux/check-phase2-cross-selftest-alignment.py",
        )
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        scripts_readme_path = tmp_root / REQUIRED_FILES["scripts_readme"]
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace("- kbuild-facing review path\n", "", 1),
            encoding="utf-8",
        )
        expect_missing(
            "scripts_readme_kbuild_path",
            tmp_root,
            "scripts_readme:kbuild-facing review path",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        phase2_validator_path = tmp_root / REQUIRED_FILES["phase2_validator"]
        original_phase2_validator = phase2_validator_path.read_text(encoding="utf-8")
        phase2_validator_path.write_text(
            original_phase2_validator.replace(
                '    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"\n',
                '    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment-missing.py"\n',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "phase2_validator_checker_path",
            tmp_root,
            'phase2_validator:ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"',
        )
        phase2_validator_path.write_text(original_phase2_validator, encoding="utf-8")

        phase2_validator_path.write_text(
            original_phase2_validator.replace(
                "    [sys.executable, str(PHASE2_TESTS_README_ALIGNMENT_CHECKER)],\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "phase2_validator_checker_run",
            tmp_root,
            "phase2_validator:[sys.executable, str(PHASE2_TESTS_README_ALIGNMENT_CHECKER)],",
        )
        phase2_validator_path.write_text(original_phase2_validator, encoding="utf-8")

        phase2_validator_path.write_text(
            original_phase2_validator.replace(
                '    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"\n',
                '    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"\n'
                '    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"\n',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "phase2_validator_checker_path_duplicate",
            tmp_root,
            'phase2_validator:ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py":count=2:expected=1',
        )
        phase2_validator_path.write_text(original_phase2_validator, encoding="utf-8")

        phase2_validator_path.write_text(
            original_phase2_validator.replace(
                "    [sys.executable, str(PHASE2_TESTS_README_ALIGNMENT_CHECKER)],\n",
                "    [sys.executable, str(PHASE2_TESTS_README_ALIGNMENT_CHECKER)],\n"
                "    [sys.executable, str(PHASE2_TESTS_README_ALIGNMENT_CHECKER)],\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "phase2_validator_checker_run_duplicate",
            tmp_root,
            "phase2_validator:[sys.executable, str(PHASE2_TESTS_README_ALIGNMENT_CHECKER)],:count=2:expected=1",
        )
        phase2_validator_path.write_text(original_phase2_validator, encoding="utf-8")

        phase2_closure_validator_path = tmp_root / REQUIRED_FILES["phase2_closure_validator"]
        original_phase2_closure_validator = phase2_closure_validator_path.read_text(encoding="utf-8")
        phase2_closure_validator_path.write_text(
            original_phase2_closure_validator.replace("    'check-phase2-toolchain-pin-scope.py --self-test',\n", "", 1),
            encoding="utf-8",
        )
        expect_missing(
            "phase2_closure_validator_toolchain_pin_self_test",
            tmp_root,
            "phase2_closure_validator:check-phase2-toolchain-pin-scope.py --self-test",
        )
        phase2_closure_validator_path.write_text(original_phase2_closure_validator, encoding="utf-8")

        phase2_closure_validator_path.write_text(
            original_phase2_closure_validator.replace("    'make -C zigux phase2-validate',\n", "", 1),
            encoding="utf-8",
        )
        expect_missing(
            "phase2_closure_validator_make_validate",
            tmp_root,
            "phase2_closure_validator:make -C zigux phase2-validate",
        )
        phase2_closure_validator_path.write_text(original_phase2_closure_validator, encoding="utf-8")

        phase2_closure_validator_path.write_text(
            original_phase2_closure_validator.replace("    'x86_64-linux',\n", "", 1),
            encoding="utf-8",
        )
        expect_missing(
            "phase2_closure_validator_pin_target",
            tmp_root,
            "phase2_closure_validator:x86_64-linux",
        )
        phase2_closure_validator_path.write_text(original_phase2_closure_validator, encoding="utf-8")

        makefile_path = tmp_root / REQUIRED_FILES["makefile"]
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_tests_readme_self_test",
            tmp_root,
            "makefile:scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_tests_readme_gate",
            tmp_root,
            "makefile:scripts/zigux/check-phase2-tests-readme-alignment.py",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_tests_readme_self_test_duplicate",
            tmp_root,
            "makefile_exact_run:scripts/zigux/check-phase2-tests-readme-alignment.py --self-test:count=2:expected=1",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "makefile_tests_readme_gate_duplicate",
            tmp_root,
            "makefile_exact_run:scripts/zigux/check-phase2-tests-readme-alignment.py:count=2:expected=1",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace("phase2-cross:\n", "", 1),
            encoding="utf-8",
        )
        expect_missing("makefile_phase2_cross", tmp_root, "makefile:phase2-cross:")
        makefile_path.write_text(original_makefile, encoding="utf-8")

        workflow_path = tmp_root / REQUIRED_FILES["workflow"]
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Self-test Phase 2 tests README alignment checker\n"
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_tests_readme_self_test",
            tmp_root,
            "workflow:Self-test Phase 2 tests README alignment checker",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Check Phase 2 tests README alignment\n"
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_tests_readme_gate",
            tmp_root,
            "workflow:Check Phase 2 tests README alignment",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Self-test Phase 2 tests README alignment checker\n"
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test\n",
                "      - name: Self-test Phase 2 tests README alignment checker\n"
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test\n"
                "      - name: Self-test Phase 2 tests README alignment checker\n"
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_tests_readme_self_test_duplicate",
            tmp_root,
            "workflow_exact_run:python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test:count=2:expected=1",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Check Phase 2 tests README alignment\n"
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\n",
                "      - name: Check Phase 2 tests README alignment\n"
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\n"
                "      - name: Check Phase 2 tests README alignment\n"
                "        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_tests_readme_gate_duplicate",
            tmp_root,
            "workflow_exact_run:python3 scripts/zigux/check-phase2-tests-readme-alignment.py:count=2:expected=1",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Check Phase 2 cross-target alignment\n"
                "        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing(
            "workflow_cross_alignment",
            tmp_root,
            "workflow:Check Phase 2 cross-target alignment",
        )

    print("PHASE2_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print("PHASE2_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=24")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


ROOT = resolve_root()
problems = validate(ROOT)
if problems:
    print("PHASE2_TESTS_README_ALIGNMENT=fail")
    print("PHASE2_TESTS_README_ALIGNMENT_MISSING_START")
    for problem in problems:
        print(problem)
    print("PHASE2_TESTS_README_ALIGNMENT_MISSING_END")
    raise SystemExit(1)

print("PHASE2_TESTS_README_ALIGNMENT=pass")
print(f"PHASE2_TESTS_README_ALIGNMENT_ROOT={ROOT}")