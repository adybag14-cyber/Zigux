#!/usr/bin/env python3
"""Guard the Phase 1 review-checklist reminder packet against drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

PRESENT_PATHS = (
    Path("Documentation/zigux/phase1-closure.md"),
    Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/README.md"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/phase1_host_tools_smoke.zig"),
    Path(".github/workflows/zigux-bootstrap.yml"),
    MANIFEST_REL,
    Path("zigux/Makefile"),
)

MISSING_PATHS = (
    Path("scripts/zigux/validate-phase1.py"),
    Path("scripts/zigux/check-phase1-parity.py"),
    Path("zigux/tests/phase1_helpers.zig"),
    Path("zigux/tests/phase1_bench.zig"),
    Path("zigux/tests/fixtures/phase1_bench_expectations.json"),
    Path("zigux/tests/fixtures/phase1_helpers_c_harness.c"),
)

REQUIRED_MARKERS = {
    "phase1_validation_prompt": "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    "parity_fixture_prompt": "* are parity tests or fixture checks included?",
    "rollback_prompt": "* is there a stated rollback owner and fallback path?",
}

FORBIDDEN_MARKERS = (
    "`scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c` still agree on the current closed-helper reminder packet",
    "zig build test --build-file zigux/tests/build.zig",
    "zig build bench --build-file zigux/tests/build.zig",
)

EXPECTED_HELPERS = (
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
)

EXPECTED_SHARED_HELPERS = (
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
)

EXPECTED_DIRECT_HELPERS = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)

EXPECTED_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers "
    "above, while bitmap, find_bit, rbtree, and string keep the only bounded direct "
    "helper-local follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}"]


def load_json_without_duplicates(path: Path) -> object:
    def hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate key {key!r}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)


def validate_manifest(root: Path) -> list[str]:
    manifest_path = root / MANIFEST_REL
    failures: list[str] = []

    try:
        manifest = load_json_without_duplicates(manifest_path)
    except Exception as exc:
        return [f"manifest_parse:{MANIFEST_REL.as_posix()}:{exc}"]

    if not isinstance(manifest, dict):
        return [f"manifest_type:expected=dict:actual={type(manifest).__name__}"]

    if manifest.get("phase") != "Phase 1":
        failures.append(f"manifest_phase:actual={manifest.get('phase')!r}")
    if manifest.get("status") != "closed":
        failures.append(f"manifest_status:actual={manifest.get('status')!r}")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        failures.append(f"manifest_helper_count:actual={manifest.get('helper_count')!r}")

    helpers = tuple(manifest.get("helpers", []))
    if helpers != EXPECTED_HELPERS:
        failures.append(f"manifest_helpers:actual={helpers!r}")

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        failures.append(
            f"manifest_lane_sequencing:expected=dict:actual={type(lane_sequencing).__name__}"
        )
        return failures

    shared_helpers = tuple(lane_sequencing.get("shared_replay_parked_helpers", []))
    if shared_helpers != EXPECTED_SHARED_HELPERS:
        failures.append(f"manifest_shared_helpers:actual={shared_helpers!r}")

    direct_helpers = tuple(lane_sequencing.get("direct_anchor_followup_helpers", []))
    if direct_helpers != EXPECTED_DIRECT_HELPERS:
        failures.append(f"manifest_direct_helpers:actual={direct_helpers!r}")

    if lane_sequencing.get("rule_summary") != EXPECTED_RULE_SUMMARY:
        failures.append("manifest_rule_summary:drift")
    if lane_sequencing.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        failures.append("manifest_anti_overlap_rule:drift")

    combined = shared_helpers + direct_helpers
    if sorted(combined) != sorted(EXPECTED_HELPERS):
        failures.append("manifest_helper_partition:drift")
    if len(set(combined)) != len(EXPECTED_HELPERS):
        failures.append("manifest_helper_partition_duplicates")

    return failures


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    checklist_path = root / REVIEW_CHECKLIST_REL
    if not checklist_path.is_file():
        return [f"missing_file:{REVIEW_CHECKLIST_REL.as_posix()}"]

    checklist_text = checklist_path.read_text(encoding="utf-8")

    for label, marker in REQUIRED_MARKERS.items():
        failures.extend(
            require_exact_occurrence(
                checklist_text,
                f"{REVIEW_CHECKLIST_REL.as_posix()}:{label}",
                marker,
            )
        )

    for marker in FORBIDDEN_MARKERS:
        count = checklist_text.count(marker)
        if count:
            failures.append(
                f"{REVIEW_CHECKLIST_REL.as_posix()}:forbidden_marker:actual_count={count}"
            )

    for path in PRESENT_PATHS:
        if not (root / path).is_file():
            failures.append(f"missing_present_path:{path.as_posix()}")

    for path in MISSING_PATHS:
        if (root / path).exists():
            failures.append(f"unexpected_returned_gap:{path.as_posix()}")

    if not failures:
        failures.extend(validate_manifest(root))

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": list(EXPECTED_HELPERS),
        "lane_sequencing": {
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_HELPERS),
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }


def write_sample_root(root: Path) -> None:
    for path in PRESENT_PATHS:
        placeholder = f"sample placeholder for {path.as_posix()}\n"
        if path == REVIEW_CHECKLIST_REL:
            placeholder = (
                "# Zigux Review Checklist\n\n"
                "## Validation\n"
                f"{REQUIRED_MARKERS['parity_fixture_prompt']}\n"
                f"{REQUIRED_MARKERS['rollback_prompt']}\n"
                f"{REQUIRED_MARKERS['phase1_validation_prompt']}\n"
            )
        elif path == MANIFEST_REL:
            placeholder = json.dumps(sample_manifest(), indent=2) + "\n"
        write_text(root / path, placeholder)


def run_self_test() -> int:
    cases = [
        ("baseline", None),
        ("missing_phase1_prompt", "remove_phase1_prompt"),
        ("duplicate_phase1_prompt", "duplicate_phase1_prompt"),
        ("missing_present_path", "remove_present_path"),
        ("unexpected_gap_return", "restore_missing_gap"),
        ("forbidden_old_route", "insert_forbidden_route"),
        ("manifest_summary_drift", "manifest_summary_drift"),
        ("manifest_duplicate_key", "manifest_duplicate_key"),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-review-checklist-{name}-") as tmp:
            root = Path(tmp)
            write_sample_root(root)

            checklist_path = root / REVIEW_CHECKLIST_REL
            checklist_text = checklist_path.read_text(encoding="utf-8")

            if mutate == "remove_phase1_prompt":
                checklist_path.write_text(
                    checklist_text.replace(
                        REQUIRED_MARKERS["phase1_validation_prompt"] + "\n", "", 1
                    ),
                    encoding="utf-8",
                )
            elif mutate == "duplicate_phase1_prompt":
                checklist_path.write_text(
                    checklist_text.replace(
                        REQUIRED_MARKERS["phase1_validation_prompt"],
                        REQUIRED_MARKERS["phase1_validation_prompt"]
                        + "\n"
                        + REQUIRED_MARKERS["phase1_validation_prompt"],
                        1,
                    ),
                    encoding="utf-8",
                )
            elif mutate == "remove_present_path":
                (root / PRESENT_PATHS[1]).unlink()
            elif mutate == "restore_missing_gap":
                write_text(root / MISSING_PATHS[0], "unexpected returned gap\n")
            elif mutate == "insert_forbidden_route":
                checklist_path.write_text(
                    checklist_text + FORBIDDEN_MARKERS[1] + "\n",
                    encoding="utf-8",
                )
            elif mutate == "manifest_summary_drift":
                manifest_path = root / MANIFEST_REL
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest["lane_sequencing"]["rule_summary"] = "drifted summary"
                manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            elif mutate == "manifest_duplicate_key":
                manifest_path = root / MANIFEST_REL
                manifest_path.write_text(
                    '{"phase":"Phase 1","phase":"duplicate"}\n',
                    encoding="utf-8",
                )

            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-review-checklist-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-review-checklist-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_REVIEW_CHECKLIST_PACKET_SELF_TEST=pass")
    print(f"PHASE1_REVIEW_CHECKLIST_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample root for focused checker replay",
    )
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_REVIEW_CHECKLIST_PACKET=pass")
    print(f"PHASE1_REVIEW_CHECKLIST_PACKET_PRESENT_COUNT={len(PRESENT_PATHS)}")
    print(f"PHASE1_REVIEW_CHECKLIST_PACKET_GAP_COUNT={len(MISSING_PATHS)}")
    print(f"PHASE1_REVIEW_CHECKLIST_PACKET_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())