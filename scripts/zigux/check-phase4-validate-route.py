#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else Path.cwd().resolve()
MAKEFILE_REL = "zigux/Makefile"
PHASE4_VALIDATE_TARGET = "phase4-validate"
PHASE4_VALIDATE_COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py",
)


def _is_makefile_target_header(raw: str) -> bool:
    if raw.startswith((" ", "\t")):
        return False
    stripped = raw.strip()
    if not stripped or stripped.startswith("#"):
        return False
    if ":=" in stripped or "?=" in stripped or "+=" in stripped or "!=" in stripped:
        return False
    return ":" in stripped


def _collect_target_commands(makefile: str, target: str) -> list[str] | None:
    in_target = False
    commands: list[str] = []
    header = f"{target}:"
    for raw in makefile.splitlines():
        stripped = raw.strip()
        if not in_target:
            if stripped.startswith(header):
                in_target = True
            continue
        if _is_makefile_target_header(raw):
            break
        if stripped:
            commands.append(stripped)
    return commands if in_target else None


def validate(root: Path) -> list[str]:
    makefile_path = root / MAKEFILE_REL
    if not makefile_path.exists():
        return [f"missing_makefile:{MAKEFILE_REL}"]

    commands = _collect_target_commands(
        makefile_path.read_text(encoding="utf-8"),
        PHASE4_VALIDATE_TARGET,
    )
    if commands is None:
        return [f"missing_makefile_target:{PHASE4_VALIDATE_TARGET}"]

    issues: list[str] = []
    for command in PHASE4_VALIDATE_COMMANDS:
        count = commands.count(command)
        if count == 0:
            issues.append(f"missing_makefile_command:{PHASE4_VALIDATE_TARGET}:{command}")
        elif count != 1:
            issues.append(
                f"unexpected_makefile_command_count:{PHASE4_VALIDATE_TARGET}:{count}:{command}"
            )

    for command in commands:
        if command not in PHASE4_VALIDATE_COMMANDS:
            issues.append(f"unexpected_makefile_command:{PHASE4_VALIDATE_TARGET}:{command}")

    filtered = [command for command in commands if command in PHASE4_VALIDATE_COMMANDS]
    if filtered != list(PHASE4_VALIDATE_COMMANDS):
        issues.append(f"makefile_command_order_drift:{PHASE4_VALIDATE_TARGET}")

    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _baseline_makefile() -> str:
    return "\n".join(
        (
            "phase4-validate:",
            *PHASE4_VALIDATE_COMMANDS,
            "",
            "phase4-test:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase4_build.zig",
            "",
        )
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_validate_route_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        _write(root / MAKEFILE_REL, _baseline_makefile())
        assert validate(root) == []
        case_count += 1

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
            "",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            f"missing_makefile_command:{PHASE4_VALIDATE_TARGET}:{PHASE4_VALIDATE_COMMANDS[6]}",
            f"makefile_command_order_drift:{PHASE4_VALIDATE_TARGET}",
        ]
        _write(root / MAKEFILE_REL, _baseline_makefile())
        case_count += 1

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py --self-test\n",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py --self-test\n"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py --self-test\n",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            f"unexpected_makefile_command_count:{PHASE4_VALIDATE_TARGET}:2:{PHASE4_VALIDATE_COMMANDS[7]}",
            f"makefile_command_order_drift:{PHASE4_VALIDATE_TARGET}",
        ]
        _write(root / MAKEFILE_REL, _baseline_makefile())
        case_count += 1

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py --self-test\n",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py --self-test\n"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            f"makefile_command_order_drift:{PHASE4_VALIDATE_TARGET}",
        ]
        _write(root / MAKEFILE_REL, _baseline_makefile())
        case_count += 1

        makefile = _baseline_makefile().replace(
            "phase4-test:",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/unexpected.py\n\nphase4-test:",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            "unexpected_makefile_command:phase4-validate:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/unexpected.py",
        ]
        case_count += 1

    print("PHASE4_VALIDATE_ROUTE=pass")
    print(f"PHASE4_VALIDATE_ROUTE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 4 Makefile validate route aligned with the shipped repo-tooling packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = Path(args.root).resolve() if args.root else ROOT
    issues = validate(repo_root)
    if issues:
        print("PHASE4_VALIDATE_ROUTE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE4_VALIDATE_ROUTE=pass")
    print(f"PHASE4_VALIDATE_ROUTE_COMMAND_COUNT={len(PHASE4_VALIDATE_COMMANDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
