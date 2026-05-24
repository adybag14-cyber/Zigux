#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
THIRD_PARTY_README = Path("third_party/README.md")
PHASE2_TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
MAKEFILE = Path("zigux/Makefile")

PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
)

THIRD_PARTY_README_MARKERS = (
    "file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the archive-verification, staged-helper contract, and staged-helper self-test packet explicit beside that same local-first archive path.",
)

PHASE2_CLOSURE_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "phase2-genksyms:",
    "phase2-fixdep:",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

MANIFEST_BOOTSTRAP_HELPERS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
)

MANIFEST_ARCHIVE_SUPPORT = (
    "third_party/README.md",
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
)

MANIFEST_CHECKERS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
)

MANIFEST_MAKE_WRAPPERS = (
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)

MANIFEST_CLOSURE_NOTES = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
)


def read_text(root: Path, rel_path: Path) -> str:
    path = root / rel_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(root: Path, rel_path: Path) -> dict[str, object]:
    path = root / rel_path
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"required json has invalid top-level shape: {path}")
    return payload


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def require_string_list(
    issues: list[tuple[str, str]],
    present_surfaces: dict[str, object],
    key: str,
) -> list[str] | None:
    value = present_surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(entry, str) for entry in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return value


def require_manifest_members(
    issues: list[tuple[str, str]],
    values: list[str] | None,
    required: tuple[str, ...],
    code: str,
) -> None:
    if values is None:
        return
    for marker in required:
        if marker not in values:
            issues.append((code, marker))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    phase2_notes_text = read_text(root, PHASE2_NOTES)
    third_party_readme_text = read_text(root, THIRD_PARTY_README)
    phase2_closure_text = read_text(root, PHASE2_CLOSURE)
    makefile_text = read_text(root, MAKEFILE)
    manifest = read_json(root, PHASE2_TOOL_MANIFEST)

    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_markers(phase2_notes_text, PHASE2_NOTES_MARKERS, "MISSING_PHASE2_NOTES_MARKER"))
    issues.extend(collect_missing_markers(third_party_readme_text, THIRD_PARTY_README_MARKERS, "MISSING_THIRD_PARTY_README_MARKER"))
    issues.extend(collect_missing_markers(phase2_closure_text, PHASE2_CLOSURE_MARKERS, "MISSING_PHASE2_CLOSURE_MARKER"))
    issues.extend(collect_missing_markers(makefile_text, MAKEFILE_MARKERS, "MISSING_MAKEFILE_MARKER"))

    if manifest.get("phase") != "Phase 2":
        issues.append(("INVALID_MANIFEST_PHASE", str(manifest.get("phase"))))

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return issues

    bootstrap_helpers = require_string_list(issues, present_surfaces, "bootstrap_helpers")
    archive_support = require_string_list(issues, present_surfaces, "archive_support")
    checkers = require_string_list(issues, present_surfaces, "checkers")
    make_wrappers = require_string_list(issues, present_surfaces, "make_wrappers")
    closure_notes = require_string_list(issues, present_surfaces, "closure_notes")

    require_manifest_members(issues, bootstrap_helpers, MANIFEST_BOOTSTRAP_HELPERS, "MISSING_MANIFEST_BOOTSTRAP_HELPER")
    require_manifest_members(issues, archive_support, MANIFEST_ARCHIVE_SUPPORT, "MISSING_MANIFEST_ARCHIVE_SUPPORT")
    require_manifest_members(issues, checkers, MANIFEST_CHECKERS, "MISSING_MANIFEST_CHECKER")
    require_manifest_members(issues, make_wrappers, MANIFEST_MAKE_WRAPPERS, "MISSING_MANIFEST_MAKE_WRAPPER")
    require_manifest_members(issues, closure_notes, MANIFEST_CLOSURE_NOTES, "MISSING_MANIFEST_CLOSURE_NOTE")
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(root: Path, rel_path: Path, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(root: Path, rel_path: Path, payload: dict[str, object]) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(root, PHASE2_NOTES, "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(root, THIRD_PARTY_README, "\n".join(THIRD_PARTY_README_MARKERS) + "\n")
    write_text(root, PHASE2_CLOSURE, "\n".join(PHASE2_CLOSURE_MARKERS) + "\n")
    write_text(root, MAKEFILE, "\n".join(MAKEFILE_MARKERS) + "\n")
    write_json(
        root,
        PHASE2_TOOL_MANIFEST,
        {
            "phase": "Phase 2",
            "present_surfaces": {
                "bootstrap_helpers": list(MANIFEST_BOOTSTRAP_HELPERS),
                "archive_support": list(MANIFEST_ARCHIVE_SUPPORT),
                "checkers": list(MANIFEST_CHECKERS),
                "make_wrappers": list(MANIFEST_MAKE_WRAPPERS),
                "closure_notes": list(MANIFEST_CLOSURE_NOTES),
            },
        },
    )


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_bootstrap_note_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        notes_text = read_text(root, PHASE2_NOTES)
        marker = PHASE2_NOTES_MARKERS[0]
        write_text(root, PHASE2_NOTES, remove_marker(notes_text, marker))
        issues = collect_issues(root)
        assert ("MISSING_PHASE2_NOTES_MARKER", marker) in issues, issues
        build_sample_root(root)
        checks_run += 1

        third_party_text = read_text(root, THIRD_PARTY_README)
        marker = THIRD_PARTY_README_MARKERS[0]
        write_text(root, THIRD_PARTY_README, remove_marker(third_party_text, marker))
        issues = collect_issues(root)
        assert ("MISSING_THIRD_PARTY_README_MARKER", marker) in issues, issues
        build_sample_root(root)
        checks_run += 1

        closure_text = read_text(root, PHASE2_CLOSURE)
        marker = PHASE2_CLOSURE_MARKERS[0]
        write_text(root, PHASE2_CLOSURE, remove_marker(closure_text, marker))
        issues = collect_issues(root)
        assert ("MISSING_PHASE2_CLOSURE_MARKER", marker) in issues, issues
        build_sample_root(root)
        checks_run += 1

        makefile_text = read_text(root, MAKEFILE)
        marker = MAKEFILE_MARKERS[0]
        write_text(root, MAKEFILE, remove_marker(makefile_text, marker))
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_MARKER", marker) in issues, issues
        build_sample_root(root)
        checks_run += 1

        payload = read_json(root, PHASE2_TOOL_MANIFEST)
        payload["present_surfaces"]["checkers"] = []
        write_json(root, PHASE2_TOOL_MANIFEST, payload)
        issues = collect_issues(root)
        assert ("MISSING_MANIFEST_CHECKER", MANIFEST_CHECKERS[0]) in issues, issues
        build_sample_root(root)
        checks_run += 1

        payload = read_json(root, PHASE2_TOOL_MANIFEST)
        payload["present_surfaces"]["make_wrappers"] = []
        write_json(root, PHASE2_TOOL_MANIFEST, payload)
        issues = collect_issues(root)
        assert ("MISSING_MANIFEST_MAKE_WRAPPER", MANIFEST_MAKE_WRAPPERS[0]) in issues, issues
        build_sample_root(root)
        checks_run += 1

        payload = read_json(root, PHASE2_TOOL_MANIFEST)
        payload["present_surfaces"] = []
        write_json(root, PHASE2_TOOL_MANIFEST, payload)
        issues = collect_issues(root)
        assert ("INVALID_MANIFEST_SHAPE", "present_surfaces") in issues, issues
        checks_run += 1

    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 toolchain bootstrap note aligned with the current shared reminder packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in regression checks")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root for focused replay")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        print(f"PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE=pass")
    print(f"PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_MARKER_COUNT={len(PHASE2_NOTES_MARKERS) + len(THIRD_PARTY_README_MARKERS) + len(PHASE2_CLOSURE_MARKERS) + len(MAKEFILE_MARKERS)}")
    print(
        "PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_MANIFEST_MEMBER_COUNT="
        f"{len(MANIFEST_BOOTSTRAP_HELPERS) + len(MANIFEST_ARCHIVE_SUPPORT) + len(MANIFEST_CHECKERS) + len(MANIFEST_MAKE_WRAPPERS) + len(MANIFEST_CLOSURE_NOTES)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
