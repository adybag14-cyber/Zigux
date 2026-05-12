#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

README_REL = "scripts/zigux/README.md"
MAKEFILE_REL = "zigux/Makefile"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
REVIEW_PROCESS_NOTE_REL = "Documentation/zigux/phase15-architecture-council-review-process.md"
HANDOFF_CHECKER_REL = "scripts/zigux/check-phase15-review-process-handoff.py"
MANIFEST_REL = "zigux/tests/phase15_architecture_council_review_process_manifest.json"
BUILD_REL = "zigux/tests/phase15_build.zig"

REQUIRED_FILES = (
    README_REL,
    MAKEFILE_REL,
    WORKFLOW_REL,
    REVIEW_CHECKLIST_REL,
    REVIEW_PROCESS_NOTE_REL,
    HANDOFF_CHECKER_REL,
    MANIFEST_REL,
    BUILD_REL,
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
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
    "- keep the parked Phase 15 governance packet explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_readiness_gate.zig`, `zigux/Makefile`, and `make -C zigux phase15` should continue to keep the current freeze-map, review-process, parity-scorecard, handoff-next-steps, blocker-evidence, indefinite-C policy, lane-owner alignment, governance-lane sequencing, and readiness-gate governance packet reviewable through the shipped scripts-root validator-first route, the workflow-backed replay, and the shared build-and-make path without implying any Architecture Council approval for a freeze-map status change.",
    "- `zigux/tests/phase15_handoff_next_steps_manifest.json` remains part of the parked Phase 15 governance packet evidence.",
    "- `zigux/tests/phase15_readiness_gate_manifest.json` remains part of the parked Phase 15 governance packet evidence.",
    "- `Documentation/zigux/phase15-handoff-next-steps-survey.md` remains the dedicated handoff note for the parked Phase 15 governance packet and its next-step record.",
    "- `Documentation/zigux/phase15-readiness-gate-survey.md` remains the dedicated maintenance-mode readiness note for the parked Phase 15 governance packet.",
    "- `validate-phase15.py` keeps the shared `phase15-validate` route fail-closed on the parked Phase 15 readiness packet and the parity scorecard's machine-reported review-field and aggregate-metric surface before the narrower handoff checkers run.",
    "- `make -C zigux phase15-validate` now reruns `validate-phase15.py`, `check-phase15-scripts-readme-alignment.py`, and `check-phase15-review-process-handoff.py` together so the shipped validator-first route covers both the broad readiness packet and the dedicated parity-scorecard reporting packet before `make -C zigux phase15-test` replays `zigux/tests/phase15_build.zig`.",
)

