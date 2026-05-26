#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CLOSURE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
INSTALL_ZIG = ROOT / "scripts" / "zigux" / "install-zig.py"
CROSS_CHECK = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
CROSS_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
MAKEFILE = ROOT / "zigux" / "Makefile"
CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

CLOSURE_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "returned installer and cross-route companions",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`make -C zigux phase2-cross`",
)

TESTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target",
)

INSTALL_ZIG_MARKERS = (
    "TOOLCHAIN_POLICY = ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json'",
    "FALLBACK_CHANNEL = 'master'",
    "def load_policy_channel(",
)

CROSS_CHECK_MARKERS = (
    'ROUTE = "make -C zigux phase2-cross"',
    'EXPECTED_FIXTURE_PHASE = "Phase 2"',
    'EXPECTED_FIXTURE_STATUS = "active"',
    'ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")',
)

CROSS_ALIGNMENT_MARKERS = (
    'ROUTE = "make -C zigux phase2-cross"',
    'SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")',
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again,",
)

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

EXPECTED_POLICY_PHASE = "Phase 2"
EXPECTED_POLICY_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_SCOPE = ["x86_64-linux"]
EXPECTED_REQUIRED_ROUTE = "phase2-cross"
EXPECTED_FIXTURE_ROUTE = "make -C zigux phase2-cross"
EXPECTED_CROSS_TARGETS = {
    "x86_64-linux": "archive_required",
    "aarch64-linux": "route_contract_only",
}


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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


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


