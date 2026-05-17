#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PHASE2_CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
ALIGNMENT_CHECKERS = (
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
)

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/validate-phase2-closure.py",
    "zigux/tests/README.md",
)

DOC_MARKERS = (
    "`PHASE2_STATUS=active`",
    "`PHASE2_CLOSURE_MODE=current-master-safe`",
    "`PHASE2_LANE24_PACKET_STATUS=partial_restore`",
    "`PHASE2_SHARED_ALIGNMENT_PACKET_COUNT=3`",
    "`PHASE2_SHARED_ALIGNMENT_PACKET=scripts/zigux/check-phase2-tests-readme-alignment.py,scripts/zigux/check-phase2-kconfig-selftest-alignment.py,scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "repeated authenticated reads on current `master` still returned missing for:",
    "`scripts/zigux/validate-phase2.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "restore the missing `zigux/Makefile`, `scripts/zigux/validate-phase2.py`, and",
)


def derive_root(script_path: Path, override: Path | None) -> Path:
    return override.resolve() if override is not None else script_path.resolve().parents[2]


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            issues.append(f"missing-file:{rel_path}")

    doc_path = root / "Documentation" / "zigux" / "phase2-closure.md"
    if not doc_path.exists():
        issues.append("missing-phase2-closure-doc")
        return issues

    doc_text = doc_path.read_text(encoding="utf-8")
    for marker in DOC_MARKERS:
        if marker not in doc_text:
            issues.append(f"missing-doc-marker:{marker}")

    for checker in (
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    ):
        if checker not in doc_text:
            issues.append(f"missing-doc-checker:{checker}")

    return issues


def build_selftest_tree(temp_root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        path = temp_root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path == "Documentation/zigux/phase2-closure.md":
            path.write_text(PHASE2_CLOSURE_DOC.read_text(encoding="utf-8"), encoding="utf-8")
        elif rel_path == "scripts/zigux/validate-phase2-closure.py":
            path.write_text("# self-test placeholder\n", encoding="utf-8")
        else:
            path.write_text(f"placeholder for {rel_path}\n", encoding="utf-8")


def run_self_test() -> list[str]:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        build_selftest_tree(temp_root)

        issues = collect_issues(temp_root)
        if issues:
            failures.append("expected clean synthetic tree")
            failures.extend(issues)

        doc_path = temp_root / "Documentation" / "zigux" / "phase2-closure.md"
        doc_path.write_text(
            doc_path.read_text(encoding="utf-8").replace(
                "`PHASE2_CLOSURE_MODE=current-master-safe`",
                "`PHASE2_CLOSURE_MODE=broken`",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(temp_root)
        if "missing-doc-marker:`PHASE2_CLOSURE_MODE=current-master-safe`" not in issues:
            failures.append("expected missing closure mode marker failure")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        failures = run_self_test()
        if failures:
            for failure in failures:
                print(failure)
            return 1
        print("PHASE2_CLOSURE_VALIDATOR_SELF_TEST=pass")
        print("PHASE2_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=2")
        return 0

    root = derive_root(Path(__file__), args.root)
    issues = collect_issues(root)
    if issues:
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print("PHASE2_CLOSURE_MODE=current-master-safe")
    print(f"PHASE2_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
