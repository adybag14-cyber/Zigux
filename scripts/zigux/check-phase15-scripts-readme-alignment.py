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
MANIFEST_REL = "zigux/tests/phase15_architecture_council_review_process_manifest.json"
READINESS_MANIFEST_REL = "zigux/tests/phase15_readiness_gate_manifest.json"
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
    MANIFEST_REL,
    READINESS_MANIFEST_REL,
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

README_SNIPPETS = (
    "- the current shared Phase 15 governance surface on `master` is `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_readiness_gate.zig`, and `zigux/tests/phase15_build.zig`.",
    "- `validate-phase15.py` keeps the shared `phase15-validate` route fail-closed on the parked Phase 15 readiness packet and the parity scorecard's machine-reported review-field and aggregate-metric surface before the narrower handoff checkers run.",
    "- `make -C zigux phase15-validate` now reruns `validate-phase15.py`, `check-phase15-scripts-readme-alignment.py`, and `check-phase15-review-process-handoff.py` together so the shipped validator-first route covers both the broad readiness packet and the dedicated parity-scorecard reporting packet before `make -C zigux phase15-test` replays `zigux/tests/phase15_build.zig`.",
    "- `check-phase15-scripts-readme-alignment.py` keeps `scripts/zigux/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, `zigux/tests/phase15_governance_lane_sequencing.zig`, and `zigux/tests/phase15_build.zig` aligned around the parked governance packet's scripts-root validator-first route and no-approval-yet posture.",
    "- `check-phase15-review-process-handoff.py` keeps the dedicated review-process note and its manifest-backed handoff evidence aligned around the self-reference, product-boundary, and parked-route markers that keep the Architecture Council packet reviewable without inventing a broader governance surface.",
    "- `zig build test --build-file zigux/tests/phase15_build.zig` and `make -C zigux phase15` rerun the parked freeze-map governance, parity-scorecard, Architecture Council review-process, handoff-next-steps, dedicated indefinite-C policy, lane-owner alignment, and readiness-gate packet without implying any new approval claim for a freeze-map anchor.",
    "- the current bounded Phase 15 decision is still to leave the lane parked unless a named reopen trigger fires or the deep-core blocker posture changes enough to justify another Architecture Council slice.",
)

DOCS_README_MARKERS = (
    "keep the parked Phase 15 governance packet explicit in the tests root too:",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/README.md",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_readiness_gate.zig",
    "zigux/Makefile",
    "scripts-root validator-first route",
    "shared build-and-make path",
    "make -C zigux phase15",
    "without implying any Architecture Council approval for a freeze-map status change",
)

MAKEFILE_REQUIRED = (
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py --self-test",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "phase15-test:",
    "$(ZIG) build test --build-file zigux/tests/phase15_build.zig",
    "phase15: phase15-validate phase15-test",
)

HANDOFF_CHECKER_MARKERS = (
    'NOTE_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md"',
    'MANIFEST_PATH = "zigux/tests/phase15_architecture_council_review_process_manifest.json"',
    '"scripts-root validator path"',
    'print("PHASE15_REVIEW_PROCESS_HANDOFF=pass")',
)

REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 15 governance packet",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15",
    "no-approval-yet posture",
)

WORKFLOW_MARKERS = (
    "Validate Phase 15 governance packet",
    "run: make -C zigux phase15-validate\n",
    "Run Phase 15 governance tests",
    "run: make -C zigux phase15-test\n",
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
    "make -C zigux phase15-test",
    "## Gates",
    "1. run the shared validator-first gate",
    "zig build test --build-file zigux/tests/phase15_build.zig",
    "make -C zigux phase15",
)

TESTS_README_MARKERS = (
    "keep the parked Phase 15 governance packet explicit in the tests root too:",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_ALIGNMENT.zig",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_readiness_gate.zig",
    "zigux/Makefile",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "shared build-and-make path",
    "make -C zigux phase15",
    "without implying any Architecture Council approval for a freeze-map status change",
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
    'b.path("phase15_indefinite_c_blocker_evidence.zig")',
    'b.path("phase15_indefinite_c_lane_owner_alignment.zig")',
    'b.path("phase15_governance_lane_sequencing.zig")',
    'b.path("phase15_readiness_gate.zig")',
    'b.step("test", "Run Phase 15 governance tests")',
)

READINESS_NOTE_MARKERS = (
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "make -C zigux phase15-validate",
    "phase15-deep-core-status-change-blocker",
)

