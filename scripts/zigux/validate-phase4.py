#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

REQUIRED_PATHS = (
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "scripts/zigux/check-phase4-remaining-gap-matrix.py",
    "scripts/zigux/check-phase4-repo-reality-warning.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-tests-readme-packet.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_diff_manifest.json",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
)


@dataclass(frozen=True)
class CheckSpec:
    name: str
    command: tuple[str, ...]


CHECKS = (
    CheckSpec(
        "phase4-repo-reality-warning-self-test",
        ("python", "scripts/zigux/check-phase4-repo-reality-warning.py", "--self-test"),
    ),
    CheckSpec(
        "phase4-repo-reality-warning",
        ("python", "scripts/zigux/check-phase4-repo-reality-warning.py"),
    ),
    CheckSpec(
        "phase4-reversible-delivery-pins-self-test",
        ("python", "scripts/zigux/check-phase4-reversible-delivery-pins.py", "--self-test"),
    ),
    CheckSpec(
        "phase4-reversible-delivery-pins",
        ("python", "scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    ),
    CheckSpec(
        "phase4-tests-readme-packet-self-test",
        ("python", "scripts/zigux/check-phase4-tests-readme-packet.py", "--self-test"),
    ),
    CheckSpec(
        "phase4-tests-readme-packet",
        ("python", "scripts/zigux/check-phase4-tests-readme-packet.py"),
    ),
    CheckSpec(
        "phase4-artifact-diff-helper-self-test",
        ("python", "scripts/zigux/artifact_diff.py", "--self-test"),
    ),
    CheckSpec(
        "phase4-artifact-diff-contract-self-test",
        ("python", "scripts/zigux/check-artifact-diff-contract.py", "--self-test"),
    ),
    CheckSpec(
        "phase4-artifact-diff-contract",
        ("python", "scripts/zigux/check-artifact-diff-contract.py"),
    ),
    CheckSpec(
        "phase4-artifact-diff-determinism-self-test",
        ("python", "scripts/zigux/check-phase4-artifact-diff-determinism.py", "--self-test"),
    ),
    CheckSpec(
        "phase4-artifact-diff-determinism",
        ("python", "scripts/zigux/check-phase4-artifact-diff-determinism.py"),
    ),
    CheckSpec(
        "phase4-artifact-diff-validator-replays-self-test",
        ("python", "scripts/zigux/check-phase4-artifact-diff-validator-replays.py", "--self-test"),
    ),
    CheckSpec(
        "phase4-artifact-diff-validator-replays",
        ("python", "scripts/zigux/check-phase4-artifact-diff-validator-replays.py"),
    ),
    CheckSpec(
        "phase4-gate-evidence-self-test",
        ("python", "scripts/zigux/check-phase4-gate-evidence.py", "--self-test"),
    ),
    CheckSpec(
        "phase4-gate-evidence",
        ("python", "scripts/zigux/check-phase4-gate-evidence.py"),
    ),
    CheckSpec(
        "phase4-perf-baseline-packet-self-test",
        ("python", "scripts/zigux/check-phase4-perf-baseline-packet.py", "--self-test"),
    ),
    CheckSpec(
        "phase4-perf-baseline-packet",
        ("python", "scripts/zigux/check-phase4-perf-baseline-packet.py"),
    ),
    CheckSpec(
        "phase4-remaining-gap-matrix-self-test",
        ("python", "scripts/zigux/check-phase4-remaining-gap-matrix.py", "--self-test"),
    ),
    CheckSpec(
        "phase4-remaining-gap-matrix",
        ("python", "scripts/zigux/check-phase4-remaining-gap-matrix.py"),
    ),
    CheckSpec(
        "phase4-workflow-route-counts-self-test",
        ("python", "scripts/zigux/check-phase4-workflow-route-counts.py", "--self-test"),
    ),
    CheckSpec(
        "phase4-workflow-route-counts",
        ("python", "scripts/zigux/check-phase4-workflow-route-counts.py"),
    ),
    CheckSpec(
        "phase4-build-test",
        ("zig", "build", "test", "--build-file", "zigux/tests/phase4_build.zig"),
    ),
)

REQUIRED_ARTIFACT_DOC_MARKERS = [
    "Current Phase 4 use",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_diff_survey.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/phase4-validation-matrix.md",
    "ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR]",
    "ARTIFACT_DIFF_SELF_TEST_TEXT",
    "ARTIFACT_DIFF_SELF_TEST_JSON",
    "ARTIFACT_DIFF_SELF_TEST_JSON_INVALID",
    "ARTIFACT_DIFF_SELF_TEST_MISSING",
    "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT",
    "ARTIFACT_DIFF_SELF_TEST_CASES",
    "ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT",
    "ARTIFACT_DIFF_CONTRACT_BASE_CASES",
    "ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT",
    "ARTIFACT_DIFF_CONTRACT_REPEAT_CASES",
    "ARTIFACT_DIFF_CONTRACT_CASE_COUNT",
    "ARTIFACT_DIFF_CONTRACT_CASES",
    "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT",
    "ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES",
    "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT",
    "PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES",
]

REQUIRED_ARTIFACT_MATRIX_MARKERS = [
    "`MODE=...`",
    "`EXPECTED_EXISTS=...`",
    "`ACTUAL_EXISTS=...`",
]

SAMPLE_PHASE4_VALIDATION_MATRIX_LINES = [
    "# Phase 4 Validation Matrix",
    "## Lab And CI Matrix",
    "* `scripts/zigux/check-artifact-diff-contract.py` currently keeps the external artifact-diff replay exact.",
    "* The existing external artifact-diff replay now names `MODE=...`, `EXPECTED_EXISTS=...`, and `ACTUAL_EXISTS=...` alongside the already-published JSON, SHA-256, and exit-code evidence.",
]


def command_for(spec: CheckSpec, root: Path) -> list[str]:
    command = list(spec.command)
    if not command:
        raise ValueError(f"empty command for {spec.name}")
    if command[0] == "python":
        return [sys.executable, str(root / command[1]), *command[2:]]
    if command[0] == "zig":
        return ["zig", *command[1:]]
    raise ValueError(f"unsupported command kind for {spec.name}: {command[0]}")


def is_zig_check(spec: CheckSpec) -> bool:
    return bool(spec.command) and spec.command[0] == "zig"


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def append_output(issues: list[str], prefix: str, completed: subprocess.CompletedProcess[str]) -> None:
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if stdout:
        issues.append(f"{prefix}:stdout={stdout}")
    if stderr:
        issues.append(f"{prefix}:stderr={stderr}")


def collect_issues(root: Path, *, skip_zig_builds: bool = False) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_required_path:{rel}")

    if issues:
        return issues

    artifact_doc_text = (root / "Documentation/zigux/artifact-diff.md").read_text(encoding="utf-8")
    missing_artifact_doc_markers = [
        marker for marker in REQUIRED_ARTIFACT_DOC_MARKERS if marker not in artifact_doc_text
    ]
    if missing_artifact_doc_markers:
        issues.extend(
            f"artifact_doc_marker_missing:{marker}"
            for marker in missing_artifact_doc_markers
        )

    artifact_matrix_text = (root / "Documentation/zigux/phase4-validation-matrix.md").read_text(
        encoding="utf-8"
    )
    missing_artifact_matrix_markers = [
        marker for marker in REQUIRED_ARTIFACT_MATRIX_MARKERS if marker not in artifact_matrix_text
    ]
    if missing_artifact_matrix_markers:
        issues.extend(
            f"artifact_matrix_marker_missing:{marker}"
            for marker in missing_artifact_matrix_markers
        )

    for spec in CHECKS:
        if skip_zig_builds and is_zig_check(spec):
            continue
        completed = run_command(command_for(spec, root), root)
        if completed.returncode != 0:
            issues.append(f"live_failed:{spec.name}:exit={completed.returncode}")
            append_output(issues, f"live_failed:{spec.name}", completed)

    return issues


def run_check(root: Path, *, skip_zig_builds: bool = False) -> int:
    issues = collect_issues(root, skip_zig_builds=skip_zig_builds)
    if issues:
        print("PHASE4_VALIDATION=fail")
        print("PHASE4_VALIDATION_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE4_VALIDATION_ISSUES_END")
        return 1

    print("PHASE4_VALIDATION=pass")
    print(f"PHASE4_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE4_VALIDATION_CHECK_COUNT={len(CHECKS)}")
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_stub_script(
    path: Path,
    *,
    self_test_exit_code: int = 0,
    live_exit_code: int | None = None,
) -> None:
    live_exit_literal = self_test_exit_code if live_exit_code is None else live_exit_code
    write_text(
        path,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import argparse",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--self-test', action='store_true')",
                "args = parser.parse_args()",
                f"SELF_TEST_EXIT_CODE = {self_test_exit_code}",
                f"LIVE_EXIT_CODE = {live_exit_literal}",
                "raise SystemExit(SELF_TEST_EXIT_CODE if args.self_test else LIVE_EXIT_CODE)",
            ]
        )
        + "\n",
    )
    os.chmod(path, 0o755)


