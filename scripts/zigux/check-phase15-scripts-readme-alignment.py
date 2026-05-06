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
TESTS_README_REL = "zigux/tests/README.md"
HANDOFF_CHECKER_REL = "scripts/zigux/check-phase15-review-process-handoff.py"
MANIFEST_REL = "zigux/tests/phase15_architecture_council_review_process_manifest.json"
BUILD_REL = "zigux/tests/phase15_build.zig"

REQUIRED_FILES = (
    README_REL,
    MAKEFILE_REL,
    WORKFLOW_REL,
    REVIEW_CHECKLIST_REL,
    REVIEW_PROCESS_NOTE_REL,
    TESTS_README_REL,
    HANDOFF_CHECKER_REL,
    MANIFEST_REL,
    BUILD_REL,
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_readiness_gate.zig",
)

README_SNIPPETS = (
    "- the current shared Phase 15 governance surface on `master` is `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, `zigux/tests/phase15_readiness_gate.zig`, and `zigux/tests/phase15_build.zig`.",
    "- `check-phase15-scripts-readme-alignment.py` keeps `scripts/zigux/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase15-review-process-handoff.py`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, and `zigux/tests/phase15_build.zig` aligned around the parked governance packet's scripts-root validator-first route and no-approval-yet posture.",
    "- `check-phase15-review-process-handoff.py` keeps the dedicated review-process note and its manifest-backed handoff evidence aligned around the self-reference, product-boundary, and parked-route markers that keep the Architecture Council packet reviewable without inventing a broader governance surface.",
    "- `zig build test --build-file zigux/tests/phase15_build.zig` and `make -C zigux phase15` rerun the parked freeze-map governance, parity-scorecard, Architecture Council review-process, handoff-next-steps, dedicated indefinite-C policy, lane-owner alignment, and readiness-gate packet without implying any new approval claim for a freeze-map anchor.",
    "- the current bounded Phase 15 decision is still to leave the lane parked unless a named reopen trigger fires or the deep-core blocker posture changes enough to justify another Architecture Council slice.",
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
    "scripts/zigux/check-phase15-review-process-handoff.py",
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

TESTS_README_MARKERS = (
    "keep the parked Phase 15 governance packet explicit in the tests root too:",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_readiness_gate.zig",
    "zigux/Makefile",
    "make -C zigux phase15-validate",
    "zig build test --build-file zigux/tests/phase15_build.zig",
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
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
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
    tests_readme = _read(root / TESTS_README_REL)
    manifest = json.loads(_read(root / MANIFEST_REL))
    build = _read(root / BUILD_REL)

    _require_markers_exact_once(readme, README_SNIPPETS, "readme", issues)
    _require_markers_present(makefile, MAKEFILE_REQUIRED, "makefile", issues)
    _require_markers_exact_once(workflow, WORKFLOW_MARKERS, "workflow", issues)
    _require_markers_present(handoff_checker, HANDOFF_CHECKER_MARKERS, "handoff_checker", issues)
    _require_markers_present(review_checklist, REVIEW_CHECKLIST_MARKERS, "review_checklist", issues)
    _require_markers_present(review_process_note, REVIEW_PROCESS_NOTE_MARKERS, "review_process_note", issues)
    _require_markers_present(tests_readme, TESTS_README_MARKERS, "tests_readme", issues)

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
            "- if the change touches the shared Phase 15 governance packet, do `scripts/zigux/check-phase15-review-process-handoff.py`, `make -C zigux phase15`, and the no-approval-yet posture still agree?",
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


def _baseline_tests_readme() -> str:
    return "\n".join(
        (
            "# zigux/tests",
            "",
            "Guidance",
            "- keep the parked Phase 15 governance packet explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase15_architecture_council_review_process_manifest.json`, `zigux/tests/phase15_build.zig`, `zigux/tests/phase15_freeze_map_governance.zig`, `zigux/tests/phase15_parity_scorecard.zig`, `zigux/tests/phase15_architecture_council_review_process.zig`, `zigux/tests/phase15_handoff_next_steps.zig`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, `zigux/tests/phase15_readiness_gate.zig`, `zigux/Makefile`, `make -C zigux phase15-validate`, `zig build test --build-file zigux/tests/phase15_build.zig`, and `make -C zigux phase15` should continue to keep the current freeze-map, review-process, parity-scorecard, handoff-next-steps, indefinite-C policy, lane-owner alignment, and readiness-gate governance packet reviewable through the shipped scripts-root validator-first route, the workflow-backed replay, and the shared build-and-make path without implying any Architecture Council approval for a freeze-map status change",
            "",
        )
    )


def _baseline_manifest() -> str:
    return json.dumps(
        {
            "handoff_evidence": {
                "current_repo_handoff": "The current repo handoff explicitly names Documentation/zigux/freeze-map.md, Documentation/zigux/phase15-freeze-map-governance.md, Documentation/zigux/phase15-architecture-council-review-process.md, Documentation/zigux/phase15-parity-scorecard.md, Documentation/zigux/phase15-indefinite-c-policy.md, Documentation/zigux/review-checklist.md, scripts/zigux/README.md, zigux/tests/README.md, zigux/Makefile, .github/workflows/zigux-bootstrap.yml, scripts/zigux/check-phase15-scripts-readme-alignment.py, scripts/zigux/check-phase15-review-process-handoff.py, zigux/tests/phase15_architecture_council_review_process_manifest.json, zigux/tests/phase15_freeze_map_governance.zig, zigux/tests/phase15_parity_scorecard.zig, zigux/tests/phase15_architecture_council_review_process.zig, zigux/tests/phase15_indefinite_c_policy.json, zigux/tests/phase15_indefinite_c_policy.zig, zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig, and zigux/tests/phase15_build.zig as the parked governance packet boundary.",
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
            'const f = b.path("phase15_indefinite_c_lane_owner_alignment.zig");',
            'const g = b.path("phase15_readiness_gate.zig");',
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
    _write(root / TESTS_README_REL, _baseline_tests_readme())
    _write(root / MANIFEST_REL, _baseline_manifest())
    _write(root / BUILD_REL, _baseline_build())
    for rel in (
        "Documentation/zigux/freeze-map.md",
        "Documentation/zigux/phase15-freeze-map-governance.md",
        "Documentation/zigux/phase15-parity-scorecard.md",
        "Documentation/zigux/phase15-indefinite-c-policy.md",
        "zigux/tests/phase15_freeze_map_governance.zig",
        "zigux/tests/phase15_parity_scorecard.zig",
        "zigux/tests/phase15_architecture_council_review_process.zig",
        "zigux/tests/phase15_handoff_next_steps.zig",
        "zigux/tests/phase15_indefinite_c_policy.json",
        "zigux/tests/phase15_indefinite_c_policy.zig",
        "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
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

        narrowed_phase15_surface = README_SNIPPETS[0].replace(
            "`scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`",
            "`scripts/zigux/README.md`, `zigux/Makefile`",
            1,
        )
        _write(root / README_REL, baseline_readme.replace(README_SNIPPETS[0], narrowed_phase15_surface, 1))
        _assert_only(
            validate(root),
            [f"readme:missing:{README_SNIPPETS[0]}"],
            "missing_readme_tests_readme_surface_guard_failed",
        )
        _write(root / README_REL, baseline_readme)
        case_count += 1

        narrowed_phase15_alignment = README_SNIPPETS[1].replace(
            "`Documentation/zigux/phase15-architecture-council-review-process.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase15-review-process-handoff.py`",
            "`Documentation/zigux/phase15-architecture-council-review-process.md`, `scripts/zigux/check-phase15-review-process-handoff.py`",
            1,
        )
        _write(root / README_REL, baseline_readme.replace(README_SNIPPETS[1], narrowed_phase15_alignment, 1))
        _assert_only(
            validate(root),
            [f"readme:missing:{README_SNIPPETS[1]}"],
            "missing_readme_tests_readme_alignment_guard_failed",
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

        checklist_path = root / REVIEW_CHECKLIST_REL
        baseline_checklist = _read(checklist_path)
        checklist_marker = "scripts/zigux/check-phase15-review-process-handoff.py"
        _write(
            root / REVIEW_CHECKLIST_REL,
            baseline_checklist.replace(checklist_marker, "scripts/zigux/check-phase15-review-process-handoff.missing", 1),
        )
        _assert_only(
            validate(root),
            [f"review_checklist:missing:{checklist_marker}"],
            "missing_review_checklist_marker_guard_failed",
        )
        _write(root / REVIEW_CHECKLIST_REL, baseline_checklist)
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
        ].replace("scripts/zigux/check-phase15-scripts-readme-alignment.py, ", "", 1)
        _write(root / MANIFEST_REL, json.dumps(manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            [
                "manifest_current_repo_handoff:missing:scripts/zigux/check-phase15-scripts-readme-alignment.py"
            ],
            "missing_manifest_repo_handoff_marker_guard_failed",
        )
        _write(root / MANIFEST_REL, baseline_manifest)
        case_count += 1

        manifest_data = json.loads(baseline_manifest)
        manifest_data["handoff_evidence"]["current_repo_handoff"] = manifest_data["handoff_evidence"][
            "current_repo_handoff"
        ].replace("scripts/zigux/README.md, ", "", 1)
        _write(root / MANIFEST_REL, json.dumps(manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_current_repo_handoff:missing:scripts/zigux/README.md"],
            "missing_manifest_scripts_readme_marker_guard_failed",
        )
        _write(root / MANIFEST_REL, baseline_manifest)
        case_count += 1

        manifest_data = json.loads(baseline_manifest)
        manifest_data["handoff_evidence"]["current_repo_handoff"] = manifest_data["handoff_evidence"][
            "current_repo_handoff"
        ].replace("zigux/tests/README.md, ", "", 1)
        _write(root / MANIFEST_REL, json.dumps(manifest_data, indent=2) + "\n")
        _assert_only(
            validate(root),
            ["manifest_current_repo_handoff:missing:zigux/tests/README.md"],
            "missing_manifest_tests_readme_marker_guard_failed",
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

        tests_readme_path = root / TESTS_README_REL
        baseline_tests_readme = _read(tests_readme_path)
        _write(
            root / TESTS_README_REL,
            baseline_tests_readme.replace(
                "scripts/zigux/check-phase15-scripts-readme-alignment.py", "scripts/zigux/check-phase15-scripts-readme-alignment.missing", 1
            ),
        )
        _assert_only(
            validate(root),
            ["tests_readme:missing:scripts/zigux/check-phase15-scripts-readme-alignment.py"],
            "missing_tests_readme_alignment_checker_marker_guard_failed",
        )
        _write(root / TESTS_README_REL, baseline_tests_readme)
        case_count += 1

        _write(
            root / TESTS_README_REL,
            baseline_tests_readme.replace(
                "zigux/tests/phase15_handoff_next_steps.zig", "zigux/tests/phase15_handoff_notes.zig", 1
            ),
        )
        _assert_only(
            validate(root),
            ["tests_readme:missing:zigux/tests/phase15_handoff_next_steps.zig"],
            "missing_tests_readme_handoff_next_steps_marker_guard_failed",
        )
        _write(root / TESTS_README_REL, baseline_tests_readme)
        case_count += 1

        _write(
            root / TESTS_README_REL,
            baseline_tests_readme.replace(
                "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
                "zigux/tests/phase15_indefinite_c_lane_owner_notes.zig",
                1,
            ),
        )
        _assert_only(
            validate(root),
            ["tests_readme:missing:zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig"],
            "missing_tests_readme_lane_owner_alignment_marker_guard_failed",
        )
        _write(root / TESTS_README_REL, baseline_tests_readme)
        case_count += 1

        _write(
            root / TESTS_README_REL,
            baseline_tests_readme.replace(
                "zigux/tests/phase15_readiness_gate.zig", "zigux/tests/phase15_readiness_snapshot.zig", 1
            ),
        )
        _assert_only(
            validate(root),
            ["tests_readme:missing:zigux/tests/phase15_readiness_gate.zig"],
            "missing_tests_readme_readiness_gate_marker_guard_failed",
        )
        _write(root / TESTS_README_REL, baseline_tests_readme)
        case_count += 1

        _write(
            root / TESTS_README_REL,
            baseline_tests_readme.replace("make -C zigux phase15-validate", "make -C zigux phase15-review", 1),
        )
        _assert_only(
            validate(root),
            ["tests_readme:missing:make -C zigux phase15-validate"],
            "missing_tests_readme_validate_route_marker_guard_failed",
        )
        _write(root / TESTS_README_REL, baseline_tests_readme)
        case_count += 1

        build_path = root / BUILD_REL
        baseline_build = _read(build_path)
        _write(
            root / BUILD_REL,
            baseline_build.replace('const g = b.path("phase15_readiness_gate.zig");\n', "", 1),
        )
        _assert_only(
            validate(root),
            ['build:missing:b.path("phase15_readiness_gate.zig")'],
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

        (root / HANDOFF_CHECKER_REL).unlink()
        _assert_only(
            validate(root),
            ["missing_file:scripts/zigux/check-phase15-review-process-handoff.py"],
            "missing_handoff_checker_file_guard_failed",
        )
        _seed_fixture_tree(root)
        case_count += 1

        (root / TESTS_README_REL).unlink()
        _assert_only(
            validate(root),
            ["missing_file:zigux/tests/README.md"],
            "missing_tests_readme_file_guard_failed",
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
        f"{len(README_SNIPPETS) + len(MAKEFILE_REQUIRED) + len(HANDOFF_CHECKER_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(REVIEW_PROCESS_NOTE_MARKERS) + len(TESTS_README_MARKERS) + len(MANIFEST_LANE_MARKERS) + len(CURRENT_REPO_HANDOFF_MARKERS) + len(BUILD_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
