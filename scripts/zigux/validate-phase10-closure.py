#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

REQUIRED_FILES = [
    "scripts/zigux/check-phase10-bootstrap-route.py",
    "scripts/zigux/validate-phase10-closure.py",
    "scripts/zigux/validate-phase10.py",
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "scripts/zigux/check-phase10-ring-packet.py",
    "scripts/zigux/check-phase10-input-packet.py",
    "scripts/zigux/check-phase10-mmio-packet.py",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
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
    "scripts/zigux/check-phase10-bootstrap-route.py",
    "scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "scripts/zigux/check-phase10-input-packet.py",
    "scripts/zigux/check-phase10-mmio-packet.py",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "zigux/tests/phase10_closure_manifest.json",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md",
    "fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`",
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
    "scripts/zigux/check-phase10-bootstrap-route.py",
    '"scripts/zigux/check-phase10-harness-coverage.py"',
]

SURVEY_MANIFESTS = {
    "core": "zigux/tests/phase10_virtio_core_manifest.json",
    "ring": "zigux/tests/phase10_virtio_ring_manifest.json",
    "input": "zigux/tests/phase10_virtio_input_manifest.json",
    "mmio": "zigux/tests/phase10_virtio_mmio_manifest.json",
}

READY_TRANSPORT_FOLLOWUPS = {
    "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
    "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
}

EXPECTED_CORE_HELPERS = [
    "phase10-queue-shape-bookkeeping-helper",
    "phase10-config-generation-bookkeeping-helper",
    "phase10-interrupt-ack-bookkeeping-helper",
    "phase10-lifecycle-guard-bookkeeping-helper",
    "phase10-driver-validation-narrowing-helper",
    "phase10-core-attribute-summary-helper",
    "phase10-reset-replay-bookkeeping-helper",
]

EXPECTED_RING_HELPERS = [
    "phase10-virtqueue-shape-helper",
    "phase10-used-buffer-polling-helper",
    "phase10-callback-enable-helper",
    "phase10-callback-delay-helper",
    "phase10-notify-prepare-helper",
    "phase10-notification-data-summary-helper",
    "phase10-broken-queue-poll-guard",
    "phase10-queue-publish-readiness-helper",
    "phase10-queue-reset-helper",
    "phase10-queue-reset-readiness-helper",
    "phase10-ring-verify-replay",
    "phase10-virtio-ring-slice-note",
]

EXPECTED_INPUT_HELPERS = [
    "phase10-virtio-input-capability-setup-helper",
    "phase10-virtio-input-multitouch-slot-helper",
    "phase10-virtio-input-probe-preflight-helper",
    "phase10-virtio-input-teardown-observation-helper",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-status-drain-helper",
]

EXPECTED_MMIO_HELPERS = [
    "phase10-virtio-mmio-lab-helper",
    "phase10-mmio-transport-identity-helper",
    "phase10-mmio-probe-preflight-helper",
    "phase10-mmio-selected-queue-readiness-helper",
    "phase10-mmio-interrupt-ack-disposition-helper",
    "phase10-mmio-feature-negotiation-summary-helper",
    "phase10-mmio-config-write-plan-freshness-helper",
    "phase10-mmio-config-write-disposition-helper",
]

LANDED_HELPER_FIELDS = {
    "landed_core_helper_evidence": {
        "path": "zigux/tests/phase10_virtio_core_manifest.json",
        "expected_helpers": EXPECTED_CORE_HELPERS,
    },
    "landed_ring_helper_evidence": {
        "path": "zigux/tests/phase10_virtio_ring_manifest.json",
        "expected_helpers": EXPECTED_RING_HELPERS,
    },
    "landed_input_helper_evidence": {
        "path": "zigux/tests/phase10_virtio_input_manifest.json",
        "expected_helpers": EXPECTED_INPUT_HELPERS,
    },
    "landed_mmio_helper_evidence": {
        "path": "zigux/tests/phase10_virtio_mmio_manifest.json",
        "expected_helpers": EXPECTED_MMIO_HELPERS,
    },
}

