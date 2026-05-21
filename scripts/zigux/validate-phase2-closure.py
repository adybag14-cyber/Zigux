#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import tempfile
from pathlib import Path


_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) > 2 else _HERE.parent

CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
MAKEFILE_PATH = ROOT / "zigux" / "Makefile"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
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

EXPECTED_CLOSURE_GAP_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/install-zig.py`",
)

EXPECTED_BOOTSTRAP_NOTES_MARKERS = (
    "shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`",
    "Linux-style cross route: `make -C zigux phase2-cross`",
    "the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin",
    "the shared and closure validators above are the fail-closed route that keeps this note in the bounded Phase 2 toolchain tranche instead of leaving it as stand-alone reference text",
)

EXPECTED_BOOTSTRAP_GAP_MARKERS = (
    "workflow install path remains historical on this branch until `scripts/zigux/install-zig.py` is restored",
)

EXPECTED_WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/validate-phase2.py",
)

EXPECTED_MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-zig-toolchain.py --zig "$(ZIG)"',
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "phase2-validate: phase2-tools phase2-kconfig",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase2-closure.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py --self-test",
    "phase2-cross: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
    "phase2: phase2-validate phase2-cross",
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

EXPECTED_SELF_TEST_CASE_COUNT = 148


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
    except OSError as exc:
        raise SystemExit(f"required file unreadable: {resolved}") from exc


def read_manifest(root: Path) -> dict[str, object]:
    resolved = resolve_path(root, MANIFEST)
    try:
        raw = resolved.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {resolved}") from exc
    except OSError as exc:
        raise SystemExit(f"manifest is unreadable: {resolved}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"manifest is not valid json: {resolved}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"manifest is not an object: {resolved}")
    return payload


def probe_required_file(path: Path) -> None:
    with path.open("rb") as handle:
        handle.read(0)


