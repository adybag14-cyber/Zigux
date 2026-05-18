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
TOOLCHAIN_BOOTSTRAP_DOC_PATH = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
CLOSURE_VALIDATOR_PATH = "scripts/zigux/validate-phase2-closure.py"
CLOSURE_DOC_PATH = "Documentation/zigux/phase2-closure.md"
SHARED_VALIDATOR_PATH = "scripts/zigux/validate-phase2.py"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_SURFACE_PATH = ".github/workflows/zigux-bootstrap.yml"
PIN_SCOPE_CHECKER_PATH = "scripts/zigux/check-phase2-toolchain-pin-scope.py"
INSTALLER_PATH = "scripts/zigux/install-zig.py"

CLOSURE_DOC_MARKERS = (
    "`PHASE2_TOOL_MANIFEST_CHECKER=scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "branch-local manifest packet",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`PHASE2_MASTER_PRESENT_BRANCH_MISSING=scripts/zigux/install-zig.py`",
)

BOOTSTRAP_NOTES_MARKERS = (
    "`PHASE2_TOOL_MANIFEST_CHECKER=scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "branch-local manifest packet",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`PHASE2_TOOLCHAIN_MASTER_PRESENT_BRANCH_MISSING=scripts/zigux/install-zig.py`",
)

PHASE2_VALIDATOR_MARKERS = (
    'ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest-packets.py"',
    'ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"',
)

PHASE2_CLOSURE_VALIDATOR_MARKERS = (
    '"`PHASE2_TOOL_MANIFEST_CHECKER=scripts/zigux/check-phase2-tool-manifest-packets.py`"',
    '"tool_manifest_checker"',
    '"scripts/zigux/check-phase2-tool-manifest-packets.py"',
    '"scripts/zigux/check-phase2-toolchain-pin-scope.py"',
    '"master_present_branch_missing_files"',
    '"scripts/zigux/install-zig.py"',
)

EXPECTED_PRESENT_FILES = [
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "zigux/Makefile",
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
]

EXPECTED_MISSING_FILES = [
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/install-zig.py",
]

EXPECTED_MASTER_PRESENT_BRANCH_MISSING_FILES = [INSTALLER_PATH]

