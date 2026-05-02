#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
PHASE7_BUILD_PATH = ROOT / "zigux" / "tests" / "phase7_build.zig"

required_files = [
    ROOT / "scripts" / "zigux" / "validate-phase7.py",
    ROOT / "scripts" / "zigux" / "check-phase7-make-wrapper.py",
    ROOT / "scripts" / "zigux" / "check-phase7-cmdline-parity.py",
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
    ROOT / "zigux" / "tests" / "phase7_cmdline.zig",
    ROOT / "zigux" / "tests" / "phase7_cmdline_survey.zig",
    ROOT / "zigux" / "tests" / "phase7_argv_split.zig",
    ROOT / "zigux" / "tests" / "phase7_argv_split_survey.zig",
    ROOT / "zigux" / "tests" / "phase7_argv_split_manifest.json",
    ROOT / "zigux" / "tests" / "phase7_rbtree.zig",
    ROOT / "zigux" / "tests" / "phase7_rbtree_survey.zig",
    ROOT / "zigux" / "tests" / "phase7_rbtree_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_string_helpers_escape_vectors.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_cmdline_next_arg_vectors.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_cmdline.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_cmdline_c_harness.c",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_rbtree.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_rbtree_c_harness.c",
    ROOT / "lib" / "string_helpers.zig",
    ROOT / "lib" / "cmdline.zig",
    ROOT / "lib" / "argv_split.zig",
    ROOT / "lib" / "rbtree.zig",
    ROOT / "samples" / "zigux" / "README.md",
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
]


