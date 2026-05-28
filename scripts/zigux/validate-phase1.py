#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_BENCH_EXPECTATIONS_REL = Path("zigux/tests/fixtures/phase1_bench_expectations.json")
PHASE1_BENCH_REL = Path("zigux/tests/phase1_bench.zig")

REQUIRED_PATHS = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-closure-packet.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "scripts/zigux/check-phase1-find-bit-review-packet.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers.json",
    "zigux/tests/fixtures/phase1_replay_blockers.json",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_helpers_build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
)


@dataclass(frozen=True)
class CheckSpec:
    name: str
    script_rel: str
    self_test_args: tuple[str, ...]
    live_args: tuple[str, ...]
    required_paths: tuple[str, ...] = ()


MANDATORY_CHECKS = (
    CheckSpec("artifact-diff-self-test", "scripts/zigux/artifact_diff.py", ("--self-test",), ()),
    CheckSpec("phase1-bench-self-test", "scripts/zigux/check-phase1-bench.py", ("--self-test",), ()),
    CheckSpec(
        "phase1-closure-packet",
        "scripts/zigux/check-phase1-closure-packet.py",
        ("--self-test",),
        ("--root", "{root}"),
    ),
    CheckSpec(
        "phase1-closure",
        "scripts/zigux/validate-phase1-closure.py",
        ("--self-test",),
        ("--root", "{root}"),
    ),
    CheckSpec(
        "phase1-direct-owner-markers",
        "scripts/zigux/check-phase1-direct-owner-markers.py",
        ("--self-test",),
        ("--root", "{root}"),
    ),
    CheckSpec(
        "phase1-direct-anchor-manifest-gate",
        "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        ("--self-test",),
        ("--root", "{root}"),
    ),
    CheckSpec(
        "phase1-find-bit-bench-anchors",
        "scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        ("--self-test",),
        ("--root", "{root}"),
    ),
    CheckSpec(
        "phase1-find-bit-review-packet",
        "scripts/zigux/check-phase1-find-bit-review-packet.py",
        ("--self-test",),
        ("--root", "{root}"),
    ),
    CheckSpec(
        "phase1-route-summary-counts",
        "scripts/zigux/check-phase1-route-summary-counts.py",
        ("--self-test",),
        ("--root", "{root}"),
    ),
    CheckSpec(
        "phase1-shared-reminder-packet",
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        ("--self-test",),
        ("--root", "{root}"),
    ),
    CheckSpec(
        "phase1-string-review-packet",
        "scripts/zigux/check-phase1-string-review-packet.py",
        ("--self-test",),
        ("--root", "{root}"),
    ),
    CheckSpec(
        "phase1-parity",
        "scripts/zigux/check-phase1-parity.py",
        ("--self-test",),
        ("--root", "{root}"),
    ),
)

