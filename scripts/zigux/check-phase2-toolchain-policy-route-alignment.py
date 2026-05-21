#!/usr/bin/env python3
"""Guard policy-driven required make routes across the shared Phase 2 note packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"

EXPECTED_PHASE = "Phase 2"


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


def require_routes(policy_path: Path) -> list[str]:
    payload = json.loads(read_text(policy_path))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid policy payload in {policy_path}")
    if payload.get("phase") != EXPECTED_PHASE:
        raise ValueError(f"unexpected phase in {policy_path}: {payload.get('phase')!r}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise ValueError(f"invalid required_make_routes in {policy_path}")
    normalized: list[str] = []
    seen: set[str] = set()
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise ValueError(f"invalid required_make_routes entry in {policy_path}")
        cleaned = route.strip()
        if cleaned in seen:
            raise ValueError(f"duplicate required_make_routes entry in {policy_path}: {cleaned}")
        normalized.append(cleaned)
        seen.add(cleaned)
    return normalized


def format_backticked_routes(routes: list[str]) -> str:
    items = [f"`{route}`" for route in routes]
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def format_shell_route(route: str) -> str:
    return f"`make -C zigux {route}`"


def expected_notes_summary(routes: list[str]) -> str:
    return (
        "`scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel "
        "`0.17.0-dev.87+9b177a7d2`, keeps the minimum version in lockstep, limits "
        f"archive digests to `x86_64-linux`, and names {format_backticked_routes(routes)} "
        "as the required Linux-style make routes when those routes are rematerialized."
    )


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    try:
        routes = require_routes(policy_path)
    except ValueError as exc:
        return [("INVALID_POLICY", str(exc))]

    notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    review_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    tests_text = read_text(resolve_path(root, TESTS_README))

    summary_marker = expected_notes_summary(routes)
    if summary_marker not in notes_text:
        issues.append(("MISSING_PHASE2_NOTES_ROUTE_SUMMARY", summary_marker))

    for route in routes:
        route_marker = format_shell_route(route)
        if route_marker not in notes_text:
            issues.append(("MISSING_PHASE2_NOTES_ROUTE_MARKER", route_marker))
        if route_marker not in review_text:
            issues.append(("MISSING_REVIEW_ROUTE_MARKER", route_marker))
        if route_marker not in tests_text:
            issues.append(("MISSING_TESTS_ROUTE_MARKER", route_marker))

    return issues


def emit_issues(issues: list[tuple[str, str]], root: Path) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOLCHAIN_POLICY_ROUTE_ALIGNMENT=fail")
    print(f"PHASE2_TOOLCHAIN_POLICY_PATH={resolve_path(root, TOOLCHAIN_POLICY)}")
    print(f"PHASE2_TOOLCHAIN_POLICY_ROUTE_NOTES_PATH={resolve_path(root, PHASE2_NOTES)}")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def sample_policy_text(routes: list[str]) -> str:
    return (
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": routes,
                },
            },
            indent=2,
        )
        + "\n"
    )


def sample_notes_text(routes: list[str]) -> str:
    route_lines = "\n".join(f"- {format_shell_route(route)}" for route in routes)
    return (
        "# Phase 2 Toolchain Bootstrap Notes\n\n"
        "## Current direct packet\n\n"
        f"- {expected_notes_summary(routes)}\n"
        "- The rematerialized make-wrapper packet is directly readable on current `master` through:\n"
        f"{route_lines}\n"
    )


def sample_review_text(routes: list[str]) -> str:
    route_lines = "\n".join(f"- {format_shell_route(route)}" for route in routes)
    return "# Zigux Review Checklist\n\n## Validation\n\n" + route_lines + "\n"


def sample_tests_text(routes: list[str]) -> str:
    route_lines = ", ".join(format_shell_route(route) for route in routes)
    return (
        "# zigux/tests\n\n## Phase 2 review packet\n\n"
        "Keep the rematerialized make-wrapper packet explicit through "
        f"{route_lines}.\n"
    )


def write_sample_root(root: Path, routes: list[str]) -> None:
    write_text(resolve_path(root, TOOLCHAIN_POLICY), sample_policy_text(routes))
    write_text(resolve_path(root, PHASE2_NOTES), sample_notes_text(routes))
    write_text(resolve_path(root, REVIEW_CHECKLIST), sample_review_text(routes))
    write_text(resolve_path(root, TESTS_README), sample_tests_text(routes))


def run_self_test() -> int:
    checks_run = 0
    routes = ["phase2-toolchain", "phase2-validate", "phase2-cross"]
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_policy_route_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        write_sample_root(root, routes)
        assert collect_issues(root) == []
        checks_run += 1

        write_sample_root(root, routes)
        write_text(
            resolve_path(root, PHASE2_NOTES),
            sample_notes_text(["phase2-toolchain", "phase2-validate"]),
        )
        issues = collect_issues(root)
        assert any(code == "MISSING_PHASE2_NOTES_ROUTE_SUMMARY" for code, _ in issues)
        assert ("MISSING_PHASE2_NOTES_ROUTE_MARKER", "`make -C zigux phase2-cross`") in issues
        checks_run += 1

        write_sample_root(root, routes)
        write_text(
            resolve_path(root, REVIEW_CHECKLIST),
            sample_review_text(["phase2-toolchain", "phase2-validate"]),
        )
        assert ("MISSING_REVIEW_ROUTE_MARKER", "`make -C zigux phase2-cross`") in collect_issues(root)
        checks_run += 1

        write_sample_root(root, routes)
        write_text(
            resolve_path(root, TESTS_README),
            sample_tests_text(["phase2-toolchain", "phase2-validate"]),
        )
        assert ("MISSING_TESTS_ROUTE_MARKER", "`make -C zigux phase2-cross`") in collect_issues(root)
        checks_run += 1

        write_sample_root(root, routes)
        write_text(
            resolve_path(root, TOOLCHAIN_POLICY),
            sample_policy_text(["phase2-toolchain", "phase2-validate", "phase2-cross", "phase2-cross"]),
        )
        issues = collect_issues(root)
        assert len(issues) == 1
        assert issues[0][0] == "INVALID_POLICY"
        assert "duplicate required_make_routes entry" in issues[0][1]
        checks_run += 1

    print("PHASE2_TOOLCHAIN_POLICY_ROUTE_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_POLICY_ROUTE_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate policy-driven required make routes across the shared Phase 2 toolchain reminder packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root to the given directory and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root, ["phase2-toolchain", "phase2-validate", "phase2-cross"])
        print(f"PHASE2_TOOLCHAIN_POLICY_ROUTE_ALIGNMENT_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues, args.root)

    routes = require_routes(resolve_path(args.root, TOOLCHAIN_POLICY))
    print("PHASE2_TOOLCHAIN_POLICY_ROUTE_ALIGNMENT=pass")
    print(f"PHASE2_TOOLCHAIN_POLICY_ROUTE_COUNT={len(routes)}")
    print("PHASE2_TOOLCHAIN_POLICY_REQUIRED_ROUTES=" + ",".join(routes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
