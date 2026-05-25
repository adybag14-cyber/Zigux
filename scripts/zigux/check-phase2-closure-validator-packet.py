#!/usr/bin/env python3
"""Guard the machine-readable Phase 2 closure validator packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
MAKEFILE = ROOT / "zigux" / "Makefile"

CLOSURE_VALIDATION_HEADER = "## Closure Validation"
CLOSURE_VALIDATORS_PREFIX = "PHASE2_CLOSURE_VALIDATORS="
SHARED_MAKE_ROUTES_PREFIX = "PHASE2_SHARED_MAKE_ROUTES="
EXPECTED_SHARED_ROUTE_COUNT = 8


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def count_target_definitions(text: str, route: str) -> int:
    prefix = f"{route}:"
    return sum(1 for line in text.splitlines() if line.strip().startswith(prefix))


def find_section_lines(text: str, header: str) -> list[str]:
    lines = text.splitlines()
    capture = False
    section: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == header:
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if capture:
            section.append(line)
    if not capture:
        raise SystemExit(f"required section missing: {header}")
    return section


def parse_bullet_command(line: str) -> str | None:
    stripped = line.strip()
    if not stripped.startswith("- `") or not stripped.endswith("`"):
        return None
    return stripped[3:-1]


def parse_sentinel_line(line: str, prefix: str) -> str | None:
    command = parse_bullet_command(line)
    if command is None or not command.startswith(prefix):
        return None
    return command[len(prefix) :]


def extract_closure_validation_commands(section_lines: list[str]) -> list[str]:
    commands: list[str] = []
    for line in section_lines:
        command = parse_bullet_command(line)
        if command is None:
            continue
        if command.startswith(CLOSURE_VALIDATORS_PREFIX) or command.startswith(SHARED_MAKE_ROUTES_PREFIX):
            continue
        commands.append(command)
    return commands


def extract_required_sentinel(section_lines: list[str], prefix: str) -> str:
    matches = [value for line in section_lines if (value := parse_sentinel_line(line, prefix)) is not None]
    if len(matches) != 1:
        raise SystemExit(f"required sentinel count mismatch for {prefix}: {len(matches)}")
    return matches[0]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    section_lines = find_section_lines(closure_text, CLOSURE_VALIDATION_HEADER)

    commands = extract_closure_validation_commands(section_lines)
    expected_validators = ",".join(commands)
    actual_validators = extract_required_sentinel(section_lines, CLOSURE_VALIDATORS_PREFIX)

    issues: list[tuple[str, str]] = []
    if actual_validators != expected_validators:
        issues.append(("PHASE2_CLOSURE_VALIDATORS_MISMATCH", actual_validators))

    shared_routes = [command for command in commands if command.startswith("make -C zigux ")]
    expected_routes = ",".join(shared_routes)
    actual_routes = extract_required_sentinel(section_lines, SHARED_MAKE_ROUTES_PREFIX)
    if actual_routes != expected_routes:
        issues.append(("PHASE2_SHARED_MAKE_ROUTES_MISMATCH", actual_routes))

    if len(shared_routes) != EXPECTED_SHARED_ROUTE_COUNT:
        issues.append(("PHASE2_SHARED_ROUTE_COUNT_MISMATCH", str(len(shared_routes))))

    if len(commands) != len(set(commands)):
        issues.append(("DUPLICATE_CLOSURE_VALIDATOR", "closure validation commands"))
    if len(shared_routes) != len(set(shared_routes)):
        issues.append(("DUPLICATE_SHARED_MAKE_ROUTE", "shared make routes"))

    for route in shared_routes:
        route_name = route.rsplit(" ", 1)[-1]
        count = count_target_definitions(makefile_text, route_name)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_ROUTE", route_name))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_ROUTE", f"{route_name}:count={count}"))

    route_sentinel_line = f"- `{SHARED_MAKE_ROUTES_PREFIX}{expected_routes}`"
    count = count_exact_lines(closure_text, route_sentinel_line)
    if count == 0:
        issues.append(("MISSING_SHARED_ROUTE_SENTINEL_LINE", route_sentinel_line))
    elif count != 1:
        issues.append(("DUPLICATE_SHARED_ROUTE_SENTINEL_LINE", f"{route_sentinel_line}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_VALIDATOR_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    commands = (
        "python3 scripts/zigux/check-zig-toolchain.py --self-test",
        "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
        "python3 scripts/zigux/validate-phase2.py",
        "python3 scripts/zigux/validate-phase2-closure.py --self-test",
        "python3 scripts/zigux/validate-phase2-closure.py",
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    )
    shared_routes = tuple(command for command in commands if command.startswith("make -C zigux "))
    closure_lines = [
        "# Phase 2 Closure",
        "",
        "## Closure Validation",
        "",
        *[f"- `{command}`" for command in commands],
        "",
        f"- `{CLOSURE_VALIDATORS_PREFIX}{','.join(commands)}`",
        f"- `{SHARED_MAKE_ROUTES_PREFIX}{','.join(shared_routes)}`",
        "",
        "## Next Step",
        "",
        "parked",
        "",
    ]
    makefile_lines = [
        ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
        "phase2-toolchain:",
        "\t@true",
        "phase2-tools:",
        "\t@true",
        "phase2-kconfig:",
        "\t@true",
        "phase2-cross:",
        "\t@true",
        "phase2-genksyms:",
        "\t@true",
        "phase2-fixdep:",
        "\t@true",
        "phase2-validate:",
        "\t@true",
        "phase2:",
        "\t@true",
    ]
    write_text(resolve_path(root, PHASE2_CLOSURE), "\n".join(closure_lines))
    write_text(resolve_path(root, MAKEFILE), "\n".join(makefile_lines) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 7
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validator_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        closure_path = resolve_path(root, PHASE2_CLOSURE)
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "python3 scripts/zigux/validate-phase2.py",
                "python3 scripts/zigux/validate-phase2-other.py",
            ),
            encoding="utf-8",
        )
        assert ("PHASE2_CLOSURE_VALIDATORS_MISMATCH", "python3 scripts/zigux/check-zig-toolchain.py --self-test,python3 scripts/zigux/check-zig-toolchain.py --policy-only,python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing,python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py --self-test,python3 scripts/zigux/validate-phase2-closure.py,make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = resolve_path(root, PHASE2_CLOSURE)
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "make -C zigux phase2-fixdep",
                "make -C zigux phase2-other",
            ),
            encoding="utf-8",
        )
        assert ("PHASE2_SHARED_MAKE_ROUTES_MISMATCH", "make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = resolve_path(root, PHASE2_CLOSURE)
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                f"- `{SHARED_MAKE_ROUTES_PREFIX}",
                "- `BROKEN_SHARED_ROUTE_SENTINEL=",
            ),
            encoding="utf-8",
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert f"required sentinel count mismatch for {SHARED_MAKE_ROUTES_PREFIX}" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing shared route sentinel did not abort")

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            replace_once(makefile_path.read_text(encoding="utf-8"), "phase2-cross:\n\t@true\n"),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_ROUTE", "phase2-cross") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8") + "phase2-cross:\n\t@true\n",
            encoding="utf-8",
        )
        assert ("DUPLICATE_MAKEFILE_ROUTE", "phase2-cross:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = resolve_path(root, PHASE2_CLOSURE)
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                "- `make -C zigux phase2`\n",
                "- `make -C zigux phase2`\n- `make -C zigux phase2`\n",
                1,
            ),
            encoding="utf-8",
        )
        assert ("DUPLICATE_CLOSURE_VALIDATOR", "closure validation commands") in collect_issues(root)
        checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_CLOSURE_VALIDATOR_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard the machine-readable Phase 2 closure validator packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    section_lines = find_section_lines(read_text(resolve_path(args.root.resolve(), PHASE2_CLOSURE)), CLOSURE_VALIDATION_HEADER)
    commands = extract_closure_validation_commands(section_lines)
    shared_routes = [command for command in commands if command.startswith("make -C zigux ")]
    print("PHASE2_CLOSURE_VALIDATOR_PACKET=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_COUNT={len(commands)}")
    print(f"PHASE2_SHARED_ROUTE_COUNT={len(shared_routes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
