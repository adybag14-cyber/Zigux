#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 toolchain pinning packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
POLICY_PATH = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TOOL_MANIFEST_PATH = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "check-zig-toolchain.py",
    ROOT / "scripts" / "zigux" / "install-zig.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py",
    ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-required-make-routes.py",
    ROOT / "scripts" / "zigux" / "check-phase2-docs-shared-reminder.py",
    ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py",
    ROOT / "scripts" / "zigux" / "validate-phase2.py",
    ROOT / "scripts" / "zigux" / "validate-phase2-closure.py",
    ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
    ROOT / "scripts" / "zigux" / "genksyms.zig",
    ROOT / "zigux" / "Makefile",
    POLICY_PATH,
    BOOTSTRAP_NOTES,
    PHASE2_CLOSURE,
    REVIEW_CHECKLIST,
    TESTS_README,
    TOOL_MANIFEST_PATH,
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "help_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "minimal_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "debug_reference_types_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "long_options_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "quiet_overrides_warning_expected.json",
)

WORKFLOW_SETUP_MARKERS = (
    "- name: Setup pinned Zig toolchain",
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'mirror_file=".zig-toolchain/community-mirrors.txt"',
    'if curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
    "echo 'failed to install a verified pinned Zig archive from mirrors or ziglang.org' >&2",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: python3 scripts/zigux/validate-phase2.py",
)

BOOTSTRAP_PRESENT_MARKERS = (
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "the `zigux/tests/fixtures/kconfig_bridge/` manifest roster",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

BOOTSTRAP_GAP_MARKERS = (
    "No current repo-reality gaps remain inside the bounded toolchain, installer, and direct cross-route packet on current `master`.",
    "Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer or direct cross-route surfaces from the current packet.",
)

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "channel_minimum_lockstep": True,
    "archive_target_scope": ["x86_64-linux"],
    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
}

EXPECTED_TOOL_MANIFEST = {
    "phase": "Phase 2",
    "status": "active",
    "scope": "current directly readable scripts-root toolchain, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, and tranche-closure reminder packet",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
    "present_surfaces": {
        "review_surfaces": [
            "Documentation/zigux/README.md",
            "Documentation/zigux/phase2-closure.md",
            "Documentation/zigux/review-checklist.md",
            "zigux/tests/README.md",
        ],
        "closure_notes": [
            "Documentation/zigux/phase2-closure.md",
            "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        ],
        "checkers": [
            "scripts/zigux/check-zig-toolchain.py",
            "scripts/zigux/check-kconfig-bridge.py",
            "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
            "scripts/zigux/check-phase2-kbuild-routes.py",
            "scripts/zigux/check-phase2-tests-readme-alignment.py",
            "scripts/zigux/check-phase2-cross.py",
            "scripts/zigux/check-phase2-cross-selftest-alignment.py",
            "scripts/zigux/check-phase2-toolchain-pinning.py",
            "scripts/zigux/check-phase2-toolchain-pin-scope.py",
            "scripts/zigux/check-phase2-required-make-routes.py",
            "scripts/zigux/check-phase2-docs-shared-reminder.py",
            "scripts/zigux/check-genksyms-bridge.py",
        ],
        "bootstrap_helpers": [
            "scripts/zigux/install-zig.py",
        ],
        "bridge_helpers": [
            "scripts/zigux/kconfig/conf_bridge.zig",
            "scripts/zigux/kconfig/confdata_bridge.zig",
            "scripts/zigux/genksyms.zig",
        ],
        "policy": [
            "scripts/zigux/zig-toolchain-policy.json",
        ],
        "make_wrappers": [
            "zigux/Makefile",
            "make -C zigux phase2-toolchain",
            "make -C zigux phase2-tools",
            "make -C zigux phase2-kconfig",
            "make -C zigux phase2-cross",
            "make -C zigux phase2-genksyms",
            "make -C zigux phase2-validate",
            "make -C zigux phase2",
        ],
        "cross_route_support": [
            "scripts/zigux/check-phase2-cross.py",
            "zigux/tests/fixtures/phase2_cross_targets.json",
        ],
        "artifact_support": [
            "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
        ],
        "fixture_roster": [
            "zigux/tests/fixtures/kconfig_bridge/cases.json",
            "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
            "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
            "zigux/tests/fixtures/genksyms_bridge/cases.json",
            "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
            "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
            "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
            "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
            "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
        ],
    },
    "repo_reality_gaps": [],
    "notes": [
        "Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, returned installer helper, direct cross-route checker, docs-shared-reminder checker, required make-route guard, kbuild routes checker, the live kconfig bridge checker and fixture roster, the bounded genksyms bridge checker and fixture packet, cross-selftest checker, and the restored tranche-closure note.",
        "Keep scripts/zigux/validate-phase2-closure.py out of the repo-reality-gap list because the closure validator is directly readable on current master and the closure-side packet depends on it as a live validation surface.",
        "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
        "Keep the fixture-backed artifact-diff support packet explicit through zigux/tests/fixtures/phase2_artifact_tools_manifest.json instead of treating it as a repo-reality gap.",
        "Keep the returned installer helper, direct cross-route checker, phase2_cross_targets fixture, and bounded genksyms fixture packet explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
    ],
}

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_SETUP_MARKERS)
    + len(WORKFLOW_LINES)
    + len(WORKFLOW_LINES)
    + len(BOOTSTRAP_PRESENT_MARKERS)
    + len(BOOTSTRAP_GAP_MARKERS)
    + 2
    + (len(SURFACE_PATHS) - 1)
    + 4
    + 1
    + 1
    + 1
    + 4
    + 1
    + 1
    + 1
    + 1
    + 1
    + 1
)


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


