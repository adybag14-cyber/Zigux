#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

FREEZE_BOUNDARY_CHECK = "python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py"

FILES = [
    "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
    "scripts/zigux/check-phase10-mmio-packet.py",
    "scripts/zigux/validate-phase10-closure.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
]

TEXT_MARKERS = {
    "scripts/zigux/check-phase10-mmio-freeze-boundary.py": [
        f'FREEZE_BOUNDARY_CHECK = "{FREEZE_BOUNDARY_CHECK}"',
        '"phase10-mmio-lifecycle-and-irq-paths"',
        '"Documentation/zigux/freeze-map.md"',
        '"blocked_on_risky_transport"',
    ],
    "scripts/zigux/check-phase10-mmio-packet.py": [
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
        "phase10-mmio-lifecycle-and-irq-paths",
        "closure_manifest:exact_checks:freeze_boundary_count",
    ],
    "scripts/zigux/validate-phase10-closure.py": [
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
        "PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py",
        "Documentation/zigux/phase10-virtio-mmio-survey.md",
    ],
    "scripts/zigux/README.md": [
        "check-phase10-mmio-freeze-boundary.py",
        "check-phase10-mmio-packet.py",
        "make -C zigux phase10-validate",
        "phase10_virtio_mmio_manifest.json",
    ],
    "Documentation/zigux/README.md": [
        "`Documentation/zigux/freeze-map.md`",
        "`scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
        "`zigux/tests/phase10_virtio_mmio_manifest.json`",
        "`make -C zigux phase10-validate`",
    ],
    "Documentation/zigux/review-checklist.md": [
        "`Documentation/zigux/freeze-map.md`",
        "`scripts/zigux/check-phase10-mmio-packet.py`",
        "`scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
        "`zigux/tests/phase10_virtio_mmio_manifest.json`",
    ],
    "Documentation/zigux/freeze-map.md": [
        "`kernel/workqueue.c`",
        "`kernel/trace/ring_buffer.c`",
        "freeze-map status-change requests must route through",
        "there is no silent exception path around the stay-in-C policy",
    ],
    "Documentation/zigux/phase10-closure-evidence.md": [
        "`Documentation/zigux/freeze-map.md`",
        "risky transport work is still blocked",
        "dual-implementation requirement remains parked",
        "Architecture Council reopen remains unattached",
    ],
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md": [
        "`Documentation/zigux/freeze-map.md`",
        "`scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
        "`zigux/tests/phase10_virtio_mmio_manifest.json`",
        "Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
    ],
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md": [
        "MMIO lane `P10-L10` owns",
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
        "Documentation/zigux/freeze-map.md",
        "phase10-mmio-lifecycle-and-irq-paths",
    ],
    "Documentation/zigux/phase10-virtio-mmio-survey.md": [
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
        "This survey stays aligned with `Documentation/zigux/freeze-map.md` and the shared Phase 10 closure packet.",
        "Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates.",
        "Allowed roadmap destinations remain `drivers/virtio/*.zig` plus justified `zigux/kernel/` or `zigux/helpers/` support surfaces; this note does not widen the tranche into new transport homes.",
        "Forbidden transport claims remain queue setup or reset paths, IRQ parity, DMA paths, input registration lifecycle, and probe-remove lifecycle behavior.",
        "The Phase 14 study-only anchors `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain outside this lane, and this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.",
    ],
    "zigux/Makefile": [
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py --self-test",
        "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
        "phase10-validate:",
        "$(ZIG) build test --build-file zigux/tests/phase10_build.zig",
    ],
    "zigux/tests/README.md": [
        "`scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
        "`Documentation/zigux/freeze-map.md`",
        "`zigux/tests/phase10_virtio_mmio_manifest.json`",
        "`make -C zigux phase10-validate`",
    ],
    "zigux/tests/phase10_closure_manifest.json": [
        '"freeze_map": "Documentation/zigux/freeze-map.md"',
        '"freeze_boundary_status": "aligned"',
        '"freeze_status_change_claimed": false',
        '"scripts/zigux/check-phase10-mmio-freeze-boundary.py"',
        f'"{FREEZE_BOUNDARY_CHECK}"',
        '"phase10-mmio-lifecycle-and-irq-paths"',
    ],
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md": [
        "PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py",
        "PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py",
        "PHASE10_LEDGER_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates",
        "PHASE10_LEDGER_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle",
    ],
}

MMIO_MANIFEST_SCALARS = {
    "lane_key": "P10-L10",
    "phase": "Phase 10",
    "surveyed_commit": "84f90e23ad1c28ae345905d5293a8c5395f37d43",
    "anchor": "drivers/virtio/virtio_mmio.c",
    "freeze_map": "Documentation/zigux/freeze-map.md",
    "freeze_boundary_status": "aligned",
    "freeze_status_change_claimed": False,
    "risky_transport_posture": "blocked_on_risky_transport",
    "architecture_council_reopen_required": True,
    "architecture_council_reopen_attached": False,
}

