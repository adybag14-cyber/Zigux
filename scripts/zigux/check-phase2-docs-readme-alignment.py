#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

DOCS_README = Path("Documentation/zigux/README.md")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
MAKEFILE = Path("zigux/Makefile")
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_FILES = (
    DOCS_README,
    PHASE2_CLOSURE,
    SCRIPTS_README,
    TESTS_README,
    MAKEFILE,
    MANIFEST,
)

DOCS_REQUIRED_MARKERS = (
    "Phase 2 notes - `Documentation/zigux/phase2-closure.md`",
    "`scripts/zigux/check-phase2-tool-manifest.py` and `zigux/tests/fixtures/phase2_tool_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the fixture-backed Phase 2 manifest packet explicit from the docs root beside the shipped reminder and make-wrapper surfaces.",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master` again, so keep the installer and direct cross-route packet explicit beside the shipped toolchain, kconfig, genksyms, and make-wrapper surfaces instead of leaving them in historical-gap wording.",
    "`scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep` are directly readable on current `master` again, so keep the returned fixdep governance, parity, helper, fixture, and wrapper packet explicit beside the shipped toolchain, kconfig, and genksyms surfaces instead of leaving fixdep implicit in the broader Phase 2 reminder.",
    "`python3 scripts/zigux/validate-phase2.py`, `python3 scripts/zigux/validate-phase2-closure.py`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2` replay the bounded current Phase 2 closure-side, bounded genksyms bridge, and make-wrapper packet without widening it back into older missing-route assumptions.",
)

CLOSURE_REQUIRED_MARKERS = (
    "`PHASE2_CURRENT_CLOSURE_PACKET=",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`PHASE2_CLOSURE_VALIDATORS=",
    "`PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`",
)

SCRIPTS_REQUIRED_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`",
    "`third_party/README.md`, `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the staged repo-local archive helper, contract, and self-test packet explicit from the scripts root beside that same shipped Lane 05 local-first archive path",
    "`Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, `make -C zigux phase2`, `zigux/tests/fixtures/phase2_tool_manifest.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` keep the shipped closure-side reminder, closure-validator, validator entrypoint, make-wrapper, and artifact-support packet explicit from the scripts root beside the surviving checker set",
)

