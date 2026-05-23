#!/usr/bin/env python3
"""Keep the Phase 2 cross-target review-status packet aligned."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
THIRD_PARTY_README = ROOT / "third_party" / "README.md"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"

ROUTE = "make -C zigux phase2-cross"
SUPPORTED_TARGETS = ("x86_64-linux", "aarch64-linux")
EXPECTED_TARGET_PACKET = {
    "x86_64-linux": {
        "review_status": "pinned bootstrap archive",
        "validation_mode": "archive_required",
    },
    "aarch64-linux": {
        "review_status": "route contract only",
        "validation_mode": "route_contract_only",
    },
}

THIRD_PARTY_README_MARKERS = (
    "- target: `x86_64-linux`",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
)

PHASE2_NOTES_MARKERS = (
    "- `scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `0.17.0-dev.87+9b177a7d2`, keeps the minimum version in lockstep, limits archive digests to `x86_64-linux`, and names `phase2-toolchain`, `phase2-validate`, and `phase2-cross` as the required Linux-style make routes when those routes are rematerialized.",
    "- `zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit through the pinned `x86_64-linux` `archive_required` lane plus the `aarch64-linux` `route_contract_only` lane, so toolchain follow-through should treat the returned cross packet as present evidence instead of a repo-reality gap.",
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


def load_policy(root: Path) -> tuple[list[str], list[str]]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    required_make_routes = upgrade_policy.get("required_make_routes")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(
            f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )
    if not isinstance(required_make_routes, list) or not required_make_routes:
        raise SystemExit(
            f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )

    normalized_scope: list[str] = []
    seen_scope: set[str] = set()
    for value in archive_target_scope:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        target = value.strip()
        if target in seen_scope:
            raise SystemExit(
                f"duplicate archive_target_scope entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        if target not in SUPPORTED_TARGETS:
            raise SystemExit(
                "unsupported archive_target_scope targets in required file: " + target
            )
        normalized_scope.append(target)
        seen_scope.add(target)

    normalized_routes: list[str] = []
    seen_routes: set[str] = set()
    for value in required_make_routes:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        route = value.strip()
        if route in seen_routes:
            raise SystemExit(
                f"duplicate required_make_routes entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        normalized_routes.append(route)
        seen_routes.add(route)

    return normalized_scope, normalized_routes


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    archive_target_scope, required_make_routes = load_policy(root)

    third_party_readme = read_text(resolve_path(root, THIRD_PARTY_README))
    for marker in THIRD_PARTY_README_MARKERS:
        if marker not in third_party_readme:
            issues.append(("MISSING_THIRD_PARTY_README_MARKER", marker))

    phase2_notes = read_text(resolve_path(root, PHASE2_NOTES))
    for marker in PHASE2_NOTES_MARKERS:
        if marker not in phase2_notes:
            issues.append(("MISSING_PHASE2_NOTES_MARKER", marker))

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    if "phase2-cross" not in required_make_routes:
        issues.append(("MISSING_REQUIRED_MAKE_ROUTE", "phase2-cross"))

    fixture = read_json(resolve_path(root, CROSS_TARGETS))
    if not isinstance(fixture, dict):
        return [("INVALID_CROSS_TARGET_FIXTURE", type(fixture).__name__)]

    if fixture.get("phase") != "Phase 2":
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "phase"))
    if fixture.get("status") != "active":
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "status"))
    if fixture.get("route") != ROUTE:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "route"))
    if fixture.get("archive_target_scope") != archive_target_scope:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = fixture.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "cross_targets"))
        return issues

    seen_targets: set[str] = set()
    actual_packet: dict[str, dict[str, str]] = {}
    archive_required_targets: list[str] = []

    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", type(entry).__name__))
            continue

        target = entry.get("target")
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")

        if not isinstance(target, str) or not target.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        target = target.strip()
        if target in seen_targets:
            issues.append(("DUPLICATE_CROSS_TARGET_ENTRY", target))
        seen_targets.add(target)

        if target not in SUPPORTED_TARGETS:
            issues.append(("UNSUPPORTED_CROSS_TARGET", target))

        if not isinstance(review_status, str) or not review_status.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
            continue
        if not isinstance(validation_mode, str) or not validation_mode.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))

        review_status = review_status.strip()
        validation_mode = validation_mode.strip()
        actual_packet[target] = {
            "review_status": review_status,
            "validation_mode": validation_mode,
        }
        if validation_mode == "archive_required":
            archive_required_targets.append(target)

    if actual_packet != EXPECTED_TARGET_PACKET:
        issues.append(("INVALID_REVIEW_STATUS_PACKET", json.dumps(actual_packet, sort_keys=True)))

    if sorted(archive_required_targets) != sorted(archive_target_scope):
        issues.append(("ARCHIVE_REQUIRED_TARGET_SCOPE_MISMATCH", ",".join(sorted(archive_required_targets))))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_REVIEW_STATUS_CONTRACT=fail")
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
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(resolve_path(root, CROSS_TARGETS), json.dumps(
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
    ) + "\n")
    write_text(resolve_path(root, THIRD_PARTY_README), "\n".join(THIRD_PARTY_README_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(("name: zigux-bootstrap", *WORKFLOW_LINES)) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(("PYTHON ?= python3", "PHASE2_SCRIPT_ROOT := ../scripts/zigux", *MAKEFILE_LINES)) + "\n")


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
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
    expected_case_count = (
        1
        + len(THIRD_PARTY_README_MARKERS)
        + len(PHASE2_NOTES_MARKERS)
        + len(WORKFLOW_LINES)
        + len(WORKFLOW_LINES)
        + len(MAKEFILE_LINES)
        + len(MAKEFILE_LINES)
        + 15
        + 6
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_review_status_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in THIRD_PARTY_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, THIRD_PARTY_README)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_THIRD_PARTY_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in PHASE2_NOTES_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_PHASE2_NOTES_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: echo removed"), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_REQUIRED_MAKE_ROUTE", "phase2-cross") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["phase"] = "Phase X"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_FIXTURE_FIELD", "phase") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["status"] = "blocked"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_FIXTURE_FIELD", "status") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["route"] = "make -C zigux phase2"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_FIXTURE_FIELD", "route") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["review_status"] = "route contract only"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_REVIEW_STATUS_PACKET" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["review_status"] = ""
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ENTRY", "aarch64-linux:review_status") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["validation_mode"] = ""
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ENTRY", "aarch64-linux:validation_mode") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["route"] = "make -C zigux phase2"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ROUTE", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["validation_mode"] = "archive_required"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "INVALID_REVIEW_STATUS_PACKET" for code, _ in issues)
        assert ("ARCHIVE_REQUIRED_TARGET_SCOPE_MISMATCH", "aarch64-linux,x86_64-linux") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"].append(dict(payload["cross_targets"][0]))
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("DUPLICATE_CROSS_TARGET_ENTRY", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["target"] = "riscv64-linux"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("UNSUPPORTED_CROSS_TARGET", "riscv64-linux") in issues
        assert any(code == "INVALID_REVIEW_STATUS_PACKET" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["riscv64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "unsupported archive_target_scope targets" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("unsupported archive_target_scope target did not abort")

        build_self_test_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid fixture json did not abort")

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid policy json did not abort")

        build_self_test_root(root)
        for path in (THIRD_PARTY_README, PHASE2_NOTES, WORKFLOW, MAKEFILE, TOOLCHAIN_POLICY, CROSS_TARGETS):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    assert checks_run == expected_case_count
    print("PHASE2_CROSS_REVIEW_STATUS_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_REVIEW_STATUS_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 cross review-status packet aligned with the live policy and reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    archive_target_scope, _ = load_policy(args.root.resolve())
    print("PHASE2_CROSS_REVIEW_STATUS_CONTRACT=pass")
    print(f"PHASE2_CROSS_REVIEW_STATUS_CONTRACT_ARCHIVE_SCOPE_COUNT={len(archive_target_scope)}")
    print(f"PHASE2_CROSS_REVIEW_STATUS_CONTRACT_TARGET_COUNT={len(EXPECTED_TARGET_PACKET)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
