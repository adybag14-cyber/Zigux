#!/usr/bin/env python3
"""Guard the workflow trigger globs for the Phase 2 cross packet."""

from __future__ import annotations

import argparse
import fnmatch
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

PACKET_PATHS = (
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/zig-toolchain-policy.json",
    "third_party/README.md",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)

EXPECTED_TRIGGER_PATHS = (
    "Documentation/zigux/**",
    "scripts/zigux/**",
    "third_party/**",
    "zigux/**",
    ".github/workflows/zigux-bootstrap.yml",
)

ROUTE = "make -C zigux phase2-cross"
EXPECTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")
EXPECTED_ARCHIVE_SCOPE = ("x86_64-linux",)
EXPECTED_SELF_TEST_CASE_COUNT = 15


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


def extract_pull_request_paths(text: str) -> list[str]:
    lines = text.splitlines()
    in_pull_request = False
    in_paths = False
    pull_request_indent = 0
    paths_indent = 0
    collected: list[str] = []

    for raw_line in lines:
        stripped = raw_line.strip()
        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if stripped == "pull_request:":
            in_pull_request = True
            in_paths = False
            pull_request_indent = indent
            continue

        if in_pull_request and indent <= pull_request_indent and stripped and stripped != "pull_request:":
            in_pull_request = False
            in_paths = False

        if not in_pull_request:
            continue

        if stripped == "paths:":
            in_paths = True
            paths_indent = indent
            continue

        if in_paths and indent <= paths_indent and stripped and stripped != "paths:":
            in_paths = False

        if not in_paths:
            continue

        candidate = stripped
        if not candidate.startswith("- "):
            continue

        value = candidate[2:].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        collected.append(value)

    if not collected:
        raise SystemExit(f"missing pull_request.paths block in required file: {WORKFLOW}")

    return collected


def path_matches_trigger(rel_path: str, trigger: str) -> bool:
    return fnmatch.fnmatchcase(rel_path, trigger)


def load_fixture_summary(root: Path) -> tuple[list[str], list[str]]:
    payload = read_json(resolve_path(root, FIXTURE))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, FIXTURE)}")

    if payload.get("route") != ROUTE:
        raise SystemExit(f"invalid route in required file: {resolve_path(root, FIXTURE)}")

    archive_scope = payload.get("archive_target_scope")
    if not isinstance(archive_scope, list):
        raise SystemExit(f"invalid archive_target_scope in required file: {resolve_path(root, FIXTURE)}")

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list):
        raise SystemExit(f"invalid cross_targets in required file: {resolve_path(root, FIXTURE)}")

    archive_values: list[str] = []
    for value in archive_scope:
        if not isinstance(value, str) or not value:
            raise SystemExit(f"invalid archive_target_scope in required file: {resolve_path(root, FIXTURE)}")
        archive_values.append(value)

    target_values: list[str] = []
    for entry in cross_targets:
        if not isinstance(entry, dict):
            raise SystemExit(f"invalid cross_targets entry in required file: {resolve_path(root, FIXTURE)}")
        target = entry.get("target")
        if not isinstance(target, str) or not target:
            raise SystemExit(f"invalid cross_targets entry in required file: {resolve_path(root, FIXTURE)}")
        target_values.append(target)

    return archive_values, target_values


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    trigger_paths = extract_pull_request_paths(workflow_text)

    for marker in EXPECTED_TRIGGER_PATHS:
        count = count_exact_lines(workflow_text, f"- '{marker}'")
        if count == 0:
            issues.append(("MISSING_TRIGGER_PATH", marker))
        elif count != 1:
            issues.append(("DUPLICATE_TRIGGER_PATH", f"{marker}:count={count}"))

    archive_scope, cross_targets = load_fixture_summary(root)
    if tuple(archive_scope) != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("UNEXPECTED_ARCHIVE_SCOPE", ",".join(archive_scope)))
    if tuple(cross_targets) != EXPECTED_CROSS_TARGETS:
        issues.append(("UNEXPECTED_CROSS_TARGETS", ",".join(cross_targets)))

    for rel_path in PACKET_PATHS:
        if not any(path_matches_trigger(rel_path, trigger) for trigger in trigger_paths):
            issues.append(("UNCOVERED_PACKET_PATH", rel_path))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_TRIGGER_PATHS=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, WORKFLOW),
        "\n".join(
            (
                "name: zigux-bootstrap",
                "on:",
                "  pull_request:",
                "    paths:",
                *[f"      - '{marker}'" for marker in EXPECTED_TRIGGER_PATHS],
            )
        )
        + "\n",
    )
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
    for rel_path in PACKET_PATHS:
        path = resolve_path(root, ROOT / rel_path)
        if not path.exists():
            write_text(path, "present\n")


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
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_trigger_paths_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in EXPECTED_TRIGGER_PATHS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), f"- '{marker}'", "      - 'other/**'"), encoding="utf-8")
            assert ("MISSING_TRIGGER_PATH", marker) in collect_issues(root)
            checks_run += 1

        for marker in EXPECTED_TRIGGER_PATHS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), f"- '{marker}'"), encoding="utf-8")
            assert ("DUPLICATE_TRIGGER_PATH", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("UNEXPECTED_ARCHIVE_SCOPE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"] = [fixture["cross_targets"][0]]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("UNEXPECTED_CROSS_TARGETS", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), "- 'third_party/**'", "      - 'tools/**'"), encoding="utf-8")
        assert ("UNCOVERED_PACKET_PATH", "third_party/README.md") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, WORKFLOW)
        path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing workflow file did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_TRIGGER_PATHS_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TRIGGER_PATHS_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the current workflow trigger globs still cover the Phase 2 cross packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_TRIGGER_PATHS=pass")
    print(f"PHASE2_CROSS_TRIGGER_PATHS_TRIGGER_COUNT={len(EXPECTED_TRIGGER_PATHS)}")
    print(f"PHASE2_CROSS_TRIGGER_PATHS_PACKET_PATH_COUNT={len(PACKET_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
