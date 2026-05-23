#!/usr/bin/env python3
"""Fail closed when Phase 10 closure-manifest summary counts or route anchors drift."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
MANIFEST_PATH = "zigux/tests/phase10_closure_manifest.json"

COUNT_FIELDS = {
    "doc_count": "docs",
    "manifest_count": "manifests",
    "driver_count": "drivers",
    "test_count": "tests",
}

REQUIRED_EXACT_CHECKS = [
    "python3 scripts/zigux/check-phase10-bootstrap-route.py",
    "python3 scripts/zigux/check-phase10-core-packet.py",
    "python3 scripts/zigux/check-phase10-shared-freeze-boundary.py",
    "python3 scripts/zigux/check-phase10-ring-packet.py",
    "python3 scripts/zigux/check-phase10-input-packet.py",
    "python3 scripts/zigux/check-phase10-mmio-packet.py",
    "python3 scripts/zigux/check-phase10-harness-coverage.py",
    "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py",
    "python3 scripts/zigux/check-phase10-closure-manifest-counts.py",
    "python3 scripts/zigux/validate-phase10.py",
    "python3 scripts/zigux/validate-phase10-closure.py",
    "make -C zigux phase10-validate",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
]

REQUIRED_RING_SCOREBOARD_EVIDENCE = [
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_ring_publish_readiness.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
]

REQUIRED_MMIO_SCOREBOARD_EVIDENCE = [
    "drivers/virtio/virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
]

REQUIRED_MMIO_READY_TRANSPORT_PATH = "zigux/tests/phase10_virtio_mmio_manifest.json"
REQUIRED_MMIO_READY_TRANSPORT_GAP = "phase10-mmio-lifecycle-and-irq-paths"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_drift(manifest: dict) -> list[str]:
    drift: list[str] = []
    for count_field, list_field in COUNT_FIELDS.items():
        listed = manifest.get(list_field)
        if not isinstance(listed, list) or not listed:
            drift.append(f"{list_field}:missing")
            continue

        count = manifest.get(count_field)
        if not isinstance(count, int):
            drift.append(f"{count_field}:missing")
            continue

        actual = len(listed)
        if count != actual:
            drift.append(f"{count_field}:{count}!=len({list_field}):{actual}")

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list) or not exact_checks:
        drift.append("exact_checks:missing")
        return drift

    indexes: list[int] = []
    for item in REQUIRED_EXACT_CHECKS:
        if item not in exact_checks:
            drift.append(f"exact_checks:{item!r}:missing")
            continue
        indexes.append(exact_checks.index(item))

    if len(indexes) == len(REQUIRED_EXACT_CHECKS) and indexes != sorted(indexes):
        drift.append("exact_checks:closure_route:out_of_order")

    scoreboard = manifest.get("roadmap_parity_scoreboard", {})
    if not isinstance(scoreboard, dict):
        drift.append("roadmap_parity_scoreboard:missing")
        return drift

    virtqueue_wrappers = scoreboard.get("virtqueue_wrappers")
    if not isinstance(virtqueue_wrappers, dict):
        drift.append("roadmap_parity_scoreboard:virtqueue_wrappers:missing")
        return drift

    ring_evidence = virtqueue_wrappers.get("evidence")
    if not isinstance(ring_evidence, list) or not ring_evidence:
        drift.append("roadmap_parity_scoreboard:virtqueue_wrappers:evidence:missing")
        return drift

    for item in REQUIRED_RING_SCOREBOARD_EVIDENCE:
        if item not in ring_evidence:
            drift.append(
                "roadmap_parity_scoreboard:virtqueue_wrappers:"
                f"{item!r}:missing"
            )

    mmio_wrappers = scoreboard.get("mmio_wrappers")
    if not isinstance(mmio_wrappers, dict):
        drift.append("roadmap_parity_scoreboard:mmio_wrappers:missing")
        return drift

    mmio_evidence = mmio_wrappers.get("evidence")
    if not isinstance(mmio_evidence, list) or not mmio_evidence:
        drift.append("roadmap_parity_scoreboard:mmio_wrappers:evidence:missing")
        return drift

    for item in REQUIRED_MMIO_SCOREBOARD_EVIDENCE:
        if item not in mmio_evidence:
            drift.append(
                "roadmap_parity_scoreboard:mmio_wrappers:"
                f"{item!r}:missing"
            )

    ready_transport_followups = manifest.get("ready_transport_followups")
    if not isinstance(ready_transport_followups, dict):
        drift.append("ready_transport_followups:missing")
        return drift

    mmio_followup = ready_transport_followups.get(REQUIRED_MMIO_READY_TRANSPORT_PATH)
    if mmio_followup != REQUIRED_MMIO_READY_TRANSPORT_GAP:
        drift.append(
            "ready_transport_followups:"
            f"{REQUIRED_MMIO_READY_TRANSPORT_PATH}:{mmio_followup!r}!={REQUIRED_MMIO_READY_TRANSPORT_GAP!r}"
        )

    blocked_transport_gaps = manifest.get("blocked_transport_gaps")
    if not isinstance(blocked_transport_gaps, dict):
        drift.append("blocked_transport_gaps:missing")
        return drift

    mmio_blocked_gap = blocked_transport_gaps.get(REQUIRED_MMIO_READY_TRANSPORT_PATH)
    if mmio_blocked_gap != REQUIRED_MMIO_READY_TRANSPORT_GAP:
        drift.append(
            "blocked_transport_gaps:"
            f"{REQUIRED_MMIO_READY_TRANSPORT_PATH}:{mmio_blocked_gap!r}!={REQUIRED_MMIO_READY_TRANSPORT_GAP!r}"
        )

    return drift


def validate(root: Path) -> tuple[list[str], list[str]]:
    manifest_path = root / MANIFEST_PATH
    if not manifest_path.exists():
        return [MANIFEST_PATH], []
    return [], collect_drift(read_json(manifest_path))


def fixture_manifest() -> dict:
    return {
        "doc_count": 7,
        "manifest_count": 4,
        "driver_count": 4,
        "test_count": 21,
        "docs": [f"doc-{index}" for index in range(7)],
        "manifests": [f"manifest-{index}" for index in range(4)],
        "drivers": [f"driver-{index}" for index in range(4)],
        "tests": [f"test-{index}" for index in range(21)],
        "exact_checks": REQUIRED_EXACT_CHECKS,
        "roadmap_parity_scoreboard": {
            "virtqueue_wrappers": {
                "status": "starter_landed",
                "evidence": REQUIRED_RING_SCOREBOARD_EVIDENCE,
            },
            "mmio_wrappers": {
                "status": "starter_landed",
                "evidence": REQUIRED_MMIO_SCOREBOARD_EVIDENCE,
            },
        },
        "ready_transport_followups": {
            REQUIRED_MMIO_READY_TRANSPORT_PATH: REQUIRED_MMIO_READY_TRANSPORT_GAP,
        },
        "blocked_transport_gaps": {
            REQUIRED_MMIO_READY_TRANSPORT_PATH: REQUIRED_MMIO_READY_TRANSPORT_GAP,
        },
    }


def write_fixture(root: Path) -> None:
    write_text(root / MANIFEST_PATH, json.dumps(fixture_manifest(), indent=2) + "\n")


def expect_contains(items: list[str], expected: str, label: str) -> None:
    if expected not in items:
        actual = ",".join(items) if items else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_manifest_counts_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)

        missing_files, drift = validate(root)
        if missing_files or drift:
            raise SystemExit(
                "phase10-manifest-counts-self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"drift={','.join(drift) or 'none'}"
            )

        manifest_path = root / MANIFEST_PATH
        original = read_json(manifest_path)

        def write_manifest(data: dict) -> None:
            write_text(manifest_path, json.dumps(data, indent=2) + "\n")

        cases = 0

        broken = dict(original)
        broken["doc_count"] = 6
        write_manifest(broken)
        expect_contains(validate(root)[1], "doc_count:6!=len(docs):7", "phase10-manifest-counts-self-test")
        cases += 1

        broken = dict(original)
        broken["manifest_count"] = 5
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "manifest_count:5!=len(manifests):4",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["driver_count"] = 3
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "driver_count:3!=len(drivers):4",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["test_count"] = 20
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "test_count:20!=len(tests):21",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        del broken["doc_count"]
        write_manifest(broken)
        expect_contains(validate(root)[1], "doc_count:missing", "phase10-manifest-counts-self-test")
        cases += 1

        broken = dict(original)
        broken["tests"] = []
        write_manifest(broken)
        expect_contains(validate(root)[1], "tests:missing", "phase10-manifest-counts-self-test")
        cases += 1

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "python3 scripts/zigux/check-phase10-core-packet.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-core-packet.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["exact_checks"] = [
            item
            for item in broken["exact_checks"]
            if item != "python3 scripts/zigux/check-phase10-shared-freeze-boundary.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-shared-freeze-boundary.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "python3 scripts/zigux/check-phase10-ring-packet.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-ring-packet.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "python3 scripts/zigux/check-phase10-input-packet.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-input-packet.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "python3 scripts/zigux/check-phase10-mmio-packet.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-mmio-packet.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["exact_checks"] = [
            item
            for item in broken["exact_checks"]
            if item != "python3 scripts/zigux/check-phase10-harness-coverage.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-harness-coverage.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["exact_checks"] = [
            item
            for item in broken["exact_checks"]
            if item != "python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["exact_checks"] = [
            item for item in broken["exact_checks"] if item != "python3 scripts/zigux/validate-phase10-closure.py"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/validate-phase10-closure.py':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        reordered = list(REQUIRED_EXACT_CHECKS)
        reordered[-1], reordered[-2] = reordered[-2], reordered[-1]
        broken["exact_checks"] = reordered
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:closure_route:out_of_order",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        del broken["exact_checks"]
        write_manifest(broken)
        expect_contains(validate(root)[1], "exact_checks:missing", "phase10-manifest-counts-self-test")
        cases += 1

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["virtqueue_wrappers"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["virtqueue_wrappers"]["evidence"]
            if item != "drivers/virtio/virtio_ring_publish_readiness.zig"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:virtqueue_wrappers:'drivers/virtio/virtio_ring_publish_readiness.zig':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["roadmap_parity_scoreboard"]["mmio_wrappers"]["evidence"] = [
            item
            for item in broken["roadmap_parity_scoreboard"]["mmio_wrappers"]["evidence"]
            if item != "Documentation/zigux/phase10-virtio-mmio-survey.md"
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:mmio_wrappers:'Documentation/zigux/phase10-virtio-mmio-survey.md':missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["ready_transport_followups"][REQUIRED_MMIO_READY_TRANSPORT_PATH] = "phase10-mmio-helper-drift"
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "ready_transport_followups:zigux/tests/phase10_virtio_mmio_manifest.json:'phase10-mmio-helper-drift'!='phase10-mmio-lifecycle-and-irq-paths'",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        broken["blocked_transport_gaps"][REQUIRED_MMIO_READY_TRANSPORT_PATH] = "phase10-mmio-helper-drift"
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "blocked_transport_gaps:zigux/tests/phase10_virtio_mmio_manifest.json:'phase10-mmio-helper-drift'!='phase10-mmio-lifecycle-and-irq-paths'",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        broken = dict(original)
        del broken["roadmap_parity_scoreboard"]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "roadmap_parity_scoreboard:virtqueue_wrappers:missing",
            "phase10-manifest-counts-self-test",
        )
        cases += 1

        manifest_path.unlink()
        missing_files, drift = validate(root)
        if drift:
            actual = ",".join(drift)
            raise SystemExit(f"phase10-manifest-counts-self-test:unexpected_drift={actual}")
        if missing_files != [MANIFEST_PATH]:
            actual = ",".join(missing_files) if missing_files else "none"
            raise SystemExit(
                "phase10-manifest-counts-self-test:"
                f"expected_missing={MANIFEST_PATH}:actual={actual}"
            )
        cases += 1

    print("PHASE10_CLOSURE_MANIFEST_COUNTS_SELF_TEST=pass")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 10 closure manifest summary-count packet."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, drift = validate(args.repo_root)
    if missing_files:
        print("PHASE10_CLOSURE_MANIFEST_COUNTS=fail")
        print("MISSING_PHASE10_CLOSURE_MANIFEST_COUNTS_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE10_CLOSURE_MANIFEST_COUNTS_FILES_END")
        return 1

    if drift:
        print("PHASE10_CLOSURE_MANIFEST_COUNTS=fail")
        print("PHASE10_CLOSURE_MANIFEST_COUNTS_DRIFT_START")
        for item in drift:
            print(item)
        print("PHASE10_CLOSURE_MANIFEST_COUNTS_DRIFT_END")
        return 1

    print("PHASE10_CLOSURE_MANIFEST_COUNTS=pass")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_FIELD_COUNT={len(COUNT_FIELDS)}")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_EXACT_CHECK_COUNT={len(REQUIRED_EXACT_CHECKS)}")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_RING_EVIDENCE_COUNT={len(REQUIRED_RING_SCOREBOARD_EVIDENCE)}")
    print(f"PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_MMIO_EVIDENCE_COUNT={len(REQUIRED_MMIO_SCOREBOARD_EVIDENCE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
