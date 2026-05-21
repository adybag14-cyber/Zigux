#!/usr/bin/env python3
"""Guard the current docs-root Phase 1 Lane 09 reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers.json",
    "zigux/Makefile",
)

DOCS_MARKERS = (
    "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "keep the live owner map, the restored closure note and closure validator, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12.",
    "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
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

EXPECTED_SHARED_REPLAY_HELPERS = [
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

EXPECTED_DIRECT_ANCHOR_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

EXPECTED_RULE_SUMMARY = (
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while "
    "bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up "
    "anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay "
    "parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for "
    "their existing helper-local anchors or already-committed shared fixture keys."
)

EXPECTED_FIXTURE_TOP_LEVEL_KEYS = [
    "find_bit",
    "bitmap",
    "string",
    "rbtree",
    "argv_split",
    "cmdline",
    "ctype",
    "hweight",
    "list_sort",
    "zalloc",
    "str_error_r",
    "slab",
    "vsprintf",
]

EXPECTED_FIXTURE_SENTINELS = {
    ("bitmap", "scnprintf"): "1-3,7,10-11",
    ("bitmap", "partial_xor_nbits"): 4,
    ("string", "replace_char_cstr_bytes"): [97, 95, 0, 45, 122],
    ("find_bit", "tail_clamped_last"): 67,
    ("rbtree", "cached_leftmost_return_serials"): [0, -1, 2, -1],
    ("argv_split", "argv"): ["alpha", "beta", "gamma"],
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: str) -> object:
    return json.loads(read_text(root, relative_path))


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).exists()]


def collect_exact_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if failures:
        return failures

    docs_text = read_text(root, "Documentation/zigux/README.md")
    failures.extend(collect_exact_markers(docs_text, "Documentation/zigux/README.md", DOCS_MARKERS))

    manifest = load_json(root, "zigux/tests/fixtures/phase1_helper_manifest.json")
    if not isinstance(manifest, dict):
        return ["phase1_helper_manifest.json:expected=dict"]

    failures.extend(check_manifest(manifest))

    fixture = load_json(root, "zigux/tests/fixtures/phase1_helpers.json")
    if not isinstance(fixture, dict):
        return ["phase1_helpers.json:expected=dict"]

    failures.extend(check_fixture(fixture))
    return failures


def check_manifest(manifest: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if manifest.get("phase") != "Phase 1":
        issues.append(f"manifest:phase:expected='Phase 1':actual={manifest.get('phase')!r}")
    if manifest.get("status") != "closed":
        issues.append(f"manifest:status:expected='closed':actual={manifest.get('status')!r}")
    if manifest.get("helper_count") != 13:
        issues.append(f"manifest:helper_count:expected=13:actual={manifest.get('helper_count')!r}")

    helpers = manifest.get("helpers")
    if helpers != EXPECTED_HELPERS:
        issues.append(f"manifest:helpers:expected={EXPECTED_HELPERS!r}:actual={helpers!r}")

    lane = manifest.get("lane_sequencing")
    if not isinstance(lane, dict):
        issues.append("manifest:lane_sequencing:expected=dict")
        return issues

    if lane.get("shared_replay_parked_helpers") != EXPECTED_SHARED_REPLAY_HELPERS:
        issues.append(
            "manifest:lane_sequencing.shared_replay_parked_helpers:"
            f"expected={EXPECTED_SHARED_REPLAY_HELPERS!r}:actual={lane.get('shared_replay_parked_helpers')!r}"
        )
    if lane.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_ANCHOR_HELPERS:
        issues.append(
            "manifest:lane_sequencing.direct_anchor_followup_helpers:"
            f"expected={EXPECTED_DIRECT_ANCHOR_HELPERS!r}:actual={lane.get('direct_anchor_followup_helpers')!r}"
        )
    if lane.get("rule_summary") != EXPECTED_RULE_SUMMARY:
        issues.append(
            "manifest:lane_sequencing.rule_summary:"
            f"expected={EXPECTED_RULE_SUMMARY!r}:actual={lane.get('rule_summary')!r}"
        )
    if lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        issues.append(
            "manifest:lane_sequencing.anti_overlap_rule:"
            f"expected={EXPECTED_ANTI_OVERLAP_RULE!r}:actual={lane.get('anti_overlap_rule')!r}"
        )
    return issues


def check_fixture(fixture: dict[str, object]) -> list[str]:
    issues: list[str] = []
    keys = list(fixture.keys())
    if keys != EXPECTED_FIXTURE_TOP_LEVEL_KEYS:
        issues.append(f"fixture:top_level_keys:expected={EXPECTED_FIXTURE_TOP_LEVEL_KEYS!r}:actual={keys!r}")

    for path, expected in EXPECTED_FIXTURE_SENTINELS.items():
        actual = nested_value(fixture, path)
        if actual != expected:
            joined = ".".join(path)
            issues.append(f"fixture:{joined}:expected={expected!r}:actual={actual!r}")
    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    docs_body = "\n".join(DOCS_MARKERS) + "\n"
    write_text(root, "Documentation/zigux/README.md", docs_body)
    write_text(root, "Documentation/zigux/phase1-closure.md", "phase1 closure marker\n")
    write_text(root, "Documentation/zigux/review-checklist.md", "review checklist marker\n")
    write_text(root, "scripts/zigux/README.md", "scripts readme marker\n")
    write_text(root, "scripts/zigux/check-phase1-bench.py", "bench marker\n")
    write_text(root, "scripts/zigux/check-phase1-direct-owner-markers.py", "owner marker\n")
    write_text(root, "scripts/zigux/check-phase1-shared-reminder-packet.py", "shared reminder marker\n")
    write_text(root, "scripts/zigux/check-phase1-string-review-packet.py", "string review marker\n")
    write_text(root, "scripts/zigux/validate-phase1-closure.py", "closure validator marker\n")
    write_text(root, "zigux/tests/README.md", "tests readme marker\n")
    write_text(root, "zigux/Makefile", "phase2-toolchain:\n")
    write_text(
        root,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": 13,
                "helpers": EXPECTED_HELPERS,
                "lane_sequencing": {
                    "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_HELPERS,
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_HELPERS,
                    "rule_summary": EXPECTED_RULE_SUMMARY,
                    "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
                },
            },
            indent=2,
        )
        + "\n",
    )
    fixture = {key: {} for key in EXPECTED_FIXTURE_TOP_LEVEL_KEYS}
    for path, value in EXPECTED_FIXTURE_SENTINELS.items():
        fixture.setdefault(path[0], {})
        fixture[path[0]][path[1]] = value
    write_text(
        root,
        "zigux/tests/fixtures/phase1_helpers.json",
        json.dumps(fixture, separators=(",", ":")) + "\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-docs-readme-packet-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_root(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for item in failures:
                print(item)
            return 1
        case_count += 1

    mutations = (
        ("missing_required_file", mutate_missing_required_file),
        ("missing_docs_marker", mutate_missing_docs_marker),
        ("duplicate_docs_marker", mutate_duplicate_docs_marker),
        ("manifest_helper_count", mutate_manifest_helper_count),
        ("manifest_direct_anchor_list", mutate_manifest_direct_anchor_list),
        ("fixture_sentinel", mutate_fixture_sentinel),
        ("fixture_top_level_keys", mutate_fixture_top_level_keys),
    )

    for name, mutate in mutations:
        with tempfile.TemporaryDirectory(prefix=f"phase1-docs-readme-packet-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            mutate(root)
            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1
            case_count += 1

    print("PHASE1_DOCS_README_PACKET_SELF_TEST=pass")
    print(f"PHASE1_DOCS_README_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def mutate_missing_required_file(root: Path) -> None:
    (root / REQUIRED_FILES[0]).unlink()


def mutate_missing_docs_marker(root: Path) -> None:
    target = root / "Documentation/zigux/README.md"
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(DOCS_MARKERS[0] + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_docs_marker(root: Path) -> None:
    target = root / "Documentation/zigux/README.md"
    text = target.read_text(encoding="utf-8")
    marker = DOCS_MARKERS[1]
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def mutate_manifest_helper_count(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["helper_count"] = 12
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mutate_manifest_direct_anchor_list(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["lane_sequencing"]["direct_anchor_followup_helpers"] = ["tools/lib/bitmap.zig"]
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mutate_fixture_sentinel(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_helpers.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["bitmap"]["scnprintf"] = "drift"
    path.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")


def mutate_fixture_top_level_keys(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_helpers.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["vsprintf"]
    path.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")


def write_sample_root(destination: Path) -> None:
    build_sample_root(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", help="write a current-like sample repo root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        write_sample_root(destination)
        print(f"phase1-docs-readme-packet:sample-root-written:{destination}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_DOCS_README_PACKET=fail")
        for item in failures:
            print(item)
        return 1

    print("PHASE1_DOCS_README_PACKET=pass")
    print(f"PHASE1_DOCS_README_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_DOCS_README_PACKET_REQUIRED_MARKER_COUNT={len(DOCS_MARKERS)}")
    print(f"PHASE1_DOCS_README_PACKET_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_DOCS_README_PACKET_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_REPLAY_HELPERS)}")
    print(f"PHASE1_DOCS_README_PACKET_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_ANCHOR_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
