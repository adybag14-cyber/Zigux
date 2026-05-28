#!/usr/bin/env python3
"""PHASE12_CHECK_PACKET=virtio_scsi_packet

Fail-closed checker for the rollback-only Phase 12 virtio_scsi survey packet.
It keeps the slice note, survey note, fallback catalog, fixture manifest,
survey manifest, survey gate, dedicated survey-build route, and shared support-bundle reminders aligned around
current repo reality.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

MARKER = "PHASE12_CHECK_PACKET=virtio_scsi_packet"
SELF_TEST_MARKER = "PHASE12_VIRTIO_SCSI_PACKET_SELF_TEST"

SLICE_PATH = "Documentation/zigux/phase12-virtio-scsi-slice.md"
SURVEY_NOTE_PATH = "Documentation/zigux/phase12-virtio-scsi-survey.md"
FALLBACK_CATALOG_PATH = (
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md"
)
FIXTURE_MANIFEST_PATH = "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json"
SURVEY_MANIFEST_PATH = "zigux/tests/phase12_virtio_scsi_manifest.json"
SURVEY_GATE_PATH = "zigux/tests/phase12_virtio_scsi_survey.zig"
SURVEY_BUILD_PATH = "zigux/tests/phase12_virtio_scsi_survey_build.zig"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
MAKEFILE_PATH = "zigux/Makefile"
SUPPORT_PACKET_PATH = "zigux/tests/phase12_virtio_scsi_packet.zig"
VALIDATOR_PACKET_CHECKER_PATH = (
    "scripts/zigux/check-phase12-virtio-scsi-validator-packet.py"
)

REQUIRED_FILES = [
    SLICE_PATH,
    SURVEY_NOTE_PATH,
    FALLBACK_CATALOG_PATH,
    FIXTURE_MANIFEST_PATH,
    SURVEY_MANIFEST_PATH,
    SURVEY_GATE_PATH,
    SURVEY_BUILD_PATH,
    PHASE12_BUILD_PATH,
    MAKEFILE_PATH,
    VALIDATOR_PACKET_CHECKER_PATH,
]

TEXT_MARKERS = {
    SLICE_PATH: [
        "`PHASE12_SLICE=virtio-scsi-rollback-evidence`",
        "active `P12-L09` survey packet",
        "current `master` no longer serves `drivers/scsi/virtio_scsi.zig`",
        "rollback evidence only",
    ],
    SURVEY_NOTE_PATH: [
        "`PHASE12_STATUS=rollback-evidence-only-live-starter-missing`",
        "* `PHASE12_LANE=P12-L09`",
        "* verified on: `2026-05-24`",
        "* `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`",
        "rollback owner: `P12-L09` keeps the active virtio_scsi survey packet",
        "throughput-parity, and survey-gate tests together with one bounded NVMe direct replay as support-bundle evidence",
        "make -C zigux phase12-validate",
        "zig build test --build-file zigux/tests/phase12_build.zig --summary all",
        "make -C zigux phase12-test",
        "make -C zigux phase12",
        "rollback-only split machine-checkable",
        "* `zigux/tests/phase12_virtio_scsi_survey_build.zig`",
    ],
    FALLBACK_CATALOG_PATH: [
        "`PHASE12_STATUS=archival-raw-read-fallback`",
        "commit pin: `ee64eec272a352da1d967999c99bb3c3560c9b97`",
        "- exact coverage evidence refreshed on `2026-05-27` against live current `master`",
        "- authenticated contents view now returns this refreshed archival catalog body on current `master` with exact blob `46c4cc86cb2f164a9709ffbe46e1b8cd563a3259`",
        "- public blob page and public raw `master` fallback now match this same `46c4cc86cb2f164a9709ffbe46e1b8cd563a3259` current-master catalog body as of `2026-05-27`",
        "`zigux/tests/phase12_virtio_scsi_survey_build.zig` `2d502aad14ed244c614095060be986dd4514652e`",
        "`zigux/tests/phase12_build.zig` `e0d297f50d2805948b93ca421ae9ec20ddfceafa`",
        "`scripts/zigux/check-phase12-libbpf-lane-marker.py` `7be88fe75bda8cc9d71eba627cb3309d8d6a0ccf`",
        "- survey-backed anchor: `zigux/tests/phase12_virtio_scsi_manifest.json`",
        "- survey-build replay: `zigux/tests/phase12_virtio_scsi_survey_build.zig`",
        "- survey note: `Documentation/zigux/phase12-virtio-scsi-survey.md`",
        "- survey replay: `zigux/tests/phase12_virtio_scsi_survey.zig`",
        "- survey gate: `scripts/zigux/check-phase12-virtio-scsi-packet.py`",
        "current `master` no longer serves `drivers/scsi/virtio_scsi.zig`",
        "- exact current shared support-bundle and replay order is `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, then `make -C zigux phase12`",
        "- `make -C zigux phase12-validate` is current repo evidence again and now reruns the shared build-only, build-inventory, complex-driver, cross-compile smoke, release-readiness, libbpf snapshot, libbpf lane-marker, and libbpf heavy-consumer checkers plus `scripts/zigux/validate-phase12.py`",
        "archival commit-pinned history only",
        "while the current-master survey note, fixture manifest, survey manifest, survey replay, survey-build replay, survey gate, validator, shared build route, and `zigux/Makefile` are rollback evidence only",
    ],
    SURVEY_GATE_PATH: [
        "\"phase12-virtio-scsi-driver-starter\"",
        "\"missing_on_master\"",
        "\"rollback_evidence_present\"",
        "pathExists(\"drivers/scsi/virtio_scsi.zig\")",
        "\"phase12 virtio scsi survey note stays aligned with rollback evidence\"",
        "\"phase12 virtio scsi survey gate keeps present files present and missing files absent\"",
    ],
    SURVEY_BUILD_PATH: [
        "b.path(\"phase12_virtio_scsi_survey.zig\")",
        "\"phase12-virtio-scsi-survey-tests\"",
        "\"Run the Phase 12 virtio_scsi rollback-only survey tests\"",
    ],
    PHASE12_BUILD_PATH: [
        "\"../../drivers/net/virtio_net_queue_resume.zig\"",
        "\"phase12_virtio_net_queue_resume.zig\"",
        "\"phase12_virtio_net_receive_refill_replay.zig\"",
        "\"phase12_virtio_net_transmit_recycle.zig\"",
        "\"phase12_virtio_net_post_reset_replay.zig\"",
        "\"phase12_virtio_net_throughput_parity.zig\"",
        "\"phase12_virtio_net_survey.zig\"",
        "\"../../drivers/nvme/host/pci.zig\"",
        "\"phase12_nvme_pci.zig\"",
        "\"phase12-nvme-pci-direct-tests\"",
        "\"Run the Phase 12 virtio_net replay packet together with the bounded NVMe direct replay smoke tests\"",
        "\"Run the Phase 12 virtio_net replay packet together with the bounded NVMe direct replay tests\"",
        "\"phase12-virtio-net-throughput-parity\"",
    ],
    MAKEFILE_PATH: [
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
}

FORBIDDEN_MARKERS = [
    "PHASE12_STATUS=starter-present-queue-submit-completion-and-recovery-survey",
    "current `master` now carries `zigux/tests/phase12_virtio_scsi.zig` as the direct bounded replay",
    "`make -C zigux phase12-validate` stays reminder-only validator wrapper vocabulary until that wrapper returns on current `master`",
]

EXPECTED_ABSENT = [
    "drivers/scsi/virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi.zig",
    "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
]

EXPECTED_REQUIRED_PATHS = [
    "Documentation/zigux/phase12-virtio-scsi-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "zigux/tests/fixtures/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
    "scripts/zigux/check-phase12-virtio-scsi-packet.py",
    "zigux/tests/phase12_virtio_scsi_survey_build.zig",
    "zigux/tests/phase12_build.zig",
    "zigux/Makefile",
]

EXPECTED_SUMMARY_FLAGS = {
    "preexisting_virtio_scsi_zig_present": False,
    "preexisting_phase12_direct_test_present": False,
    "preexisting_phase12_syntax_lab_present": False,
    "preexisting_phase12_repeated_replan_gate_present": False,
    "preexisting_phase12_repeated_rollback_gate_present": False,
    "preexisting_phase12_support_packet_present": False,
    "preexisting_phase12_support_manifest_present": True,
    "preexisting_phase12_packet_checker_present": True,
    "preexisting_phase12_slice_note_present": True,
    "preexisting_phase12_build_present": True,
    "preexisting_phase12_make_targets_present": True,
    "preexisting_phase12_survey_note_present": True,
    "preexisting_phase12_fallback_catalog_present": True,
    "preexisting_phase12_survey_gate_present": True,
    "preexisting_phase12_survey_build_present": True,
}

EXPECTED_ROADMAP_GAP_STATUSES = {
    "dma_safe_abstractions": "rollback_evidence_only_live_starter_missing",
    "queueing_correctness": "rollback_evidence_present_no_live_queue_planner",
    "throughput_and_recovery_parity": "rollback_evidence_present_no_runtime_recovery_replay",
    "segmented_rollout": "survey_packet_and_fallback_present_driver_local_replay_missing",
}

EXPECTED_GAP_STATUSES = {
    "phase12-virtio-scsi-driver-starter": "missing_on_master",
    "phase12-virtio-scsi-direct-replay": "missing_on_master",
    "phase12-virtio-scsi-syntax-lab": "missing_on_master",
    "phase12-virtio-scsi-repeated-replan-gate": "missing_on_master",
    "phase12-virtio-scsi-repeated-rollback-gate": "missing_on_master",
    "phase12-build-gate": "shared_support_bundle_present",
    "phase12-make-target": "shared_make_targets_present",
    "phase12-virtio-scsi-survey-build-route": "rollback_evidence_present",
    "phase12-virtio-scsi-survey-gate": "rollback_evidence_present",
    "phase12-virtio-scsi-survey-note": "rollback_evidence_present",
    "phase12-virtio-scsi-runtime-request-flow": "blocked_on_driver_return_dma_scsi_host_runtime",
}


def repo_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_markers(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing marker in {rel_path}: {marker}")


def forbid_markers(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden stale marker in {rel_path}: {marker}")


def run_companion_checker(root: Path, rel_path: str) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(root / rel_path), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []

    combined = []
    if result.stdout.strip():
        combined.extend(line for line in result.stdout.splitlines() if line.strip())
    if result.stderr.strip():
        combined.extend(line for line in result.stderr.splitlines() if line.strip())
    return [f"companion checker failed: {rel_path}"] + combined


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    for rel_path in REQUIRED_FILES:
        full_path = root / rel_path
        if not full_path.is_file():
            errors.append(f"missing file: {rel_path}")

    if errors:
        return errors

    for rel_path, markers in TEXT_MARKERS.items():
        text = read_text(root / rel_path)
        require_markers(errors, rel_path, text, markers)
        forbid_markers(errors, rel_path, text, FORBIDDEN_MARKERS)

    manifest = json.loads(read_text(root / SURVEY_MANIFEST_PATH))
    if manifest.get("lane_key") != "P12-L09":
        errors.append("survey manifest lane_key drift")
    if manifest.get("verified_on") != "2026-05-24":
        errors.append("survey manifest verified_on drift")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        errors.append("survey manifest missing survey_summary")
    else:
        for key, expected in EXPECTED_SUMMARY_FLAGS.items():
            if summary.get(key) != expected:
                errors.append(f"survey manifest summary drift for {key}")

    roadmap_gap_check = manifest.get("roadmap_gap_check")
    if not isinstance(roadmap_gap_check, dict):
        errors.append("survey manifest missing roadmap_gap_check")
    else:
        for key, expected_status in EXPECTED_ROADMAP_GAP_STATUSES.items():
            entry = roadmap_gap_check.get(key)
            if not isinstance(entry, dict) or entry.get("status") != expected_status:
                errors.append(f"survey manifest roadmap gap drift for {key}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        errors.append("survey manifest gaps missing")
    else:
        by_id = {
            gap.get("id"): gap
            for gap in gaps
            if isinstance(gap, dict) and isinstance(gap.get("id"), str)
        }
        for gap_id, expected_status in EXPECTED_GAP_STATUSES.items():
            gap = by_id.get(gap_id)
            if gap is None:
                errors.append(f"survey manifest missing gap: {gap_id}")
                continue
            if gap.get("status") != expected_status:
                errors.append(f"survey manifest gap status drift for {gap_id}")
            if gap_id == "phase12-build-gate" and "survey-gate tests" not in str(gap.get("why_now", "")):
                errors.append("survey manifest phase12-build-gate why_now drift")
            if gap_id == "phase12-virtio-scsi-survey-build-route" and gap.get("zigux_destination") != "zigux/tests/phase12_virtio_scsi_survey_build.zig":
                errors.append("survey manifest survey-build destination drift")

    fixture = json.loads(read_text(root / FIXTURE_MANIFEST_PATH))
    if fixture.get("lane_key") != "P12-L09":
        errors.append("fixture manifest lane_key drift")
    if fixture.get("fixture_kind") != "rollback_evidence_presence_manifest":
        errors.append("fixture manifest kind drift")
    if fixture.get("verified_on") != "2026-05-24":
        errors.append("fixture manifest verified_on drift")

    required_paths = fixture.get("required_paths")
    if required_paths != EXPECTED_REQUIRED_PATHS:
        errors.append("fixture manifest required_paths drift")

    expected_absent = fixture.get("expected_absent_paths")
    if expected_absent != EXPECTED_ABSENT:
        errors.append("fixture manifest expected_absent_paths drift")

    if "driver-local starter and replay gates are absent" not in str(fixture.get("scope", "")):
        errors.append("fixture manifest scope drift")

    errors.extend(run_companion_checker(root, VALIDATOR_PACKET_CHECKER_PATH))
    return errors


def fixture_manifest() -> dict[str, object]:
    return {
        "lane_key": "P12-L09",
        "phase": "Phase 12",
        "surveyed_commit": "unresolved_on_master",
        "verified_on": "2026-05-24",
        "anchor": "drivers/scsi/virtio_scsi.c",
        "fixture_kind": "rollback_evidence_presence_manifest",
        "source_manifest": "zigux/tests/phase12_virtio_scsi_manifest.json",
        "scope": "driver-local starter and replay gates are absent while rollback evidence remains present",
        "required_paths": EXPECTED_REQUIRED_PATHS,
        "expected_absent_paths": EXPECTED_ABSENT,
        "notes": [
            "rollback evidence only",
            "survey-build replay remains present",
        ],
    }


def survey_manifest() -> dict[str, object]:
    return {
        "lane_key": "P12-L09",
        "phase": "Phase 12",
        "surveyed_commit": "unresolved_on_master",
        "verified_on": "2026-05-24",
        "anchor": "drivers/scsi/virtio_scsi.c",
        "roadmap_destinations": [
            "drivers/scsi/virtio_scsi.zig",
            "zigux/tests/phase12_virtio_scsi.zig",
        ],
        "survey_summary": EXPECTED_SUMMARY_FLAGS,
        "roadmap_gap_check": {
            "dma_safe_abstractions": {
                "required_by_roadmap": True,
                "status": EXPECTED_ROADMAP_GAP_STATUSES["dma_safe_abstractions"],
                "current_surface": "current master no longer serves a driver-local starter",
                "blocked_by": "starter absent on current master",
            },
            "queueing_correctness": {
                "required_by_roadmap": True,
                "status": EXPECTED_ROADMAP_GAP_STATUSES["queueing_correctness"],
                "current_surface": "support-bundle evidence only",
                "blocked_by": "no live queue planner",
            },
            "throughput_and_recovery_parity": {
                "required_by_roadmap": True,
                "status": EXPECTED_ROADMAP_GAP_STATUSES["throughput_and_recovery_parity"],
                "current_surface": "archival and survey evidence",
                "blocked_by": "no runtime recovery replay",
            },
            "segmented_rollout": {
                "required_by_roadmap": True,
                "status": EXPECTED_ROADMAP_GAP_STATUSES["segmented_rollout"],
                "current_surface": "survey packet and fallback present",
                "blocked_by": "repeated rollback gate still absent",
            },
        },
        "gaps": [
            {
                "id": "phase12-virtio-scsi-driver-starter",
                "status": EXPECTED_GAP_STATUSES["phase12-virtio-scsi-driver-starter"],
                "kind": "driver",
                "zigux_destination": "drivers/scsi/virtio_scsi.zig",
                "why_now": "current master no longer serves the direct starter",
            },
            {
                "id": "phase12-virtio-scsi-direct-replay",
                "status": EXPECTED_GAP_STATUSES["phase12-virtio-scsi-direct-replay"],
                "kind": "test",
                "zigux_destination": "zigux/tests/phase12_virtio_scsi.zig",
                "why_now": "direct replay remains absent on current master",
            },
            {
                "id": "phase12-virtio-scsi-syntax-lab",
                "status": EXPECTED_GAP_STATUSES["phase12-virtio-scsi-syntax-lab"],
                "kind": "test",
                "zigux_destination": "zigux/tests/phase12_virtio_scsi_syntax_lab.zig",
                "why_now": "syntax lab has not returned on current master",
            },
            {
                "id": "phase12-virtio-scsi-repeated-replan-gate",
                "status": EXPECTED_GAP_STATUSES["phase12-virtio-scsi-repeated-replan-gate"],
                "kind": "test",
                "zigux_destination": "zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig",
                "why_now": "replan gate remains absent",
            },
            {
                "id": "phase12-virtio-scsi-repeated-rollback-gate",
                "status": EXPECTED_GAP_STATUSES["phase12-virtio-scsi-repeated-rollback-gate"],
                "kind": "test",
                "zigux_destination": "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
                "why_now": "repeated rollback gate remains absent",
            },
            {
                "id": "phase12-build-gate",
                "status": EXPECTED_GAP_STATUSES["phase12-build-gate"],
                "kind": "support",
                "zigux_destination": "zigux/tests/phase12_build.zig",
                "why_now": "shared support bundle keeps survey-gate tests reviewable",
            },
            {
                "id": "phase12-make-target",
                "status": EXPECTED_GAP_STATUSES["phase12-make-target"],
                "kind": "support",
                "zigux_destination": "zigux/Makefile",
                "why_now": "shared make targets remain present",
            },
            {
                "id": "phase12-virtio-scsi-survey-build-route",
                "status": EXPECTED_GAP_STATUSES["phase12-virtio-scsi-survey-build-route"],
                "kind": "build",
                "zigux_destination": "zigux/tests/phase12_virtio_scsi_survey_build.zig",
                "why_now": "dedicated survey-build replay remains present",
            },
            {
                "id": "phase12-virtio-scsi-survey-gate",
                "status": EXPECTED_GAP_STATUSES["phase12-virtio-scsi-survey-gate"],
                "kind": "test",
                "zigux_destination": "zigux/tests/phase12_virtio_scsi_survey.zig",
                "why_now": "survey gate still fails closed on packet drift",
            },
            {
                "id": "phase12-virtio-scsi-survey-note",
                "status": EXPECTED_GAP_STATUSES["phase12-virtio-scsi-survey-note"],
                "kind": "docs",
                "zigux_destination": "Documentation/zigux/phase12-virtio-scsi-survey.md",
                "why_now": "survey note keeps rollback evidence aligned",
            },
            {
                "id": "phase12-virtio-scsi-runtime-request-flow",
                "status": EXPECTED_GAP_STATUSES["phase12-virtio-scsi-runtime-request-flow"],
                "kind": "driver",
                "zigux_destination": "drivers/scsi/virtio_scsi.zig",
                "why_now": "runtime request flow still needs returned dma-safe scsi host surfaces",
            },
        ],
    }


def fixture_text(title: str, markers: list[str]) -> str:
    lines = [title, ""]
    lines.extend(f"- {marker}" for marker in markers)
    lines.append("")
    return "\n".join(lines)


def write_fixture_root(root: Path) -> None:
    write_text(root / SLICE_PATH, fixture_text("# Phase 12 virtio_scsi Slice", TEXT_MARKERS[SLICE_PATH]))
    write_text(root / SURVEY_NOTE_PATH, fixture_text("# Phase 12 virtio_scsi Survey", TEXT_MARKERS[SURVEY_NOTE_PATH]))
    write_text(root / FALLBACK_CATALOG_PATH, fixture_text("# Phase 12 virtio_scsi Raw GitHub Fallback Catalog", TEXT_MARKERS[FALLBACK_CATALOG_PATH]))
    write_text(root / SURVEY_GATE_PATH, "\n".join(TEXT_MARKERS[SURVEY_GATE_PATH]) + "\n")
    write_text(root / SURVEY_BUILD_PATH, "\n".join(TEXT_MARKERS[SURVEY_BUILD_PATH]) + "\n")
    write_text(root / PHASE12_BUILD_PATH, "\n".join(TEXT_MARKERS[PHASE12_BUILD_PATH]) + "\n")
    write_text(root / MAKEFILE_PATH, "\n".join(TEXT_MARKERS[MAKEFILE_PATH]) + "\n")
    write_text(
        root / VALIDATOR_PACKET_CHECKER_PATH,
        "#!/usr/bin/env python3\nfrom __future__ import annotations\nimport argparse\nfrom pathlib import Path\nparser = argparse.ArgumentParser()\nparser.add_argument('--root')\nargs = parser.parse_args()\nif (Path(args.root) / 'validator_should_fail').exists():\n    raise SystemExit(1)\nraise SystemExit(0)\n",
    )
    write_text(root / FIXTURE_MANIFEST_PATH, json.dumps(fixture_manifest(), indent=2) + "\n")
    write_text(root / SURVEY_MANIFEST_PATH, json.dumps(survey_manifest(), indent=2) + "\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    errors = validate(root)
    if not any(expected_fragment in error for error in errors):
        raise SystemExit(f"expected failure containing {expected_fragment!r}, got {errors!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-virtio-scsi-packet-"))
    try:
        write_fixture_root(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture should pass: {failures!r}")

        write_fixture_root(base)
        (base / SURVEY_NOTE_PATH).unlink()
        expect_failure(base, f"missing file: {SURVEY_NOTE_PATH}")

        write_fixture_root(base)
        write_text(base / SURVEY_NOTE_PATH, "# broken\n")
        expect_failure(base, f"missing marker in {SURVEY_NOTE_PATH}")

        write_fixture_root(base)
        write_text(base / MAKEFILE_PATH, "phase12-smoke:\n")
        expect_failure(base, f"missing marker in {MAKEFILE_PATH}")

        write_fixture_root(base)
        broken = survey_manifest()
        broken["lane_key"] = "P12-LXX"
        write_text(base / SURVEY_MANIFEST_PATH, json.dumps(broken, indent=2) + "\n")
        expect_failure(base, "survey manifest lane_key drift")

        write_fixture_root(base)
        broken_fixture = fixture_manifest()
        broken_fixture["required_paths"] = []
        write_text(base / FIXTURE_MANIFEST_PATH, json.dumps(broken_fixture, indent=2) + "\n")
        expect_failure(base, "fixture manifest required_paths drift")

        write_fixture_root(base)
        (base / "validator_should_fail").write_text("fail\n", encoding="utf-8")
        expect_failure(base, "companion checker failed")

        write_fixture_root(base)
        write_text(base / FALLBACK_CATALOG_PATH, "# broken\n")
        expect_failure(base, f"missing marker in {FALLBACK_CATALOG_PATH}")

        print(f"{SELF_TEST_MARKER}=pass")
        print(f"{SELF_TEST_MARKER}_CASE_COUNT=8")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=repo_root(), help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run fixture-backed checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.root)
    errors = validate(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("phase12 virtio_scsi rollback-evidence packet validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
