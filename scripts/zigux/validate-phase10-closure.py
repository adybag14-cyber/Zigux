#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "scripts/zigux/validate-phase10-closure.py",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "zigux/Makefile",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
]

MAKE_MARKERS = [
    "PHONY += phase10-validate phase10-test phase10",
]

CLOSURE_DOC_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/tests/phase10_closure_manifest.json",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "shared reminder-surface drift",
]

LANE_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/tests/phase10_closure_manifest.json",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

REVIEW_CHECKLIST_MARKERS = [
    "scripts/zigux/check-phase10-harness-coverage.py",
    "Documentation/zigux/phase10-closure-evidence.md",
    "zigux/tests/phase10_closure_manifest.json",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

MANIFEST_MARKERS = [
    '"phase": "Phase 10"',
    '"tranche": "virtio-lab-bundle"',
    '"scripts/zigux/check-phase10-harness-coverage.py"',
]

SURVEY_MANIFESTS = {
    "core": "zigux/tests/phase10_virtio_core_manifest.json",
    "ring": "zigux/tests/phase10_virtio_ring_manifest.json",
    "input": "zigux/tests/phase10_virtio_input_manifest.json",
    "mmio": "zigux/tests/phase10_virtio_mmio_manifest.json",
}

READY_TRANSPORT_FOLLOWUPS = {
    "zigux/tests/phase10_virtio_input_manifest.json": "blocked_on_risky_transport",
    "zigux/tests/phase10_virtio_mmio_manifest.json": "blocked_on_risky_transport",
}

LANDED_HELPER_FIELDS = {
    "landed_core_helper_evidence": "zigux/tests/phase10_virtio_core_manifest.json",
    "landed_ring_helper_evidence": "zigux/tests/phase10_virtio_ring_manifest.json",
    "landed_input_helper_evidence": "zigux/tests/phase10_virtio_input_manifest.json",
    "landed_mmio_helper_evidence": "zigux/tests/phase10_virtio_mmio_manifest.json",
}

FOCUSED_HARNESS_REPLAY_FILES = [
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
]

COMMANDS = [
    ["scripts/zigux/check-phase10-harness-coverage.py", "--self-test"],
    ["scripts/zigux/check-phase10-harness-coverage.py"],
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def read_json(root: Path, rel_path: str) -> dict:
    return json.loads(read_text(root, rel_path))


def collect_missing_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    checks = [
        ("make", "zigux/Makefile", MAKE_MARKERS),
        ("closure", "Documentation/zigux/phase10-closure-evidence.md", CLOSURE_DOC_MARKERS),
        ("lane", "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", LANE_MARKERS),
        ("review", "Documentation/zigux/review-checklist.md", REVIEW_CHECKLIST_MARKERS),
        ("manifest", "zigux/tests/phase10_closure_manifest.json", MANIFEST_MARKERS),
    ]
    for label, rel_path, markers in checks:
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing.append(f"{label}:{marker}")
    return missing


def collect_manifest_drift(root: Path) -> list[str]:
    closure = read_json(root, "zigux/tests/phase10_closure_manifest.json")
    provenance = closure.get("survey_provenance", {})
    lane_keys = provenance.get("lane_keys", {})
    surveyed_commits = provenance.get("surveyed_commits", {})
    drift: list[str] = []

    for key, path in SURVEY_MANIFESTS.items():
        manifest = read_json(root, path)
        expected_lane = manifest.get("lane_key")
        actual_lane = lane_keys.get(key)
        if actual_lane != expected_lane:
            drift.append(f"survey_provenance:{key}:lane_key:{actual_lane!r}!={expected_lane!r}")
        expected_commit = manifest.get("surveyed_commit")
        actual_commit = surveyed_commits.get(key)
        if actual_commit != expected_commit:
            drift.append(f"survey_provenance:{key}:surveyed_commit:{actual_commit!r}!={expected_commit!r}")

    ready_followups = closure.get("ready_transport_followups", {})
    for path, expected_status in READY_TRANSPORT_FOLLOWUPS.items():
        expected_gap = ready_followups.get(path)
        if not isinstance(expected_gap, str) or not expected_gap:
            drift.append(f"ready_transport_followups:{path}:missing")
            continue
        manifest = read_json(root, path)
        blocked = {
            gap.get("id")
            for gap in manifest.get("gaps", [])
            if gap.get("status") == expected_status and isinstance(gap.get("id"), str)
        }
        if expected_gap not in blocked:
            drift.append(f"ready_transport_followups:{path}:{expected_gap!r}:not_{expected_status}")

    for field, path in LANDED_HELPER_FIELDS.items():
        helper_map = closure.get(field, {})
        listed_helpers = helper_map.get(path)
        if not isinstance(listed_helpers, list) or not listed_helpers:
            drift.append(f"{field}:{path}:missing")
            continue
        manifest = read_json(root, path)
        landed = {
            gap.get("id")
            for gap in manifest.get("gaps", [])
            if gap.get("status") == "starter_landed" and isinstance(gap.get("id"), str)
        }
        for helper_id in listed_helpers:
            if helper_id not in landed:
                drift.append(f"{field}:{path}:{helper_id!r}:not_starter_landed")

    tests = closure.get("tests")
    if not isinstance(tests, list) or not tests:
        drift.append("tests:missing")
        test_set: set[str] = set()
    else:
        test_set = {item for item in tests if isinstance(item, str) and item}

    focused_harness_replays = closure.get("focused_harness_replays")
    if not isinstance(focused_harness_replays, dict) or not focused_harness_replays:
        drift.append("focused_harness_replays:missing")
    else:
        for path in FOCUSED_HARNESS_REPLAY_FILES:
            replay_labels = focused_harness_replays.get(path)
            if not isinstance(replay_labels, list) or not replay_labels:
                drift.append(f"focused_harness_replays:{path}:missing")
                continue
            if path not in test_set:
                drift.append(f"focused_harness_replays:{path}:not_listed_in_tests")
            for replay_label in replay_labels:
                if not isinstance(replay_label, str) or not replay_label.strip():
                    drift.append(f"focused_harness_replays:{path}:blank_label")
                    break

    return drift


def run_command(root: Path, cmd: list[str]) -> int:
    return subprocess.run([sys.executable, str(root / cmd[0]), *cmd[1:]], cwd=root, check=False).returncode


def run_required_commands(root: Path) -> list[str]:
    failed: list[str] = []
    for command in COMMANDS:
        if run_command(root, command) != 0:
            failed.append(" ".join(command))
    return failed


def write_fixture(root: Path) -> None:
    files = {
        "scripts/zigux/validate-phase10-closure.py": "fixture\n",
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(CLOSURE_DOC_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": "\n".join(LANE_MARKERS) + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
        "scripts/zigux/check-phase10-harness-coverage.py": (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--self-test' in sys.argv[1:]:\n"
            "    print('PHASE10_HARNESS_COVERAGE_SELF_TEST=pass')\n"
            "    raise SystemExit(0)\n"
            "print('PHASE10_HARNESS_COVERAGE=pass')\n"
        ),
        "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
        "zigux/tests/phase10_closure_manifest.json": json.dumps(
            {
                "phase": "Phase 10",
                "tranche": "virtio-lab-bundle",
                "lab_only_driver_validation": {
                    "evidence": ["scripts/zigux/check-phase10-harness-coverage.py"]
                },
                "survey_provenance": {
                    "lane_keys": {
                        "core": "P10-L01",
                        "ring": "P10-L05",
                        "input": "P10-L13",
                        "mmio": "P10-L11",
                    },
                    "surveyed_commits": {
                        "core": "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
                        "ring": "e42103fc02f544e1bd23a5ec2e5b584734f5af7d",
                        "input": "7361ac51374149a96b7a7a2c6ea3c995d8cc1231",
                        "mmio": "b53ec2bd507d0b3283486e76acc273b184ad5bf8",
                    },
                },
                "ready_transport_followups": {
                    "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
                    "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
                },
                "landed_core_helper_evidence": {
                    "zigux/tests/phase10_virtio_core_manifest.json": [
                        "phase10-queue-shape-bookkeeping-helper",
                        "phase10-reset-replay-bookkeeping-helper",
                    ]
                },
                "landed_ring_helper_evidence": {
                    "zigux/tests/phase10_virtio_ring_manifest.json": [
                        "phase10-virtqueue-shape-helper",
                        "phase10-notify-prepare-helper",
                    ]
                },
                "landed_input_helper_evidence": {
                    "zigux/tests/phase10_virtio_input_manifest.json": [
                        "phase10-virtio-input-capability-setup-helper",
                        "phase10-virtio-input-status-drain-helper",
                    ]
                },
                "landed_mmio_helper_evidence": {
                    "zigux/tests/phase10_virtio_mmio_manifest.json": [
                        "phase10-mmio-config-window-helper",
                        "phase10-mmio-selected-queue-readiness-helper",
                    ]
                },
                "focused_harness_replays": {
                    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig": [
                        "phase10 core interrupt-compound-ack replay"
                    ],
                    "zigux/tests/phase10_virtio_core_reset_queue.zig": [
                        "phase10 core reset-queue replay"
                    ],
                    "zigux/tests/phase10_virtio_driver_id.zig": [
                        "phase10 driver-id review path replay"
                    ],
                    "zigux/tests/phase10_virtio_ring_reset_reuse.zig": [
                        "phase10 ring drained-reset reuse replay"
                    ],
                    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig": [
                        "phase10 input queue-callback-preflight replay"
                    ],
                    "zigux/tests/phase10_virtio_input_status_drain.zig": [
                        "phase10 input status-drain replay"
                    ],
                    "zigux/tests/phase10_virtio_input_probe_preflight.zig": [
                        "phase10 input probe-preflight replay"
                    ],
                    "zigux/tests/phase10_virtio_input_registration_preflight.zig": [
                        "phase10 input registration-preflight replay"
                    ],
                    "zigux/tests/phase10_virtio_input_teardown_observation.zig": [
                        "phase10 input teardown-observation replay"
                    ],
                },
                "tests": [
                    "zigux/tests/phase10_virtio_core.zig",
                    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
                    "zigux/tests/phase10_virtio_core_reset_queue.zig",
                    "zigux/tests/phase10_virtio_driver_id.zig",
                    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
                    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
                    "zigux/tests/phase10_virtio_input_status_drain.zig",
                    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
                    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
                    "zigux/tests/phase10_virtio_input_teardown_observation.zig"
                ],
            }
        ),
        "zigux/tests/phase10_virtio_core_manifest.json": json.dumps(
            {
                "lane_key": "P10-L01",
                "surveyed_commit": "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
                "gaps": [
                    {"id": "phase10-queue-shape-bookkeeping-helper", "status": "starter_landed"},
                    {"id": "phase10-reset-replay-bookkeeping-helper", "status": "starter_landed"},
                ],
            }
        ),
        "zigux/tests/phase10_virtio_ring_manifest.json": json.dumps(
            {
                "lane_key": "P10-L05",
                "surveyed_commit": "e42103fc02f544e1bd23a5ec2e5b584734f5af7d",
                "gaps": [
                    {"id": "phase10-virtqueue-shape-helper", "status": "starter_landed"},
                    {"id": "phase10-notify-prepare-helper", "status": "starter_landed"},
                ],
            }
        ),
        "zigux/tests/phase10_virtio_input_manifest.json": json.dumps(
            {
                "lane_key": "P10-L13",
                "surveyed_commit": "7361ac51374149a96b7a7a2c6ea3c995d8cc1231",
                "gaps": [
                    {"id": "phase10-virtio-input-capability-setup-helper", "status": "starter_landed"},
                    {"id": "phase10-virtio-input-status-drain-helper", "status": "starter_landed"},
                    {"id": "phase10-virtio-input-registration-lifecycle", "status": "blocked_on_risky_transport"},
                ],
            }
        ),
        "zigux/tests/phase10_virtio_mmio_manifest.json": json.dumps(
            {
                "lane_key": "P10-L11",
                "surveyed_commit": "b53ec2bd507d0b3283486e76acc273b184ad5bf8",
                "gaps": [
                    {"id": "phase10-mmio-config-window-helper", "status": "starter_landed"},
                    {"id": "phase10-mmio-selected-queue-readiness-helper", "status": "starter_landed"},
                    {"id": "phase10-mmio-lifecycle-and-irq-paths", "status": "blocked_on_risky_transport"},
                ],
            }
        ),
    }
    for rel_path, content in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files = collect_missing_files(root)
        missing_markers = collect_missing_markers(root)
        manifest_drift = collect_manifest_drift(root)
        if missing_files or missing_markers or manifest_drift:
            raise SystemExit(
                "phase10-closure-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}:"
                f"drift={','.join(manifest_drift) if manifest_drift else 'none'}"
            )
        failed_commands = run_required_commands(root)
        if failed_commands:
            raise SystemExit(
                "phase10-closure-self-test:baseline_command_failed:"
                f"commands={','.join(failed_commands)}"
            )

        closure = root / "zigux/tests/phase10_closure_manifest.json"
        original_closure = json.loads(closure.read_text(encoding="utf-8"))

        broken = dict(original_closure)
        broken["survey_provenance"] = dict(original_closure["survey_provenance"])
        broken["survey_provenance"]["lane_keys"] = dict(original_closure["survey_provenance"]["lane_keys"])
        broken["survey_provenance"]["lane_keys"]["ring"] = "P10-L10"
        closure.write_text(json.dumps(broken), encoding="utf-8")
        drift = collect_manifest_drift(root)
        if "survey_provenance:ring:lane_key:'P10-L10'!='P10-L05'" not in drift:
            raise SystemExit("phase10-closure-self-test:ring_lane_drift_not_detected")
        closure.write_text(json.dumps(original_closure), encoding="utf-8")

        broken = dict(original_closure)
        broken["survey_provenance"] = dict(original_closure["survey_provenance"])
        broken["survey_provenance"]["lane_keys"] = dict(original_closure["survey_provenance"]["lane_keys"])
        broken["survey_provenance"]["lane_keys"]["mmio"] = "P10-L10"
        closure.write_text(json.dumps(broken), encoding="utf-8")
        drift = collect_manifest_drift(root)
        if not any(item.startswith("survey_provenance:mmio:lane_key:") for item in drift):
            raise SystemExit("phase10-closure-self-test:mmio_lane_drift_not_detected")
        closure.write_text(json.dumps(original_closure), encoding="utf-8")

        broken = dict(original_closure)
        broken["survey_provenance"] = dict(original_closure["survey_provenance"])
        broken["survey_provenance"]["surveyed_commits"] = dict(original_closure["survey_provenance"]["surveyed_commits"])
        broken["survey_provenance"]["surveyed_commits"]["ring"] = "stale-ring-sha"
        closure.write_text(json.dumps(broken), encoding="utf-8")
        drift = collect_manifest_drift(root)
        if "survey_provenance:ring:surveyed_commit:'stale-ring-sha'!='e42103fc02f544e1bd23a5ec2e5b584734f5af7d'" not in drift:
            raise SystemExit("phase10-closure-self-test:ring_commit_drift_not_detected")
        closure.write_text(json.dumps(original_closure), encoding="utf-8")

        broken = dict(original_closure)
        broken["ready_transport_followups"] = dict(original_closure["ready_transport_followups"])
        broken["ready_transport_followups"]["zigux/tests/phase10_virtio_mmio_manifest.json"] = "phase10-mmio-config-write-helper"
        closure.write_text(json.dumps(broken), encoding="utf-8")
        drift = collect_manifest_drift(root)
        if "ready_transport_followups:zigux/tests/phase10_virtio_mmio_manifest.json:'phase10-mmio-config-write-helper':not_blocked_on_risky_transport" not in drift:
            raise SystemExit("phase10-closure-self-test:mmio_followup_drift_not_detected")
        closure.write_text(json.dumps(original_closure), encoding="utf-8")

        broken = dict(original_closure)
        broken["landed_ring_helper_evidence"] = dict(original_closure["landed_ring_helper_evidence"])
        broken["landed_ring_helper_evidence"]["zigux/tests/phase10_virtio_ring_manifest.json"] = [
            "phase10-virtqueue-shape-helper",
            "phase10-callback-delay-helper",
        ]
        closure.write_text(json.dumps(broken), encoding="utf-8")
        drift = collect_manifest_drift(root)
        if "landed_ring_helper_evidence:zigux/tests/phase10_virtio_ring_manifest.json:'phase10-callback-delay-helper':not_starter_landed" not in drift:
            raise SystemExit("phase10-closure-self-test:ring_helper_drift_not_detected")
        closure.write_text(json.dumps(original_closure), encoding="utf-8")

        broken = dict(original_closure)
        broken["landed_input_helper_evidence"] = dict(original_closure["landed_input_helper_evidence"])
        broken["landed_input_helper_evidence"]["zigux/tests/phase10_virtio_input_manifest.json"] = [
            "phase10-virtio-input-capability-setup-helper",
            "phase10-virtio-input-queue-callback-preflight-helper",
        ]
        closure.write_text(json.dumps(broken), encoding="utf-8")
        drift = collect_manifest_drift(root)
        if "landed_input_helper_evidence:zigux/tests/phase10_virtio_input_manifest.json:'phase10-virtio-input-queue-callback-preflight-helper':not_starter_landed" not in drift:
            raise SystemExit("phase10-closure-self-test:input_helper_drift_not_detected")
        closure.write_text(json.dumps(original_closure), encoding="utf-8")

        broken = dict(original_closure)
        broken["focused_harness_replays"] = dict(original_closure["focused_harness_replays"])
        broken["focused_harness_replays"]["zigux/tests/phase10_virtio_input_status_drain.zig"] = []
        closure.write_text(json.dumps(broken), encoding="utf-8")
        drift = collect_manifest_drift(root)
        if "focused_harness_replays:zigux/tests/phase10_virtio_input_status_drain.zig:missing" not in drift:
            raise SystemExit("phase10-closure-self-test:focused_replay_missing_not_detected")
        closure.write_text(json.dumps(original_closure), encoding="utf-8")

        broken = dict(original_closure)
        broken["tests"] = [
            item
            for item in original_closure["tests"]
            if item != "zigux/tests/phase10_virtio_ring_reset_reuse.zig"
        ]
        closure.write_text(json.dumps(broken), encoding="utf-8")
        drift = collect_manifest_drift(root)
        if "focused_harness_replays:zigux/tests/phase10_virtio_ring_reset_reuse.zig:not_listed_in_tests" not in drift:
            raise SystemExit("phase10-closure-self-test:focused_replay_test_membership_drift_not_detected")
        closure.write_text(json.dumps(original_closure), encoding="utf-8")

        broken = dict(original_closure)
        broken["focused_harness_replays"] = dict(original_closure["focused_harness_replays"])
        broken["focused_harness_replays"]["zigux/tests/phase10_virtio_input_probe_preflight.zig"] = ["   "]
        closure.write_text(json.dumps(broken), encoding="utf-8")
        drift = collect_manifest_drift(root)
        if "focused_harness_replays:zigux/tests/phase10_virtio_input_probe_preflight.zig:blank_label" not in drift:
            raise SystemExit("phase10-closure-self-test:focused_replay_blank_label_not_detected")
        closure.write_text(json.dumps(original_closure), encoding="utf-8")

        makefile = root / "zigux/Makefile"
        makefile.write_text("", encoding="utf-8")
        if "make:PHONY += phase10-validate phase10-test phase10" not in collect_missing_markers(root):
            raise SystemExit("phase10-closure-self-test:missing_make_marker_not_detected")
        write_fixture(root)

        checker = root / "scripts/zigux/check-phase10-harness-coverage.py"
        checker.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--self-test' in sys.argv[1:]:\n"
            "    print('PHASE10_HARNESS_COVERAGE_SELF_TEST=pass')\n"
            "    raise SystemExit(0)\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
        )
        failed_commands = run_required_commands(root)
        if failed_commands != ["scripts/zigux/check-phase10-harness-coverage.py"]:
            raise SystemExit(
                "phase10-closure-self-test:failed_command_not_detected:"
                f"actual={','.join(failed_commands) if failed_commands else 'none'}"
            )

    print("PHASE10_CLOSURE_VALIDATION_SELF_TEST=pass")
    print("PHASE10_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT=11")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 10 closure packet.")
    parser.add_argument("--self-test", action="store_true", help="Run validator self-test cases without reading repo files.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files = collect_missing_files(ROOT)
    if missing_files:
        print("PHASE10_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE10_CLOSURE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_CLOSURE_FILES_END")
        return 1

    missing_markers = collect_missing_markers(ROOT)
    if missing_markers:
        print("PHASE10_CLOSURE_VALIDATION=fail")
        print("MISSING_PHASE10_CLOSURE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE10_CLOSURE_MARKERS_END")
        return 1

    manifest_drift = collect_manifest_drift(ROOT)
    if manifest_drift:
        print("PHASE10_CLOSURE_VALIDATION=fail")
        print("PHASE10_CLOSURE_MANIFEST_DRIFT_START")
        for item in manifest_drift:
            print(item)
        print("PHASE10_CLOSURE_MANIFEST_DRIFT_END")
        return 1

    failed_commands = run_required_commands(ROOT)
    if failed_commands:
        print("PHASE10_CLOSURE_VALIDATION=fail")
        print("PHASE10_CLOSURE_VALIDATION_FAILED_COMMANDS_START")
        for command in failed_commands:
            print(command)
        print("PHASE10_CLOSURE_VALIDATION_FAILED_COMMANDS_END")
        return 1

    print("PHASE10_CLOSURE_VALIDATION=pass")
    print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE10_CLOSURE_REQUIRED_MARKER_COUNT="
        f"{len(MAKE_MARKERS) + len(CLOSURE_DOC_MARKERS) + len(LANE_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(MANIFEST_MARKERS)}"
    )
    print(f"PHASE10_CLOSURE_COMMAND_COUNT={len(COMMANDS)}")
    print(f"PHASE10_CLOSURE_PROVENANCE_PACKET_COUNT={len(SURVEY_MANIFESTS)}")
    print(f"PHASE10_CLOSURE_READY_FOLLOWUP_COUNT={len(READY_TRANSPORT_FOLLOWUPS)}")
    print(f"PHASE10_CLOSURE_LANDED_HELPER_PACKET_COUNT={len(LANDED_HELPER_FIELDS)}")
    print(f"PHASE10_CLOSURE_FOCUSED_HARNESS_REPLAY_COUNT={len(FOCUSED_HARNESS_REPLAY_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())