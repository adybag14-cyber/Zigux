#!/usr/bin/env python3
"""Guard the Phase 2 cross packet described by the shared review checklist."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"

SUPPORTED_TARGETS = ("x86_64-linux", "aarch64-linux")
ROUTE = "make -C zigux phase2-cross"

REVIEW_CHECKLIST_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`make -C zigux phase2-cross`",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: make -C zigux phase2-cross",
)

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)


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


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


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


def load_expected_packet(root: Path) -> dict[str, object]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")

    archive_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_scope, list) or len(archive_scope) != 1:
        raise SystemExit(
            f"expected exactly one archive_target_scope entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )

    archive_target = archive_scope[0]
    if not isinstance(archive_target, str) or archive_target not in SUPPORTED_TARGETS:
        raise SystemExit(
            f"unsupported archive_target_scope target in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )

    route_contract_target = next(target for target in SUPPORTED_TARGETS if target != archive_target)
    return {
        "archive_target": archive_target,
        "route_contract_target": route_contract_target,
        "expected_modes": {
            archive_target: "archive_required",
            route_contract_target: "route_contract_only",
        },
        "expected_review_statuses": {
            archive_target: "pinned bootstrap archive",
            route_contract_target: "route contract only",
        },
    }


def collect_review_checklist_issues(root: Path) -> list[tuple[str, str]]:
    review_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    return [
        ("MISSING_REVIEW_CHECKLIST_MARKER", marker)
        for marker in REVIEW_CHECKLIST_MARKERS
        if marker not in review_text
    ]


def collect_exact_line_issues(root: Path, path: Path, markers: tuple[str, ...], prefix: str) -> list[tuple[str, str]]:
    text = read_text(resolve_path(root, path))
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((f"MISSING_{prefix}_LINE", marker))
        elif count != 1:
            issues.append((f"DUPLICATE_{prefix}_LINE", f"{marker}:count={count}"))
    return issues


def collect_fixture_issues(root: Path, packet: dict[str, object]) -> list[tuple[str, str]]:
    payload = read_json(resolve_path(root, FIXTURE))
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", type(payload).__name__)]

    if payload.get("phase") != "Phase 2":
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if payload.get("status") != "active":
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if payload.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if payload.get("archive_target_scope") != [packet["archive_target"]]:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or len(cross_targets) != len(SUPPORTED_TARGETS):
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    actual_modes: dict[str, str] = {}
    actual_statuses: dict[str, str] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", type(entry).__name__))
            continue

        target = entry.get("target")
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")

        if not isinstance(target, str) or not target:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        if target in actual_modes:
            issues.append(("DUPLICATE_CROSS_TARGET_ENTRY", target))
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if not isinstance(validation_mode, str) or not validation_mode:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        if not isinstance(review_status, str) or not review_status:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
            continue

        actual_modes[target] = validation_mode
        actual_statuses[target] = review_status

    if actual_modes != packet["expected_modes"]:
        issues.append(("INVALID_CROSS_TARGET_MODES", json.dumps(actual_modes, sort_keys=True)))
    if actual_statuses != packet["expected_review_statuses"]:
        issues.append(("INVALID_CROSS_TARGET_REVIEW_STATUSES", json.dumps(actual_statuses, sort_keys=True)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    packet = load_expected_packet(root)
    issues: list[tuple[str, str]] = []
    issues.extend(collect_review_checklist_issues(root))
    issues.extend(collect_exact_line_issues(root, WORKFLOW, WORKFLOW_LINES, "WORKFLOW"))
    issues.extend(collect_exact_line_issues(root, MAKEFILE, MAKEFILE_LINES, "MAKEFILE"))
    issues.extend(collect_fixture_issues(root, packet))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path, archive_target: str = "x86_64-linux") -> None:
    route_contract_target = next(target for target in SUPPORTED_TARGETS if target != archive_target)

    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {archive_target: "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [archive_target],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(
        resolve_path(root, FIXTURE),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": ROUTE,
                "archive_target_scope": [archive_target],
                "cross_targets": [
                    {
                        "target": archive_target,
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": ROUTE,
                    },
                    {
                        "target": route_contract_target,
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
    expected_case_count = 1 + len(REVIEW_CHECKLIST_MARKERS) + len(WORKFLOW_LINES) + len(WORKFLOW_LINES) + len(
        MAKEFILE_LINES
    ) + len(MAKEFILE_LINES) + 10 + 5
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_review_checklist_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REVIEW_CHECKLIST_MARKERS:
            build_sample_root(root)
            checklist_path = resolve_path(root, REVIEW_CHECKLIST)
            checklist_path.write_text(replace_once(checklist_path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_REVIEW_CHECKLIST_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for line in WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), line), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", line) in collect_issues(root)
            checks_run += 1

        for line in WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), line), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINE", f"{line}:count=2") in collect_issues(root)
            checks_run += 1

        for line in MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), line), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", line) in collect_issues(root)
            checks_run += 1

        for line in MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), line), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINE", f"{line}:count=2") in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["phase"] = "Phase X"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "phase") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["status"] = "blocked"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "status") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["route"] = "make -C zigux phase2"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "route") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["validation_mode"] = "route_contract_only"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_CROSS_TARGET_MODES" for code, _ in collect_issues(root))
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["review_status"] = "wrong"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_CROSS_TARGET_REVIEW_STATUSES" for code, _ in collect_issues(root))
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["route"] = "make -C zigux phase2"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ROUTE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["target"] = payload["cross_targets"][0]["target"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("DUPLICATE_CROSS_TARGET_ENTRY", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_sample_root(root, archive_target="aarch64-linux")
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["archive_target_scope"] = ["riscv64-linux"]
        policy["archive_sha256"] = {"riscv64-linux": "3" * 64}
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "unsupported archive_target_scope target" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("unsupported archive target did not abort")

        for path in (REVIEW_CHECKLIST, TOOLCHAIN_POLICY, FIXTURE, WORKFLOW, MAKEFILE):
            build_sample_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    assert checks_run == expected_case_count
    print("PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared review checklist keeps the live Phase 2 cross packet explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a passing sample repository skeleton to the given root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    packet = load_expected_packet(root)
    print("PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT=pass")
    print(f"PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT_ARCHIVE_TARGET={packet['archive_target']}")
    print(f"PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT_ROUTE_TARGET={packet['route_contract_target']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
