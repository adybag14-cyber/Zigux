#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / "scripts" / "zigux" / "validate-phase7.py",
    ROOT / "scripts" / "zigux" / "check-phase7-build-inventory.py",
    ROOT / "scripts" / "zigux" / "check-phase7-make-wrapper.py",
    ROOT / "scripts" / "zigux" / "check-phase7-cmdline-parity.py",
    ROOT / "scripts" / "zigux" / "check-phase7-argv-split-packet.py",
    ROOT / "scripts" / "zigux" / "check-phase7-argv-split-parity.py",
    ROOT / "scripts" / "zigux" / "check-phase7-rbtree-parity.py",
    ROOT / "scripts" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "review-checklist.md",
    ROOT / "Documentation" / "zigux" / "phase7-string-helpers-slice.md",
    ROOT / "Documentation" / "zigux" / "phase7-cmdline-slice.md",
    ROOT / "Documentation" / "zigux" / "phase7-argv-split-slice.md",
    ROOT / "Documentation" / "zigux" / "phase7-rbtree-slice.md",
    ROOT / "zigux" / "Makefile",
    ROOT / "zigux" / "tests" / "README.md",
    ROOT / "zigux" / "tests" / "phase7_build.zig",
    ROOT / "zigux" / "tests" / "phase7_string_helpers.zig",
    ROOT / "zigux" / "tests" / "phase7_string_helpers_survey.zig",
    ROOT / "zigux" / "tests" / "phase7_string_helpers_sample_boundary.zig",
    ROOT / "zigux" / "tests" / "phase7_string_helpers_manifest.json",
    ROOT / "zigux" / "tests" / "phase7_cmdline.zig",
    ROOT / "zigux" / "tests" / "phase7_cmdline_survey.zig",
    ROOT / "zigux" / "tests" / "phase7_cmdline_manifest.json",
    ROOT / "zigux" / "tests" / "phase7_argv_split.zig",
    ROOT / "zigux" / "tests" / "phase7_argv_split_survey.zig",
    ROOT / "zigux" / "tests" / "phase7_argv_split_manifest.json",
    ROOT / "zigux" / "tests" / "phase7_rbtree.zig",
    ROOT / "zigux" / "tests" / "phase7_rbtree_survey.zig",
    ROOT / "zigux" / "tests" / "phase7_rbtree_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_build_inventory.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_string_helpers_escape_vectors.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_cmdline_next_arg_vectors.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_cmdline.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_cmdline_c_harness.c",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split_c_harness.c",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_rbtree.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_rbtree_c_harness.c",
    ROOT / "lib" / "string_helpers.zig",
    ROOT / "lib" / "cmdline.zig",
    ROOT / "lib" / "argv_split.zig",
    ROOT / "lib" / "rbtree.zig",
    ROOT / "samples" / "zigux" / "README.md",
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
]

