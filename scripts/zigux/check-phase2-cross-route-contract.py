#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

ROUTE = "make -C zigux phase2-cross"
SUPPORTED_TARGETS = ("x86_64-linux", "aarch64-linux")
EXPECTED_FIXTURE_PHASE = "Phase 2"
EXPECTED_FIXTURE_STATUS = "active"
EXPECTED_REQUIRED_MAKE_ROUTES = ("phase2-toolchain", "phase2-validate")

PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit through the pinned `x86_64-linux` `archive_required` lane plus the `aarch64-linux` `route_contract_only` lane",
    "`make -C zigux phase2-cross`",
)

MAKEFILE_LINES = (
    "phase2-cross:",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
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


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line == marker)


def load_policy_contract(root: Path) -> dict[str, object]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")

    archive_sha256 = payload.get("archive_sha256")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise SystemExit(f"invalid archive_sha256 in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    required_make_routes = upgrade_policy.get("required_make_routes")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(
            f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )
    if not isinstance(required_make_routes, list):
        raise SystemExit(
            f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )

    normalized_scope: list[str] = []
    seen_targets: set[str] = set()
    for value in archive_target_scope:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        target = value.strip()
        if target in seen_targets:
            raise SystemExit(
                f"duplicate archive_target_scope entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        if target not in SUPPORTED_TARGETS:
            raise SystemExit(
                f"unsupported archive_target_scope target in required file: {resolve_path(root, TOOLCHAIN_POLICY)}: {target}"
            )
        normalized_scope.append(target)
        seen_targets.add(target)

    normalized_routes: list[str] = []
    for value in required_make_routes:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        normalized_routes.append(value.strip())

    archive_hash_targets: list[str] = []
    for target, digest in archive_sha256.items():
        if not isinstance(target, str) or not target.strip():
            raise SystemExit(
                f"invalid archive_sha256 target in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        if not isinstance(digest, str) or len(digest.strip()) != 64:
            raise SystemExit(
                f"invalid archive_sha256 digest in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        archive_hash_targets.append(target.strip())

    return {
        "archive_target_scope": normalized_scope,
        "required_make_routes": normalized_routes,
        "archive_hash_targets": sorted(archive_hash_targets),
    }


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    fixture = read_json(resolve_path(root, FIXTURE))
    policy = load_policy_contract(root)

    for marker in PHASE2_NOTES_MARKERS:
        if marker not in notes_text:
            issues.append(("MISSING_PHASE2_NOTES_MARKER", marker))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    expected_scope = policy["archive_target_scope"]
    expected_routes = policy["required_make_routes"]
    expected_hash_targets = policy["archive_hash_targets"]

    if expected_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):
        issues.append(("INVALID_REQUIRED_MAKE_ROUTES", ",".join(expected_routes)))

    if expected_hash_targets != sorted(expected_scope):
        issues.append(("ARCHIVE_HASH_TARGET_MISMATCH", ",".join(expected_hash_targets)))

    if not isinstance(fixture, dict):
        issues.append(("INVALID_FIXTURE_SHAPE", type(fixture).__name__))
        return issues

    if fixture.get("phase") != EXPECTED_FIXTURE_PHASE:
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if fixture.get("status") != EXPECTED_FIXTURE_STATUS:
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if fixture.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if fixture.get("archive_target_scope") != expected_scope:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = fixture.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    actual_modes: dict[str, str] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        validation_mode = entry.get("validation_mode")
        review_status = entry.get("review_status")
        route = entry.get("route")
        if not isinstance(target, str) or not target.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        target = target.strip()
        if target not in SUPPORTED_TARGETS:
            issues.append(("UNSUPPORTED_CROSS_TARGET", target))
            continue
        if target in actual_modes:
            issues.append(("DUPLICATE_CROSS_TARGET", target))
        if not isinstance(validation_mode, str) or not validation_mode.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        if not isinstance(review_status, str) or not review_status.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        actual_modes[target] = validation_mode.strip()

    expected_modes = {
        target: ("archive_required" if target in expected_scope else "route_contract_only")
        for target in SUPPORTED_TARGETS
    }
    if actual_modes != expected_modes:
        issues.append(("INVALID_CROSS_TARGET_MATRIX", json.dumps(actual_modes, sort_keys=True)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_ROUTE_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
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
                    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
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


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_route_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in PHASE2_NOTES_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_PHASE2_NOTES_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, MAKEFILE)
        path.write_text(
            duplicate_exact_line(path.read_text(encoding="utf-8"), MAKEFILE_LINES[1]),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_MAKEFILE_LINE",
            f"{MAKEFILE_LINES[1]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-cross"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_REQUIRED_MAKE_ROUTES", "phase2-cross") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_sha256"] = {"aarch64-linux": "4" * 64}
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("ARCHIVE_HASH_TARGET_MISMATCH", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["riscv64-linux"]
        payload["archive_sha256"] = {"riscv64-linux": "5" * 64}
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "unsupported archive_target_scope target" in str(exc)
        else:
            raise AssertionError("unsupported archive target did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["validation_mode"] = "archive_required"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_CROSS_TARGET_MATRIX" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"].append(dict(payload["cross_targets"][0]))
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_CROSS_TARGET", "x86_64-linux") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["review_status"] = ""
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ENTRY", "x86_64-linux:review_status") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["route"] = "make -C zigux phase2"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ROUTE", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        for target_path in (PHASE2_NOTES, MAKEFILE, TOOLCHAIN_POLICY, FIXTURE):
            build_self_test_root(root)
            resolve_path(root, target_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
            else:
                raise AssertionError(f"missing file did not abort: {target_path}")
            checks_run += 1

    print("PHASE2_CROSS_ROUTE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the live Phase 2 direct cross-route packet stays aligned "
            "across the notes, make route, toolchain policy, and target fixture."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    policy = load_policy_contract(args.root.resolve())
    print("PHASE2_CROSS_ROUTE_CONTRACT=pass")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_TARGET_COUNT={len(SUPPORTED_TARGETS)}")
    print(
        "PHASE2_CROSS_ROUTE_CONTRACT_ARCHIVE_SCOPE_COUNT="
        f"{len(policy['archive_target_scope'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
