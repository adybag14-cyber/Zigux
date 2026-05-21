#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
VALIDATOR = Path("scripts/zigux/validate-phase2.py")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
FIXTURE = Path("zigux/tests/fixtures/phase2_cross_targets.json")
CROSS_CHECKER = Path("scripts/zigux/check-phase2-cross.py")
ALIGNMENT_CHECKER = Path("scripts/zigux/check-phase2-cross-selftest-alignment.py")

ROUTE = "make -C zigux phase2-cross"
PHASE2_VALIDATE_ROUTE = "run: make -C zigux phase2-validate"

REQUIRED_PATHS = (
    VALIDATOR.as_posix(),
    WORKFLOW.as_posix(),
    MAKEFILE.as_posix(),
    TOOLCHAIN_POLICY.as_posix(),
    FIXTURE.as_posix(),
    CROSS_CHECKER.as_posix(),
    ALIGNMENT_CHECKER.as_posix(),
)

REQUIRED_VALIDATE_SNIPPETS = (
    f'"{CROSS_CHECKER.as_posix()}",',
    f'"{ALIGNMENT_CHECKER.as_posix()}",',
    f'"{FIXTURE.as_posix()}",',
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    PHASE2_VALIDATE_ROUTE,
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")
EXPECTED_SELF_TEST_CASE_COUNT = 23


def resolve_path(root: Path, relative_path: str) -> Path:
    return root / relative_path


def read_text(root: Path, relative_path: str) -> str:
    path = resolve_path(root, relative_path)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = resolve_path(root, relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(root: Path, relative_path: str) -> object:
    path = resolve_path(root, relative_path)
    try:
        return json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


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


def load_archive_target_scope(root: Path) -> list[str]:
    payload = read_json(root, TOOLCHAIN_POLICY.as_posix())
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY.as_posix())}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY.as_posix())}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(
            f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY.as_posix())}"
        )

    normalized: list[str] = []
    seen: set[str] = set()
    for value in archive_target_scope:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY.as_posix())}"
            )
        value = value.strip()
        if value in seen:
            raise SystemExit(
                f"duplicate archive_target_scope entry in required file: {resolve_path(root, TOOLCHAIN_POLICY.as_posix())}"
            )
        normalized.append(value)
        seen.add(value)
    return normalized


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    validator_text = read_text(root, VALIDATOR.as_posix())
    workflow_text = read_text(root, WORKFLOW.as_posix())
    makefile_text = read_text(root, MAKEFILE.as_posix())
    fixture = read_json(root, FIXTURE.as_posix())
    archive_target_scope = load_archive_target_scope(root)

    for relative_path in REQUIRED_PATHS:
        if not resolve_path(root, relative_path).exists():
            issues.append(("MISSING_REQUIRED_PATH", relative_path))

    for snippet in REQUIRED_VALIDATE_SNIPPETS:
        count = count_exact_lines(validator_text, snippet)
        if count == 0:
            issues.append(("MISSING_VALIDATE_SNIPPET", snippet))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATE_SNIPPET", f"{snippet}:count={count}"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    if not isinstance(fixture, dict):
        issues.append(("INVALID_FIXTURE_SHAPE", "root"))
        return issues

    if fixture.get("phase") != "Phase 2":
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if fixture.get("status") != "active":
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if fixture.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if fixture.get("archive_target_scope") != archive_target_scope:
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
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")

        if not isinstance(target, str) or not target.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue

        target = target.strip()
        if target in actual_modes:
            issues.append(("DUPLICATE_CROSS_TARGET_ENTRY", target))
        if not isinstance(review_status, str) or not review_status.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
        if validation_mode not in ALLOWED_VALIDATION_MODES:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        actual_modes[target] = validation_mode

    expected_modes = {
        "x86_64-linux": "archive_required" if "x86_64-linux" in archive_target_scope else "route_contract_only",
        "aarch64-linux": "archive_required" if "aarch64-linux" in archive_target_scope else "route_contract_only",
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
    write_text(
        root,
        VALIDATOR.as_posix(),
        "\n".join(REQUIRED_VALIDATE_SNIPPETS) + "\n",
    )
    write_text(
        root,
        WORKFLOW.as_posix(),
        "\n".join(REQUIRED_WORKFLOW_LINES) + "\n",
    )
    write_text(
        root,
        MAKEFILE.as_posix(),
        "\n".join(REQUIRED_MAKEFILE_LINES) + "\n",
    )
    write_text(
        root,
        TOOLCHAIN_POLICY.as_posix(),
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
        root,
        FIXTURE.as_posix(),
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
    write_text(root, CROSS_CHECKER.as_posix(), "present\n")
    write_text(root, ALIGNMENT_CHECKER.as_posix(), "present\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_route_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            write_text(root, WORKFLOW.as_posix(), replace_exact_line(read_text(root, WORKFLOW.as_posix()), marker, "# removed"))
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            write_text(root, MAKEFILE.as_posix(), replace_exact_line(read_text(root, MAKEFILE.as_posix()), marker, "# removed"))
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for snippet in REQUIRED_VALIDATE_SNIPPETS[:5]:
            build_self_test_root(root)
            write_text(
                root,
                VALIDATOR.as_posix(),
                replace_exact_line(read_text(root, VALIDATOR.as_posix()), snippet, "BROKEN_SNIPPET"),
            )
            assert ("MISSING_VALIDATE_SNIPPET", snippet) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW.as_posix(), duplicate_exact_line(read_text(root, WORKFLOW.as_posix()), REQUIRED_WORKFLOW_LINES[0]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[0]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE.as_posix(), duplicate_exact_line(read_text(root, MAKEFILE.as_posix()), REQUIRED_MAKEFILE_LINES[0]))
        assert ("DUPLICATE_MAKEFILE_LINE", f"{REQUIRED_MAKEFILE_LINES[0]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = json.loads(read_text(root, FIXTURE.as_posix()))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        write_text(root, FIXTURE.as_posix(), json.dumps(fixture, indent=2) + "\n")
        assert ("INVALID_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = json.loads(read_text(root, FIXTURE.as_posix()))
        fixture["cross_targets"][1]["route"] = "make -C zigux phase2"
        write_text(root, FIXTURE.as_posix(), json.dumps(fixture, indent=2) + "\n")
        assert ("INVALID_CROSS_TARGET_ROUTE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = json.loads(read_text(root, FIXTURE.as_posix()))
        fixture["cross_targets"][1]["validation_mode"] = "archive_required"
        write_text(root, FIXTURE.as_posix(), json.dumps(fixture, indent=2) + "\n")
        assert any(code == "INVALID_CROSS_TARGET_MATRIX" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        fixture = json.loads(read_text(root, FIXTURE.as_posix()))
        fixture["cross_targets"].append(fixture["cross_targets"][0].copy())
        write_text(root, FIXTURE.as_posix(), json.dumps(fixture, indent=2) + "\n")
        assert ("DUPLICATE_CROSS_TARGET_ENTRY", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, TOOLCHAIN_POLICY.as_posix()).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing toolchain policy did not abort")

        build_self_test_root(root)
        write_text(root, TOOLCHAIN_POLICY.as_posix(), "{\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid policy json did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT, (checks_run, EXPECTED_SELF_TEST_CASE_COUNT)
    print("PHASE2_CROSS_ROUTE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current Phase 2 direct cross-route packet aligned across the shared closure surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    archive_target_scope = load_archive_target_scope(args.root.resolve())
    print("PHASE2_CROSS_ROUTE_CONTRACT=pass")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_VALIDATE_SNIPPET_COUNT={len(REQUIRED_VALIDATE_SNIPPETS)}")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_ARCHIVE_SCOPE_COUNT={len(archive_target_scope)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
