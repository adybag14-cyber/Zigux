#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

MANIFEST_PATH = "zigux/tests/phase10_virtio_ring_manifest.json"

EXPECTED_SUMMARY_FIELDS = {
    "preexisting_ring_callback_enable_present": True,
    "preexisting_ring_reset_readiness_present": True,
}

EXPECTED_DESTINATIONS = {
    "phase10-callback-enable-helper": "drivers/virtio/virtio_ring_callback_enable.zig",
    "phase10-queue-reset-readiness-helper": "drivers/virtio/virtio_ring_reset_readiness.zig",
}


def load_manifest(root: Path) -> dict[str, object]:
    return json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))


def validate(root: Path) -> list[str]:
    manifest_path = root / MANIFEST_PATH
    if not manifest_path.exists():
        return [f"missing:{MANIFEST_PATH}"]

    manifest = load_manifest(root)
    problems: list[str] = []

    if manifest.get("lane_key") != "P10-L10":
        problems.append(f"{MANIFEST_PATH}:lane_key:{manifest.get('lane_key')!r}")
    if manifest.get("anchor") != "drivers/virtio/virtio_ring.c":
        problems.append(f"{MANIFEST_PATH}:anchor:{manifest.get('anchor')!r}")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        problems.append(f"{MANIFEST_PATH}:survey_summary:not_dict")
    else:
        for field, expected in EXPECTED_SUMMARY_FIELDS.items():
            actual = summary.get(field)
            if actual != expected:
                problems.append(f"{MANIFEST_PATH}:survey_summary:{field}:{actual!r}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        return problems + [f"{MANIFEST_PATH}:gaps:not_list"]

    gap_index = {
        gap.get("id"): gap
        for gap in gaps
        if isinstance(gap, dict) and isinstance(gap.get("id"), str)
    }
    for gap_id, expected_destination in EXPECTED_DESTINATIONS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            problems.append(f"{MANIFEST_PATH}:gap_missing:{gap_id}")
            continue
        actual_destination = gap.get("zigux_destination")
        if actual_destination != expected_destination:
            problems.append(
                f"{MANIFEST_PATH}:gap:{gap_id}:zigux_destination:{actual_destination!r}"
            )

    return problems


def fixture_manifest() -> dict[str, object]:
    return {
        "lane_key": "P10-L10",
        "anchor": "drivers/virtio/virtio_ring.c",
        "survey_summary": dict(EXPECTED_SUMMARY_FIELDS),
        "gaps": [
            {
                "id": gap_id,
                "status": "starter_landed",
                "kind": "queue_wrapper",
                "zigux_destination": destination,
            }
            for gap_id, destination in EXPECTED_DESTINATIONS.items()
        ],
    }


def write_manifest(root: Path, manifest: dict[str, object]) -> None:
    target = root / MANIFEST_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def expect_problem(label: str, mutate, expected: str) -> None:
    with tempfile.TemporaryDirectory(prefix=f"zigux_phase10_ring_destinations_{label}_") as tmp:
        root = Path(tmp)
        manifest = fixture_manifest()
        mutate(manifest)
        write_manifest(root, manifest)
        problems = validate(root)
        if expected not in problems:
            actual = ",".join(problems) if problems else "none"
            raise SystemExit(f"phase10-ring-destinations:{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase10_ring_destinations_baseline_") as tmp:
        root = Path(tmp)
        write_manifest(root, fixture_manifest())
        problems = validate(root)
        if problems:
            raise SystemExit("phase10-ring-destinations:baseline_failed:" + ",".join(problems))

    expect_problem(
        "callback_destination",
        lambda manifest: manifest["gaps"][0].__setitem__(
            "zigux_destination", "drivers/virtio/virtio_ring.zig"
        ),
        f"{MANIFEST_PATH}:gap:phase10-callback-enable-helper:zigux_destination:'drivers/virtio/virtio_ring.zig'",
    )
    expect_problem(
        "reset_readiness_destination",
        lambda manifest: manifest["gaps"][1].__setitem__(
            "zigux_destination", "drivers/virtio/virtio_ring.zig"
        ),
        f"{MANIFEST_PATH}:gap:phase10-queue-reset-readiness-helper:zigux_destination:'drivers/virtio/virtio_ring.zig'",
    )
    expect_problem(
        "callback_summary",
        lambda manifest: manifest["survey_summary"].__setitem__(
            "preexisting_ring_callback_enable_present", False
        ),
        f"{MANIFEST_PATH}:survey_summary:preexisting_ring_callback_enable_present:False",
    )

    print("PHASE10_RING_MANIFEST_DESTINATIONS_SELF_TEST=pass")
    print("PHASE10_RING_MANIFEST_DESTINATIONS_SELF_TEST_CASE_COUNT=4")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate P10-L10 ring manifest destinations for dedicated queue-wrapper evidence."
    )
    parser.add_argument("--root", default=ROOT, type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    problems = validate(args.root)
    if problems:
        print("PHASE10_RING_MANIFEST_DESTINATIONS=fail")
        for problem in problems:
            print(problem)
        return 1

    print("PHASE10_RING_MANIFEST_DESTINATIONS=pass")
    print(f"PHASE10_RING_MANIFEST_DESTINATION_COUNT={len(EXPECTED_DESTINATIONS)}")
    print(f"PHASE10_RING_MANIFEST_SUMMARY_FIELD_COUNT={len(EXPECTED_SUMMARY_FIELDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
