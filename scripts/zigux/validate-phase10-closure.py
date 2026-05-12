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

TRANSPORT_MANIFEST_FILES = [
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
]

REQUIRED_FILES = [
    "scripts/zigux/validate-phase10-closure.py",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase10-harness-coverage.py",
    "scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "zigux/Makefile",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    *TRANSPORT_MANIFEST_FILES,
]

MAKE_MARKERS = [
    "PHONY += phase10-validate phase10-test phase10",
    "phase10-validate:",
    "scripts/zigux/validate-phase10.py",
    "scripts/zigux/validate-phase10-closure.py",
    "phase10: phase10-validate phase10-test",
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
    '"source": "manifest_derived"',
    '"surveyed_commits": {',
    '"core": "c11221dc7a68d7511ae1c69d64b3f08528287ed8"',
    '"ring": "bdfe88e865b94387b3c3bd41ca98054c452f78b9"',
    '"input": "7361ac51374149a96b7a7a2c6ea3c995d8cc1231"',
    '"mmio": "84f90e23ad1c28ae345905d5293a8c5395f37d43"',
    '"phase10-notification-data-summary-helper"',
    '"phase10-mmio-config-write-disposition-helper"',
    '"phase10-mmio-selected-queue-readiness-helper"',
    '"zigux/tests/phase10_virtio_mmio_manifest.json": "phase10-mmio-lifecycle-and-irq-paths"',
]

MMIO_SURVEY_MARKERS = [
    "phase10-mmio-config-write-disposition-helper",
    "phase10-mmio-selected-queue-readiness-helper",
    "phase10-mmio-lifecycle-and-irq-paths",
    "the live packet-local manifest `zigux/tests/phase10_virtio_mmio_manifest.json`",
    "the live dedicated MMIO freeze-boundary checker `scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
    "This survey stays aligned with `Documentation/zigux/freeze-map.md` and the shared Phase 10 closure packet.",
    "Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates.",
    "Allowed roadmap destinations remain `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` support surfaces; this note does not widen the tranche into new transport homes.",
    "Forbidden transport claims remain queue setup or reset paths, IRQ parity, DMA paths, input registration lifecycle, and probe/remove lifecycle behavior.",
    "The Phase 14 study-only anchors `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain outside this lane, and this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.",
]

TRANSPORT_MANIFEST_MARKERS = [
    '"freeze_map": "Documentation/zigux/freeze-map.md"',
    '"freeze_boundary_status": "aligned"',
    '"freeze_status_change_claimed": false',
    '"risky_transport_posture": "blocked_on_risky_transport"',
    '"allowed_evidence_kinds": [',
    '"driver_local_lab_slices"',
    '"survey_manifests"',
    '"shared_validation_gates"',
    '"forbidden_transport_claims": [',
    '"queue_setup_reset_paths"',
    '"irq_parity"',
    '"dma_paths"',
    '"input_registration_lifecycle"',
    '"probe_remove_lifecycle"',
    '"architecture_council_reopen_required": true',
    '"architecture_council_reopen_attached": false',
]

MARKER_SETS = {
    "zigux/Makefile": MAKE_MARKERS,
    "Documentation/zigux/phase10-closure-evidence.md": CLOSURE_DOC_MARKERS,
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": LANE_MARKERS,
    "Documentation/zigux/phase10-virtio-mmio-survey.md": MMIO_SURVEY_MARKERS,
    "Documentation/zigux/review-checklist.md": REVIEW_CHECKLIST_MARKERS,
    "zigux/tests/phase10_closure_manifest.json": MANIFEST_MARKERS,
    "zigux/tests/phase10_virtio_ring_manifest.json": TRANSPORT_MANIFEST_MARKERS,
    "zigux/tests/phase10_virtio_input_manifest.json": TRANSPORT_MANIFEST_MARKERS,
    "zigux/tests/phase10_virtio_mmio_manifest.json": TRANSPORT_MANIFEST_MARKERS,
}

