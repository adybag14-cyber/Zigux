#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
PHASE2_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
PHASE2_CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

CHECKER_PATH = "scripts/zigux/check-phase2-tool-manifest-packets.py"
EXPECTED_TOOLCHAIN_BOOTSTRAP_DOC = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
EXPECTED_CLOSURE_VALIDATOR = "scripts/zigux/validate-phase2-closure.py"
EXPECTED_CLOSURE_DOC = "Documentation/zigux/phase2-closure.md"
EXPECTED_SHARED_VALIDATOR = "scripts/zigux/validate-phase2.py"
EXPECTED_MAKEFILE = "zigux/Makefile"
EXPECTED_WORKFLOW_SURFACE = ".github/workflows/zigux-bootstrap.yml"

CLOSURE_DOC_MARKERS = (
    "`PHASE2_TOOL_MANIFEST_CHECKER=scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "branch-local manifest packet",
    "directly readable on the lane branch",
)

BOOTSTRAP_NOTES_MARKERS = (
    "shared validator gate: `python3 scripts/zigux/validate-phase2.py`",
    "closure validator gate: `python3 scripts/zigux/validate-phase2-closure.py`",
    "Linux-style validator route: `make -C zigux phase2-validate`",
    "the broader fixdep, genksyms, artifact-tools, and manifest packet should stay documented through `Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and `zigux/Makefile` instead of restating the full broader checker inventory in this dedicated pin-scope note",
)

PHASE2_VALIDATOR_MARKERS = (
    'ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest-packets.py"',
    'ROOT / "scripts" / "zigux" / "check-phase2-cross.py"',
)

PHASE2_CLOSURE_VALIDATOR_MARKERS = (
    '"`PHASE2_TOOL_MANIFEST_CHECKER=scripts/zigux/check-phase2-tool-manifest-packets.py`"',
    '"tool_manifest_checker"',
    '"scripts/zigux/check-phase2-tool-manifest-packets.py"',
    '"master_present_branch_missing_files"',
)

EXPECTED_PRESENT_FILES = [
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-readme-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-zig-toolchain.py",
]

EXPECTED_MISSING_FILES = [
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/install-zig.py",
]

EXPECTED_SHARED_PRESENT_FILES = [
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-zig-toolchain.py",
]

EXPECTED_MANIFEST_FIELDS = {
    "packet",
    "phase",
    "status",
    "toolchain_bootstrap_doc",
    "closure_validator",
    "closure_doc",
    "shared_validator",
    "tool_manifest_checker",
    "makefile",
    "present_files",
    "missing_files",
    "master_present_branch_missing_files",
    "workflow_surface",
}

EXPECTED_MASTER_PRESENT_BRANCH_MISSING_FILES: list[str] = []
EXPECTED_SELF_TEST_CASE_COUNT = 55


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def read_text(root: Path, path: Path) -> str:
    resolved = resolve_path(root, path)
    try:
        return resolved.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {resolved}") from exc


def read_manifest(root: Path) -> dict[str, object]:
    resolved = resolve_path(root, MANIFEST)
    try:
        raw = resolved.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {resolved}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"manifest is not valid json: {resolved}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"manifest is not an object: {resolved}")
    return payload


