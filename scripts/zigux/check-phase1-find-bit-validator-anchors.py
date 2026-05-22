#!/usr/bin/env python3
"""Guard the Phase 1 find_bit helper-local validator packet against drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_README_REL = Path("Documentation/zigux/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")

REQUIRED_FILES = (
    FIND_BIT_HELPER_REL,
    MANIFEST_REL,
    FIXTURE_REL,
    LANE_NOTE_REL,
    PHASE1_CLOSURE_REL,
    DOCS_README_REL,
    SCRIPTS_README_REL,
)

REQUIRED_HELPER_ANCHORS = [
    'test "find first and next set bits across words, with andnot gaps explicit"',
    'test "single-word next scans honor start masks"',
    'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    'test "clump8 past-end scans return without reading bitmap words"',
    'test "getValue8 reads aligned bytes from bitmap words"',
    'test "find last bit scans backward across words"',
    'test "low-level underscore aliases mirror the primary find helpers, including andnot"',
    'test "Linux-style aliases mirror the primary find helpers, including andnot"',
]

REQUIRED_SCRIPTS_README_LINES = {
    "phase1_replay_line": "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
    "phase1_checker_packet": "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    "phase1_direct_anchor_split": "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
}

REQUIRED_DOCS_README_LINES = {
    "phase1_docs_packet": '* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.',
    "phase1_helper_split": "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
}

REQUIRED_LANE_NOTE_LINES = {
    "direct_owner": '- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), and findLastBit() byte-clump and backward-scan coverage, underscore-alias and Linux-style alias coverage including the shipped find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and _find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped and tail-inclusive-boundary find_bit replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`',
    "byte_clump_note": "- current `master` also keeps the helper-local `clump8`, `getValue8()`, and `findLastBit()` byte-clump and backward-scan proofs explicit in both `tools/lib/find_bit.zig` and the manifest's `helper_test_anchors` list, so nearby Phase 1 follow-through should keep those checks inside the same direct `find_bit` packet instead of splitting byte-clump or last-bit drift into a separate shared replay family",
    "next_safe_step": '- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`',
}

REQUIRED_CLOSURE_LINES = {
    "find_bit_tie_breaker": "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the manifest-backed review surface together with `Documentation/zigux/phase1-host-helper-lane-sequencing.md` keep that helper-local progress review-visible beside the narrower closure validator. That direct packet now also includes the explicit `clump8 past-end scans return without reading bitmap words` no-read anchor, so the byte-clump coverage is not limited to in-range or zero-bit windows. Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail windows keep the last in-range next matches reachable from an inclusive start` proof alongside the head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts.",
}

EXPECTED_FIND_BIT_PACKET = {
    "same_word_start_masks": 'test "single-word next scans honor start masks"',
    "inclusive_boundary_start": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "tail_word_inclusive_boundary_anchor": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start"',
    "zero_sized_short_circuit_anchor": 'test "zero-sized scans ignore populated backing words"',
    "past_nbits_short_circuit": 'test "next scans past nbits return without reading bitmap words"',
    "andnot_scan_entrypoints": [
        "findFirstAndNotBit",
        "find_first_andnot_bit",
        "_find_first_andnot_bit",
        "findNextAndNotBit",
        "find_next_andnot_bit",
        "_find_next_andnot_bit",
    ],
    "andnot_scan_entrypoint_contract": "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.",
    "tail_clamp_fixture_keys": [
        "tail_clamped_first",
        "tail_clamped_next",
        "tail_zero_clamped_first",
        "tail_zero_clamped_next",
        "tail_and_clamped_first",
        "tail_and_clamped_next",
        "tail_clamped_last",
        "tail_clamped_empty_last",
    ],
    "tail_inclusive_boundary_fixture_keys": [
        "tail_inclusive_boundary_next",
        "tail_inclusive_boundary_zero",
        "tail_inclusive_boundary_and",
    ],
    "review_packet_summary": "shared Phase 1 fixture keys own the exact tail-clamped and tail-inclusive-boundary find_bit replay, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, single-word tail inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master",
    "next_safe_step_note": "If this helper lane reopens, keep find_bit parked unless a fresh reread finds direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families.",
}

EXPECTED_FIND_BIT_FIXTURE = {
    "inclusive_boundary_next": 63,
    "inclusive_boundary_zero": 63,
    "inclusive_boundary_and": 63,
    "tail_inclusive_boundary_next": 68,
    "tail_inclusive_boundary_zero": 68,
    "tail_inclusive_boundary_and": 68,
    "past_nbits_next": 7,
    "past_nbits_zero": 7,
    "past_nbits_and": 7,
    "tail_clamped_first": 67,
    "tail_clamped_next": 69,
    "tail_zero_clamped_first": 69,
    "tail_zero_clamped_next": 69,
    "tail_and_clamped_first": 67,
    "tail_and_clamped_next": 69,
    "tail_clamped_last": 67,
    "tail_clamped_empty_last": 69,
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, FIND_BIT_HELPER_REL)
    for anchor in REQUIRED_HELPER_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"helper:{anchor}", anchor))

    scripts_readme = load_text(root, SCRIPTS_README_REL)
    for key, line in REQUIRED_SCRIPTS_README_LINES.items():
        failures.extend(require_exact_line(scripts_readme, f"scripts_readme:{key}", line))

    docs_readme = load_text(root, DOCS_README_REL)
    for key, line in REQUIRED_DOCS_README_LINES.items():
        failures.extend(require_exact_line(docs_readme, f"docs_readme:{key}", line))

    lane_note = load_text(root, LANE_NOTE_REL)
    for key, line in REQUIRED_LANE_NOTE_LINES.items():
        failures.extend(require_exact_line(lane_note, f"lane_note:{key}", line))

    closure = load_text(root, PHASE1_CLOSURE_REL)
    for key, line in REQUIRED_CLOSURE_LINES.items():
        failures.extend(require_exact_occurrence(closure, f"closure:{key}", line))

    manifest = load_json(root, MANIFEST_REL)
    for key, expected in EXPECTED_FIND_BIT_PACKET.items():
        failures.extend(
            require_exact_value(
                f"manifest:review_anchors.tools/lib/find_bit.zig.{key}",
                nested_value(manifest, ("review_anchors", "tools/lib/find_bit.zig", key)),
                expected,
            )
        )

    fixture = load_json(root, FIXTURE_REL)
    for key, expected in EXPECTED_FIND_BIT_FIXTURE.items():
        failures.extend(
            require_exact_value(
                f"fixture:find_bit.{key}",
                nested_value(fixture, ("find_bit", key)),
                expected,
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sample_manifest() -> str:
    return json.dumps(
        {"review_anchors": {"tools/lib/find_bit.zig": EXPECTED_FIND_BIT_PACKET}},
        indent=2,
    ) + "\n"


def sample_fixture() -> str:
    return json.dumps({"find_bit": EXPECTED_FIND_BIT_FIXTURE}, indent=2) + "\n"


def sample_text(lines: dict[str, str]) -> str:
    return "\n".join(lines.values()) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, FIND_BIT_HELPER_REL, "\n".join(REQUIRED_HELPER_ANCHORS) + "\n")
    write_file(root, MANIFEST_REL, sample_manifest())
    write_file(root, FIXTURE_REL, sample_fixture())
    write_file(root, LANE_NOTE_REL, sample_text(REQUIRED_LANE_NOTE_LINES))
    write_file(root, PHASE1_CLOSURE_REL, sample_text(REQUIRED_CLOSURE_LINES))
    write_file(root, DOCS_README_REL, sample_text(REQUIRED_DOCS_README_LINES))
    write_file(root, SCRIPTS_README_REL, sample_text(REQUIRED_SCRIPTS_README_LINES))


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker + "\n" in text:
        text = text.replace(marker + "\n", "", 1)
    else:
        text = text.replace(marker, "", 1)
    path.write_text(text, encoding="utf-8")


def duplicate_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(marker, marker + "\n" + marker, 1)
    path.write_text(text, encoding="utf-8")


def mutate_json(root: Path, relative_path: Path, path: tuple[str, ...]) -> None:
    data = json.loads((root / relative_path).read_text(encoding="utf-8"))
    current = data
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[1:]
    elif isinstance(value, int):
        current[final_key] = value + 1
    else:
        current[final_key] = f"{value} drift"
    (root / relative_path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = [("success", None)]

    for anchor in REQUIRED_HELPER_ANCHORS[:6]:
        cases.append(("remove_helper_anchor", (FIND_BIT_HELPER_REL, anchor, "remove")))
        cases.append(("duplicate_helper_anchor", (FIND_BIT_HELPER_REL, anchor, "duplicate")))

    for line in REQUIRED_SCRIPTS_README_LINES.values():
        cases.append(("remove_scripts_readme_line", (SCRIPTS_README_REL, line, "remove")))
        cases.append(("duplicate_scripts_readme_line", (SCRIPTS_README_REL, line, "duplicate")))

    for line in REQUIRED_DOCS_README_LINES.values():
        cases.append(("remove_docs_readme_line", (DOCS_README_REL, line, "remove")))
        cases.append(("duplicate_docs_readme_line", (DOCS_README_REL, line, "duplicate")))

    for line in REQUIRED_LANE_NOTE_LINES.values():
        cases.append(("remove_lane_note_line", (LANE_NOTE_REL, line, "remove")))
        cases.append(("duplicate_lane_note_line", (LANE_NOTE_REL, line, "duplicate")))

    for line in REQUIRED_CLOSURE_LINES.values():
        cases.append(("remove_closure_line", (PHASE1_CLOSURE_REL, line, "remove")))
        cases.append(("duplicate_closure_line", (PHASE1_CLOSURE_REL, line, "duplicate")))

    manifest_paths = [
        ("review_anchors", "tools/lib/find_bit.zig", "same_word_start_masks"),
        ("review_anchors", "tools/lib/find_bit.zig", "andnot_scan_entrypoint_contract"),
        ("review_anchors", "tools/lib/find_bit.zig", "tail_clamp_fixture_keys"),
        ("review_anchors", "tools/lib/find_bit.zig", "review_packet_summary"),
    ]
    for path in manifest_paths:
        cases.append(("manifest_drift", (MANIFEST_REL, path, "manifest")))

    fixture_paths = [
        ("find_bit", "tail_clamped_first"),
        ("find_bit", "tail_inclusive_boundary_next"),
        ("find_bit", "tail_clamped_empty_last"),
    ]
    for path in fixture_paths:
        cases.append(("fixture_drift", (FIXTURE_REL, path, "fixture")))

    cases.append(("missing_file", (MANIFEST_REL, None, "missing_file")))
    cases.append(("missing_file", (FIND_BIT_HELPER_REL, None, "missing_file")))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-find-bit-validator-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                relative_path, payload, kind = mutation
                target = root / relative_path
                if kind == "remove":
                    remove_marker(target, payload)
                elif kind == "duplicate":
                    duplicate_marker(target, payload)
                elif kind == "manifest" or kind == "fixture":
                    mutate_json(root, relative_path, payload)
                elif kind == "missing_file":
                    target.unlink()

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST=fail")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_VALIDATOR_ANCHOR_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_FIND_BIT_VALIDATOR_ANCHORS=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_FIND_BIT_VALIDATOR_ANCHORS=pass")
    print(f"PHASE1_FIND_BIT_VALIDATOR_ANCHOR_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_FIND_BIT_VALIDATOR_ANCHOR_REQUIRED_HELPER_COUNT="
        f"{len(REQUIRED_HELPER_ANCHORS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