MARKER_LABELS = {
    "zigux/Makefile": "make",
    "Documentation/zigux/phase10-closure-evidence.md": "closure",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": "lane",
    "Documentation/zigux/phase10-virtio-mmio-survey.md": "mmio-survey",
    "Documentation/zigux/review-checklist.md": "review",
    "zigux/tests/phase10_closure_manifest.json": "manifest",
    "zigux/tests/phase10_virtio_ring_manifest.json": "ring-manifest",
    "zigux/tests/phase10_virtio_input_manifest.json": "input-manifest",
    "zigux/tests/phase10_virtio_mmio_manifest.json": "mmio-manifest",
}

LEDGER_EXACT_ONCE_MARKERS = [
    "PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/validate-phase10.py",
    "PHASE10_LEDGER_EXACT_CHECK_2=python3 scripts/zigux/validate-phase10-closure.py",
    "PHASE10_LEDGER_EXACT_CHECK_3=make -C zigux phase10-validate",
    "PHASE10_LEDGER_EXACT_CHECK_4=python3 scripts/zigux/check-phase10-core-packet.py",
    "PHASE10_LEDGER_EXACT_CHECK_5=python3 scripts/zigux/check-phase10-ring-packet.py",
    "PHASE10_LEDGER_EXACT_CHECK_6=python3 scripts/zigux/check-phase10-input-packet.py",
    "PHASE10_LEDGER_EXACT_CHECK_7=python3 scripts/zigux/check-phase10-mmio-packet.py",
    "PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py",
    "PHASE10_LEDGER_EXACT_CHECK_9=python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test",
    "PHASE10_LEDGER_EXACT_CHECK_10=python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "PHASE10_LEDGER_EXACT_CHECK_11=python3 scripts/zigux/check-phase10-harness-coverage.py --self-test",
    "PHASE10_LEDGER_EXACT_CHECK_12=python3 scripts/zigux/check-phase10-harness-coverage.py",
    "PHASE10_LEDGER_EXACT_CHECK_13=zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "PHASE10_LEDGER_EXACT_CHECK_14=make -C zigux phase10-test",
    "PHASE10_LEDGER_EXACT_CHECK_15=make -C zigux phase10",
]

LEDGER_EXACT_ONCE_ERROR = (
    "PHASE10_CLOSURE_VALIDATION_LEDGER_EXACT_CHECKS=fail\n"
    "PHASE10_CLOSURE_LEDGER_EXACT_ONCE_MISMATCH_START\n"
    "{details}\n"
    "PHASE10_CLOSURE_LEDGER_EXACT_ONCE_MISMATCH_END"
)

LEDGER_MIRROR_ERROR = (
    "PHASE10_CLOSURE_VALIDATION_LEDGER_MIRRORS=fail\n"
    "PHASE10_CLOSURE_LEDGER_MIRROR_MISMATCH_START\n"
    "{details}\n"
    "PHASE10_CLOSURE_LEDGER_MIRROR_MISMATCH_END"
)

MANIFEST_PROVENANCE_ERROR = (
    "PHASE10_CLOSURE_VALIDATION_MANIFEST_PROVENANCE=fail\n"
    "PHASE10_CLOSURE_MANIFEST_PROVENANCE_MISMATCH_START\n"
    "{details}\n"
    "PHASE10_CLOSURE_MANIFEST_PROVENANCE_MISMATCH_END"
)

LEDGER_LANE_MAP = {
    "core": "PHASE10_LEDGER_SURVEY_CORE_LANE",
    "ring": "PHASE10_LEDGER_SURVEY_RING_LANE",
    "input": "PHASE10_LEDGER_SURVEY_INPUT_LANE",
    "mmio": "PHASE10_LEDGER_SURVEY_MMIO_LANE",
}

LEDGER_COMMIT_MAP = {
    "core": "PHASE10_LEDGER_SURVEY_CORE_COMMIT",
    "ring": "PHASE10_LEDGER_SURVEY_RING_COMMIT",
    "input": "PHASE10_LEDGER_SURVEY_INPUT_COMMIT",
    "mmio": "PHASE10_LEDGER_SURVEY_MMIO_COMMIT",
}

LEDGER_SCOREBOARD_STATUS_MAP = {
    "virtqueue_wrappers": "PHASE10_LEDGER_ROADMAP_VIRTQUEUE_WRAPPERS",
    "mmio_wrappers": "PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS",
    "lab_only_driver_validation": "PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION",
    "dual_implementations_for_risky_areas": "PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS",
}

