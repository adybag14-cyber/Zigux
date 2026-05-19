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
PHASE1_HELPERS_FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
PHASE1_HELPER_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
PHASE1_REPLAY_BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")

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
    optional_run_count: int
    optional_skip_count: int


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


def should_run_optional(spec: CheckSpec, root: Path) -> tuple[bool, str | None]:
    script_path = root / spec.script_rel
    if not script_path.exists():
        return (False, "missing_script")
    for relative_path in spec.requires:
        if not (root / relative_path).exists():
            return (False, f"missing_required_path:{relative_path}")
    return (True, None)


def collect_issues(root: Path) -> tuple[list[str], list[str], ValidationSummary]:
    issues: list[str] = []
    notes: list[str] = []
    optional_run_count = 0
    optional_skip_count = 0

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_required_path:{rel}")

    if issues:
        return (
            issues,
            notes,
            ValidationSummary(
                optional_run_count=optional_run_count,
                optional_skip_count=optional_skip_count,
            ),
        )

    for spec in MANDATORY_CHECKS:
        self_test_result = run_command(command_for(spec, root, self_test=True), root)
        if self_test_result.returncode != 0:
            issues.append(f"mandatory_self_test_failed:{spec.name}:exit={self_test_result.returncode}")
            append_output(issues, f"mandatory_self_test_failed:{spec.name}", self_test_result)

    for spec in MANDATORY_CHECKS:
        if spec.name == "phase1-bench-self-test":
            continue
        live_result = run_command(command_for(spec, root, self_test=False), root)
        if live_result.returncode != 0:
            issues.append(f"mandatory_live_failed:{spec.name}:exit={live_result.returncode}")
            append_output(issues, f"mandatory_live_failed:{spec.name}", live_result)

    bench_expectations = root / BENCH_EXPECTATIONS_REL
    if bench_expectations.exists():
        bench_spec = next(spec for spec in MANDATORY_CHECKS if spec.name == "phase1-bench-self-test")
        bench_result = run_command([sys.executable, str(root / bench_spec.script_rel)], root)
        if bench_result.returncode != 0:
            issues.append(f"bench_live_failed:exit={bench_result.returncode}")
            append_output(issues, "bench_live_failed", bench_result)
    else:
        notes.append(f"skipped_bench_live:missing_required_path:{BENCH_EXPECTATIONS_REL}")

    for spec in OPTIONAL_CHECKS:
        should_run, reason = should_run_optional(spec, root)
        if not should_run:
            optional_skip_count += 1
            notes.append(f"skipped_optional:{spec.name}:{reason}")
            continue

        optional_run_count += 1
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
            optional_run_count=optional_run_count,
            optional_skip_count=optional_skip_count,
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
        print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_RUN_COUNT={summary.optional_run_count}")
        print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_SKIP_COUNT={summary.optional_skip_count}")
        return 1

    print("PHASE1_VALIDATION=pass")
    print(f"PHASE1_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE1_VALIDATION_MANDATORY_CHECK_COUNT={len(MANDATORY_CHECKS)}")
    print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_COUNT={len(OPTIONAL_CHECKS)}")
    print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_RUN_COUNT={summary.optional_run_count}")
    print(f"PHASE1_VALIDATION_OPTIONAL_CHECK_SKIP_COUNT={summary.optional_skip_count}")
    print(f"PHASE1_VALIDATION_NOTE_COUNT={len(notes)}")
    for note in notes:
        print(f"PHASE1_VALIDATION_NOTE={note}")
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


