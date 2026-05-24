#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
MAKEFILE = Path("zigux/Makefile")

MANIFEST_BOOTSTRAP_HELPERS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
)

MANIFEST_CHECKERS = (
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
)

MANIFEST_BRIDGE_HELPERS = (
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
)

MANIFEST_NOTE_MARKERS = (
    "the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs",
    "Keep the returned install-zig archive verification checker, staged pinned-archive helper, and the stage-helper contract plus selftest packet explicit beside the local-first archive workflow, archive README contract, and installer helper so the shared Phase 2 tool packet matches the live phase2-toolchain and validate-phase2 routes.",
    "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker plus primary artifact_diff helper explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
)

PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test`",
    "`python3 scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`",
    "`python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test`",
    "`python3 scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`",
    "`python3 scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
)

PHASE2_CLOSURE_MARKERS = (
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "direct standalone genksyms invalid-long-option and ambiguous-long-option version-side-effect proofs",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
)

MAKEFILE_MARKERS = (
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "phase2-genksyms:",
    "phase2-fixdep:",
)

MAKEFILE_EXACT_LINE_MARKERS = (
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_count_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_exact_line_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker + "\n")
        if count != 1:
            issues.append((code, f"{count}::{marker}"))
    return issues


def collect_manifest_entry_issues(entries: object, required: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    if not isinstance(entries, list):
        return [(code, "missing-list")]
    values = [entry for entry in entries if isinstance(entry, str)]
    issues: list[tuple[str, str]] = []
    for marker in required:
        if marker not in values:
            issues.append((code, marker))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    manifest = read_json(resolve_path(root, MANIFEST))
    notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    makefile_text = read_text(resolve_path(root, MAKEFILE))

    if manifest.get("phase") != "Phase 2":
        issues.append(("MANIFEST_TOP_LEVEL_MISMATCH", "phase"))

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("MANIFEST_PRESENT_SURFACES_MISSING", "present_surfaces"))
    else:
        issues.extend(
            collect_manifest_entry_issues(
                present_surfaces.get("bootstrap_helpers"),
                MANIFEST_BOOTSTRAP_HELPERS,
                "MANIFEST_BOOTSTRAP_HELPERS_MISSING",
            )
        )
        issues.extend(
            collect_manifest_entry_issues(
                present_surfaces.get("checkers"),
                MANIFEST_CHECKERS,
                "MANIFEST_CHECKERS_MISSING",
            )
        )
        issues.extend(
            collect_manifest_entry_issues(
                present_surfaces.get("bridge_helpers"),
                MANIFEST_BRIDGE_HELPERS,
                "MANIFEST_BRIDGE_HELPERS_MISSING",
            )
        )

    manifest_notes = manifest.get("notes")
    if not isinstance(manifest_notes, list):
        issues.append(("MANIFEST_NOTES_MISSING", "notes"))
    else:
        note_values = [entry for entry in manifest_notes if isinstance(entry, str)]
        for marker in MANIFEST_NOTE_MARKERS:
            if marker not in note_values:
                issues.append(("MANIFEST_NOTE_MARKERS_MISSING", marker))

    issues.extend(
        collect_missing_markers(
            notes_text,
            PHASE2_NOTES_MARKERS,
            "PHASE2_NOTES_MARKERS_MISSING",
        )
    )
    issues.extend(
        collect_missing_markers(
            closure_text,
            PHASE2_CLOSURE_MARKERS,
            "PHASE2_CLOSURE_MARKERS_MISSING",
        )
    )
    issues.extend(
        collect_missing_markers(
            makefile_text,
            MAKEFILE_MARKERS,
            "MAKEFILE_MARKERS_MISSING",
        )
    )
    issues.extend(
        collect_exact_line_markers(
            makefile_text,
            MAKEFILE_EXACT_LINE_MARKERS,
            "MAKEFILE_EXACT_LINE_MARKERS",
        )
    )
    issues.extend(
        collect_exact_count_markers(
            notes_text,
            (
                "the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs",
                "`python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test`",
                "`python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`",
            ),
            "PHASE2_NOTES_MARKERS_EXACT_COUNT",
        )
    )
    issues.extend(
        collect_exact_count_markers(
            closure_text,
            (
                "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
                "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
            ),
            "PHASE2_CLOSURE_MARKERS_EXACT_COUNT",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOL_MANIFEST_STAGE_GENKSYMS_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, content: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_json(
        resolve_path(root, MANIFEST),
        {
            "phase": "Phase 2",
            "present_surfaces": {
                "bootstrap_helpers": list(MANIFEST_BOOTSTRAP_HELPERS),
                "checkers": list(MANIFEST_CHECKERS),
                "bridge_helpers": list(MANIFEST_BRIDGE_HELPERS),
            },
            "notes": list(MANIFEST_NOTE_MARKERS),
        },
    )
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, PHASE2_CLOSURE), "\n".join(PHASE2_CLOSURE_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join((*MAKEFILE_MARKERS, *MAKEFILE_EXACT_LINE_MARKERS)) + "\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + 1
        + len(MANIFEST_BOOTSTRAP_HELPERS)
        + len(MANIFEST_CHECKERS)
        + len(MANIFEST_BRIDGE_HELPERS)
        + len(MANIFEST_NOTE_MARKERS)
        + len(PHASE2_NOTES_MARKERS)
        + len(PHASE2_CLOSURE_MARKERS)
        + len(MAKEFILE_MARKERS)
        + len(MAKEFILE_EXACT_LINE_MARKERS)
        + 3
        + 2
        + 4
    )
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tool_manifest_stage_genksyms_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        manifest = read_json(resolve_path(root, MANIFEST))
        manifest["phase"] = "broken"
        write_json(resolve_path(root, MANIFEST), manifest)
        assert ("MANIFEST_TOP_LEVEL_MISMATCH", "phase") in collect_issues(root)
        checks_run += 1

        for key, markers in (
            ("bootstrap_helpers", MANIFEST_BOOTSTRAP_HELPERS),
            ("checkers", MANIFEST_CHECKERS),
            ("bridge_helpers", MANIFEST_BRIDGE_HELPERS),
        ):
            for marker in markers:
                build_sample_root(root)
                manifest = read_json(resolve_path(root, MANIFEST))
                manifest["present_surfaces"][key].remove(marker)
                write_json(resolve_path(root, MANIFEST), manifest)
                assert (f"MANIFEST_{key.upper()}_MISSING", marker) in collect_issues(root)
                checks_run += 1

        for marker in MANIFEST_NOTE_MARKERS:
            build_sample_root(root)
            manifest = read_json(resolve_path(root, MANIFEST))
            manifest["notes"].remove(marker)
            write_json(resolve_path(root, MANIFEST), manifest)
            assert ("MANIFEST_NOTE_MARKERS_MISSING", marker) in collect_issues(root)
            checks_run += 1

        for marker in PHASE2_NOTES_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, PHASE2_NOTES)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("PHASE2_NOTES_MARKERS_MISSING", marker) in collect_issues(root)
            checks_run += 1

        for marker in PHASE2_CLOSURE_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, PHASE2_CLOSURE)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("PHASE2_CLOSURE_MARKERS_MISSING", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(path.read_text(encoding="utf-8").replace(marker + "\n", "", 1), encoding="utf-8")
            assert ("MAKEFILE_MARKERS_MISSING", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_EXACT_LINE_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(path.read_text(encoding="utf-8").replace(marker + "\n", "", 1), encoding="utf-8")
            assert ("MAKEFILE_EXACT_LINE_MARKERS", f"0::{marker}") in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, PHASE2_NOTES)
        marker = "the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs"
        path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
        assert ("PHASE2_NOTES_MARKERS_EXACT_COUNT", f"2::{marker}") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, PHASE2_NOTES)
        marker = "`python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test`"
        path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
        assert ("PHASE2_NOTES_MARKERS_EXACT_COUNT", f"2::{marker}") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        path = resolve_path(root, PHASE2_NOTES)
        marker = "`python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`"
        path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
        assert ("PHASE2_NOTES_MARKERS_EXACT_COUNT", f"2::{marker}") in collect_issues(root)
        checks_run += 1

        for marker in (
            "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
            "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
        ):
            build_sample_root(root)
            path = resolve_path(root, PHASE2_CLOSURE)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            assert ("PHASE2_CLOSURE_MARKERS_EXACT_COUNT", f"2::{marker}") in collect_issues(root)
            checks_run += 1

        for rel_path in (MANIFEST, PHASE2_NOTES, PHASE2_CLOSURE, MAKEFILE):
            build_sample_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_TOOL_MANIFEST_STAGE_GENKSYMS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOL_MANIFEST_STAGE_GENKSYMS_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard the rematerialized staged-archive and genksyms version-proof packet inside the Phase 2 tool manifest family."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root for focused replay")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_TOOL_MANIFEST_STAGE_GENKSYMS_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOL_MANIFEST_STAGE_GENKSYMS_PACKET=pass")
    print(
        "PHASE2_TOOL_MANIFEST_STAGE_GENKSYMS_PACKET_MARKER_COUNT="
        f"{len(MANIFEST_BOOTSTRAP_HELPERS) + len(MANIFEST_CHECKERS) + len(MANIFEST_BRIDGE_HELPERS) + len(MANIFEST_NOTE_MARKERS) + len(PHASE2_NOTES_MARKERS) + len(PHASE2_CLOSURE_MARKERS) + len(MAKEFILE_MARKERS) + len(MAKEFILE_EXACT_LINE_MARKERS)}"
    )
    print("PHASE2_TOOL_MANIFEST_STAGE_GENKSYMS_PACKET_EXACT_COUNT_MARKER_COUNT=8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
