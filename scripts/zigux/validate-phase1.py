#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BENCH_EXPECTATIONS_REL = Path("zigux/tests/fixtures/phase1_bench_expectations.json")
ARTIFACT_DIFF_HELPER_REL = Path("scripts/zigux/artifact_diff.py")
PHASE1_PARITY_ARTIFACT_PACKET_REL = Path("scripts/zigux/check-phase1-parity-artifact-packet.py")
PHASE1_HELPERS_FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
PHASE1_HELPER_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
PHASE1_REPLAY_BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")

REQUIRED_PATHS = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_host_tools_smoke.zig",
)


@dataclass(frozen=True)
class CheckSpec:
    name: str
    script_rel: str
    self_test_args: tuple[str, ...]
    live_args: tuple[str, ...]
    required: bool = True
    requires: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationSummary:
    mandatory_live_run_count: int
    mandatory_live_skip_count: int
    mandatory_live_run_names: tuple[str, ...]
    mandatory_live_skip_notes: tuple[str, ...]
    optional_run_count: int
    optional_skip_count: int
    optional_run_names: tuple[str, ...]
    optional_skip_notes: tuple[str, ...]


MANDATORY_CHECKS = (
    CheckSpec("phase1-closure", "scripts/zigux/validate-phase1-closure.py", ("--self-test",), ("--root", "{root}")),
    CheckSpec(
        "phase1-string-review-packet",
        "scripts/zigux/check-phase1-string-review-packet.py",
        ("--self-test",),
        ("--root", "{root}"),
    ),
    CheckSpec(
        "phase1-direct-owner-markers",
        "scripts/zigux/check-phase1-direct-owner-markers.py",
        ("--self-test",),
        ("--root", "{root}"),
    ),
    CheckSpec("phase1-bench-self-test", "scripts/zigux/check-phase1-bench.py", ("--self-test",), ()),
)

OPTIONAL_CHECKS = (
    CheckSpec(
        "phase1-replay-blockers",
        "scripts/zigux/check-phase1-replay-blockers.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
        requires=(str(PHASE1_REPLAY_BLOCKERS_REL),),
    ),
    CheckSpec(
        "phase1-direct-anchor-manifest-gate",
        "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
    ),
    CheckSpec(
        "phase1-parity",
        "scripts/zigux/check-phase1-parity.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
        requires=(str(PHASE1_REPLAY_BLOCKERS_REL),),
    ),
    CheckSpec(
        "artifact-diff-contract",
        "scripts/zigux/check-artifact-diff-contract.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
        requires=(str(ARTIFACT_DIFF_HELPER_REL),),
    ),
    CheckSpec(
        "phase1-parity-artifact-packet",
        str(PHASE1_PARITY_ARTIFACT_PACKET_REL),
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
        requires=(
            str(ARTIFACT_DIFF_HELPER_REL),
            str(PHASE1_HELPERS_FIXTURE_REL),
            str(PHASE1_HELPER_MANIFEST_REL),
            str(PHASE1_REPLAY_BLOCKERS_REL),
        ),
    ),
    CheckSpec(
        "phase1-helper-lane-sequencing",
        "scripts/zigux/check-phase1-helper-lane-sequencing.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
        requires=(str(SCRIPTS_README_REL), str(PHASE1_HELPER_MANIFEST_REL)),
    ),
    CheckSpec(
        "phase1-scripts-repo-reality",
        "scripts/zigux/check-phase1-scripts-repo-reality.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
        requires=(str(SCRIPTS_README_REL),),
    ),
    CheckSpec(
        "phase1-scripts-readme-alignment",
        "scripts/zigux/check-phase1-scripts-readme-alignment.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
    ),
    CheckSpec(
        "phase1-shared-fixture-gate",
        "scripts/zigux/check-phase1-shared-fixture-gate.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
        requires=(str(PHASE1_HELPERS_FIXTURE_REL),),
    ),
    CheckSpec(
        "phase1-shared-replay-roster",
        "scripts/zigux/check-phase1-shared-replay-roster.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
        requires=(str(PHASE1_HELPERS_FIXTURE_REL), str(PHASE1_REPLAY_BLOCKERS_REL)),
    ),
    CheckSpec(
        "phase1-shared-helper-manifest-gate",
        "scripts/zigux/check-phase1-shared-helper-manifest-gate.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
        requires=(str(PHASE1_HELPER_MANIFEST_REL),),
    ),
    CheckSpec(
        "phase1-fixture-manifest-alignment",
        "scripts/zigux/check-phase1-fixture-manifest-alignment.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
        requires=(
            str(PHASE1_HELPERS_FIXTURE_REL),
            str(PHASE1_HELPER_MANIFEST_REL),
            str(PHASE1_REPLAY_BLOCKERS_REL),
        ),
    ),
    CheckSpec(
        "phase1-c-harness-blockers",
        "scripts/zigux/check-phase1-c-harness-blockers.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
        requires=(str(PHASE1_REPLAY_BLOCKERS_REL),),
    ),
    CheckSpec(
        "phase1-readme-replay-blockers",
        "scripts/zigux/check-phase1-readme-replay-blockers.py",
        ("--self-test",),
        ("--root", "{root}"),
        required=False,
        requires=(str(SCRIPTS_README_REL), str(PHASE1_REPLAY_BLOCKERS_REL)),
    ),
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT.resolve()


def command_for(spec: CheckSpec, root: Path, *, self_test: bool) -> list[str]:
    script_path = root / spec.script_rel
    raw_args = spec.self_test_args if self_test else spec.live_args
    return [sys.executable, str(script_path), *[arg.format(root=str(root)) for arg in raw_args]]


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True, cwd=cwd)


