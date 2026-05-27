#!/usr/bin/env python3
"""Guard the Phase 4 local-only perf boundary against shared-route drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MANIFEST = Path("zigux/tests/phase4_perf_baseline_manifest.json")
VALIDATOR = Path("scripts/zigux/validate-phase4.py")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
BUILD = Path("zigux/tests/phase4_build.zig")

EXPECTED_SELF_TEST_CASES = 9

MANIFEST_MARKERS = (
    '"shared_ci_perf_promotion_status": "pending"',
    '"bootstrap_ci_posture": "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow"',
    '"dedicated_local_survey_wrapper": "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig"',
    '"dedicated_linux_style_survey_wrapper": "make -C zigux phase4-perf-baseline-survey"',
)

VALIDATOR_REQUIRED_MARKERS = (
    'CheckSpec("phase4-perf-baseline-packet-self-test", ("python", "scripts/zigux/check-phase4-perf-baseline-packet.py", "--self-test"))',
    'CheckSpec("phase4-perf-baseline-packet", ("python", "scripts/zigux/check-phase4-perf-baseline-packet.py"))',
    'CheckSpec("phase4-perf-threshold-matrix-self-test", ("python", "scripts/zigux/check-phase4-perf-threshold-matrix.py", "--self-test"))',
    'CheckSpec("phase4-perf-threshold-matrix", ("python", "scripts/zigux/check-phase4-perf-threshold-matrix.py"))',
)

VALIDATOR_FORBIDDEN_MARKERS = (
    'CheckSpec("phase4-perf-baseline-survey",',
    '("zig", "build", "phase4-perf-baseline-survey", "--build-file", "zigux/tests/phase4_build.zig")',
)

MAKEFILE_REQUIRED_MARKERS = (
    "phase4-validate:",
    "phase4-perf-baseline-survey:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-baseline-packet.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-threshold-matrix.py",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
)

WORKFLOW_REQUIRED_MARKERS = (
    "- name: Validate Phase 4 rollback routes",
    "run: make -C zigux phase4-validate",
)

WORKFLOW_FORBIDDEN_MARKERS = (
    "run: make -C zigux phase4-perf-baseline-survey",
    "run: zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
)

BUILD_REQUIRED_MARKERS = (
    '"phase4-perf-baseline-survey-tests"',
    '"phase4-perf-baseline-survey",',
    "perf_baseline_survey_step.dependOn(&run_perf_baseline_survey_tests.step);",
)

BUILD_FORBIDDEN_MARKERS = (
    "test_step.dependOn(&run_perf_baseline_survey_tests.step);",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixture self-test")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_markers(text: str, markers: tuple[str, ...], label: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append(f"{label}:{marker}")


def forbid_markers(text: str, markers: tuple[str, ...], label: str, issues: list[str]) -> None:
    for marker in markers:
        if marker in text:
            issues.append(f"{label}:{marker}")


def target_body(makefile_text: str, target: str) -> list[str]:
    lines = makefile_text.splitlines()
    body: list[str] = []
    capture = False
    target_prefix = f"{target}:"
    for line in lines:
        if capture:
            if not line.startswith("\t"):
                break
            body.append(line)
            continue
        if line.startswith(target_prefix):
            capture = True
    return body


def validate_root(root: Path) -> list[str]:
    issues: list[str] = []
    manifest_path = root / MANIFEST
    validator_path = root / VALIDATOR
    makefile_path = root / MAKEFILE
    workflow_path = root / WORKFLOW
    build_path = root / BUILD

    for path in (manifest_path, validator_path, makefile_path, workflow_path, build_path):
        if not path.is_file():
            issues.append(f"file:{path.relative_to(root).as_posix()}")
    if issues:
        return issues

    manifest_text = read_text(manifest_path)
    validator_text = read_text(validator_path)
    makefile_text = read_text(makefile_path)
    workflow_text = read_text(workflow_path)
    build_text = read_text(build_path)

    require_markers(manifest_text, MANIFEST_MARKERS, "manifest_marker", issues)
    require_markers(validator_text, VALIDATOR_REQUIRED_MARKERS, "validator_required", issues)
    forbid_markers(validator_text, VALIDATOR_FORBIDDEN_MARKERS, "validator_forbidden", issues)
    require_markers(makefile_text, MAKEFILE_REQUIRED_MARKERS, "makefile_marker", issues)
    require_markers(workflow_text, WORKFLOW_REQUIRED_MARKERS, "workflow_required", issues)
    forbid_markers(workflow_text, WORKFLOW_FORBIDDEN_MARKERS, "workflow_forbidden", issues)
    require_markers(build_text, BUILD_REQUIRED_MARKERS, "build_required", issues)
    forbid_markers(build_text, BUILD_FORBIDDEN_MARKERS, "build_forbidden", issues)

    phase4_validate_body = target_body(makefile_text, "phase4-validate")
    perf_validate_command = "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig"
    if perf_validate_command in phase4_validate_body:
        issues.append(f"makefile_phase4_validate_forbidden:{perf_validate_command}")

    return issues


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing replacement target: {old!r}")
    return text.replace(old, new, 1)


def build_fixture_tree(root: Path) -> None:
    manifest_data = {
        "shared_ci_perf_promotion_status": "pending",
        "bootstrap_ci_posture": "reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
        "dedicated_local_survey_wrapper": "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
        "dedicated_linux_style_survey_wrapper": "make -C zigux phase4-perf-baseline-survey",
    }
    write_text(root / MANIFEST, json.dumps(manifest_data, indent=2) + "\n")
    write_text(
        root / VALIDATOR,
        """CheckSpec("phase4-perf-baseline-packet-self-test", ("python", "scripts/zigux/check-phase4-perf-baseline-packet.py", "--self-test"))