def build_fake_zig(path: Path, *, fail_build_file: str | None = None) -> None:
    fail_literal = repr(fail_build_file) if fail_build_file is not None else "None"
    write_text(
        path,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import sys",
                f"FAIL_BUILD_FILE = {fail_literal}",
                "args = sys.argv[1:]",
                "if args[:2] != ['build', 'test']:",
                "    raise SystemExit(2)",
                "try:",
                "    build_file = args[args.index('--build-file') + 1]",
                "except (ValueError, IndexError):",
                "    raise SystemExit(3)",
                "if FAIL_BUILD_FILE is not None and build_file == FAIL_BUILD_FILE:",
                "    print(f'fake zig failed for {build_file}')",
                "    raise SystemExit(1)",
                "raise SystemExit(0)",
            ]
        )
        + "\n",
    )
    os.chmod(path, 0o755)


def build_sample_repo(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if rel.startswith("scripts/zigux/") and rel.endswith(".py"):
            build_stub_script(path)
            continue
        write_text(path, f"sample:{rel}\n")


def write_matrix_fixture(root: Path) -> None:
    write_text(
        root / "Documentation/zigux/phase4-validation-matrix.md",
        "\n".join(SAMPLE_PHASE4_VALIDATION_MATRIX_LINES) + "\n",
    )


def run_self_test() -> int:
    original_path = os.environ.get("PATH", "")
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_validate_") as tmp_dir:
        root = Path(tmp_dir)
        tool_root = root / ".tools"
        tool_root.mkdir(parents=True, exist_ok=True)
        fake_zig = tool_root / "zig"

        def reset_fixture(*, fail_build_file: str | None = None) -> None:
            build_sample_repo(root)
            build_fake_zig(fake_zig, fail_build_file=fail_build_file)
            write_matrix_fixture(root)

        os.environ["PATH"] = f"{tool_root}{os.pathsep}{original_path}" if original_path else str(tool_root)

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            "- `scripts/zigux/check-artifact-diff-contract.py`",
            "- `scripts/zigux/check-phase4-artifact-diff-determinism.py`",
            "- `scripts/zigux/check-phase4-gate-evidence.py`",
            "- `zigux/tests/atomic64_diff.zig`",
            "- `zigux/tests/runtime_atomic64_diff.zig`",
            "- `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`",
            "- `zigux/tests/bitmap_diff.zig`",
            "- `zigux/tests/phase4_bitmap_diff_survey.zig`",
            "- `zigux/tests/phase4_bitmap_live_helper_replay.zig`",
            "- `scripts/zigux/validate-phase4.py`",
            "- `Documentation/zigux/phase4-validation-matrix.md`",
            "",
            "## Phase 4 Tooling Review Note",
            "- `ARTIFACT_DIFF_RESULT_LINES=ARTIFACT_DIFF,MODE,EXPECTED,ACTUAL[,SHA256|EXPECTED_EXISTS|ACTUAL_EXISTS|EXPECTED_JSON_ERROR|ACTUAL_JSON_ERROR]`",
            "- `ARTIFACT_DIFF_SELF_TEST_TEXT` must prove both the stable text pass shape and the direct text mismatch fail shape",
            "- `ARTIFACT_DIFF_SELF_TEST_JSON` must prove canonical JSON equivalence while `ARTIFACT_DIFF_SELF_TEST_JSON_INVALID` proves malformed JSON fails without inventing digest or exists markers",
            "- `ARTIFACT_DIFF_SELF_TEST_MISSING` must prove missing-path failures emit only the EXISTS markers",
            "- `ARTIFACT_DIFF_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_SELF_TEST_CASES` must stay aligned with the helper's published `--self-test` packet",
            "- `ARTIFACT_DIFF_CONTRACT_BASE_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_BASE_CASES`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASE_COUNT`, `ARTIFACT_DIFF_CONTRACT_REPEAT_CASES`, `ARTIFACT_DIFF_CONTRACT_CASE_COUNT`, and `ARTIFACT_DIFF_CONTRACT_CASES` must stay aligned with the published contract replay packet",
            "- `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASE_COUNT` and `ARTIFACT_DIFF_CONTRACT_SELF_TEST_CASES` must stay aligned with the isolated stale-catalog and review-note drift coverage",
            "- `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASE_COUNT` and `PHASE4_ARTIFACT_DIFF_DETERMINISM_SELF_TEST_CASES` must stay aligned with the isolated phase4-use, review-note, helper-summary, and contract-catalog drift coverage",
        ]) + "\n")
        baseline_issues = collect_issues(root)
        if baseline_issues:
            raise SystemExit("phase4-validate-self-test:baseline_failed:" + ",".join(baseline_issues))

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            "- `scripts/zigux/check-phase4-artifact-diff-determinism.py`",
        ]) + "\n")
        issues = collect_issues(root)
        expected_missing = "artifact_doc_marker_missing:scripts/zigux/check-artifact-diff-contract.py"
        if expected_missing not in issues:
            raise SystemExit(
                "phase4-validate-self-test:artifact_doc_marker_missing_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(
            root / "Documentation/zigux/phase4-validation-matrix.md",
            "\n".join(
                line for line in SAMPLE_PHASE4_VALIDATION_MATRIX_LINES if "`EXPECTED_EXISTS=...`" not in line
            ) + "\n",
        )
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        issues = collect_issues(root)
        expected_missing = "artifact_matrix_marker_missing:`EXPECTED_EXISTS=...`"
        if expected_missing not in issues:
            raise SystemExit(
                "phase4-validate-self-test:artifact_matrix_marker_missing_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        repo_reality = root / "scripts/zigux/check-phase4-repo-reality-warning.py"
        build_stub_script(repo_reality, self_test_exit_code=1, live_exit_code=0)
        issues = collect_issues(root)
        expected = "live_failed:phase4-repo-reality-warning-self-test:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:repo_reality_warning_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        pins = root / "scripts/zigux/check-phase4-reversible-delivery-pins.py"
        build_stub_script(pins, self_test_exit_code=1, live_exit_code=0)
        issues = collect_issues(root)
        expected = "live_failed:phase4-reversible-delivery-pins-self-test:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:reversible_delivery_pins_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        tests_readme = root / "scripts/zigux/check-phase4-tests-readme-packet.py"
        build_stub_script(tests_readme, self_test_exit_code=0, live_exit_code=1)
        issues = collect_issues(root)
        expected = "live_failed:phase4-tests-readme-packet:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:tests_readme_packet_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        helper = root / "scripts/zigux/artifact_diff.py"
        build_stub_script(helper, self_test_exit_code=1, live_exit_code=0)
        issues = collect_issues(root)
        expected = "live_failed:phase4-artifact-diff-helper-self-test:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:artifact_diff_helper_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        contract = root / "scripts/zigux/check-artifact-diff-contract.py"
        build_stub_script(contract, self_test_exit_code=0, live_exit_code=1)
        issues = collect_issues(root)
        expected = "live_failed:phase4-artifact-diff-contract:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:artifact_diff_contract_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        determinism = root / "scripts/zigux/check-phase4-artifact-diff-determinism.py"
        build_stub_script(determinism, self_test_exit_code=1, live_exit_code=0)
        issues = collect_issues(root)
        expected = "live_failed:phase4-artifact-diff-determinism-self-test:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:artifact_diff_determinism_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        validator_replays = root / "scripts/zigux/check-phase4-artifact-diff-validator-replays.py"
        build_stub_script(validator_replays, self_test_exit_code=0, live_exit_code=1)
        issues = collect_issues(root)
        expected = "live_failed:phase4-artifact-diff-validator-replays:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:artifact_diff_validator_replays_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        gate = root / "scripts/zigux/check-phase4-gate-evidence.py"
        build_stub_script(gate, self_test_exit_code=1, live_exit_code=0)
        issues = collect_issues(root)
        expected = "live_failed:phase4-gate-evidence-self-test:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:gate_evidence_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        gate = root / "scripts/zigux/check-phase4-gate-evidence.py"
        build_stub_script(gate, self_test_exit_code=0, live_exit_code=1)
        issues = collect_issues(root)
        expected = "live_failed:phase4-gate-evidence:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:gate_evidence_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        perf_baseline = root / "scripts/zigux/check-phase4-perf-baseline-packet.py"
        build_stub_script(perf_baseline, self_test_exit_code=0, live_exit_code=1)
        issues = collect_issues(root)
        expected = "live_failed:phase4-perf-baseline-packet:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:perf_baseline_packet_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        remaining_gap = root / "scripts/zigux/check-phase4-remaining-gap-matrix.py"
        build_stub_script(remaining_gap, self_test_exit_code=0, live_exit_code=1)
        issues = collect_issues(root)
        expected = "live_failed:phase4-remaining-gap-matrix:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:remaining_gap_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture()
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        routes = root / "scripts/zigux/check-phase4-workflow-route-counts.py"
        build_stub_script(routes, self_test_exit_code=1, live_exit_code=0)
        issues = collect_issues(root)
        expected = "live_failed:phase4-workflow-route-counts-self-test:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:workflow_route_counts_self_test_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture(fail_build_file="zigux/tests/phase4_build.zig")
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        issues = collect_issues(root)
        expected = "live_failed:phase4-build-test:exit=1"
        if expected not in issues:
            raise SystemExit(
                "phase4-validate-self-test:zig_build_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        reset_fixture(fail_build_file="zigux/tests/phase4_build.zig")
        write_text(root / "Documentation/zigux/artifact-diff.md", "\n".join([
            "# Artifact Diff Policy",
            "",
            "Current Phase 4 use",
            *[f"- `{marker}`" for marker in REQUIRED_ARTIFACT_DOC_MARKERS[1:]],
        ]) + "\n")
        issues = collect_issues(root, skip_zig_builds=True)
        if issues:
            raise SystemExit(
                "phase4-validate-self-test:skip_zig_builds_not_honored:" + ",".join(issues)
            )

    os.environ["PATH"] = original_path
    print("PHASE4_VALIDATE_SELF_TEST=pass")
    print("PHASE4_VALIDATE_SELF_TEST_CASE_COUNT=17")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--skip-zig-builds", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        return run_check(args.root.resolve(), skip_zig_builds=args.skip_zig_builds)
    except Exception as exc:  # pragma: no cover - defensive top-level guard
        print(f"PHASE4_VALIDATION=fail: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())