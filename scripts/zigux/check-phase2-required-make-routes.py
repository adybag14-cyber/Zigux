#!/usr/bin/env python3
"""Guard the rematerialized Phase 2 make-wrapper packet."""

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

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
)

MAKEFILE_MARKERS = (
    ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2",
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "phase2-kconfig:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "phase2: phase2-validate",
)

EXPECTED_SELF_TEST_CASE_COUNT = 8


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


def load_required_make_routes(policy_path: Path) -> list[str]:
    payload = json.loads(read_text(policy_path))
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise ValueError(f"invalid required_make_routes in {policy_path}")
    normalized: list[str] = []
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise ValueError(f"invalid required_make_routes in {policy_path}")
        normalized.append(route.strip())
    return normalized


def format_route_marker(route: str) -> str:
    return f"`make -C zigux {route}`"


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    required_routes = load_required_make_routes(resolve_path(root, TOOLCHAIN_POLICY))

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    for line in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, line)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINES", line))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINES", f"{line}:count={count}"))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    for marker in MAKEFILE_MARKERS:
        if marker not in makefile_text:
            issues.append(("MISSING_MAKEFILE_MARKERS", marker))

    for path, gap_code, route_code in (
        (BOOTSTRAP_NOTES, "MISSING_BOOTSTRAP_GAP_MARKERS", "MISSING_BOOTSTRAP_ROUTE_MARKERS"),
        (REVIEW_CHECKLIST, "MISSING_REVIEW_GAP_MARKERS", "MISSING_REVIEW_ROUTE_MARKERS"),
        (TESTS_README, "MISSING_TESTS_GAP_MARKERS", "MISSING_TESTS_ROUTE_MARKERS"),
    ):
        text = read_text(resolve_path(root, path))
        if "`zigux/Makefile`" not in text:
            issues.append((gap_code, "`zigux/Makefile`"))
        for route in required_routes:
            marker = format_route_marker(route)
            if marker not in text:
                issues.append((route_code, marker))

    return issues


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
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
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_MARKERS) + "\n")
    marker_text = "\n".join(
        (
            "`zigux/Makefile`",
            "`make -C zigux phase2-toolchain`",
            "`make -C zigux phase2-validate`",
        )
    )
    for path in (BOOTSTRAP_NOTES, REVIEW_CHECKLIST, TESTS_README):
        write_text(resolve_path(root, path), marker_text + "\n")


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_required_make_routes_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            replace_once(makefile_path.read_text(encoding="utf-8"), MAKEFILE_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_MARKERS", MAKEFILE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        for path, code, marker in (
            (BOOTSTRAP_NOTES, "MISSING_BOOTSTRAP_ROUTE_MARKERS", "`make -C zigux phase2-toolchain`"),
            (REVIEW_CHECKLIST, "MISSING_REVIEW_ROUTE_MARKERS", "`make -C zigux phase2-validate`"),
            (TESTS_README, "MISSING_TESTS_GAP_MARKERS", "`zigux/Makefile`"),
        ):
            build_self_test_root(root)
            resolved = resolve_path(root, path)
            resolved.write_text(
                replace_once(resolved.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert (code, marker) in collect_issues(root)
            checks_run += 1

        for path in (TOOLCHAIN_POLICY, WORKFLOW, MAKEFILE):
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
        description="Check that the rematerialized Phase 2 make-wrapper packet stays aligned."
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
    except (ValueError, json.JSONDecodeError) as exc:
        print("PHASE2_REQUIRED_MAKE_ROUTES=invalid")
        print(f"PHASE2_REQUIRED_POLICY_PATH={policy_path}")
        print(f"PHASE2_REQUIRED_MAKEFILE_PATH={resolve_path(root, MAKEFILE)}")
        print(f"PHASE2_REQUIRED_MAKE_ROUTES_NOTE={exc}")
        return 1

    issues = collect_issues(root)
    if issues:
        print("PHASE2_REQUIRED_MAKE_ROUTES=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_REQUIRED_MAKE_ROUTES=pass")
    print(f"PHASE2_REQUIRED_POLICY_PATH={policy_path}")
    print(f"PHASE2_REQUIRED_MAKEFILE_PATH={resolve_path(root, MAKEFILE)}")
    print("PHASE2_REQUIRED_ROUTE_LIST=" + ",".join(required_routes))
    print("PHASE2_REQUIRED_ROUTE_STATUS=present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
