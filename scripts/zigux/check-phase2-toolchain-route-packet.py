#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 toolchain route packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
POLICY = "scripts/zigux/zig-toolchain-policy.json"

WORKFLOW_ROUTE_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
)

PHONY_TARGETS = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
    "phase2",
)

MAKEFILE_ROUTE_HEADING = "phase2-toolchain:"
MAKEFILE_ROUTE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
)

DEPENDENT_ROUTE_LINES = (
    "phase2-kconfig: phase2-toolchain",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
)

EXPECTED_REQUIRED_ROUTES = list(PHONY_TARGETS[:-1])
EXPECTED_SELF_TEST_CASE_COUNT = 10


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def find_exact_line_indices(text: str, markers: tuple[str, ...]) -> list[int]:
    indices: list[int] = []
    lines = text.splitlines()
    for marker in markers:
        matches = [index for index, line in enumerate(lines) if line.strip() == marker]
        if len(matches) != 1:
            return []
        indices.append(matches[0])
    return indices


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            if replacement:
                lines[index] = replacement
            else:
                del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def swap_exact_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index = next(index for index, line in enumerate(lines) if line.strip() == first)
    second_index = next(index for index, line in enumerate(lines) if line.strip() == second)
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def parse_phony_targets(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            _, suffix = stripped.split(":", 1)
            targets.update(token for token in suffix.strip().split() if token)
    return targets


def find_route_block(text: str, heading: str) -> str:
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start, len(lines)):
        candidate = lines[index]
        if candidate and not candidate.startswith("\t") and candidate == candidate.lstrip():
            end = index
            break
    return "\n".join(lines[start:end]) + "\n"


def collect_order_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str, order_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    if not issues:
        indices = find_exact_line_indices(text, markers)
        if indices != sorted(indices):
            issues.append((order_code, " -> ".join(markers)))
    return issues


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    try:
        payload = json.loads(read_text(root, POLICY))
    except json.JSONDecodeError as exc:
        return [("INVALID_POLICY_JSON", exc.msg)]
    if not isinstance(payload, dict):
        return [("INVALID_POLICY", "expected JSON object")]
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return [("INVALID_POLICY", "upgrade_policy")]
    required_routes = upgrade_policy.get("required_make_routes")
    if required_routes != EXPECTED_REQUIRED_ROUTES:
        return [("INVALID_POLICY", f"required_make_routes={required_routes!r}")]
    return []


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)

    issues.extend(
        collect_order_issues(
            workflow_text,
            WORKFLOW_ROUTE_LINES,
            "MISSING_WORKFLOW_ROUTE_LINE",
            "DUPLICATE_WORKFLOW_ROUTE_LINE",
            "OUT_OF_ORDER_WORKFLOW_ROUTE_LINE",
        )
    )

    phony_targets = parse_phony_targets(makefile_text)
    missing_phony = [target for target in PHONY_TARGETS if target not in phony_targets]
    for target in missing_phony:
        issues.append(("MISSING_PHASE2_PHONY_TARGET", target))

    route_block = find_route_block(makefile_text, MAKEFILE_ROUTE_HEADING)
    if not route_block:
        issues.append(("MISSING_MAKEFILE_ROUTE_HEADING", MAKEFILE_ROUTE_HEADING))
    else:
        issues.extend(
            collect_order_issues(
                route_block,
                MAKEFILE_ROUTE_LINES,
                "MISSING_MAKEFILE_ROUTE_LINE",
                "DUPLICATE_MAKEFILE_ROUTE_LINE",
                "OUT_OF_ORDER_MAKEFILE_ROUTE_LINE",
            )
        )

    for marker in DEPENDENT_ROUTE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_DEPENDENT_ROUTE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_DEPENDENT_ROUTE_LINE", f"{marker}:count={count}"))

    issues.extend(collect_policy_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_ROUTE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(root, WORKFLOW, "\n".join(("name: zigux-bootstrap", *WORKFLOW_ROUTE_LINES)) + "\n")
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                ".PHONY: " + " ".join(PHONY_TARGETS),
                "",
                MAKEFILE_ROUTE_HEADING,
                *("\t" + line for line in MAKEFILE_ROUTE_LINES),
                "",
                "phase2-tools:",
                "\t@true",
                "",
                *DEPENDENT_ROUTE_LINES,
                "\t@true",
                "",
            )
        ),
    )
    write_text(
        root,
        POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": EXPECTED_REQUIRED_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_route_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), WORKFLOW_ROUTE_LINES[0]))
        assert ("MISSING_WORKFLOW_ROUTE_LINE", WORKFLOW_ROUTE_LINES[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), WORKFLOW_ROUTE_LINES[-1]))
        assert ("DUPLICATE_WORKFLOW_ROUTE_LINE", f"{WORKFLOW_ROUTE_LINES[-1]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, swap_exact_lines(read_text(root, WORKFLOW), WORKFLOW_ROUTE_LINES[0], WORKFLOW_ROUTE_LINES[1]))
        assert any(code == "OUT_OF_ORDER_WORKFLOW_ROUTE_LINE" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, replace_exact_line(read_text(root, MAKEFILE), "phase2-toolchain:"))
        assert ("MISSING_MAKEFILE_ROUTE_HEADING", MAKEFILE_ROUTE_HEADING) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, replace_exact_line(read_text(root, MAKEFILE), MAKEFILE_ROUTE_LINES[0]))
        assert ("MISSING_MAKEFILE_ROUTE_LINE", MAKEFILE_ROUTE_LINES[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, swap_exact_lines(read_text(root, MAKEFILE), MAKEFILE_ROUTE_LINES[0], MAKEFILE_ROUTE_LINES[1]))
        assert any(code == "OUT_OF_ORDER_MAKEFILE_ROUTE_LINE" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, replace_exact_line(read_text(root, MAKEFILE), DEPENDENT_ROUTE_LINES[0]))
        assert ("MISSING_DEPENDENT_ROUTE_LINE", DEPENDENT_ROUTE_LINES[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, replace_once(read_text(root, MAKEFILE), "phase2-toolchain ", ""))
        assert ("MISSING_PHASE2_PHONY_TARGET", "phase2-toolchain") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        payload = json.loads(read_text(root, POLICY))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        write_text(root, POLICY, json.dumps(payload, indent=2) + "\n")
        assert any(code == "INVALID_POLICY" for code, _ in collect_issues(root))
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_ROUTE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_ROUTE_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the current Phase 2 toolchain route packet stays aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_ROUTE_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_ROUTE_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_ROUTE_LINES)}")
    print(f"PHASE2_TOOLCHAIN_ROUTE_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_ROUTE_LINES)}")
    print(f"PHASE2_TOOLCHAIN_ROUTE_PACKET_DEPENDENT_ROUTE_COUNT={len(DEPENDENT_ROUTE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
