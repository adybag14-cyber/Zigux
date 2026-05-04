#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX40_NOTE = "survey provenance captured against verified `master` head"

DOCS_ROOT_LINES = [
    "Phase 14 notes",
    "`Documentation/zigux/phase14-release-boundary-survey.md` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` now make the roadmap's core-adjacent sequencing step explicit from the docs root",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay in study-only posture",
    "`kernel/rcu/tree.c` and `net/core/skbuff.c` remain blocked under the Phase 15 freeze-in-C governance packet",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zigux/tests/phase14_build.zig` now provide one validator-backed shared smoke gate",
    "reviewability lane rather than a closure or active subsystem delivery claim",
]

SURVEY_LINES = [
    "- PHASE14_SHARED_LANE=P14-L01",
    "- PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
    "- make -C zigux phase14-smoke",
    "- zigux/tests/phase14_build.zig",
    "- reviewability lane rather than a closure or active subsystem delivery claim",
    "- make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>",
    "- make -C zigux phase14-smoke ZIG=<attached-zig-path>",
    "- make -C zigux phase14-test ZIG=<attached-zig-path>",
    "- make -C zigux phase14 ZIG=<attached-zig-path>",
]

RELEASE_BOUNDARY_LINES = [
    "PHASE14_RELEASE_BOUNDARY=present",
    "PHASE14_SHARED_REPLAY_PRESENT=yes",
    "PHASE14_RELEASE_CLOSED=no",
    "shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture",
    "compile-shard matrix: one focused `phase14-smoke` shard still covers only `phase14-end-to-end-smoke-tests`, while `phase14-workqueue-bridge-tests`, `phase14-skbuff-bridge-tests`, `phase14-ring-buffer-survey-tests`, and `phase14-rcu-tree-survey-tests` remain `full_bundle_only` under `zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
    "combined shared replay entrypoint: `make -C zigux phase14` remains the published convenience route for the validator-backed smoke packet, so release-facing review and local replay still name the same one-command path as the shared smoke note and manifest instead of leaving that wrapper path implicit in `zigux/Makefile`",
    "PHASE14_SHARED_SMOKE_GATE_COUNT=1",
    "PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0",
    "Keep this lane parked unless the shared smoke packet or one of the four anchor-local Phase 14 manifests moves. If that happens, refresh this release-boundary reading and the docs-root Phase 14 summary so the release-facing story keeps matching the validator-backed smoke packet without widening it into a new active delivery claim.",
]

