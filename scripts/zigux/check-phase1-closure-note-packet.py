#!/usr/bin/env python3
"""Guard the current Phase 1 closure-note packet against reminder-surface drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
PHASE1_CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
PHASE1_BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
TESTS_README_REL = Path("zigux/tests/README.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
ZIGUX_MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    PHASE1_LANE_NOTE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    PHASE1_CLOSURE_VALIDATOR_REL,
    PHASE1_BENCH_CHECKER_REL,
    DIRECT_OWNER_CHECKER_REL,
    SHARED_REMINDER_CHECKER_REL,
    STRING_REVIEW_CHECKER_REL,
    TESTS_README_REL,
    MANIFEST_REL,
    ZIGUX_MAKEFILE_REL,
)

EXPECTED_HELPERS = [
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
]

EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_LANE_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
    "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
)

EXPECTED_CLOSURE_MARKERS = (
    "`PHASE1_STATUS=parked`",
    "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "`PHASE1_HELPER_COUNT=13`",
    "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.",
    "- `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "- `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`",
)

EXPECTED_DOCS_ROOT_MARKERS = (
    "- `Documentation/zigux/phase1-closure.md`",
    "- `scripts/zigux/validate-phase1-closure.py`",
    "keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    "`python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks",
)

EXPECTED_REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 1 host-tools closure packet",
    "`scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "keep `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `zigux/Makefile` explicit as the adjacent Phase 1 route-summary evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?`",
)

EXPECTED_SCRIPTS_README_MARKERS = (
    "`python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "`scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    "`zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded returned `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
)

EXPECTED_TESTS_README_MARKERS = (
    "current direct-readback Phase 1 reminder packet:",
    "- `Documentation/zigux/phase1-closure.md`",
    "- `scripts/zigux/validate-phase1-closure.py`",
    "* current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
)

EXPECTED_LANE_NOTE_MARKERS = (
    "`PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`",
    "`PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
    "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
)

EXPECTED_VALIDATOR_MARKERS = (
    "PHASE1_CLOSURE_VALIDATION=pass",
    "PHASE1_CLOSURE_SELF_TEST=pass",
)

EXPECTED_BENCH_CHECKER_MARKERS = (
    "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
    "def run_self_test() -> None:",
)

EXPECTED_DIRECT_OWNER_CHECKER_MARKERS = (
    "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
    'print("PHASE1_DIRECT_OWNER_MARKERS=pass")',
)

EXPECTED_SHARED_REMINDER_CHECKER_MARKERS = (
    '"""Guard the current shared Phase 1 reminder packet across docs, tests, scripts, and workflow."""',
    'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
)

EXPECTED_STRING_REVIEW_CHECKER_MARKERS = (
    "EXPECTED_STRING_SOURCE_SYMBOLS = [",
    "EXPECTED_HELPER_TEST_ANCHORS = [",
    'print("phase1-string-review-packet:ok")',
)

EXPECTED_MAKEFILE_MARKERS = (
    "phase1-route-summary:",
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase3-validate:",
    "phase3:",
    "phase4-validate:",
    "phase6-validate:",
    "phase8-validate:",
    "phase8-exec-cmd-test:",
    "phase8-test:",
    "phase10-validate:",
    "phase10-test:",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "phase14-validate:",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
)


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def collect_missing_files(root: Path) -> list[str]:
    return [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]


def load_manifest(root: Path) -> DuplicateTrackingDict:
    return json.loads(read_text(root, MANIFEST_REL), object_pairs_hook=DuplicateTrackingDict)


def collect_manifest_failures(root: Path) -> list[str]:
    try:
        manifest = load_manifest(root)
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    failures: list[str] = []
    if manifest.duplicate_keys:
        failures.extend(f"{MANIFEST_REL.as_posix()}:duplicate_key:{key}" for key in manifest.duplicate_keys)
        return failures
    if manifest.get("phase") != "Phase 1":
        failures.append(f"{MANIFEST_REL.as_posix()}:phase:{manifest.get('phase')!r}")
    if manifest.get("status") != "closed":
        failures.append(f"{MANIFEST_REL.as_posix()}:status:{manifest.get('status')!r}")
    if manifest.get("helper_count") != 13:
        failures.append(f"{MANIFEST_REL.as_posix()}:helper_count:{manifest.get('helper_count')!r}")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        failures.append(f"{MANIFEST_REL.as_posix()}:helpers:drift")
    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        failures.append(f"{MANIFEST_REL.as_posix()}:lane_sequencing:type={type(lane_sequencing).__name__}")
        return failures
    if lane_sequencing.get("shared_replay_parked_helpers") != EXPECTED_SHARED_REPLAY_PARKED_HELPERS:
        failures.append(f"{MANIFEST_REL.as_posix()}:shared_replay_parked_helpers:drift")
    if lane_sequencing.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS:
        failures.append(f"{MANIFEST_REL.as_posix()}:direct_anchor_followup_helpers:drift")
    if lane_sequencing.get("rule_summary") != EXPECTED_LANE_RULE_SUMMARY:
        failures.append(f"{MANIFEST_REL.as_posix()}:rule_summary:drift")
    if lane_sequencing.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        failures.append(f"{MANIFEST_REL.as_posix()}:anti_overlap_rule:drift")
    return failures


def collect_failures(root: Path) -> list[str]:
    failures = collect_missing_files(root)
    if failures:
        return failures

    checks = (
        (PHASE1_CLOSURE_REL, EXPECTED_CLOSURE_MARKERS),
        (DOCS_ROOT_REL, EXPECTED_DOCS_ROOT_MARKERS),
        (REVIEW_CHECKLIST_REL, EXPECTED_REVIEW_CHECKLIST_MARKERS),
        (SCRIPTS_README_REL, EXPECTED_SCRIPTS_README_MARKERS),
        (TESTS_README_REL, EXPECTED_TESTS_README_MARKERS),
        (PHASE1_LANE_NOTE_REL, EXPECTED_LANE_NOTE_MARKERS),
        (PHASE1_CLOSURE_VALIDATOR_REL, EXPECTED_VALIDATOR_MARKERS),
        (PHASE1_BENCH_CHECKER_REL, EXPECTED_BENCH_CHECKER_MARKERS),
        (DIRECT_OWNER_CHECKER_REL, EXPECTED_DIRECT_OWNER_CHECKER_MARKERS),
        (SHARED_REMINDER_CHECKER_REL, EXPECTED_SHARED_REMINDER_CHECKER_MARKERS),
        (STRING_REVIEW_CHECKER_REL, EXPECTED_STRING_REVIEW_CHECKER_MARKERS),
    )
    for relative_path, markers in checks:
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_exact_occurrence(text, relative_path.as_posix(), marker))

    makefile_text = read_text(root, ZIGUX_MAKEFILE_REL)
    for marker in EXPECTED_MAKEFILE_MARKERS:
        failures.extend(require_exact_occurrence(makefile_text, ZIGUX_MAKEFILE_REL.as_posix(), marker))
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        count = makefile_text.count(marker)
        if count:
            failures.append(f"{ZIGUX_MAKEFILE_REL.as_posix()}:forbidden_marker:actual_count={count}:{marker}")

    failures.extend(collect_manifest_failures(root))
    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_sample_tree(root: Path) -> None:
    write_text(
        root / PHASE1_CLOSURE_REL,
        "# Phase 1 Closure\n\n" + "\n".join(EXPECTED_CLOSURE_MARKERS) + "\n",
    )
    write_text(
        root / DOCS_ROOT_REL,
        "# Zigux Documentation\n\n" + "\n".join(EXPECTED_DOCS_ROOT_MARKERS) + "\n",
    )
    write_text(
        root / REVIEW_CHECKLIST_REL,
        "# Zigux Review Checklist\n\n" + "\n".join(EXPECTED_REVIEW_CHECKLIST_MARKERS) + "\n",
    )
    write_text(
        root / SCRIPTS_README_REL,
        "# scripts/zigux\n\n" + "\n".join(EXPECTED_SCRIPTS_README_MARKERS) + "\n",
    )
    write_text(
        root / TESTS_README_REL,
        "# zigux/tests\n\n" + "\n".join(EXPECTED_TESTS_README_MARKERS) + "\n",
    )
    write_text(
        root / PHASE1_LANE_NOTE_REL,
        "# Phase 1 Host-Helper Lane Sequencing\n\n" + "\n".join(EXPECTED_LANE_NOTE_MARKERS) + "\n",
    )
    write_text(root / PHASE1_CLOSURE_VALIDATOR_REL, "\n".join(EXPECTED_VALIDATOR_MARKERS) + "\n")
    write_text(root / PHASE1_BENCH_CHECKER_REL, "\n".join(EXPECTED_BENCH_CHECKER_MARKERS) + "\n")
    write_text(root / DIRECT_OWNER_CHECKER_REL, "\n".join(EXPECTED_DIRECT_OWNER_CHECKER_MARKERS) + "\n")
    write_text(
        root / SHARED_REMINDER_CHECKER_REL,
        "\n".join(EXPECTED_SHARED_REMINDER_CHECKER_MARKERS) + "\n",
    )
    write_text(
        root / STRING_REVIEW_CHECKER_REL,
        "\n".join(EXPECTED_STRING_REVIEW_CHECKER_MARKERS) + "\n",
    )
    write_text(root / ZIGUX_MAKEFILE_REL, "\n".join(EXPECTED_MAKEFILE_MARKERS) + "\n")
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": 13,
                "helpers": EXPECTED_HELPERS,
                "lane_sequencing": {
                    "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                    "rule_summary": EXPECTED_LANE_RULE_SUMMARY,
                    "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    cases: list[tuple[str, callable[[Path], None] | None]] = [
        ("baseline", None),
        (
            "missing_closure_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                read_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_MARKERS[0] + "\n", "", 1),
            ),
        ),
        (
            "missing_docs_marker",
            lambda root: write_text(
                root / DOCS_ROOT_REL,
                read_text(root, DOCS_ROOT_REL).replace(EXPECTED_DOCS_ROOT_MARKERS[2] + "\n", "", 1),
            ),
        ),
        (
            "missing_makefile_route",
            lambda root: write_text(
                root / ZIGUX_MAKEFILE_REL,
                read_text(root, ZIGUX_MAKEFILE_REL).replace("phase12-smoke:\n", "", 1),
            ),
        ),
        (
            "forbidden_phase1_route",
            lambda root: write_text(
                root / ZIGUX_MAKEFILE_REL,
                read_text(root, ZIGUX_MAKEFILE_REL) + "phase1-validate:\n",
            ),
        ),
        (
            "bad_manifest_direct_helpers",
            lambda root: write_text(
                root / MANIFEST_REL,
                json.dumps(
                    {
                        **json.loads(read_text(root, MANIFEST_REL)),
                        "lane_sequencing": {
                            **json.loads(read_text(root, MANIFEST_REL))["lane_sequencing"],
                            "direct_anchor_followup_helpers": ["tools/lib/bitmap.zig"],
                        },
                    },
                    indent=2,
                )
                + "\n",
            ),
        ),
        (
            "missing_lane_note_packet_marker",
            lambda root: write_text(
                root / PHASE1_LANE_NOTE_REL,
                read_text(root, PHASE1_LANE_NOTE_REL).replace(EXPECTED_LANE_NOTE_MARKERS[2] + "\n", "", 1),
            ),
        ),
        (
            "missing_validator_marker",
            lambda root: write_text(root / PHASE1_CLOSURE_VALIDATOR_REL, "PHASE1_CLOSURE_SELF_TEST=pass\n"),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-note-packet-") as tmp:
            root = Path(tmp)
            make_sample_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-note-packet-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-note-packet-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_NOTE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_NOTE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample tree for local replay without a full checkout",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        sample_root = Path(args.write_sample_root).resolve()
        make_sample_tree(sample_root)
        print(f"PHASE1_CLOSURE_NOTE_PACKET_SAMPLE_ROOT={sample_root}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_NOTE_PACKET=pass")
    print("PHASE1_CLOSURE_NOTE_PACKET_MODE=current-like")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
