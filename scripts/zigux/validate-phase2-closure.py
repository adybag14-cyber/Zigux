#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

EXPECTED_DOC_MARKERS = (
    "`PHASE2_STATUS=current-master-safe`",
    "`PHASE2_CLOSURE_ROUTE_STATUS=partial`",
    "`PHASE2_CLOSURE_VALIDATOR_SELF_TEST=python3 scripts/zigux/validate-phase2-closure.py --self-test`",
    "`PHASE2_CLOSURE_VALIDATOR_GATE=python3 scripts/zigux/validate-phase2-closure.py`",
    "`PHASE2_TOOL_MANIFEST=zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/check-phase2-tool-manifest-packets.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-kconfig-readme-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/install-zig.py`",
    "`zigux/Makefile`",
    "`PHASE2_NEXT_STEP=restore the missing toolchain and shared-validator companions one bounded packet at a time, starting with the dedicated Phase 2 bootstrap note plus the shared validator or the Makefile route set, instead of widening this lane into a speculative full replay`",
)

EXPECTED_PRESENT_FILES = [
    "Documentation/zigux/phase2-closure.md",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
]

EXPECTED_MISSING_FILES = [
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-kconfig-readme-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/genksyms.zig",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/install-zig.py",
    "zigux/Makefile",
]

EXPECTED_DOCS_ROOT_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
)

EXPECTED_TESTS_README_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
)

EXPECTED_REVIEW_CHECKLIST_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
)

EXPECTED_SCRIPTS_README_MARKERS = (
    "`Documentation/zigux/phase2-closure.md`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
)

EXPECTED_SELF_TEST_CASE_COUNT = 18


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
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {resolved}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"manifest is not an object: {resolved}")
    return payload


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    closure_text = read_text(root, CLOSURE_DOC)
    docs_root_text = read_text(root, DOCS_ROOT_README)
    tests_readme_text = read_text(root, TESTS_README)
    review_checklist_text = read_text(root, REVIEW_CHECKLIST)
    scripts_readme_text = read_text(root, SCRIPTS_README)
    manifest = read_manifest(root)

    issues.extend(collect_missing_markers(closure_text, EXPECTED_DOC_MARKERS, "MISSING_CLOSURE_DOC_MARKERS"))
    issues.extend(
        collect_missing_markers(docs_root_text, EXPECTED_DOCS_ROOT_MARKERS, "MISSING_DOCS_ROOT_MARKERS")
    )
    issues.extend(
        collect_missing_markers(tests_readme_text, EXPECTED_TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS")
    )
    issues.extend(
        collect_missing_markers(
            review_checklist_text,
            EXPECTED_REVIEW_CHECKLIST_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            scripts_readme_text, EXPECTED_SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"
        )
    )

    if manifest.get("packet") != "phase2_tool_manifest":
        issues.append(("INVALID_MANIFEST_FIELD", "packet"))
    if manifest.get("phase") != "phase2":
        issues.append(("INVALID_MANIFEST_FIELD", "phase"))
    if manifest.get("status") != "current_master_safe_closure_anchor":
        issues.append(("INVALID_MANIFEST_FIELD", "status"))
    if manifest.get("closure_validator") != "scripts/zigux/validate-phase2-closure.py":
        issues.append(("INVALID_MANIFEST_FIELD", "closure_validator"))
    if manifest.get("closure_doc") != "Documentation/zigux/phase2-closure.md":
        issues.append(("INVALID_MANIFEST_FIELD", "closure_doc"))
    if manifest.get("present_files") != EXPECTED_PRESENT_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "present_files"))
    if manifest.get("missing_files") != EXPECTED_MISSING_FILES:
        issues.append(("INVALID_MANIFEST_FIELD", "missing_files"))
    if manifest.get("workflow_surface") != ".github/workflows/zigux-bootstrap.yml":
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


