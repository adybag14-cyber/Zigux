#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CLOSURE_DOC = Path("Documentation/zigux/phase2-closure.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_VALIDATOR = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE_VALIDATOR = Path("scripts/zigux/validate-phase2-closure.py")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

CLOSURE_REQUIRED_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`scripts/zigux/genksyms.zig`",
    "`make -C zigux phase2-genksyms`",
    "`PHASE2_CURRENT_GAP_PACKET=`",
    "current `master` no longer leaves the installer hook, direct cross-route packet, or returned closure-validator companions in the repo-reality-gap bucket",
    "bounded genksyms bridge checker",
)

CLOSURE_FORBIDDEN_MARKERS = (
    "The remaining current `master` repo-reality gaps are the installer and direct cross-route companions:",
)

BOOTSTRAP_REQUIRED_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`make -C zigux phase2-genksyms`",
    "bounded genksyms bridge checker and fixture roster",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, and direct cross-route packet on current `master`.",
)

VALIDATOR_REQUIRED_MARKERS = (
    '"scripts/zigux/install-zig.py",',
    '"scripts/zigux/check-genksyms-bridge.py",',
    '"scripts/zigux/genksyms.zig",',
    '"zigux/tests/fixtures/genksyms_bridge/cases.json",',
    '"zigux/tests/fixtures/genksyms_bridge/help_expected.json",',
    '"make -C zigux phase2-genksyms",',
    '"run: python3 scripts/zigux/validate-phase2.py",',
)

CLOSURE_VALIDATOR_REQUIRED_MARKERS = (
    '"scripts/zigux/install-zig.py",',
    '"scripts/zigux/check-phase2-cross.py",',
    '"zigux/tests/fixtures/phase2_cross_targets.json",',
    '"scripts/zigux/validate-phase2-closure.py",',
    '"scripts/zigux/genksyms.zig",',
    '"zigux/tests/fixtures/genksyms_bridge/cases.json",',
    '"zigux/tests/fixtures/genksyms_bridge/help_expected.json",',
)

WORKFLOW_REQUIRED_MARKERS = (
    'run: python3 scripts/zigux/check-phase2-tool-manifest-packets.py --self-test',
    'run: python3 scripts/zigux/check-phase2-tool-manifest-packets.py',
)

MAKEFILE_REQUIRED_MARKERS = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2-genksyms:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
)

EXPECTED_PRESENT_SURFACES = {
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
}

