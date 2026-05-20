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
    CheckSpec(
        name="phase1-closure",
        script_rel="scripts/zigux/validate-phase1-closure.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
    ),
    CheckSpec(
        name="phase1-string-review-packet",
        script_rel="scripts/zigux/check-phase1-string-review-packet.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
    ),
    CheckSpec(
        name="phase1-direct-owner-markers",
        script_rel="scripts/zigux/check-phase1-direct-owner-markers.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
    ),
    CheckSpec(
        name="phase1-bench-self-test",
        script_rel="scripts/zigux/check-phase1-bench.py",
        self_test_args=("--self-test",),
        live_args=(),
    ),
)

OPTIONAL_CHECKS = (
    CheckSpec(
        name="phase1-replay-blockers",
        script_rel="scripts/zigux/check-phase1-replay-blockers.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
        required=False,
        requires=(str(PHASE1_REPLAY_BLOCKERS_REL),),
    ),
    CheckSpec(
        name="phase1-direct-anchor-manifest-gate",
        script_rel="scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
        required=False,
    ),
    CheckSpec(
        name="phase1-parity",
        script_rel="scripts/zigux/check-phase1-parity.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
        required=False,
        requires=(str(PHASE1_REPLAY_BLOCKERS_REL),),
    ),
    CheckSpec(
        name="artifact-diff-contract",
        script_rel="scripts/zigux/check-artifact-diff-contract.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
        required=False,
        requires=(str(ARTIFACT_DIFF_HELPER_REL),),
    ),
    CheckSpec(
        name="phase1-parity-artifact-packet",
        script_rel=str(PHASE1_PARITY_ARTIFACT_PACKET_REL),
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
        required=False,
        requires=(
            str(ARTIFACT_DIFF_HELPER_REL),
            str(PHASE1_HELPERS_FIXTURE_REL),
            str(PHASE1_HELPER_MANIFEST_REL),
            str(PHASE1_REPLAY_BLOCKERS_REL),
        ),
    ),
    CheckSpec(
        name="phase1-scripts-readme-alignment",
        script_rel="scripts/zigux/check-phase1-scripts-readme-alignment.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
        required=False,
    ),
    CheckSpec(
        name="phase1-shared-fixture-gate",
        script_rel="scripts/zigux/check-phase1-shared-fixture-gate.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
        required=False,
        requires=(str(PHASE1_HELPERS_FIXTURE_REL),),
    ),
    CheckSpec(
        name="phase1-shared-replay-roster",
        script_rel="scripts/zigux/check-phase1-shared-replay-roster.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
        required=False,
        requires=(str(PHASE1_HELPERS_FIXTURE_REL), str(PHASE1_REPLAY_BLOCKERS_REL)),
    ),
    CheckSpec(
        name="phase1-shared-helper-manifest-gate",
        script_rel="scripts/zigux/check-phase1-shared-helper-manifest-gate.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
        required=False,
        requires=(str(PHASE1_HELPER_MANIFEST_REL),),
    ),
    CheckSpec(
        name="phase1-fixture-manifest-alignment",
        script_rel="scripts/zigux/check-phase1-fixture-manifest-alignment.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
        required=False,
        requires=(
            str(PHASE1_HELPERS_FIXTURE_REL),
            str(PHASE1_HELPER_MANIFEST_REL),
            str(PHASE1_REPLAY_BLOCKERS_REL),
        ),
    ),
    CheckSpec(
        name="phase1-c-harness-blockers",
        script_rel="scripts/zigux/check-phase1-c-harness-blockers.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
        required=False,
        requires=(str(PHASE1_REPLAY_BLOCKERS_REL),),
    ),
    CheckSpec(
        name="phase1-readme-replay-blockers",
        script_rel="scripts/zigux/check-phase1-readme-replay-blockers.py",
        self_test_args=("--self-test",),
        live_args=("--root", "{root}"),
        required=False,
        requires=(str(SCRIPTS_README_REL), str(PHASE1_REPLAY_BLOCKERS_REL)),
    ),
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT.resolve()


def command_for(spec: CheckSpec, root: Path, *, self_test: bool) -> list[str]:
    script_path = root / spec.script_rel
    template_args = spec.self_test_args if self_test else spec.live_args
    args = [arg.format(root=str(root)) for arg in template_args]
    return [sys.executable, str(script_path), *args]


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
        if value in seen:
            if value not in duplicates:
                duplicates.append(value)
            continue
        seen.add(value)
    return tuple(duplicates)


def collect_roster_issues(
    mandatory_checks: tuple[CheckSpec, ...],
    optional_checks: tuple[CheckSpec, ...],
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

    mandatory_names = {spec.name for spec in mandatory_checks}
    optional_names = {spec.name for spec in optional_checks}
    for name in sorted(mandatory_names & optional_names):
        issues.append(f"overlapping_check_name:{name}")

    mandatory_scripts = {spec.script_rel for spec in mandatory_checks}
    optional_scripts = {spec.script_rel for spec in optional_checks}
    for script_rel in sorted(mandatory_scripts & optional_scripts):
        issues.append(f"overlapping_check_script:{script_rel}")

    return issues


def should_run_optional(spec: CheckSpec, root: Path) -> tuple[bool, str | None]:
    script_path = root / spec.script_rel
    if not script_path.exists():
        return (False, "missing_script")
    if not script_path.is_file():
        return (False, "script_not_file")
    for relative_path in spec.requires:
        failure = classify_required_path(root / relative_path, relative_path)
        if failure is not None:
            return (False, failure)
    return (True, None)


def collect_issues(
    root: Path,
    *,
    mandatory_checks: tuple[CheckSpec, ...] = MANDATORY_CHECKS,
    optional_checks: tuple[CheckSpec, ...] = OPTIONAL_CHECKS,
) -> tuple[list[str], list[str], ValidationSummary]:
    issues: list[str] = []
    notes: list[str] = []
    mandatory_live_run_count = 0
    mandatory_live_skip_count = 0
    mandatory_live_run_names: list[str] = []
    mandatory_live_skip_notes: list[str] = []
    optional_run_count = 0
    optional_skip_count = 0
    optional_run_names: list[str] = []
    optional_skip_notes: list[str] = []
    mandatory_self_test_failures: set[str] = set()

    issues.extend(collect_roster_issues(mandatory_checks, optional_checks))
    if issues:
        return (
            issues,
            notes,
            ValidationSummary(
                mandatory_live_run_count=mandatory_live_run_count,
                mandatory_live_skip_count=mandatory_live_skip_count,
                mandatory_live_run_names=tuple(mandatory_live_run_names),
                mandatory_live_skip_notes=tuple(mandatory_live_skip_notes),
                optional_run_count=optional_run_count,
                optional_skip_count=optional_skip_count,
                optional_run_names=tuple(optional_run_names),
                optional_skip_notes=tuple(optional_skip_notes),
            ),
        )

    for rel in REQUIRED_PATHS:
        failure = classify_required_path(root / rel, rel)
        if failure is not None:
            issues.append(failure)

    if issues:
        return (
            issues,
            notes,
            ValidationSummary(
                mandatory_live_run_count=mandatory_live_run_count,
                mandatory_live_skip_count=mandatory_live_skip_count,
                mandatory_live_run_names=tuple(mandatory_live_run_names),
                mandatory_live_skip_notes=tuple(mandatory_live_skip_notes),
                optional_run_count=optional_run_count,
                optional_skip_count=optional_skip_count,
                optional_run_names=tuple(optional_run_names),
                optional_skip_notes=tuple(optional_skip_notes),
            ),
        )

    for spec in mandatory_checks:
        self_test_result = run_command(command_for(spec, root, self_test=True), root)
        if self_test_result.returncode != 0:
            mandatory_self_test_failures.add(spec.name)
            issues.append(f"mandatory_self_test_failed:{spec.name}:exit={self_test_result.returncode}")
            append_output(issues, f"mandatory_self_test_failed:{spec.name}", self_test_result)

    for spec in mandatory_checks:
        if spec.name == "phase1-bench-self-test":
            continue
        if spec.name in mandatory_self_test_failures:
            mandatory_live_skip_count += 1
            skip_note = f"skipped_mandatory_live:{spec.name}:self_test_failed"
            notes.append(skip_note)
            mandatory_live_skip_notes.append(skip_note)
            continue
        mandatory_live_run_count += 1
        mandatory_live_run_names.append(spec.name)
        live_result = run_command(command_for(spec, root, self_test=False), root)
        if live_result.returncode != 0:
            issues.append(f"mandatory_live_failed:{spec.name}:exit={live_result.returncode}")
            append_output(issues, f"mandatory_live_failed:{spec.name}", live_result)

    bench_expectations = root / BENCH_EXPECTATIONS_REL
    bench_spec = next(spec for spec in mandatory_checks if spec.name == "phase1-bench-self-test")
    if bench_expectations.is_file():
        if bench_spec.name in mandatory_self_test_failures:
            mandatory_live_skip_count += 1
            skip_note = f"skipped_mandatory_live:{bench_spec.name}:self_test_failed"
            notes.append("skipped_bench_live:self_test_failed")
            notes.append(skip_note)
            mandatory_live_skip_notes.append(skip_note)
        else:
            mandatory_live_run_count += 1
            mandatory_live_run_names.append(bench_spec.name)
            bench_result = run_command([sys.executable, str(root / bench_spec.script_rel)], root)
            if bench_result.returncode != 0:
                issues.append(f"bench_live_failed:exit={bench_result.returncode}")
                append_output(issues, "bench_live_failed", bench_result)
    elif bench_expectations.exists():
        mandatory_live_skip_count += 1
        skip_note = (
            f"skipped_mandatory_live:{bench_spec.name}:required_path_not_file:{BENCH_EXPECTATIONS_REL}"
        )
        notes.append(f"skipped_bench_live:required_path_not_file:{BENCH_EXPECTATIONS_REL}")
        notes.append(skip_note)
        mandatory_live_skip_notes.append(skip_note)
    else:
        mandatory_live_skip_count += 1
        skip_note = f"skipped_mandatory_live:{bench_spec.name}:missing_required_path:{BENCH_EXPECTATIONS_REL}"
        notes.append(f"skipped_bench_live:missing_required_path:{BENCH_EXPECTATIONS_REL}")
        notes.append(skip_note)
        mandatory_live_skip_notes.append(skip_note)

    for spec in optional_checks:
        should_run, reason = should_run_optional(spec, root)
        if not should_run:
            optional_skip_count += 1
            skip_note = f"skipped_optional:{spec.name}:{reason}"
            notes.append(skip_note)
            optional_skip_notes.append(skip_note)
            continue

        optional_run_count += 1
        optional_run_names.append(spec.name)
        self_test_result = run_command(command_for(spec, root, self_test=True), root)
        if self_test_result.returncode != 0:
            issues.append(f"optional_self_test_failed:{spec.name}:exit={self_test_result.returncode}")
            append_output(issues, f"optional_self_test_failed:{spec.name}", self_test_result)
            continue

        live_result = run_command(command_for(spec, root, self_test=False), root)
        if live_result.returncode != 0:
            issues.append(f"optional_live_failed:{spec.name}:exit={live_result.returncode}")
            append_output(issues, f"optional_live_failed:{spec.name}", live_result)

    return (
        issues,
        notes,
        ValidationSummary(
            mandatory_live_run_count=mandatory_live_run_count,
            mandatory_live_skip_count=mandatory_live_skip_count,
            mandatory_live_run_names=tuple(mandatory_live_run_names),
            mandatory_live_skip_notes=tuple(mandatory_live_skip_notes),
            optional_run_count=optional_run_count,
            optional_skip_count=optional_skip_count,
            optional_run_names=tuple(optional_run_names),
            optional_skip_notes=tuple(optional_skip_notes),
        ),
    )


def run_check(root: Path) -> int:
    issues, notes, summary = collect_issues(root)
    if issues:
        print("PHASE1_VALIDATION=fail")
        print("PHASE1_VALIDATION_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_VALIDATION_ISSUES_END")
        if notes:
            print("PHASE1_VALIDATION_NOTES_START")
            for note in notes:
                print(note)
            print("PHASE1_VALIDATION_NOTES_END")
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
        return 1

    print("PHASE1_VALIDATION=pass")
    print(f"PHASE1_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE1_VALIDATION_MANDATORY_CHECK_COUNT={len(MANDATORY_CHECKS)}")
    print(f"PHASE1_VALIDATION_MANDATORY_LIVE_CHECK_RUN_COUNT={summary.mandatory_live_run_count}")
    print(f"PHASE1_VALIDATION_MANDATORY_LIVE_CHECK_SKIP_COUNT={summary.mandatory_live_skip_count}")
    for name in summary.mandatory_live_run_names:
        print(f"PHASE1_VALIDATION_MANDATORY_LIVE_CHECK_RUN={name}")
    for note in summary.mandatory_live_skip_notes:
        print(f"PHASE1_VALIDATION_MANDATORY_LIVE_CHECK_SKIP={note}")
    print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_COUNT={len(OPTIONAL_CHECKS]}")
    print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_RUN_COUNT={summary.optional_run_count}")
    print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_SKIP_COUNT={summary.optional_skip_count}")
    for name in summary.optional_run_names:
        print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_RUN={name}")
    for note in summary.optional_skip_notes:
        print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_SKIP={note}")
    print(f"PHASE1_VALIDATION_NOTE_COUNT={len(notes)}")
    for note in notes:
        print(f"PHASE1_VALIDATION_NOTE=zîote}")
    return 0


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
                "import sys",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--self-test', action='store_true')",
                "parser.add_argument('--root')",
                "args = parser.parse_args()",
                f"SELF_TEST_EXIT = {self_test_exit}",
                f"LIVE_EXIT = {live_exit}",
                "if args.self_test:",
                "    print('SELF_TEST=pass' if SELF_TEST_EXIT == 0 else 'SELF_TEST=fail')",
                "    raise SystemExit(SELF_TEST_EXIT)",
                "print('LIVE=pass' if LIVE_EXIT == 0 else 'LIVE=fail')",
                "raise SystemExit(LIVE_EXIT)",
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

    write_text(root / BENCH_EXPECTATIONS_REL, "{\n  \"status\": \"pass\"\n}\n")
    write_text(root / ARTIFACT_DIFF_HELPER_REL, "print('artifact diff helper placeholder')\n")
    write_text(root / PHASE1_HELPERS_FIXTURE_REL, "{\n  \"status\": \"pass\"\n}\n")
    write_text(root / PHASE1_REPLAY_BLOCKERS_REL, "{\n  \"status\": \"parked\"\n}\n")
    write_text(root / PHASE1_HELPER_MANIFEST_REL, "{\n  \"status\": \"closed\"\n}\n")


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
        assert summary.mandatory_live_run_names == tuple(spec.name for spec in MANDATORY_CHECKS), summary
        assert summary.mandatory_live_skip_notes == (), summary
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        assert summary.optional_run_names == tuple(spec.name for spec in OPTIONAL_CHECKS), summary
        assert summary.optional_skip_notes == (), summary
        case_count += 1

        duplicate_optional_name_root = base / "duplicate_optional_name"
        duplicate_optional_name_checks = OPTIONAL_CHECKS + (
            CheckSpec(
                name="phase1-direct-anchor-manifest-gate",
                script_rel="scripts/zigux/check-phase1-direct-anchor-manifest-gate-copy.py",
                self_test_args=("--self-test",),
                live_args=("--root", "{root}"),
                required=False,
            ),
        )
        build_sample_repo(duplicate_optional_name_root, optional_checks=duplicate_optional_name_checks)
        issues, 