SCRIPTS_README_LINES = [
    "- `check-phase14-docs-root-smoke-summary.py`",
    "`Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` keep the exact rollback threshold",
    "`make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`",
    "`make -C zigux phase14-smoke ZIG=<attached-zig-path>`",
    "`make -C zigux phase14-test ZIG=<attached-zig-path>`",
    "`make -C zigux phase14 ZIG=<attached-zig-path>`",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def require_exact_count(
    label: str,
    text: str,
    markers: list[str],
    expected_count: int,
    *,
    exact_line: bool = False,
) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        actual_count = count_exact_line(text, marker) if exact_line else text.count(marker)
        if actual_count != expected_count:
            issues.append(f"{label}:{actual_count}:{marker}")
    return issues


def validate_phase14_summary_surfaces(
    docs_root_text: str,
    survey_text: str,
    release_boundary_text: str,
    scripts_readme_text: str,
) -> list[str]:
    missing = require_exact_count("docs_root", docs_root_text, DOCS_ROOT_LINES, 1)
    missing.extend(
        require_exact_count("survey", survey_text, SURVEY_LINES, 1, exact_line=True)
    )
    missing.extend(
        require_exact_count(
            "release_boundary", release_boundary_text, RELEASE_BOUNDARY_LINES, 1
        )
    )
    missing.extend(
        require_exact_count(
            "scripts_readme", scripts_readme_text, SCRIPTS_README_LINES, 1
        )
    )
    if survey_text.count(HEX40_NOTE) != 1:
        missing.append(f"survey:{survey_text.count(HEX40_NOTE)}:{HEX40_NOTE}")
    return missing


def run_self_test() -> int:
    docs_root_text = """
Phase 14 notes
- `Documentation/zigux/phase14-release-boundary-survey.md` and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` now make the roadmap's core-adjacent sequencing step explicit from the docs root, so release-facing review no longer jumps directly from the active Phase 13 helper tranche to the Phase 15 governance packet.
- the current Phase 14 release reading is intentionally boundary-only: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay in study-only posture, while `kernel/rcu/tree.c` and `net/core/skbuff.c` remain blocked under the Phase 15 freeze-in-C governance packet rather than being treated as an active release lane.
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zigux/tests/phase14_build.zig` now provide one validator-backed shared smoke gate for that study-only four-anchor packet; it stays a reviewability lane rather than a closure or active subsystem delivery claim.
""".strip()

    survey_text = """
- PHASE14_SHARED_LANE=P14-L01
- PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate
- survey provenance captured against verified `master` head `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- make -C zigux phase14-smoke
- zigux/tests/phase14_build.zig
- reviewability lane rather than a closure or active subsystem delivery claim
- make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>
- make -C zigux phase14-smoke ZIG=<attached-zig-path>
- make -C zigux phase14-test ZIG=<attached-zig-path>
- make -C zigux phase14 ZIG=<attached-zig-path>
""".strip()

    release_boundary_text = """
- PHASE14_RELEASE_BOUNDARY=present
- PHASE14_SHARED_REPLAY_PRESENT=yes
- PHASE14_RELEASE_CLOSED=no
- shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture
- compile-shard matrix: one focused `phase14-smoke` shard still covers only `phase14-end-to-end-smoke-tests`, while `phase14-workqueue-bridge-tests`, `phase14-skbuff-bridge-tests`, `phase14-ring-buffer-survey-tests`, and `phase14-rcu-tree-survey-tests` remain `full_bundle_only` under `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
- combined shared replay entrypoint: `make -C zigux phase14` remains the published convenience route for the validator-backed smoke packet, so release-facing review and local replay still name the same one-command path as the shared smoke note and manifest instead of leaving that wrapper path implicit in `zigux/Makefile`
- PHASE14_SHARED_SMOKE_GATE_COUNT=1
- PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0
- Keep this lane parked unless the shared smoke packet or one of the four anchor-local Phase 14 manifests moves. If that happens, refresh this release-boundary reading and the docs-root Phase 14 summary so the release-facing story keeps matching the validator-backed smoke packet without widening it into a new active delivery claim.
""".strip()

    scripts_readme_text = """
Current bootstrap helpers
- `validate-phase14.py`
- `check-phase14-docs-root-smoke-summary.py`

Phase 14 flow
- `check-phase14-docs-root-smoke-summary.py --self-test` and `check-phase14-docs-root-smoke-summary.py` keep the docs-root Phase 14 smoke summary and the shared smoke survey fail-closed around the same validator-backed `phase14-validate`, focused `phase14-smoke`, and study-only reviewability wording before the broader shared validator runs.
- `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` keep the exact rollback threshold, automatic return-to-blocked trigger list, and ZAR-to-product transfer rationale visible from the docs root rather than relying on run memory.
- attached-toolchain fallback commands stay explicit in the scripts index too: `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`, `make -C zigux phase14-smoke ZIG=<attached-zig-path>`, `make -C zigux phase14-test ZIG=<attached-zig-path>`, and `make -C zigux phase14 ZIG=<attached-zig-path>`.
""".strip()

    cases = [
        (
            "happy_path",
            docs_root_text,
            survey_text,
            release_boundary_text,
            scripts_readme_text,
            False,
        ),
        (
            "missing_docs_root_smoke_gate",
            docs_root_text.replace("validator-backed shared smoke gate", "shared smoke gate"),
            survey_text,
            release_boundary_text,
            scripts_readme_text,
            True,
        ),
        (
            "missing_docs_root_checker_reference",
            docs_root_text.replace(
                "`scripts/zigux/check-phase14-docs-root-smoke-summary.py`, ",
                "",
            ),
            survey_text,
            release_boundary_text,
            scripts_readme_text,
            True,
        ),
        (
            "missing_survey_entrypoint",
            docs_root_text,
            survey_text.replace(
                "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate", ""
            ),
            release_boundary_text,
            scripts_readme_text,
            True,
        ),
        (
            "duplicate_docs_root_smoke_gate",
            docs_root_text
            + "\n- `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zigux/tests/phase14_build.zig` now provide one validator-backed shared smoke gate for that study-only four-anchor packet; it stays a reviewability lane rather than a closure or active subsystem delivery claim.",
            survey_text,
            release_boundary_text,
            scripts_readme_text,
            True,
        ),
        (
            "duplicate_survey_provenance",
            docs_root_text,
            survey_text
            + "\n- survey provenance captured against verified `master` head `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`",
            release_boundary_text,
            scripts_readme_text,
            True,
        ),
        (
            "missing_release_boundary_marker",
            docs_root_text,
            survey_text,
            release_boundary_text.replace("- PHASE14_RELEASE_BOUNDARY=present\n", ""),
            scripts_readme_text,
            True,
        ),
        (
            "missing_shared_replay_marker",
            docs_root_text,
            survey_text,
            release_boundary_text.replace("- PHASE14_SHARED_REPLAY_PRESENT=yes\n", ""),
            scripts_readme_text,
            True,
        ),
        (
            "missing_release_closed_marker",
            docs_root_text,
            survey_text,
            release_boundary_text.replace("- PHASE14_RELEASE_CLOSED=no\n", ""),
            scripts_readme_text,
            True,
        ),
        (
            "missing_release_boundary_smoke_gate",
            docs_root_text,
            survey_text,
            release_boundary_text.replace("shared full-bundle replay", "full-bundle replay"),
            scripts_readme_text,
            True,
        ),
        (
            "missing_release_boundary_compile_shard_matrix",
            docs_root_text,
            survey_text,
            release_boundary_text.replace(
                "- compile-shard matrix: one focused `phase14-smoke` shard still covers only `phase14-end-to-end-smoke-tests`, while `phase14-workqueue-bridge-tests`, `phase14-skbuff-bridge-tests`, `phase14-ring-buffer-survey-tests`, and `phase14-rcu-tree-survey-tests` remain `full_bundle_only` under `zig build test --build-file zigux/tests/phase14_build.zig --summary all`\n",
                "",
            ),
            scripts_readme_text,
            True,
        ),
        (
            "missing_release_boundary_combined_entrypoint",
            docs_root_text,
            survey_text,
            release_boundary_text.replace(
                "- combined shared replay entrypoint: `make -C zigux phase14` remains the published convenience route for the validator-backed smoke packet, so release-facing review and local replay still name the same one-command path as the shared smoke note and manifest instead of leaving that wrapper path implicit in `zigux/Makefile`\n",
                "",
            ),
            scripts_readme_text,
            True,
        ),
        (
            "duplicate_release_boundary_status",
            docs_root_text,
            survey_text,
            release_boundary_text + "\n- PHASE14_SHARED_REPLAY_PRESENT=yes",
            scripts_readme_text,
            True,
        ),
        (
            "duplicate_release_closed_status",
            docs_root_text,
            survey_text,
            release_boundary_text + "\n- PHASE14_RELEASE_CLOSED=no",
            scripts_readme_text,
            True,
        ),
        (
            "missing_scripts_readme_helper",
            docs_root_text,
            survey_text,
            release_boundary_text,
            scripts_readme_text.replace("- `check-phase14-docs-root-smoke-summary.py`", ""),
            True,
        ),
        (
            "missing_scripts_readme_release_boundary_line",
            docs_root_text,
            survey_text,
            release_boundary_text,
            scripts_readme_text.replace(
                "- `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` keep the exact rollback threshold, automatic return-to-blocked trigger list, and ZAR-to-product transfer rationale visible from the docs root rather than relying on run memory.\n",
                "",
            ),
            True,
        ),
        (
            "duplicate_scripts_readme_release_boundary_line",
            docs_root_text,
            survey_text,
            release_boundary_text,
            scripts_readme_text
            + "\n- `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/tests/phase14_end_to_end_smoke_survey.zig` keep the exact rollback threshold, automatic return-to-blocked trigger list, and ZAR-to-product transfer rationale visible from the docs root rather than relying on run memory.",
            True,
        ),
        (
            "duplicate_scripts_readme_helper",
            docs_root_text,
            survey_text,
            release_boundary_text,
            scripts_readme_text + "\n- `check-phase14-docs-root-smoke-summary.py`",
            True,
        ),
        (
            "missing_attached_toolchain_phase14_test",
            docs_root_text,
            survey_text.replace(
                "make -C zigux phase14-test ZIG=<attached-zig-path>", ""
            ),
            release_boundary_text,
            scripts_readme_text,
            True,
        ),
        (
            "duplicate_attached_toolchain_phase14_smoke",
            docs_root_text,
            survey_text
            + "\n- make -C zigux phase14-smoke ZIG=<attached-zig-path>",
            release_boundary_text,
            scripts_readme_text,
            True,
        ),
        (
            "missing_scripts_readme_phase14_test_fallback",
            docs_root_text,
            survey_text,
            release_boundary_text,
            scripts_readme_text.replace(
                "`make -C zigux phase14-test ZIG=<attached-zig-path>`, ", ""
            ),
            True,
        ),
        (
            "duplicate_scripts_readme_phase14_validate_fallback",
            docs_root_text,
            survey_text,
            release_boundary_text,
            scripts_readme_text
            + "\n- duplicate: `make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`",
            True,
        ),
    ]

    for (
        name,
        docs_text,
        survey_value,
        release_boundary_value,
        scripts_readme_value,
        should_fail,
    ) in cases:
        missing = validate_phase14_summary_surfaces(
            docs_text,
            survey_value,
            release_boundary_value,
            scripts_readme_value,
        )
        failed = bool(missing)
        if failed != should_fail:
            print(f"PHASE14_DOCS_ROOT_SMOKE_SUMMARY_SELF_TEST={name}:fail")
            if missing:
                print("MISSING_MARKERS_START")
                for marker in missing:
                    print(marker)
                print("MISSING_MARKERS_END")
            return 1

    print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY_SELF_TEST=pass")
    print(f"PHASE14_DOCS_ROOT_SMOKE_SUMMARY_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        return run_self_test()

    docs_root_path = ROOT / "Documentation/zigux/README.md"
    survey_path = ROOT / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
    release_boundary_path = ROOT / "Documentation/zigux/phase14-release-boundary-survey.md"
    scripts_readme_path = ROOT / "scripts/zigux/README.md"

    required_paths = [
        docs_root_path,
        survey_path,
        release_boundary_path,
        scripts_readme_path,
    ]
    missing_files = [str(path) for path in required_paths if not path.exists()]
    if missing_files:
        print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY=fail")
        print("MISSING_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_FILES_END")
        return 1

    missing = validate_phase14_summary_surfaces(
        read(docs_root_path),
        read(survey_path),
        read(release_boundary_path),
        read(scripts_readme_path),
    )
    if missing:
        print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY=fail")
        print("MISSING_MARKERS_START")
        for marker in missing:
            print(marker)
        print("MISSING_MARKERS_END")
        return 1

    print("PHASE14_DOCS_ROOT_SMOKE_SUMMARY=pass")
    print(f"PHASE14_DOCS_ROOT_MARKER_COUNT={len(DOCS_ROOT_LINES)}")
    print(f"PHASE14_SURVEY_MARKER_COUNT={len(SURVEY_LINES) + 1}")
    print(f"PHASE14_RELEASE_BOUNDARY_MARKER_COUNT={len(RELEASE_BOUNDARY_LINES)}")
    print(f"PHASE14_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
