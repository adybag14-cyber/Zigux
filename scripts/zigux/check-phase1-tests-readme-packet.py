#!/usr/bin/env python3
"""Guard the Phase 1 tests README reminder packet against parity-fixture drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

TESTS_README_REL = Path("zigux/tests/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
REPLAY_BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")
BUILD_REL = Path("zigux/tests/build.zig")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_FILES = (
    TESTS_README_REL,
    SCRIPTS_README_REL,
    LANE_NOTE_REL,
    PHASE1_CLOSURE_REL,
    MANIFEST_REL,
    REPLAY_BLOCKERS_REL,
    BUILD_REL,
    SMOKE_REL,
    WORKFLOW_REL,
    MAKEFILE_REL,
)

README_MARKERS = (
    "## Phase 1 host-tools review packet",
    "- `Documentation/zigux/phase1-closure.md`",
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "- `scripts/zigux/validate-phase1-closure.py`",
    "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "* current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
)

SCRIPTS_README_MARKERS = (
    "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
    "- `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
)

LANE_NOTE_MARKERS = (
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
)

PHASE1_CLOSURE_MARKERS = (
    "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
)

BUILD_MARKERS = (
    'root_source_file = b.path("phase1_host_tools_smoke.zig"),',
    '.name = "phase1-host-tools-smoke",',
    'const slab_module = b.createModule(.{',
    'const str_error_r_module = b.createModule(.{',
    'const vsprintf_module = b.createModule(.{',
    'const zalloc_module = b.createModule(.{',
)

SMOKE_MARKERS = (
    'const argv_split = @import("argv_split");',
    'const slab = @import("slab");',
    'const str_error_r = @import("str_error_r");',
    'const vsprintf = @import("vsprintf");',
    'const zalloc = @import("zalloc");',
    'try std.testing.expect(@hasDecl(slab, "kmallocBytes"));',
    'try std.testing.expect(@hasDecl(str_error_r, "strErrorR"));',
    'try std.testing.expect(@hasDecl(vsprintf, "scnprintf"));',
    'try std.testing.expect(@hasDecl(zalloc, "zallocBytes"));',
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

MAKEFILE_MARKERS = (
    "phase1-route-summary:",
    "phase2-toolchain:",
    "phase3-validate:",
    "phase4-validate:",
    "phase6-validate:",
    "phase8-validate:",
    "phase10-validate:",
    "phase12-validate:",
    "phase14-validate:",
)

EXPECTED_SHARED_REPLAY_PARKED_HELPER_COUNT = 9
EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPER_COUNT = 4
EXPECTED_HELPER_COUNT = 13
EXPECTED_REPLAY_STATUS = "blocked"
EXPECTED_C_HARNESS_STATUS = "blocked"
EXPECTED_REPLAY_PATH = "zigux/tests/phase1_helpers.zig"
EXPECTED_C_HARNESS_PATH = "zigux/tests/fixtures/phase1_helpers_c_harness.c"
EXPECTED_C_HARNESS_BLOCKER_ID = "phase1_helpers_c_harness_missing_c_sources"
EXPECTED_REPLAY_BLOCKER_ID = "phase1_helpers_zig_slab_zero_after_kmalloc"
EXPECTED_REPLAY_BLOCKER_FIELD = "slab.zero_after_kmalloc"


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def read_json(root: Path, relative_path: Path) -> object:
    return json.loads(read_text(root, relative_path))


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path.as_posix() for relative_path in REQUIRED_FILES if not (root / relative_path).exists()]


def collect_marker_issues(text: str, label: str, markers: tuple[str, ...], *, stripped: bool = False) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    for marker in markers:
        if stripped:
            count = sum(1 for line in lines if line.strip() == marker)
        else:
            count = text.count(marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def nested_get(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def expect_value(data: object, path: tuple[str, ...], expected: object, label: str) -> list[str]:
    actual = nested_get(data, path)
    if actual != expected:
        return [f"{label}:{'.'.join(path)}:expected={expected!r}:actual={actual!r}"]
    return []


def collect_manifest_issues(manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]
    issues: list[str] = []
    issues.extend(expect_value(manifest, ("phase",), "Phase 1", MANIFEST_REL.as_posix()))
    issues.extend(expect_value(manifest, ("status",), "closed", MANIFEST_REL.as_posix()))
    issues.extend(expect_value(manifest, ("helper_count",), EXPECTED_HELPER_COUNT, MANIFEST_REL.as_posix()))
    issues.extend(
        expect_value(
            manifest,
            ("lane_sequencing", "shared_replay_parked_helpers"),
            [
                "tools/lib/argv_split.zig",
                "tools/lib/cmdline.zig",
                "tools/lib/ctype.zig",
                "tools/lib/hweight.zig",
                "tools/lib/list_sort.zig",
                "tools/lib/slab.zig",
                "tools/lib/str_error_r.zig",
                "tools/lib/vsprintf.zig",
                "tools/lib/zalloc.zig",
            ],
            MANIFEST_REL.as_posix(),
        )
    )
    issues.extend(
        expect_value(
            manifest,
            ("lane_sequencing", "direct_anchor_followup_helpers"),
            [
                "tools/lib/bitmap.zig",
                "tools/lib/find_bit.zig",
                "tools/lib/rbtree.zig",
                "tools/lib/string.zig",
            ],
            MANIFEST_REL.as_posix(),
        )
    )
    issues.extend(
        expect_value(
            manifest,
            ("lane_sequencing", "shared_replay_parked_helper_count"),
            None,
            MANIFEST_REL.as_posix(),
        )
        if nested_get(manifest, ("lane_sequencing", "shared_replay_parked_helper_count")) is not None
        else []
    )
    return issues


def collect_replay_blocker_issues(blockers: object) -> list[str]:
    if not isinstance(blockers, dict):
        return [f"{REPLAY_BLOCKERS_REL.as_posix()}:expected=dict:actual={type(blockers).__name__}"]
    issues: list[str] = []
    issues.extend(expect_value(blockers, ("status",), "parked", REPLAY_BLOCKERS_REL.as_posix()))
    issues.extend(
        expect_value(
            blockers,
            ("lane_sequencing", "shared_replay_parked_helper_count"),
            EXPECTED_SHARED_REPLAY_PARKED_HELPER_COUNT,
            REPLAY_BLOCKERS_REL.as_posix(),
        )
    )
    issues.extend(
        expect_value(
            blockers,
            ("lane_sequencing", "direct_anchor_followup_helper_count"),
            EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPER_COUNT,
            REPLAY_BLOCKERS_REL.as_posix(),
        )
    )
    issues.extend(expect_value(blockers, ("replay", "path"), EXPECTED_REPLAY_PATH, REPLAY_BLOCKERS_REL.as_posix()))
    issues.extend(expect_value(blockers, ("replay", "state"), EXPECTED_REPLAY_STATUS, REPLAY_BLOCKERS_REL.as_posix()))
    issues.extend(
        expect_value(
            blockers,
            ("c_harness", "path"),
            EXPECTED_C_HARNESS_PATH,
            REPLAY_BLOCKERS_REL.as_posix(),
        )
    )
    issues.extend(
        expect_value(
            blockers,
            ("c_harness", "state"),
            EXPECTED_C_HARNESS_STATUS,
            REPLAY_BLOCKERS_REL.as_posix(),
        )
    )
    issues.extend(
        expect_value(
            blockers,
            ("c_harness", "blocker_id"),
            EXPECTED_C_HARNESS_BLOCKER_ID,
            REPLAY_BLOCKERS_REL.as_posix(),
        )
    )

    replay_entries = nested_get(blockers, ("replay", "blockers"))
    if not isinstance(replay_entries, list) or len(replay_entries) != 1:
        issues.append(
            f"{REPLAY_BLOCKERS_REL.as_posix()}:replay.blockers:expected_length=1:actual={0 if not isinstance(replay_entries, list) else len(replay_entries)}"
        )
        return issues
    replay_entry = replay_entries[0]
    if not isinstance(replay_entry, dict):
        issues.append(f"{REPLAY_BLOCKERS_REL.as_posix()}:replay.blockers[0]:expected=dict")
        return issues
    if replay_entry.get("id") != EXPECTED_REPLAY_BLOCKER_ID:
        issues.append(
            f"{REPLAY_BLOCKERS_REL.as_posix()}:replay.blockers[0].id:expected={EXPECTED_REPLAY_BLOCKER_ID!r}:actual={replay_entry.get('id')!r}"
        )
    if replay_entry.get("field") != EXPECTED_REPLAY_BLOCKER_FIELD:
        issues.append(
            f"{REPLAY_BLOCKERS_REL.as_posix()}:replay.blockers[0].field:expected={EXPECTED_REPLAY_BLOCKER_FIELD!r}:actual={replay_entry.get('field')!r}"
        )
    return issues


def collect_issues(root: Path) -> list[str]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return [f"missing_file:{path}" for path in missing_files]

    issues: list[str] = []
    issues.extend(collect_marker_issues(read_text(root, TESTS_README_REL), TESTS_README_REL.as_posix(), README_MARKERS))
    issues.extend(collect_marker_issues(read_text(root, SCRIPTS_README_REL), SCRIPTS_README_REL.as_posix(), SCRIPTS_README_MARKERS))
    issues.extend(collect_marker_issues(read_text(root, LANE_NOTE_REL), LANE_NOTE_REL.as_posix(), LANE_NOTE_MARKERS))
    issues.extend(collect_marker_issues(read_text(root, PHASE1_CLOSURE_REL), PHASE1_CLOSURE_REL.as_posix(), PHASE1_CLOSURE_MARKERS))
    issues.extend(collect_marker_issues(read_text(root, BUILD_REL), BUILD_REL.as_posix(), BUILD_MARKERS))
    issues.extend(collect_marker_issues(read_text(root, SMOKE_REL), SMOKE_REL.as_posix(), SMOKE_MARKERS))
    issues.extend(
        collect_marker_issues(
            read_text(root, WORKFLOW_REL),
            WORKFLOW_REL.as_posix(),
            WORKFLOW_MARKERS,
            stripped=True,
        )
    )
    issues.extend(collect_marker_issues(read_text(root, MAKEFILE_REL), MAKEFILE_REL.as_posix(), MAKEFILE_MARKERS))
    issues.extend(collect_manifest_issues(read_json(root, MANIFEST_REL)))
    issues.extend(collect_replay_blocker_issues(read_json(root, REPLAY_BLOCKERS_REL)))
    return issues


def write_text(root: Path, relative_path: Path, content: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def sample_manifest() -> str:
    data = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": EXPECTED_HELPER_COUNT,
        "helpers": [
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
        ],
        "lane_sequencing": {
            "shared_replay_parked_helpers": [
                "tools/lib/argv_split.zig",
                "tools/lib/cmdline.zig",
                "tools/lib/ctype.zig",
                "tools/lib/hweight.zig",
                "tools/lib/list_sort.zig",
                "tools/lib/slab.zig",
                "tools/lib/str_error_r.zig",
                "tools/lib/vsprintf.zig",
                "tools/lib/zalloc.zig",
            ],
            "direct_anchor_followup_helpers": [
                "tools/lib/bitmap.zig",
                "tools/lib/find_bit.zig",
                "tools/lib/rbtree.zig",
                "tools/lib/string.zig",
            ],
        },
    }
    return json.dumps(data, indent=2) + "\n"


def sample_replay_blockers() -> str:
    data = {
        "status": "parked",
        "lane_sequencing": {
            "shared_replay_parked_helper_count": EXPECTED_SHARED_REPLAY_PARKED_HELPER_COUNT,
            "direct_anchor_followup_helper_count": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPER_COUNT,
        },
        "replay": {
            "path": EXPECTED_REPLAY_PATH,
            "state": EXPECTED_REPLAY_STATUS,
            "blockers": [
                {
                    "id": EXPECTED_REPLAY_BLOCKER_ID,
                    "field": EXPECTED_REPLAY_BLOCKER_FIELD,
                }
            ],
        },
        "c_harness": {
            "path": EXPECTED_C_HARNESS_PATH,
            "state": EXPECTED_C_HARNESS_STATUS,
            "blocker_id": EXPECTED_C_HARNESS_BLOCKER_ID,
        },
    }
    return json.dumps(data, indent=2) + "\n"


def build_sample_root(root: Path) -> None:
    write_text(root, TESTS_README_REL, "\n".join(README_MARKERS) + "\n")
    write_text(root, SCRIPTS_README_REL, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(root, LANE_NOTE_REL, "\n".join(LANE_NOTE_MARKERS) + "\n")
    write_text(root, PHASE1_CLOSURE_REL, "\n".join(PHASE1_CLOSURE_MARKERS) + "\n")
    write_text(root, BUILD_REL, "\n".join(BUILD_MARKERS) + "\n")
    write_text(root, SMOKE_REL, "\n".join(SMOKE_MARKERS) + "\n")
    write_text(root, WORKFLOW_REL, "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(root, MAKEFILE_REL, "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(root, MANIFEST_REL, sample_manifest())
    write_text(root, REPLAY_BLOCKERS_REL, sample_replay_blockers())


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_json_field(root: Path, relative_path: Path, path: tuple[str, ...]) -> None:
    target = root / relative_path
    data = json.loads(target.read_text(encoding="utf-8"))
    current = data
    for key in path[:-1]:
        current = current[key]
    last = path[-1]
    value = current[last]
    if isinstance(value, int):
        current[last] = value + 1
    elif isinstance(value, list):
        current[last] = value[:-1]
    else:
        current[last] = f"{value}-drift"
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object]] = [
        ("success", None),
        ("remove_tests_readme_marker", (TESTS_README_REL, README_MARKERS[0])),
        ("remove_scripts_readme_marker", (SCRIPTS_README_REL, SCRIPTS_README_MARKERS[0])),
        ("remove_lane_note_marker", (LANE_NOTE_REL, LANE_NOTE_MARKERS[0])),
        ("remove_closure_marker", (PHASE1_CLOSURE_REL, PHASE1_CLOSURE_MARKERS[0])),
        ("remove_build_marker", (BUILD_REL, BUILD_MARKERS[0])),
        ("remove_smoke_marker", (SMOKE_REL, SMOKE_MARKERS[0])),
        ("remove_workflow_marker", (WORKFLOW_REL, WORKFLOW_MARKERS[0])),
        ("remove_makefile_marker", (MAKEFILE_REL, MAKEFILE_MARKERS[0])),
        ("manifest_helper_count_drift", ("manifest", ("helper_count",))),
        ("manifest_direct_helpers_drift", ("manifest", ("lane_sequencing", "direct_anchor_followup_helpers"))),
        ("replay_status_drift", ("blockers", ("replay", "state"))),
        ("replay_helper_count_drift", ("blockers", ("lane_sequencing", "shared_replay_parked_helper_count"))),
    ]

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-tests-readme-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            if isinstance(mutation, tuple) and len(mutation) == 2 and isinstance(mutation[0], Path):
                remove_marker(root, mutation[0], mutation[1])
            elif isinstance(mutation, tuple) and mutation[0] == "manifest":
                mutate_json_field(root, MANIFEST_REL, mutation[1])
            elif isinstance(mutation, tuple) and mutation[0] == "blockers":
                mutate_json_field(root, REPLAY_BLOCKERS_REL, mutation[1])

            issues = collect_issues(root)
            if name == "success":
                if issues:
                    print("self-test:success:unexpected_failures")
                    for issue in issues:
                        print(issue)
                    return 1
            elif not issues:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_TESTS_README_PACKET_SELF_TEST=pass")
    print(f"PHASE1_TESTS_README_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic checker coverage")
    parser.add_argument("--write-sample-root", help="write a sample root and exit")
    args = parser.parse_args()

    if args.write_sample_root:
        build_sample_root(Path(args.write_sample_root).resolve())
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_TESTS_README_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_TESTS_README_PACKET=pass")
    print(f"PHASE1_TESTS_README_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_TESTS_README_PACKET_MARKER_COUNT={len(README_MARKERS) + len(SCRIPTS_README_MARKERS) + len(LANE_NOTE_MARKERS) + len(PHASE1_CLOSURE_MARKERS) + len(BUILD_MARKERS) + len(SMOKE_MARKERS) + len(WORKFLOW_MARKERS) + len(MAKEFILE_MARKERS)}")
    print(f"PHASE1_TESTS_README_PACKET_HELPER_COUNT={EXPECTED_HELPER_COUNT}")
    print(f"PHASE1_TESTS_README_PACKET_SHARED_REPLAY_PARKED_HELPER_COUNT={EXPECTED_SHARED_REPLAY_PARKED_HELPER_COUNT}")
    print(f"PHASE1_TESTS_README_PACKET_DIRECT_ANCHOR_HELPER_COUNT={EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPER_COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