OPTIONAL_CHECKS = (
    CheckSpec(
        "phase1-helper-lane-sequencing",
        "scripts/zigux/check-phase1-helper-lane-sequencing.py",
        ("--self-test",),
        ("--root", "{root}"),
        ("Documentation/zigux/phase1-host-helper-lane-sequencing.md",),
    ),
    CheckSpec(
        "phase1-parity-artifact-packet",
        "scripts/zigux/check-phase1-parity-artifact-packet.py",
        ("--self-test",),
        ("--root", "{root}"),
        (
            "scripts/zigux/artifact_diff.py",
            "zigux/tests/fixtures/phase1_helpers.json",
            "zigux/tests/fixtures/phase1_helper_manifest.json",
            "zigux/tests/fixtures/phase1_replay_blockers.json",
        ),
    ),
    CheckSpec(
        "phase1-artifact-diff-note-packet",
        "scripts/zigux/check-phase1-artifact-diff-note-packet.py",
        ("--self-test",),
        ("--root", "{root}"),
        (
            "Documentation/zigux/artifact-diff.md",
            "scripts/zigux/artifact_diff.py",
            "zigux/tests/fixtures/phase1_helper_manifest.json",
            "zigux/tests/fixtures/phase1_helpers.json",
            "zigux/tests/fixtures/phase1_replay_blockers.json",
        ),
    ),
    CheckSpec(
        "phase1-helper-replay-build-packet",
        "scripts/zigux/check-phase1-helper-replay-build-packet.py",
        ("--self-test",),
        ("--root", "{root}"),
        (
            "zigux/tests/phase1_helpers.zig",
            "zigux/tests/phase1_helpers_build.zig",
            "zigux/tests/fixtures/phase1_helpers.json",
            "zigux/tests/fixtures/phase1_helper_manifest.json",
        ),
    ),
    CheckSpec(
        "phase1-replay-blockers",
        "scripts/zigux/check-phase1-replay-blockers.py",
        ("--self-test",),
        ("--root", "{root}"),
        ("zigux/tests/fixtures/phase1_replay_blockers.json",),
    ),
    CheckSpec(
        "phase1-c-harness-blockers",
        "scripts/zigux/check-phase1-c-harness-blockers.py",
        ("--self-test",),
        ("--root", "{root}"),
        ("zigux/tests/fixtures/phase1_replay_blockers.json",),
    ),
    CheckSpec(
        "phase1-shared-fixture-gate",
        "scripts/zigux/check-phase1-shared-fixture-gate.py",
        ("--self-test",),
        ("--root", "{root}"),
        ("zigux/tests/fixtures/phase1_helpers.json",),
    ),
    CheckSpec(
        "phase1-shared-helper-manifest-gate",
        "scripts/zigux/check-phase1-shared-helper-manifest-gate.py",
        ("--self-test",),
        ("--root", "{root}"),
        ("zigux/tests/fixtures/phase1_helper_manifest.json",),
    ),
    CheckSpec(
        "phase1-shared-replay-roster",
        "scripts/zigux/check-phase1-shared-replay-roster.py",
        ("--self-test",),
        ("--root", "{root}"),
        (
            "zigux/tests/fixtures/phase1_helpers.json",
            "zigux/tests/fixtures/phase1_replay_blockers.json",
        ),
    ),
    CheckSpec(
        "phase1-scripts-repo-reality",
        "scripts/zigux/check-phase1-scripts-repo-reality.py",
        ("--self-test",),
        ("--root", "{root}"),
        ("scripts/zigux/README.md",),
    ),
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def classify_required_path(path: Path, relative_path: str) -> str | None:
    if not path.exists():
        return f"missing_required_path:{relative_path}"
    if not path.is_file():
        return f"required_path_not_file:{relative_path}"
    return None


def command_for(spec: CheckSpec, root: Path, *, self_test: bool) -> list[str]:
    script = root / spec.script_rel
    raw_args = spec.self_test_args if self_test else spec.live_args
    args = [arg.format(root=str(root)) for arg in raw_args]
    return [sys.executable, str(script), *args]


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)


