#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PHASE4_GATE_EXPECTATIONS = {
    "atomic64_diff.zig": {
        "owner": "ABI and Runtime Team",
        "rollback_owner": "ABI and Runtime Team",
        "fallback_path": "keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses",
        "exact_check_markers": [
            "`addCounter()`",
            "onestwos growth",
            "`-1` decrement",
            "`or`",
            "`and`",
            "`xor`",
            "`andnot`",
            "`v0 -> v1`",
            "`v1 -> v2`",
            "`minInt(i64) -> -1`",
            "`cmpxchg`",
            "match-store",
            "mismatch-no-store",
            "`addUnlessCounter()`",
            "blocked and changed cases",
            "`incNotZeroCounter()`",
            "positive, zero, `-1`, and `minInt(i64)`",
            "`decIfPositiveCounter()`",
            "positive, zero, and negative return-path behavior",
            "ordered operation families",
            "`checked_returning_paths`",
            "`checked_guard_paths`",
            "post-exit invalid lifecycle errors",
            "post-selftest replay",
        ],
        "threshold_status": "correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded add, sub, bitwise, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay set",
        "threshold_posture": "threshold_pending_until_runtime_atomic64_scope_widens",
        "gate_scope": "add, sub, bitwise, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay",
        "threshold_scope": "add, sub, bitwise, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay set",
        "local_replay_markers": [
            "phase4-runtime-atomic64-diff-tests",
            "phase4-runtime-atomic64-diff-survey-tests",
        ],
        "reversible_delivery": "`lib/atomic64_test.c` stays the source of truth, and removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move while `runtime_atomic64_diff.zig` remains the single replay body and the existing Phase 9 runtime atomic64 starter remains the forward path",
    },
    "bitmap_diff.zig": {
        "owner": "Shared Subsystems Pod",
        "rollback_owner": "Shared Subsystems Pod",
        "fallback_path": "keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses",
        "rollback_evidence_gap": "direct `bitmap_fill(..., 115)` still stops at bit 114 in the shipped Zig helper, so the Phase 4 packet keeps that mismatch survey-only instead of claiming parity with the `lib/test_bitmap.c` rounded two-word anchor",
        "exact_check_markers": [
            "`bitmap_fill(..., 35)`",
            "`bitmap_fill(..., 115)`",
            "`bitmap_zero(..., 35)`",
            "`bitmap_zero(..., 115)`",
            "`bitmap_set(..., 79, 19)`",
            "`bitmap_clear(..., 79, 19)`",
            "`bitmap_fill(..., 1024)`",
            "`bitmap_zero(..., 1024)`",
            "`1-3,7,10-11`",
            "truncated `1-3` rendering",
            "23-bit single-word window",
            "cleared-destination copies",
            "filled-destination copies",
            "109-bit partial-tail",
            "97-bit aligned-copy",
            "`bitmap.copyClearTail()` keeps the 109-bit cleared-tail contract",
            "full-width nth-7 and nth-8 outcomes",
            "bit 123 for nth 7",
            "cutoff width for nth 8",
        ],
        "threshold_status": "correctness-only gate today; no hard timing threshold is approved until the lane grows past the current bounded range, rounded-prefix, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior checkpoints",
        "threshold_posture": "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
        "gate_scope": "bounded bitmap range, rounded-prefix, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior replay",
        "threshold_scope": "range, rounded-prefix, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior checkpoints",
        "local_replay_markers": [
            "phase4-bitmap-diff-tests",
        ],
        "reversible_delivery": "`lib/test_bitmap.c` stays the source of truth, and removing `bitmap_diff.zig` from the shared `phase4_build.zig` entrypoint falls back to the existing broad bitmap parity checks",
    },
}

REQUIRED_FILES = [
    "scripts/zigux/artifact_diff.py",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "scripts/zigux/check-phase4-kprobe-example-packet.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "samples/kprobes/Makefile",
    "samples/kprobes/kprobe_example.c",
    "samples/vfs/Makefile",
    "samples/vfs/test-fsmount.c",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
]

