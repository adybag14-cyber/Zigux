#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
GENKSYMS_BRIDGE_CHECKER = Path("scripts/zigux/check-genksyms-bridge.py")

REQUIRED_MANIFEST_BRIDGE_HELPER = "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig"
REQUIRED_NOTE_FRAGMENT = "standalone invalid-long-option version-side-effect proof"
REQUIRED_HELPER_ANCHORS = (
    "genksyms bridge treats pure version requests as version command",
    "genksyms bridge preserves repeated pure version invocations",
)
EXPECTED_SELF_TEST_CASE_COUNT = 8


def read_text(root: Path, rel: Path) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {root / rel}") from exc


def read_json(root: Path, rel: Path) -> object:
    try:
        return json.loads(read_text(root, rel))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in {root / rel}: {exc.msg}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    manifest = read_json(root, MANIFEST)
    if not isinstance(manifest, dict):
        return [("INVALID_MANIFEST_PAYLOAD", type(manifest).__name__)]

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("MISSING_PRESENT_SURFACES", "present_surfaces"))
    else:
        bridge_helpers = surfaces.get("bridge_helpers")
        if not isinstance(bridge_helpers, list):
            issues.append(("MISSING_BRIDGE_HELPERS", "bridge_helpers"))
        else:
            if REQUIRED_MANIFEST_BRIDGE_HELPER not in bridge_helpers:
                issues.append(("MISSING_MANIFEST_BRIDGE_HELPER", REQUIRED_MANIFEST_BRIDGE_HELPER))

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("MISSING_MANIFEST_NOTES", "notes"))
    else:
        if not any(isinstance(note, str) and REQUIRED_NOTE_FRAGMENT in note for note in notes):
            issues.append(("MISSING_MANIFEST_NOTE_FRAGMENT", REQUIRED_NOTE_FRAGMENT))

    bootstrap_notes = read_text(root, BOOTSTRAP_NOTES)
    if REQUIRED_NOTE_FRAGMENT not in bootstrap_notes:
        issues.append(("MISSING_BOOTSTRAP_NOTE_FRAGMENT", REQUIRED_NOTE_FRAGMENT))

    checker_text = read_text(root, GENKSYMS_BRIDGE_CHECKER)
    for anchor in REQUIRED_HELPER_ANCHORS:
        if anchor not in checker_text:
            issues.append(("MISSING_GENKSYMS_HELPER_ANCHOR", anchor))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_GENKSYMS_PROOF_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    manifest = {
        "present_surfaces": {
            "bridge_helpers": [
                "scripts/zigux/kconfig/conf_bridge.zig",
                "scripts/zigux/kconfig/confdata_bridge.zig",
                "scripts/zigux/genksyms.zig",
                REQUIRED_MANIFEST_BRIDGE_HELPER,
            ]
        },
        "notes": [
            f"Current packet keeps the {REQUIRED_NOTE_FRAGMENT} explicit."
        ],
    }
    write_text(root, MANIFEST, json.dumps(manifest, indent=2) + "\n")
    write_text(
        root,
        BOOTSTRAP_NOTES,
        "# Phase 2 Toolchain Bootstrap Notes\n\n"
        f"- Current packet keeps the {REQUIRED_NOTE_FRAGMENT} explicit.\n",
    )
    write_text(
        root,
        GENKSYMS_BRIDGE_CHECKER,
        "\n".join(REQUIRED_HELPER_ANCHORS) + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="lane18_genksyms_proof_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        manifest = read_json(root, MANIFEST)
        manifest["present_surfaces"]["bridge_helpers"].remove(REQUIRED_MANIFEST_BRIDGE_HELPER)
        write_text(root, MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_MANIFEST_BRIDGE_HELPER", REQUIRED_MANIFEST_BRIDGE_HELPER) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = read_json(root, MANIFEST)
        manifest["notes"] = ["different note"]
        write_text(root, MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_MANIFEST_NOTE_FRAGMENT", REQUIRED_NOTE_FRAGMENT) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, BOOTSTRAP_NOTES, "# Phase 2 Toolchain Bootstrap Notes\n")
        assert ("MISSING_BOOTSTRAP_NOTE_FRAGMENT", REQUIRED_NOTE_FRAGMENT) in collect_issues(root)
        checks_run += 1

        for anchor in REQUIRED_HELPER_ANCHORS:
            build_self_test_root(root)
            write_text(root, GENKSYMS_BRIDGE_CHECKER, "other anchor\n")
            assert ("MISSING_GENKSYMS_HELPER_ANCHOR", anchor) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, "[]\n")
        assert ("INVALID_MANIFEST_PAYLOAD", "list") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, "{\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json" in str(exc)
        else:
            raise AssertionError("invalid manifest json did not abort")
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_GENKSYMS_PROOF_PACKET_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_PROOF_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current Phase 2 genksyms proof packet aligned across the manifest, bootstrap notes, and genksyms bridge checker."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)
    print("PHASE2_GENKSYMS_PROOF_PACKET=pass")
    print("PHASE2_GENKSYMS_PROOF_PACKET_REQUIRED_HELPER_ANCHOR_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