EXPECTED_SELF_TEST_CASE_COUNT = 33


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
    payload = json.loads(read_text(root, MANIFEST))
    if not isinstance(payload, dict):
        raise SystemExit("phase2 tool manifest is not an object")
    return payload


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def read_manifest_string_list(
    manifest: dict[str, object],
    field: str,
    issues: list[tuple[str, str]],
) -> list[str]:
    value = manifest.get(field)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_FIELD", field))
        return []
    return value


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_doc_text = read_text(root, CLOSURE_DOC)
    bootstrap_notes_text = read_text(root, BOOTSTRAP_NOTES)
    phase2_validator_text = read_text(root, PHASE2_VALIDATOR)
    phase2_closure_validator_text = read_text(root, PHASE2_CLOSURE_VALIDATOR)
    manifest = read_manifest(root)

    issues.extend(collect_missing_markers(closure_doc_text, CLOSURE_DOC_MARKERS, "MISSING_CLOSURE_DOC_MARKERS"))
    issues.extend(
        collect_missing_markers(
            bootstrap_notes_text,
            BOOTSTRAP_NOTES_MARKERS,
            "MISSING_BOOTSTRAP_NOTES_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            phase2_validator_text,
            PHASE2_VALIDATOR_MARKERS,
            "MISSING_PHASE2_VALIDATOR_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            phase2_closure_validator_text,
            PHASE2_CLOSURE_VALIDATOR_MARKERS,
            "MISSING_PHASE2_CLOSURE_VALIDATOR_MARKERS",
        )
    )

    present_files = read_manifest_string_list(manifest, "present_files", issues)
    missing_files = read_manifest_string_list(manifest, "missing_files", issues)
    master_present_branch_missing_files = read_manifest_string_list(
        manifest,
        "master_present_branch_missing_files",
        issues,
    )

    if manifest.get("packet") != "phase2_tool_manifest":
        issues.append(("INVALID_MANIFEST_FIELD", "packet"))
    if manifest.get("phase") != "phase2":
        issues.append(("INVALID_MANIFEST_FIELD", "phase"))
    if manifest.get("status") != "lane24_branch_closure_packet_restacked":
        issues.append(("INVALID_MANIFEST_FIELD", "status"))
    if manifest.get("toolchain_bootstrap_doc") != TOOLCHAIN_BOOTSTRAP_DOC_PATH:
        issues.append(("INVALID_MANIFEST_FIELD", "toolchain_bootstrap_doc"))
    if manifest.get("closure_validator") != CLOSURE_VALIDATOR_PATH:
        issues.append(("INVALID_MANIFEST_FIELD", "closure_validator"))
    if manifest.get("closure_doc") != CLOSURE_DOC_PATH:
        issues.append(("INVALID_MANIFEST_FIELD", "closure_doc"))
    if manifest.get("shared_validator") != SHARED_VALIDATOR_PATH:
        issues.append(("INVALID_MANIFEST_FIELD", "shared_validator"))
    if manifest.get("tool_manifest_checker") != CHECKER_PATH:
        issues.append(("INVALID_MANIFEST_FIELD", "tool_manifest_checker"))
    if manifest.get("makefile") != MAKEFILE_PATH:
        issues.append(("INVALID_MANIFEST_FIELD", "makefile"))
    if present_files != EXPECTED_PRESENT_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "present_files"))
    if missing_files != EXPECTED_MISSING_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "missing_files"))
    if master_present_branch_missing_files != EXPECTED_MASTER_PRESENT_BRANCH_MISSING_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "master_present_branch_missing_files"))
    if manifest.get("workflow_surface") != WORKFLOW_SURFACE_PATH:
        issues.append(("INVALID_MANIFEST_FIELD", "workflow_surface"))

    present_set = set(present_files)
    missing_set = set(missing_files)
    overlap = sorted(present_set & missing_set)
    for relpath in overlap:
        issues.append(("MANIFEST_PATH_LIST_OVERLAP", relpath))

    for relpath in master_present_branch_missing_files:
        if relpath in present_set:
            issues.append(("MASTER_PRESENT_PATH_MARKED_PRESENT", relpath))
        if relpath not in missing_set:
            issues.append(("MASTER_PRESENT_PATH_NOT_MARKED_MISSING", relpath))

    if CHECKER_PATH in missing_files:
        issues.append(("CHECKER_STILL_MARKED_MISSING", CHECKER_PATH))
    if CHECKER_PATH not in present_files:
        issues.append(("CHECKER_NOT_MARKED_PRESENT", CHECKER_PATH))
    if PIN_SCOPE_CHECKER_PATH in missing_files:
        issues.append(("PIN_SCOPE_STILL_MARKED_MISSING", PIN_SCOPE_CHECKER_PATH))
    if PIN_SCOPE_CHECKER_PATH not in present_files:
        issues.append(("PIN_SCOPE_NOT_MARKED_PRESENT", PIN_SCOPE_CHECKER_PATH))
    if INSTALLER_PATH not in master_present_branch_missing_files:
        issues.append(("INSTALLER_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", INSTALLER_PATH))
    if INSTALLER_PATH not in missing_files:
        issues.append(("INSTALLER_NOT_MARKED_BRANCH_MISSING", INSTALLER_PATH))

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
    phase: str = "phase2",
    status: str = "lane24_branch_closure_packet_restacked",
    toolchain_bootstrap_doc: str = TOOLCHAIN_BOOTSTRAP_DOC_PATH,
    closure_validator: str = CLOSURE_VALIDATOR_PATH,
    closure_doc: str = CLOSURE_DOC_PATH,
    shared_validator: str = SHARED_VALIDATOR_PATH,
    tool_manifest_checker: str = CHECKER_PATH,
    makefile: str = MAKEFILE_PATH,
    present_files: list[str] | object | None = None,
    missing_files: list[str] | object | None = None,
    master_present_branch_missing_files: list[str] | object | None = None,
    workflow_surface: str = WORKFLOW_SURFACE_PATH,
) -> str:
    payload = {
        "packet": packet,
        "phase": phase,
        "status": status,
        "toolchain_bootstrap_doc": toolchain_bootstrap_doc,
        "closure_validator": closure_validator,
        "closure_doc": closure_doc,
        "shared_validator": shared_validator,
        "tool_manifest_checker": tool_manifest_checker,
        "makefile": makefile,
        "present_files": EXPECTED_PRESENT_FILES if present_files is None else present_files,
        "missing_files": EXPECTED_MISSING_FILES if missing_files is None else missing_files,
        "master_present_branch_missing_files": (
            EXPECTED_MASTER_PRESENT_BRANCH_MISSING_FILES
            if master_present_branch_missing_files is None
            else master_present_branch_missing_files
        ),
        "workflow_surface": workflow_surface,
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


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tool_manifest_packets_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for path, marker, code in (
            (CLOSURE_DOC, CLOSURE_DOC_MARKERS[0], "MISSING_CLOSURE_DOC_MARKERS"),
            (BOOTSTRAP_NOTES, BOOTSTRAP_NOTES_MARKERS[0], "MISSING_BOOTSTRAP_NOTES_MARKERS"),
            (PHASE2_VALIDATOR, PHASE2_VALIDATOR_MARKERS[0], "MISSING_PHASE2_VALIDATOR_MARKERS"),
            (
                PHASE2_CLOSURE_VALIDATOR,
                PHASE2_CLOSURE_VALIDATOR_MARKERS[0],
                "MISSING_PHASE2_CLOSURE_VALIDATOR_MARKERS",
            ),
        ):
            build_self_test_root(root)
            resolved = resolve_path(root, path)
            resolved.write_text(replace_once(resolved.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert (code, marker) in collect_issues(root)
            checks_run += 1

        for field, kwargs in (
            ("packet", {"packet": "wrong"}),
            ("phase", {"phase": "Phase 2"}),
            ("status", {"status": "partial"}),
            ("toolchain_bootstrap_doc", {"toolchain_bootstrap_doc": "Documentation/zigux/other.md"}),
            ("closure_validator", {"closure_validator": "scripts/zigux/other.py"}),
            ("closure_doc", {"closure_doc": "Documentation/zigux/other.md"}),
            ("shared_validator", {"shared_validator": "scripts/zigux/other.py"}),
            ("tool_manifest_checker", {"tool_manifest_checker": "scripts/zigux/other.py"}),
            ("makefile", {"makefile": "zigux/Other.mk"}),
            ("workflow_surface", {"workflow_surface": ".github/workflows/other.yml"}),
        ):
            build_self_test_root(root)
            write_text(root, MANIFEST, manifest_json(**kwargs))
            assert ("INVALID_MANIFEST_FIELD", field) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(present_files="not-a-list"))
        assert ("INVALID_MANIFEST_FIELD", "present_files") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(missing_files=[EXPECTED_MISSING_FILES[0], 7]))
        assert ("INVALID_MANIFEST_FIELD", "missing_files") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(master_present_branch_missing_files=[PIN_SCOPE_CHECKER_PATH, 7]))
        assert ("INVALID_MANIFEST_FIELD", "master_present_branch_missing_files") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(present_files=EXPECTED_PRESENT_FILES[:-1]))
        assert ("INVALID_MANIFEST_FIELD", "present_files") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(missing_files=EXPECTED_MISSING_FILES[:-1]))
        issues = collect_issues(root)
        assert ("INVALID_MANIFEST_FIELD", "missing_files") in issues
        assert ("MASTER_PRESENT_PATH_NOT_MARKED_MISSING", INSTALLER_PATH) in issues
        assert ("INSTALLER_NOT_MARKED_BRANCH_MISSING", INSTALLER_PATH) in issues
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(master_present_branch_missing_files=[]))
        issues = collect_issues(root)
        assert ("INVALID_MANIFEST_FIELD", "master_present_branch_missing_files") in issues
        assert ("INSTALLER_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", INSTALLER_PATH) in issues
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(master_present_branch_missing_files=[PIN_SCOPE_CHECKER_PATH]))
        issues = collect_issues(root)
        assert ("INVALID_MANIFEST_FIELD", "master_present_branch_missing_files") in issues
        assert ("MASTER_PRESENT_PATH_MARKED_PRESENT", PIN_SCOPE_CHECKER_PATH) in issues
        assert ("MASTER_PRESENT_PATH_NOT_MARKED_MISSING", PIN_SCOPE_CHECKER_PATH) in issues
        assert ("INSTALLER_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", INSTALLER_PATH) in issues
        checks_run += 1

        build_self_test_root(root)
        write_text(
            root,
            MANIFEST,
            manifest_json(
                present_files=[item for item in EXPECTED_PRESENT_FILES if item != CHECKER_PATH],
            ),
        )
        assert ("CHECKER_NOT_MARKED_PRESENT", CHECKER_PATH) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(
            root,
            MANIFEST,
            manifest_json(missing_files=[CHECKER_PATH, *EXPECTED_MISSING_FILES]),
        )
        issues = collect_issues(root)
        assert ("CHECKER_STILL_MARKED_MISSING", CHECKER_PATH) in issues
        checks_run += 1

        build_self_test_root(root)
        write_text(
            root,
            MANIFEST,
            manifest_json(
                present_files=[item for item in EXPECTED_PRESENT_FILES if item != PIN_SCOPE_CHECKER_PATH],
            ),
        )
        assert ("PIN_SCOPE_NOT_MARKED_PRESENT", PIN_SCOPE_CHECKER_PATH) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(
            root,
            MANIFEST,
            manifest_json(missing_files=[PIN_SCOPE_CHECKER_PATH, *EXPECTED_MISSING_FILES]),
        )
        issues = collect_issues(root)
        assert ("PIN_SCOPE_STILL_MARKED_MISSING", PIN_SCOPE_CHECKER_PATH) in issues
        checks_run += 1

        build_self_test_root(root)
        write_text(
            root,
            MANIFEST,
            manifest_json(
                present_files=[*EXPECTED_PRESENT_FILES, EXPECTED_MISSING_FILES[0]],
            ),
        )
        issues = collect_issues(root)
        assert ("INVALID_MANIFEST_FIELD", "present_files") in issues
        assert ("MANIFEST_PATH_LIST_OVERLAP", EXPECTED_MISSING_FILES[0]) in issues
        checks_run += 1

        build_self_test_root(root)
        write_text(
            root,
            MANIFEST,
            manifest_json(master_present_branch_missing_files=["scripts/zigux/extra-missing.py"]),
        )
        issues = collect_issues(root)
        assert ("INVALID_MANIFEST_FIELD", "master_present_branch_missing_files") in issues
        assert ("MASTER_PRESENT_PATH_NOT_MARKED_MISSING", "scripts/zigux/extra-missing.py") in issues
        assert ("INSTALLER_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", INSTALLER_PATH) in issues
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, MANIFEST).write_text("[]\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "not an object" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("non-object manifest did not abort")

        for rel_path in (CLOSURE_DOC, BOOTSTRAP_NOTES, PHASE2_VALIDATOR, PHASE2_CLOSURE_VALIDATOR):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_PACKETS_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 24 Phase 2 manifest packet stays aligned across the closure packet surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOL_MANIFEST_PACKETS=pass")
    print(f"ROOT={args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
