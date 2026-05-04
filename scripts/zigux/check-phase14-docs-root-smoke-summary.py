#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()
HEX40_NOTE = "survey provenance captured against verified `master` head"

DOCS_ROOT_LINES = [
    "Phase 14 notes",
    "`Documentation/zigux/phase14-release-boundary-survey.md` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` now make the roadmap's core-adjacent sequencing step explicit from the docs root",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay in study-only posture",
    "`kernel/rcu/tree.c` and `net/core/skbuff.c` remain blocked under the Phase 15 freeze-in-C governance packet",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, `Documentation/zigux/phase14-workqueue-bridge-survey.md`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `zigux/tests/phase14_ring_buffer_manifest.json`, `Documentation/zigux/phase14-ring-buffer-survey.md`, `zigux/tests/phase14_rcu_tree_manifest.json`, `Documentation/zigux/phase14-rcu-tree-survey.md`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `make -C zigux phase14`, and `zigux/tests/phase14_build.zig` now provide one validator-backed shared smoke gate",
    "reviewability lane rather than a closure or active subsystem delivery claim",
]

TESTS_ROOT_EXACT_LINE_COUNTS = {
    "- keep the current Phase 14 smoke packet reviewable through `zigux/tests/phase14_build.zig`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, `make -C zigux phase14`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` so the shared study-only boundary packet stays aligned across the dedicated docs-root and release-boundary smoke helpers, the focused smoke shard, the full replay, the named rollback owner, `Documentation/zigux/phase14-release-boundary-survey.md`, and the docs-root summary instead of widening into ad hoc bridge or deep-core claims": 1,
    "- keep the Phase 14 shared smoke packet explicit in the tests root: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` should continue to keep the exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, and ZAR-to-product transfer rationale visible from the tests root rather than relying on run memory": 1,
}

SURVEY_EXACT_LINE_COUNTS = {
    "- `PHASE14_SHARED_LANE=P14-Y08`": 1,
    "- `PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate`": 1,
    "- `make -C zigux phase14-smoke`": 2,
    "- `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`": 2,
    "- `zigux/tests/phase14_build.zig`": 1,
    "- `reviewability lane rather than a closure or active subsystem delivery claim`": 1,
    "- `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`": 1,
    "- `make -C zigux phase14-smoke ZIG=<attached-zig-path>`": 1,
    "- `make -C zigux phase14-test ZIG=<attached-zig-path>`": 1,
    "- `make -C zigux phase14 ZIG=<attached-zig-path>`": 1,
}

SURVEY_SHARED_SMOKE_BOUNDARY_BLOCK = [
    "- shared smoke boundary:",
    "- `scripts/zigux/validate-phase14.py`",
    "- `scripts/zigux/check-phase14-docs-root-smoke-summary.py`",
    "- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "- `scripts/zigux/README.md`",
    "- `Documentation/zigux/README.md`",
    "- `Documentation/zigux/phase14-release-boundary-survey.md`",
    "- `zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "- `zigux/tests/phase14_rcu_tree_survey.zig`",
    "- `zigux/tests/phase14_build.zig`",
    "- `zigux/Makefile`",
    "- `.github/workflows/zigux-bootstrap.yml`",
    "- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "- `Documentation/zigux/review-checklist.md`",
    "- `Documentation/zigux/freeze-map.md`",
]

SCRIPTS_README_EXACT_LINE_COUNTS = {
    "- `check-phase14-docs-root-smoke-summary.py --self-test` and `check-phase14-docs-root-smoke-summary.py` keep the docs-root Phase 14 smoke summary and the shared smoke survey fail-closed around the same validator-backed `phase14-validate`, focused `phase14-smoke`, and study-only reviewability wording before the broader shared validator runs.": 1,
    "- `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, `zig build test --build-file zigux/tests/phase14_build.zig --summary all`, and `make -C zigux phase14` are the validator-first, focused wrapper, direct focused shard, shared full-bundle, and convenience entrypoints for the current study-only four-anchor packet, while the anchor-local manifests and survey notes keep the ready-next versus blocked posture explicit without widening into new bridge or deep-core claims.": 1,
    "- `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` keep the exact rollback threshold, automatic return-to-blocked trigger list, and ZAR-to-product transfer rationale visible from the docs root rather than relying on run memory.": 1,
    "- attached-toolchain fallback commands stay explicit in the scripts index too: `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`, `make -C zigux phase14-smoke ZIG=<attached-zig-path>`, `make -C zigux phase14-test ZIG=<attached-zig-path>`, and `make -C zigux phase14 ZIG=<attached-zig-path>`.": 1,
}

