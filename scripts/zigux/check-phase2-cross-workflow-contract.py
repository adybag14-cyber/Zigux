#!/usr/bin/env python3
"""Guard the Phase 2 cross packet's bootstrap-workflow contract."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

ROUTE = "make -C zigux phase2-cross"
REQUIRED_MAKE_ROUTE = "phase2-cross"

WORKFLOW_MARKERS = (
    '- name: Self-test current Phase 2 cross checker',
    'run: python3 scripts/zigux/check-phase2-cross.py --self-test',
    '- name: Check current Phase 2 direct cross-route packet',
    'run: python3 scripts/zigux/check-phase2-cross.py',
    '- name: Self-test current Phase 2 cross selftest alignment checker',
    'run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test',
    '- name: Check current Phase 2 cross alignment packet',
    'run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py',
    '- name: Run current Phase 2 cross make route',
    'run: make -C zigux phase2-cross',
    'if len(targets) != 1:',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
)

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

EXPECTED_FIXTURE_PHASE = "Phase 2"
EXPECTED_FIXTURE_STATUS = "active"
ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")
EXPECTED_SELF_TEST_CASE_COUNT = 29


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except IsADirectoryError as exc:
        raise SystemExit(f"required path is not a file: {path}") from exc


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


def load_policy(root: Path) -> dict[str, object]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    return payload


def load_archive_target_scope(root: Path) -> list[str]:
    payload = load_policy(root)
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(
            f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )
    normalized: list[str] = []
    seen: set[str] = set()
    for value in archive_target_scope:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        target = value.strip()
        if target in seen:
            raise SystemExit(
                f"duplicate archive_target_scope entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        normalized.append(target)
        seen.add(target)
    return normalized


def load_required_make_routes(root: Path) -> list[str]:
    payload = load_policy(root)
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    required_make_routes = upgrade_policy.get("required_make_routes")
    if not isinstance(required_make_routes, list) or not required_make_routes:
        raise SystemExit(
            f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )
    normalized: list[str] = []
    seen: set[str] = set()
    for value in required_make_routes:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        route = value.strip()
        if route in seen:
            raise SystemExit(
                f"duplicate required_make_routes entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        normalized.append(route)
        seen.add(route)
    return normalized


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    fixture = read_json(resolve_path(root, FIXTURE))
    archive_target_scope = load_archive_target_scope(root)
    required_make_routes = load_required_make_routes(root)

    for marker in WORKFLOW_MARKERS:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    if REQUIRED_MAKE_ROUTE not in required_make_routes:
        issues.append(("MISSING_REQUIRED_MAKE_ROUTE", REQUIRED_MAKE_ROUTE))

    if not isinstance(fixture, dict):
        issues.append(("INVALID_FIXTURE_SHAPE", "root"))
        return issues

    if fixture.get("phase") != EXPECTED_FIXTURE_PHASE:
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if fixture.get("status") != EXPECTED_FIXTURE_STATUS:
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if fixture.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))

    fixture_scope = fixture.get("archive_target_scope")
    if fixture_scope != archive_target_scope:
        issues.append(("ARCHIVE_SCOPE_MISMATCH", ",".join(archive_target_scope)))

    cross_targets = fixture.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    seen_targets: set[str] = set()
    archive_required_targets: set[str] = set()
    for index, entry in enumerate(cross_targets):
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}"))
            continue

        target = entry.get("target")
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")

        if not isinstance(target, str) or not target.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}:target"))
            continue
        target = target.strip()

        if target in seen_targets:
            issues.append(("DUPLICATE_CROSS_TARGET", target))
        seen_targets.add(target)

        if not isinstance(review_status, str) or not review_status.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
        if validation_mode not in ALLOWED_VALIDATION_MODES:
            issues.append(("INVALID_CROSS_TARGET_MODE", target))
            continue
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if validation_mode == "archive_required":
            archive_required_targets.add(target)

    if archive_required_targets != set(archive_target_scope):
        issues.append(("ARCHIVE_REQUIRED_TARGET_SET_MISMATCH", ",".join(sorted(archive_required_targets))))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_WORKFLOW_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_current_like_root(root: Path) -> None:
    write_text(
        resolve_path(root, WORKFLOW),
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                *[f"      {marker}" for marker in WORKFLOW_MARKERS],
            )
        )
        + "\n",
    )
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
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
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, FIXTURE),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": ROUTE,
                "archive_target_scope": ["x86_64-linux"],
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


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_workflow_") as tmp_dir:
        root = Path(tmp_dir)

        build_current_like_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_MARKERS:
            build_current_like_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        build_current_like_root(root)
        path = resolve_path(root, WORKFLOW)
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), WORKFLOW_MARKERS[0]), encoding="utf-8")
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_MARKERS[0]}:count=2") in collect_issues(root)
        checks_run += 1

        for marker in MAKEFILE_LINES:
            build_current_like_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        build_current_like_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), MAKEFILE_LINES[0]), encoding="utf-8")
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[0]}:count=2") in collect_issues(root)
        checks_run += 1

        build_current_like_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_REQUIRED_MAKE_ROUTE", REQUIRED_MAKE_ROUTE) in collect_issues(root)
        checks_run += 1

        build_current_like_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = [
            "phase2-toolchain",
            "phase2-cross",
            "phase2-cross",
        ]
        path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate required_make_routes entry" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("duplicate required make route did not abort")

        build_current_like_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("ARCHIVE_SCOPE_MISMATCH", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_current_like_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][0]["validation_mode"] = "route_contract_only"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("ARCHIVE_REQUIRED_TARGET_SET_MISMATCH", "") in collect_issues(root)
        checks_run += 1

        build_current_like_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["route"] = "make -C zigux phase2-toolchain"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ROUTE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_current_like_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["validation_mode"] = "unexpected_mode"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_MODE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_current_like_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "x86_64-linux"]
        path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate archive_target_scope entry" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("duplicate archive target scope did not abort")

        for primary_path in (WORKFLOW, MAKEFILE, TOOLCHAIN_POLICY, FIXTURE):
            build_current_like_root(root)
            resolve_path(root, primary_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing primary file did not abort: {primary_path}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_WORKFLOW_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_WORKFLOW_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def write_sample_root(root: Path) -> int:
    build_current_like_root(root.resolve())
    print(f"PHASE2_CROSS_WORKFLOW_CONTRACT_SAMPLE_ROOT={root.resolve()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 cross bootstrap workflow stays aligned with the live cross packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like root for focused validation")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    fixture = read_json(resolve_path(args.root.resolve(), FIXTURE))
    assert isinstance(fixture, dict)
    cross_targets = fixture.get("cross_targets")
    assert isinstance(cross_targets, list)
    print("PHASE2_CROSS_WORKFLOW_CONTRACT=pass")
    print(f"PHASE2_CROSS_WORKFLOW_CONTRACT_WORKFLOW_LINE_COUNT={len(WORKFLOW_MARKERS)}")
    print(f"PHASE2_CROSS_WORKFLOW_CONTRACT_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_CROSS_WORKFLOW_CONTRACT_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}")
    print(f"PHASE2_CROSS_WORKFLOW_CONTRACT_TARGET_COUNT={len(cross_targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
