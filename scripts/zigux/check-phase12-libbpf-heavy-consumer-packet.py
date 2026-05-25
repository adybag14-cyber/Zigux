#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (
            candidate / "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
        ).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

HEAVY_CONSUMER_LANE_PATH = (
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
)
LIBBPF_SEGMENT_SURVEY_PATH = "Documentation/zigux/phase12-libbpf-segment-survey.md"
LIBBPF_VERIFY_SHARD_NOTE_PATH = (
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md"
)
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_CLOSURE_CHECKLIST_PATH = (
    "Documentation/zigux/phase12-release-closure-checklist.md"
)
RELEASE_READINESS_SURVEY_PATH = (
    "Documentation/zigux/phase12-release-readiness-survey.md"
)
RAW_GITHUB_COVERAGE_PATH = (
    "Documentation/zigux/phase12-raw-github-coverage-survey.md"
)
RELEASE_COORDINATION_MATRIX_PATH = (
    "Documentation/zigux/phase12-release-coordination-matrix.md"
)
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
LIBBPF_SNAPSHOT_CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-snapshot.py"
LIBBPF_LANE_MARKER_CHECKER_PATH = "scripts/zigux/check-phase12-libbpf-lane-marker.py"
RELEASE_READINESS_CHECKER_PATH = (
    "scripts/zigux/check-phase12-release-readiness-packet.py"
)
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
LIBBPF_SNAPSHOT_PATH = "zigux/tests/fixtures/phase12_libbpf_snapshot.json"
LIBBPF_SNAPSHOT_DETERMINISM_PATH = (
    "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json"
)

REQUIRED_FILES = [
    HEAVY_CONSUMER_LANE_PATH,
    LIBBPF_SEGMENT_SURVEY_PATH,
    LIBBPF_VERIFY_SHARD_NOTE_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    RELEASE_READINESS_SURVEY_PATH,
    RAW_GITHUB_COVERAGE_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    WORKFLOW_PATH,
    BUILD_ONLY_CHECKER_PATH,
    LIBBPF_SNAPSHOT_CHECKER_PATH,
    LIBBPF_LANE_MARKER_CHECKER_PATH,
    RELEASE_READINESS_CHECKER_PATH,
    VALIDATOR_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    LIBBPF_SNAPSHOT_PATH,
    LIBBPF_SNAPSHOT_DETERMINISM_PATH,
]