READINESS_VALIDATE_CHECKERS = (
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_markers_exact_once(text: str, markers: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count == 0:
            issues.append(f"{prefix}:missing:{marker}")
        elif count != 1:
            issues.append(f"{prefix}:count:{count}:{marker}")


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
    readiness_note = _read(root / READINESS_GATE_NOTE_REL)
    readiness_manifest = json.loads(_read(root / READINESS_MANIFEST_REL))
    build = _read(root / BUILD_REL)

    _require_markers_exact_once(readme, README_SNIPPETS, "readme", issues)
    _require_markers_present(docs_readme, DOCS_README_MARKERS, "docs_readme", issues)
    _require_markers_present(makefile, MAKEFILE_REQUIRED, "makefile", issues)
    _require_markers_exact_once(workflow, WORKFLOW_MARKERS, "workflow", issues)
    _require_markers_present(handoff_checker, HANDOFF_CHECKER_MARKERS, "handoff_checker", issues)
    _require_markers_present(review_checklist, REVIEW_CHECKLIST_MARKERS, "review_checklist", issues)
    _require_markers_present(review_process_note, REVIEW_PROCESS_NOTE_MARKERS, "review_process_note", issues)
    _require_markers_present(parity_scorecard, PARITY_SCORECARD_MARKERS, "parity_scorecard", issues)
    _require_markers_present(tests_readme, TESTS_README_MARKERS, "tests_readme", issues)
    _require_markers_present(readiness_note, READINESS_NOTE_MARKERS, "readiness_note", issues)

    handoff_evidence = manifest.get("handoff_evidence")
    if not isinstance(handoff_evidence, dict):
        issues.append("manifest:missing:handoff_evidence")
    else:
        current_repo_handoff = handoff_evidence.get("current_repo_handoff")
        if not isinstance(current_repo_handoff, str):
            issues.append("manifest:missing:handoff_evidence.current_repo_handoff")
        else:
            _require_markers_present(
                current_repo_handoff,
                CURRENT_REPO_HANDOFF_MARKERS,
                "manifest_current_repo_handoff",
                issues,
            )

        current_bounded_lane = handoff_evidence.get("current_bounded_lane")
        if not isinstance(current_bounded_lane, str):
            issues.append("manifest:missing:handoff_evidence.current_bounded_lane")
        else:
            _require_markers_present(
                current_bounded_lane,
                MANIFEST_LANE_MARKERS,
                "manifest_current_bounded_lane",
                issues,
            )

    phase15_validate_checkers = readiness_manifest.get("phase15_validate_checkers")
    if not isinstance(phase15_validate_checkers, list):
        issues.append("readiness_manifest:missing:phase15_validate_checkers")
    else:
        for checker in READINESS_VALIDATE_CHECKERS:
            if checker not in phase15_validate_checkers:
                issues.append(f"readiness_manifest:missing:{checker}")
        if len(phase15_validate_checkers) != len(READINESS_VALIDATE_CHECKERS):
            issues.append(f"readiness_manifest:count:{len(phase15_validate_checkers)}")

    _require_markers_present(build, BUILD_MARKERS, "build", issues)
    return issues


def _seed_fixture_tree(root: Path) -> None:
    for rel in REQUIRED_FILES:
        target = root / rel
        if rel.endswith(".json"):
            _write(target, "{}\n")
        else:
            _write(target, f"# fixture for {rel}\n")

    _write(root / README_REL, "\n".join(README_SNIPPETS) + "\n")
    _write(root / DOCS_README_REL, "\n".join(DOCS_README_MARKERS) + "\n")
    _write(root / MAKEFILE_REL, "\n".join(MAKEFILE_REQUIRED) + "\n")
    _write(root / WORKFLOW_REL, "\n".join(WORKFLOW_MARKERS))
    _write(root / HANDOFF_CHECKER_REL, "\n".join(HANDOFF_CHECKER_MARKERS) + "\n")
    _write(root / REVIEW_CHECKLIST_REL, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    _write(root / REVIEW_PROCESS_NOTE_REL, "\n".join(REVIEW_PROCESS_NOTE_MARKERS) + "\n")
    _write(root / PARITY_SCORECARD_NOTE_REL, "\n".join(PARITY_SCORECARD_MARKERS) + "\n")
    _write(root / TESTS_README_REL, "\n".join(TESTS_README_MARKERS) + "\n")
    _write(root / READINESS_GATE_NOTE_REL, "\n".join(READINESS_NOTE_MARKERS) + "\n")
    _write(
        root / MANIFEST_REL,
        json.dumps(
            {
                "handoff_evidence": {
                    "current_repo_handoff": " ".join(CURRENT_REPO_HANDOFF_MARKERS),
                    "current_bounded_lane": " ".join(MANIFEST_LANE_MARKERS),
                }
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        root / READINESS_MANIFEST_REL,
        json.dumps(
            {
                "phase15_validate_checkers": list(READINESS_VALIDATE_CHECKERS),
            },
            indent=2,
        )
        + "\n",
    )
    _write(root / BUILD_REL, "\n".join(BUILD_MARKERS) + "\n")


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        _seed_fixture_tree(root)
        _assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        readme_path = root / README_REL
        baseline_readme = _read(readme_path)
        for marker, replacement, label in (
            (
                "- `validate-phase15.py` keeps the shared `phase15-validate` route fail-closed on the parked Phase 15 readiness packet and the parity scorecard's machine-reported review-field and aggregate-metric surface before the narrower handoff checkers run.",
                "- `validate-phase15.py` keeps the shared `phase15-validate` route fail-closed on a missing packet instead of the parked readiness and parity-scorecard packet.",
                "missing_readme_validate_phase15_summary_guard_failed",
            ),
            (
                "- `make -C zigux phase15-validate` now reruns `validate-phase15.py`, `check-phase15-scripts-readme-alignment.py`, and `check-phase15-review-process-handoff.py` together so the shipped validator-first route covers both the broad readiness packet and the dedicated parity-scorecard reporting packet before `make -C zigux phase15-test` replays `zigux/tests/phase15_build.zig`.",
                "- `make -C zigux phase15-validate` now reruns only one checker and skips the shipped readiness-plus-scorecard reporting contract.",
                "missing_readme_phase15_validate_replay_guard_failed",
            ),
        ):
            _write(readme_path, baseline_readme.replace(marker, replacement, 1))
            _assert_only(validate(root), [f"readme:missing:{marker}"], label)
            _write(readme_path, baseline_readme)
            case_count += 1

        tests_readme_path = root / TESTS_README_REL
        baseline_tests_readme = _read(tests_readme_path)
        for marker, replacement, label in (
            (
                "Documentation/zigux/phase15-handoff-next-steps-survey.md",
                "Documentation/zigux/phase15-handoff-next-steps-missing.md",
                "missing_tests_readme_handoff_note_marker_guard_failed",
            ),
            (
                "Documentation/zigux/phase15-readiness-gate-survey.md",
                "Documentation/zigux/phase15-readiness-gate-missing.md",
                "missing_tests_readme_readiness_note_marker_guard_failed",
            ),
            (
                "zigux/tests/phase15_handoff_next_steps_manifest.json",
                "zigux/tests/phase15_handoff_next_steps_manifest_missing.json",
                "missing_tests_readme_handoff_manifest_marker_guard_failed",
            ),
            (
                "zigux/tests/phase15_readiness_gate_manifest.json",
                "zigux/tests/phase15_readiness_gate_manifest_missing.json",
                "missing_tests_readme_readiness_manifest_marker_guard_failed",
            ),
            (
                "Documentation/zigux/phase15-governance-lane-sequencing.md",
                "Documentation/zigux/phase15-governance-lane-missing.md",
                "missing_tests_readme_lane_sequencing_note_marker_guard_failed",
            ),
            (
                ".github/workflows/zigux-bootstrap.yml",
                ".github/workflows/phase15-missing.yml",
                "missing_tests_readme_workflow_marker_guard_failed",
            ),
            (
                "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
                "zigux/tests/phase15_blocker_evidence_missing.zig",
                "missing_tests_readme_blocker_evidence_marker_guard_failed",
            ),
            (
                "zigux/tests/phase15_governance_lane_sequencing.zig",
                "zigux/tests/phase15_lane_sequence_missing.zig",
                "missing_tests_readme_governance_lane_marker_guard_failed",
            ),
            (
                "make -C zigux phase15-test",
                "make -C zigux phase15-check",
                "missing_tests_readme_dedicated_make_test_marker_guard_failed",
            ),
        ):
            _write(tests_readme_path, baseline_tests_readme.replace(marker, replacement, 1))
            _assert_only(validate(root), [f"tests_readme:missing:{marker}"], label)
            _write(tests_readme_path, baseline_tests_readme)
            case_count += 1

        build_path = root / BUILD_REL
        baseline_build = _read(build_path)
        for marker, label in (
            ('b.path("phase15_indefinite_c_blocker_evidence.zig")', "missing_build_blocker_evidence_marker_guard_failed"),
            ('b.path("phase15_governance_lane_sequencing.zig")', "missing_build_governance_lane_marker_guard_failed"),
        ):
            _write(build_path, baseline_build.replace(marker + "\n", "", 1))
            _assert_only(validate(root), [f"build:missing:{marker}"], label)
            _write(build_path, baseline_build)
            case_count += 1

        manifest_path = root / MANIFEST_REL
        baseline_manifest = _read(manifest_path)
        manifest_data = json.loads(baseline_manifest)
        manifest_data["handoff_evidence"]["current_repo_handoff"] = manifest_data["handoff_evidence"]["current_repo_handoff"].replace(
            "zigux/tests/phase15_indefinite_c_blocker_evidence.zig", "", 1
        )
        _write(manifest_path, json.dumps(manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_current_repo_handoff:missing:zigux/tests/phase15_indefinite_c_blocker_evidence.zig"],
            "missing_manifest_blocker_evidence_marker_guard_failed",
        )
        _write(manifest_path, baseline_manifest)
        case_count += 1

        readiness_note_path = root / READINESS_GATE_NOTE_REL
        baseline_readiness_note = _read(readiness_note_path)
        readiness_note_marker = "scripts/zigux/check-phase15-review-process-handoff.py"
        _write(readiness_note_path, baseline_readiness_note.replace(readiness_note_marker, "scripts/zigux/check-phase15-review-process-missing.py", 1))
        _assert_only(
            validate(root),
            [f"readiness_note:missing:{readiness_note_marker}"],
            "missing_readiness_note_checker_marker_guard_failed",
        )
        _write(readiness_note_path, baseline_readiness_note)
        case_count += 1

        readiness_manifest_path = root / READINESS_MANIFEST_REL
        baseline_readiness_manifest = _read(readiness_manifest_path)
        readiness_manifest_data = json.loads(baseline_readiness_manifest)
        readiness_manifest_data["phase15_validate_checkers"].remove("scripts/zigux/check-phase15-review-process-handoff.py")
        _write(readiness_manifest_path, json.dumps(readiness_manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            [
                "readiness_manifest:missing:scripts/zigux/check-phase15-review-process-handoff.py",
                "readiness_manifest:count:1",
            ],
            "missing_readiness_manifest_checker_guard_failed",
        )
        _write(readiness_manifest_path, baseline_readiness_manifest)
        case_count += 1

        parity_scorecard_path = root / PARITY_SCORECARD_NOTE_REL
        baseline_parity_scorecard = _read(parity_scorecard_path)
        parity_scorecard_marker = "make -C zigux phase15-test"
        _write(
            parity_scorecard_path,
            baseline_parity_scorecard.replace(parity_scorecard_marker, "make -C zigux phase15-check", 1),
        )
        _assert_only(
            validate(root),
            [f"parity_scorecard:missing:{parity_scorecard_marker}"],
            "missing_parity_scorecard_dedicated_make_test_marker_guard_failed",
        )
        _write(parity_scorecard_path, baseline_parity_scorecard)
        case_count += 1

    print("PHASE15_SCRIPTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_SCRIPTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the scripts-root Phase 15 governance packet aligned with the shipped review surfaces."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE15_SCRIPTS_README_ALIGNMENT=fail")
        print("PHASE15_SCRIPTS_README_ALIGNMENT_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE15_SCRIPTS_README_ALIGNMENT_ISSUES_END")
        return 1

    print("PHASE15_SCRIPTS_README_ALIGNMENT=pass")
    print(
        "PHASE15_SCRIPTS_README_ALIGNMENT_MARKER_COUNT="
        f"{len(README_SNIPPETS) + len(DOCS_README_MARKERS) + len(MAKEFILE_REQUIRED) + len(HANDOFF_CHECKER_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(REVIEW_PROCESS_NOTE_MARKERS) + len(PARITY_SCORECARD_MARKERS) + len(TESTS_README_MARKERS) + len(MANIFEST_LANE_MARKERS) + len(CURRENT_REPO_HANDOFF_MARKERS) + len(READINESS_NOTE_MARKERS) + len(READINESS_VALIDATE_CHECKERS) + len(BUILD_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
