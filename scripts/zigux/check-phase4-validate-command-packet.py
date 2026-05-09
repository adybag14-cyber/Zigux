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
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _is_makefile_target_header(raw: str) -> bool:
    if raw.startswith((" ", "\t")):
        return False
    stripped = raw.strip()
    if not stripped or stripped.startswith("#"):
        return False
    if ":=" in stripped or "?=" in stripped or "+=" in stripped or "!=" in stripped:
        return False
    return ":" in stripped


def _collect_makefile_target_lines(makefile: str, target: str) -> list[str] | None:
    in_target = False
    lines: list[str] = []
    target_header = f"{target}:"
    for raw in makefile.splitlines():
        stripped = raw.strip()
        if not in_target:
            if stripped.startswith(target_header):
                in_target = True
            continue
        if _is_makefile_target_header(raw):
            break
        lines.append(raw)
    return lines if in_target else None


def validate(root: Path) -> list[str]:
    makefile_path = root / MAKEFILE_REL
    if not makefile_path.exists():
        return [f"missing_makefile:{MAKEFILE_REL}"]

    makefile = _read(makefile_path)
    lines = _collect_makefile_target_lines(makefile, PHASE4_VALIDATE_TARGET)
    if lines is None:
        return [f"missing_makefile_target:{PHASE4_VALIDATE_TARGET}"]

    issues: list[str] = []
    commands = [raw.strip() for raw in lines if raw.strip()]
    expected = list(PHASE4_VALIDATE_COMMANDS)

    for command in expected:
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

    if [command for command in commands if command in PHASE4_VALIDATE_COMMANDS] != expected:
        issues.append(f"makefile_command_order_drift:{PHASE4_VALIDATE_TARGET}")

    return issues


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
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_validate_command_packet_") as tmp_dir:
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
            f"missing_makefile_command:{PHASE4_VALIDATE_TARGET}:{PHASE4_VALIDATE_COMMANDS[-1]}",
            f"makefile_command_order_drift:{PHASE4_VALIDATE_TARGET}",
        ]
        case_count += 1

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            f"unexpected_makefile_command_count:{PHASE4_VALIDATE_TARGET}:2:{PHASE4_VALIDATE_COMMANDS[-1]}",
            f"makefile_command_order_drift:{PHASE4_VALIDATE_TARGET}",
        ]
        case_count += 1

        makefile = _baseline_makefile().replace(
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py\n",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n"
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py\n",
            1,
        )
        _write(root / MAKEFILE_REL, makefile)
        assert validate(root) == [
            f"unexpected_makefile_command_count:{PHASE4_VALIDATE_TARGET}:2:{PHASE4_VALIDATE_COMMANDS[-1]}",
            f"makefile_command_order_drift:{PHASE4_VALIDATE_TARGET}",
        ]
        case_count += 1

        _write(root / MAKEFILE_REL, "phase4-test:\n\ttrue\n")
        assert validate(root) == [f"missing_makefile_target:{PHASE4_VALIDATE_TARGET}"]
        case_count += 1

    print("PHASE4_VALIDATE_COMMAND_PACKET_SELF_TEST=pass")
    print(f"PHASE4_VALIDATE_COMMAND_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shipped phase4-validate Makefile command packet exact-counted."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = Path(args.root).resolve() if args.root else ROOT
    issues = validate(repo_root)
    if issues:
        print("PHASE4_VALIDATE_COMMAND_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE4_VALIDATE_COMMAND_PACKET=pass")
    print(f"PHASE4_VALIDATE_COMMAND_PACKET_COMMAND_COUNT={len(PHASE4_VALIDATE_COMMANDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