def extract_markdown_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    start = text.find("\n", start)
    if start == -1:
        return ""
    start += 1
    end = text.find("\n## ", start)
    if end == -1:
        end = len(text)
    return text[start:end]


def load_policy(root: Path) -> object:
    return json.loads(read_text(resolve_path(root, POLICY_PATH)))


def load_tool_manifest(root: Path) -> object:
    return json.loads(read_text(resolve_path(root, TOOL_MANIFEST_PATH)))


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        payload = load_policy(root)
    except json.JSONDecodeError as exc:
        return [("INVALID_POLICY_JSON", exc.msg)]

    if not isinstance(payload, dict):
        return issues + [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]

    if payload.get("phase") != EXPECTED_POLICY["phase"]:
        issues.append(("POLICY_PHASE_MISMATCH", f"actual={payload.get('phase')!r}:expected={EXPECTED_POLICY['phase']!r}"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + [("INVALID_UPGRADE_POLICY", type(upgrade_policy).__name__)]

    if upgrade_policy.get("channel_minimum_lockstep") is not EXPECTED_POLICY["channel_minimum_lockstep"]:
        issues.append(("POLICY_LOCKSTEP_MISMATCH", f"actual={upgrade_policy.get('channel_minimum_lockstep')!r}:expected={EXPECTED_POLICY['channel_minimum_lockstep']!r}"))

    if upgrade_policy.get("archive_target_scope") != EXPECTED_POLICY["archive_target_scope"]:
        issues.append(("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", f"actual={upgrade_policy.get('archive_target_scope')!r}:expected={EXPECTED_POLICY['archive_target_scope']!r}"))

    if upgrade_policy.get("required_make_routes") != EXPECTED_POLICY["required_make_routes"]:
        issues.append(("POLICY_REQUIRED_MAKE_ROUTES_MISMATCH", f"actual={upgrade_policy.get('required_make_routes')!r}:expected={EXPECTED_POLICY['required_make_routes']!r}"))

    return issues


def collect_tool_manifest_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        payload = load_tool_manifest(root)
    except json.JSONDecodeError as exc:
        return [("INVALID_TOOL_MANIFEST_JSON", exc.msg)]

    if not isinstance(payload, dict):
        return [("INVALID_TOOL_MANIFEST_PAYLOAD", type(payload).__name__)]

    for key in ("phase", "status", "scope", "workflow"):
        if payload.get(key) != EXPECTED_TOOL_MANIFEST[key]:
            issues.append(("TOOL_MANIFEST_FIELD_MISMATCH", f"{key}:actual={payload.get(key)!r}:expected={EXPECTED_TOOL_MANIFEST[key]!r}"))

    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        return issues + [("INVALID_TOOL_MANIFEST_PRESENT_SURFACES", type(present_surfaces).__name__)]

    expected_present_surfaces = EXPECTED_TOOL_MANIFEST["present_surfaces"]
    for key, expected_value in expected_present_surfaces.items():
        if present_surfaces.get(key) != expected_value:
            issues.append(("TOOL_MANIFEST_PRESENT_SURFACES_MISMATCH", f"{key}:actual={present_surfaces.get(key)!r}:expected={expected_value!r}"))

    if payload.get("repo_reality_gaps") != EXPECTED_TOOL_MANIFEST["repo_reality_gaps"]:
        issues.append(("TOOL_MANIFEST_REPO_GAPS_MISMATCH", f"actual={payload.get('repo_reality_gaps')!r}:expected={EXPECTED_TOOL_MANIFEST['repo_reality_gaps']!r}"))

    if payload.get("notes") != EXPECTED_TOOL_MANIFEST["notes"]:
        issues.append(("TOOL_MANIFEST_NOTES_MISMATCH", f"actual={payload.get('notes')!r}:expected={EXPECTED_TOOL_MANIFEST['notes']!r}"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    bootstrap_notes_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    bootstrap_present_text = extract_markdown_section(bootstrap_notes_text, "## Current direct packet")
    bootstrap_gap_text = extract_markdown_section(bootstrap_notes_text, "## Current repo-reality gaps")

    issues.extend(collect_missing_markers(workflow_text, WORKFLOW_SETUP_MARKERS, "MISSING_WORKFLOW_SETUP_MARKERS"))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    issues.extend(collect_missing_markers(bootstrap_present_text, BOOTSTRAP_PRESENT_MARKERS, "MISSING_BOOTSTRAP_PRESENT_MARKERS"))
    issues.extend(collect_missing_markers(bootstrap_gap_text, BOOTSTRAP_GAP_MARKERS, "MISSING_BOOTSTRAP_GAP_MARKERS"))

    for path in SURFACE_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))

    if resolve_path(root, POLICY_PATH).exists():
        issues.extend(collect_policy_issues(root))
    if resolve_path(root, TOOL_MANIFEST_PATH).exists():
        issues.extend(collect_tool_manifest_issues(root))
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
    write_text(resolve_path(root, WORKFLOW), "\n".join((*WORKFLOW_SETUP_MARKERS, *WORKFLOW_LINES)) + "\n")
    bootstrap_lines = [
        "# Phase 2 Toolchain Bootstrap Notes",
        "",
        "## Current direct packet",
        "",
        *BOOTSTRAP_PRESENT_MARKERS,
        "",
        "## Current repo-reality gaps",
        "",
        *BOOTSTRAP_GAP_MARKERS,
    ]
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(bootstrap_lines) + "\n")
    for path in SURFACE_PATHS:
        if path == POLICY_PATH:
            write_text(resolve_path(root, path), json.dumps({"phase": EXPECTED_POLICY["phase"], "channel": "0.17.0-dev.87+9b177a7d2", "minimum_version": "0.17.0-dev.87+9b177a7d2", "archive_sha256": {"x86_64-linux": "3" * 64}, "upgrade_policy": {"channel_minimum_lockstep": EXPECTED_POLICY["channel_minimum_lockstep"], "archive_target_scope": EXPECTED_POLICY["archive_target_scope"], "required_make_routes": EXPECTED_POLICY["required_make_routes"]}}, indent=2) + "\n")
        elif path == TOOL_MANIFEST_PATH:
            write_text(resolve_path(root, path), json.dumps(EXPECTED_TOOL_MANIFEST, indent=2) + "\n")
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


def mutate_json(path: Path, mutator) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_pinning_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_SETUP_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_SETUP_MARKERS", marker) in issues
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"), encoding="utf-8")
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

        for marker in BOOTSTRAP_PRESENT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_BOOTSTRAP_PRESENT_MARKERS", marker) in issues
            checks_run += 1

        for marker in BOOTSTRAP_GAP_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_BOOTSTRAP_GAP_MARKERS", marker) in issues
            checks_run += 1

        for primary_path in (WORKFLOW, BOOTSTRAP_NOTES):
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

        policy_mutations = (("phase", "Phase 3", "POLICY_PHASE_MISMATCH"), ("lockstep", False, "POLICY_LOCKSTEP_MISMATCH"), ("archive_target_scope", ["aarch64-linux"], "POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH"), ("required_make_routes", ["phase2-toolchain"], "POLICY_REQUIRED_MAKE_ROUTES_MISMATCH"))
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
        path.write_text("{\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(issue[0] == "INVALID_POLICY_JSON" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, POLICY_PATH)
        path.write_text("[]\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_POLICY_PAYLOAD", "list") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, POLICY_PATH)
        mutate_json(path, lambda payload: payload.__setitem__("upgrade_policy", []))
        issues = collect_issues(root)
        assert ("INVALID_UPGRADE_POLICY", "list") in issues
        checks_run += 1

        for key in ("phase", "status", "scope", "workflow"):
            build_self_test_root(root)
            path = resolve_path(root, TOOL_MANIFEST_PATH)
            mutate_json(path, lambda payload, key=key: payload.__setitem__(key, "broken"))
            issues = collect_issues(root)
            assert any(issue[0] == "TOOL_MANIFEST_FIELD_MISMATCH" and issue[1].startswith(f"{key}:") for issue in issues)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOL_MANIFEST_PATH)
        mutate_json(path, lambda payload: payload.__setitem__("present_surfaces", []))
        issues = collect_issues(root)
        assert ("INVALID_TOOL_MANIFEST_PRESENT_SURFACES", "list") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOL_MANIFEST_PATH)
        mutate_json(path, lambda payload: payload["present_surfaces"].__setitem__("checkers", []))
        issues = collect_issues(root)
        assert any(issue[0] == "TOOL_MANIFEST_PRESENT_SURFACES_MISMATCH" and issue[1].startswith("checkers:") for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOL_MANIFEST_PATH)
        mutate_json(path, lambda payload: payload.__setitem__("repo_reality_gaps", ["gap"]))
        issues = collect_issues(root)
        assert any(issue[0] == "TOOL_MANIFEST_REPO_GAPS_MISMATCH" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOL_MANIFEST_PATH)
        mutate_json(path, lambda payload: payload.__setitem__("notes", []))
        issues = collect_issues(root)
        assert any(issue[0] == "TOOL_MANIFEST_NOTES_MISMATCH" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOL_MANIFEST_PATH)
        path.write_text("{\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(issue[0] == "INVALID_TOOL_MANIFEST_JSON" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOL_MANIFEST_PATH)
        path.write_text("[]\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_TOOL_MANIFEST_PAYLOAD", "list") in issues
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_PINNING_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current directly readable Phase 2 toolchain pinning packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)
    print("PHASE2_TOOLCHAIN_PINNING=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_REQUIRED_MARKER_COUNT={len(BOOTSTRAP_PRESENT_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_PINNING_GAP_MARKER_COUNT={len(BOOTSTRAP_GAP_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