expected_make_expansions = {
    "phase7-validate": [
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        "python3 scripts/zigux/check-phase7-build-inventory.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
        "python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-parity.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
    ],
    "phase7-test": [
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
    "phase7": [
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        "python3 scripts/zigux/check-phase7-build-inventory.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
        "python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-parity.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
}

unexpected_make_expansions = {
    "phase7-validate": [
        "zig build test --build-file zigux/tests/build.zig",
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
    "phase7-test": [
        "python3 scripts/zigux/validate-phase7.py --self-test",
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        "python3 scripts/zigux/check-phase7-build-inventory.py",
        "python3 scripts/zigux/check-phase7-make-wrapper.py --self-test",
        "python3 scripts/zigux/check-phase7-make-wrapper.py",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-cmdline-parity.py",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-packet.py",
        "python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-argv-split-parity.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "zig build test --build-file zigux/tests/build.zig",
    ],
    "phase7": [
        "zig build test --build-file zigux/tests/build.zig",
    ],
}

required_make_markers = [
    "phase7-validate:",
    "phase7-test:",
    "phase7: phase7-validate phase7-test",
    *expected_make_expansions["phase7-validate"],
    *expected_make_expansions["phase7-test"],
]
required_workflow_markers = [
    "Self-test Phase 7 runtime validator",
    "Validate Phase 7 runtime helper gates",
    "Run Phase 7 runtime helper tests",
]
required_script_readme_markers = [
    "`validate-phase7.py`",
    "`check-phase7-build-inventory.py`",
    "`check-phase7-make-wrapper.py`",
    "`check-phase7-cmdline-parity.py`",
    "`check-phase7-argv-split-packet.py`",
    "`check-phase7-argv-split-parity.py`",
    "`check-phase7-rbtree-parity.py`",
]
required_script_readme_exact_count_markers = {
    "- `check-phase7-argv-split-packet.py`": 1,
}
required_tests_readme_markers = [
    "`zigux/tests/phase7_build.zig`",
    "`zigux/tests/fixtures/phase7_build_inventory.json`",
    "`scripts/zigux/validate-phase7.py`",
    "`scripts/zigux/check-phase7-build-inventory.py`",
    "`scripts/zigux/check-phase7-make-wrapper.py`",
    "`scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
    "`scripts/zigux/check-phase7-argv-split-packet.py`",
    "`scripts/zigux/check-phase7-cmdline-parity.py --self-test`",
    "`scripts/zigux/check-phase7-cmdline-parity.py`",
    "`scripts/zigux/check-phase7-argv-split-parity.py --self-test`",
    "`scripts/zigux/check-phase7-argv-split-parity.py`",
    "`scripts/zigux/check-phase7-rbtree-parity.py --self-test`",
    "`scripts/zigux/check-phase7-rbtree-parity.py`",
]
required_doc_readme_markers = [
    "`Documentation/zigux/phase7-string-helpers-slice.md`",
    "`Documentation/zigux/phase7-cmdline-slice.md`",
    "`Documentation/zigux/phase7-argv-split-slice.md`",
    "`Documentation/zigux/phase7-rbtree-slice.md`",
    "`python3 scripts/zigux/validate-phase7.py --self-test`",
    "`python3 scripts/zigux/check-phase7-build-inventory.py --self-test`",
    "`python3 scripts/zigux/check-phase7-build-inventory.py`",
    "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase7-argv-split-packet.py`",
    "`python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test`",
    "`python3 scripts/zigux/check-phase7-argv-split-parity.py`",
    "`make -C zigux phase7-validate`",
    "`make -C zigux phase7-test`",
    "`make -C zigux phase7`",
]
required_doc_readme_exact_count_markers = {
    "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`": 1,
    "`python3 scripts/zigux/check-phase7-argv-split-packet.py`": 1,
}
required_phase7_build_markers = [
    "fn createImportedTestRoot(",
    "fn createStandaloneTestRoot(",
    "fn addTestRun(",
    "run.setCwd(path);",
    'const repo_root = b.path("../..");',
    "phase7_string_helpers_sample_boundary.zig",
    "phase7-string-helpers-sample-boundary-tests",
    "phase7-cmdline-survey-tests",
    "phase7-argv-split-survey-tests",
    "phase7-string-helpers-survey-tests",
    "phase7-rbtree-survey-tests",
    'b.step("test", "Run Phase 7 runtime helper tests")',
]
unexpected_phase7_build_markers = [
    "../../tools/lib/",
    "zigux/tests/build.zig",
]
expected_shared_validation_gates = [
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-build-inventory.py",
    "scripts/zigux/check-phase7-make-wrapper.py",
    "scripts/zigux/check-phase7-cmdline-parity.py",
    "scripts/zigux/check-phase7-argv-split-packet.py",
    "scripts/zigux/check-phase7-argv-split-parity.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
]
expected_argv_split_fixture = {
    "blank_input": {"argc": 0, "argv": []},
    "first_nul_stops": {"argc": 2, "argv": ["root=/dev/vda", "rw"]},
    "leading_nul_stays_empty": {"argc": 0, "argv": []},
    "quote_characters_stay_literal": {
        "argc": 3,
        "argv": ['root=\"/dev/sda', '1\"', "single"],
    },
    "whitespace_collapse": {
        "argc": 3,
        "argv": ["init=/init", "console=ttyS0", "panic=-1"],
    },
}

def clone_fixture_root(destination_root: Path) -> None:
    for source in required_files:
        target = destination_root / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "zigux" / "validate-phase7.py")],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )

def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"phase7-self-test:{label}:unexpected_pass")
    if expected_marker not in result.stdout:
        actual = result.stdout.strip() or "none"
        raise SystemExit(
            f"phase7-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )

def collect_missing_markers(label: str, content: str, markers: list[str]) -> list[tuple[str, str]]:
    return [(label, marker) for marker in markers if marker not in content]

def collect_exact_count_marker_drift(
    label: str,
    content: str,
    exact_counts: dict[str, int],
) -> list[tuple[str, str]]:
    drift: list[tuple[str, str]] = []
    for marker, expected_count in exact_counts.items():
        actual_count = content.count(marker)
        if actual_count != expected_count:
            drift.append((label, f"exact_count:{marker}:{actual_count}!={expected_count}"))
    return drift

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_validator_selftest_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        baseline = run_validator(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase7-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        makefile_path = tmp_root / "zigux" / "Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-inventory.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "build_inventory_self_test_hook",
            tmp_root,
            "zigux/Makefile: python3 scripts/zigux/check-phase7-build-inventory.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-argv-split-parity.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_self_test_hook",
            tmp_root,
            "zigux/Makefile: python3 scripts/zigux/check-phase7-argv-split-parity.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        script_readme_path = tmp_root / "scripts" / "zigux" / "README.md"
        original_script_readme = script_readme_path.read_text(encoding="utf-8")
        script_readme_path.write_text(
            original_script_readme.replace(
                "- `check-phase7-argv-split-packet.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_packet_script_readme_marker",
            tmp_root,
            "scripts/zigux/README.md: `check-phase7-argv-split-packet.py`",
        )
        script_readme_path.write_text(original_script_readme, encoding="utf-8")

        script_readme_path.write_text(
            original_script_readme.replace(
                "- `check-phase7-argv-split-packet.py`\n",
                "- `check-phase7-argv-split-packet.py`\n- `check-phase7-argv-split-packet.py`\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_packet_script_readme_duplicate",
            tmp_root,
            "scripts/zigux/README.md: exact_count:- `check-phase7-argv-split-packet.py`:2!=1",
        )
        script_readme_path.write_text(original_script_readme, encoding="utf-8")

        script_readme_path.write_text(
            original_script_readme.replace(
                "- `check-phase7-argv-split-parity.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_script_readme_marker",
            tmp_root,
            "scripts/zigux/README.md: `check-phase7-argv-split-parity.py`",
        )
        script_readme_path.write_text(original_script_readme, encoding="utf-8")

        doc_path = tmp_root / "Documentation" / "zigux" / "phase7-argv-split-slice.md"
        original_doc = doc_path.read_text(encoding="utf-8")
        doc_path.write_text(
            original_doc.replace("`scripts/zigux/check-phase7-argv-split-packet.py`", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_packet_doc_marker",
            tmp_root,
            "Documentation/zigux/phase7-argv-split-slice.md: `scripts/zigux/check-phase7-argv-split-packet.py`",
        )
        doc_path.write_text(original_doc, encoding="utf-8")

        doc_readme_path = tmp_root / "Documentation" / "zigux" / "README.md"
        original_doc_readme = doc_readme_path.read_text(encoding="utf-8")
        doc_readme_path.write_text(
            original_doc_readme.replace(
                "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_packet_doc_readme_marker",
            tmp_root,
            "Documentation/zigux/README.md: `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
                "`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`, `python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_packet_doc_readme_duplicate_self_test_marker",
            tmp_root,
            "Documentation/zigux/README.md: exact_count:`python3 scripts/zigux/check-phase7-argv-split-packet.py --self-test`:2!=1",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "`python3 scripts/zigux/check-phase7-argv-split-packet.py`",
                "`python3 scripts/zigux/check-phase7-argv-split-packet.py`, `python3 scripts/zigux/check-phase7-argv-split-packet.py`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_packet_doc_readme_duplicate_marker",
            tmp_root,
            "Documentation/zigux/README.md: exact_count:`python3 scripts/zigux/check-phase7-argv-split-packet.py`:2!=1",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        doc_readme_path.write_text(
            original_doc_readme.replace(
                "`make -C zigux phase7-test`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "phase7_test_doc_readme_marker",
            tmp_root,
            "Documentation/zigux/README.md: `make -C zigux phase7-test`",
        )
        doc_readme_path.write_text(original_doc_readme, encoding="utf-8")

        workflow_path = tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Validate Phase 7 runtime helper gates\n        run: make -C zigux phase7-validate\n\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_phase7_validate_step",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml: Validate Phase 7 runtime helper gates",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        tests_readme_path = tmp_root / "zigux" / "tests" / "README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "`scripts/zigux/check-phase7-cmdline-parity.py --self-test`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_cmdline_self_test_marker",
            tmp_root,
            "zigux/tests/README.md: `scripts/zigux/check-phase7-cmdline-parity.py --self-test`",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "`scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_argv_split_packet_self_test_marker",
            tmp_root,
            "zigux/tests/README.md: `scripts/zigux/check-phase7-argv-split-packet.py --self-test`",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "`scripts/zigux/check-phase7-argv-split-packet.py`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_argv_split_packet_marker",
            tmp_root,
            "zigux/tests/README.md: `scripts/zigux/check-phase7-argv-split-packet.py`",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "`scripts/zigux/check-phase7-argv-split-parity.py --self-test`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_argv_split_self_test_marker",
            tmp_root,
            "zigux/tests/README.md: `scripts/zigux/check-phase7-argv-split-parity.py --self-test`",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "`scripts/zigux/check-phase7-rbtree-parity.py --self-test`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_rbtree_self_test_marker",
            tmp_root,
            "zigux/tests/README.md: `scripts/zigux/check-phase7-rbtree-parity.py --self-test`",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        build_path = tmp_root / "zigux" / "tests" / "phase7_build.zig"
        original_build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            original_build.replace(
                '"phase7-cmdline-survey-tests"',
                '"phase7-cmdline-standalone-tests"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "phase7_build_cmdline_survey_marker",
            tmp_root,
            "zigux/tests/phase7_build.zig: phase7-cmdline-survey-tests",
        )
        build_path.write_text(original_build, encoding="utf-8")

        build_path.write_text(
            original_build.replace(
                '"phase7-string-helpers-survey-tests"',
                '"phase7-string-helpers-standalone-tests"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "phase7_build_string_helpers_survey_marker",
            tmp_root,
            "zigux/tests/phase7_build.zig: phase7-string-helpers-survey-tests",
        )
        build_path.write_text(original_build, encoding="utf-8")

        build_inventory_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase7_build_inventory.json"
        original_build_inventory = json.loads(build_inventory_path.read_text(encoding="utf-8"))
        drifted_build_inventory = dict(original_build_inventory)
        drifted_build_inventory["shared_validation_gates"] = [
            gate
            for gate in original_build_inventory["shared_validation_gates"]
            if gate != "scripts/zigux/check-phase7-argv-split-parity.py"
        ]
        build_inventory_path.write_text(
            json.dumps(drifted_build_inventory, indent=2) + "\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "build_inventory_fixture_gate",
            tmp_root,
            "zigux/tests/fixtures/phase7_build_inventory.json: shared_validation_gates",
        )
        build_inventory_path.write_text(
            json.dumps(original_build_inventory, indent=2) + "\n",
            encoding="utf-8",
        )

        argv_split_fixture_path = tmp_root / "zigux" / "tests" / "fixtures" / "phase7_argv_split.json"
        original_argv_split_fixture = json.loads(argv_split_fixture_path.read_text(encoding="utf-8"))
        drifted_argv_split_fixture = dict(original_argv_split_fixture)
        drifted_argv_split_fixture.pop("leading_nul_stays_empty", None)
        argv_split_fixture_path.write_text(
            json.dumps(drifted_argv_split_fixture, indent=2) + "\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_fixture_case",
            tmp_root,
            "zigux/tests/fixtures/phase7_argv_split.json: leading_nul_stays_empty",
        )

        cmdline_manifest_path = tmp_root / "zigux" / "tests" / "phase7_cmdline_manifest.json"
        cmdline_manifest_path.unlink()
        expect_missing_marker(
            "cmdline_manifest_required_file",
            tmp_root,
            "zigux/tests/phase7_cmdline_manifest.json",
        )

    print("PHASE7_VALIDATOR_SELF_TEST=pass")
    print("PHASE7_VALIDATOR_SELF_TEST_CASE_COUNT=21")
    return 0

def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return run_self_test()

    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    if missing:
        print("PHASE7_VALIDATION=fail")
        print("MISSING_PHASE7_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE7_FILES_END")
        return 1

    makefile = (ROOT / "zigux" / "Makefile").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    script_readme = (ROOT / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
    tests_readme = (ROOT / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
    doc_readme = (ROOT / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
    phase7_build = (ROOT / "zigux" / "tests" / "phase7_build.zig").read_text(encoding="utf-8")

    missing_markers: list[tuple[str, str]] = []
    missing_markers.extend(collect_missing_markers("zigux/Makefile", makefile, required_make_markers))
    missing_markers.extend(collect_missing_markers(".github/workflows/zigux-bootstrap.yml", workflow, required_workflow_markers))
    missing_markers.extend(collect_missing_markers("scripts/zigux/README.md", script_readme, required_script_readme_markers))
    missing_markers.extend(
        collect_exact_count_marker_drift(
            "scripts/zigux/README.md",
            script_readme,
            required_script_readme_exact_count_markers,
        )
    )
    missing_markers.extend(collect_missing_markers("zigux/tests/README.md", tests_readme, required_tests_readme_markers))
    missing_markers.extend(collect_missing_markers("Documentation/zigux/README.md", doc_readme, required_doc_readme_markers))
    missing_markers.extend(
        collect_exact_count_marker_drift(
            "Documentation/zigux/README.md",
            doc_readme,
            required_doc_readme_exact_count_markers,
        )
    )
    missing_markers.extend(collect_missing_markers("zigux/tests/phase7_build.zig", phase7_build, required_phase7_build_markers))
    missing_markers.extend(
        [("zigux/tests/phase7_build.zig", marker) for marker in unexpected_phase7_build_markers if marker in phase7_build]
    )
    if missing_markers:
        print("PHASE7_VALIDATION=fail")
        print("MISSING_PHASE7_MARKERS_START")
        for label, marker in missing_markers:
            print(f"{label}: {marker}")
        print("MISSING_PHASE7_MARKERS_END")
        return 1

    build_inventory = json.loads((ROOT / "zigux" / "tests" / "fixtures" / "phase7_build_inventory.json").read_text(encoding="utf-8"))
    build_inventory_errors: list[str] = []
    if build_inventory.get("repo_root_path") != "../..":
        build_inventory_errors.append("repo_root_path")
    if build_inventory.get("shared_validation_gates") != expected_shared_validation_gates:
        build_inventory_errors.append("shared_validation_gates")
    if build_inventory.get("shared_validation_commands") != expected_make_expansions["phase7-validate"]:
        build_inventory_errors.append("shared_validation_commands")
    if build_inventory.get("unexpected_build_markers") != unexpected_phase7_build_markers:
        build_inventory_errors.append("unexpected_build_markers")
    if len(build_inventory.get("run_labels", [])) != 9:
        build_inventory_errors.append("run_labels")
    if len(build_inventory.get("shared_test_depend_steps", [])) != 9:
        build_inventory_errors.append("shared_test_depend_steps")
    if build_inventory.get("run_cwds", {}).get("phase7-cmdline-survey-tests") != "repo_root":
        build_inventory_errors.append("run_cwds:phase7-cmdline-survey-tests")
    if build_inventory.get("run_cwds", {}).get("phase7-argv-split-survey-tests") != "repo_root":
        build_inventory_errors.append("run_cwds:phase7-argv-split-survey-tests")
    if build_inventory.get("run_cwds", {}).get("phase7-string-helpers-survey-tests") != "repo_root":
        build_inventory_errors.append("run_cwds:phase7-string-helpers-survey-tests")
    if build_inventory.get("run_cwds", {}).get("phase7-string-helpers-sample-boundary-tests") != "repo_root":
        build_inventory_errors.append("run_cwds:phase7-string-helpers-sample-boundary-tests")
    if build_inventory.get("run_cwds", {}).get("phase7-rbtree-survey-tests") != "repo_root":
        build_inventory_errors.append("run_cwds:phase7-rbtree-survey-tests")
    if build_inventory_errors:
        print("PHASE7_VALIDATION=fail")
        print("PHASE7_BUILD_INVENTORY_SHAPE_START")
        for item in build_inventory_errors:
            print(f"zigux/tests/fixtures/phase7_build_inventory.json: {item}")
        print("PHASE7_BUILD_INVENTORY_SHAPE_END")
        return 1

    argv_split_fixture = json.loads((ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split.json").read_text(encoding="utf-8"))
    argv_split_errors = [
        key for key, value in expected_argv_split_fixture.items() if argv_split_fixture.get(key) != value
    ]
    if argv_split_errors:
        print("PHASE7_VALIDATION=fail")
        print("PHASE7_ARGV_SPLIT_FIXTURE_SHAPE_START")
        for item in argv_split_errors:
            print(f"zigux/tests/fixtures/phase7_argv_split.json: {item}")
        print("PHASE7_ARGV_SPLIT_FIXTURE_SHAPE_END")
        return 1

    packet_checker = ROOT / "scripts" / "zigux" / "check-phase7-argv-split-packet.py"
    packet_commands = [
        (
            [sys.executable, str(packet_checker), "--self-test"],
            "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST_FAILED_START",
            "PHASE7_ARGV_SPLIT_PACKET_SELF_TEST_FAILED_END",
        ),
        (
            [sys.executable, str(packet_checker)],
            "PHASE7_ARGV_SPLIT_PACKET_CHECK_FAILED_START",
            "PHASE7_ARGV_SPLIT_PACKET_CHECK_FAILED_END",
        ),
    ]
    for command, start_banner, end_banner in packet_commands:
        result = subprocess.run(
            command,
            cwd=str(ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("PHASE7_VALIDATION=fail")
            print(start_banner)
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            print(end_banner)
            return 1

    for target_name, expected_lines in expected_make_expansions.items():
        result = subprocess.run(
            ["make", "-n", "-C", str(ROOT / "zigux"), target_name],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("PHASE7_VALIDATION=fail")
            print("PHASE7_MAKE_WRAPPER_CHECK_FAILED_START")
            print(f"{target_name}: returncode={result.returncode}")
            stderr = result.stderr.strip()
            if stderr:
                print(stderr)
            print("PHASE7_MAKE_WRAPPER_CHECK_FAILED_END")
            return 1

        wrapper_output = result.stdout
        missing_wrapper_lines = [line for line in expected_lines if line not in wrapper_output]
        if missing_wrapper_lines:
            print("PHASE7_VALIDATION=fail")
            print("PHASE7_MAKE_WRAPPER_DRIFT_START")
            print(f"{target_name}: missing expected wrapper expansion")
            for line in missing_wrapper_lines:
                print(line)
            print("PHASE7_MAKE_WRAPPER_DRIFT_END")
            return 1

        unexpected_wrapper_lines = [
            line for line in unexpected_make_expansions.get(target_name, []) if line in wrapper_output
        ]
        if unexpected_wrapper_lines:
            print("PHASE7_VALIDATION=fail")
            print("PHASE7_MAKE_WRAPPER_DRIFT_START")
            print(f"{target_name}: unexpected wrapper expansion")
            for line in unexpected_wrapper_lines:
                print(line)
            print("PHASE7_MAKE_WRAPPER_DRIFT_END")
            return 1

    print("PHASE7_VALIDATION=pass")
    print(f"PHASE7_REQUIRED_FILE_COUNT={len(required_files)}")
    print(
        "PHASE7_REQUIRED_MARKER_COUNT="
        f"{len(required_make_markers) + len(required_workflow_markers) + len(required_script_readme_markers) + len(required_script_readme_exact_count_markers) + len(required_tests_readme_markers) + len(required_doc_readme_markers) + len(required_doc_readme_exact_count_markers) + len(required_phase7_build_markers)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