def collect_marker_count_issues(
    text: str,
    markers: tuple[str, ...],
    *,
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_duplicate_manifest_entries(values: object, code: str) -> list[tuple[str, str]]:
    if not isinstance(values, list):
        return []

    counts: dict[str, int] = {}
    for value in values:
        key = value if isinstance(value, str) else repr(value)
        counts[key] = counts.get(key, 0) + 1
    return [(code, f"{key}:count={count}") for key, count in counts.items() if count > 1]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_doc_text = read_text(root, CLOSURE_DOC)
    bootstrap_notes_text = read_text(root, BOOTSTRAP_NOTES)
    phase2_validator_text = read_text(root, PHASE2_VALIDATOR)
    phase2_closure_validator_text = read_text(root, PHASE2_CLOSURE_VALIDATOR)
    manifest = read_manifest(root)

    issues.extend(
        collect_marker_count_issues(
            closure_doc_text,
            CLOSURE_DOC_MARKERS,
            missing_code="MISSING_CLOSURE_DOC_MARKERS",
            duplicate_code="DUPLICATE_CLOSURE_DOC_MARKERS",
        )
    )
    issues.extend(
        collect_marker_count_issues(
            bootstrap_notes_text,
            BOOTSTRAP_NOTES_MARKERS,
            missing_code="MISSING_BOOTSTRAP_NOTES_MARKERS",
            duplicate_code="DUPLICATE_BOOTSTRAP_NOTES_MARKERS",
        )
    )
    issues.extend(
        collect_marker_count_issues(
            phase2_validator_text,
            PHASE2_VALIDATOR_MARKERS,
            missing_code="MISSING_PHASE2_VALIDATOR_MARKERS",
            duplicate_code="DUPLICATE_PHASE2_VALIDATOR_MARKERS",
        )
    )
    issues.extend(
        collect_marker_count_issues(
            phase2_closure_validator_text,
            PHASE2_CLOSURE_VALIDATOR_MARKERS,
            missing_code="MISSING_PHASE2_CLOSURE_VALIDATOR_MARKERS",
            duplicate_code="DUPLICATE_PHASE2_CLOSURE_VALIDATOR_MARKERS",
        )
    )

    unexpected_fields = sorted(set(manifest) - EXPECTED_MANIFEST_FIELDS)
    if unexpected_fields:
        issues.extend(("UNEXPECTED_MANIFEST_FIELD", field) for field in unexpected_fields)

    present_files = manifest.get("present_files")
    missing_files = manifest.get("missing_files")

    issues.extend(collect_duplicate_manifest_entries(present_files, "DUPLICATE_PRESENT_FILE_ENTRY"))
    issues.extend(collect_duplicate_manifest_entries(missing_files, "DUPLICATE_MISSING_FILE_ENTRY"))
    if isinstance(present_files, list) and isinstance(missing_files, list):
        present_set = {value for value in present_files if isinstance(value, str)}
        missing_set = {value for value in missing_files if isinstance(value, str)}
        issues.extend(
            ("MANIFEST_PATH_IN_BOTH_PRESENT_AND_MISSING", value)
            for value in sorted(present_set & missing_set)
        )

    if manifest.get("packet") != "phase2_tool_manifest":
        issues.append(("INVALID_MANIFEST_FIELD", "packet"))
    if manifest.get("phase") != "phase2":
        issues.append(("INVALID_MANIFEST_FIELD", "phase"))
    if manifest.get("status") != "lane22_branch_closure_packet_restacked":
        issues.append(("INVALID_MANIFEST_FIELD", "status"))
    if manifest.get("toolchain_bootstrap_doc") != EXPECTED_TOOLCHAIN_BOOTSTRAP_DOC:
        issues.append(("INVALID_MANIFEST_FIELD", "toolchain_bootstrap_doc"))
    if manifest.get("closure_validator") != EXPECTED_CLOSURE_VALIDATOR:
        issues.append(("INVALID_MANIFEST_FIELD", "closure_validator"))
    if manifest.get("closure_doc") != EXPECTED_CLOSURE_DOC:
        issues.append(("INVALID_MANIFEST_FIELD", "closure_doc"))
    if manifest.get("shared_validator") != EXPECTED_SHARED_VALIDATOR:
        issues.append(("INVALID_MANIFEST_FIELD", "shared_validator"))
    if manifest.get("tool_manifest_checker") != CHECKER_PATH:
        issues.append(("INVALID_MANIFEST_FIELD", "tool_manifest_checker"))
    if manifest.get("makefile") != EXPECTED_MAKEFILE:
        issues.append(("INVALID_MANIFEST_FIELD", "makefile"))
    if manifest.get("present_files") != EXPECTED_PRESENT_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "present_files"))
    if manifest.get("missing_files") != EXPECTED_MISSING_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "missing_files"))
    if manifest.get("master_present_branch_missing_files") != EXPECTED_MASTER_PRESENT_BRANCH_MISSING_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "master_present_branch_missing_files"))
    if manifest.get("workflow_surface") != EXPECTED_WORKFLOW_SURFACE:
        issues.append(("INVALID_MANIFEST_FIELD", "workflow_surface"))

    if CHECKER_PATH in manifest.get("missing_files", []):
        issues.append(("CHECKER_STILL_MARKED_MISSING", CHECKER_PATH))
    if CHECKER_PATH not in manifest.get("present_files", []):
        issues.append(("CHECKER_NOT_MARKED_PRESENT", CHECKER_PATH))
    for shared_path in EXPECTED_SHARED_PRESENT_FILES:
        if shared_path in manifest.get("missing_files", []):
            issues.append(("SHARED_TOOL_STILL_MARKED_MISSING", shared_path))
        if shared_path not in manifest.get("present_files", []):
            issues.append(("SHARED_TOOL_NOT_MARKED_PRESENT", shared_path))

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


