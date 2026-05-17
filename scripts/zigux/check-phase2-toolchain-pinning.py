#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 toolchain pinning packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
POLICY_PATH = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "check-zig-toolchain.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
    POLICY_PATH,
    BOOTSTRAP_NOTES,
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
)

README_PRESENT_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
)

README_WARNING_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/Makefile`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "historical packet members",
)

BOOTSTRAP_PRESENT_MARKERS = (
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "the `zigux/tests/fixtures/kconfig_bridge/` manifest roster",
)

BOOTSTRAP_WARNING_MARKERS = (
    "Repeated authenticated reads on current `master` still return missing for",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/Makefile`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "Treat the absent validator-first, cross-route, installer, and Linux-style make replay names as historical packet members",
)

README_FORBIDDEN_MARKERS: tuple[str, ...] = ()

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "channel_minimum_lockstep": True,
    "archive_target_scope": ["x86_64-linux"],
    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
}

EXPECTED_SELF_TEST_CASE_COUNT = 79


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def load_policy(root: Path) -> object:
    return json.loads(read_text(resolve_path(root, POLICY_PATH)))


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        payload = load_policy(root)
    except json.JSONDecodeError as exc:
        return [("INVALID_POLICY_JSON", exc.msg)]

    if not isinstance(payload, dict):
        return issues + [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]

    if payload.get("phase") != EXPECTED_POLICY["phase"]:
        issues.append(
            (
                "POLICY_PHASE_MISMATCH",
                f"actual={payload.get('phase')!r}:expected={EXPECTED_POLICY['phase']!r}",
            )
        )

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + [("INVALID_UPGRADE_POLICY", type(upgrade_policy).__name__)]

    if upgrade_policy.get("channel_minimum_lockstep") is not EXPECTED_POLICY["channel_minimum_lockstep"]:
        issues.append(
            (
                "POLICY_LOCKSTEP_MISMATCH",
                f"actual={upgrade_policy.get('channel_minimum_lockstep')!r}:expected={EXPECTED_POLICY['channel_minimum_lockstep']!r}",
            )
        )

    if upgrade_policy.get("archive_target_scope") != EXPECTED_POLICY["archive_target_scope"]:
        issues.append(
            (
                "POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH",
                f"actual={upgrade_policy.get('archive_target_scope')!r}:expected={EXPECTED_POLICY['archive_target_scope']!r}",
            )
        )

    if upgrade_policy.get("required_make_routes") != EXPECTED_POLICY["required_make_routes"]:
        issues.append(
            (
                "POLICY_REQUIRED_MAKE_ROUTES_MISMATCH",
                f"actual={upgrade_policy.get('required_make_routes')!r}:expected={EXPECTED_POLICY['required_make_routes']!r}",
            )
        )

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    readme_text = read_text(resolve_path(root, SCRIPTS_README))
    bootstrap_notes_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    issues.extend(collect_missing_markers(readme_text, README_PRESENT_MARKERS, "MISSING_README_PRESENT_MARKERS"))
    issues.extend(collect_missing_markers(readme_text, README_WARNING_MARKERS, "MISSING_README_WARNING_MARKERS"))
    issues.extend(
        collect_missing_markers(
            bootstrap_notes_text, BOOTSTRAP_PRESENT_MARKERS, "MISSING_BOOTSTRAP_PRESENT_MARKERS"
        )
    )
    issues.extend(
        collect_missing_markers(
            bootstrap_notes_text, BOOTSTRAP_WARNING_MARKERS, "MISSING_BOOTSTRAP_WARNING_MARKERS"
        )
    )
    issues.extend(collect_forbidden_markers(readme_text, README_FORBIDDEN_MARKERS, "FORBIDDEN_README_MARKERS"))

    for path in SURFACE_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))

    if resolve_path(root, POLICY_PATH).exists():
        issues.extend(collect_policy_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOLCHAIN_PINNING=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    readme_lines = [
        "# scripts/zigux",
        "",
        "## Phase 2",
        "",
        "- current packet",
        *README_PRESENT_MARKERS,
        *README_WARNING_MARKERS,
    ]
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(readme_lines) + "\n")
    bootstrap_lines = [
        "# Phase 2 Toolchain Bootstrap Notes",
        "",
        "## Current direct packet",
        "",
        *BOOTSTRAP_PRESENT_MARKERS,
        "",
        "## Current repo-reality gaps",
        "",
        *BOOTSTRAP_WARNING_MARKERS,
    ]
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(bootstrap_lines) + "\n")
    for path in SURFACE_PATHS:
        if path == POLICY_PATH:
            write_text(
                resolve_path(root, path),
                json.dumps(
                    {
                        "phase": EXPECTED_POLICY["phase"],
                        "channel": "0.17.0-dev.87+9b177a7d2",
                        "minimum_version": "0.17.0-dev.87+9b177a7d2",
                        "archive_sha256": {"x86_64-linux": "3" * 64},
                        "upgrade_policy": {
                            "channel_minimum_lockstep": EXPECTED_POLICY["channel_minimum_lockstep"],
                            "archive_target_scope": EXPECTED_POLICY["archive_target_scope"],
                            "required_make_routes": EXPECTED_POLICY["required_make_routes"],
                        },
                    },
                    indent=2,
                )
                + "\n",
            )
        elif path == BOOTSTRAP_NOTES:
            continue
        else:
            write_text(resolve_path(root, path), "present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


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
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_pinning_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_HOOKS", marker) in issues
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count=2") in issues
            checks_run += 1

        for marker in README_PRESENT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_README_PRESENT_MARKERS", marker) in issues
            checks_run += 1

        for marker in README_WARNING_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_README_WARNING_MARKERS", marker) in issues
            checks_run += 1

        for marker in BOOTSTRAP_PRESENT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_BOOTSTRAP_PRESENT_MARKERS", marker) in issues
            checks_run += 1

        for marker in BOOTSTRAP_WARNING_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_BOOTSTRAP_WARNING_MARKERS", marker) in issues
            checks_run += 1

        for marker in README_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_README_MARKERS", marker) in issues
            checks_run += 1

        for primary_path in (WORKFLOW, SCRIPTS_README, BOOTSTRAP_NOTES):
            build_self_test_root(root)
            resolve_path(root, primary_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                assert str(resolve_path(root, primary_path)) in str(exc)
            else:
                raise AssertionError("missing primary surface did not abort")
            checks_run += 1

        for rel_path in SURFACE_PATHS:
            if rel_path == BOOTSTRAP_NOTES:
                continue
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            issues = collect_issues(root)
            assert ("MISSING_SURFACE_PATHS", rel_path.relative_to(ROOT).as_posix()) in issues
            checks_run += 1

        policy_mutations = (
            ("phase", "Phase 3", "POLICY_PHASE_MISMATCH"),
            ("lockstep", False, "POLICY_LOCKSTEP_MISMATCH"),
            ("archive_target_scope", ["aarch64-linux"], "POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH"),
            ("required_make_routes", ["phase2-toolchain"], "POLICY_REQUIRED_MAKE_ROUTES_MISMATCH"),
        )
        for field_name, replacement, expected_code in policy_mutations:
            build_self_test_root(root)
            path = resolve_path(root, POLICY_PATH)
            payload = json.loads(path.read_text(encoding="utf-8"))
            if field_name == "phase":
                payload["phase"] = replacement
            elif field_name == "lockstep":
                payload["upgrade_policy"]["channel_minimum_lockstep"] = replacement
            else:
                payload["upgrade_policy"][field_name] = replacement
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert any(issue[0] == expected_code for issue in issues)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, POLICY_PATH)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"] = "broken"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_UPGRADE_POLICY", "str") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, POLICY_PATH)
        path.write_text("{not-json}\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(issue[0] == "INVALID_POLICY_JSON" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, POLICY_PATH)
        path.write_text("[]\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_POLICY_PAYLOAD", "list") in issues
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_PINNING_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current directly readable Phase 2 toolchain pinning packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_PINNING=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_WORKFLOW_HOOK_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_TOOLCHAIN_PINNING_SURFACE_PATH_COUNT={len(SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
