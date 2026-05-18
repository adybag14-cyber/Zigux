#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
INSTALLER_PATH = "scripts/zigux/install-zig.py"
CROSS_CHECKER_PATH = "scripts/zigux/check-phase2-cross.py"
CROSS_FIXTURE_PATH = "zigux/tests/fixtures/phase2_cross_targets.json"

EXPECTED_DOC_MARKERS = (
    "`PHASE2_STATUS=lane24-branch-restacked`",
    "`PHASE2_CLOSURE_ROUTE_STATUS=branch-closure-packet-restacked-on-current-master`",
    "`PHASE2_CLOSURE_VALIDATOR_SELF_TEST=python3 scripts/zigux/validate-phase2-closure.py --self-test`",
    "`PHASE2_CLOSURE_VALIDATOR_GATE=python3 scripts/zigux/validate-phase2-closure.py`",
    "`PHASE2_TOOL_MANIFEST=zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`PHASE2_TOOL_MANIFEST_CHECKER=scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`PHASE2_TOOLCHAIN_BOOTSTRAP_NOTES=Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`PHASE2_SHARED_VALIDATOR=scripts/zigux/validate-phase2.py`",
    "`PHASE2_SHARED_MAKEFILE=zigux/Makefile`",
    "`PHASE2_MASTER_PRESENT_BRANCH_MISSING=scripts/zigux/check-phase2-cross.py`",
    "`PHASE2_MASTER_PRESENT_BRANCH_MISSING=zigux/tests/fixtures/phase2_cross_targets.json`",
    "`PHASE2_MASTER_PRESENT_BRANCH_MISSING=scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-kconfig-readme-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/install-zig.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current `master` already directly serves `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `scripts/zigux/install-zig.py`",
    "`PHASE2_NEXT_STEP=restore one remaining broader checker, fixture-backed helper, or installer-backed helper packet at a time now that the closure note, bootstrap companion, shared validator, dedicated kconfig README checker, dedicated toolchain pin-scope guard, manifest checker, and Linux-style Makefile routes are replayed together on the lane branch`",
)

EXPECTED_BOOTSTRAP_NOTES_MARKERS = (
    "`PHASE2_TOOLCHAIN_BOOTSTRAP_STATUS=lane24-branch-restacked`",
    "`PHASE2_TOOLCHAIN_SURVIVING_GUARD=scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`PHASE2_TOOLCHAIN_PIN_SCOPE_GUARD=scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`PHASE2_TOOLCHAIN_ZIG_VERSION_GUARD=scripts/zigux/check-zig-toolchain.py`",
    "`PHASE2_TOOLCHAIN_WORKFLOW_SURFACE=.github/workflows/zigux-bootstrap.yml`",
    "`PHASE2_CLOSURE_COMPANION=Documentation/zigux/phase2-closure.md`",
    "`PHASE2_TOOL_MANIFEST=zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`PHASE2_TOOL_MANIFEST_CHECKER=scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`PHASE2_SHARED_VALIDATOR=scripts/zigux/validate-phase2.py`",
    "`PHASE2_SHARED_MAKEFILE=zigux/Makefile`",
    "`PHASE2_TOOLCHAIN_MASTER_PRESENT_BRANCH_MISSING=scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "current `master` already directly serves `scripts/zigux/install-zig.py`",
    "`PHASE2_TOOLCHAIN_NEXT_STEP=restore the remaining installer-backed helper now that the shared validator, direct Zig-version guard, dedicated pin-scope helper, and Linux-style Makefile routes are back on the lane branch`",
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
    CROSS_CHECKER_PATH,
    "scripts/zigux/check-genksyms-bridge.py",
    CROSS_FIXTURE_PATH,
    INSTALLER_PATH,
]

EXPECTED_MASTER_PRESENT_BRANCH_MISSING_FILES = [CROSS_CHECKER_PATH, CROSS_FIXTURE_PATH, INSTALLER_PATH]

EXPECTED_DOCS_ROOT_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
)

