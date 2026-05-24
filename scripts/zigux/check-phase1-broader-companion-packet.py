#!/usr/bin/env python3
"""Guard the current Phase 1 broader-companion packet across reminder surfaces."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
PHASE1_CLOSURE = Path("Documentation/zigux/phase1-closure.md")
DOCS_README = Path("Documentation/zigux/README.md")
SHARED_REMINDER = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
BENCH_CHECKER = Path("scripts/zigux/check-phase1-bench.py")
CLOSURE_VALIDATOR = Path("scripts/zigux/validate-phase1-closure.py")
MANIFEST = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS = Path("zigux/tests/fixtures/phase1_replay_blockers.json")

REQUIRED_FILES = (
    SCRIPTS_README,
    TESTS_README,
    PHASE1_CLOSURE,
    DOCS_README,
    SHARED_REMINDER,
    BENCH_CHECKER,
    CLOSURE_VALIDATOR,
    MANIFEST,
    BLOCKERS,
)

BROADER_COMPANION_PACKET = [
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
]

SHARED_REPLAY_PARKED_HELPERS = [
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

DIRECT_ANCHOR_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

REQUIRED_EXACT_LINES = {
    SCRIPTS_README: [
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ],
    TESTS_README: [
        "* current direct-readback Phase 1 reminder packet:",
        "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
        "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ],
    PHASE1_CLOSURE: [
        "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "This note keeps those broader companions parked as historical closure-stack vocabulary until direct current-master rereads restore them. The already-landed shared tests-root smoke route plus the shipped bench checker and shared reminder checker remain the narrower packet that current `master` can support directly.",
    ],
    DOCS_README: [
        "keep the live owner map, the restored closure note and closure validator, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
        "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
        "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    ],
    BENCH_CHECKER: [
        "RBTREE_REQUIRED_EXACT_CHECKSUMS = {",
        "FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {",
    ],
    SHARED_REMINDER: [
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
        'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")',
    ],
    CLOSURE_VALIDATOR: [
        "PHASE1_CLOSURE_VALIDATION=pass",
        "PHASE1_CLOSURE_SELF_TEST=pass",
    ],
}

FORBIDDEN_FRAGMENTS = (
    "as active tests-root proof inside this direct-readback reminder packet and as current shared smoke-route proof",
    "treat those installer-backed, older validator-first, parity, and replay routes as current direct current-`master` reminder evidence",
    "the other nine closed helpers stay parked unless the shared replay or reminder packet drifts or a shared direct-anchor batch becomes convenient",
)

MANIFEST_EXPECTATIONS = {
    ("phase",): "Phase 1",
    ("status",): "closed",
    ("helper_count",): 13,
    ("lane_sequencing", "shared_replay_parked_helpers"): SHARED_REPLAY_PARKED_HELPERS,
    ("lane_sequencing", "direct_anchor_followup_helpers"): DIRECT_ANCHOR_HELPERS,
}

BLOCKER_EXPECTATIONS = {
    ("status",): "parked",
    ("lane_sequencing", "manifest"): "zigux/tests/fixtures/phase1_helper_manifest.json",
    ("lane_sequencing", "shared_replay_parked_helper_count"): 9,
    ("lane_sequencing", "shared_replay_parked_helpers"): SHARED_REPLAY_PARKED_HELPERS,
    ("lane_sequencing", "direct_anchor_followup_helper_count"): 4,
    ("lane_sequencing", "direct_anchor_followup_helpers"): DIRECT_ANCHOR_HELPERS,
    ("replay", "path"): "zigux/tests/phase1_helpers.zig",
    ("replay", "state"): "blocked",
    ("replay", "blockers", 0, "id"): "phase1_helpers_zig_slab_zero_after_kmalloc",
    ("replay", "blockers", 0, "kind"): "fixture_mismatch",
    ("replay", "blockers", 0, "path"): "tools/lib/slab.zig",
    ("replay", "blockers", 0, "field"): "slab.zero_after_kmalloc",
    ("replay", "blockers", 0, "expected"): True,
    ("replay", "blockers", 0, "actual"): False,
    ("c_harness", "path"): "zigux/tests/fixtures/phase1_helpers_c_harness.c",
    ("c_harness", "state"): "blocked",
    ("c_harness", "helper_count"): 13,
    ("c_harness", "helpers"): SHARED_REPLAY_PARKED_HELPERS + DIRECT_ANCHOR_HELPERS,
    ("c_harness", "blocker_id"): "phase1_helpers_c_harness_missing_c_sources",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def write_text(root: Path, relative_path: Path, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    want = line.strip()
    count = sum(1 for current in text.splitlines() if current.strip() == want)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_fragment(text: str, label: str, fragment: str) -> list[str]:
    count = text.count(fragment)
    return [] if count == 0 else [f"{label}:forbidden:{fragment}:actual={count}"]


def nested_value(data: object, path: tuple[object, ...]) -> object:
    current = data
    for key in path:
        if isinstance(key, int):
            if not isinstance(current, list) or key >= len(current):
                return None
            current = current[key]
            continue
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, lines in REQUIRED_EXACT_LINES.items():
        text = read_text(root, relative_path)
        for index, line in enumerate(lines):
            failures.extend(
                require_exact_line(text, f"{relative_path.as_posix()}:line_{index}", line)
            )
        for fragment in FORBIDDEN_FRAGMENTS:
            failures.extend(
                require_absent_fragment(text, relative_path.as_posix(), fragment)
            )

    manifest = json.loads(read_text(root, MANIFEST))
    blockers = json.loads(read_text(root, BLOCKERS))

    for path, expected in MANIFEST_EXPECTATIONS.items():
        failures.extend(
            require_exact_value(
                f"{MANIFEST.as_posix()}:{'.'.join(str(part) for part in path)}",
                nested_value(manifest, path),
                expected,
            )
        )

    for path, expected in BLOCKER_EXPECTATIONS.items():
        failures.extend(
            require_exact_value(
                f"{BLOCKERS.as_posix()}:{'.'.join(str(part) for part in path)}",
                nested_value(blockers, path),
                expected,
            )
        )

    return failures


def sample_manifest() -> str:
    return json.dumps(
        {
            "phase": "Phase 1",
            "status": "closed",
            "helper_count": 13,
            "lane_sequencing": {
                "shared_replay_parked_helpers": SHARED_REPLAY_PARKED_HELPERS,
                "direct_anchor_followup_helpers": DIRECT_ANCHOR_HELPERS,
            },
        },
        indent=2,
    ) + "\n"


def sample_blockers() -> str:
    return json.dumps(
        {
            "status": "parked",
            "lane_sequencing": {
                "manifest": "zigux/tests/fixtures/phase1_helper_manifest.json",
                "shared_replay_parked_helper_count": 9,
                "shared_replay_parked_helpers": SHARED_REPLAY_PARKED_HELPERS,
                "direct_anchor_followup_helper_count": 4,
                "direct_anchor_followup_helpers": DIRECT_ANCHOR_HELPERS,
            },
            "replay": {
                "path": "zigux/tests/phase1_helpers.zig",
                "state": "blocked",
                "blockers": [
                    {
                        "id": "phase1_helpers_zig_slab_zero_after_kmalloc",
                        "kind": "fixture_mismatch",
                        "path": "tools/lib/slab.zig",
                        "field": "slab.zero_after_kmalloc",
                        "expected": True,
                        "actual": False,
                    }
                ],
            },
            "c_harness": {
                "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
                "state": "blocked",
                "helper_count": 13,
                "helpers": SHARED_REPLAY_PARKED_HELPERS + DIRECT_ANCHOR_HELPERS,
                "blocker_id": "phase1_helpers_c_harness_missing_c_sources",
            },
        },
        indent=2,
    ) + "\n"


def build_sample_root(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == MANIFEST:
            write_text(root, relative_path, sample_manifest())
            continue
        if relative_path == BLOCKERS:
            write_text(root, relative_path, sample_blockers())
            continue
        lines = REQUIRED_EXACT_LINES.get(relative_path, [])
        body = "# sample\n\n" + "\n".join(lines) + ("\n" if lines else "")
        write_text(root, relative_path, body)


def write_sample_root(destination: Path) -> None:
    build_sample_root(destination)


def mutate_remove_line(root: Path, relative_path: Path, line: str) -> None:
    target = root / relative_path
    lines = target.read_text(encoding="utf-8").splitlines()
    needle = line.strip()
    for index, current in enumerate(lines):
        if current.strip() == needle:
            del lines[index]
            target.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            return


def mutate_duplicate_line(root: Path, relative_path: Path, line: str) -> None:
    target = root / relative_path
    lines = target.read_text(encoding="utf-8").splitlines()
    needle = line.strip()
    for index, current in enumerate(lines):
        if current.strip() == needle:
            lines.insert(index + 1, current)
            target.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return


def mutate_json_path(root: Path, relative_path: Path, path: tuple[object, ...]) -> None:
    data = json.loads((root / relative_path).read_text(encoding="utf-8"))
    current = data
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[:-1]
    elif isinstance(value, bool):
        current[final_key] = not value
    elif isinstance(value, int):
        current[final_key] = value + 1
    else:
        current[final_key] = f"{value}-drift"
    write_text(root, relative_path, json.dumps(data, indent=2) + "\n")


def run_self_test() -> int:
    cases = [("success", None, None, None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", "missing_file", relative_path, None))

    for relative_path, lines in REQUIRED_EXACT_LINES.items():
        for index, line in enumerate(lines):
            cases.append((f"remove_line:{relative_path.as_posix()}:{index}", "remove_line", relative_path, line))
            cases.append((f"duplicate_line:{relative_path.as_posix()}:{index}", "duplicate_line", relative_path, line))

    for path in MANIFEST_EXPECTATIONS:
        cases.append((f"manifest_drift:{path}", "manifest_drift", MANIFEST, path))

    for path in BLOCKER_EXPECTATIONS:
        cases.append((f"blocker_drift:{path}", "blocker_drift", BLOCKERS, path))

    with tempfile.TemporaryDirectory(prefix="phase1-broader-companion-") as tmpdir:
        baseline = Path(tmpdir) / "baseline"
        build_sample_root(baseline)
        if collect_failures(baseline):
            print("self-test:baseline:unexpected_failures")
            for failure in collect_failures(baseline):
                print(failure)
            return 1

    for name, mode, relative_path, payload in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-broader-companion-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)

            if mode == "missing_file":
                assert relative_path is not None
                (root / relative_path).unlink()
            elif mode == "remove_line":
                assert isinstance(relative_path, Path)
                assert isinstance(payload, str)
                mutate_remove_line(root, relative_path, payload)
            elif mode == "duplicate_line":
                assert isinstance(relative_path, Path)
                assert isinstance(payload, str)
                mutate_duplicate_line(root, relative_path, payload)
            elif mode == "manifest_drift":
                assert isinstance(payload, tuple)
                mutate_json_path(root, MANIFEST, payload)
            elif mode == "blocker_drift":
                assert isinstance(payload, tuple)
                mutate_json_path(root, BLOCKERS, payload)

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_BROADER_COMPANION_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BROADER_COMPANION_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root used for checks")
    parser.add_argument(
        "--write-sample-root",
        help="write a synthetic current-like sample root to the given directory",
    )
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        write_sample_root(destination)
        print(f"PHASE1_BROADER_COMPANION_PACKET_SAMPLE_ROOT={destination}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BROADER_COMPANION_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BROADER_COMPANION_PACKET=pass")
    print(f"PHASE1_BROADER_COMPANION_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BROADER_COMPANION_PACKET_REQUIRED_LINE_COUNT="
        f"{sum(len(lines) for lines in REQUIRED_EXACT_LINES.values())}"
    )
    print(
        "PHASE1_BROADER_COMPANION_PACKET_BROADER_COMPANION_COUNT="
        f"{len(BROADER_COMPANION_PACKET)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
