#!/usr/bin/env python3
"""Guard the current Phase 1 artifact/blocker alignment packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

REQUIRED_FILES = (
    "scripts/zigux/artifact_diff.py",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_replay_blockers.json",
)

EXPECTED_ARTIFACT_MARKERS = (
    'MODE_CHOICES = ("text", "json", "bytes")',
    'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
    'print("ARTIFACT_DIFF_SELF_TEST=pass")',
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

EXPECTED_MANIFEST_PATH = "zigux/tests/fixtures/phase1_helper_manifest.json"
EXPECTED_REPLAY_PATH = "zigux/tests/phase1_helpers.zig"
EXPECTED_REPLAY_BLOCKER_ID = "phase1_helpers_zig_slab_zero_after_kmalloc"
EXPECTED_REPLAY_BLOCKER_KIND = "fixture_mismatch"
EXPECTED_REPLAY_BLOCKER_SOURCE_PATH = "tools/lib/slab.zig"
EXPECTED_REPLAY_BLOCKER_FIELD = "slab.zero_after_kmalloc"
EXPECTED_REPLAY_BLOCKER_EVIDENCE = (
    "Focused 2026-05-17 scratch replay of `zig build test --build-file "
    "zigux/tests/build.zig --summary all` failed at `phase1_helpers.zig:595` because the "
    "committed fixture expects `true` while `tools/lib/slab.zig` still produced `false`."
)
EXPECTED_C_HARNESS_PATH = "zigux/tests/fixtures/phase1_helpers_c_harness.c"
EXPECTED_C_HARNESS_BLOCKER_ID = "phase1_helpers_c_harness_missing_c_sources"
EXPECTED_C_HARNESS_REASON = (
    "The old host-side parity route still depends on helper `tools/lib/*.c` inputs that "
    "current master no longer ships beside the Phase 1 `.zig` ports."
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
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def issue(label: str, expected: object, actual: object) -> str:
    return f"{label}:expected={expected!r}:actual={actual!r}"


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def read_json(root: Path, relative_path: str, *, failures: list[str], label: str) -> object | None:
    try:
        text = read_text(root, relative_path)
    except UnicodeDecodeError as exc:
        failures.append(f"{label}_invalid_utf8:{relative_path}:{exc.start + 1}:{exc.reason}")
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        failures.append(f"{label}_invalid_json:{relative_path}:{exc.lineno}:{exc.colno}:{exc.msg}")
        return None


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if not path.exists():
            failures.append(f"missing_file:{relative_path}")
        elif not path.is_file():
            failures.append(f"required_file_not_regular:{relative_path}")
    if failures:
        return failures

    artifact_text = read_text(root, "scripts/zigux/artifact_diff.py")
    for marker in EXPECTED_ARTIFACT_MARKERS:
        count = artifact_text.count(marker)
        if count != 1:
            failures.append(issue(f"artifact_marker:{marker}", 1, count))

    manifest = read_json(
        root,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        failures=failures,
        label="manifest",
    )
    blockers = read_json(
        root,
        "zigux/tests/fixtures/phase1_replay_blockers.json",
        failures=failures,
        label="blockers",
    )
    if manifest is None or blockers is None:
        return failures
    if not isinstance(manifest, dict):
        failures.append(issue("manifest_type", "dict", type(manifest).__name__))
        return failures
    if not isinstance(blockers, dict):
        failures.append(issue("blockers_type", "dict", type(blockers).__name__))
        return failures

    for key, expected in (
        ("phase", "Phase 1"),
        ("status", "closed"),
        ("helper_count", len(EXPECTED_HELPERS)),
    ):
        actual = manifest.get(key)
        if actual != expected:
            failures.append(issue(f"manifest:{key}", expected, actual))

    manifest_helpers = tuple(manifest.get("helpers", []))
    if manifest_helpers != EXPECTED_HELPERS:
        failures.append(issue("manifest_helpers", EXPECTED_HELPERS, manifest_helpers))

    manifest_lane = manifest.get("lane_sequencing")
    blocker_lane = blockers.get("lane_sequencing")
    replay = blockers.get("replay")
    c_harness = blockers.get("c_harness")

    if not isinstance(manifest_lane, dict):
        failures.append(issue("manifest_lane_type", "dict", type(manifest_lane).__name__))
        return failures
    if not isinstance(blocker_lane, dict):
        failures.append(issue("blocker_lane_type", "dict", type(blocker_lane).__name__))
        return failures
    if not isinstance(replay, dict):
        failures.append(issue("replay_type", "dict", type(replay).__name__))
        return failures
    if not isinstance(c_harness, dict):
        failures.append(issue("c_harness_type", "dict", type(c_harness).__name__))
        return failures

    manifest_shared = tuple(manifest_lane.get("shared_replay_parked_helpers", []))
    manifest_direct = tuple(manifest_lane.get("direct_anchor_followup_helpers", []))
    blocker_shared = tuple(blocker_lane.get("shared_replay_parked_helpers", []))
    blocker_direct = tuple(blocker_lane.get("direct_anchor_followup_helpers", []))

    if manifest_shared != EXPECTED_SHARED_HELPERS:
        failures.append(issue("manifest_shared_helpers", EXPECTED_SHARED_HELPERS, manifest_shared))
    if manifest_direct != EXPECTED_DIRECT_HELPERS:
        failures.append(issue("manifest_direct_helpers", EXPECTED_DIRECT_HELPERS, manifest_direct))
    if blocker_shared != EXPECTED_SHARED_HELPERS:
        failures.append(issue("blocker_shared_helpers", EXPECTED_SHARED_HELPERS, blocker_shared))
    if blocker_direct != EXPECTED_DIRECT_HELPERS:
        failures.append(issue("blocker_direct_helpers", EXPECTED_DIRECT_HELPERS, blocker_direct))
    if manifest_lane.get("rule_summary") != EXPECTED_RULE_SUMMARY:
        failures.append(
            issue("manifest_rule_summary", EXPECTED_RULE_SUMMARY, manifest_lane.get("rule_summary"))
        )

    if manifest_lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        failures.append(
            issue(
                "manifest_anti_overlap_rule",
                EXPECTED_ANTI_OVERLAP_RULE,
                manifest_lane.get("anti_overlap_rule"),
            )
        )
    if blocker_lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        failures.append(
            issue(
                "blocker_anti_overlap_rule",
                EXPECTED_ANTI_OVERLAP_RULE,
                blocker_lane.get("anti_overlap_rule"),
            )
        )

    if blocker_lane.get("manifest") != EXPECTED_MANIFEST_PATH:
        failures.append(issue("blocker_manifest_path", EXPECTED_MANIFEST_PATH, blocker_lane.get("manifest")))
    if blocker_lane.get("shared_replay_parked_helper_count") != len(EXPECTED_SHARED_HELPERS):
        failures.append(
            issue(
                "blocker_shared_count",
                len(EXPECTED_SHARED_HELPERS),
                blocker_lane.get("shared_replay_parked_helper_count"),
            )
        )
    if blocker_lane.get("direct_anchor_followup_helper_count") != len(EXPECTED_DIRECT_HELPERS):
        failures.append(
            issue(
                "blocker_direct_count",
                len(EXPECTED_DIRECT_HELPERS),
                blocker_lane.get("direct_anchor_followup_helper_count"),
            )
        )

    if set(manifest_shared).intersection(manifest_direct):
        failures.append("manifest_helper_sets_overlap")
    if set(blocker_shared).intersection(blocker_direct):
        failures.append("blocker_helper_sets_overlap")
    if tuple(sorted(manifest_shared + manifest_direct)) != tuple(sorted(blocker_shared + blocker_direct)):
        failures.append("manifest_and_blocker_helper_sets_differ")

    if blockers.get("status") != "parked":
        failures.append(issue("blockers_status", "parked", blockers.get("status")))

    if replay.get("path") != EXPECTED_REPLAY_PATH:
        failures.append(issue("replay_path", EXPECTED_REPLAY_PATH, replay.get("path")))
    if replay.get("state") != "blocked":
        failures.append(issue("replay_state", "blocked", replay.get("state")))
    replay_blockers = replay.get("blockers")
    if not isinstance(replay_blockers, list) or not replay_blockers:
        failures.append(issue("replay_blockers", "non-empty list", replay_blockers))
    else:
        if len(replay_blockers) != 1:
            failures.append(issue("replay_blocker_count", 1, len(replay_blockers)))
        first = replay_blockers[0]
        if not isinstance(first, dict):
            failures.append(issue("replay_first_type", "dict", type(first).__name__))
        else:
            if first.get("id") != EXPECTED_REPLAY_BLOCKER_ID:
                failures.append(issue("replay_blocker_id", EXPECTED_REPLAY_BLOCKER_ID, first.get("id")))
            if first.get("kind") != EXPECTED_REPLAY_BLOCKER_KIND:
                failures.append(issue("replay_blocker_kind", EXPECTED_REPLAY_BLOCKER_KIND, first.get("kind")))
            if first.get("path") != EXPECTED_REPLAY_BLOCKER_SOURCE_PATH:
                failures.append(
                    issue("replay_blocker_source_path", EXPECTED_REPLAY_BLOCKER_SOURCE_PATH, first.get("path"))
                )
            if first.get("field") != EXPECTED_REPLAY_BLOCKER_FIELD:
                failures.append(issue("replay_blocker_field", EXPECTED_REPLAY_BLOCKER_FIELD, first.get("field")))
            if first.get("expected") is not True:
                failures.append(issue("replay_blocker_expected", True, first.get("expected")))
            if first.get("actual") is not False:
                failures.append(issue("replay_blocker_actual", False, first.get("actual")))
            if first.get("evidence") != EXPECTED_REPLAY_BLOCKER_EVIDENCE:
                failures.append(
                    issue("replay_blocker_evidence", EXPECTED_REPLAY_BLOCKER_EVIDENCE, first.get("evidence"))
                )

    if c_harness.get("path") != EXPECTED_C_HARNESS_PATH:
        failures.append(issue("c_harness_path", EXPECTED_C_HARNESS_PATH, c_harness.get("path")))
    if c_harness.get("state") != "blocked":
        failures.append(issue("c_harness_state", "blocked", c_harness.get("state")))
    if c_harness.get("reason") != EXPECTED_C_HARNESS_REASON:
        failures.append(issue("c_harness_reason", EXPECTED_C_HARNESS_REASON, c_harness.get("reason")))
    if c_harness.get("helper_count") != len(EXPECTED_HELPERS):
        failures.append(issue("c_harness_helper_count", len(EXPECTED_HELPERS), c_harness.get("helper_count")))
    c_harness_helpers = tuple(c_harness.get("helpers", []))
    if c_harness_helpers != EXPECTED_HELPERS:
        failures.append(issue("c_harness_helpers", EXPECTED_HELPERS, c_harness_helpers))
    if c_harness.get("blocker_id") != EXPECTED_C_HARNESS_BLOCKER_ID:
        failures.append(issue("c_harness_blocker_id", EXPECTED_C_HARNESS_BLOCKER_ID, c_harness.get("blocker_id")))

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def sample_artifact_diff() -> str:
    return "\n".join(
        (
            "#!/usr/bin/env python3",
            'MODE_CHOICES = ("text", "json", "bytes")',
            'LEGACY_MODE_ALIASES = {"sha256": "bytes"}',
            'print("ARTIFACT_DIFF_SELF_TEST=pass")',
            "",
        )
    )


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


def sample_blockers() -> dict[str, object]:
    return {
        "status": "parked",
        "lane_sequencing": {
            "manifest": EXPECTED_MANIFEST_PATH,
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
                    "kind": EXPECTED_REPLAY_BLOCKER_KIND,
                    "path": EXPECTED_REPLAY_BLOCKER_SOURCE_PATH,
                    "field": EXPECTED_REPLAY_BLOCKER_FIELD,
                    "expected": True,
                    "actual": False,
                    "evidence": EXPECTED_REPLAY_BLOCKER_EVIDENCE,
                }
            ],
        },
        "c_harness": {
            "path": EXPECTED_C_HARNESS_PATH,
            "state": "blocked",
            "reason": EXPECTED_C_HARNESS_REASON,
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": list(EXPECTED_HELPERS),
            "blocker_id": EXPECTED_C_HARNESS_BLOCKER_ID,
        },
    }


def build_sample_root(root: Path) -> None:
    write_text(root, "scripts/zigux/artifact_diff.py", sample_artifact_diff())
    write_text(
        root,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(sample_manifest(), indent=2) + "\n",
    )
    write_text(
        root,
        "zigux/tests/fixtures/phase1_replay_blockers.json",
        json.dumps(sample_blockers(), indent=2) + "\n",
    )


def run_self_test() -> int:
    cases = (
        ("success", None),
        ("missing_required_file", lambda root: (root / "scripts/zigux/artifact_diff.py").unlink()),
        (
            "missing_artifact_marker",
            lambda root: write_text(root, "scripts/zigux/artifact_diff.py", "#!/usr/bin/env python3\n"),
        ),
        (
            "manifest_helpers_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                lambda data: data.__setitem__("helpers", ["drift"]),
            ),
        ),
        (
            "manifest_rule_summary_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                lambda data: data["lane_sequencing"].__setitem__("rule_summary", "drift"),
            ),
        ),
        (
            "manifest_shared_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                lambda data: data["lane_sequencing"].__setitem__("shared_replay_parked_helpers", ["drift"]),
            ),
        ),
        (
            "blocker_direct_count_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_replay_blockers.json",
                lambda data: data["lane_sequencing"].__setitem__("direct_anchor_followup_helper_count", 99),
            ),
        ),
        (
            "blocker_id_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_replay_blockers.json",
                lambda data: data["replay"]["blockers"][0].__setitem__("id", "drift"),
            ),
        ),
        (
            "replay_evidence_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_replay_blockers.json",
                lambda data: data["replay"]["blockers"][0].__setitem__("evidence", "drift"),
            ),
        ),
        (
            "c_harness_reason_drift",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_replay_blockers.json",
                lambda data: data["c_harness"].__setitem__("reason", "drift"),
            ),
        ),
        (
            "helper_set_overlap",
            lambda root: _mutate_json(
                root / "zigux/tests/fixtures/phase1_helper_manifest.json",
                lambda data: data["lane_sequencing"]["direct_anchor_followup_helpers"].__setitem__(
                    0, EXPECTED_SHARED_HELPERS[0]
                ),
            ),
        ),
        (
            "blockers_invalid_json",
            lambda root: write_text(root, "zigux/tests/fixtures/phase1_replay_blockers.json", "{\n"),
        ),
    )

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="lane09_artifact_blocker_alignment_") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            if mutation is not None:
                mutation(root)
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def _mutate_json(path: Path, mutation) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutation(data)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT=pass")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_HELPERS)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