def append_output(issues: list[str], prefix: str, completed: subprocess.CompletedProcess[str]) -> None:
    if completed.stdout.strip():
        issues.append(f"{prefix}:stdout={completed.stdout.strip()}")
    if completed.stderr.strip():
        issues.append(f"{prefix}:stderr={completed.stderr.strip()}")


def classify_required_path(path: Path, relative_path: str) -> str | None:
    if not path.exists():
        return f"missing_required_path:{relative_path}"
    if not path.is_file():
        return f"required_path_not_file:{relative_path}"
    return None


def duplicate_values(values: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return tuple(duplicates)


def collect_roster_issues(
    mandatory_checks: tuple[CheckSpec, ...], optional_checks: tuple[CheckSpec, ...]
) -> list[str]:
    issues: list[str] = []
    for name in duplicate_values(tuple(spec.name for spec in mandatory_checks)):
        issues.append(f"duplicate_mandatory_check_name:{name}")
    for script_rel in duplicate_values(tuple(spec.script_rel for spec in mandatory_checks)):
        issues.append(f"duplicate_mandatory_check_script:{script_rel}")
    for name in duplicate_values(tuple(spec.name for spec in optional_checks)):
        issues.append(f"duplicate_optional_check_name:{name}")
    for script_rel in duplicate_values(tuple(spec.script_rel for spec in optional_checks)):
        issues.append(f"duplicate_optional_check_script:{script_rel}")
    for name in sorted({spec.name for spec in mandatory_checks} & {spec.name for spec in optional_checks}):
        issues.append(f"overlapping_check_name:{name}")
    for script_rel in sorted({spec.script_rel for spec in mandatory_checks} & {spec.script_rel for spec in optional_checks}):
        issues.append(f"overlapping_check_script:{script_rel}")
    return issues


def should_run_optional(spec: CheckSpec, root: Path) -> tuple[bool, str | None]:
    failure = classify_required_path(root / spec.script_rel, spec.script_rel)
    if failure is not None:
        if failure.startswith("missing_required_path:"):
            return (False, "missing_script")
        if failure.startswith("required_path_not_file:"):
            return (False, "script_not_file")
        return (False, failure)
    for relative_path in spec.requires:
        failure = classify_required_path(root / relative_path, relative_path)
        if failure is not None:
            return (False, failure)
    return (True, None)


def summary_from_state(
    mandatory_live_run_names: list[str],
    mandatory_live_skip_notes: list[str],
    optional_run_names: list[str],
    optional_skip_notes: list[str],
) -> ValidationSummary:
    return ValidationSummary(
        mandatory_live_run_count=len(mandatory_live_run_names),
        mandatory_live_skip_count=len(mandatory_live_skip_notes),
        mandatory_live_run_names=tuple(mandatory_live_run_names),
        mandatory_live_skip_notes=tuple(mandatory_live_skip_notes),
        optional_run_count=len(optional_run_names),
        optional_skip_count=len(optional_skip_notes),
        optional_run_names=tuple(optional_run_names),
        optional_skip_notes=tuple(optional_skip_notes),
    )


def collect_issues(
    root: Path,
    *,
    mandatory_checks: tuple[CheckSpec, ...] = MANDATORY_CHECKS,
    optional_checks: tuple[CheckSpec, ...] = OPTIONAL_CHECKS,
) -> tuple[list[str], list[str], ValidationSummary]:
    issues: list[str] = []
    notes: list[str] = []
    mandatory_live_run_names: list[str] = []
    mandatory_live_skip_notes: list[str] = []
    optional_run_names: list[str] = []
    optional_skip_notes: list[str] = []
    mandatory_self_test_failures: set[str] = set()

    issues.extend(collect_roster_issues(mandatory_checks, optional_checks))
    if issues:
        return issues, notes, summary_from_state(
            mandatory_live_run_names, mandatory_live_skip_notes, optional_run_names, optional_skip_notes
        )

    for rel in REQUIRED_PATHS:
        failure = classify_required_path(root / rel, rel)
        if failure is not None:
            issues.append(failure)
    if issues:
        return issues, notes, summary_from_state(
            mandatory_live_run_names, mandatory_live_skip_notes, optional_run_names, optional_skip_notes
        )

    for spec in mandatory_checks:
        result = run_command(command_for(spec, root, self_test=True), root)
        if result.returncode != 0:
            mandatory_self_test_failures.add(spec.name)
            issues.append(f"mandatory_self_test_failed:{spec.name}:exit={result.returncode}")
            append_output(issues, f"mandatory_self_test_failed:{spec.name}", result)

    for spec in mandatory_checks:
        if spec.name == "phase1-bench-self-test":
            continue
        if spec.name in mandatory_self_test_failures:
            skip_note = f"skipped_mandatory_live:{spec.name}:self_test_failed"
            notes.append(skip_note)
            mandatory_live_skip_notes.append(skip_note)
            continue
        mandatory_live_run_names.append(spec.name)
        result = run_command(command_for(spec, root, self_test=False), root)
        if result.returncode != 0:
            issues.append(f"mandatory_live_failed:{spec.name}:exit={result.returncode}")
            append_output(issues, f"mandatory_live_failed:{spec.name}", result)

    bench_spec = next(spec for spec in mandatory_checks if spec.name == "phase1-bench-self-test")
    bench_expectations = root / BENCH_EXPECTATIONS_REL
    if bench_spec.name in mandatory_self_test_failures:
        skip_note = f"skipped_mandatory_live:{bench_spec.name}:self_test_failed"
        notes.extend(("skipped_bench_live:self_test_failed", skip_note))
        mandatory_live_skip_notes.append(skip_note)
    else:
        bench_failure = classify_required_path(bench_expectations, str(BENCH_EXPECTATIONS_REL))
        if bench_failure is None:
            mandatory_live_run_names.append(bench_spec.name)
            result = run_command([sys.executable, str(root / bench_spec.script_rel)], root)
            if result.returncode != 0:
                issues.append(f"bench_live_failed:exit={result.returncode}")
                append_output(issues, "bench_live_failed", result)
        else:
            skip_note = f"skipped_mandatory_live:{bench_spec.name}:{bench_failure}"
            notes.extend((f"skipped_bench_live:{bench_failure}", skip_note))
            mandatory_live_skip_notes.append(skip_note)

    for spec in optional_checks:
        should_run, reason = should_run_optional(spec, root)
        if not should_run:
            skip_note = f"skipped_optional:{spec.name}:{reason}"
            notes.append(skip_note)
            optional_skip_notes.append(skip_note)
            continue
        result = run_command(command_for(spec, root, self_test=True), root)
        if result.returncode != 0:
            issues.append(f"optional_self_test_failed:{spec.name}:exit={result.returncode}")
            append_output(issues, f"optional_self_test_failed:{spec.name}", result)
            skip_note = f"skipped_optional:{spec.name}:self_test_failed"
            notes.append(skip_note)
            optional_skip_notes.append(skip_note)
            continue
        optional_run_names.append(spec.name)
        result = run_command(command_for(spec, root, self_test=False), root)
        if result.returncode != 0:
            issues.append(f"optional_live_failed:{spec.name}:exit={result.returncode}")
            append_output(issues, f"optional_live_failed:{spec.name}", result)

    return issues, notes, summary_from_state(
        mandatory_live_run_names, mandatory_live_skip_notes, optional_run_names, optional_skip_notes
    )


def emit_summary(summary: ValidationSummary, notes: list[str], *, success: bool) -> int:
    print(f"PHASE1_VALIDATION={'pass' if success else 'fail'}")
    if success:
        print(f"PHASE1_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
        print(f"PHASE1_VALIDATION_MANDATORY_CHECK_COUNT={len(MANDATORY_CHECKS)}")
        print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_COUNT={len(OPTIONAL_CHECKS)}")
    print(f"PHASE1_VALIDATION_MANDATORY_LIVE_CHECK_RUN_COUNT={summary.mandatory_live_run_count}")
    print(f"PHASE1_VALIDATION_MANDATORY_LIVE_CHECK_SKIP_COUNT={summary.mandatory_live_skip_count}")
    for name in summary.mandatory_live_run_names:
        print(f"PHASE1_VALIDATION_MANDATORY_LIVE_CHECK_RUN={name}")
    for note in summary.mandatory_live_skip_notes:
        print(f"PHASE1_VALIDATION_MANDATORY_LIVE_CHECK_SKIP={note}")
    print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_RUN_COUNT={summary.optional_run_count}")
    print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_SKIP_COUNT={summary.optional_skip_count}")
    for name in summary.optional_run_names:
        print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_RUN={name}")
    for note in summary.optional_skip_notes:
        print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_SKIP={note}")
    print(f"PHASE1_VALIDATION_NOTE_COUNT={len(notes)}")
    for note in notes:
        print(f"PHASE1_VALIDATION_NOTE={note}")
    return 0 if success else 1


def run_check(root: Path) -> int:
    issues, notes, summary = collect_issues(root)
    if issues:
        print("PHASE1_VALIDATION_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_VALIDATION_ISSUES_END")
        if notes:
            print("PHASE1_VALIDATION_NOTES_START")
            for note in notes:
                print(note)
            print("PHASE1_VALIDATION_NOTES_END")
        return emit_summary(summary, notes, success=False)
    return emit_summary(summary, notes, success=True)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_stub_script(path: Path, *, self_test_exit: int = 0, live_exit: int = 0) -> None:
    write_text(
        path,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import argparse",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--self-test', action='store_true')",
                "parser.add_argument('--root')",
                "args = parser.parse_args()",
                f"SELF_TEST_EXIT = {self_test_exit}",
                f"LIVE_EXIT = {live_exit}",
                "raise SystemExit(SELF_TEST_EXIT if args.self_test else LIVE_EXIT)",
            ]
        )
        + "\n",
    )
    os.chmod(path, 0o755)