TESTS_REQUIRED_MARKERS = (
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",
    "current `master` now directly materializes `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so keep that returned installer, direct cross-route, and cross-target fixture packet explicit here instead of leaving it in the historical-gap bucket",
    "current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

REQUIRED_MANIFEST_VALUES = {
    "phase": "Phase 2",
    "status": "active",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
    "present_surfaces.review_surfaces": (
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/README.md",
    ),
    "present_surfaces.closure_notes": (
        "Documentation/zigux/phase2-closure.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    ),
    "present_surfaces.validators": (
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
    ),
    "present_surfaces.make_wrappers": (
        "zigux/Makefile",
        "make -C zigux phase2-toolchain",
        "make -C zigux phase2-tools",
        "make -C zigux phase2-kconfig",
        "make -C zigux phase2-cross",
        "make -C zigux phase2-genksyms",
        "make -C zigux phase2-fixdep",
        "make -C zigux phase2-validate",
        "make -C zigux phase2",
    ),
}


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_manifest(root: Path) -> dict[str, object]:
    return json.loads(read_text(root, MANIFEST))


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def manifest_get(manifest: dict[str, object], dotted_key: str) -> object:
    value: object = manifest
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def expect_markers(failures: list[str], label: str, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:missing:{marker}")


def expect_manifest_values(failures: list[str], manifest: dict[str, object]) -> None:
    for key, expected in REQUIRED_MANIFEST_VALUES.items():
        actual = manifest_get(manifest, key)
        if isinstance(expected, tuple):
            if not isinstance(actual, list):
                failures.append(f"manifest:missing_list:{key}")
                continue
            for item in expected:
                if item not in actual:
                    failures.append(f"manifest:missing_value:{key}:{item}")
        elif actual != expected:
            failures.append(f"manifest:wrong_value:{key}:{actual!r}")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    docs_readme = read_text(root, DOCS_README)
    closure = read_text(root, PHASE2_CLOSURE)
    scripts_readme = read_text(root, SCRIPTS_README)
    tests_readme = read_text(root, TESTS_README)
    makefile = read_text(root, MAKEFILE)
    manifest = load_manifest(root)

    expect_markers(failures, "docs_readme", docs_readme, DOCS_REQUIRED_MARKERS)
    expect_markers(failures, "closure_note", closure, CLOSURE_REQUIRED_MARKERS)
    expect_markers(failures, "scripts_readme", scripts_readme, SCRIPTS_REQUIRED_MARKERS)
    expect_markers(failures, "tests_readme", tests_readme, TESTS_REQUIRED_MARKERS)

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile, marker)
        if count == 0:
            failures.append(f"makefile:missing:{marker}")
        elif count != 1:
            failures.append(f"makefile:duplicate:{marker}:count={count}")

    expect_manifest_values(failures, manifest)
    return failures


def sample_docs_readme() -> str:
    return "\n".join(
        [
            "# Zigux Documentation",
            "",
            DOCS_REQUIRED_MARKERS[0],
            "",
            DOCS_REQUIRED_MARKERS[1],
            DOCS_REQUIRED_MARKERS[2],
            DOCS_REQUIRED_MARKERS[3],
            DOCS_REQUIRED_MARKERS[4],
            DOCS_REQUIRED_MARKERS[5],
            "",
        ]
    )


def sample_closure_note() -> str:
    return "\n".join(["# Phase 2 Closure", "", *CLOSURE_REQUIRED_MARKERS, ""])


def sample_scripts_readme() -> str:
    return "\n".join(["# scripts/zigux", "", *SCRIPTS_REQUIRED_MARKERS, ""])


def sample_tests_readme() -> str:
    return "\n".join(["# zigux/tests", "", *TESTS_REQUIRED_MARKERS, ""])


def sample_makefile() -> str:
    return "\n".join(
        [
            "PYTHON ?= python3",
            "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
            "",
            "phase2-toolchain:",
            "phase2-tools:",
            "phase2-kconfig:",
            "phase2-cross:",
            "phase2-genksyms:",
            "phase2-fixdep:",
            *REQUIRED_MAKEFILE_LINES,
            "",
        ]
    )


def sample_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 2",
        "status": "active",
        "workflow": ".github/workflows/zigux-bootstrap.yml",
        "present_surfaces": {
            "review_surfaces": list(REQUIRED_MANIFEST_VALUES["present_surfaces.review_surfaces"]),
            "closure_notes": list(REQUIRED_MANIFEST_VALUES["present_surfaces.closure_notes"]),
            "validators": list(REQUIRED_MANIFEST_VALUES["present_surfaces.validators"]),
            "make_wrappers": list(REQUIRED_MANIFEST_VALUES["present_surfaces.make_wrappers"]),
        },
    }


def seed(root: Path) -> None:
    write_text(root, DOCS_README, sample_docs_readme())
    write_text(root, PHASE2_CLOSURE, sample_closure_note())
    write_text(root, SCRIPTS_README, sample_scripts_readme())
    write_text(root, TESTS_README, sample_tests_readme())
    write_text(root, MAKEFILE, sample_makefile())
    write_text(root, MANIFEST, json.dumps(sample_manifest(), indent=2) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_docs_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        seed(root)
        if collect_failures(root):
            raise AssertionError(f"baseline should pass: {collect_failures(root)}")
        checks += 1

        mutated = root / "missing_docs_marker"
        seed(mutated)
        write_text(mutated, DOCS_README, replace_once(sample_docs_readme(), DOCS_REQUIRED_MARKERS[3]))
        expected = [f"docs_readme:missing:{DOCS_REQUIRED_MARKERS[3]}"]
        if collect_failures(mutated) != expected:
            raise AssertionError(collect_failures(mutated))
        checks += 1

        mutated = root / "missing_closure_marker"
        seed(mutated)
        write_text(mutated, PHASE2_CLOSURE, replace_once(sample_closure_note(), CLOSURE_REQUIRED_MARKERS[1]))
        expected = [f"closure_note:missing:{CLOSURE_REQUIRED_MARKERS[1]}"]
        if collect_failures(mutated) != expected:
            raise AssertionError(collect_failures(mutated))
        checks += 1

        mutated = root / "missing_scripts_marker"
        seed(mutated)
        write_text(mutated, SCRIPTS_README, replace_once(sample_scripts_readme(), SCRIPTS_REQUIRED_MARKERS[1]))
        expected = [f"scripts_readme:missing:{SCRIPTS_REQUIRED_MARKERS[1]}"]
        if collect_failures(mutated) != expected:
            raise AssertionError(collect_failures(mutated))
        checks += 1

        mutated = root / "missing_tests_marker"
        seed(mutated)
        write_text(mutated, TESTS_README, replace_once(sample_tests_readme(), TESTS_REQUIRED_MARKERS[2]))
        expected = [f"tests_readme:missing:{TESTS_REQUIRED_MARKERS[2]}"]
        if collect_failures(mutated) != expected:
            raise AssertionError(collect_failures(mutated))
        checks += 1

        mutated = root / "missing_makefile_line"
        seed(mutated)
        write_text(mutated, MAKEFILE, replace_once(sample_makefile(), REQUIRED_MAKEFILE_LINES[2] + "\n"))
        expected = [f"makefile:missing:{REQUIRED_MAKEFILE_LINES[2]}"]
        if collect_failures(mutated) != expected:
            raise AssertionError(collect_failures(mutated))
        checks += 1

        mutated = root / "duplicate_makefile_line"
        seed(mutated)
        duplicated = sample_makefile().replace(
            REQUIRED_MAKEFILE_LINES[3],
            REQUIRED_MAKEFILE_LINES[3] + "\n" + REQUIRED_MAKEFILE_LINES[3],
            1,
        )
        write_text(mutated, MAKEFILE, duplicated)
        expected = [f"makefile:duplicate:{REQUIRED_MAKEFILE_LINES[3]}:count=2"]
        if collect_failures(mutated) != expected:
            raise AssertionError(collect_failures(mutated))
        checks += 1

        mutated = root / "manifest_missing_value"
        seed(mutated)
        manifest = sample_manifest()
        manifest["present_surfaces"]["validators"] = ["scripts/zigux/validate-phase2.py"]
        write_text(mutated, MANIFEST, json.dumps(manifest, indent=2) + "\n")
        expected = [
            "manifest:missing_value:present_surfaces.validators:scripts/zigux/validate-phase2-closure.py"
        ]
        if collect_failures(mutated) != expected:
            raise AssertionError(collect_failures(mutated))
        checks += 1

    print("PHASE2_DOCS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_DOCS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def write_sample_root(target: Path) -> None:
    seed(target)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the docs-root Phase 2 reminder stays aligned with the shipped closure-side packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal current-like sample root for focused replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE2_DOCS_README_ALIGNMENT_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root.resolve())
    if failures:
        print("PHASE2_DOCS_README_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE2_DOCS_README_ALIGNMENT=pass")
    print(f"PHASE2_DOCS_README_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_DOCS_README_ALIGNMENT_REQUIRED_DOC_MARKER_COUNT={len(DOCS_REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