RELEASE_BOUNDARY_LINES = [
    "PHASE14_RELEASE_BOUNDARY=present",
    "PHASE14_SHARED_REPLAY_PRESENT=yes",
    "PHASE14_RELEASE_CLOSED=no",
    "shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture",
    "compile-shard matrix: one focused `phase14-smoke` shard still covers only `phase14-end-to-end-smoke-tests`, while `phase14-workqueue-bridge-tests`, `phase14-skbuff-bridge-tests`, `phase14-ring-buffer-survey-tests`, and `phase14-rcu-tree-survey-tests` remain `full_bundle_only` under `zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
    "combined shared replay entrypoint: `make -C zigux phase14` remains the published convenience route for the validator-backed smoke packet, so release-facing review and local replay still name the same one-command path as the shared smoke note and manifest instead of leaving that wrapper path implicit in `zigux/Makefile`",
    "PHASE14_SHARED_SMOKE_GATE_COUNT=1",
    "PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0",
]

MAKEFILE_EXACT_LINE_COUNTS = {
    "PHONY += phase14-validate phase14-smoke phase14-test phase14": 1,
    "phase14-validate:": 1,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test": 1,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py": 1,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test": 1,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py": 1,
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py": 1,
    "phase14-smoke:": 1,
    "cd $(ZIGUX_ROOT) && $(ZIG) build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all": 1,
    "phase14-test:": 1,
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase14_build.zig --summary all": 1,
    "phase14: phase14-validate phase14-test": 1,
}

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def count_exact_line(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)