def append_process_output(issues: list[str], prefix: str, result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout.strip():
        issues.append(f"{prefix}:stdout={result.stdout.strip()}")
    if result.stderr.strip():
        issues.append(f"{prefix}:stderr={result.stderr.strip()}")


def should_run_optional(spec: CheckSpec, root: Path) -> tuple[bool, str | None]:
    failure = classify_required_path(root / spec.script_rel, spec.script_rel)
    if failure is not None:
        if failure.startswith("missing_required_path:"):
            return False, "missing_script"
        return False, "script_not_file"
    for relative_path in spec.required_paths:
        failure = classify_required_path(root / relative_path, relative_path)
        if failure is not None:
            return False, failure
    return True, None


def collect_issues(root: Path) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    notes: list[str] = []

    for relative_path in REQUIRED_PATHS:
        failure = classify_required_path(root / relative_path, relative_path)
        if failure is not None:
            issues.append(failure)
    if issues:
        return issues, notes

    for spec in MANDATORY_CHECKS:
        self_test = run_command(command_for(spec, root, self_test=True), root)
        if self_test.returncode != 0:
            issues.append(f"mandatory_self_test_failed:{spec.name}:exit={self_test.returncode}")
            append_process_output(issues, f"mandatory_self_test_failed:{spec.name}", self_test)
            continue
        if not spec.live_args:
            notes.append(f"mandatory_self_test_only:{spec.name}")
            continue
        live = run_command(command_for(spec, root, self_test=False), root)
        if live.returncode != 0:
            issues.append(f"mandatory_live_failed:{spec.name}:exit={live.returncode}")
            append_process_output(issues, f"mandatory_live_failed:{spec.name}", live)

    for spec in OPTIONAL_CHECKS:
        should_run, reason = should_run_optional(spec, root)
        if not should_run:
            notes.append(f"skipped_optional:{spec.name}:{reason}")
            continue
        self_test = run_command(command_for(spec, root, self_test=True), root)
        if self_test.returncode != 0:
            issues.append(f"optional_self_test_failed:{spec.name}:exit={self_test.returncode}")
            append_process_output(issues, f"optional_self_test_failed:{spec.name}", self_test)
            notes.append(f"skipped_optional:{spec.name}:self_test_failed")
            continue
        if not spec.live_args:
            notes.append(f"optional_self_test_only:{spec.name}")
            continue
        live = run_command(command_for(spec, root, self_test=False), root)
        if live.returncode != 0:
            issues.append(f"optional_live_failed:{spec.name}:exit={live.returncode}")
            append_process_output(issues, f"optional_live_failed:{spec.name}", live)

    bench_expectations_failure = classify_required_path(
        root / PHASE1_BENCH_EXPECTATIONS_REL, PHASE1_BENCH_EXPECTATIONS_REL.as_posix()
    )
    bench_source_failure = classify_required_path(root / PHASE1_BENCH_REL, PHASE1_BENCH_REL.as_posix())
    if bench_expectations_failure is None and bench_source_failure is None:
        bench_live = run_command(
            [sys.executable, str(root / "scripts/zigux/check-phase1-bench.py"), "--root", str(root)],
            root,
        )
        if bench_live.returncode != 0:
            issues.append(f"optional_live_failed:phase1-bench-live:exit={bench_live.returncode}")
            append_process_output(issues, "optional_live_failed:phase1-bench-live", bench_live)
    else:
        reason = bench_expectations_failure or bench_source_failure or "unknown"
        notes.append(f"skipped_optional:phase1-bench-live:{reason}")

    return issues, notes


def emit_result(issues: list[str], notes: list[str]) -> int:
    success = not issues
    print(f"PHASE1_VALIDATE={'pass' if success else 'fail'}")
    print(f"PHASE1_VALIDATE_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE1_VALIDATE_MANDATORY_CHECK_COUNT={len(MANDATORY_CHECKS)}")
    print(f"PHASE1_VALIDATE_OPTIONAL_CHECK_COUNT={len(OPTIONAL_CHECKS) + 1}")
    print(f"PHASE1_VALIDATE_ISSUE_COUNT={len(issues)}")
    for issue in issues:
        print(f"PHASE1_VALIDATE_ISSUE={issue}")
    print(f"PHASE1_VALIDATE_NOTE_COUNT={len(notes)}")
    for note in notes:
        print(f"PHASE1_VALIDATE_NOTE={note}")
    return 0 if success else 1


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_stub_script(path: Path, *, self_test_exit: int = 0, live_exit: int = 0) -> None:
    write_text(
        path,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import argparse",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--self-test', action='store_true')",
                "parser.add_argument('--root')",
                "args = parser.parse_args()",
                f"raise SystemExit({self_test_exit} if args.self_test else {live_exit})",
            )
        )
        + "\n",
    )
    os.chmod(path, 0o755)