COMMANDS = [
    ["scripts/zigux/check-phase10-harness-coverage.py", "--self-test"],
    ["scripts/zigux/check-phase10-tests-readme-core-surfaces.py", "--self-test"],
    ["scripts/zigux/check-phase10-harness-coverage.py"],
    ["scripts/zigux/check-phase10-tests-readme-core-surfaces.py"],
]

EXPECTED_SURVEY_PROVENANCE_SOURCE = "manifest_derived"

EXPECTED_SURVEY_LANE_KEYS = {
    "core": "P10-L01",
    "ring": "P10-L07",
    "input": "P10-L13",
    "mmio": "P10-L10",
}

EXPECTED_SURVEYED_COMMITS = {
    "core": "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
    "ring": "bdfe88e865b94387b3c3bd41ca98054c452f78b9",
    "input": "7361ac51374149a96b7a7a2c6ea3c995d8cc1231",
    "mmio": "84f90e23ad1c28ae345905d5293a8c5395f37d43",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def read_manifest(root: Path) -> dict:
    return json.loads(read_text(root, "zigux/tests/phase10_closure_manifest.json"))


def collect_missing_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel_path, markers in MARKER_SETS.items():
        label = MARKER_LABELS[rel_path]
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing.append(f"{label}:{marker}")
    return missing


def collect_manifest_provenance_mismatches(root: Path) -> list[str]:
    manifest = read_manifest(root)
    provenance = manifest.get("survey_provenance", {})
    mismatches: list[str] = []

    if provenance.get("source") != EXPECTED_SURVEY_PROVENANCE_SOURCE:
        mismatches.append(f"survey_provenance.source={provenance.get('source')}")

    lane_keys = provenance.get("lane_keys", {})
    for key, expected in EXPECTED_SURVEY_LANE_KEYS.items():
        actual = lane_keys.get(key)
        if actual != expected:
            mismatches.append(f"survey_provenance.lane_keys.{key}={actual}")
    for key in sorted(set(lane_keys) - set(EXPECTED_SURVEY_LANE_KEYS)):
        mismatches.append(f"survey_provenance.lane_keys.extra.{key}={lane_keys[key]}")

    surveyed_commits = provenance.get("surveyed_commits", {})
    for key, expected in EXPECTED_SURVEYED_COMMITS.items():
        actual = surveyed_commits.get(key)
        if actual != expected:
            mismatches.append(f"survey_provenance.surveyed_commits.{key}={actual}")
    for key in sorted(set(surveyed_commits) - set(EXPECTED_SURVEYED_COMMITS)):
        mismatches.append(
            f"survey_provenance.surveyed_commits.extra.{key}={surveyed_commits[key]}"
        )

    return mismatches


def build_ledger_mirror_markers(root: Path) -> list[str]:
    manifest = read_manifest(root)
    scoreboard = manifest["roadmap_parity_scoreboard"]
    provenance = manifest["survey_provenance"]
    markers = [
        "PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE=zigux/tests/phase10_closure_manifest.json",
        f"PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE={provenance['source']}",
    ]
    for key, label in LEDGER_LANE_MAP.items():
        markers.append(f"{label}={provenance['lane_keys'][key]}")
    for key, label in LEDGER_COMMIT_MAP.items():
        markers.append(f"{label}={provenance['surveyed_commits'][key]}")
    for key, label in LEDGER_SCOREBOARD_STATUS_MAP.items():
        markers.append(f"{label}={scoreboard[key]['status']}")
    return markers


def collect_ledger_mirror_mismatches(root: Path) -> list[str]:
    ledger_lines = set(read_text(root, "zigux-alpha/PHASE10_CLOSURE_LEDGER.md").splitlines())
    mismatches: list[str] = []
    for marker in build_ledger_mirror_markers(root):
        if marker not in ledger_lines:
            mismatches.append(marker)
    return mismatches


def collect_ledger_exact_once_mismatches(root: Path) -> list[str]:
    ledger_text = read_text(root, "zigux-alpha/PHASE10_CLOSURE_LEDGER.md")
    mismatches: list[str] = []
    for marker in LEDGER_EXACT_ONCE_MARKERS:
        count = ledger_text.count(marker)
        if count != 1:
            mismatches.append(f"{marker}:count={count}")
    return mismatches


def run_command(root: Path, cmd: list[str]) -> int:
    return subprocess.run(
        [sys.executable, str(root / cmd[0]), *cmd[1:]],
        cwd=root,
        check=False,
    ).returncode


def run_required_commands(root: Path) -> list[str]:
    failed: list[str] = []
    for command in COMMANDS:
        if run_command(root, command) != 0:
            failed.append(" ".join(command))
    return failed


def build_fixture_manifest_text() -> str:
    return """{
  \"phase\": \"Phase 10\",
  \"status\": \"active\",
  \"tranche\": \"virtio-lab-bundle\",
  \"roadmap_parity_scoreboard\": {
    \"virtqueue_wrappers\": {
      \"status\": \"starter_landed\"
    },
    \"mmio_wrappers\": {
      \"status\": \"starter_landed\"
    },
    \"lab_only_driver_validation\": {
      \"status\": \"starter_landed\"
    },
    \"dual_implementations_for_risky_areas\": {
      \"status\": \"blocked_on_risky_transport\"
    }
  },
  \"survey_provenance\": {
    \"source\": \"manifest_derived\",
    \"lane_keys\": {
      \"core\": \"P10-L01\",
      \"ring\": \"P10-L07\",
      \"input\": \"P10-L13\",
      \"mmio\": \"P10-L10\"
    },
    \"surveyed_commits\": {
      \"core\": \"c11221dc7a68d7511ae1c69d64b3f08528287ed8\",
      \"ring\": \"bdfe88e865b94387b3c3bd41ca98054c452f78b9\",
      \"input\": \"7361ac51374149a96b7a7a2c6ea3c995d8cc1231\",
      \"mmio\": \"84f90e23ad1c28ae345905d5293a8c5395f37d43\"
    }
  },
  \"focused_harness_replays\": {
    \"zigux/tests/phase10_virtio_core_reset_queue.zig\": [
      \"phase10 core reset-queue replay\"
    ]
  },
  \"exact_checks\": [
    \"scripts/zigux/check-phase10-harness-coverage.py\"
  ],
  \"ready_transport_followups\": {
    \"zigux/tests/phase10_virtio_mmio_manifest.json\": \"phase10-mmio-lifecycle-and-irq-paths\"
  },
  \"landed_ring_helper_evidence\": {
    \"zigux/tests/phase10_virtio_ring_manifest.json\": [
      \"phase10-notification-data-summary-helper\"
    ]
  },
  \"landed_mmio_helper_evidence\": {
    \"zigux/tests/phase10_virtio_mmio_manifest.json\": [
      \"phase10-mmio-config-write-disposition-helper\",
      \"phase10-mmio-selected-queue-readiness-helper\"
    ]
  }
}
"""


def build_fixture_ledger_text(root: Path) -> str:
    return "\n".join(build_ledger_mirror_markers(root) + LEDGER_EXACT_ONCE_MARKERS) + "\n"


def write_fixture(root: Path) -> None:
    transport_manifest_body = "\n".join(TRANSPORT_MANIFEST_MARKERS) + "\n"
    files = {
        "scripts/zigux/validate-phase10-closure.py": "fixture\n",
        "Documentation/zigux/phase10-closure-evidence.md": "\n".join(CLOSURE_DOC_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": "\n".join(LANE_MARKERS) + "\n",
        "Documentation/zigux/phase10-virtio-mmio-survey.md": "\n".join(MMIO_SURVEY_MARKERS) + "\n",
        "Documentation/zigux/review-checklist.md": "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
        "scripts/zigux/check-phase10-harness-coverage.py": (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--self-test' in sys.argv[1:]:\n"
            "    print('PHASE10_HARNESS_COVERAGE_SELF_TEST=pass')\n"
            "    raise SystemExit(0)\n"
            "print('PHASE10_HARNESS_COVERAGE=pass')\n"
        ),
        "scripts/zigux/check-phase10-tests-readme-core-surfaces.py": (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--self-test' in sys.argv[1:]:\n"
            "    print('PHASE10_TESTS_README_CORE_SURFACES_CHECKER_SELF_TEST=pass')\n"
            "    raise SystemExit(0)\n"
            "print('PHASE10_TESTS_README_CORE_SURFACES_CHECK=pass')\n"
        ),
        "zigux/Makefile": "\n".join(MAKE_MARKERS) + "\n",
        "zigux/tests/phase10_closure_manifest.json": build_fixture_manifest_text(),
        "zigux/tests/phase10_virtio_ring_manifest.json": transport_manifest_body,
        "zigux/tests/phase10_virtio_input_manifest.json": transport_manifest_body,
        "zigux/tests/phase10_virtio_mmio_manifest.json": transport_manifest_body,
    }
    for rel_path, content in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    ledger_path = root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(build_fixture_ledger_text(root), encoding="utf-8")


def expect_marker_missing(root: Path, expected: str, error_label: str) -> None:
    if expected not in collect_missing_markers(root):
        raise SystemExit(error_label)


def expect_manifest_provenance_mismatch(root: Path, expected: str, error_label: str) -> None:
    mismatches = collect_manifest_provenance_mismatches(root)
    if expected not in mismatches:
        actual = ",".join(mismatches) if mismatches else "none"
        raise SystemExit(f"{error_label}:actual={actual}")


def expect_failed_commands(root: Path, expected: list[str], error_label: str) -> None:
    failed_commands = run_required_commands(root)
    if failed_commands != expected:
        actual = ",".join(failed_commands) if failed_commands else "none"
        raise SystemExit(f"{error_label}:actual={actual}")


def expect_ledger_mirror_mismatch(root: Path, expected: str, error_label: str) -> None:
    mismatches = collect_ledger_mirror_mismatches(root)
    if expected not in mismatches:
        actual = ",".join(mismatches) if mismatches else "none"
        raise SystemExit(f"{error_label}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_closure_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files = collect_missing_files(root)
        missing_markers = collect_missing_markers(root)
        manifest_provenance_mismatches = collect_manifest_provenance_mismatches(root)
        ledger_mismatches = collect_ledger_exact_once_mismatches(root)
        ledger_mirror_mismatches = collect_ledger_mirror_mismatches(root)
        if (
            missing_files
            or missing_markers
            or manifest_provenance_mismatches
            or ledger_mismatches
            or ledger_mirror_mismatches
        ):
            raise SystemExit(
                "phase10-closure-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}:"
                f"manifest_provenance={','.join(manifest_provenance_mismatches) if manifest_provenance_mismatches else 'none'}:"
                f"ledger={','.join(ledger_mismatches) if ledger_mismatches else 'none'}:"
                f"ledger_mirrors={','.join(ledger_mirror_mismatches) if ledger_mirror_mismatches else 'none'}"
            )
        expect_failed_commands(root, [], "phase10-closure-self-test:baseline_command_failed")

        makefile = root / "zigux/Makefile"
        makefile.write_text(
            makefile.read_text(encoding="utf-8").replace("phase10-validate:\n", "", 1),
            encoding="utf-8",
        )
        expect_marker_missing(root, "make:phase10-validate:", "phase10-closure-self-test:missing_make_marker_not_detected")
        write_fixture(root)

        closure = root / "Documentation/zigux/phase10-closure-evidence.md"
        closure.write_text(
            closure.read_text(encoding="utf-8").replace("shared reminder-surface drift\n", "", 1),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            "closure:shared reminder-surface drift",
            "phase10-closure-self-test:missing_closure_marker_not_detected",
        )
        write_fixture(root)

        lane = root / "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md"
        lane.write_text(
            lane.read_text(encoding="utf-8").replace("scripts/zigux/validate-phase10-closure.py\n", "", 1),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            "lane:scripts/zigux/validate-phase10-closure.py",
            "phase10-closure-self-test:missing_lane_marker_not_detected",
        )
        write_fixture(root)

        mmio_survey = root / "Documentation/zigux/phase10-virtio-mmio-survey.md"
        mmio_survey.write_text(
            mmio_survey.read_text(encoding="utf-8").replace("phase10-mmio-config-write-disposition-helper\n", "", 1),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            "mmio-survey:phase10-mmio-config-write-disposition-helper",
            "phase10-closure-self-test:mmio_survey_config_write_disposition_marker_not_detected",
        )
        write_fixture(root)

        mmio_survey.write_text(
            mmio_survey.read_text(encoding="utf-8").replace("phase10-mmio-selected-queue-readiness-helper\n", "", 1),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            "mmio-survey:phase10-mmio-selected-queue-readiness-helper",
            "phase10-closure-self-test:mmio_survey_marker_not_detected",
        )
        write_fixture(root)

        mmio_survey.write_text(
            mmio_survey.read_text(encoding="utf-8").replace(
                "the live packet-local manifest `zigux/tests/phase10_virtio_mmio_manifest.json`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            "mmio-survey:the live packet-local manifest `zigux/tests/phase10_virtio_mmio_manifest.json`",
            "phase10-closure-self-test:mmio_survey_manifest_marker_not_detected",
        )
        write_fixture(root)

        mmio_survey.write_text(
            mmio_survey.read_text(encoding="utf-8").replace(
                "the live dedicated MMIO freeze-boundary checker `scripts/zigux/check-phase10-mmio-freeze-boundary.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            "mmio-survey:the live dedicated MMIO freeze-boundary checker `scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
            "phase10-closure-self-test:mmio_survey_freeze_boundary_marker_not_detected",
        )
        write_fixture(root)

        mmio_survey.write_text(
            mmio_survey.read_text(encoding="utf-8").replace(
                "This survey stays aligned with `Documentation/zigux/freeze-map.md` and the shared Phase 10 closure packet.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            "mmio-survey:This survey stays aligned with `Documentation/zigux/freeze-map.md` and the shared Phase 10 closure packet.",
            "phase10-closure-self-test:mmio_survey_freeze_map_alignment_not_detected",
        )
        write_fixture(root)

        mmio_survey.write_text(
            mmio_survey.read_text(encoding="utf-8").replace(
                "Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            "mmio-survey:Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates.",
            "phase10-closure-self-test:mmio_survey_allowed_evidence_not_detected",
        )
        write_fixture(root)

        mmio_survey.write_text(
            mmio_survey.read_text(encoding="utf-8").replace(
                "Allowed roadmap destinations remain `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` support surfaces; this note does not widen the tranche into new transport homes.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            "mmio-survey:Allowed roadmap destinations remain `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` support surfaces; this note does not widen the tranche into new transport homes.",
            "phase10-closure-self-test:mmio_survey_allowed_destinations_not_detected",
        )
        write_fixture(root)

        mmio_survey.write_text(
            mmio_survey.read_text(encoding="utf-8").replace(
                "Forbidden transport claims remain queue setup or reset paths, IRQ parity, DMA paths, input registration lifecycle, and probe/remove lifecycle behavior.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            "mmio-survey:Forbidden transport claims remain queue setup or reset paths, IRQ parity, DMA paths, input registration lifecycle, and probe/remove lifecycle behavior.",
            "phase10-closure-self-test:mmio_survey_forbidden_transport_not_detected",
        )
        write_fixture(root)

        mmio_survey.write_text(
            mmio_survey.read_text(encoding="utf-8").replace(
                "The Phase 14 study-only anchors `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain outside this lane, and this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            "mmio-survey:The Phase 14 study-only anchors `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain outside this lane, and this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.",
            "phase10-closure-self-test:mmio_survey_phase14_boundary_not_detected",
        )
        write_fixture(root)

        review = root / "Documentation/zigux/review-checklist.md"
        review.write_text(
            review.read_text(encoding="utf-8").replace("zigux/tests/phase10_closure_manifest.json\n", "", 1),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            "review:zigux/tests/phase10_closure_manifest.json",
            "phase10-closure-self-test:missing_review_marker_not_detected",
        )
        write_fixture(root)

        closure_manifest = root / "zigux/tests/phase10_closure_manifest.json"
        closure_manifest.write_text(
            closure_manifest.read_text(encoding="utf-8").replace(
                '"scripts/zigux/check-phase10-harness-coverage.py"',
                '"scripts/zigux/check-phase10-harness-coverage.py-missing"',
                1,
            ),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            'manifest:"scripts/zigux/check-phase10-harness-coverage.py"',
            "phase10-closure-self-test:missing_manifest_marker_not_detected",
        )
        write_fixture(root)

        closure_manifest.write_text(
            closure_manifest.read_text(encoding="utf-8").replace(
                '"phase10-mmio-config-write-disposition-helper"',
                '"phase10-mmio-config-write-disposition-helper-missing"',
                1,
            ),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            'manifest:"phase10-mmio-config-write-disposition-helper"',
            "phase10-closure-self-test:missing_manifest_mmio_disposition_marker_not_detected",
        )
        write_fixture(root)

        closure_manifest.write_text(
            closure_manifest.read_text(encoding="utf-8").replace(
                '"input": "P10-L13"',
                '"input": "P10-Y05"',
                1,
            ),
            encoding="utf-8",
        )
        expect_manifest_provenance_mismatch(
            root,
            "survey_provenance.lane_keys.input=P10-Y05",
            "phase10-closure-self-test:manifest_lane_key_mismatch_not_detected",
        )
        write_fixture(root)

        closure_manifest.write_text(
            closure_manifest.read_text(encoding="utf-8").replace(
                '"core": "c11221dc7a68d7511ae1c69d64b3f08528287ed8"',
                '"core": "0000000000000000000000000000000000000000"',
                1,
            ),
            encoding="utf-8",
        )
        expect_manifest_provenance_mismatch(
            root,
            "survey_provenance.surveyed_commits.core=0000000000000000000000000000000000000000",
            "phase10-closure-self-test:manifest_commit_mismatch_not_detected",
        )
        write_fixture(root)

        ledger = root / "zigux-alpha/PHASE10_CLOSURE_LEDGER.md"
        ledger.write_text(
            ledger.read_text(encoding="utf-8").replace(
                "PHASE10_LEDGER_EXACT_CHECK_4=python3 scripts/zigux/check-phase10-core-packet.py\n",
                "PHASE10_LEDGER_EXACT_CHECK_3=python3 scripts/zigux/check-phase10-core-packet.py\n",
                1,
            ),
            encoding="utf-8",
        )
        ledger_mismatches = collect_ledger_exact_once_mismatches(root)
        if "PHASE10_LEDGER_EXACT_CHECK_4=python3 scripts/zigux/check-phase10-core-packet.py:count=0" not in ledger_mismatches:
            actual = ",".join(ledger_mismatches) if ledger_mismatches else "none"
            raise SystemExit(
                "phase10-closure-self-test:missing_ledger_exact_once_mismatch_not_detected:"
                f"actual={actual}"
            )
        write_fixture(root)

        ledger.write_text(
            ledger.read_text(encoding="utf-8").replace(
                "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_ledger_mirror_mismatch(
            root,
            "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
            "phase10-closure-self-test:missing_ledger_source_mismatch_not_detected",
        )
        write_fixture(root)

        ledger.write_text(
            ledger.read_text(encoding="utf-8").replace(
                "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L13\n",
                "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-Y05\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_ledger_mirror_mismatch(
            root,
            "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L13",
            "phase10-closure-self-test:missing_ledger_lane_mismatch_not_detected",
        )
        write_fixture(root)

        ledger.write_text(
            ledger.read_text(encoding="utf-8").replace(
                "PHASE10_LEDGER_SURVEY_CORE_COMMIT=c11221dc7a68d7511ae1c69d64b3f08528287ed8\n",
                "PHASE10_LEDGER_SURVEY_CORE_COMMIT=0000000000000000000000000000000000000000\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_ledger_mirror_mismatch(
            root,
            "PHASE10_LEDGER_SURVEY_CORE_COMMIT=c11221dc7a68d7511ae1c69d64b3f08528287ed8",
            "phase10-closure-self-test:missing_ledger_commit_mismatch_not_detected",
        )
        write_fixture(root)

        ledger.write_text(
            ledger.read_text(encoding="utf-8").replace(
                "PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS=starter_landed\n",
                "PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS=blocked_on_risky_transport\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_ledger_mirror_mismatch(
            root,
            "PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS=starter_landed",
            "phase10-closure-self-test:missing_ledger_scoreboard_status_mismatch_not_detected",
        )
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
        expect_failed_commands(
            root,
            ["scripts/zigux/check-phase10-harness-coverage.py"],
            "phase10-closure-self-test:failed_command_not_detected",
        )
        write_fixture(root)

        tests_readme_checker = root / "scripts/zigux/check-phase10-tests-readme-core-surfaces.py"
        tests_readme_checker.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--self-test' in sys.argv[1:]:\n"
            "    print('PHASE10_TESTS_README_CORE_SURFACES_CHECKER_SELF_TEST=pass')\n"
            "    raise SystemExit(0)\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
        )
        expect_failed_commands(
            root,
            ["scripts/zigux/check-phase10-tests-readme-core-surfaces.py"],
            "phase10-closure-self-test:tests_readme_checker_failure_not_detected",
        )
        write_fixture(root)

        ring_manifest = root / "zigux/tests/phase10_virtio_ring_manifest.json"
        ring_manifest.write_text(
            ring_manifest.read_text(encoding="utf-8").replace('"freeze_boundary_status": "aligned"', "", 1),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            'ring-manifest:"freeze_boundary_status": "aligned"',
            "phase10-closure-self-test:ring_manifest_freeze_status_not_detected",
        )
        write_fixture(root)

        input_manifest = root / "zigux/tests/phase10_virtio_input_manifest.json"
        input_manifest.write_text(
            input_manifest.read_text(encoding="utf-8").replace(
                '"risky_transport_posture": "blocked_on_risky_transport"',
                '"risky_transport_posture": "starter_landed"',
                1,
            ),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            'input-manifest:"risky_transport_posture": "blocked_on_risky_transport"',
            "phase10-closure-self-test:input_manifest_risky_transport_not_detected",
        )
        write_fixture(root)

        mmio_manifest = root / "zigux/tests/phase10_virtio_mmio_manifest.json"
        mmio_manifest.write_text(
            mmio_manifest.read_text(encoding="utf-8").replace('"dma_paths"', "", 1),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            'mmio-manifest:"dma_paths"',
            "phase10-closure-self-test:mmio_manifest_dma_guard_not_detected",
        )
        write_fixture(root)

        ring_manifest.write_text(
            ring_manifest.read_text(encoding="utf-8").replace(
                '"architecture_council_reopen_attached": false',
                '"architecture_council_reopen_attached": true',
                1,
            ),
            encoding="utf-8",
        )
        expect_marker_missing(
            root,
            'ring-manifest:"architecture_council_reopen_attached": false',
            "phase10-closure-self-test:ring_manifest_reopen_attachment_not_detected",
        )

    print("PHASE10_CLOSURE_VALIDATION_SELF_TEST=pass")
    print("PHASE10_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT=30")
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

    manifest_provenance_mismatches = collect_manifest_provenance_mismatches(ROOT)
    if manifest_provenance_mismatches:
        print(MANIFEST_PROVENANCE_ERROR.format(details="\n".join(manifest_provenance_mismatches)))
        return 1

    ledger_mirror_mismatches = collect_ledger_mirror_mismatches(ROOT)
    if ledger_mirror_mismatches:
        print(LEDGER_MIRROR_ERROR.format(details="\n".join(ledger_mirror_mismatches)))
        return 1

    ledger_mismatches = collect_ledger_exact_once_mismatches(ROOT)
    if ledger_mismatches:
        print(LEDGER_EXACT_ONCE_ERROR.format(details="\n".join(ledger_mismatches)))
        return 1

    failed_commands = run_required_commands(ROOT)
    if failed_commands:
        print("PHASE10_CLOSURE_VALIDATION=fail")
        print("PHASE10_CLOSURE_VALIDATION_FAILED_COMMANDS_START")
        for command in failed_commands:
            print(command)
        print("PHASE10_CLOSURE_VALIDATION_FAILED_COMMANDS_END")
        return 1

    marker_count = (
        sum(len(markers) for markers in MARKER_SETS.values())
        + len(LEDGER_EXACT_ONCE_MARKERS)
        + len(build_ledger_mirror_markers(ROOT))
        + 1
        + len(EXPECTED_SURVEY_LANE_KEYS)
        + len(EXPECTED_SURVEYED_COMMITS)
    )
    print("PHASE10_CLOSURE_VALIDATION=pass")
    print(f"PHASE10_CLOSURE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE10_CLOSURE_REQUIRED_MARKER_COUNT={marker_count}")
    print(f"PHASE10_CLOSURE_COMMAND_COUNT={len(COMMANDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