MAKEFILE_REQUIRED = (
    "PHONY += phase15-validate phase15-test phase15",
    "phase15-validate:",
    "scripts/zigux/validate-phase15.py",
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
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/validate-phase15.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_build.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
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

MANIFEST_LANE_MARKERS = (
    "scripts-root validator path",
    "Linux-style `make -C zigux phase15-validate` route",
    "tests-root guidance path",
    "dedicated handoff-checker route",
)

CURRENT_REPO_HANDOFF_MARKERS = (
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_readiness_gate_manifest.json",
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
    makefile = _read(root / MAKEFILE_REL)
    workflow = _read(root / WORKFLOW_REL)
    handoff_checker = _read(root / HANDOFF_CHECKER_REL)
    review_checklist = _read(root / REVIEW_CHECKLIST_REL)
    review_process_note = _read(root / REVIEW_PROCESS_NOTE_REL)
    manifest = json.loads(_read(root / MANIFEST_REL))
    build = _read(root / BUILD_REL)

    _require_markers_exact_once(readme, README_SNIPPETS, "readme", issues)
    _require_markers_present(makefile, MAKEFILE_REQUIRED, "makefile", issues)
    _require_markers_exact_once(workflow, WORKFLOW_MARKERS, "workflow", issues)
    _require_markers_present(handoff_checker, HANDOFF_CHECKER_MARKERS, "handoff_checker", issues)
    _require_markers_present(review_checklist, REVIEW_CHECKLIST_MARKERS, "review_checklist", issues)
    _require_markers_present(review_process_note, REVIEW_PROCESS_NOTE_MARKERS, "review_process_note", issues)

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

    _require_markers_present(build, BUILD_MARKERS, "build", issues)

    return issues


def _baseline_readme() -> str:
    return "\n".join(
        (
            "# scripts/zigux",
            "",
            "Phase 15 flow",
            *README_SNIPPETS,
            "",
        )
    )


def _baseline_makefile() -> str:
    return "\n".join(
        (
            "PHONY += phase15-validate phase15-test phase15",
            "",
            "phase15-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase15.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py",
            "",
            "phase15-test:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase15_build.zig",
            "",
            "phase15: phase15-validate phase15-test",
            "",
        )
    )


def _baseline_workflow() -> str:
    return "\n".join(
        (
            "jobs:",
            "  bootstrap:",
            "    steps:",
            "      - name: Validate Phase 15 governance packet",
            "        run: make -C zigux phase15-validate",
            "",
            "      - name: Run Phase 15 governance tests",
            "        run: make -C zigux phase15-test",
            "",
        )
    )


def _baseline_handoff_checker() -> str:
    return "\n".join(
        (
            '#!/usr/bin/env python3',
            'NOTE_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md"',
            'MANIFEST_PATH = "zigux/tests/phase15_architecture_council_review_process_manifest.json"',
            'OPTIONAL = "scripts-root validator path"',
            'print("PHASE15_REVIEW_PROCESS_HANDOFF=pass")',
            "",
        )
    )


def _baseline_review_checklist() -> str:
    return "\n".join(
        (
            "# Checklist",
            "- if the change touches the shared Phase 15 governance packet, do `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-governance-lane-sequencing.md`, `scripts/zigux/validate-phase15.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_readiness_gate_manifest.json`, `zigux/tests/phase15_build.zig`, `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, and the no-approval-yet posture still agree?",
            "",
        )
    )


def _baseline_review_process_note() -> str:
    return "\n".join(
        (
            "# Phase 15",
            "- no Architecture Council approval is currently recorded for a freeze-map status change",
            "- reopen triggers remain attached",
            "- Keep the Phase 15 governance lane in maintenance mode.",
            "",
        )
    )


def _baseline_manifest() -> str:
    return json.dumps(
        {
            "handoff_evidence": {
                "current_repo_handoff": "The current repo handoff explicitly names Documentation/zigux/freeze-map.md, Documentation/zigux/phase15-freeze-map-governance.md, Documentation/zigux/phase15-architecture-council-review-process.md, Documentation/zigux/phase15-parity-scorecard.md, Documentation/zigux/phase15-indefinite-c-policy.md, Documentation/zigux/review-checklist.md, scripts/zigux/check-phase15-scripts-readme-alignment.py, scripts/zigux/check-phase15-review-process-handoff.py, zigux/tests/phase15_architecture_council_review_process_manifest.json, zigux/tests/phase15_handoff_next_steps_manifest.json, zigux/tests/phase15_readiness_gate_manifest.json, zigux/tests/phase15_freeze_map_governance.zig, zigux/tests/phase15_parity_scorecard.zig, zigux/tests/phase15_architecture_council_review_process.zig, zigux/tests/phase15_indefinite_c_policy.json, zigux/tests/phase15_indefinite_c_policy.zig, zigux/tests/phase15_indefinite_c_blocker_evidence.zig, zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig, zigux/tests/phase15_governance_lane_sequencing.zig, and zigux/tests/phase15_build.zig as the parked governance packet boundary.",
                "current_bounded_lane": "The parked Architecture Council packet stays aligned with its scripts-root validator path, its Linux-style `make -C zigux phase15-validate` route, its tests-root guidance path, and its dedicated handoff-checker route."
            }
        },
        indent=2,
    ) + "\n"


def _baseline_build() -> str:
    return "\n".join(
        (
            'const a = b.path("phase15_freeze_map_governance.zig");',
            'const b1 = b.path("phase15_parity_scorecard.zig");',
            'const c = b.path("phase15_architecture_council_review_process.zig");',
            'const d = b.path("phase15_handoff_next_steps.zig");',
            'const e = b.path("phase15_indefinite_c_policy.zig");',
            'const f = b.path("phase15_indefinite_c_blocker_evidence.zig");',
            'const g = b.path("phase15_indefinite_c_lane_owner_alignment.zig");',
            'const h = b.path("phase15_governance_lane_sequencing.zig");',
            'const i = b.path("phase15_readiness_gate.zig");',
            'const step = b.step("test", "Run Phase 15 governance tests");',
            "",
        )
    )


def _seed_fixture_tree(root: Path) -> None:
    _write(root / README_REL, _baseline_readme())
    _write(root / MAKEFILE_REL, _baseline_makefile())
    _write(root / WORKFLOW_REL, _baseline_workflow())
    _write(root / HANDOFF_CHECKER_REL, _baseline_handoff_checker())
    _write(root / REVIEW_CHECKLIST_REL, _baseline_review_checklist())
    _write(root / REVIEW_PROCESS_NOTE_REL, _baseline_review_process_note())
    _write(root / MANIFEST_REL, _baseline_manifest())
    _write(root / BUILD_REL, _baseline_build())
    for rel in (
        "Documentation/zigux/freeze-map.md",
        "Documentation/zigux/phase15-freeze-map-governance.md",
        "Documentation/zigux/phase15-parity-scorecard.md",
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        "Documentation/zigux/phase15-handoff-next-steps-survey.md",
        "Documentation/zigux/phase15-readiness-gate-survey.md",
        "Documentation/zigux/phase15-governance-lane-sequencing.md",
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        "zigux/tests/phase15_readiness_gate_manifest.json",
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
    ):
        _write(root / rel, "{}\n" if rel.endswith(".json") else "// stub\n")


def _assert_only(issues: list[str], expected: list[str], label: str) -> None:
    if issues != expected:
        got = ",".join(issues) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase15-scripts-readme-alignment-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_scripts_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        _seed_fixture_tree(root)
        _assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        readme_path = root / README_REL
        baseline_readme = _read(readme_path)
        missing_readme_snippet = README_SNIPPETS[3]
        _write(root / README_REL, baseline_readme.replace(missing_readme_snippet + "\n", "", 1))
        _assert_only(
            validate(root),
            [f"readme:missing:{missing_readme_snippet}"],
            "missing_readme_snippet_guard_failed",
        )
        _write(root / README_REL, baseline_readme)
        case_count += 1

        duplicate_readme_snippet = README_SNIPPETS[1]
        _write(root / README_REL, baseline_readme + duplicate_readme_snippet + "\n")
        _assert_only(
            validate(root),
            [f"readme:count:2:{duplicate_readme_snippet}"],
            "duplicate_readme_snippet_guard_failed",
        )
        _write(root / README_REL, baseline_readme)
        case_count += 1

        makefile_path = root / MAKEFILE_REL
        baseline_makefile = _read(makefile_path)
        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase15.py\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["makefile:missing:scripts/zigux/validate-phase15.py"],
            "missing_validate_route_marker_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        _write(
            root / MAKEFILE_REL,
            baseline_makefile.replace("phase15: phase15-validate phase15-test", "phase15:", 1),
        )
        _assert_only(
            validate(root),
            ["makefile:missing:phase15: phase15-validate phase15-test"],
            "missing_makefile_marker_guard_failed",
        )
        _write(root / MAKEFILE_REL, baseline_makefile)
        case_count += 1

        workflow_path = root / WORKFLOW_REL
        baseline_workflow = _read(workflow_path)
        _write(
            root / WORKFLOW_REL,
            baseline_workflow.replace("      - name: Validate Phase 15 governance packet\n", "", 1),
        )
        _assert_only(
            validate(root),
            ["workflow:missing:Validate Phase 15 governance packet"],
            "missing_workflow_marker_guard_failed",
        )
        _write(root / WORKFLOW_REL, baseline_workflow)
        case_count += 1

        checker_path = root / HANDOFF_CHECKER_REL
        baseline_checker = _read(checker_path)
        _write(
            root / HANDOFF_CHECKER_REL,
            baseline_checker.replace('MANIFEST_PATH = "zigux/tests/phase15_architecture_council_review_process_manifest.json"\n', "", 1),
        )
        _assert_only(
            validate(root),
            ['handoff_checker:missing:MANIFEST_PATH = "zigux/tests/phase15_architecture_council_review_process_manifest.json"'],
            "missing_handoff_marker_guard_failed",
        )
        _write(root / HANDOFF_CHECKER_REL, baseline_checker)
        case_count += 1

        review_checklist_path = root / REVIEW_CHECKLIST_REL
        baseline_review_checklist = _read(review_checklist_path)
        _write(
            root / REVIEW_CHECKLIST_REL,
            baseline_review_checklist.replace("`scripts/zigux/validate-phase15.py`, ", "", 1),
        )
        _assert_only(
            validate(root),
            ["review_checklist:missing:scripts/zigux/validate-phase15.py"],
            "missing_validate_phase15_review_checklist_guard_failed",
        )
        _write(root / REVIEW_CHECKLIST_REL, baseline_review_checklist)
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_REL,
            baseline_review_checklist.replace("`Documentation/zigux/phase15-governance-lane-sequencing.md`, ", "", 1),
        )
        _assert_only(
            validate(root),
            ["review_checklist:missing:Documentation/zigux/phase15-governance-lane-sequencing.md"],
            "missing_lane_sequencing_review_checklist_guard_failed",
        )
        _write(root / REVIEW_CHECKLIST_REL, baseline_review_checklist)
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_REL,
            baseline_review_checklist.replace("`zigux/tests/phase15_handoff_next_steps_manifest.json`, ", "", 1),
        )
        _assert_only(
            validate(root),
            ["review_checklist:missing:zigux/tests/phase15_handoff_next_steps_manifest.json"],
            "missing_handoff_manifest_review_checklist_guard_failed",
        )
        _write(root / REVIEW_CHECKLIST_REL, baseline_review_checklist)
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_REL,
            baseline_review_checklist.replace("`zigux/tests/phase15_readiness_gate_manifest.json`, ", "", 1),
        )
        _assert_only(
            validate(root),
            ["review_checklist:missing:zigux/tests/phase15_readiness_gate_manifest.json"],
            "missing_readiness_manifest_review_checklist_guard_failed",
        )
        _write(root / REVIEW_CHECKLIST_REL, baseline_review_checklist)
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_REL,
            baseline_review_checklist.replace("`make -C zigux phase15-test`, ", "", 1),
        )
        _assert_only(
            validate(root),
            ["review_checklist:missing:make -C zigux phase15-test"],
            "missing_phase15_test_review_checklist_guard_failed",
        )
        _write(root / REVIEW_CHECKLIST_REL, baseline_review_checklist)
        case_count += 1

        manifest_path = root / MANIFEST_REL
        baseline_manifest = _read(manifest_path)
        _write(root / MANIFEST_REL, json.dumps({"handoff_evidence": {}}, indent=2) + "\n")
        _assert_only(
            validate(root),
            [
                "manifest:missing:handoff_evidence.current_repo_handoff",
                "manifest:missing:handoff_evidence.current_bounded_lane",
            ],
            "missing_manifest_lane_string_guard_failed",
        )
        _write(root / MANIFEST_REL, baseline_manifest)
        case_count += 1

        manifest_data = json.loads(baseline_manifest)
        manifest_data["handoff_evidence"]["current_repo_handoff"] = manifest_data["handoff_evidence"][
            "current_repo_handoff"
        ].replace("zigux/tests/phase15_handoff_next_steps_manifest.json, ", "", 1)
        _write(root / MANIFEST_REL, json.dumps(manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            [
                "manifest_current_repo_handoff:missing:zigux/tests/phase15_handoff_next_steps_manifest.json"
            ],
            "missing_manifest_repo_handoff_marker_guard_failed",
        )
        _write(root / MANIFEST_REL, baseline_manifest)
        case_count += 1

        manifest_data = json.loads(baseline_manifest)
        manifest_data["handoff_evidence"]["current_bounded_lane"] = manifest_data["handoff_evidence"][
            "current_bounded_lane"
        ].replace("Linux-style `make -C zigux phase15-validate` route, ", "", 1)
        _write(root / MANIFEST_REL, json.dumps(manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_current_bounded_lane:missing:Linux-style `make -C zigux phase15-validate` route"],
            "missing_manifest_validate_route_guard_failed",
        )
        _write(root / MANIFEST_REL, baseline_manifest)
        case_count += 1

        build_path = root / BUILD_REL
        baseline_build = _read(build_path)
        _write(
            root / BUILD_REL,
            baseline_build.replace('const h = b.path("phase15_governance_lane_sequencing.zig");\n', "", 1),
        )
        _assert_only(
            validate(root),
            ['build:missing:b.path("phase15_governance_lane_sequencing.zig")'],
            "missing_build_marker_guard_failed",
        )
        _write(root / BUILD_REL, baseline_build)
        case_count += 1

        (root / "zigux/tests/phase15_handoff_next_steps.zig").unlink()
        _assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase15_handoff_next_steps.zig"],
            "missing_handoff_next_steps_file_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        (root / "zigux/tests/phase15_handoff_next_steps_manifest.json").unlink()
        _assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase15_handoff_next_steps_manifest.json"],
            "missing_handoff_next_steps_manifest_file_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        (root / "zigux/tests/phase15_readiness_gate_manifest.json").unlink()
        _assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase15_readiness_gate_manifest.json"],
            "missing_readiness_gate_manifest_file_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        (root / "zigux/tests/phase15_indefinite_c_blocker_evidence.zig").unlink()
        _assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase15_indefinite_c_blocker_evidence.zig"],
            "missing_blocker_evidence_file_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        (root / "zigux/tests/phase15_readiness_gate.zig").unlink()
        _assert_only(
            validate(root),
            ["missing_file:zigux/tests/phase15_readiness_gate.zig"],
            "missing_readiness_gate_file_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        review_note_path = root / REVIEW_PROCESS_NOTE_REL
        baseline_note = _read(review_note_path)
        _write(
            root / REVIEW_PROCESS_NOTE_REL,
            baseline_note.replace(
                "- no Architecture Council approval is currently recorded for a freeze-map status change\n",
                "",
                1,
            ),
        )
        _assert_only(
            validate(root),
            [
                "review_process_note:missing:no Architecture Council approval is currently recorded for a freeze-map status change"
            ],
            "missing_review_process_marker_guard_failed",
        )
        _write(root / REVIEW_PROCESS_NOTE_REL, baseline_note)
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
        f"{len(README_SNIPPETS) + len(MAKEFILE_REQUIRED) + len(HANDOFF_CHECKER_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(REVIEW_PROCESS_NOTE_MARKERS) + len(MANIFEST_LANE_MARKERS) + len(CURRENT_REPO_HANDOFF_MARKERS) + len(BUILD_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