REQUIRED_MARKERS = {
    HEAVY_CONSUMER_LANE_PATH: [
        "- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
        "- complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`",
        "- Keep the shared libbpf packet explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` snapshot anchor, and the helper-local `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` determinism companion, while treating the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` as parked note-owned boundaries until they land again on current `master`, while keeping `tools/lib/bpf/zigux_segments/verify.zig` explicit as the directly readable compile-together shard for the current helper footing, and while keeping `tools/lib/bpf/zigux_segments/manifest.json` explicit as the directly readable helper-first packet catalog rather than as proof of a shipped shared replay route.",
        "- Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on current `master`, so keep `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` explicit here as shipped wrapper evidence and keep the directly readable support bundle explicit through `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py`, `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `scripts/zigux/validate-phase12.py` beside the returned smoke-and-test wrappers.",
        "- The shipped lane-marker guard now sits beside that same support bundle too: `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py --self-test` and `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py` keep the parked survey lane-key, manifest, and verify-shard boundary fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.",
        "- The shipped heavy-consumer guard now sits beside that same support bundle too: `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test` and `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the parked helper-first packet fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.",
        "- If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the shipped attached-toolchain reruns `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only fallback entrypoint.",
        "- Keep the degraded-workflow support bundle explicit beside that same order too:",
        "- The older helper-first segment footing remains a Phase 12 heavy-consumer packet on current `master`; do not recast it as lingering Phase 8 work now that the roadmap and docs root already place it in the shared Phase 12 release packet.",
        "- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper queueing and transport anchors, so this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.",
    ],
    LIBBPF_SEGMENT_SURVEY_PATH: [
        "- scope: Phase 12 roadmap comparison, shared survey truthfulness, the parked libbpf verify-shard plus snapshot companions, and the boundary between the still-present direct helper-first segment footing and the still-unadopted shared replay packet",
        "- rollback owner and reversible-delivery drill: restore the last truthful survey wording in this note, then rerun `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/validate-phase12.py`, and the shipped wrapper `make -C zigux phase12-validate`; then rerun `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-test`, and `make -C zigux phase12` so the shared Phase 12 release packet stays reviewable without pretending those shared routes already exercise the parked direct `phase12_libbpf_*` replay files directly`",
        "- `scripts/zigux/check-build-only-phase12-surface.py` is a shared release-packet checker for the active Phase 12 build-only contract. It exact-checks the current driver-facing release packet and adjacent PMO reminders, but it does not yet mean that the parked libbpf reviewability packet has been adopted into `zigux/tests/phase12_build.zig` or the shipped Make replay order.",
        "- current `master` now also ships the validator-side support bundle through `scripts/zigux/check-phase12-libbpf-snapshot.py`, its direct `--self-test` replay, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, and the returned wrapper `make -C zigux phase12-validate`; that smaller support bundle still complements the smoke-first shared replay order instead of proving that the parked libbpf reviewability packet has been adopted into `zigux/tests/phase12_build.zig` or the shared direct replay order.",
    ],
    LIBBPF_VERIFY_SHARD_NOTE_PATH: [
        "- shared survey companion: `Documentation/zigux/phase12-libbpf-segment-survey.md`",
        "- shared heavy-consumer anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
        "- snapshot checker: `scripts/zigux/check-phase12-libbpf-snapshot.py`",
        "- the current validator-first support bundle remains separate: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and the returned wrapper `make -C zigux phase12-validate` keep the shared release packet fail-closed without turning this parked note into a second direct replay route, while the returned `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` wrappers stay evidence for the broader shared smoke-first packet rather than proof for this parked note by themselves`",
    ],
    RELEASE_SEQUENCING_PATH: [
        "* shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`",
        "* verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "- The deterministic libbpf fixture pair stays explicit: `zigux/tests/fixtures/phase12_libbpf_snapshot.json` and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` remain required before the shared release packet can be described as ready for closure review.",
        "- The parked libbpf heavy-consumer packet stays explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being rounded up into a shipped shared replay claim.",
    ],
    RELEASE_READINESS_SURVEY_PATH: [
        "- adjacent release-planning surfaces that are present on current `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/README.md`, and `zigux/tests/README.md`",
        "- Because the parked verify-shard note still governs the shared libbpf packet through public-tree readback, `zigux/tests/fixtures/phase12_libbpf_snapshot.json` remains the parked visibility anchor for the note-owned libbpf reviewability packet on current `master`, while `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` remains the helper-local determinism companion for directly readable `tools/lib/bpf/zigux_segments/pin_path.zig`; the direct `phase12_libbpf_*` replay files remain note-owned or snapshot-backed boundaries and the directly readable `tools/lib/bpf/zigux_segments/verify.zig` shard remains helper footing rather than shipped shared-route evidence.",
    ],
    RAW_GITHUB_COVERAGE_PATH: [
        "  * verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
        "  * reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever fallback wording changes`",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
        "- Shared libbpf heavy-consumer packet: keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` aligned around the parked reviewability packet.",
    ],
    WORKFLOW_PATH: [
        "- name: Self-test current Phase 12 libbpf heavy-consumer packet checker\n        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test",
        "- name: Check current Phase 12 libbpf heavy-consumer packet\n        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
        "- name: Validate current Phase 12 support bundle\n        run: python3 scripts/zigux/validate-phase12.py",
    ],
    LIBBPF_SNAPSHOT_CHECKER_PATH: [
        "EXPECTED_SNAPSHOT_TRACKED_PATHS = [",
        "    \"Documentation/zigux/phase12-libbpf-segment-survey.md\",",
        "    \"Documentation/zigux/phase12-libbpf-verify-shard-note.md\",",
        "    \"Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md\",",
        "    \"Documentation/zigux/phase12-release-coordination-matrix.md\",",
        "EXPECTED_DETERMINISM_LANE_KEY = \"P12-L17\"",
        "EXPECTED_DETERMINISM_TRACKED_PATHS = [",
        "    \"tools/lib/bpf/zigux_segments/pin_path.zig\",",
        "SELF_TEST_CASE_COUNT = 29",
    ],
    SCRIPTS_README_PATH: [
        "- `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, and `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
        "- `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
    ],
    TESTS_README_PATH: [
        "Keep `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` explicit as the shared heavy-helper anti-overlap companion so the tests-root reminder stays aligned with the same parked libbpf boundary already named by the release-order, closure, readiness, coordination, fallback, and complex-driver notes.",
        "Keep `Documentation/zigux/phase12-raw-github-coverage-survey.md` explicit as the shared degraded-read companion so the tests-root reminder stays aligned with the same one-catalog plus one-current-master-gap-note companion plus shared-support-bundle fallback split already named by the PMO release packet.",
    ],
    VALIDATOR_PATH: [
        "LIBBPF_SNAPSHOT_CHECKER_PATH,",
        "LIBBPF_LANE_MARKER_CHECKER_PATH,",
        "HEAVY_CONSUMER_PACKET_CHECKER_PATH,",
        "\"PHASE12_LIBBPF_LANE_MARKER_SELF_TEST=pass\",",
        "\"PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_SELF_TEST=pass\",",
    ],
}

