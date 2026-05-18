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

EXPECTED_TOOLCHAIN_BOOTSTRAP_DOC = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
EXPECTED_CLOSURE_VALIDATOR = "scripts/zigux/validate-phase2-closure.py"
EXPECTED_CLOSURE_DOC = "Documentation/zigux/phase2-closure.md"
EXPECTED_SHARED_VALIDATOR = "scripts/zigux/validate-phase2.py"
EXPECTED_TOOL_MANIFEST_CHECKER = "scripts/zigux/check-phase2-tool-manifest-packets.py"
EXPECTED_MAKEFILE = "zigux/Makefile"
EXPECTED_WORKFLOW_SURFACE = ".github/workflows/zigux-bootstrap.yml"

EXPECTED_DOC_MARKERS = (
    "`PHASE2_STATUS=lane22-branch-restacked`",
    "`PHASE2_CLOSURE_VALIDATOR_GATE=python3 scripts/zigux/validate-phase2-closure.py`",
    "`PHASE2_TOOL_MANIFEST_CHECKER=scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "active Lane 22 draft review path",
    "`PHASE2_NEXT_STEP=restore one remaining broader helper packet at a time now that the closure note, bootstrap companion, shared validator, direct cross checker, dedicated kconfig README checker, dedicated toolchain pin-scope helper, manifest checker, and Linux-style Makefile routes are replayed together on the lane branch`",
)

EXPECTED_BOOTSTRAP_NOTES_MARKERS = (
    "shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`",
    "Linux-style cross route: `make -C zigux phase2-cross`",
    "the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin",
    "the shared and closure validators above are the fail-closed route that keeps this note in the bounded Phase 2 toolchain tranche instead of leaving it as stand-alone reference text",
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

EXPECTED_DOCS_ROOT_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
)

EXPECTED_TESTS_README_MARKERS = EXPECTED_DOCS_ROOT_MARKERS
EXPECTED_REVIEW_CHECKLIST_MARKERS = EXPECTED_DOCS_ROOT_MARKERS
EXPECTED_SCRIPTS_README_MARKERS = (
    "`check-phase2-cross.py`",
    "`check-phase2-tool-manifest-packets.py`",
    "`validate-phase2-closure.py`",
)

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

EXPECTED_SELF_TEST_CASE_COUNT = 40


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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


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
    for text, code in (
        (docs_root_text, "MISSING_DOCS_ROOT_MARKERS"),
    ):
        issues.extend(collect_missing_markers(text, EXPECTED_DOCS_ROOT_MARKERS, code))
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

    unexpected_fields = sorted(set(manifest) - EXPECTED_MANIFEST_FIELDS)
    if unexpected_fields:
        issues.extend(("UNEXPECTED_MANIFEST_FIELD", field) for field in unexpected_fields)

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
    if manifest.get("tool_manifest_checker") != EXPECTED_TOOL_MANIFEST_CHECKER:
        issues.append(("INVALID_MANIFEST_FIELD", "tool_manifest_checker"))
    if manifest.get("makefile") != EXPECTED_MAKEFILE:
        issues.append(("INVALID_MANIFEST_FIELD", "makefile"))
    if manifest.get("present_files") != EXPECTED_PRESENT_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "present_files"))
    if manifest.get("missing_files") != EXPECTED_MISSING_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "missing_files"))
    if manifest.get("master_present_branch_missing_files") != []:
        issues.append(("INVALID_MANIFEST_FIELD", "master_present_branch_missing_files"))
    if manifest.get("workflow_surface") != EXPECTED_WORKFLOW_SURFACE:
        issues.append(("INVALID_MANIFEST_FIELD", "workflow_surface"))

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


def manifest_json(*, present_files: list[str] | None = None, missing_files: list[str] | None = None) -> str:
    payload = {
        "packet": "phase2_tool_manifest",
        "phase": "phase2",
        "status": "lane22_branch_closure_packet_restacked",
        "toolchain_bootstrap_doc": EXPECTED_TOOLCHAIN_BOOTSTRAP_DOC,
        "closure_validator": EXPECTED_CLOSURE_VALIDATOR,
        "closure_doc": EXPECTED_CLOSURE_DOC,
        "shared_validator": EXPECTED_SHARED_VALIDATOR,
        "tool_manifest_checker": EXPECTED_TOOL_MANIFEST_CHECKER,
        "makefile": EXPECTED_MAKEFILE,
        "present_files": EXPECTED_PRESENT_FILES if present_files is None else present_files,
        "missing_files": EXPECTED_MISSING_FILES if missing_files is None else missing_files,
        "master_present_branch_missing_files": [],
        "workflow_surface": EXPECTED_WORKFLOW_SURFACE,
    }
    return json.dumps(payload, indent=2) + "\n"


def build_self_test_root(root: Path) -> None:
    write_text(root, CLOSURE_DOC, "\n".join(EXPECTED_DOC_MARKERS) + "\n")
    write_text(root, BOOTSTRAP_NOTES, "\n".join(EXPECTED_BOOTSTRAP_NOTES_MARKERS) + "\n")
    for path in (DOCS_ROOT_README, TESTS_README, REVIEW_CHECKLIST):
        write_text(root, path, "\n".join(EXPECTED_DOCS_ROOT_MARKERS) + "\n")
    write_text(root, SCRIPTS_README, "\n".join(EXPECTED_SCRIPTS_README_MARKERS) + "\n")
    write_text(root, MANIFEST, manifest_json())


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def assert_system_exit_contains(callback, expected_fragment: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        assert expected_fragment in str(exc), str(exc)
        return
    raise AssertionError(f"expected SystemExit containing: {expected_fragment}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validator_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for path, markers, code in (
            (CLOSURE_DOC, EXPECTED_DOC_MARKERS, "MISSING_CLOSURE_DOC_MARKERS"),
            (BOOTSTRAP_NOTES, EXPECTED_BOOTSTRAP_NOTES_MARKERS, "MISSING_BOOTSTRAP_NOTES_MARKERS"),
            (DOCS_ROOT_README, EXPECTED_DOCS_ROOT_MARKERS, "MISSING_DOCS_ROOT_MARKERS"),
            (TESTS_README, EXPECTED_TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"),
            (REVIEW_CHECKLIST, EXPECTED_REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"),
            (SCRIPTS_README, EXPECTED_SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"),
        ):
            for marker in markers:
                build_self_test_root(root)
                resolved = resolve_path(root, path)
                resolved.write_text(replace_once(resolved.read_text(encoding="utf-8"), marker), encoding="utf-8")
                assert (code, marker) in collect_issues(root)
                checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(present_files=EXPECTED_PRESENT_FILES[:-1]))
        assert ("INVALID_MANIFEST_FIELD", "present_files") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(missing_files=EXPECTED_MISSING_FILES[:-1]))
        assert ("INVALID_MANIFEST_FIELD", "missing_files") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["packet"] = "wrong"
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        assert ("INVALID_MANIFEST_FIELD", "packet") in collect_issues(root)
        checks_run += 1

        for field in (
            "phase",
            "status",
            "toolchain_bootstrap_doc",
            "closure_validator",
            "closure_doc",
            "shared_validator",
            "tool_manifest_checker",
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
        resolve_path(root, CLOSURE_DOC).unlink()
        assert_system_exit_contains(lambda: collect_issues(root), "required file missing:")
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
    print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Lane 22 Phase 2 closure packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print(f"PHASE2_CLOSURE_PRESENT_COUNT={len(EXPECTED_PRESENT_FILES)}")
    print(f"PHASE2_CLOSURE_MISSING_COUNT={len(EXPECTED_MISSING_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