def collect_marker_count_issues(
    text: str,
    markers: tuple[str, ...],
    *,
    missing_code: str,
    duplicate_code: str,
    exact_line: bool = False,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        if exact_line:
            count = sum(1 for line in text.splitlines() if line.strip() == marker)
        else:
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


def collect_non_string_manifest_entries(values: object, code: str) -> list[tuple[str, str]]:
    if not isinstance(values, list):
        return []
    return [(code, repr(value)) for value in values if not isinstance(value, str)]


def collect_branch_manifest_path_issues(
    root: Path,
    values: object,
    *,
    missing_code: str,
    unexpected_code: str,
    non_file_code: str = "",
    unreadable_code: str = "",
) -> list[tuple[str, str]]:
    if not isinstance(values, list):
        return []

    issues: list[tuple[str, str]] = []
    for value in values:
        if not isinstance(value, str):
            continue
        resolved = resolve_path(root, Path(value))
        if resolved.is_file():
            try:
                probe_required_file(resolved)
            except OSError:
                if unreadable_code:
                    issues.append((unreadable_code, value))
                elif unexpected_code:
                    issues.append((unexpected_code, value))
                continue
            if unexpected_code:
                issues.append((unexpected_code, value))
            continue
        if resolved.exists():
            if non_file_code:
                issues.append((non_file_code, value))
            elif unexpected_code:
                issues.append((unexpected_code, value))
            continue
        if missing_code:
            issues.append((missing_code, value))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    closure_text = read_text(root, CLOSURE_DOC)
    bootstrap_notes_text = read_text(root, BOOTSTRAP_NOTES)
    docs_root_text = read_text(root, DOCS_ROOT_README)
    tests_readme_text = read_text(root, TESTS_README)
    review_checklist_text = read_text(root, REVIEW_CHECKLIST)
    scripts_readme_text = read_text(root, SCRIPTS_README)
    workflow_text = read_text(root, WORKFLOW_PATH)
    makefile_text = read_text(root, MAKEFILE_PATH)
    manifest = read_manifest(root)

    issues.extend(
        collect_marker_count_issues(
            closure_text,
            EXPECTED_DOC_MARKERS,
            missing_code="MISSING_CLOSURE_DOC_MARKERS",
            duplicate_code="DUPLICATE_CLOSURE_DOC_MARKERS",
        )
    )
    issues.extend(
        collect_marker_count_issues(
            closure_text,
            EXPECTED_CLOSURE_GAP_MARKERS,
            missing_code="MISSING_CLOSURE_GAP_MARKERS",
            duplicate_code="DUPLICATE_CLOSURE_GAP_MARKERS",
        )
    )
    issues.extend(
        collect_marker_count_issues(
            bootstrap_notes_text,
            EXPECTED_BOOTSTRAP_NOTES_MARKERS,
            missing_code="MISSING_BOOTSTRAP_NOTES_MARKERS",
            duplicate_code="DUPLICATE_BOOTSTRAP_NOTES_MARKERS",
        )
    )
    issues.extend(
        collect_marker_count_issues(
            bootstrap_notes_text,
            EXPECTED_BOOTSTRAP_GAP_MARKERS,
            missing_code="MISSING_BOOTSTRAP_GAP_MARKERS",
            duplicate_code="DUPLICATE_BOOTSTRAP_GAP_MARKERS",
        )
    )
    issues.extend(
        collect_marker_count_issues(
            workflow_text,
            EXPECTED_WORKFLOW_MARKERS,
            missing_code="MISSING_WORKFLOW_MARKERS",
            duplicate_code="DUPLICATE_WORKFLOW_MARKERS",
            exact_line=True,
        )
    )
    issues.extend(
        collect_marker_count_issues(
            makefile_text,
            EXPECTED_MAKEFILE_MARKERS,
            missing_code="MISSING_MAKEFILE_MARKERS",
            duplicate_code="DUPLICATE_MAKEFILE_MARKERS",
            exact_line=True,
        )
    )
    issues.extend(
        collect_marker_count_issues(
            docs_root_text,
            EXPECTED_DOCS_ROOT_MARKERS,
            missing_code="MISSING_DOCS_ROOT_MARKERS",
            duplicate_code="DUPLICATE_DOCS_ROOT_MARKERS",
        )
    )
    issues.extend(
        collect_marker_count_issues(
            tests_readme_text,
            EXPECTED_TESTS_README_MARKERS,
            missing_code="MISSING_TESTS_README_MARKERS",
            duplicate_code="DUPLICATE_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_marker_count_issues(
            review_checklist_text,
            EXPECTED_REVIEW_CHECKLIST_MARKERS,
            missing_code="MISSING_REVIEW_CHECKLIST_MARKERS",
            duplicate_code="DUPLICATE_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(
        collect_marker_count_issues(
            scripts_readme_text,
            EXPECTED_SCRIPTS_README_MARKERS,
            missing_code="MISSING_SCRIPTS_README_MARKERS",
            duplicate_code="DUPLICATE_SCRIPTS_README_MARKERS",
        )
    )

    unexpected_fields = sorted(set(manifest) - EXPECTED_MANIFEST_FIELDS)
    if unexpected_fields:
        issues.extend(("UNEXPECTED_MANIFEST_FIELD", field) for field in unexpected_fields)

    present_files = manifest.get("present_files")
    missing_files = manifest.get("missing_files")
    master_present_branch_missing_files = manifest.get("master_present_branch_missing_files")

    if not isinstance(present_files, list):
        issues.append(("MANIFEST_FIELD_NOT_LIST", "present_files"))
    if not isinstance(missing_files, list):
        issues.append(("MANIFEST_FIELD_NOT_LIST", "missing_files"))
    if not isinstance(master_present_branch_missing_files, list):
        issues.append(("MANIFEST_FIELD_NOT_LIST", "master_present_branch_missing_files"))

    issues.extend(collect_non_string_manifest_entries(present_files, "NON_STRING_PRESENT_FILE_ENTRY"))
    issues.extend(collect_non_string_manifest_entries(missing_files, "NON_STRING_MISSING_FILE_ENTRY"))
    issues.extend(
        collect_non_string_manifest_entries(
            master_present_branch_missing_files,
            "NON_STRING_MASTER_PRESENT_BRANCH_MISSING_FILE_ENTRY",
        )
    )

    issues.extend(collect_duplicate_manifest_entries(present_files, "DUPLICATE_PRESENT_FILE_ENTRY"))
    issues.extend(collect_duplicate_manifest_entries(missing_files, "DUPLICATE_MISSING_FILE_ENTRY"))
    issues.extend(
        collect_duplicate_manifest_entries(
            master_present_branch_missing_files,
            "DUPLICATE_MASTER_PRESENT_BRANCH_MISSING_FILE_ENTRY",
        )
    )
    issues.extend(
        collect_branch_manifest_path_issues(
            root,
            present_files,
            missing_code="PRESENT_FILE_MISSING_ON_BRANCH",
            unexpected_code="",
            non_file_code="PRESENT_FILE_NOT_FILE_ON_BRANCH",
            unreadable_code="PRESENT_FILE_UNREADABLE_ON_BRANCH",
        )
    )
    issues.extend(
        collect_branch_manifest_path_issues(
            root,
            missing_files,
            missing_code="",
            unexpected_code="MISSING_FILE_ALREADY_PRESENT_ON_BRANCH",
            non_file_code="MISSING_FILE_NOT_FILE_ON_BRANCH",
        )
    )
    issues.extend(
        collect_branch_manifest_path_issues(
            root,
            master_present_branch_missing_files,
            missing_code="MASTER_PRESENT_BRANCH_PATH_NOT_MISSING_ON_BRANCH",
            unexpected_code="MASTER_PRESENT_BRANCH_PATH_ALREADY_PRESENT_ON_BRANCH",
            non_file_code="MASTER_PRESENT_BRANCH_PATH_NOT_FILE_ON_BRANCH",
        )
    )
    if isinstance(present_files, list) and isinstance(missing_files, list):
        present_set = {value for value in present_files if isinstance(value, str)}
        missing_set = {value for value in missing_files if isinstance(value, str)}
        issues.extend(
            ("MANIFEST_PATH_IN_BOTH_PRESENT_AND_MISSING", value)
            for value in sorted(present_set & missing_set)
        )
        if isinstance(master_present_branch_missing_files, list):
            master_present_set = {
                value for value in master_present_branch_missing_files if isinstance(value, str)
            }
            issues.extend(
                ("MASTER_PRESENT_BRANCH_PATH_ALREADY_PRESENT", value)
                for value in sorted(master_present_set & present_set)
            )
            issues.extend(
                ("MASTER_PRESENT_BRANCH_PATH_NOT_MARKED_MISSING", value)
                for value in sorted(master_present_set - missing_set)
            )

        if EXPECTED_TOOL_MANIFEST_CHECKER in missing_set:
            issues.append(("CHECKER_STILL_MARKED_MISSING", EXPECTED_TOOL_MANIFEST_CHECKER))
        if EXPECTED_TOOL_MANIFEST_CHECKER not in present_set:
            issues.append(("CHECKER_NOT_MARKED_PRESENT", EXPECTED_TOOL_MANIFEST_CHECKER))
        for shared_path in EXPECTED_SHARED_PRESENT_FILES:
            if shared_path in missing_set:
                issues.append(("SHARED_TOOL_STILL_MARKED_MISSING", shared_path))
            if shared_path not in present_set:
                issues.append(("SHARED_TOOL_NOT_MARKED_PRESENT", shared_path))

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


def run_validator(root: Path) -> int:
    try:
        issues = collect_issues(root)
    except SystemExit as exc:
        print("PHASE2_CLOSURE_VALIDATION=fail")
        print(f"PHASE2_CLOSURE_VALIDATION_NOTE={exc}")
        return 1
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print(f"PHASE2_CLOSURE_PRESENT_COUNT={len(EXPECTED_PRESENT_FILES)}")
    print(f"PHASE2_CLOSURE_MISSING_COUNT={len(EXPECTED_MISSING_FILES)}")
    return 0


def write_text(root: Path, path: Path, content: str) -> None:
    resolved = resolve_path(root, path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding="utf-8")


def manifest_json(
    *,
    present_files: object | None = None,
    missing_files: object | None = None,
    master_present_branch_missing_files: object | None = None,
) -> str:
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
        "master_present_branch_missing_files": (
            [] if master_present_branch_missing_files is None else master_present_branch_missing_files
        ),
        "workflow_surface": EXPECTED_WORKFLOW_SURFACE,
    }
    return json.dumps(payload, indent=2) + "\n"


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        CLOSURE_DOC,
        "\n".join((*EXPECTED_DOC_MARKERS, *EXPECTED_CLOSURE_GAP_MARKERS)) + "\n",
    )
    write_text(
        root,
        BOOTSTRAP_NOTES,
        "\n".join((*EXPECTED_BOOTSTRAP_NOTES_MARKERS, *EXPECTED_BOOTSTRAP_GAP_MARKERS)) + "\n",
    )
    write_text(root, WORKFLOW_PATH, "\n".join(EXPECTED_WORKFLOW_MARKERS) + "\n")
    write_text(root, MAKEFILE_PATH, "\n".join(EXPECTED_MAKEFILE_MARKERS) + "\n")
    for path in (DOCS_ROOT_README, TESTS_README, REVIEW_CHECKLIST):
        write_text(root, path, "\n".join(EXPECTED_DOCS_ROOT_MARKERS) + "\n")
    write_text(root, SCRIPTS_README, "\n".join(EXPECTED_SCRIPTS_README_MARKERS) + "\n")
    for rel_path in EXPECTED_PRESENT_FILES:
        target = Path(rel_path)
        resolved = resolve_path(root, target)
        if resolved.exists():
            continue
        placeholder = "# present\n" if target.suffix == ".py" else "present\n"
        write_text(root, target, placeholder)
    write_text(root, MANIFEST, manifest_json())


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def duplicate_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, f"{marker}\n{marker}", 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            if replacement:
                lines[index] = replacement
            else:
                del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def assert_system_exit_contains(callback, expected_fragment: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        assert expected_fragment in str(exc), str(exc)
        return
    raise AssertionError(f"expected SystemExit containing: {expected_fragment}")


def assert_run_validator_note_contains(root: Path, expected_fragment: str) -> None:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = run_validator(root)
    output = stdout.getvalue()
    assert exit_code == 1, output
    assert "PHASE2_CLOSURE_VALIDATION=fail" in output, output
    assert f"PHASE2_CLOSURE_VALIDATION_NOTE={expected_fragment}" in output, output


def assert_run_validator_output_contains(root: Path, expected_fragment: str) -> None:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = run_validator(root)
    output = stdout.getvalue()
    assert exit_code == 1, output
    assert "PHASE2_CLOSURE_VALIDATION=fail" in output, output
    assert expected_fragment in output, output


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validator_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for path, markers, missing_code, duplicate_code, exact_line in (
            (
                CLOSURE_DOC,
                EXPECTED_DOC_MARKERS,
                "MISSING_CLOSURE_DOC_MARKERS",
                "DUPLICATE_CLOSURE_DOC_MARKERS",
                False,
            ),
            (
                CLOSURE_DOC,
                EXPECTED_CLOSURE_GAP_MARKERS,
                "MISSING_CLOSURE_GAP_MARKERS",
                "DUPLICATE_CLOSURE_GAP_MARKERS",
                False,
            ),
            (
                BOOTSTRAP_NOTES,
                EXPECTED_BOOTSTRAP_NOTES_MARKERS,
                "MISSING_BOOTSTRAP_NOTES_MARKERS",
                "DUPLICATE_BOOTSTRAP_NOTES_MARKERS",
                False,
            ),
            (
                BOOTSTRAP_NOTES,
                EXPECTED_BOOTSTRAP_GAP_MARKERS,
                "MISSING_BOOTSTRAP_GAP_MARKERS",
                "DUPLICATE_BOOTSTRAP_GAP_MARKERS",
                False,
            ),
            (
                WORKFLOW_PATH,
                EXPECTED_WORKFLOW_MARKERS,
                "MISSING_WORKFLOW_MARKERS",
                "DUPLICATE_WORKFLOW_MARKERS",
                True,
            ),
            (
                MAKEFILE_PATH,
                EXPECTED_MAKEFILE_MARKERS,
                "MISSING_MAKEFILE_MARKERS",
                "DUPLICATE_MAKEFILE_MARKERS",
                True,
            ),
            (
                DOCS_ROOT_README,
                EXPECTED_DOCS_ROOT_MARKERS,
                "MISSING_DOCS_ROOT_MARKERS",
                "DUPLICATE_DOCS_ROOT_MARKERS",
                False,
            ),
            (
                TESTS_README,
                EXPECTED_TESTS_README_MARKERS,
                "MISSING_TESTS_README_MARKERS",
                "DUPLICATE_TESTS_README_MARKERS",
                False,
            ),
            (
                REVIEW_CHECKLIST,
                EXPECTED_REVIEW_CHECKLIST_MARKERS,
                "MISSING_REVIEW_CHECKLIST_MARKERS",
                "DUPLICATE_REVIEW_CHECKLIST_MARKERS",
                False,
            ),
            (
                SCRIPTS_README,
                EXPECTED_SCRIPTS_README_MARKERS,
                "MISSING_SCRIPTS_README_MARKERS",
                "DUPLICATE_SCRIPTS_README_MARKERS",
                False,
            ),
        ):
            for marker in markers:
                build_self_test_root(root)
                resolved = resolve_path(root, path)
                source = resolved.read_text(encoding="utf-8")
                if exact_line:
                    resolved.write_text(replace_exact_line(source, marker), encoding="utf-8")
                else:
                    resolved.write_text(replace_once(source, marker), encoding="utf-8")
                assert (missing_code, marker) in collect_issues(root)
                checks_run += 1

                build_self_test_root(root)
                resolved = resolve_path(root, path)
                source = resolved.read_text(encoding="utf-8")
                if exact_line:
                    resolved.write_text(duplicate_exact_line(source, marker), encoding="utf-8")
                else:
                    resolved.write_text(duplicate_once(source, marker), encoding="utf-8")
                assert (duplicate_code, f"{marker}:count=2") in collect_issues(root)
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
        assert_run_validator_output_contains(root, "UNEXPECTED_MANIFEST_FIELD_START")
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
        bad["master_present_branch_missing_files"] = ["scripts/zigux/install-zig.py", "scripts/zigux/install-zig.py"]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        assert (
            "DUPLICATE_MASTER_PRESENT_BRANCH_MISSING_FILE_ENTRY",
            "scripts/zigux/install-zig.py:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["master_present_branch_missing_files"] = [EXPECTED_PRESENT_FILES[0]]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        assert ("MASTER_PRESENT_BRANCH_PATH_ALREADY_PRESENT", EXPECTED_PRESENT_FILES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["master_present_branch_missing_files"] = ["scripts/zigux/not-in-missing.py"]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MASTER_PRESENT_BRANCH_PATH_NOT_MARKED_MISSING", "scripts/zigux/not-in-missing.py") in issues
        assert ("MASTER_PRESENT_BRANCH_PATH_NOT_MISSING_ON_BRANCH", "scripts/zigux/not-in-missing.py") in issues
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["missing_files"] = EXPECTED_MISSING_FILES + [EXPECTED_PRESENT_FILES[0]]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MANIFEST_PATH_IN_BOTH_PRESENT_AND_MISSING", EXPECTED_PRESENT_FILES[0]) in issues
        assert ("MISSING_FILE_ALREADY_PRESENT_ON_BRANCH", EXPECTED_PRESENT_FILES[0]) in issues
        checks_run += 1
        assert_run_validator_output_contains(root, "MANIFEST_PATH_IN_BOTH_PRESENT_AND_MISSING_START")
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, Path(EXPECTED_PRESENT_FILES[-1])).unlink()
        assert ("PRESENT_FILE_MISSING_ON_BRANCH", EXPECTED_PRESENT_FILES[-1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        present_dir = resolve_path(root, Path(EXPECTED_PRESENT_FILES[-1]))
        present_dir.unlink()
        present_dir.mkdir()
        assert ("PRESENT_FILE_NOT_FILE_ON_BRANCH", EXPECTED_PRESENT_FILES[-1]) in collect_issues(root)
        checks_run += 1
        assert_run_validator_output_contains(root, "PRESENT_FILE_NOT_FILE_ON_BRANCH_START")
        checks_run += 1
        present_dir.rmdir()

        build_self_test_root(root)
        write_text(root, Path(EXPECTED_MISSING_FILES[0]), "# restored on branch\n")
        assert ("MISSING_FILE_ALREADY_PRESENT_ON_BRANCH", EXPECTED_MISSING_FILES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        missing_dir = resolve_path(root, Path(EXPECTED_MISSING_FILES[0]))
        if missing_dir.exists():
            if missing_dir.is_dir():
                missing_dir.rmdir()
            else:
                missing_dir.unlink()
        missing_dir.parent.mkdir(parents=True, exist_ok=True)
        missing_dir.mkdir()
        assert ("MISSING_FILE_NOT_FILE_ON_BRANCH", EXPECTED_MISSING_FILES[0]) in collect_issues(root)
        checks_run += 1
        assert_run_validator_output_contains(root, "MISSING_FILE_NOT_FILE_ON_BRANCH_START")
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["missing_files"] = EXPECTED_MISSING_FILES + [EXPECTED_TOOL_MANIFEST_CHECKER]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        assert ("CHECKER_STILL_MARKED_MISSING", EXPECTED_TOOL_MANIFEST_CHECKER) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["present_files"] = [path for path in EXPECTED_PRESENT_FILES if path != EXPECTED_TOOL_MANIFEST_CHECKER]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        assert ("CHECKER_NOT_MARKED_PRESENT", EXPECTED_TOOL_MANIFEST_CHECKER) in collect_issues(root)
        checks_run += 1

        for shared_path in EXPECTED_SHARED_PRESENT_FILES:
            build_self_test_root(root)
            bad = json.loads(manifest_json())
            bad["missing_files"] = EXPECTED_MISSING_FILES + [shared_path]
            write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
            assert ("SHARED_TOOL_STILL_MARKED_MISSING", shared_path) in collect_issues(root)
            checks_run += 1

            build_self_test_root(root)
            bad = json.loads(manifest_json())
            bad["present_files"] = [path for path in EXPECTED_PRESENT_FILES if path != shared_path]
            write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
            assert ("SHARED_TOOL_NOT_MARKED_PRESENT", shared_path) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(present_files="wrong"))
        issues = collect_issues(root)
        assert ("MANIFEST_FIELD_NOT_LIST", "present_files") in issues
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(missing_files="wrong"))
        issues = collect_issues(root)
        assert ("MANIFEST_FIELD_NOT_LIST", "missing_files") in issues
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, manifest_json(master_present_branch_missing_files="wrong"))
        issues = collect_issues(root)
        assert ("MANIFEST_FIELD_NOT_LIST", "master_present_branch_missing_files") in issues
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["present_files"] = [EXPECTED_PRESENT_FILES[0], 7]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("NON_STRING_PRESENT_FILE_ENTRY", "7") in issues
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["missing_files"] = [EXPECTED_MISSING_FILES[0], 7]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("NON_STRING_MISSING_FILE_ENTRY", "7") in issues
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["master_present_branch_missing_files"] = [7]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("NON_STRING_MASTER_PRESENT_BRANCH_MISSING_FILE_ENTRY", "7") in issues
        checks_run += 1

        build_self_test_root(root)
        bad = json.loads(manifest_json())
        bad["master_present_branch_missing_files"] = [EXPECTED_MISSING_FILES[0]]
        write_text(root, MANIFEST, json.dumps(bad, indent=2) + "\n")
        master_missing_dir = resolve_path(root, Path(EXPECTED_MISSING_FILES[0]))
        if master_missing_dir.exists():
            if master_missing_dir.is_dir():
                master_missing_dir.rmdir()
            else:
                master_missing_dir.unlink()
        master_missing_dir.parent.mkdir(parents=True, exist_ok=True)
        master_missing_dir.mkdir()
        assert (
            "MASTER_PRESENT_BRANCH_PATH_NOT_FILE_ON_BRANCH",
            EXPECTED_MISSING_FILES[0],
        ) in collect_issues(root)
        checks_run += 1

        original_probe_required_file = globals()["probe_required_file"]
        try:
            build_self_test_root(root)

            def fail_present_probe(path: Path) -> None:
                if path == resolve_path(root, Path(EXPECTED_PRESENT_FILES[-1])):
                    raise OSError("simulated unreadable present file")
                original_probe_required_file(path)

            globals()["probe_required_file"] = fail_present_probe
            assert (
                "PRESENT_FILE_UNREADABLE_ON_BRANCH",
                EXPECTED_PRESENT_FILES[-1],
            ) in collect_issues(root)
            checks_run += 1
            assert_run_validator_output_contains(root, "PRESENT_FILE_UNREADABLE_ON_BRANCH_START")
            checks_run += 1

        finally:
            globals()["probe_required_file"] = original_probe_required_file

        for path in (
            CLOSURE_DOC,
            BOOTSTRAP_NOTES,
            DOCS_ROOT_README,
            REVIEW_CHECKLIST,
            SCRIPTS_README,
            TESTS_README,
            MAKEFILE_PATH,
            WORKFLOW_PATH,
        ):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            assert_run_validator_note_contains(root, "required file missing:")
            checks_run += 1

            build_self_test_root(root)
            unreadable = resolve_path(root, path)
            unreadable.unlink()
            unreadable.mkdir(parents=True)
            assert_run_validator_note_contains(root, "required file unreadable:")
            unreadable.rmdir()
            checks_run += 1

        build_self_test_root(root)
        resolve_path(root, MANIFEST).unlink()
        assert_run_validator_note_contains(root, "required file missing:")
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, MANIFEST).unlink()
        resolve_path(root, MANIFEST).mkdir(parents=True)
        assert_run_validator_note_contains(root, "manifest is unreadable:")
        resolve_path(root, MANIFEST).rmdir()
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, "{\n")
        assert_run_validator_note_contains(root, "manifest is not valid json:")
        checks_run += 1

        build_self_test_root(root)
        write_text(root, MANIFEST, "[]\n")
        assert_run_validator_note_contains(root, "manifest is not an object:")
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

    return run_validator(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
