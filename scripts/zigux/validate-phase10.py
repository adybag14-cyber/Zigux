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

REQUIRED_PATHS = (
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase10-bootstrap-route.py",
    "scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "scripts/zigux/check-phase10-ring-packet.py",
    "scripts/zigux/check-phase10-input-packet.py",
    "scripts/zigux/check-phase10-mmio-packet.py",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
)


@dataclass(frozen=True)
class CheckSpec:
    name: str
    script_rel: str
    live_args: tuple[str, ...] = ()


CHECKS = (
    CheckSpec("phase10-bootstrap-route", "scripts/zigux/check-phase10-bootstrap-route.py"),
    CheckSpec("phase10-shared-freeze-boundary", "scripts/zigux/check-phase10-shared-freeze-boundary.py"),
    CheckSpec("phase10-ring-packet", "scripts/zigux/check-phase10-ring-packet.py"),
    CheckSpec("phase10-input-packet", "scripts/zigux/check-phase10-input-packet.py"),
    CheckSpec("phase10-mmio-packet", "scripts/zigux/check-phase10-mmio-packet.py"),
    CheckSpec("phase10-harness-coverage", "scripts/zigux/check-phase10-harness-coverage.py"),
    CheckSpec(
        "phase10-tests-readme-core-surfaces",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    ),
    CheckSpec("phase10-closure", "scripts/zigux/validate-phase10-closure.py"),
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT.resolve()


def command_for(spec: CheckSpec, root: Path) -> list[str]:
    args = [arg.format(root=str(root)) for arg in spec.live_args]
    return [sys.executable, str(root / spec.script_rel), *args]


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


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_required_path:{rel}")

    if issues:
        return issues

    for spec in CHECKS:
        completed = run_command(command_for(spec, root), root)
        if completed.returncode != 0:
            issues.append(f"live_failed:{spec.name}:exit={completed.returncode}")
            append_output(issues, f"live_failed:{spec.name}", completed)

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE10_VALIDATION=fail")
        print("PHASE10_VALIDATION_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE10_VALIDATION_ISSUES_END")
        return 1

    print("PHASE10_VALIDATION=pass")
    print(f"PHASE10_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE10_VALIDATION_CHECK_COUNT={len(CHECKS)}")
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_stub_script(path: Path, *, exit_code: int = 0) -> None:
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
                "parser.parse_args()",
                f"raise SystemExit({exit_code})",
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


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_validate_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_repo(root)

        baseline_issues = collect_issues(root)
        if baseline_issues:
            raise SystemExit(
                "phase10-validate-self-test:baseline_failed:"
                + ",".join(baseline_issues)
            )

        missing = root / REQUIRED_PATHS[0]
        missing.unlink()
        issues = collect_issues(root)
        expected_missing = f"missing_required_path:{REQUIRED_PATHS[0]}"
        if expected_missing not in issues:
            raise SystemExit(
                "phase10-validate-self-test:missing_required_path_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        failing_script = root / "scripts/zigux/check-phase10-harness-coverage.py"
        build_stub_script(failing_script, exit_code=1)
        issues = collect_issues(root)
        expected_failure = "live_failed:phase10-harness-coverage:exit=1"
        if expected_failure not in issues:
            raise SystemExit(
                "phase10-validate-self-test:subcommand_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

    print("PHASE10_VALIDATE_SELF_TEST=pass")
    print("PHASE10_VALIDATE_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_check(repo_root(args.root))


if __name__ == "__main__":
    sys.exit(main())
