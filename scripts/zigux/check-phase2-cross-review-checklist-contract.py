#!/usr/bin/env python3
"""Guard the Phase 2 cross review-checklist contract."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
MAKEFILE = ROOT / "zigux" / "Makefile"

ROUTE = "make -C zigux phase2-cross"
EXPECTED_ARCHIVE_SCOPE = ["x86_64-linux"]
EXPECTED_REQUIRED_ROUTES = [
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
]
EXPECTED_TARGETS = {
    "x86_64-linux": ("pinned bootstrap archive", "archive_required"),
    "aarch64-linux": ("route contract only", "route_contract_only"),
}
MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

REQUIRED_REVIEW_CHECKLIST_MARKERS = (
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`make -C zigux phase2-cross`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

REQUIRED_PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    f"`{ROUTE}`",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
)

REQUIRED_TESTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "Does the bounded Phase 2 reminder keep the current direct-readback toolchain self-check, repo-local archive workflow, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, validator, closure-validator, helper-local kconfig allconfig guard, kconfig bridge, genksyms bridge, fixdep packet, make-wrapper, and fixture packet aligned without reviving older missing validator-first or wrapper-only proof?",
)

EXPECTED_SELF_TEST_CASE_COUNT = 13


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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def load_required_routes(root: Path) -> list[str]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    required_routes = upgrade_policy.get("required_make_routes")
    if not isinstance(required_routes, list):
        raise SystemExit(f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    if any(not isinstance(route, str) for route in required_routes):
        raise SystemExit(f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    return required_routes


def load_archive_scope(root: Path) -> list[str]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    archive_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_scope, list):
        raise SystemExit(f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    if any(not isinstance(target, str) for target in archive_scope):
        raise SystemExit(f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    return archive_scope


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    review_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    tests_text = read_text(resolve_path(root, TESTS_README))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    fixture = read_json(resolve_path(root, FIXTURE))
    required_routes = load_required_routes(root)
    archive_scope = load_archive_scope(root)

    issues.extend(
        collect_missing_markers(
            review_text,
            REQUIRED_REVIEW_CHECKLIST_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            notes_text,
            REQUIRED_PHASE2_NOTES_MARKERS,
            "MISSING_PHASE2_NOTES_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            tests_text,
            REQUIRED_TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKER",
        )
    )

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    if required_routes != EXPECTED_REQUIRED_ROUTES:
        issues.append(("REQUIRED_ROUTE_SET_MISMATCH", ",".join(required_routes)))
    if archive_scope != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("ARCHIVE_SCOPE_MISMATCH", ",".join(archive_scope)))

    if not isinstance(fixture, dict):
        issues.append(("INVALID_FIXTURE_SHAPE", "root"))
        return issues

    if fixture.get("phase") != "Phase 2":
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if fixture.get("status") != "active":
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if fixture.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if fixture.get("archive_target_scope") != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = fixture.get("cross_targets")
    if not isinstance(cross_targets, list):
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    seen_targets: set[str] = set()
    found_targets: dict[str, tuple[str, str]] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "shape"))
            continue
        target = entry.get("target")
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")
        if not all(isinstance(value, str) for value in (target, review_status, validation_mode, route)):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", json.dumps(entry, sort_keys=True)))
            continue
        if target in seen_targets:
            issues.append(("DUPLICATE_CROSS_TARGET", target))
            continue
        seen_targets.add(target)
        found_targets[target] = (review_status, validation_mode)
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))

    if set(found_targets) != set(EXPECTED_TARGETS):
        issues.append(("TARGET_SET_MISMATCH", ",".join(sorted(found_targets))))
    for target, expected_contract in EXPECTED_TARGETS.items():
        if found_targets.get(target) != expected_contract:
            issues.append(("TARGET_CONTRACT_MISMATCH", f"{target}:{found_targets.get(target)}"))

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


def build_sample_root(root: Path) -> None:
    write_text(
        resolve_path(root, REVIEW_CHECKLIST),
        "# Zigux Review Checklist\n\n"
        + "\n".join(f"- {marker}" for marker in REQUIRED_REVIEW_CHECKLIST_MARKERS)
        + "\n",
    )
    write_text(
        resolve_path(root, PHASE2_NOTES),
        "# Phase 2 Toolchain Bootstrap Notes\n\n"
        + "\n".join(f"- {marker}" for marker in REQUIRED_PHASE2_NOTES_MARKERS)
        + "\n",
    )
    write_text(
        resolve_path(root, TESTS_README),
        "# zigux/tests\n\n"
        + "\n".join(f"- {marker}" for marker in REQUIRED_TESTS_README_MARKERS)
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
                    "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                    "required_make_routes": EXPECTED_REQUIRED_ROUTES,
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
                "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                "cross_targets": [
                    {
                        "target": target,
                        "review_status": review_status,
                        "validation_mode": validation_mode,
                        "route": ROUTE,
                    }
                    for target, (review_status, validation_mode) in EXPECTED_TARGETS.items()
                ],
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_review_checklist_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        checklist_path = resolve_path(root, REVIEW_CHECKLIST)
        checklist_text = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(checklist_text.replace(REQUIRED_REVIEW_CHECKLIST_MARKERS[0], "", 1), encoding="utf-8")
        assert ("MISSING_REVIEW_CHECKLIST_MARKER", REQUIRED_REVIEW_CHECKLIST_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        notes_path = resolve_path(root, PHASE2_NOTES)
        notes_text = notes_path.read_text(encoding="utf-8")
        notes_path.write_text(notes_text.replace(REQUIRED_PHASE2_NOTES_MARKERS[0], "", 1), encoding="utf-8")
        assert ("MISSING_PHASE2_NOTES_MARKER", REQUIRED_PHASE2_NOTES_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        tests_path = resolve_path(root, TESTS_README)
        tests_text = tests_path.read_text(encoding="utf-8")
        tests_path.write_text(tests_text.replace(REQUIRED_TESTS_README_MARKERS[0], "", 1), encoding="utf-8")
        assert ("MISSING_TESTS_README_MARKER", REQUIRED_TESTS_README_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_text = makefile_path.read_text(encoding="utf-8")
            makefile_path.write_text(makefile_text.replace(marker + "\n", "", 1), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-cross"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("REQUIRED_ROUTE_SET_MISMATCH", "phase2-toolchain,phase2-cross") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("ARCHIVE_SCOPE_MISMATCH", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        fixture_path = resolve_path(root, FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["review_status"] = "pinned bootstrap archive"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("TARGET_CONTRACT_MISMATCH", "aarch64-linux:('pinned bootstrap archive', 'route_contract_only')") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        fixture_path = resolve_path(root, FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"].append(dict(fixture["cross_targets"][0]))
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("DUPLICATE_CROSS_TARGET", "x86_64-linux") in collect_issues(root)
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        raise SystemExit(
            f"self-test case count changed: expected {EXPECTED_SELF_TEST_CASE_COUNT}, got {checks_run}"
        )
    print("PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"WROTE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT=pass")
    print(
        "PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_REVIEW_CHECKLIST_MARKERS) + len(REQUIRED_PHASE2_NOTES_MARKERS) + len(REQUIRED_TESTS_README_MARKERS)}"
    )
    print("PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT_REQUIRED_PATH_COUNT=6")
    print(f"PHASE2_CROSS_REVIEW_CHECKLIST_CONTRACT_TARGET_COUNT={len(EXPECTED_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
