#!/usr/bin/env python3
"""Guard the Phase 2 cross packet around the shared required-make-routes surface."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_ROUTES_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-required-make-routes.py"
VALIDATE_PHASE2 = ROOT / "scripts" / "zigux" / "validate-phase2.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
CROSS_FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

ROUTE = "make -C zigux phase2-cross"
REQUIRED_POLICY_ROUTE = "phase2-cross"
EXPECTED_ARCHIVE_SCOPE = ["x86_64-linux"]
EXPECTED_TARGETS = ("x86_64-linux", "aarch64-linux")

REQUIRED_ROUTES_CHECKER_MARKERS = (
    "`make -C zigux phase2-cross`",
    "run: make -C zigux phase2-cross",
    "phase2-cross:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

VALIDATE_MARKERS = (
    '"run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-required-make-routes.py",',
    '"run: make -C zigux phase2-cross",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",',
    '"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",',
)

BOOTSTRAP_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`make -C zigux phase2-cross`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: make -C zigux phase2-cross",
)

MAKEFILE_LINES = (
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "phase2-cross:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

EXPECTED_SELF_TEST_CASE_COUNT = 10


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


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


def collect_policy_issues(root: Path) -> tuple[list[tuple[str, str]], list[str]]:
    issues: list[tuple[str, str]] = []
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_SHAPE", type(payload).__name__)], []

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return [("INVALID_POLICY_UPGRADE_POLICY", "upgrade_policy")], []

    archive_scope = upgrade_policy.get("archive_target_scope")
    if archive_scope != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_ARCHIVE_TARGET_SCOPE", json.dumps(archive_scope)))

    required_routes = upgrade_policy.get("required_make_routes")
    if not isinstance(required_routes, list) or not required_routes:
        return issues + [("INVALID_REQUIRED_MAKE_ROUTES", "required_make_routes")], []

    normalized: list[str] = []
    for value in required_routes:
        if not isinstance(value, str) or not value.strip():
            issues.append(("INVALID_REQUIRED_MAKE_ROUTES_ENTRY", repr(value)))
            continue
        normalized.append(value.strip())

    route_count = normalized.count(REQUIRED_POLICY_ROUTE)
    if route_count == 0:
        issues.append(("MISSING_REQUIRED_POLICY_ROUTE", REQUIRED_POLICY_ROUTE))
    elif route_count != 1:
        issues.append(("DUPLICATE_REQUIRED_POLICY_ROUTE", f"{REQUIRED_POLICY_ROUTE}:count={route_count}"))
    return issues, normalized


def collect_fixture_issues(root: Path) -> tuple[list[tuple[str, str]], dict[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = read_json(resolve_path(root, CROSS_FIXTURE))
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", type(payload).__name__)], {}

    if payload.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_ROUTE", str(payload.get("route"))))
    if payload.get("archive_target_scope") != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_FIXTURE_ARCHIVE_SCOPE", json.dumps(payload.get("archive_target_scope"))))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        return issues + [("INVALID_FIXTURE_CROSS_TARGETS", "cross_targets")], {}

    seen: dict[str, str] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_FIXTURE_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        route = entry.get("route")
        mode = entry.get("validation_mode")
        if not isinstance(target, str) or not target.strip():
            issues.append(("INVALID_FIXTURE_ENTRY", "target"))
            continue
        normalized_target = target.strip()
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", normalized_target))
        if not isinstance(mode, str) or not mode.strip():
            issues.append(("INVALID_CROSS_TARGET_MODE", normalized_target))
            continue
        seen[normalized_target] = mode.strip()

    if tuple(seen.keys()) != EXPECTED_TARGETS:
        issues.append(("INVALID_CROSS_TARGET_SET", ",".join(seen.keys())))
    if seen.get("x86_64-linux") != "archive_required":
        issues.append(("INVALID_CROSS_TARGET_MODE", "x86_64-linux"))
    if seen.get("aarch64-linux") != "route_contract_only":
        issues.append(("INVALID_CROSS_TARGET_MODE", "aarch64-linux"))
    return issues, seen


def collect_exact_line_issues(
    text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> tuple[list[tuple[str, str]], list[str], dict[str, str]]:
    issues, required_routes = collect_policy_issues(root)
    fixture_issues, cross_modes = collect_fixture_issues(root)
    issues.extend(fixture_issues)

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    issues.extend(collect_exact_line_issues(workflow_text, WORKFLOW_LINES, "MISSING_WORKFLOW_LINE", "DUPLICATE_WORKFLOW_LINE"))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    issues.extend(collect_exact_line_issues(makefile_text, MAKEFILE_LINES, "MISSING_MAKEFILE_LINE", "DUPLICATE_MAKEFILE_LINE"))

    required_routes_checker_text = read_text(resolve_path(root, REQUIRED_ROUTES_CHECKER))
    issues.extend(
        collect_missing_markers(
            required_routes_checker_text,
            REQUIRED_ROUTES_CHECKER_MARKERS,
            "MISSING_REQUIRED_ROUTES_CHECKER_MARKER",
        )
    )

    validate_text = read_text(resolve_path(root, VALIDATE_PHASE2))
    issues.extend(collect_missing_markers(validate_text, VALIDATE_MARKERS, "MISSING_VALIDATE_MARKER"))

    bootstrap_notes_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    issues.extend(
        collect_missing_markers(
            bootstrap_notes_text,
            BOOTSTRAP_NOTES_MARKERS,
            "MISSING_BOOTSTRAP_NOTES_MARKER",
        )
    )

    return issues, required_routes, cross_modes


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_REQUIRED_ROUTES_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


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
                    "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(resolve_path(root, REQUIRED_ROUTES_CHECKER), "\n".join(REQUIRED_ROUTES_CHECKER_MARKERS) + "\n")
    write_text(resolve_path(root, VALIDATE_PHASE2), "\n".join(VALIDATE_MARKERS) + "\n")
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(BOOTSTRAP_NOTES_MARKERS) + "\n")
    write_text(
        resolve_path(root, CROSS_FIXTURE),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": ROUTE,
                "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                "cross_targets": [
                    {
                        "target": "x86_64-linux",
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": ROUTE,
                    },
                    {
                        "target": "aarch64-linux",
                        "review_status": "route contract only",
                        "validation_mode": "route_contract_only",
                        "route": ROUTE,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_required_routes_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        issues, routes, cross_modes = collect_issues(root)
        assert issues == []
        assert REQUIRED_POLICY_ROUTE in routes
        assert cross_modes["x86_64-linux"] == "archive_required"
        checks_run += 1

        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_REQUIRED_POLICY_ROUTE", REQUIRED_POLICY_ROUTE) in collect_issues(root)[0]
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"].append(REQUIRED_POLICY_ROUTE)
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("DUPLICATE_REQUIRED_POLICY_ROUTE", f"{REQUIRED_POLICY_ROUTE}:count=2") in collect_issues(root)[0]
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, CROSS_FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["route"] = "make -C zigux phase2-tools"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_ROUTE", "make -C zigux phase2-tools") in collect_issues(root)[0]
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_LINES[1], "# removed"),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINE", WORKFLOW_LINES[1]) in collect_issues(root)[0]
        checks_run += 1

        build_self_test_root(root)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_LINES[2]),
            encoding="utf-8",
        )
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[2]}:count=2") in collect_issues(root)[0]
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), MAKEFILE_LINES[1], "# removed"),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_LINE", MAKEFILE_LINES[1]) in collect_issues(root)[0]
        checks_run += 1

        build_self_test_root(root)
        checker_path = resolve_path(root, REQUIRED_ROUTES_CHECKER)
        checker_path.write_text(checker_path.read_text(encoding="utf-8").replace(REQUIRED_ROUTES_CHECKER_MARKERS[0], "", 1), encoding="utf-8")
        assert ("MISSING_REQUIRED_ROUTES_CHECKER_MARKER", REQUIRED_ROUTES_CHECKER_MARKERS[0]) in collect_issues(root)[0]
        checks_run += 1

        build_self_test_root(root)
        validate_path = resolve_path(root, VALIDATE_PHASE2)
        validate_path.write_text(validate_path.read_text(encoding="utf-8").replace(VALIDATE_MARKERS[2], "", 1), encoding="utf-8")
        assert ("MISSING_VALIDATE_MARKER", VALIDATE_MARKERS[2]) in collect_issues(root)[0]
        checks_run += 1

        build_self_test_root(root)
        notes_path = resolve_path(root, BOOTSTRAP_NOTES)
        notes_path.write_text(notes_path.read_text(encoding="utf-8").replace(BOOTSTRAP_NOTES_MARKERS[4], "", 1), encoding="utf-8")
        assert ("MISSING_BOOTSTRAP_NOTES_MARKER", BOOTSTRAP_NOTES_MARKERS[4]) in collect_issues(root)[0]
        checks_run += 1

    print("PHASE2_CROSS_REQUIRED_ROUTES_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_REQUIRED_ROUTES_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    return 0


def run_contract(root: Path) -> int:
    issues, required_routes, cross_modes = collect_issues(root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_REQUIRED_ROUTES_CONTRACT=pass")
    print(f"PHASE2_CROSS_REQUIRED_ROUTES_CONTRACT_REQUIRED_ROUTE_COUNT={len(required_routes)}")
    print(f"PHASE2_CROSS_REQUIRED_ROUTES_CONTRACT_REQUIRED_ROUTES={','.join(required_routes)}")
    print(f"PHASE2_CROSS_REQUIRED_ROUTES_CONTRACT_TARGET_COUNT={len(cross_modes)}")
    print(
        "PHASE2_CROSS_REQUIRED_ROUTES_CONTRACT_TARGETS="
        + ",".join(EXPECTED_TARGETS)
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a passing sample root to the given directory and exit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root)
        return 0
    return run_contract(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
