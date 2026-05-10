#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else Path.cwd().resolve()
MAKEFILE_REL = "zigux/Makefile"
HELPER_REL = "scripts/zigux/check-phase4-gate-evidence.py"
TARGET = "phase4-validate"
COMMANDS = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/artifact_diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-artifact-diff-contract.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py",
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def is_target_header(raw: str) -> bool:
    if raw.startswith((" ", "\t")):
        return False
    stripped = raw.strip()
    if not stripped or stripped.startswith("#"):
        return False
    if ":=" in stripped or "?=" in stripped or "+=" in stripped or "!=" in stripped:
        return False
    return ":" in stripped


def collect_target_commands(makefile: str, target: str) -> list[str] | None:
    header = f"{target}:"
    in_target = False
    commands: list[str] = []
    for raw in makefile.splitlines():
        stripped = raw.strip()
        if not in_target:
            if stripped.startswith(header):
                in_target = True
            continue
        if is_target_header(raw):
            break
        if stripped:
            commands.append(stripped)
    return commands if in_target else None


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    makefile_path = root / MAKEFILE_REL
    helper_path = root / HELPER_REL

    if not makefile_path.exists():
        return [f"missing_file:{MAKEFILE_REL}"]
    if not helper_path.exists():
        return [f"missing_file:{HELPER_REL}"]

    commands = collect_target_commands(read_text(root, MAKEFILE_REL), TARGET)
    if commands is None:
        return [f"missing_target:{TARGET}"]

    for command in COMMANDS:
        count = commands.count(command)
        if count == 0:
            issues.append(f"missing_command:{command}")
        elif count != 1:
            issues.append(f"unexpected_command_count:{count}:{command}")

    for command in commands:
        if command not in COMMANDS:
            issues.append(f"unexpected_command:{command}")

    if [command for command in commands if command in COMMANDS] != list(COMMANDS):
        issues.append("phase4_validate_command_order_drift")

    return issues


def baseline_makefile() -> str:
    lines = ["phase4-validate:"]
    lines.extend(f"\t{command}" for command in COMMANDS)
    lines.append("")
    lines.append("phase4-test:")
    lines.append("\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase4_build.zig")
    lines.append("")
    return "\n".join(lines)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase4-gate-evidence-command-alignment-") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        write_text(root / MAKEFILE_REL, baseline_makefile())
        write_text(root / HELPER_REL, "#!/usr/bin/env python3\n")

        if validate(root) != []:
            print("PHASE4_GATE_EVIDENCE_COMMAND_ALIGNMENT_SELF_TEST=fail")
            return 1
        case_count += 1

        missing = baseline_makefile().replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
            "",
            1,
        )
        write_text(root / MAKEFILE_REL, missing)
        expected = [f"missing_command:{COMMANDS[-1]}", "phase4_validate_command_order_drift"]
        if validate(root) != expected:
            print("PHASE4_GATE_EVIDENCE_COMMAND_ALIGNMENT_SELF_TEST=fail")
            return 1
        write_text(root / MAKEFILE_REL, baseline_makefile())
        case_count += 1

        duplicate = baseline_makefile().replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n"
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
            1,
        )
        write_text(root / MAKEFILE_REL, duplicate)
        expected = [
            f"unexpected_command_count:2:{COMMANDS[-1]}",
            "phase4_validate_command_order_drift",
        ]
        if validate(root) != expected:
            print("PHASE4_GATE_EVIDENCE_COMMAND_ALIGNMENT_SELF_TEST=fail")
            return 1
        write_text(root / MAKEFILE_REL, baseline_makefile())
        case_count += 1

        reordered = baseline_makefile().replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py\n"
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n"
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-artifact-diff-determinism.py\n",
            1,
        )
        write_text(root / MAKEFILE_REL, reordered)
        expected = ["phase4_validate_command_order_drift"]
        if validate(root) != expected:
            print("PHASE4_GATE_EVIDENCE_COMMAND_ALIGNMENT_SELF_TEST=fail")
            return 1
        write_text(root / MAKEFILE_REL, baseline_makefile())
        case_count += 1

        (root / HELPER_REL).unlink()
        expected = [f"missing_file:{HELPER_REL}"]
        if validate(root) != expected:
            print("PHASE4_GATE_EVIDENCE_COMMAND_ALIGNMENT_SELF_TEST=fail")
            return 1
        case_count += 1

    print("PHASE4_GATE_EVIDENCE_COMMAND_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE4_GATE_EVIDENCE_COMMAND_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that zigux/Makefile keeps the Phase 4 gate-evidence command in the shared phase4-validate route."
    )
    parser.add_argument("root", nargs="?", default=ROOT, type=Path, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the isolated self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE4_GATE_EVIDENCE_COMMAND_ALIGNMENT=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE4_GATE_EVIDENCE_COMMAND_ALIGNMENT=pass")
    print(f"PHASE4_GATE_EVIDENCE_COMMAND_ALIGNMENT_COMMAND_COUNT={len(COMMANDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