def build_sample_repo(
    root: Path,
    *,
    mandatory_checks: tuple[CheckSpec, ...] = MANDATORY_CHECKS,
    optional_checks: tuple[CheckSpec, ...] = OPTIONAL_CHECKS,
) -> None:
    for rel in REQUIRED_PATHS:
        write_text(root / rel, f"sample:{rel}\n")
    for spec in mandatory_checks:
        build_stub_script(root / spec.script_rel)
    for spec in optional_checks:
        build_stub_script(root / spec.script_rel)
    write_text(root / BENCH_EXPECTATIONS_REL, '{\n  "status": "pass"\n}\n')
    write_text(root / ARTIFACT_DIFF_HELPER_REL, "helper\n")
    write_text(root / PHASE1_HELPERS_FIXTURE_REL, '{\n  "status": "pass"\n}\n')
    write_text(root / PHASE1_REPLAY_BLOCKERS_REL, '{\n  "status": "parked"\n}\n')
    write_text(root / PHASE1_HELPER_MANIFEST_REL, '{\n  "status": "closed"\n}\n')


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_validate_phase1_") as tmp_dir:
        base = Path(tmp_dir)

        success_root = base / "success"
        build_sample_repo(success_root)
        issues, notes, summary = collect_issues(success_root)
        assert issues == [], issues
        assert notes == [], notes
        assert summary.mandatory_live_run_count == len(MANDATORY_CHECKS), summary
        assert summary.mandatory_live_skip_count == 0, summary
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        missing_optional_root = base / "missing_optional"
        build_sample_repo(missing_optional_root)
        (missing_optional_root / "scripts/zigux/check-phase1-parity.py").unlink()
        issues, notes, summary = collect_issues(missing_optional_root)
        assert issues == [], issues
        assert "skipped_optional:phase1-parity:missing_script" in notes, notes
        assert summary.optional_run_count == len(OPTIONAL_CHECKS) - 1, summary
        assert summary.optional_skip_count == 1, summary
        case_count += 1

        optional_directory_root = base / "optional_directory"
        build_sample_repo(optional_directory_root)
        optional_dir = optional_directory_root / "scripts/zigux/check-phase1-shared-replay-roster.py"
        optional_dir.unlink()
        optional_dir.mkdir()
        issues, notes, summary = collect_issues(optional_directory_root)
        assert issues == [], issues
        assert "skipped_optional:phase1-shared-replay-roster:script_not_file" in notes, notes
        assert summary.optional_skip_count == 1, summary
        case_count += 1

        missing_required_root = base / "missing_required"
        build_sample_repo(missing_required_root)
        (missing_required_root / "zigux/tests/README.md").unlink()
        issues, notes, summary = collect_issues(missing_required_root)
        assert "missing_required_path:zigux/tests/README.md" in issues, issues
        assert summary.mandatory_live_run_count == 0, summary
        case_count += 1

        required_directory_root = base / "required_directory"
        build_sample_repo(required_directory_root)
        required_dir = required_directory_root / "Documentation/zigux/review-checklist.md"
        required_dir.unlink()
        required_dir.mkdir()
        issues, notes, summary = collect_issues(required_directory_root)
        assert "required_path_not_file:Documentation/zigux/review-checklist.md" in issues, issues
        assert summary.mandatory_live_run_count == 0, summary
        case_count += 1

        bench_missing_root = base / "bench_missing"
        build_sample_repo(bench_missing_root)
        (bench_missing_root / BENCH_EXPECTATIONS_REL).unlink()
        issues, notes, summary = collect_issues(bench_missing_root)
        assert issues == [], issues
        assert (
            "skipped_mandatory_live:phase1-bench-self-test:missing_required_path:"
            f"{BENCH_EXPECTATIONS_REL}"
        ) in summary.mandatory_live_skip_notes, summary
        case_count += 1

        bench_directory_root = base / "bench_directory"
        build_sample_repo(bench_directory_root)
        bench_path = bench_directory_root / BENCH_EXPECTATIONS_REL
        bench_path.unlink()
        bench_path.mkdir()
        issues, notes, summary = collect_issues(bench_directory_root)
        assert issues == [], issues
        assert (
            "skipped_mandatory_live:phase1-bench-self-test:required_path_not_file:"
            f"{BENCH_EXPECTATIONS_REL}"
        ) in summary.mandatory_live_skip_notes, summary
        case_count += 1

        mandatory_self_test_fail_root = base / "mandatory_self_test_fail"
        build_sample_repo(mandatory_self_test_fail_root)
        build_stub_script(
            mandatory_self_test_fail_root / "scripts/zigux/check-phase1-string-review-packet.py",
            self_test_exit=1,
        )
        issues, notes, summary = collect_issues(mandatory_self_test_fail_root)
        assert "mandatory_self_test_failed:phase1-string-review-packet:exit=1" in issues, issues
        assert "skipped_mandatory_live:phase1-string-review-packet:self_test_failed" in notes, notes
        assert "phase1-string-review-packet" not in summary.mandatory_live_run_names, summary
        case_count += 1

        bench_self_test_fail_root = base / "bench_self_test_fail"
        build_sample_repo(bench_self_test_fail_root)
        build_stub_script(bench_self_test_fail_root / "scripts/zigux/check-phase1-bench.py", self_test_exit=1)
        issues, notes, summary = collect_issues(bench_self_test_fail_root)
        assert "mandatory_self_test_failed:phase1-bench-self-test:exit=1" in issues, issues
        assert "skipped_mandatory_live:phase1-bench-self-test:self_test_failed" in notes, notes
        assert "phase1-bench-self-test" not in summary.mandatory_live_run_names, summary
        case_count += 1

        optional_self_test_fail_root = base / "optional_self_test_fail"
        build_sample_repo(optional_self_test_fail_root)
        build_stub_script(
            optional_self_test_fail_root / "scripts/zigux/check-phase1-shared-helper-manifest-gate.py",
            self_test_exit=1,
        )
        issues, notes, summary = collect_issues(optional_self_test_fail_root)
        assert "optional_self_test_failed:phase1-shared-helper-manifest-gate:exit=1" in issues, issues
        assert "skipped_optional:phase1-shared-helper-manifest-gate:self_test_failed" in notes, notes
        assert "phase1-shared-helper-manifest-gate" not in summary.optional_run_names, summary
        assert summary.optional_run_count == len(OPTIONAL_CHECKS) - 1, summary
        assert summary.optional_skip_count == 1, summary
        case_count += 1

        duplicate_optional_name_checks = OPTIONAL_CHECKS + (
            CheckSpec(
                "phase1-parity",
                "scripts/zigux/check-phase1-parity-copy.py",
                ("--self-test",),
                ("--root", "{root}"),
                required=False,
            ),
        )
        duplicate_optional_name_root = base / "duplicate_optional_name"
        build_sample_repo(duplicate_optional_name_root, optional_checks=duplicate_optional_name_checks)
        issues, notes, _summary = collect_issues(
            duplicate_optional_name_root, optional_checks=duplicate_optional_name_checks
        )
        assert issues == ["duplicate_optional_check_name:phase1-parity"], issues
        assert notes == [], notes
        case_count += 1

        overlapping_roster_root = base / "overlapping_roster"
        overlapping_mandatory_checks = MANDATORY_CHECKS + (
            CheckSpec(
                "phase1-replay-blockers",
                "scripts/zigux/check-phase1-replay-blockers-mandatory.py",
                ("--self-test",),
                ("--root", "{root}"),
            ),
        )
        build_sample_repo(overlapping_roster_root, mandatory_checks=overlapping_mandatory_checks)
        issues, _notes, _summary = collect_issues(
            overlapping_roster_root, mandatory_checks=overlapping_mandatory_checks
        )
        assert "overlapping_check_name:phase1-replay-blockers" in issues, issues
        case_count += 1

        output_root = base / "output_root"
        build_sample_repo(output_root)
        check_result = run_command(
            [sys.executable, str(Path(__file__)), "--root", str(output_root)],
            cwd=ROOT,
        )
        assert check_result.returncode == 0, check_result.stderr
        assert "PHASE1_VALIDATION=pass" in check_result.stdout, check_result.stdout
        assert (
            f"PHASE1_VALIDATION_OPTIONAL_CHECK_COUNT={len(OPTIONAL_CHECKS)}" in check_result.stdout
        ), check_result.stdout
        assert "PHASE1_VALIDATION_NOTE_COUNT=0" in check_result.stdout, check_result.stdout
        case_count += 1

    print("PHASE1_VALIDATE_SELF_TEST=pass")
    print(f"PHASE1_VALIDATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return run_check(repo_root(args.root))


if __name__ == "__main__":
    raise SystemExit(main())