def manifest_json(
    *,
    packet: str = "phase2_tool_manifest",
    phase: str = "phase2",
    status: str = "current_master_safe_closure_anchor",
    closure_validator: str = "scripts/zigux/validate-phase2-closure.py",
    closure_doc: str = "Documentation/zigux/phase2-closure.md",
    present_files: list[str] | None = None,
    missing_files: list[str] | None = None,
    workflow_routes: list[str] | None = None,
) -> str:
    payload = {
        "packet": packet,
        "phase": phase,
        "status": status,
        "closure_validator": closure_validator,
        "closure_doc": closure_doc,
        "present_files": EXPECTED_PRESENT_FILES if present_files is None else present_files,
        "missing_files": EXPECTED_MISSING_FILES if missing_files is None else missing_files,
        "workflow_surface": ".github/workflows/zigux-bootstrap.yml",
    }
    return json.dumps(payload, indent=2) + "\n"


def build_self_test_root(root: Path) -> None:
    write_text(root, CLOSURE_DOC, "\n".join(EXPECTED_DOC_MARKERS) + "\n")
    write_text(root, DOCS_ROOT_README, "\n".join(EXPECTED_DOCS_ROOT_MARKERS) + "\n")
    write_text(root, TESTS_README, "\n".join(EXPECTED_TESTS_README_MARKERS) + "\n")
    write_text(root, REVIEW_CHECKLIST, "\n".join(EXPECTED_REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root, SCRIPTS_README, "\n".join(EXPECTED_SCRIPTS_README_MARKERS) + "\n")
    write_text(root, MANIFEST, manifest_json())


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

        build_self_test_root(root)
        path = resolve_path(root, CLOSURE_DOC)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), EXPECTED_DOC_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_CLOSURE_DOC_MARKERS", EXPECTED_DOC_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CLOSURE_DOC)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), EXPECTED_DOC_MARKERS[15]), encoding="utf-8")
        assert ("MISSING_CLOSURE_DOC_MARKERS", EXPECTED_DOC_MARKERS[15]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, DOCS_ROOT_README)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), EXPECTED_DOCS_ROOT_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_DOCS_ROOT_MARKERS", EXPECTED_DOCS_ROOT_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TESTS_README)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), EXPECTED_TESTS_README_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_TESTS_README_MARKERS", EXPECTED_TESTS_README_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, REVIEW_CHECKLIST)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), EXPECTED_REVIEW_CHECKLIST_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_REVIEW_CHECKLIST_MARKERS", EXPECTED_REVIEW_CHECKLIST_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, SCRIPTS_README)
        path.writeText(
            replace_once(path.read_text(encoding="utf-8"), EXPECTED_SCRIPTS_README_MARKERS[0]),
            encoding="utf-8",
        )
        assert ("MISSING_SCRIPTS_README_MARKERS", EXPECTED_SCRIPTS_README_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(packet="not_phase2_tool_manifest"))
        assert ("INVALID_MANIFEST_FIELD", "packet") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(phase="Phase 2"))
        assert ("INVALID_MANIFEST_FIELD", "phase") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(status="partial"))
        assert ("INVALID_MANIFEST_FIELD", "status") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(closure_validator="scripts/zigux/other.py"))
        assert ("INVALID_MANIFEST_FIELD", "closure_validator") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(closure_doc="Documentation/zigux/other.md"))
        assert ("INVALID_MANIFEST_FIELD", "closure_doc") in collect_issues(root)
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
        write_text(root, MANIFEST, json.dumps({**json.loads(manifest_json()), "workflow_surface": "wrong"}, indent=2) + "\n")
        assert ("INVALID_MANIFEST_FIELD", "workflow_surface") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, "[]\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "manifest is not an object" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("non-object manifest did not abort")

        build_self_test_root(root)
        resolve_path(root, CLOSURE_DOC).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing closure doc did not abort")

        build_self_test_root(root)
        resolve_path(root, MANIFEST).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing manifest did not abort")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the bounded current-master-safe Phase 2 closure packet."
    )
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
