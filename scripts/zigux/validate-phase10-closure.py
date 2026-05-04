#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]

DOCS = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "Documentation/zigux/phase10-virtio-input-survey.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
]
MANIFESTS = [
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
]
DRIVERS = [
    "drivers/virtio/virtio.zig",
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_input.zig",
    "drivers/virtio/virtio_mmio.zig",
]
TESTS = [
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_survey.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
]
EXPECTED_EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase10-closure-inventory.py",
    "python3 scripts/zigux/check-phase10-core-packet.py",
    "python3 scripts/zigux/validate-phase10.py",
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "python3 scripts/zigux/validate-phase10-closure.py",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]
EXPECTED_ALLOWED_ROADMAP_DESTINATIONS = ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"]
EXPECTED_ALLOWED_EVIDENCE_KINDS = ["driver_local_lab_slices", "survey_manifests", "shared_validation_gates"]
EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS = [
    "queue_setup_reset_paths",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
]
EXPECTED_SURVEY_LANE_KEYS = {"core": "P10-L01", "ring": "P10-L07", "input": "P10-L13", "mmio": "P10-L18"}
EXPECTED_SURVEYED_COMMITS = {
    "core": "d30cbe483a2f019ae797b309a29556bd58fe00d0",
    "ring": "fe8a43ea2e186da0da152198b571dff57ea3c38c",
    "input": "f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21",
    "mmio": "0945df1cf664a3582d7241f859183a13f3f04adb",
}
EXPECTED_LANDED_INPUT_HELPERS = [
    "phase10-virtio-input-capability-setup-helper",
    "phase10-virtio-input-multitouch-slot-helper",
    "phase10-virtio-input-teardown-observation-helper",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-probe-preflight-helper",
]
EXPECTED_LANDED_MMIO_HELPERS = [
    "phase10-mmio-register-window-helper",
    "phase10-mmio-queue-register-helper",
    "phase10-mmio-queue-notify-helper",
    "phase10-mmio-queue-address-helper",
    "phase10-mmio-config-window-helper",
    "phase10-mmio-config-write-helper",
    "phase10-mmio-interrupt-ack-helper",
    "phase10-mmio-probe-preflight-helper",
]
EXPECTED_FOCUSED_HARNESS = {
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig": ["phase10 ring drained-reset reuse replay"],
    "zigux/tests/phase10_virtio_input_multitouch_preflight.zig": ["phase10 input multitouch-ready preflight replay"],
    "zigux/tests/phase10_virtio_mmio_queue_isolation.zig": [
        "phase10 mmio multi-queue isolation replay",
        "phase10 mmio reset clears legacy and modern queue address plans after queue selection changes",
    ],
}
REQUIRED_FILES = [
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-closure-inventory.py",
    "scripts/zigux/check-phase10-core-packet.py",
    "zigux/tests/README.md",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
    *DOCS,
    *MANIFESTS,
    *DRIVERS,
    *TESTS,
]
TEXT_MARKERS = {
    "Documentation/zigux/phase10-closure-evidence.md": [
        "PHASE10_STATUS=active",
        "PHASE10_TRANCHE=virtio-lab-bundle",
        "PHASE10_SURVEY_CORE_LANE=P10-L01",
        "PHASE10_SURVEY_RING_LANE=P10-L07",
        "PHASE10_SURVEY_INPUT_LANE=P10-L13",
        "PHASE10_SURVEY_MMIO_LANE=P10-L18",
        "phase10-mmio-interrupt-ack-helper",
        "phase10-mmio-probe-preflight-helper",
        "phase10-mmio-lifecycle-and-irq-paths",
        "zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
        "zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
        "PHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py",
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase10-closure-evidence.md",
        "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
        "python3 scripts/zigux/check-phase10-harness-coverage.py",
        "focused harness replays",
        "queue-handling and ready-state gate",
    ],
    "zigux/tests/README.md": [
        "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
        "scripts/zigux/check-phase10-core-packet.py",
        "four lane survey manifests plus the shared `zigux/tests/phase10_closure_manifest.json`",
    ],
    "Documentation/zigux/review-checklist.md": ["phase10-closure-evidence.md", "phase10_closure_manifest.json", "kernel/workqueue.c", "kernel/trace/ring_buffer.c"],
    "Documentation/zigux/freeze-map.md": ["kernel/sched/core.c", "mm/page_alloc.c", "kernel/rcu/tree.c", "net/core/skbuff.c", "kernel/workqueue.c", "kernel/trace/ring_buffer.c"],
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": [
        "PHASE10_LEDGER_STATUS=active",
        "PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py",
        "PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py",
        "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L13",
        "PHASE10_LEDGER_INPUT_MULTITOUCH_PREFLIGHT_GATE=zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
        "PHASE10_LEDGER_MMIO_QUEUE_ISOLATION_GATE=zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
        "PHASE10_LEDGER_LANDED_MMIO_HELPERS=phase10-mmio-register-window-helper,phase10-mmio-queue-register-helper,phase10-mmio-queue-notify-helper,phase10-mmio-queue-address-helper,phase10-mmio-config-window-helper,phase10-mmio-config-write-helper,phase10-mmio-interrupt-ack-helper,phase10-mmio-probe-preflight-helper",
    ],
    "zigux/Makefile": [
        "phase10-validate:",
        "scripts/zigux/check-phase10-closure-inventory.py",
        "scripts/zigux/check-phase10-core-packet.py",
        "scripts/zigux/validate-phase10.py",
        "scripts/zigux/check-phase10-harness-coverage.py --self-test",
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/validate-phase10-closure.py",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "Self-test Phase 10 harness coverage checker",
        "Validate Phase 10 focused harness coverage",
        "Validate Phase 10 closure evidence",
        "make -C zigux phase10-validate",
        "Run Phase 10 virtio helper tests",
    ],
    "zigux/tests/phase10_build.zig": [
        "phase10-virtio-core-survey-tests",
        "phase10-virtio-ring-reset-reuse-tests",
        "phase10-virtio-input-multitouch-preflight-tests",
        "phase10-virtio-mmio-queue-isolation-tests",
        "phase10-virtio-ring-survey-tests",
        "phase10-virtio-input-survey-tests",
        "phase10-virtio-mmio-survey-tests",
    ],
    "Documentation/zigux/phase10-virtio-core-survey.md": ["phase10-config-generation-summary-helper", "phase10-config-delivery-disposition-helper", "phase10-core-probe-remove-lifecycle"],
    "Documentation/zigux/phase10-virtio-ring-survey.md": ["phase10-broken-queue-recovery-helper", "phase10-mmio-interrupt-ack-helper", "phase10-mmio-lifecycle-and-irq-paths"],
    "Documentation/zigux/phase10-virtio-input-survey.md": ["phase10-virtio-input-registration-preflight-helper", "phase10-virtio-input-queue-callback-preflight-helper", "phase10-virtio-input-registration-lifecycle"],
    "Documentation/zigux/phase10-virtio-mmio-survey.md": ["phase10-mmio-config-write-helper", "phase10-mmio-interrupt-ack-helper", "phase10-mmio-probe-preflight-helper", "phase10-mmio-lifecycle-and-irq-paths"],
}
EXACT_ONCE = {
    "Documentation/zigux/phase10-closure-evidence.md": [
        "PHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py",
        "PHASE10_TEST_COUNT=11",
    ],
    "Documentation/zigux/README.md": ["python3 scripts/zigux/check-phase10-harness-coverage.py", "focused harness replays", "queue-handling and ready-state gate"],
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": [
        "PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py",
        "PHASE10_LEDGER_INPUT_MULTITOUCH_PREFLIGHT_GATE=zigux/tests/phase10_virtio_input_multitouch_preflight.zig",
        "PHASE10_LEDGER_MMIO_QUEUE_ISOLATION_GATE=zigux/tests/phase10_virtio_mmio_queue_isolation.zig",
        "PHASE10_LEDGER_EXACT_CHECK_4=python3 scripts/zigux/check-phase10-harness-coverage.py",
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def load_json(root: Path, rel_path: str) -> object:
    return json.loads(read_text(root, rel_path))


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing: list[str] = []
    for rel_path, markers in TEXT_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel_path}:{marker}")
        for marker in EXACT_ONCE.get(rel_path, []):
            count = text.count(marker)
            if count != 1:
                missing.append(f"{rel_path}:count:{marker}={count}")

    closure = load_json(root, "zigux/tests/phase10_closure_manifest.json")
    if not isinstance(closure, dict):
        missing.append("closure_manifest:type")
        return [], missing

    scalar_expectations = {
        "phase": "Phase 10",
        "status": "active",
        "tranche": "virtio-lab-bundle",
        "doc_count": 9,
        "manifest_count": 4,
        "driver_count": 4,
        "test_count": 11,
        "has_virtio_mmio_zig": True,
        "freeze_map": "Documentation/zigux/freeze-map.md",
        "freeze_boundary_status": "aligned",
        "freeze_status_change_claimed": False,
        "review_checklist": "Documentation/zigux/review-checklist.md",
        "risky_transport_posture": "blocked_on_risky_transport",
        "architecture_council_reopen_required": True,
        "architecture_council_reopen_attached": False,
    }
    for key, expected in scalar_expectations.items():
        if closure.get(key) != expected:
            missing.append(f"closure_manifest:{key}")

    array_expectations = {
        "manifests": MANIFESTS,
        "drivers": DRIVERS,
        "tests": TESTS,
        "allowed_roadmap_destinations": EXPECTED_ALLOWED_ROADMAP_DESTINATIONS,
        "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
        "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
        "exact_checks": EXPECTED_EXACT_CHECKS,
    }
    for key, expected in array_expectations.items():
        if closure.get(key) != expected:
            missing.append(f"closure_manifest:{key}")

    survey = closure.get("survey_provenance")
    if not isinstance(survey, dict):
        missing.append("closure_manifest:survey_provenance")
    else:
        if survey.get("source") != "manifest_derived":
            missing.append("closure_manifest:survey_provenance:source")
        if survey.get("lane_keys") != EXPECTED_SURVEY_LANE_KEYS:
            missing.append("closure_manifest:survey_provenance:lane_keys")
        if survey.get("surveyed_commits") != EXPECTED_SURVEYED_COMMITS:
            missing.append("closure_manifest:survey_provenance:surveyed_commits")

    roadmap = closure.get("roadmap_parity_scoreboard")
    if not isinstance(roadmap, dict):
        missing.append("closure_manifest:roadmap_parity_scoreboard")
    else:
        row = roadmap.get("lab_only_driver_validation")
        if not isinstance(row, dict) or row.get("status") != "starter_landed":
            missing.append("closure_manifest:roadmap_parity_scoreboard:lab_only_driver_validation")

    landed_input = closure.get("landed_input_helper_evidence")
    if landed_input != {"zigux/tests/phase10_virtio_input_manifest.json": EXPECTED_LANDED_INPUT_HELPERS}:
        missing.append("closure_manifest:landed_input_helper_evidence")
    landed_mmio = closure.get("landed_mmio_helper_evidence")
    if landed_mmio != {"zigux/tests/phase10_virtio_mmio_manifest.json": EXPECTED_LANDED_MMIO_HELPERS}:
        missing.append("closure_manifest:landed_mmio_helper_evidence")
    if closure.get("focused_harness_replays") != EXPECTED_FOCUSED_HARNESS:
        missing.append("closure_manifest:focused_harness_replays")

    blocked = closure.get("blocked_transport_gaps")
    if not isinstance(blocked, dict) or blocked.get("zigux/tests/phase10_virtio_mmio_manifest.json") != "phase10-mmio-lifecycle-and-irq-paths":
        missing.append("closure_manifest:blocked_transport_gaps:mmio")

    ring_manifest = load_json(root, "zigux/tests/phase10_virtio_ring_manifest.json")
    gaps = ring_manifest.get("gaps") if isinstance(ring_manifest, dict) else None
    if not isinstance(gaps, list):
        missing.append("ring_manifest:gaps")
    else:
        ring_gap = next((gap for gap in gaps if isinstance(gap, dict) and gap.get("id") == "phase10-broken-queue-recovery-helper"), None)
        if ring_gap is None:
            missing.append("ring_manifest:broken-queue-recovery-helper")
        else:
            why_now = str(ring_gap.get("why_now", ""))
            if ring_gap.get("status") != "starter_landed":
                missing.append("ring_manifest:broken-queue-recovery-helper:status")
            if "broken-queue recovery helper" not in why_now:
                missing.append("ring_manifest:broken-queue-recovery-helper:phrase")
            if "teardown-safe queue reuse" not in why_now:
                missing.append("ring_manifest:broken-queue-recovery-helper:reuse")

    return [], missing