EXPECTED_ROADMAP_DESTINATIONS = ["drivers/virtio/*.zig", "zigux/kernel/", "zigux/helpers/"]
EXPECTED_ALLOWED_EVIDENCE_KINDS = [
    "driver_local_lab_slices",
    "survey_manifests",
    "shared_validation_gates",
]
EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS = [
    "queue_setup_reset_paths",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
]

EXPECTED_GAP_STATUSES = {
    "phase10-mmio-config-write-disposition-helper": "starter_landed",
    "phase10-mmio-selected-queue-readiness-helper": "starter_landed",
    "phase10-mmio-lifecycle-and-irq-paths": "blocked_on_risky_transport",
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        return missing_files, []

    missing_markers: list[str] = []
    for rel_path, markers in TEXT_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{Path(rel_path).name}:{marker}")

    closure_manifest_text = read_text(root, "zigux/tests/phase10_closure_manifest.json")
    freeze_boundary_count = closure_manifest_text.count(FREEZE_BOUNDARY_CHECK)
    if freeze_boundary_count != 1:
        missing_markers.append(f"closure_manifest:exact_checks:freeze_boundary_count={freeze_boundary_count}")

    manifest = json.loads(read_text(root, "zigux/tests/phase10_virtio_mmio_manifest.json"))
    for key, expected in MMIO_MANIFEST_SCALARS.items():
        actual = manifest.get(key)
        if actual != expected:
            missing_markers.append(f"mmio_manifest:{key}={actual!r}")

    if manifest.get("roadmap_destinations") != EXPECTED_ROADMAP_DESTINATIONS:
        missing_markers.append("mmio_manifest:roadmap_destinations")
    if manifest.get("allowed_evidence_kinds") != EXPECTED_ALLOWED_EVIDENCE_KINDS:
        missing_markers.append("mmio_manifest:allowed_evidence_kinds")
    if manifest.get("forbidden_transport_claims") != EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS:
        missing_markers.append("mmio_manifest:forbidden_transport_claims")

    summary = manifest.get("survey_summary", {})
    if summary.get("preexisting_virtio_mmio_verify_present") is not True:
        missing_markers.append(
            f"mmio_manifest:survey_summary:preexisting_virtio_mmio_verify_present={summary.get('preexisting_virtio_mmio_verify_present')!r}"
        )

    gaps = {
        gap.get("id"): gap.get("status")
        for gap in manifest.get("gaps", [])
        if isinstance(gap, dict)
    }
    for gap_id, expected_status in EXPECTED_GAP_STATUSES.items():
        actual_status = gaps.get(gap_id)
        if actual_status != expected_status:
            missing_markers.append(f"mmio_manifest:gap_status:{gap_id}={actual_status!r}")

    return [], missing_markers


def build_fixture() -> dict[str, str]:
    fixture = {}
    for rel_path, markers in TEXT_MARKERS.items():
        fixture[rel_path] = "\n".join(markers) + "\n"

    fixture["zigux/tests/phase10_virtio_mmio_manifest.json"] = json.dumps(
        {
            **MMIO_MANIFEST_SCALARS,
            "roadmap_destinations": EXPECTED_ROADMAP_DESTINATIONS,
            "allowed_evidence_kinds": EXPECTED_ALLOWED_EVIDENCE_KINDS,
            "forbidden_transport_claims": EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS,
            "survey_summary": {
                "preexisting_virtio_mmio_verify_present": True,
            },
            "gaps": [
                {"id": gap_id, "status": status}
                for gap_id, status in EXPECTED_GAP_STATUSES.items()
            ],
        },
        indent=2,
    ) + "\n"
    return fixture


def expect_missing_marker(root: Path, rel_path: str, old: str, new: str, expected: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    _, missing_markers = validate(root)
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-mmio-freeze-self-test:expected={expected}:actual={actual}")
    path.write_text(original, encoding="utf-8")


def run_manifest_case(root: Path) -> None:
    manifest_path = root / "zigux/tests/phase10_virtio_mmio_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["risky_transport_posture"] = "starter_landed"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    _, missing_markers = validate(root)
    expected = "mmio_manifest:risky_transport_posture='starter_landed'"
    if expected not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"phase10-mmio-freeze-self-test:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_mmio_freeze_") as tmp_dir:
        root = Path(tmp_dir)
        fixture = build_fixture()
        for rel_path, content in fixture.items():
            path = root / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase10-mmio-freeze-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"markers={','.join(missing_markers) or 'none'}"
            )

        cases = [
            (
                "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
                f'FREEZE_BOUNDARY_CHECK = "{FREEZE_BOUNDARY_CHECK}"',
                'FREEZE_BOUNDARY_CHECK = "python3 scripts/zigux/check-phase10-mmio-freeze-boundary-drift.py"',
                f'check-phase10-mmio-freeze-boundary.py:FREEZE_BOUNDARY_CHECK = "{FREEZE_BOUNDARY_CHECK}"',
            ),
            (
                "Documentation/zigux/freeze-map.md",
                "`kernel/workqueue.c`",
                "`kernel/workqueue_bridge.zig`",
                "freeze-map.md:`kernel/workqueue.c`",
            ),
            (
                "Documentation/zigux/phase10-virtio-mmio-survey.md",
                "Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates.",
                "Allowed evidence for this lane remains limited to direct transport execution.",
                "phase10-virtio-mmio-survey.md:Allowed evidence for this lane remains limited to driver-local lab slices, survey manifests, and shared validation gates.",
            ),
            (
                "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
                "scripts/zigux/check-phase10-mmio-freeze-boundary.py",
                "scripts/zigux/check-phase10-mmio-freeze-boundary-missing.py",
                "phase10-virtio-driver-lane-sequencing.md:scripts/zigux/check-phase10-mmio-freeze-boundary.py",
            ),
            (
                "Documentation/zigux/review-checklist.md",
                "`scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
                "`scripts/zigux/check-phase10-mmio-freeze-boundary-missing.py`",
                "review-checklist.md:`scripts/zigux/check-phase10-mmio-freeze-boundary.py`",
            ),
            (
                "scripts/zigux/README.md",
                "check-phase10-mmio-freeze-boundary.py",
                "check-phase10-mmio-freeze-boundary-missing.py",
                "README.md:check-phase10-mmio-freeze-boundary.py",
            ),
            (
                "scripts/zigux/check-phase10-mmio-packet.py",
                "phase10-mmio-lifecycle-and-irq-paths",
                "phase10-mmio-lifecycle-gap",
                "check-phase10-mmio-packet.py:phase10-mmio-lifecycle-and-irq-paths",
            ),
            (
                "scripts/zigux/validate-phase10-closure.py",
                "PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py",
                "PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/check-phase10-mmio-freeze-boundary-missing.py",
                "validate-phase10-closure.py:PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py",
            ),
            (
                "zigux/Makefile",
                "scripts/zigux/check-phase10-mmio-freeze-boundary.py --self-test",
                "scripts/zigux/check-phase10-mmio-freeze-boundary-missing.py --self-test",
                "Makefile:scripts/zigux/check-phase10-mmio-freeze-boundary.py --self-test",
            ),
            (
                "zigux/tests/phase10_closure_manifest.json",
                '"scripts/zigux/check-phase10-mmio-freeze-boundary.py"',
                '"scripts/zigux/check-phase10-mmio-freeze-boundary-missing.py"',
                'phase10_closure_manifest.json:"scripts/zigux/check-phase10-mmio-freeze-boundary.py"',
            ),
            (
                "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
                "PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py",
                "PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/check-phase10-mmio-freeze-boundary-missing.py",
                "PHASE10_CLOSURE_LEDGER.md:PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py",
            ),
        ]

        for rel_path, old, new, expected in cases:
            expect_missing_marker(root, rel_path, old, new, expected)

        run_manifest_case(root)

    print("PHASE10_MMIO_FREEZE_BOUNDARY_SELF_TEST=pass")
    print("PHASE10_MMIO_FREEZE_BOUNDARY_SELF_TEST_CASE_COUNT=12")
    return 0


