#!/usr/bin/env python3
"""Keep the scripts-root Phase 2 cross reminder aligned with the live packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
DIRECT_CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

ROUTE = "make -C zigux phase2-cross"
SUPPORTED_TARGETS = ("x86_64-linux", "aarch64-linux")
EXPECTED_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/install-zig.py` is directly readable on current `master`",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "`make -C zigux phase2-cross`",
)

REVIEW_CHECKLIST_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

TESTS_README_MARKERS = (
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, kconfig bridge checker, genksyms bridge, and fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, kconfig bridge, genksyms bridge, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
)

DIRECT_CROSS_MARKERS = (
    'EXPECTED_SELF_TEST_CASE_COUNT = 17',
    'ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")',
    'print("PHASE2_DIRECT_CROSS_ROUTE=pass")',
)

ALIGNMENT_MARKERS = (
    'SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")',
    'SCRIPTS_README_MARKERS = (',
    'print("PHASE2_CROSS_ALIGNMENT=pass")',
)

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

FORBIDDEN_SCRIPTS_README_MARKERS = (
    "still return missing for `scripts/zigux/install-zig.py`",
    "`aarch64-linux-musl`",
    "`riscv64-linux-musl`",
)


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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


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


def load_expected_fixture(root: Path) -> dict[str, object]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):
        raise SystemExit(f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")

    normalized_scope: list[str] = []
    for value in archive_target_scope:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        target = value.strip()
        if target not in SUPPORTED_TARGETS:
            raise SystemExit(f"unsupported archive_target_scope target in required file: {target}")
        if target in normalized_scope:
            raise SystemExit(f"duplicate archive_target_scope target in required file: {target}")
        normalized_scope.append(target)

    expected_modes = {
        target: ("archive_required" if target in normalized_scope else "route_contract_only")
        for target in SUPPORTED_TARGETS
    }
    return {
        "phase": "Phase 2",
        "status": "active",
        "route": ROUTE,
        "archive_target_scope": normalized_scope,
        "cross_targets": expected_modes,
    }


def collect_fixture_issues(payload: object, root: Path) -> list[tuple[str, str]]:
    expected = load_expected_fixture(root)
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_CROSS_TARGET_FIXTURE", type(payload).__name__)]
    if payload.get("phase") != expected["phase"]:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "phase"))
    if payload.get("status") != expected["status"]:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "status"))
    if payload.get("route") != expected["route"]:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "route"))
    if payload.get("archive_target_scope") != expected["archive_target_scope"]:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "cross_targets"))
        return issues

    actual_modes: dict[str, str] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")
        if not isinstance(target, str) or not target:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        if not isinstance(validation_mode, str) or not validation_mode:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        if route != expected["route"]:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if target in actual_modes:
            issues.append(("DUPLICATE_CROSS_TARGET_ENTRY", target))
        actual_modes[target] = validation_mode

    if actual_modes != expected["cross_targets"]:
        issues.append(("INVALID_CROSS_TARGET_MATRIX", json.dumps(actual_modes, sort_keys=True)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    root = root.resolve()
    issues: list[tuple[str, str]] = []

    scripts_text = read_text(resolve_path(root, SCRIPTS_README))
    issues.extend(collect_missing_markers(scripts_text, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKER"))
    issues.extend(
        collect_forbidden_markers(
            scripts_text,
            FORBIDDEN_SCRIPTS_README_MARKERS,
            "FORBIDDEN_SCRIPTS_README_MARKER",
        )
    )

    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, PHASE2_NOTES)),
            PHASE2_NOTES_MARKERS,
            "MISSING_PHASE2_NOTES_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, REVIEW_CHECKLIST)),
            REVIEW_CHECKLIST_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TESTS_README)),
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, DIRECT_CROSS_CHECKER)),
            DIRECT_CROSS_MARKERS,
            "MISSING_DIRECT_CROSS_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, ALIGNMENT_CHECKER)),
            ALIGNMENT_MARKERS,
            "MISSING_ALIGNMENT_MARKER",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, MAKEFILE)),
            MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINE",
            "DUPLICATE_MAKEFILE_LINE",
        )
    )
    issues.extend(collect_fixture_issues(read_json(resolve_path(root, CROSS_TARGETS)), root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_SCRIPTS_README_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, DIRECT_CROSS_CHECKER), "\n".join(DIRECT_CROSS_MARKERS) + "\n")
    write_text(resolve_path(root, ALIGNMENT_CHECKER), "\n".join(ALIGNMENT_MARKERS) + "\n")
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
                    "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, CROSS_TARGETS),
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
    expected_case_count = 43
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_scripts_readme_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in SCRIPTS_README_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_SCRIPTS_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in FORBIDDEN_SCRIPTS_README_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("FORBIDDEN_SCRIPTS_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for path_ref, markers, code in (
            (PHASE2_NOTES, PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKER"),
            (REVIEW_CHECKLIST, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKER"),
            (TESTS_README, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKER"),
            (DIRECT_CROSS_CHECKER, DIRECT_CROSS_MARKERS, "MISSING_DIRECT_CROSS_MARKER"),
            (ALIGNMENT_CHECKER, ALIGNMENT_MARKERS, "MISSING_ALIGNMENT_MARKER"),
        ):
            for marker in markers:
                build_sample_root(root)
                path = resolve_path(root, path_ref)
                path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                assert (code, marker) in collect_issues(root)
                checks_run += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["validation_mode"] = "archive_required"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_CROSS_TARGET_MATRIX" for code, _ in collect_issues(root))
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["route"] = "make -C zigux phase2-toolchain"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ROUTE", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        payload["archive_sha256"] = {"aarch64-linux": "3" * 64}
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        fixture_path = resolve_path(root, CROSS_TARGETS)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        fixture["cross_targets"][0]["validation_mode"] = "route_contract_only"
        fixture["cross_targets"][1]["validation_mode"] = "archive_required"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["riscv64-linux"]
        payload["archive_sha256"] = {"riscv64-linux": "3" * 64}
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "unsupported archive_target_scope target" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("unsupported archive target did not abort")

        build_sample_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-cross", "phase2-validate"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid required_make_routes" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid required routes did not abort")

        build_sample_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = "broken"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid required_make_routes" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid required routes shape did not abort")

        build_sample_root(root)
        resolve_path(root, SCRIPTS_README).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing scripts readme did not abort")

        build_sample_root(root)
        path = resolve_path(root, CROSS_TARGETS)
        path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid fixture json did not abort")

        build_sample_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid policy json did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_CROSS_SCRIPTS_README_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_SCRIPTS_README_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the scripts-root Phase 2 cross reminder stays aligned with the live packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a sample current-like repository root for replay validation",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    expected = load_expected_fixture(args.root.resolve())
    print("PHASE2_CROSS_SCRIPTS_README_CONTRACT=pass")
    print(
        "PHASE2_CROSS_SCRIPTS_README_CONTRACT_MARKER_COUNT="
        f"{len(SCRIPTS_README_MARKERS) + len(PHASE2_NOTES_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(TESTS_README_MARKERS) + len(DIRECT_CROSS_MARKERS) + len(ALIGNMENT_MARKERS) + len(MAKEFILE_LINES)}"
    )
    print(
        "PHASE2_CROSS_SCRIPTS_README_CONTRACT_FORBIDDEN_MARKER_COUNT="
        f"{len(FORBIDDEN_SCRIPTS_README_MARKERS)}"
    )
    print(
        "PHASE2_CROSS_SCRIPTS_README_CONTRACT_ARCHIVE_SCOPE_COUNT="
        f"{len(expected['archive_target_scope'])}"
    )
    print(
        "PHASE2_CROSS_SCRIPTS_README_CONTRACT_TARGET_COUNT="
        f"{len(expected['cross_targets'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
