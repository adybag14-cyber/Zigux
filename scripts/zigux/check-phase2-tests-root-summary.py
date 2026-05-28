#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

TESTS_README_MARKERS = (
    "## Phase 2 review packet",
    "current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`third_party/README.md`",
    "current `master` now directly materializes `third_party/README.md`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py`, so keep that returned repo-local pinned-archive workflow, bootstrap guard, and archive README contract explicit here instead of leaving them outside the tests-root reminder",
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
    "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`, `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`, `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`, and `python3 scripts/zigux/check-lane05-local-archive-readme.py`.",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
    "current `master` also directly materializes `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned survey, selftest-alignment, checker, bridge helper, standalone proof, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
    "keep the fixture-backed tool-manifest and artifact-tools-manifest guards, tool-manifest, artifact-tools, cross-target, helper-local kconfig allconfig, the survey-backed genksyms packet, and fixdep packet visible in the tests root without reviving missing validator-first or make-wrapper proof text",
)

PHASE2_CLOSURE_MARKERS = (
    "`zigux/tests/README.md`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`PHASE2_CURRENT_CLOSURE_PACKET=`",
    "`PHASE2_CLOSURE_VALIDATORS=`",
)

SCRIPTS_README_MARKERS = (
    "## Phase 2",
    "`scripts/zigux/check-phase2-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed current Phase 2 tool packet explicit from the scripts root beside the closure-side validator packet and the surviving alignment guards",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
    "keep those installer, tool-manifest, artifact-support, direct cross-route, genksyms bridge, and fixdep surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

REQUIRED_REVIEW_SURFACES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

REQUIRED_CHECKERS = (
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
)

REQUIRED_MAKE_WRAPPERS = (
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
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


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def manifest_list(manifest: dict[str, object], key: str) -> list[str]:
    value = manifest.get("present_surfaces", {})
    if not isinstance(value, dict):
        raise SystemExit("manifest present_surfaces must be an object")
    items = value.get(key)
    if not isinstance(items, list) or not all(isinstance(item, str) for item in items):
        raise SystemExit(f"manifest present_surfaces.{key} must be a string list")
    return items


def collect_issues(root: Path) -> list[tuple[str, str]]:
    tests_text = read_text(resolve_path(root, TESTS_README))
    closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    scripts_text = read_text(resolve_path(root, SCRIPTS_README))
    manifest = read_manifest(resolve_path(root, MANIFEST))

    issues: list[tuple[str, str]] = []
    issues.extend(missing_markers(tests_text, TESTS_README_MARKERS, "tests_readme"))
    issues.extend(missing_markers(closure_text, PHASE2_CLOSURE_MARKERS, "phase2_closure"))
    issues.extend(missing_markers(scripts_text, SCRIPTS_README_MARKERS, "scripts_readme"))

    review_surfaces = manifest_list(manifest, "review_surfaces")
    checkers = manifest_list(manifest, "checkers")
    make_wrappers = manifest_list(manifest, "make_wrappers")

    for surface in REQUIRED_REVIEW_SURFACES:
        if surface not in review_surfaces:
            issues.append(("manifest_review_surfaces", surface))

    for checker in REQUIRED_CHECKERS:
        if checker not in checkers:
            issues.append(("manifest_checkers", checker))

    for wrapper in REQUIRED_MAKE_WRAPPERS:
        if wrapper not in make_wrappers:
            issues.append(("manifest_make_wrappers", wrapper))

    return issues


def write_sample_root(root: Path) -> None:
    tests_text = "\n".join(TESTS_README_MARKERS) + "\n"
    closure_text = "\n".join(PHASE2_CLOSURE_MARKERS) + "\n"
    scripts_text = "\n".join(SCRIPTS_README_MARKERS) + "\n"
    manifest = {
        "present_surfaces": {
            "review_surfaces": list(REQUIRED_REVIEW_SURFACES),
            "checkers": list(REQUIRED_CHECKERS),
            "make_wrappers": list(REQUIRED_MAKE_WRAPPERS),
        }
    }

    targets = (
        (TESTS_README, tests_text),
        (PHASE2_CLOSURE, closure_text),
        (SCRIPTS_README, scripts_text),
        (MANIFEST, json.dumps(manifest, indent=2) + "\n"),
    )

    for path, content in targets:
        target = resolve_path(root, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase2-tests-root-summary-") as tmpdir:
        sample_root = Path(tmpdir)
        write_sample_root(sample_root)
        issues = collect_issues(sample_root)
        if issues:
            raise SystemExit(f"self-test failed: {issues!r}")

    print("PHASE2_TESTS_ROOT_SUMMARY_SELF_TEST=pass")
    print("PHASE2_TESTS_ROOT_SUMMARY_SELF_TEST_CASE_COUNT=1")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Guard the shared Phase 2 tests-root summary packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repo root to validate (defaults to the inferred repository root)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root to the provided directory",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)

    if args.self_test:
        run_self_test()
        return

    issues = collect_issues(args.root)
    if issues:
        print("PHASE2_TESTS_ROOT_SUMMARY=fail")
        for code, detail in issues:
            print(f"{code}: missing {detail}")
        raise SystemExit(1)

    manifest = read_manifest(resolve_path(args.root, MANIFEST))
    review_surfaces = manifest_list(manifest, "review_surfaces")
    print("PHASE2_TESTS_ROOT_SUMMARY=pass")
    print(f"PHASE2_TESTS_ROOT_SUMMARY_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE2_TESTS_ROOT_SUMMARY_REVIEW_SURFACE_COUNT={len(review_surfaces)}")
    print(f"PHASE2_TESTS_ROOT_SUMMARY_REQUIRED_CHECKER_COUNT={len(REQUIRED_CHECKERS)}")


if __name__ == "__main__":
    main()