REQUIRED_MAKE_MARKERS = [
    "PHONY += phase4-validate phase4-test phase4-runtime-atomic64-diff phase4-test-fsmount-survey phase4-kprobe-example-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4",
    "phase4-validate:",
    "scripts/zigux/artifact_diff.py --self-test",
    "scripts/zigux/check-artifact-diff-contract.py",
    "scripts/zigux/check-phase4-kprobe-example-packet.py --self-test",
    "scripts/zigux/check-phase4-kprobe-example-packet.py",
    "scripts/zigux/check-phase4-workflow-route-counts.py --self-test",
    "scripts/zigux/check-phase4-workflow-route-counts.py",
    "scripts/zigux/validate-phase4.py",
    "scripts/zigux/validate-phase4.py --self-test",
    "scripts/zigux/check-phase4-gate-evidence.py --self-test",
    "scripts/zigux/check-phase4-gate-evidence.py",
    "phase4-test:",
    "zigux/tests/phase4_build.zig",
    "phase4-kprobe-example-survey:",
    "phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
    "phase4-perf-baseline-survey:",
    "phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
]

EXACT_REQUIRED_MAKE_LINES = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-kprobe-example-packet.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py",
]

REQUIRED_WORKFLOW_MARKERS = [
    "Self-test Phase 4 validator",
    "Validate Phase 4 diff gates",
    "Run Phase 4 diff tests",
    "make -C zigux phase4-validate",
    "make -C zigux phase4-test",
]

REQUIRED_DOC_MARKERS = [
    "Current Phase 4 use",
    "python3 scripts/zigux/artifact_diff.py --self-test",
    "python3 scripts/zigux/check-artifact-diff-contract.py",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
    "Documentation/zigux/artifact-diff.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "shared comparison layer that already backs the bounded host-side tools under `scripts/zigux/`",
    "keeps stale expected-output and catalog drift small, auditable, and easy to refresh",
    "`EXPECTED_JSON_ERROR=`",
    "`ACTUAL_JSON_ERROR=`",
]

REQUIRED_DOC_MARKER_GROUPS = [
    (
        "reversible_delivery_link",
        [
            "reversible-delivery",
            "current C anchor",
        ],
    ),
]

FORBIDDEN_DOC_MARKERS = [
    "future Phase 2 tooling work will reuse",
    "reuse the same artifact-diff pattern for Phase 2 dual-implementation and bridge outputs such as `fixdep`, `genksyms`, `genksyms_crc`, `kconfig_bridge`, and `mk_elfconfig`",
]

REQUIRED_TESTS_README_MARKERS = [
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "make -C zigux phase4-kprobe-example-survey",
    "phase4-kprobe-example-survey-tests",
    "c_anchor_only_until_kprobe_example_starter_lands",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_build.zig",
    "scripts/zigux/validate-phase4.py",
    "make -C zigux phase4-perf-baseline-survey",
    "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
]

REQUIRED_SCRIPT_README_MARKERS = [
    "artifact_diff.py --self-test",
    "check-artifact-diff-contract.py",
    "check-phase4-kprobe-example-packet.py --self-test",
    "check-phase4-kprobe-example-packet.py",
    "check-phase4-workflow-route-counts.py --self-test",
    "check-phase4-workflow-route-counts.py",
    "make -C zigux phase4-validate",
    "make -C zigux phase4-kprobe-example-survey",
    "make -C zigux phase4-test-fsmount-survey",
    "make -C zigux phase4-perf-baseline-survey",
    "validate-phase4.py",
    "Phase 4 flow",
    "phase4_build.zig",
    "phase4-validation-matrix.md",
    "phase4-kprobe-example-survey",
    "phase4-kprobe-example-survey-tests",
    "phase4-test-fsmount-survey",
    "phase4-runtime-atomic64-diff-survey-tests",
    "phase4_perf_baseline_manifest.json",
    "phase4-perf-baseline-survey-tests",
    "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
    "reversible-delivery evidence",
]

REQUIRED_DOC_README_MARKERS = [
    "Phase 4 notes",
    "make -C zigux phase4-validate",
    "python3 scripts/zigux/artifact_diff.py --self-test",
    "check-artifact-diff-contract.py",
    "check-phase4-kprobe-example-packet.py",
    "check-phase4-workflow-route-counts.py",
    "validate-phase4.py",
    "phase4-validation-matrix.md",
    "Validate Phase 4 diff gates",
    "Run Phase 4 diff tests",
    "phase4-kprobe-example-survey",
    "phase4-kprobe-example-survey-tests",
    "still-absent `samples/zigux/kprobe_example.zig` sample explicitly survey-only",
    "phase4-test-fsmount-survey",
    "phase4-runtime-atomic64-diff-survey-tests",
    "phase4_perf_baseline_manifest.json",
    "phase4-perf-baseline-survey-tests",
    "make -C zigux phase4-perf-baseline-survey",
    "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
    "reversible-delivery evidence",
]

