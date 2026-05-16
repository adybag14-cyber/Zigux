#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()
README_REL = "scripts/zigux/README.md"
DOCS_README_REL = "Documentation/zigux/README.md"
MAKEFILE_REL = "zigux/Makefile"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
REVIEW_PROCESS_NOTE_REL = "Documentation/zigux/phase15-architecture-council-review-process.md"
HANDOFF_NEXT_STEPS_NOTE_REL = "Documentation/zigux/phase15-handoff-next-steps-survey.md"
READINESS_GATE_NOTE_REL = "Documentation/zigux/phase15-readiness-gate-survey.md"
PARITY_SCORECARD_NOTE_REL = "Documentation/zigux/phase15-parity-scorecard.md"
TESTS_README_REL = "zigux/tests/README.md"
HANDOFF_CHECKER_REL = "scripts/zigux/check-phase15-review-process-handoff.py"
DOCS_CHECKER_REL = "scripts/zigux/check-phase15-docs-readme-alignment.py"
SHARED_SUMMARY_CHECKER_REL = "scripts/zigux/check-phase15-shared-summary-gap.py"
MANIFEST_REL = "zigux/tests/phase15_architecture_council_review_process_manifest.json"
BUILD_REL = "zigux/tests/phase15_build.zig"

REQUIRED_FILES = (
    README_REL,
    DOCS_README_REL,
    MAKEFILE_REL,
    WORKFLOW_REL,
    REVIEW_CHECKLIST_REL,
    REVIEW_PROCESS_NOTE_REL,
    HANDOFF_NEXT_STEPS_NOTE_REL,
    READINESS_GATE_NOTE_REL,
    TESTS_README_REL,
    HANDOFF_CHECKER_REL,
    DOCS_CHECKER_REL,
    SHARED_SUMMARY_CHECKER_REL,
    MANIFEST_REL,
    BUILD_REL,
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    PARITY_SCORECARD_NOTE_REL,
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate.zig",
)

README_MARKERS = (
    "Phase 15 flow",
    "check-phase15-docs-readme-alignment.py",
    "check-phase15-scripts-readme-alignment.py",
    "check-phase15-review-process-handoff.py",
    "check-phase15-shared-summary-gap.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "no-approval",
    "reopen-trigger",
)

DOCS_README_MARKERS = (
    "Phase 15 notes",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
)

MAKEFILE_MARKERS = (
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/check-phase15-docs-readme-alignment.py --self-test",
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py --self-test",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "phase15-test:",
    "$(ZIG) build test --build-file zigux/tests/phase15_build.zig",
    "phase15: phase15-validate phase15-test",
)

WORKFLOW_MARKERS = (
    "Validate Phase 15 governance packet",
    "make -C zigux phase15-validate",
    "Run Phase 15 governance tests",
    "make -C zigux phase15-test",
)

REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 15 governance packet",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
)

REVIEW_PROCESS_NOTE_MARKERS = (
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "reopen triggers",
    "Keep the Phase 15 governance lane in maintenance mode.",
)

PARITY_SCORECARD_MARKERS = (
    "shared validator-first gate through",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "make -C zigux phase15-validate",
)

TESTS_README_MARKERS = (
    "keep the parked Phase 15 governance packet explicit in the tests root too:",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
)

HANDOFF_CHECKER_MARKERS = (
    'NOTE_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md"',
    'MANIFEST_PATH = "zigux/tests/phase15_architecture_council_review_process_manifest.json"',
    'print("PHASE15_REVIEW_PROCESS_HANDOFF=pass")',
)

MANIFEST_LANE_MARKERS = (
    "scripts-root validator path",
    "Linux-style `make -C zigux phase15-validate` route",
    "tests-root guidance path",
    "dedicated handoff-checker route",
)

CURRENT_REPO_HANDOFF_MARKERS = (
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_build.zig",
)