EXACT_COUNT_MARKERS = {
    HEAVY_CONSUMER_LANE_PATH: {
        "- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`": 1,
        "- complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`": 1,
        "- Keep the shared libbpf packet explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, the still-present `zigux/tests/fixtures/phase12_libbpf_snapshot.json` snapshot anchor, and the helper-local `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` determinism companion, while treating the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` as parked note-owned boundaries until they land again on current `master`, while keeping `tools/lib/bpf/zigux_segments/verify.zig` explicit as the directly readable compile-together shard for the current helper footing, and while keeping `tools/lib/bpf/zigux_segments/manifest.json` explicit as the directly readable helper-first packet catalog rather than as proof of a shipped shared replay route.": 1,
        "- Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on current `master`, so keep `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` explicit here as shipped wrapper evidence and keep the directly readable support bundle explicit through `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`, `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py`, `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test`, `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `scripts/zigux/validate-phase12.py` beside the returned smoke-and-test wrappers.": 1,
        "- The shipped lane-marker guard now sits beside that same support bundle too: `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py --self-test` and `python3 scripts/zigux/check-phase12-libbpf-lane-marker.py` keep the parked survey lane-key, manifest, and verify-shard boundary fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.": 1,
        "- The shipped heavy-consumer guard now sits beside that same support bundle too: `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test` and `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the parked helper-first packet fail-closed beside the snapshot checker and shared validator entrypoint without turning the shared release packet into a focused libbpf replay route.": 1,
        "- If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the shipped attached-toolchain reruns `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only fallback entrypoint.": 1,
        "- Keep the degraded-workflow support bundle explicit beside that same order too:": 1,
    },
    RELEASE_SEQUENCING_PATH: {
        "* verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`": 1,
    },
    RELEASE_CLOSURE_CHECKLIST_PATH: {
        "- The parked libbpf heavy-consumer packet stays explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being rounded up into a shipped shared replay claim.": 1,
    },
    RELEASE_READINESS_SURVEY_PATH: {
        "- adjacent release-planning surfaces that are present on current `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/README.md`, and `zigux/tests/README.md`": 1,
    },
    RAW_GITHUB_COVERAGE_PATH: {
        "  * verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`": 1,
    },
    LIBBPF_VERIFY_SHARD_NOTE_PATH: {
        "- snapshot checker: `scripts/zigux/check-phase12-libbpf-snapshot.py`": 1,
    },
    RELEASE_COORDINATION_MATRIX_PATH: {
        "- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`": 1,
        "- Shared libbpf heavy-consumer packet: keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` aligned around the parked reviewability packet.": 1,
    },
    WORKFLOW_PATH: {
        "Self-test current Phase 12 libbpf heavy-consumer packet checker": 1,
        "Check current Phase 12 libbpf heavy-consumer packet": 1,
        "Validate current Phase 12 support bundle": 1,
    },
    LIBBPF_SNAPSHOT_CHECKER_PATH: {
        "EXPECTED_DETERMINISM_TRACKED_PATHS = [": 1,
        "    \"tools/lib/bpf/zigux_segments/pin_path.zig\",": 1,
    },
    SCRIPTS_README_PATH: {
        "- `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, and `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`": 1,
    },
    VALIDATOR_PATH: {
        "LIBBPF_SNAPSHOT_CHECKER_PATH,": 1,
        "LIBBPF_LANE_MARKER_CHECKER_PATH,": 1,
        "HEAVY_CONSUMER_PACKET_CHECKER_PATH,": 1,
        "\"PHASE12_LIBBPF_LANE_MARKER_SELF_TEST=pass\",": 1,
        "\"PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_SELF_TEST=pass\",": 1,
    },
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in EXACT_COUNT_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker, expected_count in markers.items():
            actual_count = text.count(marker)
            if actual_count != expected_count:
                failures.append(
                    "wrong_count:"
                    f"{rel_path}:{marker}:expected={expected_count}:actual={actual_count}"
                )

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(markers) + "\n"


def fixture_text(rel_path: str) -> str:
    if rel_path in REQUIRED_MARKERS:
        title = {
            HEAVY_CONSUMER_LANE_PATH: "# Phase 12 Libbpf Heavy-Consumer Lane Sequencing",
            LIBBPF_SEGMENT_SURVEY_PATH: "# Phase 12 Libbpf Segment Survey",
            LIBBPF_VERIFY_SHARD_NOTE_PATH: "# Phase 12 Libbpf Verify Shard Note",
            RELEASE_SEQUENCING_PATH: "# Phase 12 Release Sequencing",
            RELEASE_CLOSURE_CHECKLIST_PATH: "# Phase 12 Release Closure Checklist",
            RELEASE_READINESS_SURVEY_PATH: "# Phase 12 Release Readiness Survey",
            RAW_GITHUB_COVERAGE_PATH: "# Phase 12 Raw GitHub Coverage Survey",
            RELEASE_COORDINATION_MATRIX_PATH: "# Phase 12 Release Coordination Matrix",
            WORKFLOW_PATH: "name: zigux-bootstrap",
            LIBBPF_SNAPSHOT_CHECKER_PATH: "#!/usr/bin/env python3",
            SCRIPTS_README_PATH: "# scripts/zigux",
            TESTS_README_PATH: "# zigux/tests",
        }.get(rel_path, "# Fixture")
        return marker_fixture(title, REQUIRED_MARKERS[rel_path])
    if rel_path.endswith(".json"):
        return '{\n  "lane_key": "P12-L16"\n}\n'
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel_path.endswith(".md"):
        return "# Fixture\n"
    return "fixture\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(marker + "\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    if updated == text:
        raise SystemExit(f"unable to mutate marker in fixture: {marker}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-libbpf-heavy-consumer-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        missing_file_cases = REQUIRED_FILES[:]
        for rel_path in missing_file_cases:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (rel_path, marker)
            for rel_path, markers in REQUIRED_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        exact_count_cases = [
            (rel_path, marker, expected_count)
            for rel_path, markers in EXACT_COUNT_MARKERS.items()
            for marker, expected_count in markers.items()
        ]
        for rel_path, marker, expected_count in exact_count_cases:
            write_fixture_tree(base)
            write_text(
                base / rel_path,
                (base / rel_path).read_text(encoding="utf-8") + marker + "\n",
            )
            expect_failure(
                base,
                "wrong_count:"
                f"{rel_path}:{marker}:expected={expected_count}:actual={expected_count + 1}"
            )

        case_count = (
            len(missing_file_cases)
            + len(marker_cases)
            + len(exact_count_cases)
        )
        print("PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_SELF_TEST=pass")
        print(
            "PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_SELF_TEST_CASE_COUNT="
            f"{case_count}"
        )
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current bounded Phase 12 libbpf heavy-consumer packet "
            "across the shared lane note, parked verify-shard note, survey, "
            "release-readiness note, degraded-read note, snapshot checker, and "
            "shared reminder surfaces."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET=pass")
    print(f"PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE12_LIBBPF_HEAVY_CONSUMER_PACKET_EXACT_COUNT_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_COUNT_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())