REQUIRED_PHASE4_MATRIX_MARKERS = [
    "scripts/zigux/artifact_diff.py --self-test",
    "python3 scripts/zigux/check-artifact-diff-contract.py",
    "Documentation/zigux/phase4-gate-evidence.md",
    "deterministic_preflight_required_for_host_side_diff_tools",
    "roadmap names `zigux/tests/atomic64_diff.zig`",
    "canonical wrapper while the bounded atomic64 replay gate at `zigux/tests/runtime_atomic64_diff.zig` remains the single underlying replay body",
    "atomic64_diff.zig",
    "runtime_atomic64_diff.zig",
    "phase4_runtime_atomic64_diff_survey.zig",
    "phase4_kprobe_example_manifest.json",
    "phase4_kprobe_example_survey.zig",
    "phase4-kprobe-example-survey-tests",
    "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
    "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "c_anchor_only_until_kprobe_example_starter_lands",
    "phase4_perf_baseline_manifest.json",
    "phase4-perf-baseline-survey-tests",
    "make -C zigux phase4-perf-baseline-survey",
    "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
    "threshold_pending_until_runtime_atomic64_scope_widens",
    "threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks",
    "bitmap_diff.zig",
    "rollback owner",
    "lab and CI matrix",
    "reversible delivery evidence",
    "perf threshold status",
    "Validate Phase 4 diff gates",
    "Run Phase 4 diff tests",
    "make -C zigux phase4-validate",
    "make -C zigux phase4-test",
    "phase4-runtime-atomic64-diff-tests",
    "phase4-runtime-atomic64-diff-survey-tests",
    "phase4-test-fsmount-survey-tests",
    "phase4-kprobe-example-survey-tests",
    "phase4-perf-baseline-survey-tests",
    "phase4-bitmap-diff-tests",
    "make -C zigux phase4-test-fsmount-survey",
    "make -C zigux phase4-perf-baseline-survey",
    "c_anchor_only_until_test_fsmount_starter_lands",
    "Remaining Measurability Gaps Vs Roadmap",
    "samples/zigux/kprobe_example.zig",
    "samples/zigux/test_fsmount.zig",
    "the current anchor remains `samples/vfs/test-fsmount.c` through `samples/vfs/Makefile` and `userprogs-always-y += test-fsmount`",
    "reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/vfs`; the Zig lab matrix remains C-anchor-only and no hard timing threshold is approved before a bounded Zig sample lands",
    "benchmark command and acceptable limit are still unapproved for both landed gates",
    "paired exact readback note",
    "inspected `master` head",
]

ROADMAP_GAP_EXPECTATIONS = {
    "samples/zigux/kprobe_example.zig": {
        "current_repo_state": "not present on `master`; the current anchor remains `samples/kprobes/kprobe_example.c` through `samples/kprobes/Makefile` and `CONFIG_SAMPLE_KPROBES`, and the validator-backed absence check keeps that true today",
        "measurability_gap": "reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`; the Zig lab matrix remains C-anchor-only and no hard timing threshold is approved before a bounded Zig sample lands",
        "next_bounded_step": "land one bounded survey manifest or starter gate under `samples/zigux/` that keeps the same owner, rollback owner, and replay command before claiming this anchor as active Phase 4 work",
    },
    "samples/zigux/test_fsmount.zig": {
        "current_repo_state": "not present on `master`; the current anchor remains `samples/vfs/test-fsmount.c` through `samples/vfs/Makefile` and `userprogs-always-y += test-fsmount`, the validator-backed absence check keeps that true today, and the manifest-backed survey gate now lives in `zigux/tests/phase4_test_fsmount_manifest.json` plus `zigux/tests/phase4_test_fsmount_survey.zig` under the shared `phase4-test-fsmount-survey-tests` replay",
        "measurability_gap": "reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/vfs`; the Zig lab matrix remains C-anchor-only and no hard timing threshold is approved before a bounded Zig sample lands",
        "next_bounded_step": "land one bounded starter under `samples/zigux/test_fsmount.zig` that keeps the same owner, rollback owner, and `make M=samples/vfs` replay contract before claiming this anchor as active Phase 4 work",
    },
    "perf baselines and thresholds for the two shipped rollback gates": {
        "current_repo_state": "`zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` are still correctness-only gates today",
        "measurability_gap": "benchmark command and acceptable limit are still unapproved for both landed gates",
        "next_bounded_step": "land one bounded benchmark command and one acceptable limit per gate before Phase 4 claims perf coverage",
    },
}