def collect_policy_issues(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_SHAPE", type(payload).__name__)]

    if payload.get("phase") != EXPECTED_POLICY_PHASE:
        issues.append(("INVALID_POLICY_FIELD", "phase"))
    if payload.get("channel") != EXPECTED_POLICY_CHANNEL:
        issues.append(("INVALID_POLICY_FIELD", "channel"))
    if payload.get("minimum_version") != EXPECTED_POLICY_CHANNEL:
        issues.append(("INVALID_POLICY_FIELD", "minimum_version"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or list(archive_sha256.keys()) != EXPECTED_SCOPE:
        issues.append(("INVALID_POLICY_FIELD", "archive_sha256"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
        return issues

    if upgrade_policy.get("archive_target_scope") != EXPECTED_SCOPE:
        issues.append(("INVALID_POLICY_FIELD", "archive_target_scope"))
    required_routes = upgrade_policy.get("required_make_routes")
    if not isinstance(required_routes, list) or EXPECTED_REQUIRED_ROUTE not in required_routes:
        issues.append(("INVALID_POLICY_FIELD", "required_make_routes"))
    return issues


def collect_cross_target_issues(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_CROSS_TARGET_FIXTURE", type(payload).__name__)]

    if payload.get("phase") != EXPECTED_POLICY_PHASE:
        issues.append(("INVALID_CROSS_TARGET_FIELD", "phase"))
    if payload.get("status") != "active":
        issues.append(("INVALID_CROSS_TARGET_FIELD", "status"))
    if payload.get("route") != EXPECTED_FIXTURE_ROUTE:
        issues.append(("INVALID_CROSS_TARGET_FIELD", "route"))
    if payload.get("archive_target_scope") != EXPECTED_SCOPE:
        issues.append(("INVALID_CROSS_TARGET_FIELD", "archive_target_scope"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_CROSS_TARGET_FIELD", "cross_targets"))
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
        if route != EXPECTED_FIXTURE_ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if not isinstance(validation_mode, str) or not validation_mode:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        if target in actual_modes:
            issues.append(("DUPLICATE_CROSS_TARGET_ENTRY", target))
        actual_modes[target] = validation_mode

    if actual_modes != EXPECTED_CROSS_TARGETS:
        issues.append(("INVALID_CROSS_TARGET_MATRIX", json.dumps(actual_modes, sort_keys=True)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, CLOSURE_NOTE)),
            CLOSURE_MARKERS,
            "MISSING_CLOSURE_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TESTS_README)),
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, INSTALL_ZIG)),
            INSTALL_ZIG_MARKERS,
            "MISSING_INSTALLER_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, CROSS_CHECK)),
            CROSS_CHECK_MARKERS,
            "MISSING_CROSS_CHECK_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, CROSS_ALIGNMENT)),
            CROSS_ALIGNMENT_MARKERS,
            "MISSING_CROSS_ALIGNMENT_MARKERS",
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
    issues.extend(collect_policy_issues(read_json(resolve_path(root, TOOLCHAIN_POLICY))))
    issues.extend(collect_cross_target_issues(read_json(resolve_path(root, CROSS_TARGETS))))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CLOSURE_INSTALLER_CROSS_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, CLOSURE_NOTE), "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, INSTALL_ZIG), "\n".join(INSTALL_ZIG_MARKERS) + "\n")
    write_text(resolve_path(root, CROSS_CHECK), "\n".join(CROSS_CHECK_MARKERS) + "\n")
    write_text(resolve_path(root, CROSS_ALIGNMENT), "\n".join(CROSS_ALIGNMENT_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": EXPECTED_POLICY_PHASE,
                "channel": EXPECTED_POLICY_CHANNEL,
                "minimum_version": EXPECTED_POLICY_CHANNEL,
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_SCOPE,
                    "required_make_routes": [
                        "phase2-toolchain",
                        "phase2-tools",
                        "phase2-kconfig",
                        "phase2-cross",
                        "phase2-genksyms",
                        "phase2-fixdep",
                        "phase2-validate",
                    ],
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
                "phase": EXPECTED_POLICY_PHASE,
                "status": "active",
                "route": EXPECTED_FIXTURE_ROUTE,
                "archive_target_scope": EXPECTED_SCOPE,
                "cross_targets": [
                    {
                        "target": "x86_64-linux",
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": EXPECTED_FIXTURE_ROUTE,
                    },
                    {
                        "target": "aarch64-linux",
                        "review_status": "route contract only",
                        "validation_mode": "route_contract_only",
                        "route": EXPECTED_FIXTURE_ROUTE,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def remove_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_installer_cross_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        text_marker_sets = (
            (CLOSURE_NOTE, CLOSURE_MARKERS, "MISSING_CLOSURE_MARKERS"),
            (TESTS_README, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"),
            (INSTALL_ZIG, INSTALL_ZIG_MARKERS, "MISSING_INSTALLER_MARKERS"),
            (CROSS_CHECK, CROSS_CHECK_MARKERS, "MISSING_CROSS_CHECK_MARKERS"),
            (CROSS_ALIGNMENT, CROSS_ALIGNMENT_MARKERS, "MISSING_CROSS_ALIGNMENT_MARKERS"),
        )
        for rel_path, markers, code in text_marker_sets:
            for marker in markers:
                build_sample_root(root)
                path = resolve_path(root, rel_path)
                path.write_text(remove_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
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
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_FIELD", "required_make_routes") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        fixture_path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["validation_mode"] = "archive_required"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_CROSS_TARGET_MATRIX" for code, _ in collect_issues(root))
        checks_run += 1

        build_sample_root(root)
        fixture_path = resolve_path(root, CROSS_TARGETS)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["route"] = "make -C zigux phase2-tools"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ROUTE", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        resolve_path(root, CLOSURE_NOTE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing closure note did not abort")

    print("PHASE2_CLOSURE_INSTALLER_CROSS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_INSTALLER_CROSS_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the closure-side Phase 2 installer and direct-cross reminder packet aligned to current repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for focused replay and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_CLOSURE_INSTALLER_CROSS_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_INSTALLER_CROSS_PACKET=pass")
    print("PHASE2_CLOSURE_INSTALLER_CROSS_PACKET_REQUIRED_PATH_COUNT=8")
    print(
        "PHASE2_CLOSURE_INSTALLER_CROSS_PACKET_MARKER_COUNT="
        f"{len(CLOSURE_MARKERS) + len(TESTS_README_MARKERS) + len(INSTALL_ZIG_MARKERS) + len(CROSS_CHECK_MARKERS) + len(CROSS_ALIGNMENT_MARKERS) + len(MAKEFILE_LINES)}"
    )
    print("PHASE2_CLOSURE_INSTALLER_CROSS_PACKET_CROSS_TARGET_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
