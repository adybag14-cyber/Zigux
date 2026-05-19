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
    "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "scripts/zigux/check-phase11-build-inventory.py",
    "scripts/zigux/check-phase11-matrix-gap-survey.py",
    "scripts/zigux/check-phase11-validation-matrix-gap-survey.py",
    "scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py",
    "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase11_build_inventory.json",
)


@dataclass(frozen=True)
class CheckSpec:
    name: str
    script_rel: str


CHECKS = (
    CheckSpec("phase11-build-inventory", "scripts/zigux/check-phase11-build-inventory.py"),
    CheckSpec("phase11-matrix-gap-survey", "scripts/zigux/check-phase11-matrix-gap-survey.py"),
    CheckSpec(
        "phase11-validation-matrix-gap-survey",
        "scripts/zigux/check-phase11-validation-matrix-gap-survey.py",
    ),
    CheckSpec(
        "phase11-hvc-cleanup-current-head",
        "scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    ),
    CheckSpec(
        "phase11-dw-wdt-teardown-packet",
        "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py",
    ),
    CheckSpec(
        "phase11-dw-wdt-verify-alignment",
        "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py",
    ),
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT.resolve()


def command_for(spec: CheckSpec, root: Path) -> list[str]:
    return [sys.executable, str(root / spec.script_rel)]


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
        print("PHASE11_VALIDATION=fail")
        print("PHASE11_VALIDATION_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE11_VALIDATION_ISSUES_END")
        return 1

    print("PHASE11_VALIDATION=pass")
    print(f"PHASE11_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE11_VALIDATION_CHECK_COUNT={len(CHECKS)}")
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_validate_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_repo(root)

        baseline_issues = collect_issues(root)
        if baseline_issues:
            raise SystemExit(
                "phase11-validate-self-test:baseline_failed:"
                + ",".join(baseline_issues)
            )

        missing = root / "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md"
        missing.unlink()
        issues = collect_issues(root)
        expected_missing = "missing_required_path:Documentation/zigux/phase11-gpio-wdt-validation-matrix.md"
        if expected_missing not in issues:
            raise SystemExit(
                "phase11-validate-self-test:missing_required_path_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        failing_script = root / "scripts/zigux/check-phase11-validation-matrix-gap-survey.py"
        build_stub_script(failing_script, exit_code=1)
        issues = collect_issues(root)
        expected_failure = "live_failed:phase11-validation-matrix-gap-survey:exit=1"
        if expected_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:subcommand_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

        build_sample_repo(root)
        failing_dw_script = root / "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py"
        build_stub_script(failing_dw_script, exit_code=1)
        issues = collect_issues(root)
        expected_dw_failure = "live_failed:phase11-dw-wdt-verify-alignment:exit=1"
        if expected_dw_failure not in issues:
            raise SystemExit(
                "phase11-validate-self-test:dw_subcommand_failure_not_detected:"
                + ",".join(issues or ["none"])
            )

    print("PHASE11_VALIDATE_SELF_TEST=pass")
    print("PHASE11_VALIDATE_SELF_TEST_CASE_COUNT=4")
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
