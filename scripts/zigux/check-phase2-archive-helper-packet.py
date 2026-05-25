#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
VALIDATE_PHASE2_CLOSURE = Path("scripts/zigux/validate-phase2-closure.py")

REQUIRED_PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are directly readable on current `master` and keep the pinned-channel archive download, staged repo-local archive materialization, archive-verification, helper-contract, helper-selftest, and install-root replay path explicit beside the reminder guards.",
    "`python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test`",
    "`python3 scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`",
    "`python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test`",
    "`python3 scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`",
    "`python3 scripts/zigux/check-lane05-stage-helper-selftest.py`",
)

REQUIRED_MANIFEST_CHECKERS = (
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
)

REQUIRED_MANIFEST_BOOTSTRAP_HELPERS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
)

REQUIRED_MANIFEST_NOTE = (
    "Keep the returned install-zig archive verification checker, staged pinned-archive helper, and the stage-helper contract plus selftest packet explicit beside the local-first archive workflow, archive README contract, and installer helper so the shared Phase 2 tool packet matches the live phase2-toolchain and validate-phase2 routes."
)

REQUIRED_VALIDATE_CLOSURE_MARKERS = (
    'INSTALL_ZIG_ARCHIVE_VERIFICATION_CHECKER_REL = Path("scripts/zigux/check-lane05-install-zig-archive-verification.py")',
    'STAGE_HELPER_CONTRACT_CHECKER_REL = Path("scripts/zigux/check-lane05-stage-helper-contract.py")',
    'STAGE_HELPER_SELFTEST_CHECKER_REL = Path("scripts/zigux/check-lane05-stage-helper-selftest.py")',
    'STAGE_PINNED_ARCHIVE_REL = Path("scripts/zigux/stage-pinned-zig-archive.py")',
    '"`python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test`",',
    '"`python3 scripts/zigux/check-lane05-install-zig-archive-verification.py`",',
    '"`python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`",',
    '"`python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test`",',
    '"`python3 scripts/zigux/check-lane05-stage-helper-contract.py`",',
    '"`python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`",',
    '"`python3 scripts/zigux/check-lane05-stage-helper-selftest.py`",',
    '"run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",',
    '"run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",',
    '"run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",',
    '"run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",',
    '"run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",',
    '"run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",',
    '"run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",',
)


def resolve_path(root: Path, rel: Path) -> Path:
    try:
        return root / rel.relative_to(ROOT)
    except ValueError:
        return root / rel


def read_text(root: Path, rel: Path) -> str:
    path = resolve_path(root, rel)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = resolve_path(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_manifest(root: Path) -> dict[str, object]:
    path = resolve_path(root, PHASE2_TOOL_MANIFEST)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"required json has invalid top-level shape: {path}")
    return payload


def require_manifest_list(
    issues: list[tuple[str, str]], manifest: dict[str, object], key: str
) -> list[str] | None:
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return list(value)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    phase2_notes_text = read_text(root, PHASE2_NOTES)
    for marker in REQUIRED_PHASE2_NOTES_MARKERS:
        if marker not in phase2_notes_text:
            issues.append(("MISSING_PHASE2_NOTES_MARKER", marker))

    manifest = read_manifest(root)
    notes = manifest.get("notes")
    if not isinstance(notes, list) or REQUIRED_MANIFEST_NOTE not in notes:
        issues.append(("MISSING_MANIFEST_NOTE", REQUIRED_MANIFEST_NOTE))

    manifest_checkers = require_manifest_list(issues, manifest, "checkers")
    if manifest_checkers is not None:
        for marker in REQUIRED_MANIFEST_CHECKERS:
            if marker not in manifest_checkers:
                issues.append(("MISSING_MANIFEST_CHECKER", marker))

    bootstrap_helpers = require_manifest_list(issues, manifest, "bootstrap_helpers")
    if bootstrap_helpers is not None:
        for marker in REQUIRED_MANIFEST_BOOTSTRAP_HELPERS:
            if marker not in bootstrap_helpers:
                issues.append(("MISSING_BOOTSTRAP_HELPER", marker))

    validate_phase2_closure_text = read_text(root, VALIDATE_PHASE2_CLOSURE)
    for marker in REQUIRED_VALIDATE_CLOSURE_MARKERS:
        if marker not in validate_phase2_closure_text:
            issues.append(("MISSING_VALIDATE_PHASE2_CLOSURE_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_ARCHIVE_HELPER_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(root, PHASE2_NOTES, "\n".join(REQUIRED_PHASE2_NOTES_MARKERS) + "\n")
    write_text(
        root,
        PHASE2_TOOL_MANIFEST,
        json.dumps(
            {
                "present_surfaces": {
                    "checkers": list(REQUIRED_MANIFEST_CHECKERS),
                    "bootstrap_helpers": list(REQUIRED_MANIFEST_BOOTSTRAP_HELPERS),
                },
                "notes": [REQUIRED_MANIFEST_NOTE],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    write_text(
        root,
        VALIDATE_PHASE2_CLOSURE,
        "\n".join(REQUIRED_VALIDATE_CLOSURE_MARKERS) + "\n",
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_archive_helper_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        phase2_notes_path = resolve_path(root, PHASE2_NOTES)
        original_phase2_notes_text = phase2_notes_path.read_text(encoding="utf-8")
        for marker in REQUIRED_PHASE2_NOTES_MARKERS:
            build_self_test_root(root)
            phase2_notes_path.write_text(
                replace_once(original_phase2_notes_text, marker), encoding="utf-8"
            )
            assert ("MISSING_PHASE2_NOTES_MARKER", marker) in collect_issues(root)
            checks_run += 1

        manifest_path = resolve_path(root, PHASE2_TOOL_MANIFEST)
        for marker in REQUIRED_MANIFEST_CHECKERS:
            build_self_test_root(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["present_surfaces"]["checkers"] = [
                item for item in manifest["present_surfaces"]["checkers"] if item != marker
            ]
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            assert ("MISSING_MANIFEST_CHECKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_MANIFEST_BOOTSTRAP_HELPERS:
            build_self_test_root(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["present_surfaces"]["bootstrap_helpers"] = [
                item
                for item in manifest["present_surfaces"]["bootstrap_helpers"]
                if item != marker
            ]
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            assert ("MISSING_BOOTSTRAP_HELPER", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["notes"] = []
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_NOTE", REQUIRED_MANIFEST_NOTE) in collect_issues(root)
        checks_run += 1

        validate_phase2_closure_path = resolve_path(root, VALIDATE_PHASE2_CLOSURE)
        original_validate_phase2_closure_text = validate_phase2_closure_path.read_text(
            encoding="utf-8"
        )
        for marker in REQUIRED_VALIDATE_CLOSURE_MARKERS:
            build_self_test_root(root)
            validate_phase2_closure_path.write_text(
                replace_once(original_validate_phase2_closure_text, marker),
                encoding="utf-8",
            )
            assert ("MISSING_VALIDATE_PHASE2_CLOSURE_MARKER", marker) in collect_issues(root)
            checks_run += 1

    print("PHASE2_ARCHIVE_HELPER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_ARCHIVE_HELPER_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 22 archive-verification and staged-helper packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--self-test", action="store_true", help="Run the built-in contract self-test"
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_ARCHIVE_HELPER_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())