if "--self-test" in sys.argv[1:]:
    sys.exit(run_self_test())

missing_files, missing_markers = validate(ROOT)
if missing_files:
    print("PHASE10_MMIO_FREEZE_BOUNDARY=fail")
    print("MISSING_PHASE10_MMIO_FREEZE_FILES_START")
    for item in missing_files:
        print(item)
    print("MISSING_PHASE10_MMIO_FREEZE_FILES_END")
    sys.exit(1)
if missing_markers:
    print("PHASE10_MMIO_FREEZE_BOUNDARY=fail")
    print("MISSING_PHASE10_MMIO_FREEZE_MARKERS_START")
    for item in missing_markers:
        print(item)
    print("MISSING_PHASE10_MMIO_FREEZE_MARKERS_END")
    sys.exit(1)

print("PHASE10_MMIO_FREEZE_BOUNDARY=pass")
print(f"PHASE10_MMIO_FREEZE_REQUIRED_FILE_COUNT={len(FILES)}")
print(
    "PHASE10_MMIO_FREEZE_REQUIRED_MARKER_COUNT="
    f"{sum(len(markers) for markers in TEXT_MARKERS.values()) + len(MMIO_MANIFEST_SCALARS) + len(EXPECTED_ROADMAP_DESTINATIONS) + len(EXPECTED_ALLOWED_EVIDENCE_KINDS) + len(EXPECTED_FORBIDDEN_TRANSPORT_CLAIMS) + len(EXPECTED_GAP_STATUSES) + 2}"
)
