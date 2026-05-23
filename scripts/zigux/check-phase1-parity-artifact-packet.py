#!/usr/bin/env python3
"""Guard the current Phase 1 parity artifact packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "scripts/zigux/artifact_diff.py",
    "zigux/tests/fixtures/phase1_helpers.json",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_replay_blockers.json",
)

ARTIFACT_DIFF_COMMON_MARKERS = (
    'print("ARTIFACT_DIFF_SELF_TEST=pass")',
)

ARTIFACT_DIFF_FAMILY_MARKERS = {
    "bytes": (
        'MODE_CHOICES = ("text", "json", "bytes")',
        'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
    ),
    "sha256": (
        'parser.add_argument("--mode", choices=["text", "json", "sha256"])',
        'elif mode == "sha256":',
    ),
}

EXPECTED_FIXTURE_ORDER = (
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
)

EXPECTED_MANIFEST_HELPERS = (
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
    "above, while bitmap, find_bit, rbtree, and string keep the only bounded "
    "direct helper-local follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)

EXPECTED_FIXTURE_SENTINELS = {
    ("find_bit", "bits_per_long"): 64,
    ("find_bit", "tail_clamped_empty_last"): 69,
    ("bitmap", "weight"): 3,
    ("bitmap", "terminator_only_nul"): 0,
    ("string", "strtobool_invalid"): 184,
    ("string", "replace_char_cstr_end"): 2,
    ("rbtree", "cached_leftmost_return_serials"): [0, -1, 2, -1],
    ("argv_split", "argc"): 3,
    ("cmdline", "invalid"): {"value": 0, "rest": "xyz"},
    ("ctype", "mask_space"): 160,
    ("hweight", "w64"): 32,
    ("list_sort", "bool_sorted_ordinals"): [1, 3, 0, 2, 4],
    ("zalloc", "freed_is_null"): True,
    ("str_error_r", "enoent"): "No such file or directory",
    ("slab", "zero_after_kmalloc"): True,
    ("vsprintf", "pad_text"): "id=7    ",
}

FIXTURE_SECTION_TO_HELPER = {
    "find_bit": "tools/lib/find_bit.zig",
    "bitmap": "tools/lib/bitmap.zig",
    "string": "tools/lib/string.zig",
    "rbtree": "tools/lib/rbtree.zig",
    "argv_split": "tools/lib/argv_split.zig",
    "cmdline": "tools/lib/cmdline.zig",
    "ctype": "tools/lib/ctype.zig",
    "hweight": "tools/lib/hweight.zig",
    "list_sort": "tools/lib/list_sort.zig",
    "zalloc": "tools/lib/zalloc.zig",
    "str_error_r": "tools/lib/str_error_r.zig",
    "slab": "tools/lib/slab.zig",
    "vsprintf": "tools/lib/vsprintf.zig",
}

EXPECTED_REPLAY_PATH = "zigux/tests/phase1_helpers.zig"
EXPECTED_REPLAY_BLOCKER_ID = "phase1_helpers_zig_slab_zero_after_kmalloc"
EXPECTED_C_HARNESS_PATH = "zigux/tests/fixtures/phase1_helpers_c_harness.c"
EXPECTED_C_HARNESS_BLOCKER_ID = "phase1_helpers_c_harness_missing_c_sources"
EXPECTED_BLOCKER_MANIFEST_PATH = "zigux/tests/fixtures/phase1_helper_manifest.json"


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def issue(label: str, expected: object, actual: object) -> str:
    return f"{label}:expected={expected!r}:actual={actual!r}"


def collect_required_file_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if not path.exists():
            failures.append(f"missing_file:{relative_path}")
        elif not path.is_file():
            failures.append(f"required_file_not_regular:{relative_path}")
    return failures


def detect_artifact_diff_family(artifact_diff_text: str) -> tuple[str | None, list[str]]:
    failures: list[str] = []
    for marker in ARTIFACT_DIFF_COMMON_MARKERS:
        count = artifact_diff_text.count(marker)
        if count != 1:
            failures.append(issue(f"artifact_diff_marker:{marker}", 1, count))

    matched_families: list[str] = []
    for family, markers in ARTIFACT_DIFF_FAMILY_MARKERS.items():
        if all(artifact_diff_text.count(marker) == 1 for marker in markers):
            matched_families.append(family)

    if not matched_families:
        failures.append(
            "artifact_diff_family:no_match:"
            + ",".join(sorted(ARTIFACT_DIFF_FAMILY_MARKERS))
        )
        return None, failures
    if len(matched_families) > 1:
        failures.append(issue("artifact_diff_family", "single_match", tuple(sorted(matched_families))))
        return None, failures
    return matched_families[0], failures


def load_json_file(root: Path, relative_path: str, *, label: str, failures: list[str]) -> object | None:
    try:
        text = read_text(root, relative_path)
    except UnicodeDecodeError as exc:
        failures.append(
            f"{label}_invalid_utf8:{relative_path}:{exc.start + 1}:{exc.reason}"
        )
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        failures.append(
            f"{label}_invalid_json:{relative_path}:{exc.lineno}:{exc.colno}:{exc.msg}"
        )
        return None


def collect_failures(root: Path) -> list[str]:
    failures = collect_required_file_failures(root)
    if failures:
        return failures

    artifact_diff_text = read_text(root, "scripts/zigux/artifact_diff.py")
    _family, artifact_family_failures = detect_artifact_diff_family(artifact_diff_text)
    failures.extend(artifact_family_failures)

    fixture = load_json_file(
        root,
        "zigux/tests/fixtures/phase1_helpers.json",
        label="fixture",
        failures=failures,
    )
    if fixture is None:
        return failures
    if not isinstance(fixture, dict):
        failures.append(issue("fixture_type", "dict", type(fixture).__name__))
        return failures
    fixture_order = tuple(fixture.keys())
    if fixture_order != EXPECTED_FIXTURE_ORDER:
        failures.append(issue("fixture_order", EXPECTED_FIXTURE_ORDER, fixture_order))

    mapped_helpers = tuple(
        FIXTURE_SECTION_TO_HELPER[name]
        for name in fixture_order
        if name in FIXTURE_SECTION_TO_HELPER
    )
    if len(mapped_helpers) != len(EXPECTED_FIXTURE_ORDER):
        failures.append(
            issue("fixture_mapped_helper_count", len(EXPECTED_FIXTURE_ORDER), len(mapped_helpers))
        )
    elif tuple(sorted(mapped_helpers)) != tuple(sorted(EXPECTED_MANIFEST_HELPERS)):
        failures.append(
            issue(
                "fixture_mapped_helpers",
                tuple(sorted(EXPECTED_MANIFEST_HELPERS)),
                tuple(sorted(mapped_helpers)),
            )
        )

    for (section, field), expected in EXPECTED_FIXTURE_SENTINELS.items():
        section_value = fixture.get(section)
        actual = None if not isinstance(section_value, dict) else section_value.get(field)
        if actual != expected:
            failures.append(issue(f"fixture_sentinel:{section}.{field}", expected, actual))

    manifest = load_json_file(
        root,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        label="manifest",
        failures=failures,
    )
    if manifest is None:
        return failures
    if not isinstance(manifest, dict):
        failures.append(issue("manifest_type", "dict", type(manifest).__name__))
        return failures

    for key, expected in (("phase", "Phase 1"), ("status", "closed"), ("helper_count", 13)):
        actual = manifest.get(key)
        if actual != expected:
            failures.append(issue(f"manifest:{key}", expected, actual))

    manifest_helpers = tuple(manifest.get("helpers", []))
    if manifest_helpers != EXPECTED_MANIFEST_HELPERS:
        failures.append(issue("manifest_helpers", EXPECTED_MANIFEST_HELPERS, manifest_helpers))

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        failures.append(issue("manifest_lane_sequencing", "dict", type(lane_sequencing).__name__))
    else:
        shared_helpers = tuple(lane_sequencing.get("shared_replay_parked_helpers", []))
        direct_helpers = tuple(lane_sequencing.get("direct_anchor_followup_helpers", []))
        if shared_helpers != EXPECTED_SHARED_HELPERS:
            failures.append(issue("manifest_shared_helpers", EXPECTED_SHARED_HELPERS, shared_helpers))
        if direct_helpers != EXPECTED_DIRECT_HELPERS:
            failures.append(issue("manifest_direct_helpers", EXPECTED_DIRECT_HELPERS, direct_helpers))
        if lane_sequencing.get("rule_summary") != EXPECTED_RULE_SUMMARY:
            failures.append(
                issue("manifest_rule_summary", EXPECTED_RULE_SUMMARY, lane_sequencing.get("rule_summary"))
            )
        if lane_sequencing.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
            failures.append(
                issue(
                    "manifest_anti_overlap_rule",
                    EXPECTED_ANTI_OVERLAP_RULE,
                    lane_sequencing.get("anti_overlap_rule"),
                )
            )

    blockers = load_json_file(
        root,
        "zigux/tests/fixtures/phase1_replay_blockers.json",
        label="blockers",
        failures=failures,
    )
    if blockers is None:
        return failures
    if not isinstance(blockers, dict):
        failures.append(issue("blockers_type", "dict", type(blockers).__name__))
        return failures

    if blockers.get("status") != "parked":
        failures.append(issue("blockers_status", "parked", blockers.get("status")))

    blocker_lane = blockers.get("lane_sequencing")
    if not isinstance(blocker_lane, dict):
        failures.append(issue("blocker_lane_sequencing", "dict", type(blocker_lane).__name__))
    else:
        for key, expected in (
            ("manifest", EXPECTED_BLOCKER_MANIFEST_PATH),
            ("shared_replay_parked_helper_count", len(EXPECTED_SHARED_HELPERS)),
            ("direct_anchor_followup_helper_count", len(EXPECTED_DIRECT_HELPERS)),
        ):
            actual = blocker_lane.get(key)
            if actual != expected:
                failures.append(issue(f"blocker_lane:{key}", expected, actual))

        shared_helpers = tuple(blocker_lane.get("shared_replay_parked_helpers", []))
        direct_helpers = tuple(blocker_lane.get("direct_anchor_followup_helpers", []))
        if shared_helpers != EXPECTED_SHARED_HELPERS:
            failures.append(issue("blocker_lane:shared_helpers", EXPECTED_SHARED_HELPERS, shared_helpers))
        if direct_helpers != EXPECTED_DIRECT_HELPERS:
            failures.append(issue("blocker_lane:direct_helpers", EXPECTED_DIRECT_HELPERS, direct_helpers))
        if blocker_lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
            failures.append(
                issue(
                    "blocker_lane:anti_overlap_rule",
                    EXPECTED_ANTI_OVERLAP_RULE,
                    blocker_lane.get("anti_overlap_rule"),
                )
            )

    replay = blockers.get("replay")
    if not isinstance(replay, dict):
        failures.append(issue("replay_block", "dict", type(replay).__name__))
    else:
        for key, expected in (("path", EXPECTED_REPLAY_PATH), ("state", "blocked")):
            actual = replay.get(key)
            if actual != expected:
                failures.append(issue(f"replay:{key}", expected, actual))
        replay_blockers = replay.get("blockers")
        if not isinstance(replay_blockers, list) or not replay_blockers:
            failures.append(issue("replay_blockers", "non-empty list", replay_blockers))
        else:
            first = replay_blockers[0]
            if not isinstance(first, dict):
                failures.append(issue("replay_blocker_first", "dict", type(first).__name__))
            else:
                if first.get("id") != EXPECTED_REPLAY_BLOCKER_ID:
                    failures.append(issue("replay_blocker_id", EXPECTED_REPLAY_BLOCKER_ID, first.get("id")))
                if first.get("field") != "slab.zero_after_kmalloc":
                    failures.append(issue("replay_blocker_field", "slab.zero_after_kmalloc", first.get("field")))

    c_harness = blockers.get("c_harness")
    if not isinstance(c_harness, dict):
        failures.append(issue("c_harness_block", "dict", type(c_harness).__name__))
    else:
        for key, expected in (
            ("path", EXPECTED_C_HARNESS_PATH),
            ("state", "blocked"),
            ("helper_count", len(EXPECTED_MANIFEST_HELPERS)),
            ("blocker_id", EXPECTED_C_HARNESS_BLOCKER_ID),
        ):
            actual = c_harness.get(key)
            if actual != expected:
                failures.append(issue(f"c_harness:{key}", expected, actual))
        helpers = tuple(c_harness.get("helpers", []))
        if helpers != EXPECTED_MANIFEST_HELPERS:
            failures.append(issue("c_harness:helpers", EXPECTED_MANIFEST_HELPERS, helpers))

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def sample_artifact_diff_text() -> str:
    return "\n".join(
        (
            "#!/usr/bin/env python3",
            'MODE_CHOICES = ("text", "json", "bytes")',
            'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
            'print("ARTIFACT_DIFF_SELF_TEST=pass")',
            "",
        )
    )


def sample_sha256_artifact_diff_text() -> str:
    return "\n".join(
        (
            "#!/usr/bin/env python3",
            'print("ARTIFACT_DIFF_SELF_TEST=pass")',
            'elif mode == "sha256":',
            'parser.add_argument("--mode", choices=["text", "json", "sha256"])',
            "",
        )
    )


def sample_fixture() -> dict[str, object]:
    return {
        "find_bit": {"bits_per_long": 64, "tail_clamped_empty_last": 69},
        "bitmap": {"weight": 3, "terminator_only_nul": 0},
        "string": {"strtobool_invalid": 184, "replace_char_cstr_end": 2},
        "rbtree": {"cached_leftmost_return_serials": [0, -1, 2, -1]},
        "argv_split": {"argc": 3},
        "cmdline": {"invalid": {"value": 0, "rest": "xyz"}},
        "ctype": {"mask_space": 160},
        "hweight": {"w64": 32},
        "list_sort": {"bool_sorted_ordinals": [1, 3, 0, 2, 4]},
        "zalloc": {"freed_is_null": True},
        "str_error_r": {"enoent": "No such file or directory"},
        "slab": {"zero_after_kmalloc": True},
        "vsprintf": {"pad_text": "id=7    "},
    }


def sample_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "helpers": list(EXPECTED_MANIFEST_HELPERS),
        "lane_sequencing": {
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_HELPERS),
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }


def sample_blockers() -> dict[str, object]:
    return {
        "status": "parked",
        "lane_sequencing": {
            "manifest": EXPECTED_BLOCKER_MANIFEST_PATH,
            "shared_replay_parked_helper_count": len(EXPECTED_SHARED_HELPERS),
            "shared_replay_parked_helpers": list(EXPECTED_SHARED_HELPERS),
            "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_HELPERS),
            "direct_anchor_followup_helpers": list(EXPECTED_DIRECT_HELPERS),
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "replay": {
            "path": EXPECTED_REPLAY_PATH,
            "state": "blocked",
            "blockers": [
                {
                    "id": EXPECTED_REPLAY_BLOCKER_ID,
                    "field": "slab.zero_after_kmalloc",
                    "expected": True,
                    "actual": False,
                }
            ],
        },
        "c_harness": {
            "path": EXPECTED_C_HARNESS_PATH,
            "state": "blocked",
            "helper_count": len(EXPECTED_MANIFEST_HELPERS),
            "helpers": list(EXPECTED_MANIFEST_HELPERS),
            "blocker_id": EXPECTED_C_HARNESS_BLOCKER_ID,
        },
    }


def build_sample_repo(root: Path, *, artifact_diff_text: str | None = None) -> None:
    write_text(
        root,
        "scripts/zigux/artifact_diff.py",
        artifact_diff_text if artifact_diff_text is not None else sample_artifact_diff_text(),
    )
    write_text(
        root,
        "zigux/tests/fixtures/phase1_helpers.json",
        json.dumps(sample_fixture(), indent=2, sort_keys=False) + "\n",
    )
    write_text(
        root,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(sample_manifest(), indent=2, sort_keys=False) + "\n",
    )
    write_text(
        root,
        "zigux/tests/fixtures/phase1_replay_blockers.json",
        json.dumps(sample_blockers(), indent=2, sort_keys=False) + "\n",
    )


def mutate_remove_artifact_marker(root: Path) -> None:
    path = root / "scripts/zigux/artifact_diff.py"
    text = path.read_text(encoding="utf-8")
    marker = ARTIFACT_DIFF_COMMON_MARKERS[0]
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_required_file_not_regular(root: Path) -> None:
    path = root / "scripts/zigux/artifact_diff.py"
    path.unlink()
    path.mkdir()


def mutate_fixture_order(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_helpers.json"
    fixture = json.loads(path.read_text(encoding="utf-8"))
    bitmap = fixture.pop("bitmap")
    reordered = {"bitmap": bitmap}
    reordered.update(fixture)
    path.write_text(json.dumps(reordered, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def mutate_fixture_sentinel(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_helpers.json"
    fixture = json.loads(path.read_text(encoding="utf-8"))
    fixture["slab"]["zero_after_kmalloc"] = False
    path.write_text(json.dumps(fixture, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def mutate_fixture_invalid_json(root: Path) -> None:
    write_text(root, "zigux/tests/fixtures/phase1_helpers.json", '{"find_bit":\n')


def mutate_fixture_not_object(root: Path) -> None:
    write_text(root, "zigux/tests/fixtures/phase1_helpers.json", "[]\n")


def mutate_manifest_count(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["helper_count"] = 12
    path.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def mutate_manifest_summary(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["lane_sequencing"]["rule_summary"] = "drifted summary"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def mutate_manifest_invalid_json(root: Path) -> None:
    write_text(root, "zigux/tests/fixtures/phase1_helper_manifest.json", '{"phase":\n')


def mutate_blocker_manifest(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_replay_blockers.json"
    blockers = json.loads(path.read_text(encoding="utf-8"))
    blockers["lane_sequencing"]["manifest"] = "zigux/tests/fixtures/drift.json"
    path.write_text(json.dumps(blockers, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def mutate_blocker_shared_count(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_replay_blockers.json"
    blockers = json.loads(path.read_text(encoding="utf-8"))
    blockers["lane_sequencing"]["shared_replay_parked_helper_count"] = 8
    path.write_text(json.dumps(blockers, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def mutate_blocker_anti_overlap_rule(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_replay_blockers.json"
    blockers = json.loads(path.read_text(encoding="utf-8"))
    blockers["lane_sequencing"]["anti_overlap_rule"] = "drifted anti-overlap rule"
    path.write_text(json.dumps(blockers, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def mutate_replay_blocker_id(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_replay_blockers.json"
    blockers = json.loads(path.read_text(encoding="utf-8"))
    blockers["replay"]["blockers"][0]["id"] = "drifted_replay_blocker"
    path.write_text(json.dumps(blockers, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def mutate_c_harness_blocker_id(root: Path) -> None:
    path = root / "zigux/tests/fixtures/phase1_replay_blockers.json"
    blockers = json.loads(path.read_text(encoding="utf-8"))
    blockers["c_harness"]["blocker_id"] = "drifted_c_harness_blocker"
    path.write_text(json.dumps(blockers, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def mutate_blockers_invalid_json(root: Path) -> None:
    write_text(root, "zigux/tests/fixtures/phase1_replay_blockers.json", '{"status":\n')


def mutate_unknown_artifact_family(root: Path) -> None:
    write_text(
        root,
        "scripts/zigux/artifact_diff.py",
        '#!/usr/bin/env python3\nprint("ARTIFACT_DIFF_SELF_TEST=pass")\n',
    )


def run_self_test() -> int:
    cases = (
        ("success", None, None),
        ("sha256_artifact_family", None, sample_sha256_artifact_diff_text()),
        ("missing_artifact_diff", lambda root: (root / "scripts/zigux/artifact_diff.py").unlink(), None),
        ("required_file_not_regular", mutate_required_file_not_regular, None),
        ("missing_artifact_marker", mutate_remove_artifact_marker, None),
        ("unknown_artifact_family", mutate_unknown_artifact_family, None),
        ("fixture_order", mutate_fixture_order, None),
        ("fixture_sentinel", mutate_fixture_sentinel, None),
        ("fixture_invalid_json", mutate_fixture_invalid_json, None),
        ("fixture_not_object", mutate_fixture_not_object, None),
        ("manifest_count", mutate_manifest_count, None),
        ("manifest_summary", mutate_manifest_summary, None),
        ("manifest_invalid_json", mutate_manifest_invalid_json, None),
        ("blocker_manifest", mutate_blocker_manifest, None),
        ("blocker_shared_count", mutate_blocker_shared_count, None),
        ("blocker_anti_overlap_rule", mutate_blocker_anti_overlap_rule, None),
        ("replay_blocker_id", mutate_replay_blocker_id, None),
        ("c_harness_blocker_id", mutate_c_harness_blocker_id, None),
        ("blockers_invalid_json", mutate_blockers_invalid_json, None),
    )

    for name, mutation, artifact_diff_text in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-parity-artifact-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root, artifact_diff_text=artifact_diff_text)
            if mutation is not None:
                mutation(root)
            failures = collect_failures(root)
            if name in {"success", "sha256_artifact_family"}:
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_PARITY_ARTIFACT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_PARITY_ARTIFACT_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_PARITY_ARTIFACT_PACKET=fail")
        for item in failures:
            print(item)
        return 1

    print("PHASE1_PARITY_ARTIFACT_PACKET=pass")
    print(f"PHASE1_PARITY_ARTIFACT_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_PARITY_ARTIFACT_PACKET_HELPER_COUNT={len(EXPECTED_MANIFEST_HELPERS)}")
    print(f"PHASE1_PARITY_ARTIFACT_PACKET_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_HELPERS)}")
    print(f"PHASE1_PARITY_ARTIFACT_PACKET_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
