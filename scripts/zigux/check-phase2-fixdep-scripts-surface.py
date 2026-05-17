#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
PHASE2_BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
PHASE2_CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

SCRIPTS_README_MARKERS = (
    "`check-phase2-fixdep-gate.py --self-test` plus `check-phase2-fixdep-gate.py`, "
    "`check-fixdep-diff.py --self-test` plus `check-fixdep-diff.py`, and the direct "
    "`zig test scripts/zigux/fixdep.zig` replay keep the dedicated fixdep slice explicit here",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`Documentation/zigux/artifact-diff.md`",
    "`Documentation/zigux/phase2-closure.md`",
    "`zigux/tests/README.md`",
    "`zigux/Makefile`",
    "`.github/workflows/zigux-bootstrap.yml`",
)

PHASE2_BOOTSTRAP_NOTES_MARKERS = (
    "the broader fixdep, genksyms, artifact-tools, and manifest packet should stay documented "
    "through `Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and "
    "`zigux/Makefile` instead of restating the full broader checker inventory in this dedicated "
    "pin-scope note",
    "the active Phase 2 closure note and Makefile keep the validator-routed direct "
    "`zig test scripts/zigux/fixdep.zig`, `zig test scripts/zigux/genksyms.zig`, `zig test "
    "scripts/zigux/kconfig/conf_bridge.zig`, and `zig test scripts/zigux/kconfig/confdata_bridge.zig` "
    "replays explicit beside the same bounded Phase 2 tools and kconfig routes, while "
    "`zigux/tests/README.md` keeps the corresponding fixdep, genksyms bridge, and kconfig "
    "manifest packet reviewable without restating every direct tests-root replay command",
)

PHASE2_CLOSURE_DOC_MARKERS = (
    "shared fixdep diff gate: `python3 scripts/zigux/check-fixdep-diff.py`",
    "zig test scripts/zigux/fixdep.zig",
)

TESTS_README_MARKERS = (
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "zig test scripts/zigux/fixdep.zig",
)

WORKFLOW_MARKERS = (
    "      - name: Self-test Phase 2 fixdep gate checker\n"
    "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "      - name: Check Phase 2 fixdep gate packet\n"
    "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "      - name: Self-test Phase 2 fixdep diff checker\n"
    "        run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "      - name: Check Phase 2 fixdep diff packet\n"
    "        run: python3 scripts/zigux/check-fixdep-diff.py",
    "      - name: Run Phase 2 fixdep unit tests\n"
    "        run: zig test scripts/zigux/fixdep.zig",
)

EXPECTED_SELF_TEST_CASE_COUNT = 25


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc



def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    bootstrap_notes_text = read_text(resolve_path(root, PHASE2_BOOTSTRAP_NOTES))
    closure_doc_text = read_text(resolve_path(root, PHASE2_CLOSURE_DOC))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    workflow_text = read_text(resolve_path(root, WORKFLOW))

    issues.extend(
        collect_missing_markers(
            scripts_readme_text,
            SCRIPTS_README_MARKERS,
            "MISSING_SCRIPTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            bootstrap_notes_text,
            PHASE2_BOOTSTRAP_NOTES_MARKERS,
            "MISSING_BOOTSTRAP_NOTES_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            closure_doc_text,
            PHASE2_CLOSURE_DOC_MARKERS,
            "MISSING_CLOSURE_DOC_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            tests_readme_text,
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            workflow_text,
            WORKFLOW_MARKERS,
            "MISSING_WORKFLOW_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_FIXDEP_SCRIPTS_SURFACE=fail")
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
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(
        resolve_path(root, PHASE2_BOOTSTRAP_NOTES),
        "\n".join(PHASE2_BOOTSTRAP_NOTES_MARKERS) + "\n",
    )
    write_text(resolve_path(root, PHASE2_CLOSURE_DOC), "\n".join(PHASE2_CLOSURE_DOC_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_fixdep_scripts_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in SCRIPTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker, ""),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_SCRIPTS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in PHASE2_BOOTSTRAP_NOTES_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_BOOTSTRAP_NOTES)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker, ""),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_BOOTSTRAP_NOTES_MARKERS", marker) in issues
            checks_run += 1

        for marker in PHASE2_CLOSURE_DOC_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, PHASE2_CLOSURE_DOC)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker, ""),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_CLOSURE_DOC_MARKERS", marker) in issues
            checks_run += 1

        for marker in TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker, ""),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in WORKFLOW_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker, ""),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_MARKERS", marker) in issues
            checks_run += 1

        for rel_path in (
            SCRIPTS_README,
            PHASE2_BOOTSTRAP_NOTES,
            PHASE2_CLOSURE_DOC,
            TESTS_README,
            WORKFLOW,
        ):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_FIXDEP_SCRIPTS_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_SCRIPTS_SURFACE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 2 fixdep scripts-facing packet stays aligned with the current reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_FIXDEP_SCRIPTS_SURFACE=pass")
    print(f"PHASE2_FIXDEP_SCRIPTS_SURFACE_SCRIPTS_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(
        "PHASE2_FIXDEP_SCRIPTS_SURFACE_SHARED_MARKER_COUNT="
        f"{len(PHASE2_BOOTSTRAP_NOTES_MARKERS) + len(PHASE2_CLOSURE_DOC_MARKERS) + len(TESTS_README_MARKERS) + len(WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