def write_text(root: Path, path: Path, content: str) -> None:
    resolved = resolve_path(root, path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding="utf-8")


def manifest_json(
    *,
    packet: str = "phase2_tool_manifest",
    tool_manifest_checker: str = CHECKER_PATH,
    present_files: list[str] | None = None,
    missing_files: list[str] | None = None,
) -> str:
    payload = {
        "packet": packet,
        "phase": "phase2",
        "status": "lane22_branch_closure_packet_restacked",
        "toolchain_bootstrap_doc": EXPECTED_TOOLCHAIN_BOOTSTRAP_DOC,
        "closure_validator": EXPECTED_CLOSURE_VALIDATOR,
        "closure_doc": EXPECTED_CLOSURE_DOC,
        "shared_validator": EXPECTED_SHARED_VALIDATOR,
        "tool_manifest_checker": tool_manifest_checker,
        "makefile": EXPECTED_MAKEFILE,
        "present_files": EXPECTED_PRESENT_FILES if present_files is None else present_files,
        "missing_files": EXPECTED_MISSING_FILES if missing_files is None else missing_files,
        "master_present_branch_missing_files": EXPECTED_MASTER_PRESENT_BRANCH_MISSING_FILES,
        "workflow_surface": EXPECTED_WORKFLOW_SURFACE,
    }
    return json.dumps(payload, indent=2) + "\n"


def build_self_test_root(root: Path) -> None:
    write_text(root, CLOSURE_DOC, "\n".join(CLOSURE_DOC_MARKERS) + "\n")
    write_text(root, BOOTSTRAP_NOTES, "\n".join(BOOTSTRAP_NOTES_MARKERS) + "\n")
    write_text(root, PHASE2_VALIDATOR, "\n".join(PHASE2_VALIDATOR_MARKERS) + "\n")
    write_text(root, PHASE2_CLOSURE_VALIDATOR, "\n".join(PHASE2_CLOSURE_VALIDATOR_MARKERS) + "\n")
    write_text(root, MANIFEST, manifest_json())


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def duplicate_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, f"{marker}\n{marker}", 1)


