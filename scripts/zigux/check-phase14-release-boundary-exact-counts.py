#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

DOCS_ROOT_CHECKER_SNIPPETS = [
    "RELEASE_BOUNDARY_LINES = [",
    '"PHASE14_RELEASE_BOUNDARY=present"',
    '"PHASE14_SHARED_REPLAY_PRESENT=yes"',
    '"PHASE14_RELEASE_CLOSED=no"',
    '"shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture"',
    'require_exact_count("release_boundary", release_boundary_text, RELEASE_BOUNDARY_LINES)',
]

RELEASE_BOUNDARY_LINES = [
    "PHASE14_RELEASE_BOUNDARY=present",
    "PHASE14_SHARED_REPLAY_PRESENT=yes",
    "PHASE14_RELEASE_CLOSED=no",
    "shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture",
    "compile-shard matrix: one focused `phase14-smoke` shard still covers only `phase14-end-to-end-smoke-tests`, while `phase14-workqueue-bridge-tests`, `phase14-skbuff-bridge-tests`, `phase14-ring-buffer-survey-tests`, and `phase14-rcu-tree-survey-tests` remain `full_bundle_only` under `zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
    "combined shared replay entrypoint: `make -C zigux phase14` remains the published convenience route for the validator-backed smoke packet, so release-facing review and local replay still name the same one-command path as the shared smoke note and manifest instead of leaving that wrapper path implicit in `zigux/Makefile`",
    "wrapper-backed full-bundle replay: `make -C zigux phase14-test` remains the smallest make-surface route for the shared full-bundle compile matrix, so release-facing review can name the same wrapper-backed internal-bridge replay that `zigux/Makefile` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` already publish instead of relying only on the raw `zig build test --build-file zigux/tests/phase14_build.zig --summary all` command",
    "PHASE14_SHARED_SMOKE_GATE_COUNT=1",
    "PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0",
]

SURVEY_EXACT_LINE_SNIPPETS = [
    "- `PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14`",
    "- `PHASE14_FULL_BUNDLE_DEPENDENCY_COUNT=5`",
    "- `PHASE14_FOCUSED_SHARD_COUNT=1`",
    "- `PHASE14_FOCUSED_SHARD_DEPENDENCY_COUNT=1`",
    "- `PHASE14_FOCUSED_SHARD_ONLY_ARTIFACT=phase14-end-to-end-smoke-tests`",
    "- `PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4`",
]

