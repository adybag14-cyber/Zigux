#!/usr/bin/env python3
"""Validate the current machine-readable Phase 2 tooling packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "active"
EXPECTED_SCOPE = "current directly readable scripts-root kbuild, toolchain, and kconfig reminder packet"
EXPECTED_WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
EXPECTED_PRESENT_GROUPS = ("review_surfaces", "checkers", "bridge_helpers", "policy", "fixture_roster")
EXPECTED_GAPS = (
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)
EXPECTED_NOTES = (
    "Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, kbuild routes checker, and kconfig bridge fixture roster.",
    "Do not treat missing closure-side, cross-route, or artifact-tools packet members as directly readable current-master evidence until they are republished.",
)
REQUIRED_CHECKER = "scripts/zigux/check-zig-toolchain.py"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, rel_path: str) -> Path:
    return root / rel_path


def load_manifest(root: Path) -> dict[str, object]:
    manifest_path = resolve_path(root, MANIFEST.relative_to(ROOT).as_posix())
    try:
        payload = json.loads(read_text(manifest_path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {manifest_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid manifest payload in {manifest_path}: expected object")
    return payload


def require_string(value: object, field_name: str) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return f"{field_name}:expected non-empty string"
    return None


def require_string_list(value: object, field_name: str) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    if not isinstance(value, list) or not value:
        return [], [f"{field_name}:expected non-empty list"]
    normalized: list[str] = []
    seen: set[str] = set()
    for entry in value:
        if not isinstance(entry, str) or not entry.strip():
            issues.append(f"{field_name}:contains non-string entry")
            continue
        stripped = entry.strip()
        if stripped in seen:
            issues.append(f"{field_name}:duplicate entry:{stripped}")
            continue
        normalized.append(stripped)
        seen.add(stripped)
    return normalized, issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = load_manifest(root)

    phase_issue = require_string(payload.get("phase"), "phase")
    if phase_issue is not None:
        issues.append(("INVALID_FIELD", phase_issue))
    elif payload["phase"] != EXPECTED_PHASE:
        issues.append(("UNEXPECTED_FIELD_VALUE", f"phase:{payload['phase']}"))

    status_issue = require_string(payload.get("status"), "status")
    if status_issue is not None:
        issues.append(("INVALID_FIELD", status_issue))
    elif payload["status"] != EXPECTED_STATUS:
        issues.append(("UNEXPECTED_FIELD_VALUE", f"status:{payload['status']}"))

    scope_issue = require_string(payload.get("scope"), "scope")
    if scope_issue is not None:
        issues.append(("INVALID_FIELD", scope_issue))
    elif payload["scope"] != EXPECTED_SCOPE:
        issues.append(("UNEXPECTED_FIELD_VALUE", f"scope:{payload['scope']}"))

    workflow_issue = require_string(payload.get("workflow"), "workflow")
    if workflow_issue is not None:
        issues.append(("INVALID_FIELD", workflow_issue))
    else:
        workflow_value = str(payload["workflow"])
        if workflow_value != EXPECTED_WORKFLOW:
            issues.append(("UNEXPECTED_FIELD_VALUE", f"workflow:{workflow_value}"))
        elif not resolve_path(root, workflow_value).exists():
            issues.append(("MISSING_WORKFLOW_PATH", workflow_value))

    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_FIELD", "present_surfaces:expected object"))
    else:
        for group in EXPECTED_PRESENT_GROUPS:
            values, value_issues = require_string_list(present_surfaces.get(group), f"present_surfaces.{group}")
            issues.extend(("INVALID_FIELD", item) for item in value_issues)
            for rel_path in values:
                if not resolve_path(root, rel_path).exists():
                    issues.append(("MISSING_PRESENT_SURFACE", rel_path))
            if group == "checkers" and REQUIRED_CHECKER not in values:
                issues.append(("MISSING_REQUIRED_CHECKER", REQUIRED_CHECKER))

        unexpected_groups = sorted(set(present_surfaces) - set(EXPECTED_PRESENT_GROUPS))
        for group in unexpected_groups:
            issues.append(("UNEXPECTED_PRESENT_GROUP", group))

    gaps, gap_issues = require_string_list(payload.get("repo_reality_gaps"), "repo_reality_gaps")
    issues.extend(("INVALID_FIELD", item) for item in gap_issues)
    if tuple(gaps) != EXPECTED_GAPS:
        issues.append(("UNEXPECTED_GAP_SET", ",".join(gaps)))
    for rel_path in gaps:
        if resolve_path(root, rel_path).exists():
            issues.append(("PRESENT_REPO_REALITY_GAP", rel_path))

    notes, note_issues = require_string_list(payload.get("notes"), "notes")
    issues.extend(("INVALID_FIELD", item) for item in note_issues)
    if tuple(notes) != EXPECTED_NOTES:
        issues.append(("UNEXPECTED_NOTES", "notes"))

    unexpected_keys = sorted(set(payload) - {"phase", "status", "scope", "workflow", "present_surfaces", "repo_reality_gaps", "notes"})
    for key in unexpected_keys:
        issues.append(("UNEXPECTED_TOP_LEVEL_KEY", key))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOL_MANIFEST=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_manifest(root: Path, content: str) -> None:
    write_text(resolve_path(root, MANIFEST.relative_to(ROOT).as_posix()), content)


def build_self_test_root(root: Path) -> None:
    write_manifest(
        root,
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "status": EXPECTED_STATUS,
                "scope": EXPECTED_SCOPE,
                "workflow": EXPECTED_WORKFLOW,
                "present_surfaces": {
                    "review_surfaces": [
                        "Documentation/zigux/review-checklist.md",
                        "scripts/zigux/README.md",
                        "zigux/tests/README.md",
                    ],
                    "checkers": [
                        REQUIRED_CHECKER,
                        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
                        "scripts/zigux/check-phase2-kbuild-routes.py",
                        "scripts/zigux/check-phase2-toolchain-pinning.py",
                        "scripts/zigux/check-phase2-tests-readme-alignment.py",
                    ],
                    "bridge_helpers": [
                        "scripts/zigux/kconfig/conf_bridge.zig",
                        "scripts/zigux/kconfig/confdata_bridge.zig",
                    ],
                    "policy": [
                        "scripts/zigux/zig-toolchain-policy.json",
                    ],
                    "fixture_roster": [
                        "zigux/tests/fixtures/kconfig_bridge/cases.json",
                        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
                        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
                    ],
                },
                "repo_reality_gaps": list(EXPECTED_GAPS),
                "notes": list(EXPECTED_NOTES),
            },
            indent=2,
        )
        + "\n",
    )
    write_text(resolve_path(root, EXPECTED_WORKFLOW), "name: zigux-bootstrap\n")
    for rel_path in (
        "Documentation/zigux/review-checklist.md",
        "scripts/zigux/README.md",
        "zigux/tests/README.md",
        REQUIRED_CHECKER,
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-kbuild-routes.py",
        "scripts/zigux/check-phase2-toolchain-pinning.py",
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "scripts/zigux/zig-toolchain-policy.json",
        "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    ):
        content = "{}\n" if rel_path.endswith(".json") else "# present\n"
        write_text(resolve_path(root, rel_path), content)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 13
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tool_manifest_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve_path(root, MANIFEST.relative_to(ROOT).as_posix())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["phase"] = "Phase X"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("UNEXPECTED_FIELD_VALUE", "phase:Phase X") in issues
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve_path(root, MANIFEST.relative_to(ROOT).as_posix())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["checkers"].remove(REQUIRED_CHECKER)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_REQUIRED_CHECKER", REQUIRED_CHECKER) in issues
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, REQUIRED_CHECKER).unlink()
        issues = collect_issues(root)
        assert ("MISSING_PRESENT_SURFACE", REQUIRED_CHECKER) in issues
        checks_run += 1

        build_self_test_root(root)
        gap_path = resolve_path(root, EXPECTED_GAPS[0])
        write_text(gap_path, "# now present\n")
        issues = collect_issues(root)
        assert ("PRESENT_REPO_REALITY_GAP", EXPECTED_GAPS[0]) in issues
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve_path(root, MANIFEST.relative_to(ROOT).as_posix())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["repo_reality_gaps"] = [EXPECTED_GAPS[1], EXPECTED_GAPS[2], EXPECTED_GAPS[0]]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "UNEXPECTED_GAP_SET" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve_path(root, MANIFEST.relative_to(ROOT).as_posix())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["notes"] = [EXPECTED_NOTES[0]]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("UNEXPECTED_NOTES", "notes") in issues
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve_path(root, MANIFEST.relative_to(ROOT).as_posix())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["workflow"] = "other.yml"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("UNEXPECTED_FIELD_VALUE", "workflow:other.yml") in issues
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, EXPECTED_WORKFLOW).unlink()
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_PATH", EXPECTED_WORKFLOW) in issues
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve_path(root, MANIFEST.relative_to(ROOT).as_posix())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["unexpected"] = ["extra"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("UNEXPECTED_PRESENT_GROUP", "unexpected") in issues
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve_path(root, MANIFEST.relative_to(ROOT).as_posix())
        manifest_path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid JSON" in str(exc)
        else:
            raise AssertionError("invalid json did not abort")
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, MANIFEST.relative_to(ROOT).as_posix()).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing manifest did not abort")
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve_path(root, MANIFEST.relative_to(ROOT).as_posix())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["extra"] = True
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("UNEXPECTED_TOP_LEVEL_KEY", "extra") in issues
        checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_TOOL_MANIFEST_SELF_TEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the current machine-readable Phase 2 tool manifest stays aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOL_MANIFEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_PRESENT_GROUP_COUNT={len(EXPECTED_PRESENT_GROUPS)}")
    print(f"PHASE2_TOOL_MANIFEST_GAP_COUNT={len(EXPECTED_GAPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