def write_fixture(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")

    for rel_path, markers in TEXT_MARKERS.items():
        extra = EXACT_ONCE.get(rel_path, [])
        all_markers = markers + [m for m in extra if m not in markers]
        (root / rel_path).write_text("\n".join(all_markers) + "\nPHASE10_TEST_COUNT=11\n", encoding="utf-8")

    closure_manifest = {
        "phase": "Phase 10",
        "status": "active",
        "tranche": "virtio-lab-bundle",
        "doc_count": 9,
        "manifest_count": 4,
        "driver_count": 4,
        "test_count": 11,
        "has_virtio_mmio_zig": True,
        "freeze_map": "Documentation/zigux/freeze-map.md",
        "freeze_boundary_status": "aligned",
        "freeze_status_change_claimed": False,
        "review_checklist": "Documentation/zigux/review-checklist.md",
        "risky_transport_posture": "blocked_on_risky_transport",
        "architecture_council_reopen_required": True,
        "architecture_council_reopen_attached": False,
        "manifests": MANIFESTS,
        "drivers": DRIVERS,
        "tests": TESTS,
        "allowed_roadmap_destinations": EXPECTED_ALLOWED_ROADMAP_DESTINATIONS,
        "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
        "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
        "exact_checks": EXPECTED_EXACT_CHECKS,
        "survey_provenance": {
            "source": "manifest_derived",
            "lane_keys": EXPECTED_SURVEY_LANE_KEYS,
            "surveyed_commits": EXPECTED_SURVEYED_COMMITS,
        },
        "roadmap_parity_scoreboard": {"lab_only_driver_validation": {"status": "starter_landed"}},
        "landed_input_helper_evidence": {"zigux/tests/phase10_virtio_input_manifest.json": EXPECTED_LANDED_INPUT_HELPERS},
        "landed_mmio_helper_evidence": {"zigux/tests/phase10_virtio_mmio_manifest.json": EXPECTED_LANDED_MMIO_HELPERS},
        "focused_harness_replays": EXPECTED_FOCUSED_HARNESS,
        "blocked_transport_gaps": {"zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths"},
    }
    (root / "zigux/tests/phase10_closure_manifest.json").write_text(json.dumps(closure_manifest, indent=2) + "\n", encoding="utf-8")
    ring_manifest = {"gaps": [{"id": "phase10-broken-queue-recovery-helper", "status": "starter_landed", "why_now": "broken-queue recovery helper with teardown-safe queue reuse"}]}
    (root / "zigux/tests/phase10_virtio_ring_manifest.json").write_text(json.dumps(ring_manifest, indent=2) + "\n", encoding="utf-8")
    (root / "zigux/tests/phase10_virtio_core_manifest.json").write_text("{}\n", encoding="utf-8")
    (root / "zigux/tests/phase10_virtio_input_manifest.json").write_text("{}\n", encoding="utf-8")
    (root / "zigux/tests/phase10_virtio_mmio_manifest.json").write_text("{}\n", encoding="utf-8")


def expect_marker(label: str, root: Path, marker: str) -> None:
    files, markers = validate(root)
    if files:
        raise SystemExit(f"phase10-closure-self-test:{label}:missing_files:{','.join(files)}")
    if marker not in markers:
        raise SystemExit(f"phase10-closure-self-test:{label}:expected:{marker}:actual:{','.join(markers) if markers else 'none'}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_") as tmp_dir:
        root = Path(tmp_dir) / "repo"
        write_fixture(root)
        files, markers = validate(root)
        if files or markers:
            raise SystemExit(f"phase10-closure-self-test:baseline_failed:files={files}:markers={markers}")

        closure_manifest_path = root / "zigux/tests/phase10_closure_manifest.json"
        manifest = json.loads(closure_manifest_path.read_text(encoding="utf-8"))
        manifest["test_count"] = 9
        closure_manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_marker("test_count_guard", root, "closure_manifest:test_count")
        write_fixture(root)

        manifest = json.loads(closure_manifest_path.read_text(encoding="utf-8"))
        manifest["landed_mmio_helper_evidence"]["zigux/tests/phase10_virtio_mmio_manifest.json"] = EXPECTED_LANDED_MMIO_HELPERS[:-1]
        closure_manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_marker("mmio_probe_preflight_guard", root, "closure_manifest:landed_mmio_helper_evidence")
        write_fixture(root)

        note_path = root / "Documentation/zigux/phase10-closure-evidence.md"
        note_path.write_text(note_path.read_text(encoding="utf-8").replace("phase10-mmio-probe-preflight-helper", "drift", 1), encoding="utf-8")
        expect_marker("closure_note_probe_preflight_guard", root, "Documentation/zigux/phase10-closure-evidence.md:phase10-mmio-probe-preflight-helper")
        write_fixture(root)

        ledger_path = root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        ledger_path.write_text(ledger_path.read_text(encoding="utf-8").replace("phase10-mmio-probe-preflight-helper", "drift", 1), encoding="utf-8")
        expect_marker("ledger_probe_preflight_guard", root, "zigux-alpha/PHASE10_CLOSURE_LEDGER.md:PHASE10_LEDGER_LANDED_MMIO_HELPERS=phase10-mmio-register-window-helper,phase10-mmio-queue-register-helper,phase10-mmio-queue-notify-helper,phase10-mmio-queue-address-helper,phase10-mmio-config-window-helper,phase10-mmio-config-write-helper,phase10-mmio-interrupt-ack-helper,phase10-mmio-probe-preflight-helper")
        write_fixture(root)

        mmio_survey_path = root / "Documentation/zigux/phase10-virtio-mmio-survey.md"
        mmio_survey_path.write_text(mmio_survey_path.read_text(encoding="utf-8").replace("phase10-mmio-probe-preflight-helper", "drift", 1), encoding="utf-8")
        expect_marker("mmio_survey_probe_preflight_guard", root, "Documentation/zigux/phase10-virtio-mmio-survey.md:phase10-mmio-probe-preflight-helper")
        write_fixture(root)

        readme_path = root / "Documentation/zigux/README.md"
        readme_path.write_text(readme_path.read_text(encoding="utf-8") + "python3 scripts/zigux/check-phase10-harness-coverage.py\n", encoding="utf-8")
        expect_marker("docs_readme_duplicate_guard", root, "Documentation/zigux/README.md:count:python3 scripts/zigux/check-phase10-harness-coverage.py=2")
        write_fixture(root)

        ring_manifest_path = root / "zigux/tests/phase10_virtio_ring_manifest.json"
        ring_manifest = json.loads(ring_manifest_path.read_text(encoding="utf-8"))
        ring_manifest["gaps"][0]["why_now"] = "broken-queue recovery helper only"
        ring_manifest_path.write_text(json.dumps(ring_manifest, indent=2) + "\n", encoding="utf-8")
        expect_marker("ring_reuse_guard", root, "ring_manifest:broken-queue-recovery-helper:reuse")
        write_fixture(root)

        (root / "scripts/zigux/check-phase10-harness-coverage.py").unlink()
        files, markers = validate(root)
        if "scripts/zigux/check-phase10-harness-coverage.py" not in files:
            raise SystemExit(f"phase10-closure-self-test:file_guard:actual_files={files}:markers={markers}")

    print("PHASE10_CLOSURE_VALIDATOR_SELF_TEST=pass")
    print("PHASE10_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=8")
    return 0


if "--self-test" in sys.argv[1:]:
    sys.exit(run_self_test())

missing_files, missing_markers = validate(ROOT)
if missing_files:
    print("PHASE10_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE10_CLOSURE_FILES_START")
    for item in missing_files:
        print(item)
    print("MISSING_PHASE10_CLOSURE_FILES_END")
    sys.exit(1)
if missing_markers:
    print("PHASE10_CLOSURE_VALIDATION=fail")
    print("MISSING_PHASE10_CLOSURE_MARKERS_START")
    for item in missing_markers:
        print(item)
    print("MISSING_PHASE10_CLOSURE_MARKERS_END")
    sys.exit(1)

total_markers = sum(len(v) for v in TEXT_MARKERS.values()) + sum(len(v) for v in EXACT_ONCE.values())
print("PHASE10_CLOSURE_VALIDATION=pass")
print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE10_CLOSURE_REQUIRED_MARKER_COUNT={total_markers}")
