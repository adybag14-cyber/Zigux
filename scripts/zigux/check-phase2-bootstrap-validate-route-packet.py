#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents) >= 4 else Path.cwd()
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
POLICY = Path("scripts/zigux/zig-toolchain-policy.json")

REQUIRED_ROUTE = "phase2-validate"
REQUIRED_PATHS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/zig-toolchain-policy.json",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
)

WORKFLOW_LINES = (
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

EXPECTED_ROUTE_DEPENDENCIES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def load_required_routes(path: Path) -> list[str]:
    payload = json.loads(read_text(path))
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {path}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise ValueError(f"invalid required_make_routes in {path}")

    normalized: list[str] = []
    seen: set[str] = set()
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise ValueError(f"invalid required_make_routes in {path}")
        route = route.strip()
        if route in seen:
            raise ValueError(f"duplicate required_make_routes entry in {path}: {route}")
        normalized.append(route)
        seen.add(route)
    return normalized


def workflow_line_order(text: str, markers: tuple[str, ...]) -> list[int]:
    positions: list[int] = []
    lines = [line.strip() for line in text.splitlines()]
    for marker in markers:
        positions.append(lines.index(marker))
    return positions


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    workflow_text = read_text(root / WORKFLOW)
    makefile_text = read_text(root / MAKEFILE)

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    if not any(code == "MISSING_WORKFLOW_LINE" for code, _ in issues):
        positions = workflow_line_order(workflow_text, WORKFLOW_LINES)
        if positions != sorted(positions):
            issues.append(("MISORDERED_WORKFLOW_PACKET", "phase2-validate handoff"))
        if positions[2] != positions[1] + 1:
            issues.append(("NONCONTIGUOUS_WORKFLOW_HANDOFF", "phase2-validate -> validate-phase2.py"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    try:
        required_routes = load_required_routes(root / POLICY)
    except (ValueError, json.JSONDecodeError) as exc:
        issues.append(("INVALID_POLICY", str(exc)))
        return issues

    if REQUIRED_ROUTE not in required_routes:
        issues.append(("MISSING_POLICY_ROUTE", REQUIRED_ROUTE))

    for dependency in EXPECTED_ROUTE_DEPENDENCIES:
        if dependency not in MAKEFILE_LINES[0]:
            issues.append(("MISSING_ROUTE_DEPENDENCY", dependency))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(root / WORKFLOW, "name: zigux-bootstrap\n" + "\n".join(WORKFLOW_LINES) + "\n")
    write_text(
        root / MAKEFILE,
        "\n".join(
            (
                "PYTHON ?= python3",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "",
                *MAKEFILE_LINES,
            )
        )
        + "\n",
    )
    write_text(
        root / POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    for rel in REQUIRED_PATHS:
        if rel in {str(WORKFLOW), str(MAKEFILE), str(POLICY)}:
            continue
        write_text(root / rel, "present\n")


def run_self_test() -> int:
    expected_case_count = 17
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validate_route_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            workflow_path = root / WORKFLOW
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert (("MISSING_WORKFLOW_LINE", marker)) in collect_issues(root)
            checks += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            workflow_path = root / WORKFLOW
            workflow_path.write_text(
                duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert (("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2")) in collect_issues(root)
            checks += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW
        workflow_path.write_text(
            "name: zigux-bootstrap\n"
            "run: python3 scripts/zigux/validate-phase2.py\n"
            "run: make -C zigux phase2-genksyms\n"
            "run: make -C zigux phase2-validate\n",
            encoding="utf-8",
        )
        assert (("MISORDERED_WORKFLOW_PACKET", "phase2-validate handoff")) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW
        workflow_path.write_text(
            "name: zigux-bootstrap\n"
            "run: make -C zigux phase2-genksyms\n"
            "run: make -C zigux phase2-validate\n"
            "run: python3 scripts/zigux/other.py\n"
            "run: python3 scripts/zigux/validate-phase2.py\n",
            encoding="utf-8",
        )
        assert (("NONCONTIGUOUS_WORKFLOW_HANDOFF", "phase2-validate -> validate-phase2.py")) in collect_issues(root)
        checks += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            makefile_path = root / MAKEFILE
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert (("MISSING_MAKEFILE_LINE", marker)) in collect_issues(root)
            checks += 1

        build_sample_root(root)
        policy_path = root / POLICY
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-cross"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (("MISSING_POLICY_ROUTE", REQUIRED_ROUTE)) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy_path = root / POLICY
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"] = "broken"
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "INVALID_POLICY" for code, _ in issues)
        checks += 1

        build_sample_root(root)
        required_path = root / "scripts/zigux/check-phase2-tool-manifest.py"
        required_path.unlink()
        assert (("MISSING_REQUIRED_PATH", "scripts/zigux/check-phase2-tool-manifest.py")) in collect_issues(root)
        checks += 1

    assert checks == expected_case_count
    print("PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the bootstrap workflow still hands off through the current phase2-validate route."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for focused validation",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_BOOTSTRAP_VALIDATE_ROUTE_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