EXPECTED_TESTS_README_MARKERS = EXPECTED_DOCS_ROOT_MARKERS
EXPECTED_REVIEW_CHECKLIST_MARKERS = EXPECTED_DOCS_ROOT_MARKERS
EXPECTED_SCRIPTS_README_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/phase2-closure.md`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
)

EXPECTED_SELF_TEST_CASE_COUNT = 38


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def resolve_manifest_relpath(root: Path, relpath: str) -> Path:
    return root / Path(relpath)


def read_text(root: Path, path: Path) -> str:
    resolved = resolve_path(root, path)
    try:
        return resolved.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {resolved}") from exc


def read_manifest(root: Path) -> dict[str, object]:
    resolved = resolve_path(root, MANIFEST)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {resolved}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"manifest is not an object: {resolved}")
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

    closure_text = read_text(root, CLOSURE_DOC)
    bootstrap_notes_text = read_text(root, BOOTSTRAP_NOTES)
    docs_root_text = read_text(root, DOCS_ROOT_README)
    tests_readme_text = read_text(root, TESTS_README)
    review_checklist_text = read_text(root, REVIEW_CHECKLIST)
    scripts_readme_text = read_text(root, SCRIPTS_README)
    manifest = read_manifest(root)

    issues.extend(collect_missing_markers(closure_text, EXPECTED_DOC_MARKERS, "MISSING_CLOSURE_DOC_MARKERS"))
    issues.extend(
        collect_missing_markers(
            bootstrap_notes_text,
            EXPECTED_BOOTSTRAP_NOTES_MARKERS,
            "MISSING_BOOTSTRAP_NOTES_MARKERS",
        )
    )
    issues.extend(collect_missing_markers(docs_root_text, EXPECTED_DOCS_ROOT_MARKERS, "MISSING_DOCS_ROOT_MARKERS"))
    issues.extend(collect_missing_markers(tests_readme_text, EXPECTED_TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"))
    issues.extend(
        collect_missing_markers(
            review_checklist_text,
            EXPECTED_REVIEW_CHECKLIST_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            scripts_readme_text,
            EXPECTED_SCRIPTS_README_MARKERS,
            "MISSING_SCRIPTS_README_MARKERS",
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
    if manifest.get("toolchain_bootstrap_doc") != "Documentation/zigux/phase2-toolchain-bootstrap-notes.md":
        issues.append(("INVALID_MANIFEST_FIELD", "toolchain_bootstrap_doc"))
    if manifest.get("closure_validator") != "scripts/zigux/validate-phase2-closure.py":
        issues.append(("INVALID_MANIFEST_FIELD", "closure_validator"))
    if manifest.get("closure_doc") != "Documentation/zigux/phase2-closure.md":
        issues.append(("INVALID_MANIFEST_FIELD", "closure_doc"))
    if manifest.get("shared_validator") != "scripts/zigux/validate-phase2.py":
        issues.append(("INVALID_MANIFEST_FIELD", "shared_validator"))
    if manifest.get("tool_manifest_checker") != "scripts/zigux/check-phase2-tool-manifest-packets.py":
        issues.append(("INVALID_MANIFEST_FIELD", "tool_manifest_checker"))
    if manifest.get("makefile") != "zigux/Makefile":
        issues.append(("INVALID_MANIFEST_FIELD", "makefile"))
    if present_files != EXPECTED_PRESENT_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "present_files"))
    if missing_files != EXPECTED_MISSING_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "missing_files"))
    if master_present_branch_missing_files != EXPECTED_MASTER_PRESENT_BRANCH_MISSING_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "master_present_branch_missing_files"))
    if manifest.get("workflow_surface") != ".github/workflows/zigux-bootstrap.yml":
        issues.append(("INVALID_MANIFEST_FIELD", "workflow_surface"))

    present_set = set(present_files)
    missing_set = set(missing_files)
    overlap = sorted(present_set & missing_set)
    for relpath in overlap:
        issues.append(("MANIFEST_PATH_LIST_OVERLAP", relpath))

    for relpath in present_files:
        if not resolve_manifest_relpath(root, relpath).exists():
            issues.append(("PRESENT_FILE_MISSING_FROM_TREE", relpath))
    for relpath in missing_files:
        if resolve_manifest_relpath(root, relpath).exists():
            issues.append(("MISSING_FILE_PRESENT_IN_TREE", relpath))
    for relpath in master_present_branch_missing_files:
        if relpath in present_set:
            issues.append(("MASTER_PRESENT_PATH_MARKED_PRESENT", relpath))
        if resolve_manifest_relpath(root, relpath).exists():
            issues.append(("MASTER_BRANCH_MISSING_FILE_PRESENT_IN_TREE", relpath))
        if relpath not in missing_set:
            issues.append(("MASTER_PRESENT_PATH_NOT_MARKED_MISSING", relpath))

    if CROSS_CHECKER_PATH not in master_present_branch_missing_files:
        issues.append(("CROSS_CHECKER_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", CROSS_CHECKER_PATH))
    if CROSS_CHECKER_PATH not in missing_files:
        issues.append(("CROSS_CHECKER_NOT_MARKED_BRANCH_MISSING", CROSS_CHECKER_PATH))
    if CROSS_FIXTURE_PATH not in master_present_branch_missing_files:
        issues.append(("CROSS_FIXTURE_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", CROSS_FIXTURE_PATH))
    if CROSS_FIXTURE_PATH not in missing_files:
        issues.append(("CROSS_FIXTURE_NOT_MARKED_BRANCH_MISSING", CROSS_FIXTURE_PATH))
    if INSTALLER_PATH not in master_present_branch_missing_files:
        issues.append(("INSTALLER_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", INSTALLER_PATH))
    if INSTALLER_PATH not in missing_files:
        issues.append(("INSTALLER_NOT_MARKED_BRANCH_MISSING", INSTALLER_PATH))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_VALIDATION=fail")
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


def write_placeholder(root: Path, relpath: str) -> None:
    path = resolve_manifest_relpath(root, relpath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("present\n", encoding="utf-8")


def manifest_json(
    *,
    packet: str = "phase2_tool_manifest",
    phase: str = "phase2",
    status: str = "lane24_branch_closure_packet_restacked",
    toolchain_bootstrap_doc: str = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    closure_validator: str = "scripts/zigux/validate-phase2-closure.py",
    closure_doc: str = "Documentation/zigux/phase2-closure.md",
    shared_validator: str = "scripts/zigux/validate-phase2.py",
    tool_manifest_checker: str = "scripts/zigux/check-phase2-tool-manifest-packets.py",
    makefile: str = "zigux/Makefile",
    present_files: list[str] | object | None = None,
    missing_files: list[str] | object | None = None,
    master_present_branch_missing_files: list[str] | object | None = None,
    workflow_surface: str = ".github/workflows/zigux-bootstrap.yml",
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
    write_text(root, CLOSURE_DOC, "\n".join(EXPECTED_DOC_MARKERS) + "\n")
    write_text(root, BOOTSTRAP_NOTES, "\n".join(EXPECTED_BOOTSTRAP_NOTES_MARKERS) + "\n")
    write_text(root, DOCS_ROOT_README, "\n".join(EXPECTED_DOCS_ROOT_MARKERS) + "\n")
    write_text(root, TESTS_README, "\n".join(EXPECTED_TESTS_README_MARKERS) + "\n")
    write_text(root, REVIEW_CHECKLIST, "\n".join(EXPECTED_REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root, SCRIPTS_README, "\n".join(EXPECTED_SCRIPTS_README_MARKERS) + "\n")
    write_text(root, MANIFEST, manifest_json())
    for relpath in EXPECTED_PRESENT_FILES:
        if relpath == MANIFEST.relative_to(ROOT).as_posix():
            continue
        if resolve_manifest_relpath(root, relpath).exists():
            continue
        write_placeholder(root, relpath)


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for path, marker, code in (
            (CLOSURE_DOC, EXPECTED_DOC_MARKERS[0], "MISSING_CLOSURE_DOC_MARKERS"),
            (BOOTSTRAP_NOTES, EXPECTED_BOOTSTRAP_NOTES_MARKERS[0], "MISSING_BOOTSTRAP_NOTES_MARKERS"),
            (DOCS_ROOT_README, EXPECTED_DOCS_ROOT_MARKERS[0], "MISSING_DOCS_ROOT_MARKERS"),
            (TESTS_README, EXPECTED_TESTS_README_MARKERS[0], "MISSING_TESTS_README_MARKERS"),
            (REVIEW_CHECKLIST, EXPECTED_REVIEW_CHECKLIST_MARKERS[0], "MISSING_REVIEW_CHECKLIST_MARKERS"),
            (SCRIPTS_README, EXPECTED_SCRIPTS_README_MARKERS[0], "MISSING_SCRIPTS_README_MARKERS"),
        ):
            build_self_test_root(root)
            target = resolve_path(root, path)
            target.write_text(replace_once(target.read_text(encoding="utf-8"), marker), encoding="utf-8")
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
        write_text(root, MANIFEST, manifest_json(missing_files=[INSTALLER_PATH, 7]))
        assert ("INVALID_MANIFEST_FIELD", "missing_files") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(master_present_branch_missing_files=[INSTALLER_PATH, 7]))
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
        assert ("CROSS_CHECKER_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", CROSS_CHECKER_PATH) in issues
        assert ("CROSS_FIXTURE_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", CROSS_FIXTURE_PATH) in issues
        assert ("INSTALLER_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", INSTALLER_PATH) in issues
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(master_present_branch_missing_files=[CROSS_CHECKER_PATH, INSTALLER_PATH]))
        issues = collect_issues(root)
        assert ("INVALID_MANIFEST_FIELD", "master_present_branch_missing_files") in issues
        assert ("CROSS_FIXTURE_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", CROSS_FIXTURE_PATH) in issues
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(master_present_branch_missing_files=["scripts/zigux/check-phase2-toolchain-pin-scope.py"]))
        issues = collect_issues(root)
        assert ("INVALID_MANIFEST_FIELD", "master_present_branch_missing_files") in issues
        assert ("MASTER_PRESENT_PATH_MARKED_PRESENT", "scripts/zigux/check-phase2-toolchain-pin-scope.py") in issues
        assert ("MASTER_PRESENT_PATH_NOT_MARKED_MISSING", "scripts/zigux/check-phase2-toolchain-pin-scope.py") in issues
        assert ("CROSS_CHECKER_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", CROSS_CHECKER_PATH) in issues
        assert ("CROSS_FIXTURE_NOT_MARKED_MASTER_PRESENT_BRANCH_MISSING", CROSS_FIXTURE_PATH) in issues
        checks_run += 1

        build_self_test_root(root)
        resolve_manifest_relpath(root, EXPECTED_PRESENT_FILES[-1]).unlink()
        assert ("PRESENT_FILE_MISSING_FROM_TREE", EXPECTED_PRESENT_FILES[-1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_placeholder(root, EXPECTED_MISSING_FILES[0])
        assert ("MISSING_FILE_PRESENT_IN_TREE", EXPECTED_MISSING_FILES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_placeholder(root, INSTALLER_PATH)
        issues = collect_issues(root)
        assert ("MASTER_BRANCH_MISSING_FILE_PRESENT_IN_TREE", INSTALLER_PATH) in issues
        checks_run += 1

        build_self_test_root(root)
        write_placeholder(root, CROSS_FIXTURE_PATH)
        issues = collect_issues(root)
        assert ("MASTER_BRANCH_MISSING_FILE_PRESENT_IN_TREE", CROSS_FIXTURE_PATH) in issues
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
        resolve_path(root, MANIFEST).write_text("[]\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "manifest is not an object" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("non-object manifest did not abort")

        for path in (
            CLOSURE_DOC,
            BOOTSTRAP_NOTES,
            DOCS_ROOT_README,
            TESTS_README,
            REVIEW_CHECKLIST,
            SCRIPTS_README,
            MANIFEST,
        ):
            build_self_test_root(root)
            resolved = resolve_path(root, path)
            resolved.unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                assert str(resolved) in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing primary file did not abort: {path}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Lane 24 Phase 2 closure packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print(f"PHASE2_CLOSURE_PRESENT_FILE_COUNT={len(EXPECTED_PRESENT_FILES)}")
    print(f"PHASE2_CLOSURE_MISSING_FILE_COUNT={len(EXPECTED_MISSING_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