MAKEFILE_SNIPPETS = [
    "phase14-validate:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_exact_line(text: str, snippet: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == snippet)


def require_exact_count(label: str, text: str, snippets: list[str]) -> list[str]:
    issues: list[str] = []
    for snippet in snippets:
        actual = text.count(snippet)
        if actual != 1:
            issues.append(f"{label}:{actual}:{snippet}")
    return issues


def require_exact_line_count(label: str, text: str, snippets: list[str]) -> list[str]:
    issues: list[str] = []
    for snippet in snippets:
        actual = count_exact_line(text, snippet)
        if actual != 1:
            issues.append(f"{label}:{actual}:{snippet}")
    return issues


def validate_alignment(
    docs_root_checker_text: str,
    release_boundary_text: str,
    survey_text: str,
    makefile_text: str,
) -> list[str]:
    issues = require_exact_count("docs_root_checker", docs_root_checker_text, DOCS_ROOT_CHECKER_SNIPPETS)
    issues.extend(require_exact_count("release_boundary", release_boundary_text, RELEASE_BOUNDARY_LINES))
    issues.extend(require_exact_line_count("survey", survey_text, SURVEY_EXACT_LINE_SNIPPETS))
    issues.extend(require_exact_line_count("makefile", makefile_text, MAKEFILE_SNIPPETS))
    return issues


def run_self_test() -> int:
    docs_root_checker_text = """
RELEASE_BOUNDARY_LINES = [
    "PHASE14_RELEASE_BOUNDARY=present",
    "PHASE14_SHARED_REPLAY_PRESENT=yes",
    "PHASE14_RELEASE_CLOSED=no",
    "shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture",
]
issues = require_exact_count("release_boundary", release_boundary_text, RELEASE_BOUNDARY_LINES)
""".strip()

    release_boundary_text = """
- PHASE14_RELEASE_BOUNDARY=present
- PHASE14_SHARED_REPLAY_PRESENT=yes
- PHASE14_RELEASE_CLOSED=no
- shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture
- compile-shard matrix: one focused `phase14-smoke` shard still covers only `phase14-end-to-end-smoke-tests`, while `phase14-workqueue-bridge-tests`, `phase14-skbuff-bridge-tests`, `phase14-ring-buffer-survey-tests`, and `phase14-rcu-tree-survey-tests` remain `full_bundle_only` under `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
- combined shared replay entrypoint: `make -C zigux phase14` remains the published convenience route for the validator-backed smoke packet, so release-facing review and local replay still name the same one-command path as the shared smoke note and manifest instead of leaving that wrapper path implicit in `zigux/Makefile`
- wrapper-backed full-bundle replay: `make -C zigux phase14-test` remains the smallest make-surface route for the shared full-bundle compile matrix, so release-facing review can name the same wrapper-backed internal-bridge replay that `zigux/Makefile` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` already publish instead of relying only on the raw `zig build test --build-file zigux/tests/phase14_build.zig --summary all` command
- PHASE14_SHARED_SMOKE_GATE_COUNT=1
- PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0
""".strip()

    survey_text = """
- `PHASE14_COMBINED_ENTRYPOINT=make -C zigux phase14`
- `PHASE14_FULL_BUNDLE_DEPENDENCY_COUNT=5`
- `PHASE14_FOCUSED_SHARD_COUNT=1`
- `PHASE14_FOCUSED_SHARD_DEPENDENCY_COUNT=1`
- `PHASE14_FOCUSED_SHARD_ONLY_ARTIFACT=phase14-end-to-end-smoke-tests`
- `PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4`
""".strip()

    makefile_text = """
phase14-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py
""".strip()

    good = validate_alignment(docs_root_checker_text, release_boundary_text, survey_text, makefile_text)
    bad_docs_root_checker = validate_alignment(
        docs_root_checker_text.replace(
            '`scripts/zigux/check-phase14-release-boundary-exact-counts.py`, ',
            "",
            1,
        ),
        release_boundary_text,
        survey_text,
        makefile_text,
    )
    bad_release_boundary = validate_alignment(
        docs_root_checker_text,
        release_boundary_text.replace("- PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0", "", 1),
        survey_text,
        makefile_text,
    )
    duplicate_release_boundary = validate_alignment(
        docs_root_checker_text,
        release_boundary_text + "\n- PHASE14_SHARED_SMOKE_GATE_COUNT=1",
        survey_text,
        makefile_text,
    )
    bad_survey = validate_alignment(
        docs_root_checker_text,
        release_boundary_text,
        survey_text.replace("- `PHASE14_FOCUSED_SHARD_ONLY_ARTIFACT=phase14-end-to-end-smoke-tests`\n", "", 1),
        makefile_text,
    )
    duplicate_survey = validate_alignment(
        docs_root_checker_text,
        release_boundary_text,
        survey_text + "\n- `PHASE14_FOCUSED_SHARD_COUNT=1`",
        makefile_text,
    )
    if good or not bad_docs_root_checker or not bad_release_boundary or not duplicate_release_boundary or not bad_survey or not duplicate_survey:
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=fail")
        return 1

    print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass")
    print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST_CASE_COUNT=6")
    return 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        return run_self_test()

    docs_root_checker_path = ROOT / "scripts/zigux/check-phase14-docs-root-smoke-summary.py"
    release_boundary_path = ROOT / "Documentation/zigux/phase14-release-boundary-survey.md"
    survey_path = ROOT / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
    makefile_path = ROOT / "zigux/Makefile"
    required_paths = [docs_root_checker_path, release_boundary_path, survey_path, makefile_path]
    missing_files = [str(path) for path in required_paths if not path.exists()]
    if missing_files:
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=fail")
        print("MISSING_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_FILES_END")
        return 1

    issues = validate_alignment(
        read(docs_root_checker_path),
        read(release_boundary_path),
        read(survey_path),
        read(makefile_path),
    )
    if issues:
        print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=fail")
        print("ISSUES_START")
        for issue in issues:
            print(issue)
        print("ISSUES_END")
        return 1

    print("PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=pass")
    print(f"PHASE14_DOCS_ROOT_CHECKER_SNIPPET_COUNT={len(DOCS_ROOT_CHECKER_SNIPPETS)}")
    print(f"PHASE14_RELEASE_BOUNDARY_LINE_COUNT={len(RELEASE_BOUNDARY_LINES)}")
    print(f"PHASE14_SURVEY_EXACT_LINE_SNIPPET_COUNT={len(SURVEY_EXACT_LINE_SNIPPETS)}")
    print(f"PHASE14_MAKEFILE_SNIPPET_COUNT={len(MAKEFILE_SNIPPETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