def assert_system_exit_contains(callback, expected_fragment: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        assert expected_fragment in str(exc), str(exc)
        return
    raise AssertionError(f"expected SystemExit containing: {expected_fragment}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tool_manifest_packets_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for path, markers, missing_code, duplicate_code in (
            (
                CLOSURE_DOC,
                CLOSURE_DOC_MARKERS,
                "MISSING_CLOSURE_DOC_MARKERS",
                "DUPLICATE_CLOSURE_DOC_MARKERS",
            ),
            (
                BOOTSTRAP_NOTES,
                BOOTSTRAP_NOTES_MARKERS,
                "MISSING_BOOTSTRAP_NOTES_MARKERS",
                "DUPLICATE_BOOTSTRAP_NOTES_MARKERS",
            ),
            (
                PHASE2_VALIDATOR,
                PHASE2_VALIDATOR_MARKERS,
                "MISSING_PHASE2_VALIDATOR_MARKERS",
                "DUPLICATE_PHASE2_VALIDATOR_MARKERS",
            ),
            (
                PHASE2_CLOSURE_VALIDATOR,
                PHASE2_CLOSURE_VALIDATOR_MARKERS,
                "MISSING_PHASE2_CLOSURE_VALIDATOR_MARKERS",
                "DUPLICATE_PHASE2_CLOSURE_VALIDATOR_MARKERS",
            ),
        ):
            for marker in markers:
                build_self_test_root(root)
                resolved = resolve_path(root, path)
                resolved.write_text(replace_once(resolved.read_text(encoding="utf-8"), marker), encoding="utf-8")
                assert (missing_code, marker) in collect_issues(root)
                checks_run += 1

                build_self_test_root(root)
                resolved = resolve_path(root, path)
                resolved.write_text(duplicate_once(resolved.read_text(encoding="utf-8"), marker), encoding="utf-8")
                assert (duplicate_code, f"{marker}:count=2") in collect_issues(root)
                checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(packet="wrong"))
        assert ("INVALID_MANIFEST_FIELD", "packet") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(tool_manifest_checker="scripts/zigux/other.py"))
        assert ("INVALID_MANIFEST_FIELD", "tool_manifest_checker") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(present_files=EXPECTED_PRESENT_FILES[:-1]))
        assert ("INVALID_MANIFEST_FIELD", "present_files") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(missing_files=EXPECTED_MISSING_FILES[:-1]))
        assert ("INVALID_MANIFEST_FIELD", "missing_files") in collect_issues(root)
        checks_run += 1

        for field in (
            "phase",
            "status",
            "toolchain_bootstrap_doc",
            "closure_validator",
            "closure_doc",
            "shared_validator",
            "makefile",
            "master_present_branch_missing_files",
            "workflow_surface",
        ):
            build_self_test_root(root)
            bad = json.loads(manifest_json())
            bad[field] = ["wrong"] if field == "master_present_branch_missing_files" else "wrong"
            write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
            assert ("INVALID_MANIFEST_FIELD", field) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["unexpected"] = "value"
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        assert ("UNEXPECTED_MANIFEST_FIELD", "unexpected") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["present_files"] = EXPECTED_PRESENT_FILES + [EXPECTED_PRESENT_FILES[0]]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        assert ("DUPLICATE_PRESENT_FILE_ENTRY", f"{EXPECTED_PRESENT_FILES[0]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["missing_files"] = EXPECTED_MISSING_FILES + [EXPECTED_MISSING_FILES[0]]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        assert ("DUPLICATE_MISSING_FILE_ENTRY", f"{EXPECTED_MISSING_FILES[0]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["missing_files"] = EXPECTED_MISSING_FILES + [EXPECTED_PRESENT_FILES[0]]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        assert ("MANIFEST_PATH_IN_BOTH_PRESENT_AND_MISSING", EXPECTED_PRESENT_FILES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["present_files"] = [item for item in EXPECTED_PRESENT_FILES if item != CHECKER_PATH]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        assert ("CHECKER_NOT_MARKED_PRESENT", CHECKER_PATH) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["missing_files"] = EXPECTED_MISSING_FILES + [CHECKER_PATH]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        assert ("CHECKER_STILL_MARKED_MISSING", CHECKER_PATH) in collect_issues(root)
        checks_run += 1

        for shared_path in EXPECTED_SHARED_PRESENT_FILES:
            build_self_test_root(root)
            bad = json.loads(manifest_json())
            bad["present_files"] = [item for item in EXPECTED_PRESENT_FILES if item != shared_path]
            write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
            assert ("SHARED_TOOL_NOT_MARKED_PRESENT", shared_path) in collect_issues(root)
            checks_run += 1

            build_self_test_root(root)
            bad = json.loads(manifest_json())
            bad["missing_files"] = EXPECTED_MISSING_FILES + [shared_path]
            write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
            assert ("SHARED_TOOL_STILL_MARKED_MISSING", shared_path) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        resolve_path(root, MANIFEST).unlink()
        assert_system_exit_contains(lambda: collect_issues(root), "required file missing:")
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, "{\n")
        assert_system_exit_contains(lambda: collect_issues(root), "manifest is not valid json:")
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, "[]\n")
        assert_system_exit_contains(lambda: collect_issues(root), "manifest is not an object:")
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep the Lane 22 Phase 2 tool manifest packet aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOL_MANIFEST_PACKETS=pass")
    print(f"PHASE2_TOOL_MANIFEST_PRESENT_COUNT={len(EXPECTED_PRESENT_FILES)}")
    print(f"PHASE2_TOOL_MANIFEST_MISSING_COUNT={len(EXPECTED_MISSING_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