def build_bench_stub(path: Path) -> None:
    write_text(
        path,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "import argparse",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--self-test', action='store_true')",
                "parser.add_argument('--root')",
                "args = parser.parse_args()",
                "if args.self_test:",
                "    raise SystemExit(0)",
                "print('PHASE1_BENCH_CHECK=pass')",
                "raise SystemExit(0)",
            )
        )
        + "\n",
    )
    os.chmod(path, 0o755)


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_PATHS:
        write_text(root / relative_path, f"sample:{relative_path}\n")

    for spec in MANDATORY_CHECKS:
        if spec.name == "phase1-bench-self-test":
            build_bench_stub(root / spec.script_rel)
        else:
            build_stub_script(root / spec.script_rel)
    for spec in OPTIONAL_CHECKS:
        build_stub_script(root / spec.script_rel)

    write_text(root / PHASE1_BENCH_EXPECTATIONS_REL, '{\n  "status": "pass"\n}\n')
    write_text(root / PHASE1_BENCH_REL, "test {}\n")
    write_text(root / "Documentation/zigux/artifact-diff.md", "sample:Documentation/zigux/artifact-diff.md\n")


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_validate_phase1_") as tmp_dir:
        base = Path(tmp_dir)

        success_root = base / "success"
        build_sample_repo(success_root)
        issues, notes = collect_issues(success_root)
        assert issues == [], issues
        assert "mandatory_self_test_only:artifact-diff-self-test" in notes, notes
        case_count += 1

        missing_required_root = base / "missing_required"
        build_sample_repo(missing_required_root)
        (missing_required_root / "zigux/tests/phase1_helpers_build.zig").unlink()
        issues, _notes = collect_issues(missing_required_root)
        assert "missing_required_path:zigux/tests/phase1_helpers_build.zig" in issues, issues
        case_count += 1

        missing_optional_root = base / "missing_optional"
        build_sample_repo(missing_optional_root)
        (missing_optional_root / "scripts/zigux/check-phase1-helper-lane-sequencing.py").unlink()
        issues, notes = collect_issues(missing_optional_root)
        assert issues == [], issues
        assert "skipped_optional:phase1-helper-lane-sequencing:missing_script" in notes, notes
        case_count += 1

        optional_directory_root = base / "optional_directory"
        build_sample_repo(optional_directory_root)
        optional_dir = optional_directory_root / "scripts/zigux/check-phase1-shared-fixture-gate.py"
        optional_dir.unlink()
        optional_dir.mkdir()
        issues, notes = collect_issues(optional_directory_root)
        assert issues == [], issues
        assert "skipped_optional:phase1-shared-fixture-gate:script_not_file" in notes, notes
        case_count += 1

        mandatory_failure_root = base / "mandatory_failure"
        build_sample_repo(mandatory_failure_root)
        build_stub_script(
            mandatory_failure_root / "scripts/zigux/check-phase1-route-summary-counts.py",
            self_test_exit=1,
        )
        issues, _notes = collect_issues(mandatory_failure_root)
        assert "mandatory_self_test_failed:phase1-route-summary-counts:exit=1" in issues, issues
        case_count += 1

        optional_failure_root = base / "optional_failure"
        build_sample_repo(optional_failure_root)
        build_stub_script(
            optional_failure_root / "scripts/zigux/check-phase1-artifact-diff-note-packet.py",
            self_test_exit=1,
        )
        issues, notes = collect_issues(optional_failure_root)
        assert "optional_self_test_failed:phase1-artifact-diff-note-packet:exit=1" in issues, issues
        assert "skipped_optional:phase1-artifact-diff-note-packet:self_test_failed" in notes, notes
        case_count += 1

        bench_skip_root = base / "bench_skip"
        build_sample_repo(bench_skip_root)
        (bench_skip_root / PHASE1_BENCH_EXPECTATIONS_REL).unlink()
        issues, notes = collect_issues(bench_skip_root)
        assert issues == [], issues
        assert (
            "skipped_optional:phase1-bench-live:missing_required_path:"
            "zigux/tests/fixtures/phase1_bench_expectations.json"
        ) in notes, notes
        case_count += 1

    print("PHASE1_VALIDATE_SELF_TEST=pass")
    print(f"PHASE1_VALIDATE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in validator self-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    issues, notes = collect_issues(repo_root(args.root))
    return emit_result(issues, notes)


if __name__ == "__main__":
    raise SystemExit(main())
