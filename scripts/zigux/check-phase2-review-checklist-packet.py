#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
PHASE2_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 2 toolchain pin-scope packet",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "if the change touches the shared Phase 2 toolchain packet",
    "`third_party/README.md`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
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
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

PHASE2_NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/artifact_diff.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`make -C zigux phase2-validate`",
)

REQUIRED_MANIFEST_CHECKERS = (
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
)

REQUIRED_MANIFEST_REVIEW_SURFACES = (
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
)

REQUIRED_MANIFEST_CLOSURE_NOTES = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
)

REQUIRED_MANIFEST_ARTIFACT_SUPPORT = (
    "scripts/zigux/artifact_diff.py",
)

REQUIRED_MANIFEST_MAKE_WRAPPERS = (
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_manifest(root: Path, relative_path: Path) -> dict[str, object]:
    path = root / relative_path
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"required json has invalid top-level shape: {path}")
    return payload


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    review_checklist_text = read_text(root, REVIEW_CHECKLIST)
    phase2_notes_text = read_text(root, PHASE2_NOTES)
    manifest = read_manifest(root, PHASE2_TOOL_MANIFEST)

    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            review_checklist_text,
            REVIEW_CHECKLIST_MARKERS,
            "MISSING_REVIEW_CHECKLIST_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            phase2_notes_text,
            PHASE2_NOTES_MARKERS,
            "MISSING_PHASE2_NOTES_MARKER",
        )
    )

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return issues

    review_surfaces = require_string_list(issues, present_surfaces, "review_surfaces")
    closure_notes = require_string_list(issues, present_surfaces, "closure_notes")
    checkers = require_string_list(issues, present_surfaces, "checkers")
    artifact_support = require_string_list(issues, present_surfaces, "artifact_support")
    make_wrappers = require_string_list(issues, present_surfaces, "make_wrappers")

    if review_surfaces is not None:
        for surface in REQUIRED_MANIFEST_REVIEW_SURFACES:
            if surface not in review_surfaces:
                issues.append(("MISSING_MANIFEST_REVIEW_SURFACE", surface))
    if closure_notes is not None:
        for note in REQUIRED_MANIFEST_CLOSURE_NOTES:
            if note not in closure_notes:
                issues.append(("MISSING_MANIFEST_CLOSURE_NOTE", note))
    if checkers is not None:
        for checker in REQUIRED_MANIFEST_CHECKERS:
            if checker not in checkers:
                issues.append(("MISSING_MANIFEST_CHECKER", checker))
    if artifact_support is not None:
        for support_path in REQUIRED_MANIFEST_ARTIFACT_SUPPORT:
            if support_path not in artifact_support:
                issues.append(("MISSING_MANIFEST_ARTIFACT_SUPPORT", support_path))
    if make_wrappers is not None:
        for route in REQUIRED_MANIFEST_MAKE_WRAPPERS:
            if route not in make_wrappers:
                issues.append(("MISSING_MANIFEST_MAKE_WRAPPER", route))

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


def build_sample_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 2",
        "present_surfaces": {
            "review_surfaces": list(REQUIRED_MANIFEST_REVIEW_SURFACES),
            "closure_notes": list(REQUIRED_MANIFEST_CLOSURE_NOTES),
            "checkers": list(REQUIRED_MANIFEST_CHECKERS),
            "artifact_support": list(REQUIRED_MANIFEST_ARTIFACT_SUPPORT),
            "make_wrappers": list(REQUIRED_MANIFEST_MAKE_WRAPPERS),
        },
    }


def write_sample_root(root: Path) -> None:
    write_text(root, REVIEW_CHECKLIST, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(root, PHASE2_NOTES, "\n".join(PHASE2_NOTES_MARKERS) + "\n")
    write_text(
        root,
        PHASE2_TOOL_MANIFEST,
        json.dumps(build_sample_manifest(), indent=2, sort_keys=True) + "\n",
    )


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_review_checklist_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        review_checklist_text = read_text(root, REVIEW_CHECKLIST)
        review_marker = REVIEW_CHECKLIST_MARKERS[0]
        write_text(root, REVIEW_CHECKLIST, remove_marker(review_checklist_text, review_marker))
        issues = collect_issues(root)
        assert (("MISSING_REVIEW_CHECKLIST_MARKER", review_marker) in issues), issues
        write_sample_root(root)
        checks_run += 1

        phase2_notes_text = read_text(root, PHASE2_NOTES)
        notes_marker = PHASE2_NOTES_MARKERS[0]
        write_text(root, PHASE2_NOTES, remove_marker(phase2_notes_text, notes_marker))
        issues = collect_issues(root)
        assert (("MISSING_PHASE2_NOTES_MARKER", notes_marker) in issues), issues
        write_sample_root(root)
        checks_run += 1

        payload = read_manifest(root, PHASE2_TOOL_MANIFEST)
        payload["present_surfaces"]["checkers"] = []
        write_text(root, PHASE2_TOOL_MANIFEST, json.dumps(payload, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        assert (("MISSING_MANIFEST_CHECKER", REQUIRED_MANIFEST_CHECKERS[0]) in issues), issues
        write_sample_root(root)
        checks_run += 1

        payload = read_manifest(root, PHASE2_TOOL_MANIFEST)
        payload["present_surfaces"]["review_surfaces"] = []
        write_text(root, PHASE2_TOOL_MANIFEST, json.dumps(payload, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        assert (("MISSING_MANIFEST_REVIEW_SURFACE", REQUIRED_MANIFEST_REVIEW_SURFACES[0]) in issues), issues
        write_sample_root(root)
        checks_run += 1

        payload = read_manifest(root, PHASE2_TOOL_MANIFEST)
        payload["present_surfaces"]["artifact_support"] = []
        write_text(root, PHASE2_TOOL_MANIFEST, json.dumps(payload, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        assert (("MISSING_MANIFEST_ARTIFACT_SUPPORT", REQUIRED_MANIFEST_ARTIFACT_SUPPORT[0]) in issues), issues
        write_sample_root(root)
        checks_run += 1

        payload = read_manifest(root, PHASE2_TOOL_MANIFEST)
        payload["present_surfaces"] = []
        write_text(root, PHASE2_TOOL_MANIFEST, json.dumps(payload, indent=2, sort_keys=True) + "\n")
        issues = collect_issues(root)
        assert (("INVALID_MANIFEST_SHAPE", "present_surfaces") in issues), issues
        checks_run += 1

    print("PHASE2_REVIEW_CHECKLIST_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 review-checklist packet aligned with the current reminder surfaces."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in regression checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample repository root")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_REVIEW_CHECKLIST_PACKET=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_NOTES_MARKER_COUNT={len(PHASE2_NOTES_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_CHECKER_COUNT={len(REQUIRED_MANIFEST_CHECKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
