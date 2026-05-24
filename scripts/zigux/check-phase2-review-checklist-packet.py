#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

REVIEW_CHECKLIST_MARKERS = (
    "* if the change touches the shared Phase 2 toolchain packet, do `Documentation/zigux/README.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "`make -C zigux phase2-validate`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`make -C zigux phase2-validate`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_manifest(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"required json has invalid top-level shape: {path}")
    return payload


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    review_checklist_text = read_text(root / REVIEW_CHECKLIST)
    phase2_notes_text = read_text(root / PHASE2_NOTES)
    manifest = read_manifest(root / PHASE2_TOOL_MANIFEST)

    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            review_checklist_text,
            REVIEW_CHECKLIST_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            phase2_notes_text,
            PHASE2_NOTES_MARKERS,
            "MISSING_PHASE2_NOTES_MARKERS",
        )
    )

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return issues
    review_surfaces = present_surfaces.get("review_surfaces")
    checkers = present_surfaces.get("checkers")
    if not isinstance(review_surfaces, list) or not all(isinstance(entry, str) for entry in review_surfaces):
        issues.append(("INVALID_MANIFEST_SHAPE", "review_surfaces"))
        return issues
    if not isinstance(checkers, list) or not all(isinstance(entry, str) for entry in checkers):
        issues.append(("INVALID_MANIFEST_SHAPE", "checkers"))
        return issues
    if "Documentation/zigux/review-checklist.md" not in review_surfaces:
        issues.append(("MISSING_MANIFEST_REVIEW_SURFACE", "Documentation/zigux/review-checklist.md"))
    for checker in (
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "scripts/zigux/check-phase2-docs-shared-reminder.py",
        "scripts/zigux/check-phase2-required-make-routes.py",
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
        "scripts/zigux/check-phase2-tool-manifest.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    ):
        if checker not in checkers:
            issues.append(("MISSING_MANIFEST_CHECKER", checker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_REVIEW_CHECKLIST_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(root / REVIEW_CHECKLIST, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root / PHASE2_NOTES, "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(
        root / PHASE2_TOOL_MANIFEST,
        json.dumps(
            {
                "phase": "Phase 2",
                "present_surfaces": {
                    "review_surfaces": ["Documentation/zigux/review-checklist.md"],
                    "checkers": [
                        "scripts/zigux/check-phase2-tests-readme-alignment.py",
                        "scripts/zigux/check-phase2-docs-shared-reminder.py",
                        "scripts/zigux/check-phase2-required-make-routes.py",
                        "scripts/zigux/check-phase2-cross.py",
                        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
                        "scripts/zigux/check-phase2-tool-manifest.py",
                        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
                    ],
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def remove_all(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_review_checklist_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        review_checklist_path = root / REVIEW_CHECKLIST
        review_checklist_text = read_text(review_checklist_path)
        for marker in REVIEW_CHECKLIST_MARKERS:
            write_text(review_checklist_path, remove_all(review_checklist_text, marker))
            issues = collect_issues(root)
            assert ("MISSING_REVIEW_CHECKLIST_MARKERS", marker) in issues, (marker, issues)
            build_self_test_root(root)
            review_checklist_text = read_text(review_checklist_path)
            checks_run += 1

        phase2_notes_path = root / PHASE2_NOTES
        phase2_notes_text = read_text(phase2_notes_path)
        for marker in PHASE2_NOTES_MARKERS:
            write_text(phase2_notes_path, remove_all(phase2_notes_text, marker))
            issues = collect_issues(root)
            assert ("MISSING_PHASE2_NOTES_MARKERS", marker) in issues, (marker, issues)
            build_self_test_root(root)
            phase2_notes_text = read_text(phase2_notes_path)
            checks_run += 1

        manifest_path = root / PHASE2_TOOL_MANIFEST
        payload = read_manifest(manifest_path)
        payload["present_surfaces"]["checkers"] = []
        write_text(manifest_path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        assert ("MISSING_MANIFEST_CHECKER", "scripts/zigux/check-phase2-tests-readme-alignment.py") in issues, issues
        build_self_test_root(root)
        checks_run += 1

        payload = read_manifest(manifest_path)
        payload["present_surfaces"] = []
        write_text(manifest_path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        assert ("INVALID_MANIFEST_SHAPE", "present_surfaces") in issues, issues
        build_self_test_root(root)
        checks_run += 1

    print("PHASE2_REVIEW_CHECKLIST_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 review-checklist packet aligned with the current reminder surfaces."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in regression checks")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_REVIEW_CHECKLIST_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
