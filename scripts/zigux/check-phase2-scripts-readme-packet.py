#!/usr/bin/env python3
"""Guard the restored Phase 2 scripts README packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

README = Path("scripts/zigux/README.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
TESTS_README = Path("zigux/tests/README.md")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")

README_MARKERS = (
    "## Phase 2",
    "Phase 2 flow - the current scripts-root toolchain reminder keeps the returned pinned-archive, installer, direct cross-route, docs-shared-reminder, manifest, artifact-support, genksyms bridge, fixdep, and make-wrapper packet explicit without reopening broader workflow, docs-root, or closure-side surfaces.",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "No current repo-reality gaps remain inside the bounded scripts-root toolchain, installer, direct cross-route, local-first archive, docs-shared-reminder, required-make-route, tool-manifest, artifact-support, fixdep, or make-wrapper packet on current `master`.",
)

NOTES_MARKERS = (
    "`scripts/zigux/README.md` is the shipped scripts-root reminder surface for the same current Phase 2 toolchain, kbuild, installer, cross-route, and make-wrapper packet",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
)

REVIEW_MARKERS = (
    "* if the change touches the shared Phase 2 toolchain packet",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
)

TESTS_MARKERS = (
    "* `scripts/zigux/README.md`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, installer, direct cross-route, cross-selftest, docs-shared-reminder, tool-manifest, artifact-tools-manifest, required-make-route, toolchain reminder, helper-local kconfig allconfig guard, kconfig bridge checker, the dedicated genksyms survey, selftest-alignment guard, bridge helper, and standalone version-side-effect proofs, fixdep governance and parity set plus the live kconfig bridge helpers, the restored closure-side note, validator entrypoint, closure validator, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`",
    "current `master` also directly materializes `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
)

MANIFEST_EXPECTED = (
    ("review_surfaces", "scripts/zigux/README.md"),
    ("checkers", "scripts/zigux/check-phase2-tool-manifest.py"),
    ("checkers", "scripts/zigux/check-phase2-artifact-tools-manifest.py"),
    ("checkers", "scripts/zigux/check-genksyms-bridge.py"),
    ("checkers", "scripts/zigux/check-phase2-fixdep-gate.py"),
    ("checkers", "scripts/zigux/check-fixdep-diff.py"),
    ("bootstrap_helpers", "scripts/zigux/install-zig.py"),
    ("cross_route_support", "scripts/zigux/check-phase2-cross.py"),
    ("make_wrappers", "make -C zigux phase2-genksyms"),
    ("make_wrappers", "make -C zigux phase2-fixdep"),
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(README_MARKERS)
    + len(NOTES_MARKERS)
    + len(REVIEW_MARKERS)
    + len(TESTS_MARKERS)
    + len(WORKFLOW_LINES)
    + len(MANIFEST_EXPECTED)
    + 1
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_missing_lines(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    lines = {line.strip() for line in text.splitlines()}
    return [(code, marker) for marker in markers if marker not in lines]


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    payload = json.loads(read_text(resolve(root, TOOL_MANIFEST)))
    surfaces = payload.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return [("MANIFEST_FIELD_MISMATCH", "present_surfaces")]
    issues: list[tuple[str, str]] = []
    for bucket, marker in MANIFEST_EXPECTED:
        if marker not in surfaces.get(bucket, []):
            issues.append(("MANIFEST_MISSING_SURFACE", f"{bucket}:{marker}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_markers(read_text(resolve(root, README)), README_MARKERS, "MISSING_README_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve(root, BOOTSTRAP_NOTES)), NOTES_MARKERS, "MISSING_NOTES_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve(root, REVIEW_CHECKLIST)), REVIEW_MARKERS, "MISSING_REVIEW_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve(root, TESTS_README)), TESTS_MARKERS, "MISSING_TESTS_MARKERS"))
    issues.extend(collect_missing_lines(read_text(resolve(root, WORKFLOW)), WORKFLOW_LINES, "MISSING_WORKFLOW_LINES"))
    issues.extend(collect_manifest_issues(root))
    return issues


def build_sample_root(root: Path) -> None:
    write_text(resolve(root, README), "\n".join(README_MARKERS) + "\n")
    write_text(resolve(root, BOOTSTRAP_NOTES), "\n".join(NOTES_MARKERS) + "\n")
    write_text(resolve(root, REVIEW_CHECKLIST), "\n".join(REVIEW_MARKERS) + "\n")
    write_text(resolve(root, TESTS_README), "\n".join(TESTS_MARKERS) + "\n")
    write_text(resolve(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")

    surfaces: dict[str, list[str]] = {}
    for bucket, marker in MANIFEST_EXPECTED:
        surfaces.setdefault(bucket, []).append(marker)
    write_text(
        resolve(root, TOOL_MANIFEST),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "workflow": ".github/workflows/zigux-bootstrap.yml",
                "present_surfaces": surfaces,
            },
            indent=2,
        )
        + "\n",
    )


def remove_once(text: str, marker: str) -> str:
    index = text.find(marker)
    if index == -1:
        raise AssertionError(f"marker not found: {marker}")
    return text[:index] + text[index + len(marker) :]


def remove_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_scripts_readme_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for rel, markers, code in (
            (README, README_MARKERS, "MISSING_README_MARKERS"),
            (BOOTSTRAP_NOTES, NOTES_MARKERS, "MISSING_NOTES_MARKERS"),
            (REVIEW_CHECKLIST, REVIEW_MARKERS, "MISSING_REVIEW_MARKERS"),
            (TESTS_README, TESTS_MARKERS, "MISSING_TESTS_MARKERS"),
        ):
            for marker in markers:
                build_sample_root(root)
                path = resolve(root, rel)
                write_text(path, remove_once(read_text(path), marker))
                assert (code, marker) in collect_issues(root)
                checks_run += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve(root, WORKFLOW)
            write_text(path, remove_exact_line(read_text(path), marker))
            assert ("MISSING_WORKFLOW_LINES", marker) in collect_issues(root)
            checks_run += 1

        for bucket, marker in MANIFEST_EXPECTED:
            build_sample_root(root)
            path = resolve(root, TOOL_MANIFEST)
            payload = json.loads(read_text(path))
            payload["present_surfaces"][bucket].remove(marker)
            write_text(path, json.dumps(payload, indent=2) + "\n")
            assert ("MANIFEST_MISSING_SURFACE", f"{bucket}:{marker}") in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT, (checks_run, EXPECTED_SELF_TEST_CASE_COUNT)
    print("PHASE2_SCRIPTS_README_PACKET_SELF_TEST=pass")
    print(f"PHASE2_SCRIPTS_README_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE2_SCRIPTS_README_PACKET=fail")
        for code, marker in issues:
            print(f"{code}:{marker}")
        return 1
    print("PHASE2_SCRIPTS_README_PACKET=pass")
    print("PHASE2_SCRIPTS_README_PACKET_REQUIRED_FILE_COUNT=6")
    print(f"PHASE2_SCRIPTS_README_PACKET_README_MARKER_COUNT={len(README_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_PACKET_NOTES_MARKER_COUNT={len(NOTES_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_PACKET_TESTS_MARKER_COUNT={len(TESTS_MARKERS)}")
    print(f"PHASE2_SCRIPTS_README_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_SCRIPTS_README_PACKET_MANIFEST_SURFACE_COUNT={len(MANIFEST_EXPECTED)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repo root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in self-test suite.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
