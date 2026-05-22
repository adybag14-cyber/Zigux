#!/usr/bin/env python3
"""Guard the current Phase 10 closure ledger packet in zigux-alpha/."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

LEDGER_REL = Path("zigux-alpha/PHASE10_CLOSURE_LEDGER.md")

REQUIRED_LINES = [
    "# Phase 10 Closure Ledger",
    "This focused ledger records the current closure-evidence bundle for the active Phase 10 virtio tranche.",
    "- `PHASE10_LEDGER_STATUS=active`",
    "- `PHASE10_LEDGER_TRANCHE=virtio-lab-bundle`",
    "- `PHASE10_LEDGER_SCOPE=virtio-core,virtio-ring,virtio-input,virtio-mmio-lab-bundle`",
    "- `PHASE10_LEDGER_ROADMAP_ANCHORS=drivers/virtio/virtio.c,drivers/virtio/virtio_ring.c,drivers/virtio/virtio_input.c,drivers/virtio/virtio_mmio.c`",
    "- `PHASE10_LEDGER_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md`",
    "- `PHASE10_LEDGER_CORE_PACKET_VALIDATE=repo_reality_gap:scripts/zigux/check-phase10-core-packet.py`",
    "- `PHASE10_LEDGER_TESTS_README_CORE_VALIDATE=scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "- `PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py`",
    "- `PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py`",
    "- `PHASE10_LEDGER_SHARED_VALIDATE=scripts/zigux/validate-phase10.py`",
    "- `PHASE10_LEDGER_MANIFEST=zigux/tests/phase10_closure_manifest.json`",
    "- `PHASE10_LEDGER_CORE_SLICE=Documentation/zigux/phase10-virtio-core-slice.md`",
    "- `PHASE10_LEDGER_CORE_SURVEY=Documentation/zigux/phase10-virtio-core-survey.md`",
    "- `PHASE10_LEDGER_RING_SURVEY=Documentation/zigux/phase10-virtio-ring-survey.md`",
    "- `PHASE10_LEDGER_INPUT_SURVEY=Documentation/zigux/phase10-virtio-input-survey.md`",
    "- `PHASE10_LEDGER_MMIO_SURVEY=Documentation/zigux/phase10-virtio-mmio-survey.md`",
    "- `PHASE10_LEDGER_REPO_REALITY_GAPS=scripts/zigux/check-phase10-core-packet.py`",
    "- `PHASE10_LEDGER_CONTENTS_BRIDGE_GAPS=none`",
    "- `PHASE10_LEDGER_PUBLIC_FALLBACK_CONFIRMED_RING_SURFACES=drivers/virtio/virtio_ring.zig,drivers/virtio/virtio_ring_verify.zig,zigux/tests/phase10_virtio_ring.zig,zigux/tests/phase10_virtio_ring_reset_reuse.zig,zigux/tests/phase10_virtio_ring_survey.zig,scripts/zigux/check-phase10-ring-packet.py`",
    "- `PHASE10_LEDGER_MMIO_CONTENTS_BRIDGE_GAPS=none`",
    "- `PHASE10_LEDGER_CORE_LAB_GATE=zigux/tests/phase10_virtio_core.zig`",
    "- `PHASE10_LEDGER_CORE_RESET_QUEUE_REPLAY=zigux/tests/phase10_virtio_core_reset_queue.zig`",
    "- `PHASE10_LEDGER_CORE_SURVEY_GATE=zigux/tests/phase10_virtio_core_survey.zig`",
    "- `PHASE10_LEDGER_DRIVER_ID_REPLAY=zigux/tests/phase10_virtio_driver_id.zig`",
    "- `PHASE10_LEDGER_RING_SURVEY_GATE=zigux/tests/phase10_virtio_ring_survey.zig`",
    "- `PHASE10_LEDGER_INPUT_QUEUE_CALLBACK_PREFLIGHT_REPLAY=zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`",
    "- `PHASE10_LEDGER_INPUT_STATUS_DRAIN_REPLAY=zigux/tests/phase10_virtio_input_status_drain.zig`",
    "- `PHASE10_LEDGER_INPUT_PROBE_PREFLIGHT_REPLAY=zigux/tests/phase10_virtio_input_probe_preflight.zig`",
    "- `PHASE10_LEDGER_INPUT_REGISTRATION_PREFLIGHT_REPLAY=zigux/tests/phase10_virtio_input_registration_preflight.zig`",
    "- `PHASE10_LEDGER_INPUT_TEARDOWN_OBSERVATION_REPLAY=zigux/tests/phase10_virtio_input_teardown_observation.zig`",
    "- `PHASE10_LEDGER_INPUT_SURVEY_GATE=zigux/tests/phase10_virtio_input_survey.zig`",
    "- `PHASE10_LEDGER_MMIO_SURVEY_GATE=zigux/tests/phase10_virtio_mmio_survey.zig`",
    "- `PHASE10_LEDGER_CORE_MANIFEST=zigux/tests/phase10_virtio_core_manifest.json`",
    "- `PHASE10_LEDGER_RING_MANIFEST=zigux/tests/phase10_virtio_ring_manifest.json`",
    "- `PHASE10_LEDGER_INPUT_MANIFEST=zigux/tests/phase10_virtio_input_manifest.json`",
    "- `PHASE10_LEDGER_MMIO_MANIFEST=zigux/tests/phase10_virtio_mmio_manifest.json`",
    "- `PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE=zigux/tests/phase10_closure_manifest.json`",
    "- `PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived`",
    "- `PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01`",
    "- `PHASE10_LEDGER_SURVEY_RING_LANE=P10-L10`",
    "- `PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L22`",
    "- `PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11`",
    "- `PHASE10_LEDGER_SURVEY_CORE_COMMIT=c11221dc7a68d7511ae1c69d64b3f08528287ed8`",
    "- `PHASE10_LEDGER_SURVEY_RING_COMMIT=0aa2db32bcb1c7065850ee3f66ec119b071fbf5c`",
    "- `PHASE10_LEDGER_SURVEY_INPUT_COMMIT=ee789f026f11a0c5c70ded9a868979cdf4f55393`",
    "- `PHASE10_LEDGER_SURVEY_MMIO_COMMIT=b53ec2bd507d0b3283486e76acc273b184ad5bf8`",
    "- `PHASE10_LEDGER_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed`",
    "- `PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE=zigux/tests/phase10_virtio_ring_manifest.json,Documentation/zigux/phase10-virtio-ring-survey.md,Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "- `PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS=starter_landed`",
    "- `PHASE10_LEDGER_MMIO_WRAPPERS=starter_landed`",
    "- `PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE=drivers/virtio/virtio_mmio.zig,zigux/tests/phase10_virtio_mmio.zig,drivers/virtio/virtio_mmio_verify.zig,zigux/tests/phase10_virtio_mmio_manifest.json,Documentation/zigux/phase10-virtio-mmio-survey.md`",
    "- `PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed`",
    "- `PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE=Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md,zigux/tests/phase10_build.zig,zigux/tests/phase10_virtio_ring_reset_reuse.zig,drivers/virtio/virtio_ring_verify.zig,drivers/virtio/virtio_input_verify.zig,zigux/tests/phase10_virtio_input.zig,zigux/tests/phase10_virtio_input_probe_preflight.zig,zigux/tests/phase10_virtio_input_registration_preflight.zig,zigux/tests/phase10_virtio_input_teardown_observation.zig,zigux/tests/phase10_virtio_input_queue_callback_preflight.zig,zigux/tests/phase10_virtio_input_status_drain.zig,zigux/tests/phase10_virtio_input_survey.zig,drivers/virtio/virtio_mmio_verify.zig,zigux/tests/phase10_virtio_mmio.zig,zigux/tests/phase10_virtio_mmio_survey.zig,scripts/zigux/check-phase10-bootstrap-route.py,scripts/zigux/check-phase10-shared-freeze-boundary.py,scripts/zigux/check-phase10-ring-packet.py,scripts/zigux/check-phase10-input-packet.py,scripts/zigux/check-phase10-mmio-packet.py,scripts/zigux/check-phase10-harness-coverage.py,scripts/zigux/check-phase10-tests-readme-core-surfaces.py,scripts/zigux/validate-phase10.py,scripts/zigux/validate-phase10-closure.py,zigux/Makefile,.github/workflows/zigux-bootstrap.yml`",
    "- `PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport`",
    "- `PHASE10_LEDGER_SCOREBOARD_DUAL_IMPLEMENTATIONS_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md,zigux/tests/phase10_virtio_core_manifest.json,zigux/tests/phase10_virtio_ring_manifest.json,zigux/tests/phase10_virtio_input_manifest.json,zigux/tests/phase10_virtio_mmio_manifest.json`",
    "- `PHASE10_LEDGER_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/kernel/,zigux/helpers/`",
    "- `PHASE10_LEDGER_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates`",
    "- `PHASE10_LEDGER_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes`",
    "- `PHASE10_LEDGER_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no`",
    "- `PHASE10_LEDGER_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,queue_reset_execution,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle,freeze_restore_lifecycle`",
    "- `PHASE10_LEDGER_PHASE14_STUDY_ONLY_ANCHORS=kernel/workqueue.c,kernel/trace/ring_buffer.c`",
    "- `PHASE10_LEDGER_MAKEFILE=zigux/Makefile`",
    "- `PHASE10_LEDGER_WORKFLOW=.github/workflows/zigux-bootstrap.yml`",
    "- `PHASE10_LEDGER_ENTRYPOINTS=make -C zigux phase10-validate,make -C zigux phase10-test,make -C zigux phase10`",
    "- `PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/check-phase10-bootstrap-route.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_2=python3 scripts/zigux/check-phase10-shared-freeze-boundary.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_3=python3 scripts/zigux/check-phase10-ring-packet.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_4=python3 scripts/zigux/check-phase10-input-packet.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_5=python3 scripts/zigux/check-phase10-mmio-packet.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_6=python3 scripts/zigux/check-phase10-harness-coverage.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_7=python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/validate-phase10.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_9=python3 scripts/zigux/validate-phase10-closure.py`",
    "- `PHASE10_LEDGER_EXACT_CHECK_10=make -C zigux phase10-validate`",
    "- `PHASE10_LEDGER_EXACT_CHECK_11=zig build test --build-file zigux/tests/phase10_build.zig --summary all`",
    "- `PHASE10_LEDGER_EXACT_CHECK_12=make -C zigux phase10-test`",
    "- `PHASE10_LEDGER_EXACT_CHECK_13=make -C zigux phase10`",
    "- `PHASE10_LEDGER_NEXT_STEP=leave_parked_unless_shared_phase10_surfaces_drift_again_around_the_manifest_backed_packet_and_reopen_P10-L06_only_if_a_fresh_shared_reminder_reread_proves_new_drift`",
    "- `PHASE10_LEDGER_BLOCKERS=phase10-core-probe-remove-lifecycle,phase10-virtio-input-registration-lifecycle,phase10-mmio-lifecycle-and-irq-paths`",
    "- `PHASE10_LEDGER_LANDED_CORE_HELPERS=phase10-queue-shape-bookkeeping-helper,phase10-config-generation-bookkeeping-helper,phase10-interrupt-ack-bookkeeping-helper,phase10-lifecycle-guard-bookkeeping-helper,phase10-driver-validation-narrowing-helper,phase10-core-attribute-summary-helper,phase10-reset-replay-bookkeeping-helper`",
    "- `PHASE10_LEDGER_LANDED_RING_HELPERS=phase10-virtqueue-shape-helper,phase10-used-buffer-polling-helper,phase10-callback-enable-helper,phase10-callback-delay-helper,phase10-notify-prepare-helper,phase10-notification-data-summary-helper,phase10-broken-queue-poll-guard,phase10-queue-publish-readiness-helper,phase10-queue-reset-helper,phase10-queue-reset-readiness-helper,phase10-ring-verify-replay,phase10-virtio-ring-slice-note`",
    "- `PHASE10_LEDGER_LANDED_INPUT_HELPERS=phase10-virtio-input-capability-setup-helper,phase10-virtio-input-multitouch-slot-helper,phase10-virtio-input-probe-preflight-helper,phase10-virtio-input-teardown-observation-helper,phase10-virtio-input-registration-preflight-helper,phase10-virtio-input-queue-callback-preflight-helper,phase10-virtio-input-status-drain-helper`",
    "- `PHASE10_LEDGER_LANDED_MMIO_HELPERS=phase10-virtio-mmio-lab-helper,phase10-mmio-transport-identity-helper,phase10-mmio-probe-preflight-helper,phase10-mmio-selected-queue-readiness-helper,phase10-mmio-interrupt-ack-disposition-helper,phase10-mmio-feature-negotiation-summary-helper,phase10-mmio-config-write-plan-freshness-helper,phase10-mmio-config-write-disposition-helper`",
    "This ledger stays intentionally narrow.",
]

REQUIRED_PARAGRAPHS = [
    "It records the roadmap-backed closure packet and the current parked-next-step posture without claiming queue setup, reset, IRQ parity, DMA, probe or remove lifecycle, or input registration lifecycle parity. The roadmap-facing scoreboard is mirrored here from the shared closure manifest so the closure packet can be compared directly against the Phase 10 roadmap requirements without hopping between survey notes.",
    "That shared scoreboard still reads `starter_landed` for virtqueue wrappers, MMIO wrappers, and lab-only validation, while risky dual implementations remain `blocked_on_risky_transport` until a smaller transport-facing helper lane is ready. The narrower current-head repo-reality gap inside this ledger is the still-missing `scripts/zigux/check-phase10-core-packet.py` marker, so keep the core packet governed through the returned closure manifest, the returned `zigux/tests/phase10_virtio_core.zig` replay, the direct core survey note, and the shared tests-root core-surface guard rather than promoting a missing dedicated core checker back into current-head evidence.",
    "The same manifest also carries the survey-provenance packet for the current closure bundle, so this ledger now publishes the exact lane ownership and inspected heads behind the live core, ring, input, and MMIO survey notes: ring ownership is now `P10-L10`, input ownership is now `P10-L22` with the current manifest-backed `ee789f026f11a0c5c70ded9a868979cdf4f55393`, and MMIO ownership remains `P10-L11` with the current manifest-backed `b53ec2bd507d0b3283486e76acc273b184ad5bf8`.",
    "Fresh public GitHub fallback rereads now materialize the previously stale ring and MMIO packet surfaces on current `master`, including `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `scripts/zigux/check-phase10-ring-packet.py`, `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_build.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig`. Because the packet-local slice-note set is also directly readable again, this ledger no longer carries the older repo-reality-gap or contents-bridge-gap wording for those surfaces.",
    "The current exact replay packet is the manifest-backed shared closure route: `check-phase10-bootstrap-route.py`, `check-phase10-shared-freeze-boundary.py`, `check-phase10-ring-packet.py`, `check-phase10-input-packet.py`, `check-phase10-mmio-packet.py`, `check-phase10-harness-coverage.py`, `check-phase10-tests-readme-core-surfaces.py`, `validate-phase10.py`, `validate-phase10-closure.py`, `make -C zigux phase10-validate`, `zig build test --build-file zigux/tests/phase10_build.zig --summary all`, `make -C zigux phase10-test`, and `make -C zigux phase10`.",
    "The shared closure manifest-backed helper ladders stay explicit here for all four bounded Phase 10 lanes, so reviewers can recover the current core, ring, input, and MMIO starter packet directly from this tranche record instead of stopping at older shorthand.",
]

REQUIRED_EXACT_CHECK_LINES = [
    line for line in REQUIRED_LINES if "PHASE10_LEDGER_EXACT_CHECK_" in line
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    if not (root / LEDGER_REL).is_file():
        return [str(LEDGER_REL)]
    return []


def collect_issues(root: Path) -> list[str]:
    text = read_text(root, LEDGER_REL)
    issues: list[str] = []

    for line in REQUIRED_LINES:
        if line not in text:
            issues.append(f"missing_line:{line}")

    for paragraph in REQUIRED_PARAGRAPHS:
        if paragraph not in text:
            issues.append(f"missing_paragraph:{paragraph}")

    if text.count("PHASE10_LEDGER_EXACT_CHECK_") != len(REQUIRED_EXACT_CHECK_LINES):
        issues.append("unexpected_exact_check_count")

    next_step_idx = text.find("PHASE10_LEDGER_NEXT_STEP=")
    blockers_idx = text.find("PHASE10_LEDGER_BLOCKERS=")
    landed_core_idx = text.find("PHASE10_LEDGER_LANDED_CORE_HELPERS=")
    narrow_idx = text.find("This ledger stays intentionally narrow.")
    first_paragraph_idx = text.find(REQUIRED_PARAGRAPHS[0])
    last_paragraph_idx = text.find(REQUIRED_PARAGRAPHS[-1])
    if (
        next_step_idx == -1
        or blockers_idx == -1
        or landed_core_idx == -1
        or narrow_idx == -1
        or first_paragraph_idx == -1
        or last_paragraph_idx == -1
        or not (next_step_idx < blockers_idx < landed_core_idx < narrow_idx < first_paragraph_idx < last_paragraph_idx)
    ):
        issues.append("reordered_closure_ledger_packets")

    return issues


def make_fixture_text() -> str:
    return "\n".join(
        [
            REQUIRED_LINES[0],
            "",
            REQUIRED_LINES[1],
            "",
            *REQUIRED_LINES[2:],
            "",
            *[
                chunk
                for paragraph in REQUIRED_PARAGRAPHS
                for chunk in (paragraph, "")
            ],
        ]
    ).rstrip() + "\n"


def make_fixture_root(root: Path) -> None:
    write_text(root, LEDGER_REL, make_fixture_text())


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane01_phase10_ledger_") as tmp:
        root = Path(tmp)
        make_fixture_root(root)

        assert collect_missing_files(root) == []
        assert collect_issues(root) == []
        case_count += 1

        (root / LEDGER_REL).unlink()
        assert str(LEDGER_REL) in collect_missing_files(root)
        case_count += 1
        make_fixture_root(root)

        ledger_path = root / LEDGER_REL
        text = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(text.replace(REQUIRED_LINES[5] + "\n", "", 1), encoding="utf-8")
        assert any(issue.startswith("missing_line:") for issue in collect_issues(root))
        case_count += 1
        make_fixture_root(root)

        text = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(text.replace(REQUIRED_EXACT_CHECK_LINES[-1] + "\n", "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert any(issue.startswith("missing_line:") for issue in issues)
        assert "unexpected_exact_check_count" in issues
        case_count += 1
        make_fixture_root(root)

        text = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(text.replace(REQUIRED_PARAGRAPHS[3], "drifted paragraph", 1), encoding="utf-8")
        assert any(issue.startswith("missing_paragraph:") for issue in collect_issues(root))
        case_count += 1
        make_fixture_root(root)

        text = ledger_path.read_text(encoding="utf-8")
        reordered = text.replace(
            REQUIRED_LINES[79] + "\n" + REQUIRED_LINES[80],
            REQUIRED_LINES[80] + "\n" + REQUIRED_LINES[79],
            1,
        )
        ledger_path.write_text(reordered, encoding="utf-8")
        assert "reordered_closure_ledger_packets" in collect_issues(root)
        case_count += 1
        make_fixture_root(root)

        text = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(text.replace(REQUIRED_LINES[-1], "drifted helper packet", 1), encoding="utf-8")
        assert any(issue.startswith("missing_line:") for issue in collect_issues(root))
        case_count += 1
        make_fixture_root(root)

        text = ledger_path.read_text(encoding="utf-8")
        ledger_path.write_text(text + REQUIRED_EXACT_CHECK_LINES[0] + "\n", encoding="utf-8")
        assert "unexpected_exact_check_count" in collect_issues(root)
        case_count += 1

    print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_SELF_TEST_CASES={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Lane 01 Phase 10 closure ledger packet.")
    parser.add_argument("--root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER=fail")
        print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_MISSING_FILES_START")
        for item in missing_files:
            print(item)
        print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_MISSING_FILES_END")
        return 1

    issues = collect_issues(root)
    if issues:
        print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER=fail")
        print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_ISSUES_START")
        for item in issues:
            print(item)
        print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_ISSUES_END")
        return 1

    print("LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER=pass")
    print(f"LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    print(f"LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_EXACT_CHECK_COUNT={len(REQUIRED_EXACT_CHECK_LINES)}")
    print(f"LANE01_BOOTSTRAP_PHASE10_CLOSURE_LEDGER_PARAGRAPH_COUNT={len(REQUIRED_PARAGRAPHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