PHASE4_SURVEY_MATRIX_EXPECTATIONS = {
    "zigux/tests/phase4_test_fsmount_survey.zig": {
        "owner": "Validation and Perf Team",
        "rollback_owner": "Validation and Perf Team",
        "bootstrap_ci_replay_markers": [
            "Validate Phase 4 diff gates",
            "Run Phase 4 diff tests",
            "phase4-test-fsmount-survey-tests",
        ],
        "local_lab_replay_markers": [
            "make -C zigux phase4-test-fsmount-survey",
            "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
            "make M=samples/vfs",
        ],
        "reversible_delivery_markers": [
            "`samples/vfs/test-fsmount.c` stays the source of truth",
            "C-anchor-only until a bounded `samples/zigux/test_fsmount.zig` starter lands",
            "returns this roadmap row to matrix-only tracking without overstating a landed Zig sample",
        ],
        "threshold_posture": "c_anchor_only_until_test_fsmount_starter_lands",
    },
    "zigux/tests/phase4_kprobe_example_survey.zig": {
        "owner": "Validation and Perf Team",
        "rollback_owner": "Validation and Perf Team",
        "bootstrap_ci_replay_markers": [
            "Validate Phase 4 diff gates",
            "Run Phase 4 diff tests",
            "phase4-kprobe-example-survey-tests",
        ],
        "local_lab_replay_markers": [
            "make -C zigux phase4-kprobe-example-survey",
            "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
            "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
        ],
        "reversible_delivery_markers": [
            "`samples/kprobes/kprobe_example.c` stays the source of truth",
            "C-anchor-only until a bounded `samples/zigux/kprobe_example.zig` starter lands",
            "returns this roadmap row to matrix-only tracking without overstating a landed Zig sample",
        ],
        "threshold_posture": "c_anchor_only_until_kprobe_example_starter_lands",
    },
    "zigux/tests/phase4_perf_baseline_survey.zig": {
        "owner": "Validation and Perf Team",
        "rollback_owner": "Validation and Perf Team",
        "bootstrap_ci_replay_markers": [
            "Validate Phase 4 diff gates",
            "Run Phase 4 diff tests",
            "phase4-perf-baseline-survey-tests",
        ],
        "local_lab_replay_markers": [
            "make -C zigux phase4-perf-baseline-survey",
            "zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig",
            "phase4-runtime-atomic64-diff-tests",
            "phase4-runtime-atomic64-diff-survey-tests",
            "phase4-bitmap-diff-tests",
        ],
        "reversible_delivery_markers": [
            "`zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` remain the shipped rollback gates",
            "only machine-checked record that their benchmark command and acceptable limit are still unapproved",
            "instead of landed",
        ],
        "threshold_posture": "perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land",
    },
}

PHASE4_KPROBE_MANIFEST_EXPECTATIONS = {
    "lane_key": "P4-L19",
    "phase": "Phase 4",
    "owner": "Validation and Perf Team",
    "rollback_owner": "Validation and Perf Team",
    "anchor": "samples/kprobes/kprobe_example.c",
    "roadmap_destinations": ["samples/zigux/kprobe_example.zig"],
    "current_replay": "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "isolated_survey_replay": "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
    "shared_build_replay": "phase4-kprobe-example-survey-tests",
    "threshold_posture": "c_anchor_only_until_kprobe_example_starter_lands",
    "survey_summary": {
        "kprobe_makefile_replay_present": true,
        "kprobe_anchor_symbol_present": true,
        "zig_sample_present": false,
        "phase4_build_present": true,
        "phase4_validation_matrix_present": true,
        "phase4_gate_evidence_present": true
      }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 4 diff bundle.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in synthetic marker-contract check.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_markers = validate_root(ROOT)
    if missing_markers:
        print("PHASE4_VALIDATION=fail")
        print("MISSING_PHASE4_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE4_MARKERS_END")
        return 1

    print("PHASE4_VALIDATION=pass")
    print(f"PHASE4_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE4_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
