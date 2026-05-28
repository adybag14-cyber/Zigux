#!/usr/bin/env python3
"""Guard the tests-readme side of the live Phase 2 cross packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_ARCHIVE_SCOPE = ["x86_64-linux"]
EXPECTED_REQUIRED_MAKE_ROUTES = [
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
]
EXPECTED_CROSS_TARGETS = [
    {
        "target": "x86_64-linux",
        "review_status": "pinned bootstrap archive",
        "validation_mode": "archive_required",
        "route": EXPECTED_ROUTE,
    },
    {
        "target": "aarch64-linux",
        "review_status": "route contract only",
        "validation_mode": "route_contract_only",
        "route": EXPECTED_ROUTE,
    },
]

TESTS_README_DIRECT_PACKET_SENTENCE = (
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, "
    "`python3 scripts/zigux/install-zig.py --self-test`, "
    "`scripts/zigux/check-phase2-cross.py`, "
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`, and "
    "`zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, "
    "direct cross-route, and cross-target fixture packet explicit here instead of leaving "
    "it in the historical-gap bucket"
)
TESTS_README_WRAPPER_SENTENCE = (
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, "
    "`make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, "
    "`make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, "
    "`make -C zigux phase2-validate`, and `make -C zigux phase2`."
)
BOOTSTRAP_NOTES_CROSS_SENTENCE = (
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct "
    "cross-route packet explicit through the pinned `x86_64-linux` `archive_required` "
    "lane plus the `aarch64-linux` `route_contract_only` lane, so toolchain follow-through "
    "should treat the returned cross packet as present evidence instead of a repo-reality gap."
)

TESTS_README_MARKERS = [
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    TESTS_README_DIRECT_PACKET_SENTENCE,
    TESTS_README_WRAPPER_SENTENCE,
]
BOOTSTRAP_NOTES_MARKERS = [
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`make -C zigux phase2-cross`",
    BOOTSTRAP_NOTES_CROSS_SENTENCE,
]
MAKEFILE_LINES = [
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
]
FORBIDDEN_STALE_MARKERS = [
    "three-target compile matrix",
    "riscv64-linux-musl",
    "riscv64-linux",
]
EXPECTED_SELF_TEST_CASE_COUNT = 11


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def validate_markers(text: str, *, label: str, markers: list[str]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        if marker not in text:
            issues.append(("MISSING_MARKER", f"{label}:{marker}"))
    return issues


def validate_forbidden(text: str, *, label: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in FORBIDDEN_STALE_MARKERS:
        if marker in text:
            issues.append(("FORBIDDEN_STALE_MARKER", f"{label}:{marker}"))
    return issues


def validate_makefile(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in MAKEFILE_LINES:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))
    return issues


def validate_policy(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_SHAPE", "root")]

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return [("INVALID_POLICY_FIELD", "upgrade_policy")]

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if archive_target_scope != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_POLICY_FIELD", "archive_target_scope"))

    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != EXPECTED_REQUIRED_MAKE_ROUTES:
        issues.append(("INVALID_POLICY_FIELD", "required_make_routes"))
    return issues


def validate_fixture(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", "root")]

    if payload.get("phase") != "Phase 2":
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if payload.get("status") != "active":
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if payload.get("route") != EXPECTED_ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if payload.get("archive_target_scope") != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = payload.get("cross_targets")
    if cross_targets != EXPECTED_CROSS_TARGETS:
        issues.append(("INVALID_CROSS_TARGET_PACKET", repr(cross_targets)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    bootstrap_notes_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    policy = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    fixture = read_json(resolve_path(root, FIXTURE))

    issues.extend(validate_markers(tests_readme_text, label="tests_readme", markers=TESTS_README_MARKERS))
    issues.extend(validate_markers(bootstrap_notes_text, label="bootstrap_notes", markers=BOOTSTRAP_NOTES_MARKERS))
    issues.extend(validate_forbidden(tests_readme_text, label="tests_readme"))
    issues.extend(validate_forbidden(bootstrap_notes_text, label="bootstrap_notes"))
    issues.extend(validate_makefile(makefile_text))
    issues.extend(validate_policy(policy))
    issues.extend(validate_fixture(fixture))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_TESTS_README_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(BOOTSTRAP_NOTES_MARKERS) + "\n")
    write_text(
        resolve_path(root, MAKEFILE),
        "\n".join(
            [
                "phase2-cross:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
                "",
                "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
                "",
                "phase2: phase2-validate",
                "",
            ]
        ),
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
                    "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                    "required_make_routes": EXPECTED_REQUIRED_MAKE_ROUTES,
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
                "route": EXPECTED_ROUTE,
                "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                "cross_targets": EXPECTED_CROSS_TARGETS,
            },
            indent=2,
        )
        + "\n",
    )


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise AssertionError(f"marker not found: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_tests_readme_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        tests_path = resolve_path(root, TESTS_README)
        build_self_test_root(root)
        tests_path.write_text(
            replace_once(
                tests_path.read_text(encoding="utf-8"),
                "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
                "`scripts/zigux/check-phase2-cross-target-replay.py`",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_MARKER",
            "tests_readme:`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        tests_path.write_text(tests_path.read_text(encoding="utf-8") + "riscv64-linux\n", encoding="utf-8")
        assert ("FORBIDDEN_STALE_MARKER", "tests_readme:riscv64-linux") in collect_issues(root)
        checks_run += 1

        bootstrap_path = resolve_path(root, BOOTSTRAP_NOTES)
        build_self_test_root(root)
        bootstrap_path.write_text(
            replace_once(bootstrap_path.read_text(encoding="utf-8"), BOOTSTRAP_NOTES_CROSS_SENTENCE, "older wording"),
            encoding="utf-8",
        )
        assert ("MISSING_MARKER", f"bootstrap_notes:{BOOTSTRAP_NOTES_CROSS_SENTENCE}") in collect_issues(root)
        checks_run += 1

        makefile_path = resolve_path(root, MAKEFILE)
        build_self_test_root(root)
        makefile_path.write_text(
            replace_once(
                makefile_path.read_text(encoding="utf-8"),
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-target-replay.py --self-test",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_MAKEFILE_LINE",
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
        ) in collect_issues(root)
        checks_run += 1

        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        build_self_test_root(root)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-cross"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_FIELD", "required_make_routes") in collect_issues(root)
        checks_run += 1

        fixture_path = resolve_path(root, FIXTURE)
        build_self_test_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"].append(
            {
                "target": "riscv64-linux",
                "review_status": "historical only",
                "validation_mode": "route_contract_only",
                "route": EXPECTED_ROUTE,
            }
        )
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_CROSS_TARGET_PACKET" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        bootstrap_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing bootstrap notes did not abort")
        checks_run += 1

        build_self_test_root(root)
        fixture_path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
        else:
            raise AssertionError("invalid fixture json did not abort")
        checks_run += 1

        build_self_test_root(root)
        policy_path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
        else:
            raise AssertionError("invalid policy json did not abort")
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_TESTS_README_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TESTS_README_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the tests-readme side of the Phase 2 cross packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_TESTS_README_CONTRACT=pass")
    print(f"PHASE2_CROSS_TESTS_README_CONTRACT_TARGET_COUNT={len(EXPECTED_CROSS_TARGETS)}")
    print("PHASE2_CROSS_TESTS_README_CONTRACT_REQUIRED_PATH_COUNT=5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
