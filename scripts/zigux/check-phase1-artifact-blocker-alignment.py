#!/usr/bin/env python3
"""Guard the current Phase 1 artifact/blocker packet against drift."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

ARTIFACT_DIFF_REL = Path("scripts/zigux/artifact_diff.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")

REQUIRED_FILES = (ARTIFACT_DIFF_REL, MANIFEST_REL, BLOCKERS_REL)

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
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, "
    "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local "
    "follow-up anchors on current master."
)

EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers "
    "reopen only for their existing helper-local anchors or already-committed shared fixture keys."
)

EXPECTED_ARTIFACT_HELP_LINES = [
    "usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test]",
    " [expected] [actual]",
    "",
    "Compare two artifacts in a stable mode.",
    "",
    "positional arguments:",
    " expected",
    " actual",
    "",
    "options:",
    " -h, --help show this help message and exit",
    " --mode {text,json,bytes}",
    " --self-test Run built-in deterministic comparison checks.",
]

EXPECTED_ARTIFACT_SELF_TEST_CASES = [
    "text_pass",
    "text_mismatch",
    "json_pass",
    "json_mismatch",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "bytes_pass",
    "bytes_drift",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "bytes_missing_expected",
    "bytes_missing_actual",
    "bytes_missing_both",
    "legacy_sha256_alias",
    "missing_mode_value_rejected",
    "missing_positional_arguments_rejected",
    "invalid_mode_rejected",
    "extra_positional_rejected",
]

EXPECTED_ARTIFACT_SELF_TEST_LINES = [
    "ARTIFACT_DIFF_SELF_TEST=pass",
    f"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(EXPECTED_ARTIFACT_SELF_TEST_CASES)}",
    "ARTIFACT_DIFF_SELF_TEST_CASES=" + ",".join(EXPECTED_ARTIFACT_SELF_TEST_CASES),
]


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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_artifact_diff(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / ARTIFACT_DIFF_REL), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=root,
    )


def load_json_with_tracking(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=DuplicateTrackingDict)


def collect_duplicate_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(collect_duplicate_paths(item, prefix))
    return paths


def expect_equal(actual: object, expected: object, label: str, failures: list[str]) -> None:
    if actual != expected:
        failures.append(f"{label}:expected={expected!r}:actual={actual!r}")


def expect_lines(actual: list[str], expected: list[str], label: str, failures: list[str]) -> None:
    if actual != expected:
        failures.append(f"{label}:expected={expected!r}:actual={actual!r}")


def expect_regular_files(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.exists():
            failures.append(f"missing_file:{rel.as_posix()}")
            continue
        if not path.is_file():
            failures.append(f"not_a_file:{rel.as_posix()}")
    return failures


def verify_artifact_diff(root: Path) -> list[str]:
    failures: list[str] = []

    help_run = run_artifact_diff(root, ["-h"])
    expect_equal(help_run.returncode, 0, "artifact_diff_help:exit", failures)
    expect_equal(help_run.stderr, "", "artifact_diff_help:stderr", failures)
    expect_lines(help_run.stdout.splitlines(), EXPECTED_ARTIFACT_HELP_LINES, "artifact_diff_help:stdout", failures)

    self_test_run = run_artifact_diff(root, ["--self-test"])
    expect_equal(self_test_run.returncode, 0, "artifact_diff_self_test:exit", failures)
    expect_equal(self_test_run.stderr, "", "artifact_diff_self_test:stderr", failures)
    expect_lines(
        self_test_run.stdout.splitlines(),
        EXPECTED_ARTIFACT_SELF_TEST_LINES,
        "artifact_diff_self_test:stdout",
        failures,
    )

    with tempfile.TemporaryDirectory(prefix="phase1_artifact_blocker_alignment_") as tmp_dir:
        tmp = Path(tmp_dir)
        expected = tmp / "expected.bin"
        actual = tmp / "actual.bin"
        expected.write_bytes(b"zigux-phase1-artifact")
        actual.write_bytes(b"zigux-phase1-artifact")
        sha = hashlib.sha256(expected.read_bytes()).hexdigest()

        alias_run = run_artifact_diff(root, ["--mode", "sha256", str(expected), str(actual)])
        expect_equal(alias_run.returncode, 0, "artifact_diff_sha256_alias:exit", failures)
        expect_equal(alias_run.stderr, "", "artifact_diff_sha256_alias:stderr", failures)
        expect_lines(
            alias_run.stdout.splitlines(),
            [
                "ARTIFACT_DIFF=pass",
                "MODE=bytes",
                f"EXPECTED={expected}",
                f"ACTUAL={actual}",
                f"SHA256={sha}",
            ],
            "artifact_diff_sha256_alias:stdout",
            failures,
        )

    return failures


def verify_manifest_and_blockers(root: Path) -> list[str]:
    failures: list[str] = []

    try:
        manifest_data = load_json_with_tracking(root / MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [f"{MANIFEST_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    try:
        blockers_data = load_json_with_tracking(root / BLOCKERS_REL)
    except json.JSONDecodeError as exc:
        return [f"{BLOCKERS_REL.as_posix()}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]

    if not isinstance(manifest_data, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest_data).__name__}"]
    if not isinstance(blockers_data, dict):
        return [f"{BLOCKERS_REL.as_posix()}:expected=dict:actual={type(blockers_data).__name__}"]

    manifest_duplicates = collect_duplicate_paths(manifest_data)
    blockers_duplicates = collect_duplicate_paths(blockers_data)
    if manifest_duplicates:
        failures.extend(f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}" for path in manifest_duplicates)
    if blockers_duplicates:
        failures.extend(f"{BLOCKERS_REL.as_posix()}:duplicate_json_key:{path}" for path in blockers_duplicates)
    if failures:
        return failures

    expect_equal(manifest_data.get("helper_count"), len(EXPECTED_HELPERS), "manifest:helper_count", failures)
    expect_equal(manifest_data.get("helpers"), EXPECTED_HELPERS, "manifest:helpers", failures)
    expect_equal(manifest_data.get("status"), "closed", "manifest:status", failures)

    lane = manifest_data.get("lane_sequencing")
    if not isinstance(lane, dict):
        failures.append("manifest:lane_sequencing:expected=dict")
        return failures
    expect_equal(
        lane.get("shared_replay_parked_helpers"),
        EXPECTED_SHARED_REPLAY_HELPERS,
        "manifest:shared_replay_parked_helpers",
        failures,
    )
    expect_equal(
        lane.get("direct_anchor_followup_helpers"),
        EXPECTED_DIRECT_ANCHOR_HELPERS,
        "manifest:direct_anchor_followup_helpers",
        failures,
    )
    expect_equal(lane.get("rule_summary"), EXPECTED_RULE_SUMMARY, "manifest:rule_summary", failures)
    expect_equal(
        lane.get("anti_overlap_rule"),
        EXPECTED_ANTI_OVERLAP_RULE,
        "manifest:anti_overlap_rule",
        failures,
    )

    expect_equal(blockers_data.get("status"), "parked", "blockers:status", failures)

    blockers_lane = blockers_data.get("lane_sequencing")
    if not isinstance(blockers_lane, dict):
        failures.append("blockers:lane_sequencing:expected=dict")
        return failures
    expect_equal(
        blockers_lane.get("manifest"),
        MANIFEST_REL.as_posix(),
        "blockers:lane_sequencing.manifest",
        failures,
    )
    expect_equal(
        blockers_lane.get("shared_replay_parked_helper_count"),
        len(EXPECTED_SHARED_REPLAY_HELPERS),
        "blockers:shared_replay_parked_helper_count",
        failures,
    )
    expect_equal(
        blockers_lane.get("shared_replay_parked_helpers"),
        EXPECTED_SHARED_REPLAY_HELPERS,
        "blockers:shared_replay_parked_helpers",
        failures,
    )
    expect_equal(
        blockers_lane.get("direct_anchor_followup_helper_count"),
        len(EXPECTED_DIRECT_ANCHOR_HELPERS),
        "blockers:direct_anchor_followup_helper_count",
        failures,
    )
    expect_equal(
        blockers_lane.get("direct_anchor_followup_helpers"),
        EXPECTED_DIRECT_ANCHOR_HELPERS,
        "blockers:direct_anchor_followup_helpers",
        failures,
    )
    expect_equal(
        blockers_lane.get("anti_overlap_rule"),
        EXPECTED_ANTI_OVERLAP_RULE,
        "blockers:anti_overlap_rule",
        failures,
    )

    replay = blockers_data.get("replay")
    if not isinstance(replay, dict):
        failures.append("blockers:replay:expected=dict")
    else:
        expect_equal(replay.get("state"), "blocked", "blockers:replay.state", failures)
        expect_equal(replay.get("path"), "zigux/tests/phase1_helpers.zig", "blockers:replay.path", failures)

    c_harness = blockers_data.get("c_harness")
    if not isinstance(c_harness, dict):
        failures.append("blockers:c_harness:expected=dict")
    else:
        expect_equal(c_harness.get("state"), "blocked", "blockers:c_harness.state", failures)
        expect_equal(
            c_harness.get("path"),
            "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "blockers:c_harness.path",
            failures,
        )
        expect_equal(c_harness.get("helper_count"), len(EXPECTED_HELPERS), "blockers:c_harness.helper_count", failures)
        expect_equal(c_harness.get("helpers"), EXPECTED_HELPERS, "blockers:c_harness.helpers", failures)

    return failures


def collect_failures(root: Path) -> list[str]:
    failures = expect_regular_files(root)
    if failures:
        return failures
    failures.extend(verify_artifact_diff(root))
    failures.extend(verify_manifest_and_blockers(root))
    return failures


def sample_artifact_diff() -> str:
    lines = [
        "#!/usr/bin/env python3",
        "from __future__ import annotations",
        "import hashlib",
        "import sys",
        "from pathlib import Path",
        "",
        "HELP_LINES = " + repr(EXPECTED_ARTIFACT_HELP_LINES),
        "SELF_TEST_LINES = " + repr(EXPECTED_ARTIFACT_SELF_TEST_LINES),
        "",
        "def main() -> int:",
        "    argv = sys.argv[1:]",
        "    if argv in ([\"-h\"], [\"--help\"]):",
        "        print(\"\\n\".join(HELP_LINES))",
        "        return 0",
        "    if argv == [\"--self-test\"]:",
        "        print(\"\\n\".join(SELF_TEST_LINES))",
        "        return 0",
        "    if len(argv) != 4 or argv[0] != \"--mode\":",
        "        print(\"unsupported sample invocation\", file=sys.stderr)",
        "        return 2",
        "    mode = argv[1]",
        "    expected = Path(argv[2])",
        "    actual = Path(argv[3])",
        "    return 0",
        "",
        "if __name__ == '__main__':",
        "    argv = sys.argv[1:]",
        "    if argv in ([\"-h\"], [\"--help\"]):",
        "        print(\"\\n\".join(HELP_LINES))",
        "        raise SystemExit(0)",
        "    if argv == [\"--self-test\"]:",
        "        print(\"\\n\".join(SELF_TEST_LINES))",
        "        raise SystemExit(0)",
        "    if len(argv) != 4 or argv[0] != \"--mode\":",
        "        print(\"unsupported sample invocation\", file=sys.stderr)",
        "        raise SystemExit(2)",
        "    mode = argv[1]",
        "    expected = Path(argv[2])",
        "    actual = Path(argv[3])",
        "    digest_expected = hashlib.sha256(expected.read_bytes()).hexdigest()",
        "    digest_actual = hashlib.sha256(actual.read_bytes()).hexdigest()",
        "    if mode == 'sha256' and digest_expected == digest_actual:",
        "        print('ARTIFACT_DIFF=pass')",
        "        print('MODE=bytes')",
        "        print(f'EXPECTED={expected}')",
        "        print(f'ACTUAL={actual}')",
        "        print(f'SHA256={digest_expected}')",
        "        raise SystemExit(0)",
        "    print('unsupported sample invocation', file=sys.stderr)",
        "    raise SystemExit(2)",
    ]
    return "\n".join(lines) + "\n"


def sample_manifest() -> str:
    data = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": len(EXPECTED_HELPERS),
        "helpers": EXPECTED_HELPERS,
        "lane_sequencing": {
            "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_HELPERS,
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_HELPERS,
            "rule_summary": EXPECTED_RULE_SUMMARY,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
    }
    return json.dumps(data, indent=2) + "\n"


def sample_blockers() -> str:
    data = {
        "status": "parked",
        "lane_sequencing": {
            "manifest": MANIFEST_REL.as_posix(),
            "shared_replay_parked_helper_count": len(EXPECTED_SHARED_REPLAY_HELPERS),
            "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_HELPERS,
            "direct_anchor_followup_helper_count": len(EXPECTED_DIRECT_ANCHOR_HELPERS),
            "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_HELPERS,
            "anti_overlap_rule": EXPECTED_ANTI_OVERLAP_RULE,
        },
        "replay": {
            "path": "zigux/tests/phase1_helpers.zig",
            "state": "blocked",
        },
        "c_harness": {
            "path": "zigux/tests/fixtures/phase1_helpers_c_harness.c",
            "state": "blocked",
            "helper_count": len(EXPECTED_HELPERS),
            "helpers": EXPECTED_HELPERS,
        },
    }
    return json.dumps(data, indent=2) + "\n"


def write_sample_root(root: Path) -> None:
    artifact = root / ARTIFACT_DIFF_REL
    write_text(artifact, sample_artifact_diff())
    artifact.chmod(0o755)
    write_text(root / MANIFEST_REL, sample_manifest())
    write_text(root / BLOCKERS_REL, sample_blockers())


def run_self_test() -> int:
    def assert_fails(mutator, expected_fragment: str) -> None:
        with tempfile.TemporaryDirectory(prefix="phase1_artifact_blocker_alignment_case_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            failures = collect_failures(root)
            if not any(expected_fragment in failure for failure in failures):
                raise AssertionError((expected_fragment, failures))

    with tempfile.TemporaryDirectory(prefix="phase1_artifact_blocker_alignment_success_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(failures)

    cases = 0
    assert_fails(lambda root: (root / ARTIFACT_DIFF_REL).unlink(), "missing_file:scripts/zigux/artifact_diff.py")
    cases += 1
    assert_fails(
        lambda root: write_text(root / MANIFEST_REL, "{\n"),
        f"{MANIFEST_REL.as_posix()}:invalid_json:",
    )
    cases += 1
    assert_fails(
        lambda root: write_text(root / BLOCKERS_REL, "{\n"),
        f"{BLOCKERS_REL.as_posix()}:invalid_json:",
    )
    cases += 1
    assert_fails(
        lambda root: write_text(
            root / MANIFEST_REL,
            sample_manifest().replace(
                '"helper_count": 13,',
                '"helper_count": 12,',
                1,
            ),
        ),
        "manifest:helper_count",
    )
    cases += 1
    assert_fails(
        lambda root: write_text(
            root / BLOCKERS_REL,
            sample_blockers().replace(
                '"shared_replay_parked_helper_count": 9,',
                '"shared_replay_parked_helper_count": 8,',
                1,
            ),
        ),
        "blockers:shared_replay_parked_helper_count",
    )
    cases += 1
    assert_fails(
        lambda root: write_text(
            root / BLOCKERS_REL,
            sample_blockers().replace(
                '"state": "blocked"',
                '"state": "open"',
                1,
            ),
        ),
        "blockers:replay.state",
    )
    cases += 1
    assert_fails(
        lambda root: write_text(
            root / BLOCKERS_REL,
            sample_blockers().replace(
                '"state": "blocked"',
                '"state": "parked"',
                2,
            ),
        ),
        "blockers:c_harness.state",
    )
    cases += 1
    assert_fails(
        lambda root: write_text(
            root / ARTIFACT_DIFF_REL,
            sample_artifact_diff().replace("--mode {text,json,bytes}", "--mode {text,json,sha256}", 1),
        ),
        "artifact_diff_help:stdout",
    )
    cases += 1
    assert_fails(
        lambda root: write_text(
            root / ARTIFACT_DIFF_REL,
            sample_artifact_diff().replace("legacy_sha256_alias", "legacy_sha256_alias_drift", 1),
        ),
        "artifact_diff_self_test:stdout",
    )
    cases += 1
    assert_fails(
        lambda root: (root / BLOCKERS_REL).write_text(
            sample_blockers().replace(
                '"anti_overlap_rule": "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys."',
                '"anti_overlap_rule": "drifted"',
                1,
            ),
            encoding="utf-8",
            newline="\n",
        ),
        "blockers:anti_overlap_rule",
    )
    cases += 1

    print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run checker self-test")
    parser.add_argument("--write-sample-root", help="write a current-like sample root")
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SAMPLE_ROOT=written")
        return 0

    if args.self_test:
        return run_self_test()

    root = repo_root(args.root)
    failures = collect_failures(root)
    if failures:
        print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT=fail")
        print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_ISSUES_START")
        for failure in failures:
            print(failure)
        print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_ISSUES_END")
        return 1

    print("PHASE1_ARTIFACT_BLOCKER_ALIGNMENT=pass")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_HELPER_COUNT={len(EXPECTED_HELPERS)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_REPLAY_HELPERS)}")
    print(f"PHASE1_ARTIFACT_BLOCKER_ALIGNMENT_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_ANCHOR_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