EXPECTED_NOTE_MARKERS = (
    "Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, returned installer helper, direct cross-route checker",
    "Keep scripts/zigux/validate-phase2-closure.py out of the repo-reality-gap list",
    "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-validate, and phase2 make wrappers",
    "Keep the returned installer helper, direct cross-route checker, phase2_cross_targets fixture, and bounded genksyms fixture packet explicit",
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(root: Path, rel: Path) -> str:
    path = resolve(root, rel)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = resolve(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_manifest(root: Path) -> dict[str, object]:
    path = resolve(root, MANIFEST)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("phase2 tool manifest is not an object")
    return payload


def collect_marker_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_exact_line_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def require_string_list(
    issues: list[tuple[str, str]],
    mapping: dict[str, object],
    key: str,
    expected: list[str],
) -> None:
    value = mapping.get(key)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_FIELD", key))
        return
    if value != expected:
        issues.append(("INVALID_MANIFEST_FIELD", key))


def collect_manifest_issues(manifest: dict[str, object]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    if manifest.get("phase") != "Phase 2":
        issues.append(("INVALID_MANIFEST_FIELD", "phase"))
    if manifest.get("status") != "active":
        issues.append(("INVALID_MANIFEST_FIELD", "status"))
    if manifest.get("scope") != "current directly readable scripts-root toolchain, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, and tranche-closure reminder packet":
        issues.append(("INVALID_MANIFEST_FIELD", "scope"))
    if manifest.get("workflow") != ".github/workflows/zigux-bootstrap.yml":
        issues.append(("INVALID_MANIFEST_FIELD", "workflow"))

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_FIELD", "present_surfaces"))
    else:
        for key, expected in EXPECTED_PRESENT_SURFACES.items():
            require_string_list(issues, present_surfaces, key, expected)

    gaps = manifest.get("repo_reality_gaps")
    if gaps != []:
        issues.append(("INVALID_MANIFEST_FIELD", "repo_reality_gaps"))

    notes = manifest.get("notes")
    if not isinstance(notes, list) or any(not isinstance(item, str) for item in notes):
        issues.append(("INVALID_MANIFEST_FIELD", "notes"))
    else:
        joined = "\n".join(notes)
        for marker in EXPECTED_NOTE_MARKERS:
            if marker not in joined:
                issues.append(("INVALID_MANIFEST_NOTE", marker))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    closure_text = read_text(root, CLOSURE_DOC)
    bootstrap_text = read_text(root, BOOTSTRAP_NOTES)
    validator_text = read_text(root, PHASE2_VALIDATOR)
    closure_validator_text = read_text(root, PHASE2_CLOSURE_VALIDATOR)
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)

    issues.extend(collect_marker_issues(closure_text, CLOSURE_REQUIRED_MARKERS, "MISSING_CLOSURE_MARKER"))
    issues.extend(collect_forbidden_issues(closure_text, CLOSURE_FORBIDDEN_MARKERS, "FORBIDDEN_CLOSURE_MARKER"))
    issues.extend(collect_marker_issues(bootstrap_text, BOOTSTRAP_REQUIRED_MARKERS, "MISSING_BOOTSTRAP_MARKER"))
    issues.extend(collect_marker_issues(validator_text, VALIDATOR_REQUIRED_MARKERS, "MISSING_VALIDATOR_MARKER"))
    issues.extend(
        collect_marker_issues(
            closure_validator_text,
            CLOSURE_VALIDATOR_REQUIRED_MARKERS,
            "MISSING_CLOSURE_VALIDATOR_MARKER",
        )
    )
    issues.extend(collect_exact_line_issues(workflow_text, WORKFLOW_REQUIRED_MARKERS, "MISSING_WORKFLOW_MARKER", "DUPLICATE_WORKFLOW_MARKER"))
    issues.extend(collect_marker_issues(makefile_text, MAKEFILE_REQUIRED_MARKERS, "MISSING_MAKEFILE_MARKER"))
    issues.extend(collect_manifest_issues(read_manifest(root)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOL_MANIFEST_PACKETS=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_manifest(*, bad_field: str | None = None, bad_value: object | None = None) -> str:
    payload: dict[str, object] = {
        "phase": "Phase 2",
        "status": "active",
        "scope": "current directly readable scripts-root toolchain, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, and tranche-closure reminder packet",
        "workflow": ".github/workflows/zigux-bootstrap.yml",
        "present_surfaces": EXPECTED_PRESENT_SURFACES,
        "repo_reality_gaps": [],
        "notes": list(EXPECTED_NOTE_MARKERS) + [
            "Current Phase 2 repo-tooling evidence remains directly readable on current master.",
        ],
    }
    if bad_field is not None:
        payload[bad_field] = bad_value
    return json.dumps(payload, indent=2) + "\n"


def build_self_test_root(root: Path) -> None:
    write_text(root, CLOSURE_DOC, "\n".join(CLOSURE_REQUIRED_MARKERS) + "\n")
    write_text(root, BOOTSTRAP_NOTES, "\n".join(BOOTSTRAP_REQUIRED_MARKERS) + "\n")
    write_text(root, PHASE2_VALIDATOR, "\n".join(VALIDATOR_REQUIRED_MARKERS) + "\n")
    write_text(
        root,
        PHASE2_CLOSURE_VALIDATOR,
        "\n".join(CLOSURE_VALIDATOR_REQUIRED_MARKERS) + "\n",
    )
    write_text(root, WORKFLOW, "\n".join(("name: zigux-bootstrap", *WORKFLOW_REQUIRED_MARKERS)) + "\n")
    write_text(root, MAKEFILE, "\n".join(MAKEFILE_REQUIRED_MARKERS) + "\n")
    write_text(root, MANIFEST, build_manifest())


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tool_manifest_packets_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root, CLOSURE_DOC, replace_once(read_text(root, CLOSURE_DOC), CLOSURE_REQUIRED_MARKERS[0]))
        assert ("MISSING_CLOSURE_MARKER", CLOSURE_REQUIRED_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, CLOSURE_DOC, read_text(root, CLOSURE_DOC) + CLOSURE_FORBIDDEN_MARKERS[0] + "\n")
        assert ("FORBIDDEN_CLOSURE_MARKER", CLOSURE_FORBIDDEN_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, BOOTSTRAP_NOTES, replace_once(read_text(root, BOOTSTRAP_NOTES), BOOTSTRAP_REQUIRED_MARKERS[0]))
        assert ("MISSING_BOOTSTRAP_MARKER", BOOTSTRAP_REQUIRED_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, PHASE2_VALIDATOR, replace_once(read_text(root, PHASE2_VALIDATOR), VALIDATOR_REQUIRED_MARKERS[0]))
        assert ("MISSING_VALIDATOR_MARKER", VALIDATOR_REQUIRED_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            PHASE2_CLOSURE_VALIDATOR,
            replace_once(read_text(root, PHASE2_CLOSURE_VALIDATOR), CLOSURE_VALIDATOR_REQUIRED_MARKERS[0]),
        )
        assert ("MISSING_CLOSURE_VALIDATOR_MARKER", CLOSURE_VALIDATOR_REQUIRED_MARKERS[0]) in collect_issues(root)
        checks += 1

        for workflow_marker in WORKFLOW_REQUIRED_MARKERS:
            build_self_test_root(root)
            write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), workflow_marker))
            assert ("MISSING_WORKFLOW_MARKER", workflow_marker) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, MAKEFILE_REQUIRED_MARKERS[0] + "\n")
        assert ("MISSING_MAKEFILE_MARKER", MAKEFILE_REQUIRED_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, build_manifest(bad_field="repo_reality_gaps", bad_value=["scripts/zigux/install-zig.py"]))
        assert ("INVALID_MANIFEST_FIELD", "repo_reality_gaps") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, build_manifest(bad_field="status", bad_value="parked"))
        assert ("INVALID_MANIFEST_FIELD", "status") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        manifest = json.loads(build_manifest())
        manifest["present_surfaces"] = "wrong"
        write_text(root, MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert ("INVALID_MANIFEST_FIELD", "present_surfaces") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        manifest = json.loads(build_manifest())
        manifest["notes"] = ["too narrow"]
        write_text(root, MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert ("INVALID_MANIFEST_NOTE", EXPECTED_NOTE_MARKERS[0]) in collect_issues(root)
        checks += 1

    print("PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 2 tool-manifest packet against the live closure surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOL_MANIFEST_PACKETS=pass")
    print(f"PHASE2_TOOL_MANIFEST_PRESENT_SURFACE_GROUP_COUNT={len(EXPECTED_PRESENT_SURFACES)}")
    print(f"PHASE2_TOOL_MANIFEST_NOTE_MARKER_COUNT={len(EXPECTED_NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