def build_sample_repo(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        write_text(root / rel, f"sample:{rel}\n")

    for spec in MANDATORY_CHECKS:
        build_stub_script(root / spec.script_rel)

    for spec in OPTIONAL_CHECKS:
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
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        missing_required_root = base / "missing_required"
        build_sample_repo(missing_required_root)
        (missing_required_root / "Documentation/zigux/phase1-closure.md").unlink()
        issues, _, summary = collect_issues(missing_required_root)
        assert "missing_required_path:Documentation/zigux/phase1-closure.md" in issues, issues
        assert summary.optional_run_count == 0, summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        mandatory_self_test_root = base / "mandatory_self_test"
        build_sample_repo(mandatory_self_test_root)
        build_stub_script(
            mandatory_self_test_root / "scripts/zigux/check-phase1-string-review-packet.py",
            self_test_exit=1,
        )
        issues, _, summary = collect_issues(mandatory_self_test_root)
        assert "mandatory_self_test_failed:phase1-string-review-packet:exit=1" in issues, issues
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        mandatory_live_root = base / "mandatory_live"
        build_sample_repo(mandatory_live_root)
        build_stub_script(
            mandatory_live_root / "scripts/zigux/check-phase1-direct-owner-markers.py",
            live_exit=1,
        )
        issues, _, summary = collect_issues(mandatory_live_root)
        assert "mandatory_live_failed:phase1-direct-owner-markers:exit=1" in issues, issues
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        optional_self_test_root = base / "optional_self_test"
        build_sample_repo(optional_self_test_root)
        build_stub_script(
            optional_self_test_root / "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
            self_test_exit=1,
        )
        issues, _, summary = collect_issues(optional_self_test_root)
        assert "optional_self_test_failed:phase1-direct-anchor-manifest-gate:exit=1" in issues, issues
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        optional_live_root = base / "optional_live"
        build_sample_repo(optional_live_root)
        build_stub_script(
            optional_live_root / "scripts/zigux/check-phase1-replay-blockers.py",
            live_exit=1,
        )
        issues, _, summary = collect_issues(optional_live_root)
        assert "optional_live_failed:phase1-replay-blockers:exit=1" in issues, issues
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        optional_scripts_readme_live_root = base / "optional_scripts_readme_live"
        build_sample_repo(optional_scripts_readme_live_root)
        build_stub_script(
            optional_scripts_readme_live_root / "scripts/zigux/check-phase1-scripts-readme-alignment.py",
            live_exit=1,
        )
        issues, _, summary = collect_issues(optional_scripts_readme_live_root)
        assert "optional_live_failed:phase1-scripts-readme-alignment:exit=1" in issues, issues
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        optional_shared_fixture_live_root = base / "optional_shared_fixture_live"
        build_sample_repo(optional_shared_fixture_live_root)
        build_stub_script(
            optional_shared_fixture_live_root / "scripts/zigux/check-phase1-shared-fixture-gate.py",
            live_exit=1,
        )
        issues, _, summary = collect_issues(optional_shared_fixture_live_root)
        assert "optional_live_failed:phase1-shared-fixture-gate:exit=1" in issues, issues
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        optional_shared_replay_live_root = base / "optional_shared_replay_live"
        build_sample_repo(optional_shared_replay_live_root)
        build_stub_script(
            optional_shared_replay_live_root / "scripts/zigux/check-phase1-shared-replay-roster.py",
            live_exit=1,
        )
        issues, _, summary = collect_issues(optional_shared_replay_live_root)
        assert "optional_live_failed:phase1-shared-replay-roster:exit=1" in issues, issues
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        optional_shared_helper_manifest_live_root = base / "optional_shared_helper_manifest_live"
        build_sample_repo(optional_shared_helper_manifest_live_root)
        build_stub_script(
            optional_shared_helper_manifest_live_root / "scripts/zigux/check-phase1-shared-helper-manifest-gate.py",
            live_exit=1,
        )
        issues, _, summary = collect_issues(optional_shared_helper_manifest_live_root)
        assert "optional_live_failed:phase1-shared-helper-manifest-gate:exit=1" in issues, issues
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        optional_fixture_manifest_alignment_live_root = base / "optional_fixture_manifest_alignment_live"
        build_sample_repo(optional_fixture_manifest_alignment_live_root)
        build_stub_script(
            optional_fixture_manifest_alignment_live_root / "scripts/zigux/check-phase1-fixture-manifest-alignment.py",
            live_exit=1,
        )
        issues, _, summary = collect_issues(optional_fixture_manifest_alignment_live_root)
        assert "optional_live_failed:phase1-fixture-manifest-alignment:exit=1" in issues, issues
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        bench_skip_root = base / "bench_skip"
        build_sample_repo(bench_skip_root)
        (bench_skip_root / BENCH_EXPECTATIONS_REL).unlink()
        issues, notes, summary = collect_issues(bench_skip_root)
        assert issues == [], issues
        assert f"skipped_bench_live:missing_required_path:{BENCH_EXPECTATIONS_REL}" in notes, notes
        assert summary.optional_run_count == len(OPTIONAL_CHECKS), summary
        assert summary.optional_skip_count == 0, summary
        case_count += 1

        optional_skip_root = base / "optional_skip"
        build_sample_repo(optional_skip_root)
        (optional_skip_root / "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py").unlink()
        issues, notes, summary = collect_issues(optional_skip_root)
        assert issues == [], issues
        assert "skipped_optional:phase1-direct-anchor-manifest-gate:missing_script" in notes, notes
        assert summary.optional_run_count == len(OPTIONAL_CHECKS) - 1, summary
        assert summary.optional_skip_count == 1, summary
        case_count += 1

        optional_skip_required_path_root = base / "optional_skip_required_path"
        build_sample_repo(optional_skip_required_path_root)
        (optional_skip_required_path_root / PHASE1_REPLAY_BLOCKERS_REL).unlink()
        issues, notes, summary = collect_issues(optional_skip_required_path_root)
        assert issues == [], issues
        assert (
            f"skipped_optional:phase1-replay-blockers:missing_required_path:{PHASE1_REPLAY_BLOCKERS_REL}"
            in notes
        ), notes
        assert (
            f"skipped_optional:phase1-parity:missing_required_path:{PHASE1_REPLAY_BLOCKERS_REL}"
            in notes
        ), notes
        assert (
            f"skipped_optional:phase1-shared-replay-roster:missing_required_path:{PHASE1_REPLAY_BLOCKERS_REL}"
            in notes
        ), notes
        assert (
            f"skipped_optional:phase1-fixture-manifest-alignment:missing_required_path:{PHASE1_REPLAY_BLOCKERS_REL}"
            in notes
        ), notes
        assert summary.optional_run_count == len(OPTIONAL_CHECKS) - 4, summary
        assert summary.optional_skip_count == 4, summary
        case_count += 1

    print("PHASE1_VALIDATE_SELF_TEST=pass")
    print(f"PHASE1_VALIDATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 1 reminder packet and Lane 09 companion gates."
    )
    parser.add_argument("--root", help="Override the repository root for validation.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in validator self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_check(repo_root(args.root))


if __name__ == "__main__":
    raise SystemExit(main())