BUILD_MARKERS = (
    'b.path("phase15_freeze_map_governance.zig")',
    'b.path("phase15_parity_scorecard.zig")',
    'b.path("phase15_architecture_council_review_process.zig")',
    'b.path("phase15_handoff_next_steps.zig")',
    'b.path("phase15_indefinite_c_policy.zig")',
    'b.path("phase15_indefinite_c_lane_owner_alignment.zig")',
    'b.path("phase15_readiness_gate.zig")',
    'b.step("test", "Run Phase 15 governance tests")',
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_markers_present(text: str, markers: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append(f"{prefix}:missing:{marker}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    readme = _read(root / README_REL)
    docs_readme = _read(root / DOCS_README_REL)
    makefile = _read(root / MAKEFILE_REL)
    workflow = _read(root / WORKFLOW_REL)
    handoff_checker = _read(root / HANDOFF_CHECKER_REL)
    review_checklist = _read(root / REVIEW_CHECKLIST_REL)
    review_process_note = _read(root / REVIEW_PROCESS_NOTE_REL)
    parity_scorecard = _read(root / PARITY_SCORECARD_NOTE_REL)
    tests_readme = _read(root / TESTS_README_REL)
    manifest = json.loads(_read(root / MANIFEST_REL))
    build = _read(root / BUILD_REL)

    _require_markers_present(readme, README_MARKERS, "readme", issues)
    _require_markers_present(docs_readme, DOCS_README_MARKERS, "docs_readme", issues)
    _require_markers_present(makefile, MAKEFILE_MARKERS, "makefile", issues)
    _require_markers_present(workflow, WORKFLOW_MARKERS, "workflow", issues)
    _require_markers_present(handoff_checker, HANDOFF_CHECKER_MARKERS, "handoff_checker", issues)
    _require_markers_present(review_checklist, REVIEW_CHECKLIST_MARKERS, "review_checklist", issues)
    _require_markers_present(review_process_note, REVIEW_PROCESS_NOTE_MARKERS, "review_process_note", issues)
    _require_markers_present(parity_scorecard, PARITY_SCORECARD_MARKERS, "parity_scorecard", issues)
    _require_markers_present(tests_readme, TESTS_README_MARKERS, "tests_readme", issues)
    _require_markers_present(build, BUILD_MARKERS, "build", issues)

    handoff_evidence = manifest.get("handoff_evidence")
    if not isinstance(handoff_evidence, dict):
        issues.append("manifest:missing:handoff_evidence")
    else:
        current_repo_handoff = handoff_evidence.get("current_repo_handoff")
        if not isinstance(current_repo_handoff, str):
            issues.append("manifest:missing:handoff_evidence.current_repo_handoff")
        else:
            _require_markers_present(current_repo_handoff, CURRENT_REPO_HANDOFF_MARKERS, "manifest_current_repo_handoff", issues)
        current_bounded_lane = handoff_evidence.get("current_bounded_lane")
        if not isinstance(current_bounded_lane, str):
            issues.append("manifest:missing:handoff_evidence.current_bounded_lane")
        else:
            _require_markers_present(current_bounded_lane, MANIFEST_LANE_MARKERS, "manifest_current_bounded_lane", issues)

    return issues


def _baseline_readme() -> str:
    return "\n".join(
        (
            "# scripts/zigux",
            "",
            "Phase 15 flow",
            "- `check-phase15-docs-readme-alignment.py` remains part of the parked Phase 15 validator-first route.",
            "- `check-phase15-scripts-readme-alignment.py` remains part of the parked Phase 15 validator-first route.",
            "- `check-phase15-review-process-handoff.py` remains part of the parked Phase 15 validator-first route.",
            "- `check-phase15-shared-summary-gap.py` remains the dedicated shared-summary drift guard for the parked Phase 15 governance packet's docs-root, checklist, scripts-root, and tests-root reminder wording, including the no-approval and reopen-trigger maintenance posture that must stay explicit without widening into a freeze-map status change.",
            "- `make -C zigux phase15-validate` now reruns `validate-phase15.py`, `check-phase15-docs-readme-alignment.py`, `check-phase15-scripts-readme-alignment.py`, `check-phase15-review-process-handoff.py`, and `check-phase15-shared-summary-gap.py` together so the shipped validator-first route covers the broad readiness packet, the docs-root and scripts-root shared-summary guards, and the dedicated parity-scorecard reporting packet before `make -C zigux phase15-test` replays `zigux/tests/phase15_build.zig`.",
            "- `make -C zigux phase15` remains the parked convenience route.",
            "",
        )
    )


def _baseline_docs_readme() -> str:
    return "\n".join(("# Zigux Documentation", "", "Phase 15 notes", "- Documentation/zigux/phase15-governance-lane-sequencing.md", "- scripts/zigux/check-phase15-scripts-readme-alignment.py", "- make -C zigux phase15-validate", "- make -C zigux phase15-test", "- make -C zigux phase15", ""))


def _baseline_makefile() -> str:
    return "\n".join(
        (
            "PHONY += phase15-validate phase15-test phase15",
            "",
            "phase15-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-docs-readme-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-docs-readme-alignment.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-shared-summary-gap.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-shared-summary-gap.py",
            "",
            "phase15-test:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase15_build.zig",
            "",
            "phase15: phase15-validate phase15-test",
            "",
        )
    )


def _baseline_workflow() -> str:
    return "\n".join(("Validate Phase 15 governance packet", "make -C zigux phase15-validate", "Run Phase 15 governance tests", "make -C zigux phase15-test", ""))


def _baseline_handoff_checker() -> str:
    return "\n".join((
        '#!/usr/bin/env python3',
        'NOTE_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md"',
        'MANIFEST_PATH = "zigux/tests/phase15_architecture_council_review_process_manifest.json"',
        'print("PHASE15_REVIEW_PROCESS_HANDOFF=pass")',
        "",
    ))


def _baseline_review_checklist() -> str:
    return "\n".join(("# Checklist", "- if the change touches the shared Phase 15 governance packet", "- scripts/zigux/check-phase15-scripts-readme-alignment.py", "- scripts/zigux/check-phase15-review-process-handoff.py", "- make -C zigux phase15-validate", "- make -C zigux phase15", ""))


def _baseline_review_process_note() -> str:
    return "\n".join(("# Phase 15", "- no Architecture Council approval is currently recorded for a freeze-map status change", "- reopen triggers remain attached", "- Keep the Phase 15 governance lane in maintenance mode.", ""))


def _baseline_parity_scorecard() -> str:
    return "\n".join(("# Phase 15 Parity Scorecard", "", "shared validator-first gate through", "scripts/zigux/check-phase15-scripts-readme-alignment.py", "scripts/zigux/check-phase15-review-process-handoff.py", "make -C zigux phase15-validate", ""))


def _baseline_tests_readme() -> str:
    return "\n".join(("# zigux/tests", "", "keep the parked Phase 15 governance packet explicit in the tests root too:", "scripts/zigux/check-phase15-scripts-readme-alignment.py", "scripts/zigux/check-phase15-review-process-handoff.py", "zigux/tests/phase15_handoff_next_steps_manifest.json", "zigux/tests/phase15_readiness_gate_manifest.json", "make -C zigux phase15-validate", "make -C zigux phase15-test", "make -C zigux phase15", ""))


def _baseline_manifest() -> str:
    return json.dumps({
        "handoff_evidence": {
            "current_repo_handoff": "Documentation/zigux/phase15-freeze-map-governance.md Documentation/zigux/phase15-governance-lane-sequencing.md scripts/zigux/README.md zigux/tests/README.md zigux/Makefile .github/workflows/zigux-bootstrap.yml scripts/zigux/check-phase15-scripts-readme-alignment.py scripts/zigux/check-phase15-review-process-handoff.py zigux/tests/phase15_indefinite_c_blocker_evidence.zig zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig zigux/tests/phase15_governance_lane_sequencing.zig zigux/tests/phase15_build.zig",
            "current_bounded_lane": "scripts-root validator path Linux-style `make -C zigux phase15-validate` route tests-root guidance path dedicated handoff-checker route",
        }
    }, indent=2) + "\n"


def _baseline_build() -> str:
    return "\n".join((
        'b.path("phase15_freeze_map_governance.zig")',
        'b.path("phase15_parity_scorecard.zig")',
        'b.path("phase15_architecture_council_review_process.zig")',
        'b.path("phase15_handoff_next_steps.zig")',
        'b.path("phase15_indefinite_c_policy.zig")',
        'b.path("phase15_indefinite_c_lane_owner_alignment.zig")',
        'b.path("phase15_readiness_gate.zig")',
        'b.step("test", "Run Phase 15 governance tests")',
        "",
    ))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write(root / README_REL, _baseline_readme())
        _write(root / DOCS_README_REL, _baseline_docs_readme())
        _write(root / MAKEFILE_REL, _baseline_makefile())
        _write(root / WORKFLOW_REL, _baseline_workflow())
        _write(root / HANDOFF_CHECKER_REL, _baseline_handoff_checker())
        _write(root / REVIEW_CHECKLIST_REL, _baseline_review_checklist())
        _write(root / REVIEW_PROCESS_NOTE_REL, _baseline_review_process_note())
        _write(root / PARITY_SCORECARD_NOTE_REL, _baseline_parity_scorecard())
        _write(root / TESTS_README_REL, _baseline_tests_readme())
        _write(root / MANIFEST_REL, _baseline_manifest())
        _write(root / BUILD_REL, _baseline_build())
        for rel in REQUIRED_FILES:
            path = root / rel
            if not path.exists():
                _write(path, "placeholder\n")
        issues = validate(root)
    if issues:
        for issue in issues:
            print(issue)
        return 1
    print("PHASE15_SCRIPTS_README_ALIGNMENT=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in fixture test")
    args = parse_args()
    if args.self_test:
        return run_self_test()
    issues = validate(ROOT)
    if issues:
        for issue in issues:
            print(issue)
        return 1
    print("PHASE15_SCRIPTS_README_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
