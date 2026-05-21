#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 review-checklist packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

REQUIRED_PATHS = (
    REVIEW_CHECKLIST,
    BOOTSTRAP_NOTES,
    SCRIPTS_README,
    TESTS_README,
    TOOL_MANIFEST,
)

REVIEW_MARKERS = (
    "if the change touches the shared Phase 2 toolchain packet",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "current directly readable Phase 2 local-first archive, toolchain, installer, direct cross-route, kbuild, kconfig bridge, docs-shared-reminder, tool-manifest, artifact-support, fixdep, genksyms-bridge, and required-make-route packet",
    "current rematerialized Phase 2 local-first archive, closure-side, closure-validator, validation, installer, direct cross-route, artifact-support, fixdep, toolchain self-check, and make-wrapper packet",
)

REVIEW_FORBIDDEN_MARKERS = (
    "current directly readable Phase 2 toolchain, kbuild, kconfig bridge, docs-shared-reminder, and required-make-route packet",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` stay framed as historical packet members rather than shipped current-`master` evidence",
    "`zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2`, and `make -C zigux phase2-validate` stay framed as historical packet members rather than shipped current-`master` evidence",
)

NOTES_MARKERS = (
    "# Phase 2 Toolchain Bootstrap Notes",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/install-zig.py` is directly readable on current `master`",
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master`",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
    "installer-path truthfulness, direct cross-route truthfulness, local-first archive workflow truthfulness, third_party archive README truthfulness",
)

SCRIPTS_MARKERS = (
    "## Phase 2",
    "the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet",
    "`scripts/zigux/check-phase2-docs-shared-reminder.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

TESTS_MARKERS = (
    "## Phase 2 review packet",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`",
)

MANIFEST_REVIEW_SURFACES = (
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
)

MANIFEST_CHECKERS = (
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
)

MANIFEST_MAKE_WRAPPERS = (
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)

EXPECTED_SELF_TEST_CASE_COUNT = 8


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_present_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def validate_manifest(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_MANIFEST", "expected JSON object")]

    if payload.get("phase") != "Phase 2":
        issues.append(("INVALID_MANIFEST", f"phase={payload.get('phase')!r}"))
    if payload.get("status") != "active":
        issues.append(("INVALID_MANIFEST", f"status={payload.get('status')!r}"))

    scope = payload.get("scope")
    if not isinstance(scope, str):
        issues.append(("INVALID_MANIFEST_SCOPE", "missing scope"))
    else:
        for fragment in ("installer", "direct cross-route", "genksyms", "fixdep"):
            if fragment not in scope:
                issues.append(("INVALID_MANIFEST_SCOPE", fragment))

    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        return issues + [("INVALID_MANIFEST_SURFACES", "missing present_surfaces")]

    review_surfaces = present_surfaces.get("review_surfaces")
    if not isinstance(review_surfaces, list):
        issues.append(("INVALID_MANIFEST_REVIEW_SURFACES", type(review_surfaces).__name__))
    else:
        for marker in MANIFEST_REVIEW_SURFACES:
            if marker not in review_surfaces:
                issues.append(("MISSING_MANIFEST_REVIEW_SURFACE", marker))

    closure_notes = present_surfaces.get("closure_notes")
    if not isinstance(closure_notes, list) or "Documentation/zigux/phase2-toolchain-bootstrap-notes.md" not in closure_notes:
        issues.append(("MISSING_MANIFEST_CLOSURE_NOTE", "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"))

    checkers = present_surfaces.get("checkers")
    if not isinstance(checkers, list):
        issues.append(("INVALID_MANIFEST_CHECKERS", type(checkers).__name__))
    else:
        for marker in MANIFEST_CHECKERS:
            if marker not in checkers:
                issues.append(("MISSING_MANIFEST_CHECKER", marker))

    bootstrap_helpers = present_surfaces.get("bootstrap_helpers")
    if not isinstance(bootstrap_helpers, list) or "scripts/zigux/install-zig.py" not in bootstrap_helpers:
        issues.append(("MISSING_MANIFEST_BOOTSTRAP_HELPER", "scripts/zigux/install-zig.py"))

    cross_route_support = present_surfaces.get("cross_route_support")
    if not isinstance(cross_route_support, list):
        issues.append(("INVALID_MANIFEST_CROSS_SUPPORT", type(cross_route_support).__name__))
    else:
        for marker in ("scripts/zigux/check-phase2-cross.py", "zigux/tests/fixtures/phase2_cross_targets.json"):
            if marker not in cross_route_support:
                issues.append(("MISSING_MANIFEST_CROSS_SUPPORT", marker))

    make_wrappers = present_surfaces.get("make_wrappers")
    if not isinstance(make_wrappers, list):
        issues.append(("INVALID_MANIFEST_MAKE_WRAPPERS", type(make_wrappers).__name__))
    else:
        for marker in MANIFEST_MAKE_WRAPPERS:
            if marker not in make_wrappers:
                issues.append(("MISSING_MANIFEST_MAKE_WRAPPER", marker))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_PATHS:
        candidate = resolve_path(root, path)
        if not candidate.exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))

    if issues:
        return issues

    review_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    notes_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    scripts_text = read_text(resolve_path(root, SCRIPTS_README))
    tests_text = read_text(resolve_path(root, TESTS_README))

    issues.extend(collect_missing_markers(review_text, REVIEW_MARKERS, "MISSING_REVIEW_MARKER"))
    issues.extend(collect_present_markers(review_text, REVIEW_FORBIDDEN_MARKERS, "FORBIDDEN_REVIEW_MARKER"))
    issues.extend(collect_missing_markers(notes_text, NOTES_MARKERS, "MISSING_NOTES_MARKER"))
    issues.extend(collect_missing_markers(scripts_text, SCRIPTS_MARKERS, "MISSING_SCRIPTS_MARKER"))
    issues.extend(collect_missing_markers(tests_text, TESTS_MARKERS, "MISSING_TESTS_MARKER"))

    try:
        manifest_payload = json.loads(read_text(resolve_path(root, TOOL_MANIFEST)))
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_MANIFEST_JSON", exc.msg))
        return issues

    issues.extend(validate_manifest(manifest_payload))
    return issues


def make_sample_root(root: Path) -> None:
    review_text = "\n".join(
        (
            "# Zigux Review Checklist",
            "",
            "## Validation",
            "",
            " * " + REVIEW_MARKERS[0],
            " * " + " ".join(REVIEW_MARKERS[1:]),
        )
    ) + "\n"
    notes_text = "\n".join(("# Phase 2 Toolchain Bootstrap Notes",) + NOTES_MARKERS[1:]) + "\n"
    scripts_text = "\n".join(("## Phase 2",) + SCRIPTS_MARKERS[1:]) + "\n"
    tests_text = "\n".join(("## Phase 2 review packet",) + TESTS_MARKERS[1:]) + "\n"
    manifest_payload = {
        "phase": "Phase 2",
        "status": "active",
        "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
        "present_surfaces": {
            "review_surfaces": list(MANIFEST_REVIEW_SURFACES),
            "closure_notes": [
                "Documentation/zigux/phase2-closure.md",
                "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            ],
            "checkers": list(MANIFEST_CHECKERS),
            "bootstrap_helpers": ["scripts/zigux/install-zig.py"],
            "cross_route_support": [
                "scripts/zigux/check-phase2-cross.py",
                "zigux/tests/fixtures/phase2_cross_targets.json",
            ],
            "make_wrappers": ["zigux/Makefile", *MANIFEST_MAKE_WRAPPERS],
        },
    }

    write_text(root / "Documentation" / "zigux" / "review-checklist.md", review_text)
    write_text(root / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md", notes_text)
    write_text(root / "scripts" / "zigux" / "README.md", scripts_text)
    write_text(root / "zigux" / "tests" / "README.md", tests_text)
    write_text(root / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json", json.dumps(manifest_payload, indent=2) + "\n")


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase2-review-checklist-packet-") as tmp:
        root = Path(tmp)
        make_sample_root(root)

        issues = collect_issues(root)
        if issues:
            raise AssertionError(f"expected passing sample root, found {issues!r}")
        cases += 1

        review_path = root / "Documentation" / "zigux" / "review-checklist.md"
        original_review = read_text(review_path)
        review_path.write_text(original_review.replace("`scripts/zigux/check-phase2-tool-manifest.py`", "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_REVIEW_MARKER", "`scripts/zigux/check-phase2-tool-manifest.py`") in issues
        review_path.write_text(original_review, encoding="utf-8")
        cases += 1

        review_path.write_text(original_review + REVIEW_FORBIDDEN_MARKERS[0] + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("FORBIDDEN_REVIEW_MARKER", REVIEW_FORBIDDEN_MARKERS[0]) in issues
        review_path.write_text(original_review, encoding="utf-8")
        cases += 1

        notes_path = root / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
        original_notes = read_text(notes_path)
        notes_path.write_text(original_notes.replace("No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.", "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_NOTES_MARKER", "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.") in issues
        notes_path.write_text(original_notes, encoding="utf-8")
        cases += 1

        manifest_path = root / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
        original_manifest = json.loads(read_text(manifest_path))
        broken_manifest = json.loads(json.dumps(original_manifest))
        broken_manifest["present_surfaces"]["checkers"].remove("scripts/zigux/check-phase2-cross.py")
        manifest_path.write_text(json.dumps(broken_manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_MANIFEST_CHECKER", "scripts/zigux/check-phase2-cross.py") in issues
        manifest_path.write_text(json.dumps(original_manifest, indent=2) + "\n", encoding="utf-8")
        cases += 1

        broken_manifest = json.loads(json.dumps(original_manifest))
        broken_manifest["scope"] = "current directly readable scripts-root toolchain and kbuild packet"
        manifest_path.write_text(json.dumps(broken_manifest, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_MANIFEST_SCOPE", "installer") in issues
        manifest_path.write_text(json.dumps(original_manifest, indent=2) + "\n", encoding="utf-8")
        cases += 1

        tests_path = root / "zigux" / "tests" / "README.md"
        original_tests = read_text(tests_path)
        tests_path.write_text(original_tests.replace("current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`", "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_TESTS_MARKER", "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`") in issues
        tests_path.write_text(original_tests, encoding="utf-8")
        cases += 1

        (root / "scripts" / "zigux" / "README.md").unlink()
        issues = collect_issues(root)
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/README.md") in issues
        cases += 1

    if cases != EXPECTED_SELF_TEST_CASE_COUNT:
        raise AssertionError(f"unexpected self-test case count: {cases} != {EXPECTED_SELF_TEST_CASE_COUNT}")

    print("PHASE2_REVIEW_CHECKLIST_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_SELF_TEST_CASE_COUNT={cases}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in checker self-test")
    parser.add_argument("--write-sample-root", type=Path, help="write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    if args.write_sample_root is not None:
        make_sample_root(args.write_sample_root)
        return

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_REVIEW_CHECKLIST_PACKET=fail")
        for code, detail in issues:
            print(f"{code}={detail}")
        raise SystemExit(1)

    print("PHASE2_REVIEW_CHECKLIST_PACKET=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_FORBIDDEN_MARKER_COUNT={len(REVIEW_FORBIDDEN_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_NOTES_MARKER_COUNT={len(NOTES_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_TESTS_MARKER_COUNT={len(TESTS_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_PACKET_MANIFEST_CHECKER_COUNT={len(MANIFEST_CHECKERS)}")


if __name__ == "__main__":
    main()
