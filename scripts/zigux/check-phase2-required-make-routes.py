#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 required-make-routes packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
EXPECTED_SELF_TEST_CASE_COUNT = 17


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_route_list(payload: object, policy_path: Path) -> list[str]:
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")

    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise ValueError(f"invalid required_make_routes in {policy_path}")

    normalized: list[str] = []
    seen: set[str] = set()
    for entry in routes:
        if not isinstance(entry, str) or not entry.strip():
            raise ValueError(f"invalid required_make_routes entry in {policy_path}")
        route = entry.strip()
        if route in seen:
            raise ValueError(f"duplicate required_make_routes entry in {policy_path}: {route}")
        normalized.append(route)
        seen.add(route)
    return normalized


def load_required_make_routes(policy_path: Path = TOOLCHAIN_POLICY) -> list[str]:
    try:
        payload = json.loads(read_text(policy_path))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc
    return require_route_list(payload, policy_path)


def format_route_marker(route: str) -> str:
    return f"`make -C zigux {route}`"


def workflow_lines() -> tuple[str, str]:
    return (
        "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
        "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    )


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_route_marker_issues(text: str, required_routes: list[str], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for route in required_routes:
        marker = format_route_marker(route)
        if marker not in text:
            issues.append((code, marker))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    required_routes = load_required_make_routes(policy_path)

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    for line in workflow_lines():
        if count_exact_lines(workflow_text, line) != 1:
            issues.append(("MISSING_WORKFLOW_LINES", line))

    bootstrap_notes_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    review_checklist_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))

    for text, marker_code, route_code in (
        (bootstrap_notes_text, "MISSING_BOOTSTRAP_GAP_MARKERS", "MISSING_BOOTSTRAP_ROUTE_MARKERS"),
        (review_checklist_text, "MISSING_REVIEW_GAP_MARKERS", "MISSING_REVIEW_ROUTE_MARKERS"),
        (tests_readme_text, "MISSING_TESTS_GAP_MARKERS", "MISSING_TESTS_ROUTE_MARKERS"),
    ):
        if "`zigux/Makefile`" not in text:
            issues.append((marker_code, "`zigux/Makefile`"))
        issues.extend(collect_route_marker_issues(text, required_routes, route_code))

    if resolve_path(root, MAKEFILE).exists():
        issues.append(("UNEXPECTED_PRESENT_PATHS", MAKEFILE.relative_to(ROOT).as_posix()))

    return issues


def emit_issues(issues: list[tuple[str, str]], root: Path, required_routes: list[str]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_REQUIRED_MAKE_ROUTES=fail")
    print(f"PHASE2_REQUIRED_POLICY_PATH={resolve_path(root, TOOLCHAIN_POLICY)}")
    print(f"PHASE2_REQUIRED_MAKEFILE_PATH={resolve_path(root, MAKEFILE)}")
    print("PHASE2_REQUIRED_ROUTE_LIST=" + ",".join(required_routes))
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> Path:
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    write_text(
        policy_path,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, WORKFLOW),
        "\n".join(workflow_lines()) + "\n",
    )
    route_markers = "\n".join(
        (
            "`zigux/Makefile`",
            *[format_route_marker(route) for route in ["phase2-toolchain", "phase2-validate"]],
        )
    )
    for path in (BOOTSTRAP_NOTES, REVIEW_CHECKLIST, TESTS_README):
        write_text(resolve_path(root, path), route_markers + "\n")
    return policy_path


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_required_make_routes_") as tmp_dir:
        root = Path(tmp_dir)
        policy_path = build_self_test_root(root)

        required_routes = load_required_make_routes(resolve_path(root, TOOLCHAIN_POLICY))
        assert required_routes == ["phase2-toolchain", "phase2-validate"]
        assert collect_issues(root) == []
        checks_run += 1

        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), workflow_lines()[0]),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINES", workflow_lines()[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), workflow_lines()[1]),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINES", workflow_lines()[1]) in collect_issues(root)
        checks_run += 1

        for path, code, marker in (
            (BOOTSTRAP_NOTES, "MISSING_BOOTSTRAP_ROUTE_MARKERS", format_route_marker("phase2-toolchain")),
            (REVIEW_CHECKLIST, "MISSING_REVIEW_ROUTE_MARKERS", format_route_marker("phase2-validate")),
            (TESTS_README, "MISSING_TESTS_GAP_MARKERS", "`zigux/Makefile`"),
        ):
            build_self_test_root(root)
            resolved = resolve_path(root, path)
            resolved.write_text(replace_once(resolved.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert (code, marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        write_text(resolve_path(root, MAKEFILE), "phase2-toolchain:\n\t@true\n")
        assert ("UNEXPECTED_PRESENT_PATHS", "zigux/Makefile") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path.write_text("{not-json}\n", encoding="utf-8")
        try:
            load_required_make_routes(policy_path)
        except ValueError as exc:
            assert "invalid toolchain policy JSON" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid JSON did not fail")

        for payload, expected in (
            ({"upgrade_policy": {"required_make_routes": []}}, "invalid required_make_routes"),
            ({"upgrade_policy": {"required_make_routes": ["phase2-toolchain", "phase2-toolchain"]}}, "duplicate required_make_routes entry"),
            ({"upgrade_policy": "bad"}, "invalid upgrade_policy"),
            ([], "invalid toolchain policy payload"),
        ):
            build_self_test_root(root)
            if isinstance(payload, list):
                policy_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            else:
                base = json.loads(read_text(policy_path))
                base["upgrade_policy"] = payload["upgrade_policy"]
                policy_path.write_text(json.dumps(base, indent=2) + "\n", encoding="utf-8")
            try:
                load_required_make_routes(policy_path)
            except ValueError as exc:
                assert expected in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"{expected} did not fail")

        for path in (TOOLCHAIN_POLICY, WORKFLOW, BOOTSTRAP_NOTES, REVIEW_CHECKLIST, TESTS_README):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_REQUIRED_MAKE_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_REQUIRED_MAKE_ROUTES_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 2 required-make-routes packet stays aligned with repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    try:
        required_routes = load_required_make_routes(policy_path)
    except ValueError as exc:
        print("PHASE2_REQUIRED_MAKE_ROUTES=invalid")
        print(f"PHASE2_REQUIRED_POLICY_PATH={policy_path}")
        print(f"PHASE2_REQUIRED_MAKEFILE_PATH={resolve_path(root, MAKEFILE)}")
        print(f"PHASE2_REQUIRED_MAKE_ROUTES_NOTE={exc}")
        return 1

    issues = collect_issues(root)
    if issues:
        return emit_issues(issues, root, required_routes)

    print("PHASE2_REQUIRED_MAKE_ROUTES=pass")
    print(f"PHASE2_REQUIRED_POLICY_PATH={policy_path}")
    print(f"PHASE2_REQUIRED_MAKEFILE_PATH={resolve_path(root, MAKEFILE)}")
    print("PHASE2_REQUIRED_ROUTE_LIST=" + ",".join(required_routes))
    print(f"PHASE2_REQUIRED_ROUTE_COUNT={len(required_routes)}")
    print("PHASE2_REQUIRED_ROUTE_STATUS=historical-gap-tracked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