def clone_fixture_root(destination_root: Path) -> None:
    for source in required_files:
        target = destination_root / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def run_validator(
    root: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "zigux" / "validate-phase7.py")],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
        env=env,
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
                'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_self_test_hook",
            tmp_root,
            "zigux/Makefile: scripts/zigux/validate-phase7.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        workflow_path = tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Self-test Phase 7 runtime validator\n"
                "        run: python3 scripts/zigux/validate-phase7.py --self-test\n\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_self_test_step",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml: Self-test Phase 7 runtime validator",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        fake_make_dir = tmp_root / "fake-bin"
        fake_make_dir.mkdir()
        fake_make_path = fake_make_dir / "make"
        fake_make_path.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "\n"
            "target = sys.argv[-1]\n"
            "outputs = {\n"
            "    'phase7-validate': [\n"
            "        'python3 scripts/zigux/validate-phase7.py --self-test',\n"
            "        'python3 scripts/zigux/validate-phase7.py',\n"
            "        'python3 scripts/zigux/check-phase7-build-inventory.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-build-inventory.py',\n"
            "        'python3 scripts/zigux/check-phase7-make-wrapper.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-make-wrapper.py',\n"
            "        'python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-cmdline-parity.py',\n"
            "        'python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-rbtree-parity.py',\n"
            "    ],\n"
            "    'phase7-test': [\n"
            "        'zig build test --build-file zigux/tests/phase7_build.zig',\n"
            "    ],\n"
            "    'phase7': [\n"
            "        'python3 scripts/zigux/validate-phase7.py --self-test',\n"
            "        'python3 scripts/zigux/validate-phase7.py',\n"
            "        'python3 scripts/zigux/check-phase7-build-inventory.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-build-inventory.py',\n"
            "        'python3 scripts/zigux/check-phase7-make-wrapper.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-make-wrapper.py',\n"
            "        'python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-cmdline-parity.py',\n"
            "        'python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-rbtree-parity.py',\n"
            "        'zig build test --build-file zigux/tests/phase7_build.zig --summary all',\n"
            "    ],\n"
            "}\n"
            "for line in outputs.get(target, []):\n"
            "    print(line)\n",
            encoding="utf-8",
        )
        fake_make_path.chmod(0o755)
        fake_make_env = os.environ.copy()
        fake_make_env["PATH"] = f"{fake_make_dir}:{fake_make_env['PATH']}"
        result = run_validator(tmp_root, env=fake_make_env)
        if result.returncode == 0:
            raise SystemExit("phase7-self-test:make_wrapper_drift:unexpected_pass")
        if "phase7-test: missing expected wrapper expansion" not in result.stdout:
            actual = result.stdout.strip() or "none"
            raise SystemExit(
                "phase7-self-test:make_wrapper_drift:expected_wrapper_failure:"
                f"actual:{actual}"
            )

        fake_make_path.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "\n"
            "target = sys.argv[-1]\n"
            "outputs = {\n"
            "    'phase7-validate': [\n"
            "        'python3 scripts/zigux/validate-phase7.py --self-test',\n"
            "        'python3 scripts/zigux/validate-phase7.py',\n"
            "        'python3 scripts/zigux/check-phase7-build-inventory.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-build-inventory.py',\n"
            "        'python3 scripts/zigux/check-phase7-make-wrapper.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-make-wrapper.py',\n"
            "        'python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-cmdline-parity.py',\n"
            "        'python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-rbtree-parity.py',\n"
            "    ],\n"
            "    'phase7-test': [\n"
            "        'zig build test --build-file zigux/tests/phase7_build.zig --summary all',\n"
            "        'zig build test --build-file zigux/tests/build.zig',\n"
            "    ],\n"
            "    'phase7': [\n"
            "        'python3 scripts/zigux/validate-phase7.py --self-test',\n"
            "        'python3 scripts/zigux/validate-phase7.py',\n"
            "        'python3 scripts/zigux/check-phase7-build-inventory.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-build-inventory.py',\n"
            "        'python3 scripts/zigux/check-phase7-make-wrapper.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-make-wrapper.py',\n"
            "        'python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-cmdline-parity.py',\n"
            "        'python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-rbtree-parity.py',\n"
            "        'zig build test --build-file zigux/tests/phase7_build.zig --summary all',\n"
            "        'zig build test --build-file zigux/tests/build.zig',\n"
            "    ],\n"
            "}\n"
            "for line in outputs.get(target, []):\n"
            "    print(line)\n",
            encoding="utf-8",
        )
        result = run_validator(tmp_root, env=fake_make_env)
        if result.returncode == 0:
            raise SystemExit("phase7-self-test:stale_wrapper_expansion:unexpected_pass")
        if "phase7-test: unexpected wrapper expansion" not in result.stdout:
            actual = result.stdout.strip() or "none"
            raise SystemExit(
                "phase7-self-test:stale_wrapper_expansion:expected_wrapper_failure:"
                f"actual:{actual}"
            )

        fake_make_path.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "\n"
            "target = sys.argv[-1]\n"
            "outputs = {\n"
            "    'phase7-validate': [\n"
            "        'python3 scripts/zigux/validate-phase7.py --self-test',\n"
            "        'python3 scripts/zigux/validate-phase7.py',\n"
            "        'python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-cmdline-parity.py',\n"
            "        'python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-rbtree-parity.py',\n"
            "    ],\n"
            "    'phase7-test': [\n"
            "        'zig build test --build-file zigux/tests/phase7_build.zig --summary all',\n"
            "    ],\n"
            "    'phase7': [\n"
            "        'python3 scripts/zigux/validate-phase7.py --self-test',\n"
            "        'python3 scripts/zigux/validate-phase7.py',\n"
            "        'python3 scripts/zigux/check-phase7-cmdline-parity.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-cmdline-parity.py',\n"
            "        'python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test',\n"
            "        'python3 scripts/zigux/check-phase7-rbtree-parity.py',\n"
            "        'zig build test --build-file zigux/tests/phase7_build.zig --summary all',\n"
            "    ],\n"
            "}\n"
            "for line in outputs.get(target, []):\n"
            "    print(line)\n",
            encoding="utf-8",
        )
        result = run_validator(tmp_root, env=fake_make_env)
        if result.returncode == 0:
            raise SystemExit("phase7-self-test:missing_make_wrapper_gate:unexpected_pass")
        if "phase7-validate: missing expected wrapper expansion" not in result.stdout:
            actual = result.stdout.strip() or "none"
            raise SystemExit(
                "phase7-self-test:missing_make_wrapper_gate:expected_wrapper_failure:"
                f"actual:{actual}"
            )

        argv_split_survey_path = tmp_root / "zigux" / "tests" / "phase7_argv_split_survey.zig"
        original_argv_split_survey = argv_split_survey_path.read_text(encoding="utf-8")
        argv_split_survey_path.write_text(
            original_argv_split_survey.replace(
                'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_ready_next_guard",
            tmp_root,
            'zigux/tests/phase7_argv_split_survey.zig: try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
        )
        argv_split_survey_path.write_text(original_argv_split_survey, encoding="utf-8")

        argv_split_helper_path = tmp_root / "lib" / "argv_split.zig"
        original_argv_split_helper = argv_split_helper_path.read_text(encoding="utf-8")
        argv_split_helper_path.write_text(
            original_argv_split_helper.replace(
                "const leading_nul_expected = [_][]const u8{};",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_leading_nul_helper_surface",
            tmp_root,
            "lib/argv_split.zig: const leading_nul_expected = [_][]const u8{};",
        )
        argv_split_helper_path.write_text(
            original_argv_split_helper, encoding="utf-8"
        )

        argv_split_tests_path = tmp_root / "zigux" / "tests" / "phase7_argv_split.zig"
        original_argv_split_tests = argv_split_tests_path.read_text(encoding="utf-8")
        argv_split_tests_path.write_text(
            original_argv_split_tests.replace(
                "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_ownership_review_surface",
            tmp_root,
            "zigux/tests/phase7_argv_split.zig: phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
        )
        argv_split_tests_path.write_text(
            original_argv_split_tests, encoding="utf-8"
        )

        argv_split_survey_path.write_text(
            original_argv_split_survey.replace(
                'try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplitWithArgc reports the split length through the optional out parameter") != null);',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "argv_split_argc_review_surface",
            tmp_root,
            'zigux/tests/phase7_argv_split_survey.zig: try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplitWithArgc reports the split length through the optional out parameter") != null);',
        )
        argv_split_survey_path.write_text(
            original_argv_split_survey, encoding="utf-8"
        )

        cmdline_doc_path = tmp_root / "Documentation" / "zigux" / "phase7-cmdline-slice.md"
        original_cmdline_doc = cmdline_doc_path.read_text(encoding="utf-8")
        cmdline_doc_path.write_text(
            original_cmdline_doc.replace(
                "exact bare-option matching for comma-delimited flags",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "cmdline_bare_option_review_surface",
            tmp_root,
            "Documentation/zigux/phase7-cmdline-slice.md: exact bare-option matching for comma-delimited flags",
        )
        cmdline_doc_path.write_text(original_cmdline_doc, encoding="utf-8")

        string_helpers_survey_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers_survey.zig"
        original_string_helpers_survey = string_helpers_survey_path.read_text(encoding="utf-8")
        string_helpers_survey_path.write_text(
            original_string_helpers_survey.replace(
                'try expectContains(string_helpers_tests, "phase 7 kasprintfStrarray returns sequential owned strings with a null-pointer terminator");',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "string_helpers_string_array_review_surface",
            tmp_root,
            'zigux/tests/phase7_string_helpers_survey.zig: phase 7 kasprintfStrarray returns sequential owned strings with a null-pointer terminator',
        )
        string_helpers_survey_path.write_text(
            original_string_helpers_survey, encoding="utf-8"
        )

        string_helpers_tests_path = tmp_root / "zigux" / "tests" / "phase7_string_helpers.zig"
        original_string_helpers_tests = string_helpers_tests_path.read_text(encoding="utf-8")
        string_helpers_tests_path.write_text(
            original_string_helpers_tests.replace(
                "phase 7 stringEscapeMem reports truncated output length without forcing a terminator",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "string_helpers_escape_truncation_review_surface",
            tmp_root,
            "zigux/tests/phase7_string_helpers.zig: phase 7 stringEscapeMem reports truncated output length without forcing a terminator",
        )
        string_helpers_tests_path.write_text(
            original_string_helpers_tests, encoding="utf-8"
        )

        rbtree_survey_path = tmp_root / "zigux" / "tests" / "phase7_rbtree_survey.zig"
        original_rbtree_survey = rbtree_survey_path.read_text(encoding="utf-8")
        rbtree_survey_path.write_text(
            original_rbtree_survey.replace(
                'try std.testing.expect(std.mem.indexOf(u8, rbtree_tests, "phase 7 rbtree eraseInit detaches erased nodes for reuse") != null);',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "rbtree_eraseinit_review_surface",
            tmp_root,
            'zigux/tests/phase7_rbtree_survey.zig: try std.testing.expect(std.mem.indexOf(u8, rbtree_tests, "phase 7 rbtree eraseInit detaches erased nodes for reuse") != null);',
        )
        rbtree_survey_path.write_text(original_rbtree_survey, encoding="utf-8")

        phase7_build_path = tmp_root / "zigux" / "tests" / "phase7_build.zig"
        original_phase7_build = phase7_build_path.read_text(encoding="utf-8")
        phase7_build_path.write_text(
            original_phase7_build.replace(
                "    test_step.dependOn(&run_rbtree_survey_tests.step);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        result = run_validator(tmp_root, env=fake_make_env)
        if result.returncode == 0:
            raise SystemExit("phase7-self-test:dependency_edge_drift:unexpected_pass")
        if "phase7-test-step: missing expected dependency edge" not in result.stdout:
            actual = result.stdout.strip() or "none"
            raise SystemExit(
                "phase7-self-test:dependency_edge_drift:expected_dependency_failure:"
                f"actual:{actual}"
            )

    print("PHASE7_VALIDATOR_SELF_TEST=pass")
    print("PHASE7_VALIDATOR_SELF_TEST_CASE_COUNT=14")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print("PHASE7_VALIDATION=fail")
    print("MISSING_PHASE7_FILES_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE7_FILES_END")
    sys.exit(1)

makefile = (ROOT / "zigux" / "Makefile").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
script_readme = (ROOT / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
tests_readme = (ROOT / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
doc_readme = (ROOT / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
phase7_build = (ROOT / "zigux" / "tests" / "phase7_build.zig").read_text(encoding="utf-8")
phase7_string_helpers_tests = (ROOT / "zigux" / "tests" / "phase7_string_helpers.zig").read_text(encoding="utf-8")
phase7_string_helpers_survey = (ROOT / "zigux" / "tests" / "phase7_string_helpers_survey.zig").read_text(encoding="utf-8")
phase7_string_helpers_doc = (ROOT / "Documentation" / "zigux" / "phase7-string-helpers-slice.md").read_text(encoding="utf-8")
phase7_cmdline_survey = (ROOT / "zigux" / "tests" / "phase7_cmdline_survey.zig").read_text(encoding="utf-8")
phase7_cmdline_tests = (ROOT / "zigux" / "tests" / "phase7_cmdline.zig").read_text(encoding="utf-8")
phase7_argv_split_doc = (ROOT / "Documentation" / "zigux" / "phase7-argv-split-slice.md").read_text(encoding="utf-8")
phase7_argv_split_helper = (ROOT / "lib" / "argv_split.zig").read_text(encoding="utf-8")
phase7_argv_split_manifest = json.loads(
    (ROOT / "zigux" / "tests" / "phase7_argv_split_manifest.json").read_text(encoding="utf-8")
)
phase7_argv_split_survey = (ROOT / "zigux" / "tests" / "phase7_argv_split_survey.zig").read_text(encoding="utf-8")
phase7_argv_split_tests = (ROOT / "zigux" / "tests" / "phase7_argv_split.zig").read_text(encoding="utf-8")
phase7_rbtree_tests = (ROOT / "zigux" / "tests" / "phase7_rbtree.zig").read_text(encoding="utf-8")
phase7_rbtree_survey = (ROOT / "zigux" / "tests" / "phase7_rbtree_survey.zig").read_text(encoding="utf-8")
phase7_cmdline_doc = (ROOT / "Documentation" / "zigux" / "phase7-cmdline-slice.md").read_text(encoding="utf-8")
phase7_rbtree_doc = (ROOT / "Documentation" / "zigux" / "phase7-rbtree-slice.md").read_text(encoding="utf-8")
phase7_rbtree_manifest = json.loads(
    (ROOT / "zigux" / "tests" / "phase7_rbtree_manifest.json").read_text(encoding="utf-8")
)

required_make_markers = [
    "phase7-validate:",
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py --self-test',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase7.py',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-inventory.py --self-test',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-build-inventory.py',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py --self-test',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-make-wrapper.py',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-cmdline-parity.py --self-test',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-cmdline-parity.py',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py --self-test',
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase7-rbtree-parity.py',
    "phase7-test:",
    'cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase7_build.zig --summary all',
    "phase7: phase7-validate phase7-test",
]

required_workflow_markers = [
    "- name: Self-test Phase 7 runtime validator",
    "run: python3 scripts/zigux/validate-phase7.py --self-test",
    "- name: Validate Phase 7 runtime helper gates",
    "run: make -C zigux phase7-validate",
    "- name: Run Phase 7 runtime helper tests",
    "run: zig build test --build-file zigux/tests/phase7_build.zig --summary all",
]

required_script_readme_markers = [
    "`validate-phase7.py`",
    "`check-phase7-build-inventory.py`",
    "`check-phase7-make-wrapper.py`",
    "`check-phase7-cmdline-parity.py`",
    "`check-phase7-rbtree-parity.py`",
    "`check-phase7-build-inventory.py --self-test` and `check-phase7-build-inventory.py` keep the committed `zigux/tests/fixtures/phase7_build_inventory.json` snapshot aligned with the shared `zigux/tests/phase7_build.zig` helper bundle before the broader Phase 7 replay runs.",
    "`check-phase7-make-wrapper.py --self-test` and `check-phase7-make-wrapper.py` keep the published `make -C zigux phase7-validate`, `make -C zigux phase7-test`, and `make -C zigux phase7` wrapper expansions aligned with the validator-first Phase 7 flow before the broader helper replay runs.",
    "`make -C zigux phase7-validate` is the validator-first entrypoint for the current Phase 7 flow.",
    "`make -C zigux phase7-test` is the shared replay path after the validator, build-inventory, make-wrapper, and parity gates pass.",
    "`make -C zigux phase7` keeps the one-command bundle aligned with the published review path instead of bypassing the fail-closed validator.",
]

required_tests_readme_markers = [
    "keep the current Phase 7 helper packet reviewable through `zigux/tests/phase7_build.zig`, `zigux/tests/fixtures/phase7_build_inventory.json`, `make -C zigux phase7-test`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-cmdline-parity.py`, and `scripts/zigux/check-phase7-rbtree-parity.py` instead of widening into ad hoc helper-local bootstrap rules",
    "keep `scripts/zigux/validate-phase7.py --self-test`, `scripts/zigux/check-phase7-build-inventory.py --self-test`, and `scripts/zigux/check-phase7-make-wrapper.py --self-test` in the same packet so the shared Phase 7 review path still proves it catches Makefile-hook, workflow-step, build-inventory, make-wrapper, and parked argv-split survey drift before the broader helper replay runs",
    "keep the Phase 7 handoff explicit: the helper roots in `zigux/tests/phase7_build.zig` receive `string_helpers`, `cmdline`, `argv_split`, and `rbtree` through `addImport(...)`, `zigux/tests/phase7_string_helpers_survey.zig` and `zigux/tests/phase7_cmdline_survey.zig` stay standalone so the helper-only string and cmdline slices keep their roadmap-backed review notes explicit without widening into extra helper-local bootstrap rules or later-phase sample claims, and `zigux/tests/phase7_argv_split_survey.zig` and `zigux/tests/phase7_rbtree_survey.zig` rely on repo-root reads of `zigux/tests/phase7_argv_split_manifest.json` and `zigux/tests/phase7_rbtree_manifest.json`, so `phase7_build.zig` keeps those survey runs rooted at `repo_root`",
]

required_doc_readme_markers = [
    "`samples/zigux/README.md` is the shared Phase 5 sample-root catalog",
    "the Phase 7 string-helpers slice is intentionally helper-only",
    "current `master` ships no `samples/zigux/*string*` reference sample",
    "sample-root follow-up should not treat that absence as a missing Phase 5 port",
]

required_phase7_string_helpers_survey_markers = [
    "phase7-string-helpers-tests",
    "phase7-string-helpers-survey-tests",
    "`samples/zigux/README.md` is the shared Phase 5 sample-root catalog",
    "the Phase 7 string-helpers slice is intentionally helper-only",
    "current `master` ships no `samples/zigux/*string*` reference sample",
    "sample-root follow-up should not treat that absence as a missing Phase 5 port",
    "phase 7 kasprintfStrarray returns sequential owned strings with a null-pointer terminator",
]

required_phase7_string_helpers_test_markers = [
    "fixtures/phase7_string_helpers_escape_vectors.zig",
    "phase 7 stringEscapeMem reports truncated output length without forcing a terminator",
    "phase 7 kasprintfStrarray returns sequential owned strings with a null-pointer terminator",
]

required_phase7_string_helpers_doc_markers = [
    "integration with validation substrate through `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_string_helpers_survey.zig`, and `zigux/tests/phase7_build.zig`.",
    "prove the shared Phase 7 validator packet plus the build-inventory and make-wrapper gates still fail closed before the helper replay runs",
    "`python3 scripts/zigux/check-phase7-build-inventory.py`",
    "`python3 scripts/zigux/check-phase7-make-wrapper.py`",
    "`make -C zigux phase7-validate`",
]

required_phase7_cmdline_survey_markers = [
    "phase 7 cmdline survey keeps the roadmap-backed helper-only boundary explicit",
    "exact bare-option matching for comma-delimited flags",
    "`zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig`",
]

required_phase7_cmdline_test_markers = [
    "fixtures/phase7_cmdline_next_arg_vectors.zig",
    "phase 7 nextArg keeps the mirrored edge corpus reviewable",
    "phase 7 parseOptionStr keeps bare comma-delimited flags exact",
]

required_phase7_cmdline_doc_markers = [
    "integration with validation substrate through `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_cmdline_survey.zig`, and `zigux/tests/phase7_build.zig`.",
    "exact bare-option matching for comma-delimited flags",
    "`python3 scripts/zigux/check-phase7-build-inventory.py`",
    "`python3 scripts/zigux/check-phase7-make-wrapper.py`",
]

required_phase7_argv_split_helper_markers = [
    "const leading_nul_expected = [_][]const u8{};",
    "pub fn argvFree",
]

required_phase7_argv_split_doc_markers = [
    "integration with validation substrate through `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-build-inventory.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, and `zigux/tests/phase7_build.zig`.",
    "prove the shared Phase 7 validator packet still fails closed before the helper replay runs",
    "`python3 scripts/zigux/check-phase7-build-inventory.py`",
    "`python3 scripts/zigux/check-phase7-make-wrapper.py`",
    "`make -C zigux phase7-validate`",
    "`zig build test --build-file zigux/tests/phase7_build.zig --summary all`",
    "`zig test zigux/tests/phase7_argv_split_survey.zig`",
    "keep the roadmap survey record machine-checked from `repo_root`",
    "The manifest-backed survey packet stays rooted at `repo_root` through `zigux/tests/phase7_build.zig`",
    "`argv_free()` via `argvFree()`",
    "optional argc reporting that stays in sync with the returned argv length",
    "leading-NUL truncation to zero argv entries before any later bytes are considered",
    "repeated blank-input `argvFree()` teardown safety so the shared empty sentinel state survives explicit release without allocator backing",
    "teardown cleanup that clears the exported storage handle alongside the argv views after `ArgvSplitResult.deinit()`",
    "repeated teardown safety so an already-cleared `ArgvSplitResult` can be passed through `deinit()` again without freeing the shared empty sentinel state",
    "allocator-failure cleanup that proves the shared Phase 7 gate also exercises the intermediate allocation teardown path already covered by the direct helper tests",
]

required_phase7_argv_split_survey_markers = [
    "zigux/tests/phase7_argv_split_manifest.json",
    'try std.testing.expectEqual(@as(usize, 0), ready_next_count);',
    'try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplitWithArgc reports the split length through the optional out parameter") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, argv_split_tests, "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup") != null);',
]

required_phase7_argv_split_test_markers = [
    "phase 7 argvSplitWithArgc reports the split length through the optional out parameter",
    "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
    "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
]

required_phase7_rbtree_survey_markers = [
    "zigux/tests/phase7_rbtree_manifest.json",
    'try std.testing.expect(std.mem.indexOf(u8, rbtree_helper, "pub fn iterateMatches") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, rbtree_helper, "pub fn eraseInit") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, rbtree_tests, "phase 7 rbtree eraseInit detaches erased nodes for reuse") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, rbtree_tests, "phase 7 rbtree postorder traversal matches committed parity fixture") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, rbtree_slice, "erase-and-detach reuse semantics via `eraseInit()`") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, rbtree_slice, "a machine-checked manifest that records the `lib/rbtree.c` anchor and the landed Phase 7 review surfaces") != null);',
]

required_phase7_rbtree_test_markers = [
    '@embedFile("fixtures/phase7_rbtree.json")',
    "phase 7 rbtree balancing helpers keep ordered insert erase traversal stable",
    "phase 7 rbtree eraseInit detaches erased nodes for reuse",
    "phase 7 rbtree detached nodes stay non-empty until callers clear them",
    "phase 7 rbtree clearNode marks detached nodes as empty",
    "phase 7 rbtree find helpers walk duplicate-key ranges",
    "phase 7 rbtree iterateMatches streams duplicate-key ranges",
    "phase 7 rbtree findAdd inserts new nodes and returns existing duplicates",
    "phase 7 rbtree postorder traversal matches committed parity fixture",
]

required_phase7_rbtree_doc_markers = [
    "integration with validation substrate through `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_build.zig`, and `scripts/zigux/check-phase7-rbtree-parity.py`.",
    "erase-and-detach reuse semantics via `eraseInit()`",
    "a machine-checked manifest that records the `lib/rbtree.c` anchor and the landed Phase 7 review surfaces",
]

expected_phase7_build_paths = {
    "../..",
    "../../lib/string_helpers.zig",
    "../../lib/cmdline.zig",
    "../../lib/argv_split.zig",
    "../../lib/rbtree.zig",
    "phase7_string_helpers.zig",
    "phase7_string_helpers_survey.zig",
    "phase7_cmdline.zig",
    "phase7_cmdline_survey.zig",
    "phase7_argv_split.zig",
    "phase7_argv_split_survey.zig",
    "phase7_rbtree.zig",
    "phase7_rbtree_survey.zig",
}

expected_phase7_import_calls = {
    "string_helpers": (
        r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"phase7_string_helpers\.zig",'
        r'\s*"string_helpers",\s*"\.\./\.\./lib/string_helpers\.zig",'
    ),
    "cmdline": (
        r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"phase7_cmdline\.zig",'
        r'\s*"cmdline",\s*"\.\./\.\./lib/cmdline\.zig",'
    ),
    "argv_split": (
        r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"phase7_argv_split\.zig",'
        r'\s*"argv_split",\s*"\.\./\.\./lib/argv_split\.zig",'
    ),
    "rbtree": (
        r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"phase7_rbtree\.zig",'
        r'\s*"rbtree",\s*"\.\./\.\./lib/rbtree\.zig",'
    ),
}

expected_phase7_run_labels = {
    "phase7-string-helpers-tests",
    "phase7-string-helpers-survey-tests",
    "phase7-cmdline-tests",
    "phase7-cmdline-survey-tests",
    "phase7-argv-split-tests",
    "phase7-argv-split-survey-tests",
    "phase7-rbtree-tests",
    "phase7-rbtree-survey-tests",
}

expected_phase7_run_cwds = {
    "phase7-string-helpers-tests": "null",
    "phase7-cmdline-tests": "null",
    "phase7-cmdline-survey-tests": "repo_root",
    "phase7-argv-split-tests": "null",
    "phase7-argv-split-survey-tests": "repo_root",
    "phase7-string-helpers-survey-tests": "repo_root",
    "phase7-rbtree-tests": "null",
    "phase7-rbtree-survey-tests": "repo_root",
}

expected_phase7_test_step_dependencies = {
    "run_string_helpers_tests",
    "run_cmdline_tests",
    "run_cmdline_survey_tests",
    "run_argv_split_tests",
    "run_argv_split_survey_tests",
    "run_string_helpers_survey_tests",
    "run_rbtree_tests",
    "run_rbtree_survey_tests",
}

required_phase7_build_markers = [
    "fn createImportedTestRoot(",
    "fn createStandaloneTestRoot(",
    "fn addTestRun(",
    "run.setCwd(path);",
    'const repo_root = b.path("../..");',
    "Helper tests keep the shipped lib imports explicit, while survey tests stay standalone.",
    "../../lib/string_helpers.zig",
    "../../lib/cmdline.zig",
    "../../lib/argv_split.zig",
    "../../lib/rbtree.zig",
    "phase7_string_helpers.zig",
    "phase7_string_helpers_survey.zig",
    "phase7_cmdline.zig",
    "phase7_cmdline_survey.zig",
    "phase7_argv_split.zig",
    "phase7_argv_split_survey.zig",
    "phase7_rbtree.zig",
    "phase7_rbtree_survey.zig",
    "phase7-string-helpers-tests",
    "phase7-string-helpers-survey-tests",
    "phase7-cmdline-tests",
    "phase7-cmdline-survey-tests",
    "phase7-argv-split-tests",
    "phase7-argv-split-survey-tests",
    "phase7-rbtree-tests",
    "phase7-rbtree-survey-tests",
    "string_helpers_root_module,\n        null,",
    "cmdline_root_module,\n        null,",
    "cmdline_survey_root_module,\n        repo_root,",
    "argv_split_root_module,\n        null,",
    "argv_split_survey_root_module,\n        repo_root,",
    "string_helpers_survey_root_module,\n        repo_root,",
    "rbtree_root_module,\n        null,",
    "rbtree_survey_root_module,\n        repo_root,",
    'b.step("test", "Run Phase 7 runtime helper tests")',
]

unexpected_phase7_build_markers = [
    "../../tools/lib/",
    "zigux/tests/build.zig",
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
        "python3 scripts/zigux/check-phase7-rbtree-parity.py --self-test",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "zig build test --build-file zigux/tests/build.zig",
    ],
    "phase7": [
        "zig build test --build-file zigux/tests/build.zig",
    ],
}

checks = [
    ("zigux/Makefile", makefile, required_make_markers),
    (".github/workflows/zigux-bootstrap.yml", workflow, required_workflow_markers),
    ("scripts/zigux/README.md", script_readme, required_script_readme_markers),
    ("zigux/tests/README.md", tests_readme, required_tests_readme_markers),
    ("Documentation/zigux/README.md", doc_readme, required_doc_readme_markers),
    ("zigux/tests/phase7_build.zig", phase7_build, required_phase7_build_markers),
    ("zigux/tests/phase7_string_helpers_survey.zig", phase7_string_helpers_survey, required_phase7_string_helpers_survey_markers),
    ("zigux/tests/phase7_string_helpers.zig", phase7_string_helpers_tests, required_phase7_string_helpers_test_markers),
    ("Documentation/zigux/phase7-string-helpers-slice.md", phase7_string_helpers_doc, required_phase7_string_helpers_doc_markers),
    ("zigux/tests/phase7_cmdline_survey.zig", phase7_cmdline_survey, required_phase7_cmdline_survey_markers),
    ("zigux/tests/phase7_cmdline.zig", phase7_cmdline_tests, required_phase7_cmdline_test_markers),
    ("Documentation/zigux/phase7-argv-split-slice.md", phase7_argv_split_doc, required_phase7_argv_split_doc_markers),
    ("lib/argv_split.zig", phase7_argv_split_helper, required_phase7_argv_split_helper_markers),
    ("zigux/tests/phase7_argv_split_survey.zig", phase7_argv_split_survey, required_phase7_argv_split_survey_markers),
    ("zigux/tests/phase7_argv_split.zig", phase7_argv_split_tests, required_phase7_argv_split_test_markers),
    ("zigux/tests/phase7_rbtree_survey.zig", phase7_rbtree_survey, required_phase7_rbtree_survey_markers),
    ("zigux/tests/phase7_rbtree.zig", phase7_rbtree_tests, required_phase7_rbtree_test_markers),
    ("Documentation/zigux/phase7-cmdline-slice.md", phase7_cmdline_doc, required_phase7_cmdline_doc_markers),
    ("Documentation/zigux/phase7-rbtree-slice.md", phase7_rbtree_doc, required_phase7_rbtree_doc_markers),
]

missing_markers: list[tuple[str, str]] = []
for label, content, markers in checks:
    for marker in markers:
        if marker not in content:
            missing_markers.append((label, marker))

if missing_markers:
    print("PHASE7_VALIDATION=fail")
    print("MISSING_PHASE7_MARKERS_START")
    for label, marker in missing_markers:
        print(f"{label}: {marker}")
    print("MISSING_PHASE7_MARKERS_END")
    sys.exit(1)

expected_argv_split_gap_destinations = {
    "phase7-build-gate": "zigux/tests/phase7_build.zig",
    "phase7-argv-split-helper": "lib/argv_split.zig",
    "phase7-argv-split-dedicated-tests": "zigux/tests/phase7_argv_split.zig",
    "phase7-argv-split-shared-fixtures": "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "phase7-argv-split-slice-note": "Documentation/zigux/phase7-argv-split-slice.md",
    "phase7-argv-split-survey-gate": "zigux/tests/phase7_argv_split_survey.zig",
}

expected_rbtree_gap_destinations = {
    "phase7-build-gate": "zigux/tests/phase7_build.zig",
    "phase7-rbtree-helper": "lib/rbtree.zig",
    "phase7-rbtree-dedicated-tests": "zigux/tests/phase7_rbtree.zig",
    "phase7-rbtree-slice-note": "Documentation/zigux/phase7-rbtree-slice.md",
    "phase7-rbtree-survey-gate": "zigux/tests/phase7_rbtree_survey.zig",
    "phase7-rbtree-parity-fixture-layer": "zigux/tests/fixtures/phase7_rbtree.json",
}

manifest_shape_errors: list[str] = []
if phase7_argv_split_manifest.get("lane_key") != "P7-L12":
    manifest_shape_errors.append("lane_key")
if phase7_argv_split_manifest.get("phase") != "Phase 7":
    manifest_shape_errors.append("phase")
if phase7_argv_split_manifest.get("surveyed_commit") != "ac615fab1a13cf24fc9a45abf09b1500fb1e2ac9":
    manifest_shape_errors.append("surveyed_commit")
if phase7_argv_split_manifest.get("anchor") != "lib/argv_split.c":
    manifest_shape_errors.append("anchor")
if phase7_argv_split_manifest.get("roadmap_destinations") != ["lib/argv_split.zig"]:
    manifest_shape_errors.append("roadmap_destinations")

survey_summary = phase7_argv_split_manifest.get("survey_summary", {})
expected_summary = {
    "argv_split_c_lines": 95,
    "preexisting_phase7_test_files": 1,
    "preexisting_phase7_fixture_modules": 1,
    "preexisting_phase7_build_present": True,
    "preexisting_phase7_doc_present": True,
    "preexisting_phase7_helper_present": True,
}
for key, expected_value in expected_summary.items():
    if survey_summary.get(key) != expected_value:
        manifest_shape_errors.append(f"survey_summary:{key}")

gaps = phase7_argv_split_manifest.get("gaps")
if not isinstance(gaps, list):
    manifest_shape_errors.append("gaps")
else:
    for gap_id, destination in expected_argv_split_gap_destinations.items():
        matches = [gap for gap in gaps if gap.get("id") == gap_id]
        if len(matches) != 1:
            manifest_shape_errors.append(f"gaps:{gap_id}")
            continue
        gap = matches[0]
        if gap.get("status") != "starter_landed":
            manifest_shape_errors.append(f"gaps:{gap_id}:status")
        if gap.get("zigux_destination") != destination:
            manifest_shape_errors.append(f"gaps:{gap_id}:zigux_destination")
        if not gap.get("why_now"):
            manifest_shape_errors.append(f"gaps:{gap_id}:why_now")

if manifest_shape_errors:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_ARGV_SPLIT_MANIFEST_SHAPE_START")
    for item in manifest_shape_errors:
        print(item)
    print("PHASE7_ARGV_SPLIT_MANIFEST_SHAPE_END")
    sys.exit(1)

rbtree_manifest_shape_errors: list[str] = []
if phase7_rbtree_manifest.get("lane_key") != "P7-L13":
    rbtree_manifest_shape_errors.append("lane_key")
if phase7_rbtree_manifest.get("phase") != "Phase 7":
    rbtree_manifest_shape_errors.append("phase")
if phase7_rbtree_manifest.get("surveyed_commit") != "2d4d54a73329556a8d6dab46afef9a4aad341ef9":
    rbtree_manifest_shape_errors.append("surveyed_commit")
if phase7_rbtree_manifest.get("anchor") != "lib/rbtree.c":
    rbtree_manifest_shape_errors.append("anchor")
if phase7_rbtree_manifest.get("roadmap_destinations") != ["lib/rbtree.zig"]:
    rbtree_manifest_shape_errors.append("roadmap_destinations")

rbtree_survey_summary = phase7_rbtree_manifest.get("survey_summary", {})
expected_rbtree_summary = {
    "rbtree_c_lines": 618,
    "preexisting_phase7_test_files": 1,
    "preexisting_phase7_build_present": True,
    "preexisting_phase7_doc_present": True,
    "preexisting_phase7_helper_present": True,
}
for key, expected_value in expected_rbtree_summary.items():
    if rbtree_survey_summary.get(key) != expected_value:
        rbtree_manifest_shape_errors.append(f"survey_summary:{key}")

rbtree_gaps = phase7_rbtree_manifest.get("gaps")
if not isinstance(rbtree_gaps, list):
    rbtree_manifest_shape_errors.append("gaps")
else:
    ready_next_count = 0
    for gap_id, destination in expected_rbtree_gap_destinations.items():
        matches = [gap for gap in rbtree_gaps if gap.get("id") == gap_id]
        if len(matches) != 1:
            rbtree_manifest_shape_errors.append(f"gaps:{gap_id}")
            continue
        gap = matches[0]
        if gap.get("status") != "starter_landed":
            rbtree_manifest_shape_errors.append(f"gaps:{gap_id}:status")
        if gap.get("zigux_destination") != destination:
            rbtree_manifest_shape_errors.append(f"gaps:{gap_id}:zigux_destination")
        if not gap.get("why_now"):
            rbtree_manifest_shape_errors.append(f"gaps:{gap_id}:why_now")

        why_now = gap.get("why_now", "")
        if gap_id == "phase7-rbtree-helper":
            if "eraseInit ownership reset" not in why_now:
                rbtree_manifest_shape_errors.append("gaps:phase7-rbtree-helper:why_now:eraseInit ownership reset")
            if "duplicate-range iterator access" not in why_now:
                rbtree_manifest_shape_errors.append("gaps:phase7-rbtree-helper:why_now:duplicate-range iterator access")
        if gap_id == "phase7-rbtree-parity-fixture-layer" and "eraseInit ownership reset" not in why_now:
            rbtree_manifest_shape_errors.append(
                "gaps:phase7-rbtree-parity-fixture-layer:why_now:eraseInit ownership reset"
            )

        if gap.get("status") == "ready_next":
            ready_next_count += 1

    if ready_next_count != 0:
        rbtree_manifest_shape_errors.append("ready_next_count")

if rbtree_manifest_shape_errors:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_RBTREE_MANIFEST_SHAPE_START")
    for item in rbtree_manifest_shape_errors:
        print(item)
    print("PHASE7_RBTREE_MANIFEST_SHAPE_END")
    sys.exit(1)

phase7_build_paths = set(re.findall(r'b\.path\("([^"]+)"\)', phase7_build))
for root_path, import_path in re.findall(
    r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"([^"]+)",\s*"[^"]+",\s*"([^"]+)"',
    phase7_build,
    re.S,
):
    phase7_build_paths.add(root_path)
    phase7_build_paths.add(import_path)

for root_path in re.findall(
    r'createStandaloneTestRoot\(\s*b,\s*target,\s*optimize,\s*"([^"]+)"',
    phase7_build,
    re.S,
):
    phase7_build_paths.add(root_path)
if phase7_build_paths != expected_phase7_build_paths:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_PATH_DRIFT_START")
    missing_paths = sorted(expected_phase7_build_paths - phase7_build_paths)
    unexpected_paths = sorted(phase7_build_paths - expected_phase7_build_paths)
    for rel_path in missing_paths:
        print(f"missing:{rel_path}")
    for rel_path in unexpected_paths:
        print(f"unexpected:{rel_path}")
    print("PHASE7_BUILD_PATH_DRIFT_END")
    sys.exit(1)

missing_build_inputs = []
for rel_path in sorted(expected_phase7_build_paths):
    resolved = (PHASE7_BUILD_PATH.parent / rel_path).resolve()
    if not resolved.exists():
        missing_build_inputs.append(str(resolved.relative_to(ROOT)))

if missing_build_inputs:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_INPUTS_MISSING_START")
    for rel_path in missing_build_inputs:
        print(rel_path)
    print("PHASE7_BUILD_INPUTS_MISSING_END")
    sys.exit(1)

missing_imports = sorted(
    name
    for name, pattern in expected_phase7_import_calls.items()
    if not re.search(pattern, phase7_build, re.S)
)
if missing_imports:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_IMPORT_DRIFT_START")
    for name in missing_imports:
        print(name)
    print("PHASE7_BUILD_IMPORT_DRIFT_END")
    sys.exit(1)

missing_run_labels = sorted(label for label in expected_phase7_run_labels if label not in phase7_build)
if missing_run_labels:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_RUN_LABEL_DRIFT_START")
    for label in missing_run_labels:
        print(label)
    print("PHASE7_BUILD_RUN_LABEL_DRIFT_END")
    sys.exit(1)

run_call_pattern = re.compile(
    r'const\s+\w+\s*=\s*addTestRun\(\s*'
    r'b,\s*"([^"]+)",\s*\w+,\s*(null|repo_root)\s*,?\s*\)',
    re.S,
)
actual_run_cwds = {label: cwd for label, cwd in run_call_pattern.findall(phase7_build)}
if actual_run_cwds != expected_phase7_run_cwds:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_CWD_DRIFT_START")
    for label in sorted(expected_phase7_run_cwds):
        actual = actual_run_cwds.get(label)
        expected = expected_phase7_run_cwds[label]
        if actual != expected:
            print(f"{label}: expected={expected} actual={actual or 'missing'}")
    for label in sorted(actual_run_cwds):
        if label not in expected_phase7_run_cwds:
            print(f"{label}: unexpected={actual_run_cwds[label]}")
    print("PHASE7_BUILD_CWD_DRIFT_END")
    sys.exit(1)

actual_test_step_dependencies = set(
    re.findall(r"test_step\.dependOn\(&(\w+)\.step\);", phase7_build)
)
if actual_test_step_dependencies != expected_phase7_test_step_dependencies:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_DEPENDENCY_DRIFT_START")
    for dependency in sorted(
        expected_phase7_test_step_dependencies - actual_test_step_dependencies
    ):
        print(f"phase7-test-step: missing expected dependency edge {dependency}")
    for dependency in sorted(
        actual_test_step_dependencies - expected_phase7_test_step_dependencies
    ):
        print(f"phase7-test-step: unexpected dependency edge {dependency}")
    print("PHASE7_BUILD_DEPENDENCY_DRIFT_END")
    sys.exit(1)

unexpected_build_hits = [
    marker for marker in unexpected_phase7_build_markers if marker in phase7_build
]
if unexpected_build_hits:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_STALE_MARKERS_START")
    for marker in unexpected_build_hits:
        print(marker)
    print("PHASE7_BUILD_STALE_MARKERS_END")
    sys.exit(1)

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
        sys.exit(1)

    wrapper_output = result.stdout
    missing_wrapper_lines = [
        line for line in expected_lines if line not in wrapper_output
    ]
    if missing_wrapper_lines:
        print("PHASE7_VALIDATION=fail")
        print("PHASE7_MAKE_WRAPPER_DRIFT_START")
        print(f"{target_name}: missing expected wrapper expansion")
        for line in missing_wrapper_lines:
            print(line)
        print("PHASE7_MAKE_WRAPPER_DRIFT_END")
        sys.exit(1)

    unexpected_wrapper_lines = [
        line
        for line in unexpected_make_expansions.get(target_name, [])
        if line in wrapper_output
    ]
    if unexpected_wrapper_lines:
        print("PHASE7_VALIDATION=fail")
        print("PHASE7_MAKE_WRAPPER_DRIFT_START")
        print(f"{target_name}: unexpected wrapper expansion")
        for line in unexpected_wrapper_lines:
            print(line)
        print("PHASE7_MAKE_WRAPPER_DRIFT_END")
        sys.exit(1)

print("PHASE7_VALIDATION=pass")
print(f"PHASE7_REQUIRED_FILE_COUNT={len(required_files)}")
print(
    "PHASE7_REQUIRED_MARKER_COUNT="
    f"{sum(len(markers) for _, _, markers in checks)}"
)