def require_exact_count(label: str, text: str, markers: list[str]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        actual = text.count(marker)
        if actual != 1:
            issues.append(f"{label}:{actual}:{marker}")
    return issues

def require_exact_lines(label: str, text: str, counts: dict[str, int]) -> list[str]:
    issues: list[str] = []
    for marker, expected in counts.items():
        actual = count_exact_line(text, marker)
        if actual != expected:
            issues.append(f"{label}:{actual}:{marker}")
    return issues

def extract_exact_block(text: str, heading: str) -> list[str] | None:
    lines = text.splitlines()
    for index, raw_line in enumerate(lines):
        if raw_line.strip() != heading:
            continue
        block = [raw_line.strip()]
        cursor = index + 1
        while cursor < len(lines):
            candidate = lines[cursor]
            stripped = candidate.strip()
            if not stripped:
                break
            if not candidate.startswith("  - "):
                break
            block.append(stripped)
            cursor += 1
        return block
    return None

def require_exact_block(label: str, text: str, expected_lines: list[str]) -> list[str]:
    issues: list[str] = []
    actual_block = extract_exact_block(text, expected_lines[0])
    if actual_block is None:
        issues.append(f"{label}:missing_block:{expected_lines[0]}")
    elif actual_block != expected_lines:
        issues.append(f"{label}:block_mismatch:{expected_lines[0]}")
    return issues

def validate_phase14_summary_surfaces(
    docs_root_text: str,
    tests_root_text: str,
    scripts_readme_text: str,
    survey_text: str,
    release_boundary_text: str,
    makefile_text: str,
) -> list[str]:
    issues = require_exact_count("docs_root", docs_root_text, DOCS_ROOT_LINES)
    issues.extend(require_exact_lines("tests_root", tests_root_text, TESTS_ROOT_EXACT_LINE_COUNTS))
    issues.extend(require_exact_lines("scripts_readme", scripts_readme_text, SCRIPTS_README_EXACT_LINE_COUNTS))
    issues.extend(require_exact_lines("survey", survey_text, SURVEY_EXACT_LINE_COUNTS))
    issues.extend(require_exact_block("survey", survey_text, SURVEY_SHARED_SMOKE_BOUNDARY_BLOCK))
    issues.extend(require_exact_count("release_boundary", release_boundary_text, RELEASE_BOUNDARY_LINES))
    issues.extend(require_exact_lines("makefile", makefile_text, MAKEFILE_EXACT_LINE_COUNTS))
    if survey_text.count(HEX40_NOTE) != 1:
        issues.append(f"survey:{survey_text.count(HEX40_NOTE)}:{HEX40_NOTE}")
    return issues

def run_self_test() -> int:
    docs_root_text = """
Phase 14 notes
- `Documentation/zigux/phase14-release-boundary-survey.md` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` now make the roadmap's core-adjacent sequencing step explicit from the docs root, so release-facing review no longer jumps directly from the active Phase 13 helper tranche to the Phase 15 governance packet.
- the current Phase 14 release reading is intentionally boundary-only: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay in study-only posture, while `kernel/rcu/tree.c` and `net/core/skbuff.c` remain blocked under the Phase 15 freeze-in-C governance packet rather than being treated as an active release lane.
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, `Documentation/zigux/phase14-workqueue-bridge-survey.md`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `zigux/tests/phase14_ring_buffer_manifest.json`, `Documentation/zigux/phase14-ring-buffer-survey.md`, `zigux/tests/phase14_rcu_tree_manifest.json`, `Documentation/zigux/phase14-rcu-tree-survey.md`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `make -C zigux phase14`, and `zigux/tests/phase14_build.zig` now provide one validator-backed shared smoke gate for that study-only four-anchor packet; it stays a reviewability lane rather than a closure or active subsystem delivery claim.
""".strip()

    tests_root_text = """
Phase 14 guidance
- keep the current Phase 14 smoke packet reviewable through `zigux/tests/phase14_build.zig`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, `make -C zigux phase14`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` so the shared study-only boundary packet stays aligned across the dedicated docs-root and release-boundary smoke helpers, the focused smoke shard, the full replay, the named rollback owner, `Documentation/zigux/phase14-release-boundary-survey.md`, and the docs-root summary instead of widening into ad hoc bridge or deep-core claims
- keep the Phase 14 shared smoke packet explicit in the tests root: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` should continue to keep the exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, and ZAR-to-product transfer rationale visible from the tests root rather than relying on run memory
""".strip()

    scripts_readme_text = """
Phase 14 flow
- `check-phase14-docs-root-smoke-summary.py --self-test` and `check-phase14-docs-root-smoke-summary.py` keep the docs-root Phase 14 smoke summary and the shared smoke survey fail-closed around the same validator-backed `phase14-validate`, focused `phase14-smoke`, and study-only reviewability wording before the broader shared validator runs.
- `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, `zig build test --build-file zigux/tests/phase14_build.zig --summary all`, and `make -C zigux phase14` are the validator-first, focused wrapper, direct focused shard, shared full-bundle, and convenience entrypoints for the current study-only four-anchor packet, while the anchor-local manifests and survey notes keep the ready-next versus blocked posture explicit without widening into new bridge or deep-core claims.
- `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` keep the exact rollback threshold, automatic return-to-blocked trigger list, and ZAR-to-product transfer rationale visible from the docs root rather than relying on run memory.
- attached-toolchain fallback commands stay explicit in the scripts index too: `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`, `make -C zigux phase14-smoke ZIG=<attached-zig-path>`, `make -C zigux phase14-test ZIG=<attached-zig-path>`, and `make -C zigux phase14 ZIG=<attached-zig-path>`.
""".strip()

    survey_text = """
- `PHASE14_SHARED_LANE=P14-Y08`
- `PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate`
- survey provenance captured against verified `master` head `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- shared smoke boundary:
  - `scripts/zigux/validate-phase14.py`
  - `scripts/zigux/check-phase14-docs-root-smoke-summary.py`
  - `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
  - `scripts/zigux/README.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/phase14-release-boundary-survey.md`
  - `zigux/tests/phase14_end_to_end_smoke_manifest.json`
  - `zigux/tests/phase14_end_to_end_smoke_survey.zig`
  - `zigux/tests/phase14_rcu_tree_survey.zig`
  - `zigux/tests/phase14_build.zig`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
  - `Documentation/zigux/review-checklist.md`
  - `Documentation/zigux/freeze-map.md`
- `make -C zigux phase14-smoke`
- `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
- `reviewability lane rather than a closure or active subsystem delivery claim`
- `make -C zigux phase14-smoke`
- `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
- `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`
- `make -C zigux phase14-smoke ZIG=<attached-zig-path>`
- `make -C zigux phase14-test ZIG=<attached-zig-path>`
- `make -C zigux phase14 ZIG=<attached-zig-path>`
""".strip()

    release_boundary_text = """
- PHASE14_RELEASE_BOUNDARY=present
- PHASE14_SHARED_REPLAY_PRESENT=yes
- PHASE14_RELEASE_CLOSED=no
- shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture
- compile-shard matrix: one focused `phase14-smoke` shard still covers only `phase14-end-to-end-smoke-tests`, while `phase14-workqueue-bridge-tests`, `phase14-skbuff-bridge-tests`, `phase14-ring-buffer-survey-tests`, and `phase14-rcu-tree-survey-tests` remain `full_bundle_only` under `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
- combined shared replay entrypoint: `make -C zigux phase14` remains the published convenience route for the validator-backed smoke packet, so release-facing review and local replay still name the same one-command path as the shared smoke note and manifest instead of leaving that wrapper path implicit in `zigux/Makefile`
- PHASE14_SHARED_SMOKE_GATE_COUNT=1
- PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0
""".strip()

    makefile_text = """
PHONY += phase14-validate phase14-smoke phase14-test phase14

phase14-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-docs-root-smoke-summary.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py

phase14-smoke:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all

phase14-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase14_build.zig --summary all

phase14: phase14-validate phase14-test
""".strip()

    good = validate_phase14_summary_surfaces(
        docs_root_text,
        tests_root_text,
        scripts_readme_text,
        survey_text,
        release_boundary_text,
        makefile_text,
    )
    missing_entrypoint = validate_phase14_summary_surfaces(
        docs_root_text,
        tests_root_text,
        scripts_readme_text.replace(
            "`zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, ",
            "",
            1,
        ),
        survey_text,
        release_boundary_text,
        makefile_text,
    )
    missing_tests_packet = validate_phase14_summary_surfaces(
        docs_root_text,
        tests_root_text.replace(
            "- keep the Phase 14 shared smoke packet explicit in the tests root: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` should continue to keep the exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, and ZAR-to-product transfer rationale visible from the tests root rather than relying on run memory",
            "",
            1,
        ),
        scripts_readme_text,
        survey_text,
        release_boundary_text,
        makefile_text,
    )
    duplicate_attached_toolchain = validate_phase14_summary_surfaces(
        docs_root_text,
        tests_root_text,
        scripts_readme_text
        + "\n- attached-toolchain fallback commands stay explicit in the scripts index too: `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`, `make -C zigux phase14-smoke ZIG=<attached-zig-path>`, `make -C zigux phase14-test ZIG=<attached-zig-path>`, and `make -C zigux phase14 ZIG=<attached-zig-path>`.",
        survey_text,
        release_boundary_text,
        makefile_text,
    )
    duplicate_tests_packet = validate_phase14_summary_surfaces(
        docs_root_text,
        tests_root_text
        + "\n- keep the Phase 14 shared smoke packet explicit in the tests root: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` should continue to keep the exact rollback threshold, automatic return-to-blocked trigger list, shared-surface accounting, and ZAR-to-product transfer rationale visible from the tests root rather than relying on run memory",
        scripts_readme_text,
        survey_text,
        release_boundary_text,
        makefile_text,
    )
    missing_release_boundary = validate_phase14_summary_surfaces(
        docs_root_text,
        tests_root_text,
        scripts_readme_text,
        survey_text,
        release_boundary_text.replace(
            "- shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture\n",
            "",
            1,
        ),
        makefile_text,
    )
    duplicate_docs_root = validate_phase14_summary_surfaces(
        docs_root_text
        + "\n- `Documentation/zigux/phase14-release-boundary-survey.md` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` now make the roadmap's core-adjacent sequencing step explicit from the docs root, so release-facing review no longer jumps directly from the active Phase 13 helper tranche to the Phase 15 governance packet.",
        tests_root_text,
        scripts_readme_text,
        survey_text,
        release_boundary_text,
        makefile_text,
    )
    stray_boundary_entry = validate_phase14_summary_surfaces(
        docs_root_text,
        tests_root_text,
        scripts_readme_text,
        survey_text.replace(
            "  - `zigux/tests/phase14_build.zig`\n",
            "  - `zigux/tests/phase14_build.zig`\n  - `zigux/tests/phase14_workqueue_bridge.zig`\n",
            1,
        ),
        release_boundary_text,
        makefile_text,
    )
    if (
        good
        or not missing_entrypoint
        or not missing_tests_packet
        or not duplicate_attached_toolchain
        or not duplicate_tests_packet
        or not missing_release_boundary
        or not duplicate_docs_root
        or not stray_boundary_entry
    ):
        print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY_SELF_TEST=fail")
        return 1

    print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY_SELF_TEST=pass")
    print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY_SELF_TEST_CASE_COUNT=8")
    return 0

def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        return run_self_test()

    docs_root_path = ROOT / "Documentation/zigux/README.md"
    tests_root_path = ROOT / "zigux/tests/README.md"
    scripts_readme_path = ROOT / "scripts/zigux/README.md"
    survey_path = ROOT / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
    release_boundary_path = ROOT / "Documentation/zigux/phase14-release-boundary-survey.md"
    makefile_path = ROOT / "zigux/Makefile"

    required_paths = [
        docs_root_path,
        tests_root_path,
        scripts_readme_path,
        survey_path,
        release_boundary_path,
        makefile_path,
    ]
    missing_files = [str(path) for path in required_paths if not path.exists()]
    if missing_files:
        print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY=fail")
        print("MISSING_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_FILES_END")
        return 1

    issues = validate_phase14_summary_surfaces(
        read(docs_root_path),
        read(tests_root_path),
        read(scripts_readme_path),
        read(survey_path),
        read(release_boundary_path),
        read(makefile_path),
    )
    if issues:
        print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY=fail")
        print("MISSING_MARKERS_START")
        for issue in issues:
            print(issue)
        print("MISSING_MARKERS_END")
        return 1

    print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY=pass")
    print(f"PHASE14_DOCS_ROOT_MARKER_COUNT={len(DOCS_ROOT_LINES)}")
    print(f"PHASE14_TESTS_ROOT_MARKER_COUNT={len(TESTS_ROOT_EXACT_LINE_COUNTS)}")
    print(f"PHASE14_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_EXACT_LINE_COUNTS)}")
    print(f"PHASE14_SURVEY_MARKER_COUNT={len(SURVEY_EXACT_LINE_COUNTS) + 1}")
    print(f"PHASE14_SURVEY_SHARED_SMOKE_BOUNDARY_ENTRY_COUNT={len(SURVEY_SHARED_SMOKE_BOUNDARY_BLOCK) - 1}")
    print(f"PHASE14_RELEASE_BOUNDARY_MARKER_COUNT={len(RELEASE_BOUNDARY_LINES)}")
    print(f"PHASE14_MAKEFILE_MARKER_COUNT={len(MAKEFILE_EXACT_LINE_COUNTS)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
