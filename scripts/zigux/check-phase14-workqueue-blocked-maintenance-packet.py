#!/usr/bin/env python3
"""Fail-close the current Phase 14 workqueue blocked-maintenance packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SLICE_NOTE = Path("Documentation/zigux/phase14-workqueue-bridge-slice.md")
SURVEY_NOTE = Path("Documentation/zigux/phase14-workqueue-bridge-survey.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
WORKQUEUE_BRIDGE = Path("kernel/workqueue_bridge.zig")
WORKQUEUE_BRIDGE_TEST = Path("zigux/tests/phase14_workqueue_bridge.zig")
WORKQUEUE_REVIEWABILITY = Path("zigux/tests/phase14_workqueue_reviewability.zig")
MANIFEST_PATH = Path("zigux/tests/phase14_workqueue_bridge_manifest.json")

REQUIRED_MARKERS = {
    SLICE_NOTE: (
        "PHASE14_LANE_KEY=P14-L04",
        "PHASE14_STATUS=blocked_maintenance",
        "PHASE14_SLICE=phase14-workqueue-scheduler-visible-worker-state-refinement",
        "zigux/tests/phase14_workqueue_reviewability.zig",
        "phase14-workqueue-live-execution-blocker",
        "blocked maintenance",
    ),
    SURVEY_NOTE: (
        "PHASE14_STATUS=blocked_maintenance",
        "PHASE14_LANE_KEY=P14-L04",
        "PHASE14_SURVEYED_COMMIT=9b98d3b9c812840bf279508030be0b8de093736c",
        "phase14-workqueue-scheduler-visible-worker-state-refinement",
        "shared Phase 14 smoke packet",
        "zig test zigux/tests/phase14_workqueue_reviewability.zig",
        "make -C zigux phase14-validate",
        "missing `phase14-smoke`, `phase14-test`, and `phase14` wrappers",
    ),
    SCRIPTS_README: (
        "## Phase 14",
        "Phase 14 flow - the current scripts-root shared smoke packet stays reviewable",
        "`kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` keep the directly readable workqueue reviewability shard explicit",
    ),
    WORKQUEUE_BRIDGE: (
        'return "phase14-workqueue-scheduler-visible-worker-state-refinement";',
        '.posture = "blocked_maintenance",',
        '"zigux/tests/phase14_workqueue_reviewability.zig"',
        '"Documentation/zigux/phase14-workqueue-bridge-slice.md"',
        '"Documentation/zigux/phase14-workqueue-bridge-survey.md"',
        '.blocked_by = "phase14-workqueue-live-execution-blocker",',
    ),
    WORKQUEUE_BRIDGE_TEST: (
        'try std.testing.expectEqualStrings("phase14-workqueue-scheduler-visible-worker-state-refinement", workqueue_bridge.WorkqueueBridgeLab.currentSliceId());',
        'try std.testing.expect(std.mem.indexOf(u8, handoff.next_future_target, "blocked maintenance") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, cancel_handoff.blocked_by, "pending-bit and completion rules") != null);',
    ),
    WORKQUEUE_REVIEWABILITY: (
        'try std.testing.expectEqualStrings("P14-L04", manifest.lane_key);',
        'try expectGapStatus(manifest, "phase14-workqueue-scheduler-visible-worker-state-refinement", "starter_landed");',
        'try expectGapStatus(manifest, "phase14-workqueue-live-execution-blocker", "blocked_on_live_concurrency");',
        'try std.testing.expect(std.mem.indexOf(u8, survey_note, "make -C zigux phase14-validate") != null);',
        'try std.testing.expect(std.mem.indexOf(u8, review_checklist, "same study-only stay-in-C posture") != null);',
    ),
}

REQUIRED_MANIFEST_FIELDS = {
    "lane_key": "P14-L04",
    "phase": "Phase 14",
    "surveyed_commit": "9b98d3b9c812840bf279508030be0b8de093736c",
    "anchor": "kernel/workqueue.c",
}

REQUIRED_MAINTENANCE_FIELDS = {
    "current_lane_posture": "blocked_maintenance",
    "productization_posture": "shared_packet_local_only",
}

REQUIRED_REPLAY_BEFORE_TRUSTING = [
    "zig test zigux/tests/phase14_workqueue_reviewability.zig",
]

REQUIRED_PRODUCTIZATION_CHECKS = [
    "python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "python3 scripts/zigux/check-phase14-shared-smoke-route.py",
    "python3 scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
    "python3 scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
    "python3 scripts/zigux/validate-phase14.py --self-test",
    "python3 scripts/zigux/validate-phase14.py",
    "python3 scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
    "python3 scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "python3 scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "python3 scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "make -C zigux phase14-validate",
]

REQUIRED_GAPS = {
    "phase14-workqueue-boundary-map-starter": "starter_landed",
    "phase14-workqueue-delayed-timer-expiry-followup": "starter_landed",
    "phase14-workqueue-delayed-requeue-governance": "starter_landed",
    "phase14-workqueue-flush-drain-governance": "starter_landed",
    "phase14-workqueue-rescuer-mayday-governance": "starter_landed",
    "phase14-workqueue-scheduler-visible-worker-state-refinement": "starter_landed",
    "phase14-workqueue-live-execution-blocker": "blocked_on_live_concurrency",
}

EXPECTED_STARTER_LANDED_COUNT = 17
EXPECTED_BLOCKED_COUNT = 1


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _append_duplicate_list_entry_issues(label: str, values: list[object], issues: list[str]) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        first_index = seen.get(key)
        if first_index is None:
            seen[key] = index
            continue
        issues.append(
            f"{label} duplicate entry: {value!r} (first index {first_index}, duplicate index {index})"
        )


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    for rel_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / rel_path
        if not path.is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue
        text = _read(path)
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {rel_path.as_posix()} marker: {marker}")

    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        issues.append(f"missing repo file: {MANIFEST_PATH.as_posix()}")
        return issues

    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    for field, expected in REQUIRED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(f"phase14_workqueue_bridge_manifest.json wrong {field}: {actual!r} != {expected!r}")

    maintenance_handoff = manifest.get("maintenance_handoff")
    if not isinstance(maintenance_handoff, dict):
        issues.append("phase14_workqueue_bridge_manifest.json maintenance_handoff is not an object")
        return issues

    for field, expected in REQUIRED_MAINTENANCE_FIELDS.items():
        actual = maintenance_handoff.get(field)
        if actual != expected:
            issues.append(
                f"phase14_workqueue_bridge_manifest.json wrong maintenance_handoff.{field}: "
                f"{actual!r} != {expected!r}"
            )

    replay_before_trusting = maintenance_handoff.get("replay_before_trusting")
    if not isinstance(replay_before_trusting, list):
        issues.append("phase14_workqueue_bridge_manifest.json replay_before_trusting is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase14_workqueue_bridge_manifest.json replay_before_trusting",
            replay_before_trusting,
            issues,
        )
        if replay_before_trusting != REQUIRED_REPLAY_BEFORE_TRUSTING:
            issues.append(
                "phase14_workqueue_bridge_manifest.json replay_before_trusting drifted from the "
                "current bridge-local trust gate"
            )

    productization_checks = maintenance_handoff.get("productization_exact_checks")
    if not isinstance(productization_checks, list):
        issues.append("phase14_workqueue_bridge_manifest.json productization_exact_checks is not a list")
    else:
        _append_duplicate_list_entry_issues(
            "phase14_workqueue_bridge_manifest.json productization_exact_checks",
            productization_checks,
            issues,
        )
        for route in REQUIRED_PRODUCTIZATION_CHECKS:
            if route not in productization_checks:
                issues.append(
                    f"phase14_workqueue_bridge_manifest.json missing productization_exact_checks entry: {route}"
                )

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        issues.append("phase14_workqueue_bridge_manifest.json gaps is not a list")
        return issues

    starter_landed_count = 0
    blocked_count = 0
    gap_index: dict[str, dict[str, object]] = {}
    for gap in gaps:
        if not isinstance(gap, dict):
            issues.append("phase14_workqueue_bridge_manifest.json gaps contains a non-object entry")
            continue
        gap_id = gap.get("id")
        if not isinstance(gap_id, str):
            issues.append("phase14_workqueue_bridge_manifest.json gaps contains an entry without string id")
            continue
        if gap_id in gap_index:
            issues.append(f"phase14_workqueue_bridge_manifest.json duplicate gap id: {gap_id}")
            continue
        gap_index[gap_id] = gap
        status = gap.get("status")
        if status == "starter_landed":
            starter_landed_count += 1
        if status == "blocked_on_live_concurrency":
            blocked_count += 1

    if starter_landed_count != EXPECTED_STARTER_LANDED_COUNT:
        issues.append(
            "phase14_workqueue_bridge_manifest.json wrong starter_landed count: "
            f"{starter_landed_count} != {EXPECTED_STARTER_LANDED_COUNT}"
        )
    if blocked_count != EXPECTED_BLOCKED_COUNT:
        issues.append(
            "phase14_workqueue_bridge_manifest.json wrong blocked_on_live_concurrency count: "
            f"{blocked_count} != {EXPECTED_BLOCKED_COUNT}"
        )

    for gap_id, expected_status in REQUIRED_GAPS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            issues.append(f"phase14_workqueue_bridge_manifest.json missing gap id: {gap_id}")
            continue
        actual_status = gap.get("status")
        if actual_status != expected_status:
            issues.append(
                f"phase14_workqueue_bridge_manifest.json wrong gap status for {gap_id}: "
                f"{actual_status!r} != {expected_status!r}"
            )

    return issues


def _populate_repo(root: Path) -> None:
    for rel_path, markers in REQUIRED_MARKERS.items():
        _write(root / rel_path, "\n".join(markers) + "\n")

    manifest = {
        "lane_key": REQUIRED_MANIFEST_FIELDS["lane_key"],
        "phase": REQUIRED_MANIFEST_FIELDS["phase"],
        "surveyed_commit": REQUIRED_MANIFEST_FIELDS["surveyed_commit"],
        "anchor": REQUIRED_MANIFEST_FIELDS["anchor"],
        "maintenance_handoff": {
            "current_lane_posture": REQUIRED_MAINTENANCE_FIELDS["current_lane_posture"],
            "replay_before_trusting": list(REQUIRED_REPLAY_BEFORE_TRUSTING),
            "productization_posture": REQUIRED_MAINTENANCE_FIELDS["productization_posture"],
            "productization_exact_checks": list(REQUIRED_PRODUCTIZATION_CHECKS),
        },
        "gaps": [],
    }

    starter_ids = [
        "phase14-build-gate",
        "phase14-make-target",
        "phase14-kernel-export-shim-foundation",
        "phase14-workqueue-boundary-map-starter",
        "phase14-workqueue-test-gate",
        "phase14-workqueue-slice-note",
        "phase14-workqueue-survey-note",
        "phase14-workqueue-concurrency-audit-outline",
        "phase14-workqueue-max-active-audit",
        "phase14-workqueue-lock-handoff-audit",
        "phase14-workqueue-pending-bit-followup",
        "phase14-workqueue-delayed-submission-alias-followup",
        "phase14-workqueue-delayed-timer-expiry-followup",
        "phase14-workqueue-delayed-requeue-governance",
        "phase14-workqueue-flush-drain-governance",
        "phase14-workqueue-rescuer-mayday-governance",
        "phase14-workqueue-scheduler-visible-worker-state-refinement",
    ]
    for gap_id in starter_ids:
        manifest["gaps"].append({"id": gap_id, "status": "starter_landed"})
    manifest["gaps"].append(
        {"id": "phase14-workqueue-live-execution-blocker", "status": "blocked_on_live_concurrency"}
    )

    _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase14_workqueue_packet_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE14_WORKQUEUE_BLOCKED_MAINTENANCE_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        cases = (
            (
                WORKQUEUE_BRIDGE,
                '.blocked_by = "phase14-workqueue-live-execution-blocker",\n',
                'missing kernel/workqueue_bridge.zig marker: .blocked_by = "phase14-workqueue-live-execution-blocker",',
            ),
            (
                SURVEY_NOTE,
                "make -C zigux phase14-validate\n",
                "missing Documentation/zigux/phase14-workqueue-bridge-survey.md marker: make -C zigux phase14-validate",
            ),
            (
                WORKQUEUE_REVIEWABILITY,
                'try expectGapStatus(manifest, "phase14-workqueue-live-execution-blocker", "blocked_on_live_concurrency");\n',
                'missing zigux/tests/phase14_workqueue_reviewability.zig marker: try expectGapStatus(manifest, "phase14-workqueue-live-execution-blocker", "blocked_on_live_concurrency");',
            ),
            (
                SCRIPTS_README,
                "## Phase 14\n",
                "missing scripts/zigux/README.md marker: ## Phase 14",
            ),
        )

        for rel_path, marker, expected in cases:
            path = root / rel_path
            _write(path, _read(path).replace(marker, "", 1))
            issues = validate_repo(root)
            if expected not in issues:
                print("PHASE14_WORKQUEUE_BLOCKED_MAINTENANCE_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1
            _populate_repo(root)

        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["maintenance_handoff"]["replay_before_trusting"] = []
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase14_workqueue_bridge_manifest.json replay_before_trusting drifted from the "
            "current bridge-local trust gate"
        )
        if expected not in issues:
            print("PHASE14_WORKQUEUE_BLOCKED_MAINTENANCE_PACKET_SELF_TEST=fail")
            print("expected replay-before-trusting drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["maintenance_handoff"]["productization_exact_checks"].remove("make -C zigux phase14-validate")
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase14_workqueue_bridge_manifest.json missing productization_exact_checks entry: "
            "make -C zigux phase14-validate"
        )
        if expected not in issues:
            print("PHASE14_WORKQUEUE_BLOCKED_MAINTENANCE_PACKET_SELF_TEST=fail")
            print("expected productization route drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["gaps"] = [gap for gap in manifest["gaps"] if gap["id"] != "phase14-workqueue-live-execution-blocker"]
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = "phase14_workqueue_bridge_manifest.json missing gap id: phase14-workqueue-live-execution-blocker"
        if expected not in issues:
            print("PHASE14_WORKQUEUE_BLOCKED_MAINTENANCE_PACKET_SELF_TEST=fail")
            print("expected blocked gap drift was not reported")
            return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["gaps"].append({"id": "phase14-workqueue-boundary-map-starter", "status": "starter_landed"})
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = "phase14_workqueue_bridge_manifest.json duplicate gap id: phase14-workqueue-boundary-map-starter"
        if expected not in issues:
            print("PHASE14_WORKQUEUE_BLOCKED_MAINTENANCE_PACKET_SELF_TEST=fail")
            print("expected duplicate gap id was not reported")
            return 1

    print("PHASE14_WORKQUEUE_BLOCKED_MAINTENANCE_PACKET_SELF_TEST=pass")
    print("PHASE14_WORKQUEUE_BLOCKED_MAINTENANCE_PACKET_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bounded Phase 14 workqueue blocked-maintenance packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the workqueue blocked-maintenance packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE14_WORKQUEUE_BLOCKED_MAINTENANCE_PACKET=fail")
        print("\n".join(issues))
        return 1

    print("PHASE14_WORKQUEUE_BLOCKED_MAINTENANCE_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