CheckSpec("phase4-perf-baseline-packet", ("python", "scripts/zigux/check-phase4-perf-baseline-packet.py"))
CheckSpec("phase4-perf-threshold-matrix-self-test", ("python", "scripts/zigux/check-phase4-perf-threshold-matrix.py", "--self-test"))
CheckSpec("phase4-perf-threshold-matrix", ("python", "scripts/zigux/check-phase4-perf-threshold-matrix.py"))
""",
    )
    write_text(
        root / MAKEFILE,
        """phase4-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-baseline-packet.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-threshold-matrix.py

phase4-perf-baseline-survey:
\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig
""",
    )
    write_text(
        root / WORKFLOW,
        """- name: Validate Phase 4 rollback routes
  run: make -C zigux phase4-validate
""",
    )
    write_text(
        root / BUILD,
        """"phase4-perf-baseline-survey-tests"
"phase4-perf-baseline-survey",
perf_baseline_survey_step.dependOn(&run_perf_baseline_survey_tests.step);
""",
    )


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(item.startswith(expected_prefix) for item in validate_root(root))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-perf-local-only-boundary-") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        if validate_root(root):
            print("PHASE4_PERF_LOCAL_ONLY_BOUNDARY_SELF_TEST=fail")
            print("baseline fixture did not validate cleanly")
            return 1

        cases = 1
        variants = (
            (
                MANIFEST,
                '"shared_ci_perf_promotion_status": "pending"',
                '"shared_ci_perf_promotion_status": "approved"',
                "manifest_marker:\"shared_ci_perf_promotion_status\": \"pending\"",
            ),
            (
                VALIDATOR,
                'CheckSpec("phase4-perf-threshold-matrix", ("python", "scripts/zigux/check-phase4-perf-threshold-matrix.py"))\n',
                "",
                'validator_required:CheckSpec("phase4-perf-threshold-matrix", ("python", "scripts/zigux/check-phase4-perf-threshold-matrix.py"))',
            ),
            (
                VALIDATOR,
                'CheckSpec("phase4-perf-threshold-matrix", ("python", "scripts/zigux/check-phase4-perf-threshold-matrix.py"))\n',
                'CheckSpec("phase4-perf-threshold-matrix", ("python", "scripts/zigux/check-phase4-perf-threshold-matrix.py"))\nCheckSpec("phase4-perf-baseline-survey", ("zig", "build", "phase4-perf-baseline-survey", "--build-file", "zigux/tests/phase4_build.zig"))\n',
                'validator_forbidden:CheckSpec("phase4-perf-baseline-survey",',
            ),
            (
                MAKEFILE,
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-threshold-matrix.py\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-threshold-matrix.py\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\n",
                "makefile_phase4_validate_forbidden:\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
            ),
            (
                WORKFLOW,
                "run: make -C zigux phase4-validate\n",
                "run: make -C zigux phase4-validate\n- name: Run Phase 4 perf survey\n  run: make -C zigux phase4-perf-baseline-survey\n",
                "workflow_forbidden:run: make -C zigux phase4-perf-baseline-survey",
            ),
            (
                BUILD,
                "perf_baseline_survey_step.dependOn(&run_perf_baseline_survey_tests.step);\n",
                "perf_baseline_survey_step.dependOn(&run_perf_baseline_survey_tests.step);\ntest_step.dependOn(&run_perf_baseline_survey_tests.step);\n",
                "build_forbidden:test_step.dependOn(&run_perf_baseline_survey_tests.step);",
            ),
            (
                MAKEFILE,
                "phase4-perf-baseline-survey:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig\n",
                "",
                "makefile_marker:phase4-perf-baseline-survey:",
            ),
        )
        for rel, old, new, expected_prefix in variants:
            build_fixture_tree(root)
            target = root / rel
            write_text(target, replace_once(read_text(target), old, new))
            if not expect_failure(root, expected_prefix):
                print("PHASE4_PERF_LOCAL_ONLY_BOUNDARY_SELF_TEST=fail")
                print(f"drift case did not fail closed: {expected_prefix}")
                return 1
            cases += 1

        build_fixture_tree(root)
        (root / VALIDATOR).unlink()
        if not expect_failure(root, f"file:{VALIDATOR.as_posix()}"):
            print("PHASE4_PERF_LOCAL_ONLY_BOUNDARY_SELF_TEST=fail")
            print("missing validator file case did not fail closed")
            return 1
        cases += 1

        if cases != EXPECTED_SELF_TEST_CASES:
            print("PHASE4_PERF_LOCAL_ONLY_BOUNDARY_SELF_TEST=fail")
            print(f"expected {EXPECTED_SELF_TEST_CASES} self-test cases, saw {cases}")
            return 1

    print("PHASE4_PERF_LOCAL_ONLY_BOUNDARY_SELF_TEST=pass")
    print(f"PHASE4_PERF_LOCAL_ONLY_BOUNDARY_SELF_TEST_CASES={EXPECTED_SELF_TEST_CASES}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    issues = validate_root(Path(args.root).resolve())
    if issues:
        print("PHASE4_PERF_LOCAL_ONLY_BOUNDARY=fail")
        for item in issues:
            print(item)
        return 1
    print("PHASE4_PERF_LOCAL_ONLY_BOUNDARY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