FOCUSED_HARNESS_REPLAY_FILES = [
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
    "drivers/virtio/virtio_ring_publish_readiness.zig",
    "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
    "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
]

EXPECTED_EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase10-bootstrap-route.py",
    "python3 scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "python3 scripts/zigux/check-phase10-ring-packet.py",
    "python3 scripts/zigux/check-phase10-input-packet.py",
    "python3 scripts/zigux/check-phase10-mmio-packet.py",
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "python3 scripts/zigux/validate-phase10.py",
    "python3 scripts/zigux/validate-phase10-closure.py",
    "make -C zigux phase10-validate",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-test",
    "make -C zigux phase10"
]

COMMANDS = [
    ["scripts/zigux/check-phase10-bootstrap-route.py", "--self-test"],
    ["scripts/zigux/check-phase10-bootstrap-route.py"],
    ["scripts/zigux/check-phase10-shared-freeze-boundary.py", "--self-test"],
    ["scripts/zigux/check-phase10-shared-freeze-boundary.py"],
    ["scripts/zigux/check-phase10-ring-packet.py", "--self-test"],
    ["scripts/zigux/check-phase10-ring-packet.py"],
    ["scripts/zigux/check-phase10-input-packet.py", "--self-test"],
    ["scripts/zigux/check-phase10-input-packet.py"],
    ["scripts/zigux/check-phase10-mmio-packet.py", "--self-test"],
    ["scripts/zigux/check-phase10-mmio-packet.py"],
    ["scripts/zigux/check-phase10-harness-coverage.py", "--self-test"],
    ["scripts/zigux/check-phase10-harness-coverage.py"],
    ["scripts/zigux/check-phase10-tests-readme-core-surfaces.py", "--self-test"],
    ["scripts/zigux/check-phase10-tests-readme-core-surfaces.py"],
    ["scripts/zigux/validate-phase10.py", "--self-test"],
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def read_json(root: Path, rel_path: str) -> dict:
    return json.loads(read_text(root, rel_path))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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

    exact_checks = closure.get("exact_checks")
    if not isinstance(exact_checks, list) or not exact_checks:
        drift.append("exact_checks:missing")
    else:
        indexes: list[int] = []
        for item in EXPECTED_EXACT_CHECKS:
            if item not in exact_checks:
                drift.append(f"exact_checks:{item!r}:missing")
                continue
            indexes.append(exact_checks.index(item))
        if len(indexes) == len(EXPECTED_EXACT_CHECKS) and indexes != sorted(indexes):
            drift.append("exact_checks:phase10_route:out_of_order")

    for key, path in SURVEY_MANIFESTS.items():
        manifest = read_json(root, path)
        if lane_keys.get(key) != manifest.get("lane_key"):
            drift.append(
                f"survey_provenance:{key}:lane_key:{lane_keys.get(key)!r}!={manifest.get('lane_key')!r}"
            )
        if surveyed_commits.get(key) != manifest.get("surveyed_commit"):
            drift.append(
                f"survey_provenance:{key}:surveyed_commit:{surveyed_commits.get(key)!r}!={manifest.get('surveyed_commit')!r}"
            )

    ready_followups = closure.get("ready_transport_followups", {})
    blocked_transport_gaps = closure.get("blocked_transport_gaps", {})
    for path, expected_gap in READY_TRANSPORT_FOLLOWUPS.items():
        actual_gap = ready_followups.get(path)
        if not isinstance(actual_gap, str) or not actual_gap:
            drift.append(f"ready_transport_followups:{path}:missing")
        elif actual_gap != expected_gap:
            drift.append(f"ready_transport_followups:{path}:{actual_gap!r}!={expected_gap!r}")

        blocked_gap = blocked_transport_gaps.get(path)
        if not isinstance(blocked_gap, str) or not blocked_gap:
            drift.append(f"blocked_transport_gaps:{path}:missing")
        elif blocked_gap != expected_gap:
            drift.append(f"blocked_transport_gaps:{path}:{blocked_gap!r}!={expected_gap!r}")

        if isinstance(actual_gap, str) and actual_gap and isinstance(blocked_gap, str) and blocked_gap and actual_gap != blocked_gap:
            drift.append(f"ready_transport_followups:{path}:{actual_gap!r}!=blocked_transport_gaps:{blocked_gap!r}")

        manifest = read_json(root, path)
        blocked = {
            gap.get("id")
            for gap in manifest.get("gaps", [])
            if gap.get("status") == "blocked_on_risky_transport" and isinstance(gap.get("id"), str)
        }
        if expected_gap not in blocked:
            drift.append(f"ready_transport_followups:{path}:{expected_gap!r}:not_blocked_on_risky_transport")

    for field, packet in LANDED_HELPER_FIELDS.items():
        path = packet["path"]
        expected_helpers = packet["expected_helpers"]
        helper_map = closure.get(field, {})
        listed = helper_map.get(path)
        if not isinstance(listed, list) or not listed:
            drift.append(f"{field}:{path}:missing")
            continue
        for helper_id in expected_helpers:
            if helper_id not in listed:
                drift.append(f"{field}:{path}:{helper_id!r}:missing_from_closure")
        for helper_id in listed:
            if helper_id not in expected_helpers:
                drift.append(f"{field}:{path}:{helper_id!r}:unexpected_in_closure")
        manifest = read_json(root, path)
        landed = {
            gap.get("id")
            for gap in manifest.get("gaps", [])
            if gap.get("status") == "starter_landed" and isinstance(gap.get("id"), str)
        }
        for helper_id in expected_helpers:
            if helper_id not in landed:
                drift.append(f"{field}:{path}:{helper_id!r}:not_starter_landed")

    tests = closure.get("tests")
    test_set = {item for item in tests if isinstance(item, str) and item} if isinstance(tests, list) else set()
    if not test_set:
        drift.append("tests:missing")

    focused = closure.get("focused_harness_replays", {})
    if not isinstance(focused, dict) or not focused:
        drift.append("focused_harness_replays:missing")
    else:
        for path in FOCUSED_HARNESS_REPLAY_FILES:
            labels = focused.get(path)
            if not isinstance(labels, list) or not labels:
                drift.append(f"focused_harness_replays:{path}:missing")
                continue
            if path not in test_set:
                drift.append(f"focused_harness_replays:{path}:not_listed_in_tests")
            for label in labels:
                if not isinstance(label, str) or not label.strip():
                    drift.append(f"focused_harness_replays:{path}:blank_label")
                    break

    return drift


def run_command(root: Path, command: list[str]) -> int:
    return subprocess.run([sys.executable, str(root / command[0]), *command[1:]], cwd=root, check=False).returncode


def run_required_commands(root: Path) -> list[str]:
    failures: list[str] = []
    for command in COMMANDS:
        if run_command(root, command) != 0:
            failures.append(" ".join(command))
    return failures


def build_manifest(lane_key: str, surveyed_commit: str, starter_ids: list[str], blocked_ids: list[str]) -> str:
    return json.dumps(
        {
            "lane_key": lane_key,
            "surveyed_commit": surveyed_commit,
            "gaps": [{"id": item, "status": "starter_landed"} for item in starter_ids]
            + [{"id": item, "status": "blocked_on_risky_transport"} for item in blocked_ids],
        }
    )


def write_fixture(root: Path) -> None:
    write_text(root / "scripts/zigux/validate-phase10-closure.py", "fixture\n")
    for rel_path in [
        "scripts/zigux/validate-phase10.py",
        "scripts/zigux/check-phase10-bootstrap-route.py",
        "scripts/zigux/check-phase10-shared-freeze-boundary.py",
        "scripts/zigux/check-phase10-ring-packet.py",
        "scripts/zigux/check-phase10-input-packet.py",
        "scripts/zigux/check-phase10-mmio-packet.py",
        "scripts/zigux/check-phase10-harness-coverage.py",
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    ]:
        write_text(
            root / rel_path,
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--self-test' in sys.argv[1:]:\n"
            "    raise SystemExit(0)\n"
            "raise SystemExit(0)\n",
        )
    for rel_path in [
        "Documentation/zigux/phase10-closure-evidence.md",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/Makefile",
    ]:
        markers = {
            "Documentation/zigux/phase10-closure-evidence.md": CLOSURE_DOC_MARKERS,
            "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": LANE_MARKERS,
            "Documentation/zigux/review-checklist.md": REVIEW_CHECKLIST_MARKERS,
            "zigux/Makefile": MAKE_MARKERS,
        }[rel_path]
        write_text(root / rel_path, "\n".join(markers) + "\n")

    write_text(
        root / ".github/workflows/zigux-bootstrap.yml",
        "name: zigux-bootstrap\n"
        "jobs:\n"
        "  bootstrap:\n"
        "    steps:\n"
        "      - name: Self-test current Phase 10 bootstrap route checker\n"
        "        run: python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test\n"
        "      - name: Check current Phase 10 bootstrap route\n"
        "        run: python3 scripts/zigux/check-phase10-bootstrap-route.py\n"
        "      - name: Validate Phase 10 checker-backed review packet\n"
        "        run: make -C zigux phase10-validate\n"
        "      - name: Run Phase 10 helper tests\n"
        "        run: make -C zigux phase10-test\n",
    )

    closure_manifest = {
        "phase": "Phase 10",
        "tranche": "virtio-lab-bundle",
        "lab_only_driver_validation": {
            "evidence": ["scripts/zigux/check-phase10-harness-coverage.py"]
        },
        "exact_checks": EXPECTED_EXACT_CHECKS,
        "survey_provenance": {
            "lane_keys": {
                "core": "P10-L01",
                "ring": "P10-L10",
                "input": "P10-L22",
                "mmio": "P10-L11",
            },
            "surveyed_commits": {
                "core": "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
                "ring": "0aa2db32bcb1c7065850ee3f66ec119b071fbf5c",
                "input": "ee789f026f11a0c5c70ded9a868979cdf4f55393",
                "mmio": "b53ec2bd507d0b3283486e76acc273b184ad5bf8",
            },
        },
        "ready_transport_followups": READY_TRANSPORT_FOLLOWUPS,
        "blocked_transport_gaps": {
            "zigux/tests/phase10_virtio_core_manifest.json": "phase10-core-probe-remove-lifecycle",
            "zigux/tests/phase10_virtio_input_manifest.json": "phase10-virtio-input-registration-lifecycle",
            "zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths",
        },
        "landed_core_helper_evidence": {
            "zigux/tests/phase10_virtio_core_manifest.json": EXPECTED_CORE_HELPERS
        },
        "landed_ring_helper_evidence": {
            "zigux/tests/phase10_virtio_ring_manifest.json": EXPECTED_RING_HELPERS
        },
        "landed_input_helper_evidence": {
            "zigux/tests/phase10_virtio_input_manifest.json": EXPECTED_INPUT_HELPERS
        },
        "landed_mmio_helper_evidence": {
            "zigux/tests/phase10_virtio_mmio_manifest.json": EXPECTED_MMIO_HELPERS
        },
        "focused_harness_replays": {
            path: [path.rsplit("/", 1)[-1].replace(".zig", " replay")]
            for path in FOCUSED_HARNESS_REPLAY_FILES
        },
        "tests": FOCUSED_HARNESS_REPLAY_FILES,
    }
    write_text(root / "zigux/tests/phase10_closure_manifest.json", json.dumps(closure_manifest))
    write_text(
        root / "zigux/tests/phase10_virtio_core_manifest.json",
        build_manifest(
            "P10-L01",
            "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
            [
                *EXPECTED_CORE_HELPERS,
            ],
            ["phase10-core-probe-remove-lifecycle"],
        ),
    )
    write_text(
        root / "zigux/tests/phase10_virtio_ring_manifest.json",
        build_manifest(
            "P10-L10",
            "0aa2db32bcb1c7065850ee3f66ec119b071fbf5c",
            [
                *EXPECTED_RING_HELPERS,
            ],
            [],
        ),
    )
    write_text(
        root / "zigux/tests/phase10_virtio_input_manifest.json",
        build_manifest(
            "P10-L22",
            "ee789f026f11a0c5c70ded9a868979cdf4f55393",
            [
                *EXPECTED_INPUT_HELPERS,
            ],
            ["phase10-virtio-input-registration-lifecycle"],
        ),
    )
    write_text(
        root / "zigux/tests/phase10_virtio_mmio_manifest.json",
        build_manifest(
            "P10-L11",
            "b53ec2bd507d0b3283486e76acc273b184ad5bf8",
            [
                *EXPECTED_MMIO_HELPERS,
            ],
            ["phase10-mmio-lifecycle-and-irq-paths"],
        ),
    )


def expect_contains(items: list[str], expected: str, label: str) -> None:
    if expected not in items:
        actual = ",".join(items) if items else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        if collect_missing_files(root) or collect_missing_markers(root) or collect_manifest_drift(root):
            raise SystemExit("phase10-closure-self-test:baseline_failed")
        if run_required_commands(root):
            raise SystemExit("phase10-closure-self-test:baseline_commands_failed")

        closure_path = root / "zigux/tests/phase10_closure_manifest.json"
        original = read_json(root, "zigux/tests/phase10_closure_manifest.json")

        def write_closure(data: dict) -> None:
            write_text(closure_path, json.dumps(data))

        def expect_command_failure(rel_path: str, expected_failure: str, error_label: str) -> None:
            path = root / rel_path
            path.write_text(
                "#!/usr/bin/env python3\n"
                "raise SystemExit(1)\n",
                encoding="utf-8",
            )
            failures = run_required_commands(root)
            if failures != [expected_failure]:
                actual = ",".join(failures) if failures else "none"
                raise SystemExit(f"{error_label}:{actual}")
            write_fixture(root)

        cases = 0

        broken = dict(original)
        broken["exact_checks"] = [item for item in original["exact_checks"] if item != EXPECTED_EXACT_CHECKS[0]]
        write_closure(broken)
        expect_contains(
            collect_manifest_drift(root),
            f"exact_checks:{EXPECTED_EXACT_CHECKS[0]!r}:missing",
            "phase10-closure-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["exact_checks"] = [item for item in original["exact_checks"] if item != EXPECTED_EXACT_CHECKS[4]]
        write_closure(broken)
        expect_contains(
            collect_manifest_drift(root),
            f"exact_checks:{EXPECTED_EXACT_CHECKS[4]!r}:missing",
            "phase10-closure-self-test",
        )
        cases += 1

        broken = dict(original)
        reordered = list(EXPECTED_EXACT_CHECKS)
        reordered[1], reordered[2] = reordered[2], reordered[1]
        broken["exact_checks"] = reordered
        write_closure(broken)
        expect_contains(
            collect_manifest_drift(root),
            "exact_checks:phase10_route:out_of_order",
            "phase10-closure-self-test",
        )
        cases += 1
        write_closure(original)

        drift_cases = [
            ("survey_provenance", "lane_keys", "core", "P10-L10", "survey_provenance:core:lane_key:'P10-L10'!='P10-L01'"),
            ("survey_provenance", "surveyed_commits", "core", "stale-core-sha", "survey_provenance:core:surveyed_commit:'stale-core-sha'!='c11221dc7a68d7511ae1c69d64b3f08528287ed8'"),
            ("survey_provenance", "lane_keys", "ring", "P10-L05", "survey_provenance:ring:lane_key:'P10-L05'!='P10-L10'"),
            ("survey_provenance", "lane_keys", "mmio", "P10-L10", "survey_provenance:mmio:lane_key:'P10-L10'!='P10-L11'"),
            ("survey_provenance", "surveyed_commits", "ring", "stale-ring-sha", "survey_provenance:ring:surveyed_commit:'stale-ring-sha'!='0aa2db32bcb1c7065850ee3f66ec119b071fbf5c'"),
        ]
        for outer, inner, key, value, expected in drift_cases:
            broken = json.loads(json.dumps(original))
            broken[outer][inner][key] = value
            write_closure(broken)
            expect_contains(collect_manifest_drift(root), expected, "phase10-closure-self-test")
            cases += 1

        broken = json.loads(json.dumps(original))
        broken["ready_transport_followups"]["zigux/tests/phase10_virtio_mmio_manifest.json"] = "phase10-mmio-config-write-helper"
        write_closure(broken)
        expect_contains(
            collect_manifest_drift(root),
            "ready_transport_followups:zigux/tests/phase10_virtio_mmio_manifest.json:'phase10-mmio-config-write-helper'!='phase10-mmio-lifecycle-and-irq-paths'",
            "phase10-closure-self-test",
        )
        expect_contains(
            collect_manifest_drift(root),
            "ready_transport_followups:zigux/tests/phase10_virtio_mmio_manifest.json:'phase10-mmio-config-write-helper'!=blocked_transport_gaps:'phase10-mmio-lifecycle-and-irq-paths'",
            "phase10-closure-self-test",
        )
        cases += 1

        broken = json.loads(json.dumps(original))
        del broken["blocked_transport_gaps"]["zigux/tests/phase10_virtio_input_manifest.json"]
        write_closure(broken)
        expect_contains(
            collect_manifest_drift(root),
            "blocked_transport_gaps:zigux/tests/phase10_virtio_input_manifest.json:missing",
            "phase10-closure-self-test",
        )
        cases += 1

        broken = json.loads(json.dumps(original))
        broken["blocked_transport_gaps"]["zigux/tests/phase10_virtio_mmio_manifest.json"] = "phase10-mmio-config-write-helper"
        write_closure(broken)
        expect_contains(
            collect_manifest_drift(root),
            "blocked_transport_gaps:zigux/tests/phase10_virtio_mmio_manifest.json:'phase10-mmio-config-write-helper'!='phase10-mmio-lifecycle-and-irq-paths'",
            "phase10-closure-self-test",
        )
        expect_contains(
            collect_manifest_drift(root),
            "ready_transport_followups:zigux/tests/phase10_virtio_mmio_manifest.json:'phase10-mmio-lifecycle-and-irq-paths'!=blocked_transport_gaps:'phase10-mmio-config-write-helper'",
            "phase10-closure-self-test",
        )
        cases += 1

        helper_cases = [
            ("landed_core_helper_evidence", "zigux/tests/phase10_virtio_core_manifest.json", "phase10-core-unexpected-helper"),
            ("landed_ring_helper_evidence", "zigux/tests/phase10_virtio_ring_manifest.json", "phase10-ring-unexpected-helper"),
            ("landed_input_helper_evidence", "zigux/tests/phase10_virtio_input_manifest.json", "phase10-input-unexpected-helper"),
        ]
        for field, path, helper_id in helper_cases:
            broken = json.loads(json.dumps(original))
            broken[field][path] = [*broken[field][path], helper_id]
            write_closure(broken)
            expect_contains(
                collect_manifest_drift(root),
                f"{field}:{path}:{helper_id!r}:unexpected_in_closure",
                "phase10-closure-self-test",
            )
            cases += 1

        exact_helper_cases = [
            (
                "landed_core_helper_evidence",
                "zigux/tests/phase10_virtio_core_manifest.json",
                "phase10-core-attribute-summary-helper",
            ),
            (
                "landed_ring_helper_evidence",
                "zigux/tests/phase10_virtio_ring_manifest.json",
                "phase10-queue-publish-readiness-helper",
            ),
            (
                "landed_mmio_helper_evidence",
                "zigux/tests/phase10_virtio_mmio_manifest.json",
                "phase10-mmio-config-write-plan-freshness-helper",
            ),
        ]
        for field, path, helper_id in exact_helper_cases:
            broken = json.loads(json.dumps(original))
            broken[field][path] = [
                item for item in broken[field][path] if item != helper_id
            ]
            write_closure(broken)
            expect_contains(
                collect_manifest_drift(root),
                f"{field}:{path}:{helper_id!r}:missing_from_closure",
                "phase10-closure-self-test",
            )
            cases += 1

        replay_cases = [
            ("drivers/virtio/virtio_ring_publish_readiness.zig", "missing"),
            ("zigux/tests/phase10_virtio_ring_notification_data_readiness.zig", "missing"),
            ("zigux/tests/phase10_virtio_core_reset_queue.zig", "missing"),
            ("zigux/tests/phase10_virtio_input_status_drain.zig", "missing"),
            ("zigux/tests/phase10_virtio_mmio_survey.zig", "missing"),
        ]
        for path, _ in replay_cases:
            broken = json.loads(json.dumps(original))
            broken["focused_harness_replays"][path] = []
            write_closure(broken)
            expect_contains(
                collect_manifest_drift(root),
                f"focused_harness_replays:{path}:missing",
                "phase10-closure-self-test",
            )
            cases += 1

        broken = json.loads(json.dumps(original))
        broken["tests"] = [item for item in original["tests"] if item != "drivers/virtio/virtio_ring_publish_readiness.zig"]
        write_closure(broken)
        expect_contains(
            collect_manifest_drift(root),
            "focused_harness_replays:drivers/virtio/virtio_ring_publish_readiness.zig:not_listed_in_tests",
            "phase10-closure-self-test",
        )
        cases += 1

        broken = json.loads(json.dumps(original))
        broken["focused_harness_replays"]["zigux/tests/phase10_virtio_input_probe_preflight.zig"] = ["   "]
        write_closure(broken)
        expect_contains(
            collect_manifest_drift(root),
            "focused_harness_replays:zigux/tests/phase10_virtio_input_probe_preflight.zig:blank_label",
            "phase10-closure-self-test",
        )
        cases += 1

        closure_doc = root / "Documentation/zigux/phase10-closure-evidence.md"
        original_doc = closure_doc.read_text(encoding="utf-8")
        closure_doc.write_text(original_doc.replace("zigux/tests/phase10_virtio_core_manifest.json", "zigux/tests/phase10_virtio_core_manifest_missing.json", 1), encoding="utf-8")
        expect_contains(collect_missing_markers(root), "closure:zigux/tests/phase10_virtio_core_manifest.json", "phase10-closure-self-test")
        cases += 1
        closure_doc.writeText = None
        closure_doc.write_text(original_doc.replace("zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig", "zigux/tests/phase10_virtio_core_interrupt_compound_ack_missing.zig", 1), encoding="utf-8")
        expect_contains(collect_missing_markers(root), "closure:zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig", "phase10-closure-self-test")
        cases += 1
        closure_doc.write_text(original_doc.replace("zigux/tests/phase10_virtio_mmio_survey.zig", "zigux/tests/phase10_virtio_mmio_survey_missing.zig", 1), encoding="utf-8")
        expect_contains(collect_missing_markers(root), "closure:zigux/tests/phase10_virtio_mmio_survey.zig", "phase10-closure-self-test")
        cases += 1
        closure_doc.write_text(original_doc.replace("Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md", "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-missing.md", 1), encoding="utf-8")
        expect_contains(collect_missing_markers(root), "closure:Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md", "phase10-closure-self-test")
        cases += 1
        closure_doc.write_text(original_doc.replace("scripts/zigux/check-phase10-shared-freeze-boundary.py", "scripts/zigux/check-phase10-shared-freeze-boundary-missing.py", 1), encoding="utf-8")
        expect_contains(collect_missing_markers(root), "closure:scripts/zigux/check-phase10-shared-freeze-boundary.py", "phase10-closure-self-test")
        cases += 1
        closure_doc.write_text(original_doc.replace("scripts/zigux/check-phase10-input-packet.py", "scripts/zigux/check-phase10-input-packet-missing.py", 1), encoding="utf-8")
        expect_contains(collect_missing_markers(root), "closure:scripts/zigux/check-phase10-input-packet.py", "phase10-closure-self-test")
        cases += 1
        closure_doc.write_text(original_doc.replace("scripts/zigux/check-phase10-mmio-packet.py", "scripts/zigux/check-phase10-mmio-packet-missing.py", 1), encoding="utf-8")
        expect_contains(collect_missing_markers(root), "closure:scripts/zigux/check-phase10-mmio-packet.py", "phase10-closure-self-test")
        cases += 1
        closure_doc.write_text(original_doc.replace("scripts/zigux/check-phase10-tests-readme-core-surfaces.py", "scripts/zigux/check-phase10-tests-readme-core-surfaces-missing.py", 1), encoding="utf-8")
        expect_contains(collect_missing_markers(root), "closure:scripts/zigux/check-phase10-tests-readme-core-surfaces.py", "phase10-closure-self-test")
        cases += 1
        closure_doc.write_text(original_doc, encoding="utf-8")

        makefile = root / "zigux/Makefile"
        makefile.write_text("", encoding="utf-8")
        expect_contains(
            collect_missing_markers(root),
            "make:PHONY += phase10-validate phase10-test phase10",
            "phase10-closure-self-test",
        )
        cases += 1
        write_fixture(root)

        expect_command_failure(
            "scripts/zigux/check-phase10-shared-freeze-boundary.py",
            "scripts/zigux/check-phase10-shared-freeze-boundary.py",
            "phase10-closure-self-test:failed_shared_freeze_command_not_detected",
        )
        cases += 1
        expect_command_failure(
            "scripts/zigux/check-phase10-ring-packet.py",
            "scripts/zigux/check-phase10-ring-packet.py",
            "phase10-closure-self-test:failed_ring_command_not_detected",
        )
        cases += 1
        expect_command_failure(
            "scripts/zigux/check-phase10-input-packet.py",
            "scripts/zigux/check-phase10-input-packet.py",
            "phase10-closure-self-test:failed_input_command_not_detected",
        )
        cases += 1
        expect_command_failure(
            "scripts/zigux/check-phase10-mmio-packet.py",
            "scripts/zigux/check-phase10-mmio-packet.py",
            "phase10-closure-self-test:failed_mmio_command_not_detected",
        )
        cases += 1
        expect_command_failure(
            "scripts/zigux/check-phase10-harness-coverage.py",
            "scripts/zigux/check-phase10-harness-coverage.py",
            "phase10-closure-self-test:failed_harness_command_not_detected",
        )
        cases += 1
        expect_command_failure(
            "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
            "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
            "phase10-closure-self-test:failed_tests_readme_command_not_detected",
        )
        cases += 1
        expect_command_failure(
            "scripts/zigux/validate-phase10.py",
            "scripts/zigux/validate-phase10.py --self-test",
            "phase10-closure-self-test:failed_phase10_validate_self_test_not_detected",
        )
        cases += 1

    print("PHASE10_CLOSURE_VALIDATION_SELF_TEST=pass")
    print(f"PHASE10_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={cases}")
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
        print("MISSING_PHASE10_CLOSURE_DRIFT_START")
        for item in manifest_drift:
            print(item)
        print("MISSING_PHASE10_CLOSURE_DRIFT_END")
        return 1

    command_failures = run_required_commands(ROOT)
    if command_failures:
        print("PHASE10_CLOSURE_VALIDATION=fail")
        print("PHASE10_CLOSURE_REQUIRED_COMMAND_FAILURES_START")
        for item in command_failures:
            print(item)
        print("PHASE10_CLOSURE_REQUIRED_COMMAND_FAILURES_END")
        return 1

    print("PHASE10_CLOSURE_VALIDATION=pass")
    print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE10_CLOSURE_DOC_MARKER_COUNT={len(CLOSURE_DOC_MARKERS)}")
    print(f"PHASE10_CLOSURE_EXACT_CHECK_COUNT={len(EXPECTED_EXACT_CHECKS)}")
    print(f"PHASE10_CLOSURE_FOCUSED_REPLAY_COUNT={len(FOCUSED_HARNESS_REPLAY_FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
