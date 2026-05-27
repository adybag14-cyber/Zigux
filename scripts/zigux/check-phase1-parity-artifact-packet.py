#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER_REL = Path("scripts/zigux/artifact_diff.py")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
BLOCKERS_REL = Path("zigux/tests/fixtures/phase1_replay_blockers.json")

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
EXPECTED_SHARED_HELPERS = [
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
EXPECTED_DIRECT_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]
EXPECTED_FIXTURE_SECTIONS = [
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
EXPECTED_ANTI_OVERLAP_RULE = (
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; "
    "shared-replay parked helpers reopen only for packet drift, while direct-anchor "
    "helpers reopen only for their existing helper-local anchors or already-committed "
    "shared fixture keys."
)
EXPECTED_REQUIRED_FILES = [
    HELPER_REL,
    FIXTURE_REL,
    MANIFEST_REL,
    BLOCKERS_REL,
]
EXPECTED_MODES = ["text", "json", "bytes"]

ARTIFACT_HELPER_TEXT = """#!/usr/bin/env python3
MODE_CHOICES = (\"text\", \"json\", \"bytes\")
LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}
SELF_TEST_CASES = [
    \"text_pass\",
    \"json_pass\",
    \"bytes_pass\",
    \"legacy_sha256_alias\",
]
"""

FIXTURE_TEXT = """{
  \"find_bit\": {},
  \"bitmap\": {},
  \"string\": {},
  \"rbtree\": {},
  \"argv_split\": {},
  \"cmdline\": {},
  \"ctype\": {},
  \"hweight\": {},
  \"list_sort\": {},
  \"zalloc\": {},
  \"str_error_r\": {},
  \"slab\": {},
  \"vsprintf\": {}
}
"""

MANIFEST_TEXT = """{
  \"phase\": \"Phase 1\",
  \"status\": \"closed\",
  \"helper_count\": 13,
  \"helpers\": [
    \"tools/lib/argv_split.zig\",
    \"tools/lib/bitmap.zig\",
    \"tools/lib/cmdline.zig\",
    \"tools/lib/ctype.zig\",
    \"tools/lib/find_bit.zig\",
    \"tools/lib/hweight.zig\",
    \"tools/lib/list_sort.zig\",
    \"tools/lib/rbtree.zig\",
    \"tools/lib/slab.zig\",
    \"tools/lib/str_error_r.zig\",
    \"tools/lib/string.zig\",
    \"tools/lib/vsprintf.zig\",
    \"tools/lib/zalloc.zig\"
  ],
  \"lane_sequencing\": {
    \"shared_replay_parked_helpers\": [
      \"tools/lib/argv_split.zig\",
      \"tools/lib/cmdline.zig\",
      \"tools/lib/ctype.zig\",
      \"tools/lib/hweight.zig\",
      \"tools/lib/list_sort.zig\",
      \"tools/lib/slab.zig\",
      \"tools/lib/str_error_r.zig\",
      \"tools/lib/vsprintf.zig\",
      \"tools/lib/zalloc.zig\"
    ],
    \"direct_anchor_followup_helpers\": [
      \"tools/lib/bitmap.zig\",
      \"tools/lib/find_bit.zig\",
      \"tools/lib/rbtree.zig\",
      \"tools/lib/string.zig\"
    ],
    \"anti_overlap_rule\": \"Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.\"
  }
}
"""

BLOCKERS_TEXT = """{
  \"status\": \"parked\",
  \"lane_sequencing\": {
    \"manifest\": \"zigux/tests/fixtures/phase1_helper_manifest.json\",
    \"shared_replay_parked_helper_count\": 9,
    \"shared_replay_parked_helpers\": [
      \"tools/lib/argv_split.zig\",
      \"tools/lib/cmdline.zig\",
      \"tools/lib/ctype.zig\",
      \"tools/lib/hweight.zig\",
      \"tools/lib/list_sort.zig\",
      \"tools/lib/slab.zig\",
      \"tools/lib/str_error_r.zig\",
      \"tools/lib/vsprintf.zig\",
      \"tools/lib/zalloc.zig\"
    ],
    \"direct_anchor_followup_helper_count\": 4,
    \"direct_anchor_followup_helpers\": [
      \"tools/lib/bitmap.zig\",
      \"tools/lib/find_bit.zig\",
      \"tools/lib/rbtree.zig\",
      \"tools/lib/string.zig\"
    ],
    \"anti_overlap_rule\": \"Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.\"
  },
  \"replay\": {
    \"path\": \"zigux/tests/phase1_helpers.zig\",
    \"state\": \"blocked\"
  },
  \"c_harness\": {
    \"path\": \"zigux/tests/fixtures/phase1_helpers_c_harness.c\",
    \"state\": \"blocked\",
    \"helper_count\": 13,
    \"blocker_id\": \"phase1_helpers_c_harness_missing_c_sources\"
  }
}
"""

SELF_TEST_CASES = [
    "pass_current_like_packet",
    "missing_required_file",
    "required_path_is_directory",
    "invalid_fixture_json",
    "artifact_mode_drift",
    "fixture_section_drift",
    "manifest_helper_count_drift",
    "manifest_shared_split_drift",
    "blocker_manifest_pointer_drift",
    "blocker_split_drift",
    "anti_overlap_rule_drift",
    "blocked_state_drift",
]


class PacketError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail closed on the Phase 1 parity-fixture and artifact-diff packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def ensure_file(path: Path) -> None:
    if not path.exists():
        raise PacketError(f"missing required file: {path}")
    if not path.is_file():
        raise PacketError(f"required path is not a file: {path}")


def load_json(path: Path) -> object:
    ensure_file(path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PacketError(f"invalid JSON in {path}: {exc.msg}") from exc


def parse_python_list(source: str, name: str) -> list[str]:
    marker = f"{name} ="
    start = source.find(marker)
    if start < 0:
        raise PacketError(f"missing {name} in artifact helper")
    anchor = source.find("[", start)
    if anchor < 0:
        raise PacketError(f"missing list payload for {name}")
    depth = 0
    for index in range(anchor, len(source)):
        char = source[index]
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return ast.literal_eval(source[anchor : index + 1])
    raise PacketError(f"unterminated list payload for {name}")


def parse_mode_choices(source: str) -> list[str]:
    marker = "MODE_CHOICES ="
    start = source.find(marker)
    if start < 0:
        raise PacketError("missing MODE_CHOICES in artifact helper")
    anchor = source.find("(", start)
    if anchor < 0:
        raise PacketError("missing MODE_CHOICES payload in artifact helper")
    depth = 0
    for index in range(anchor, len(source)):
        char = source[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return list(ast.literal_eval(source[anchor : index + 1]))
    raise PacketError("unterminated MODE_CHOICES payload in artifact helper")


def validate(root: Path) -> list[str]:
    helper_path = root / HELPER_REL
    fixture_path = root / FIXTURE_REL
    manifest_path = root / MANIFEST_REL
    blockers_path = root / BLOCKERS_REL

    for rel in EXPECTED_REQUIRED_FILES:
        ensure_file(root / rel)

    helper_source = helper_path.read_text(encoding="utf-8")
    modes = parse_mode_choices(helper_source)
    if modes != EXPECTED_MODES:
        raise PacketError(f"artifact helper mode drift: expected {EXPECTED_MODES}, got {modes}")
    helper_self_test_cases = parse_python_list(helper_source, "SELF_TEST_CASES")
    if "legacy_sha256_alias" not in helper_self_test_cases:
        raise PacketError("artifact helper lost legacy_sha256_alias self-test coverage")

    fixture = load_json(fixture_path)
    manifest = load_json(manifest_path)
    blockers = load_json(blockers_path)

    if not isinstance(fixture, dict):
        raise PacketError("phase1 helper fixture root must be an object")
    fixture_sections = list(fixture.keys())
    if fixture_sections != EXPECTED_FIXTURE_SECTIONS:
        raise PacketError(
            f"fixture section drift: expected {EXPECTED_FIXTURE_SECTIONS}, got {fixture_sections}"
        )

    if not isinstance(manifest, dict):
        raise PacketError("phase1 helper manifest root must be an object")
    manifest_helpers = manifest.get("helpers")
    if manifest_helpers != EXPECTED_HELPERS:
        raise PacketError("phase1 helper manifest helper roster drifted")
    if manifest.get("helper_count") != len(EXPECTED_HELPERS):
        raise PacketError("phase1 helper manifest helper_count drifted")
    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        raise PacketError("phase1 helper manifest lane_sequencing must be an object")
    if lane_sequencing.get("shared_replay_parked_helpers") != EXPECTED_SHARED_HELPERS:
        raise PacketError("phase1 helper manifest shared replay split drifted")
    if lane_sequencing.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_HELPERS:
        raise PacketError("phase1 helper manifest direct anchor split drifted")
    if lane_sequencing.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        raise PacketError("phase1 helper manifest anti-overlap rule drifted")

    if not isinstance(blockers, dict):
        raise PacketError("phase1 replay blockers root must be an object")
    if blockers.get("status") != "parked":
        raise PacketError("phase1 replay blockers status drifted")
    blocker_lane = blockers.get("lane_sequencing")
    if not isinstance(blocker_lane, dict):
        raise PacketError("phase1 replay blockers lane_sequencing must be an object")
    if blocker_lane.get("manifest") != str(MANIFEST_REL):
        raise PacketError("phase1 replay blockers manifest pointer drifted")
    if blocker_lane.get("shared_replay_parked_helper_count") != len(EXPECTED_SHARED_HELPERS):
        raise PacketError("phase1 replay blockers shared helper count drifted")
    if blocker_lane.get("shared_replay_parked_helpers") != EXPECTED_SHARED_HELPERS:
        raise PacketError("phase1 replay blockers shared helper roster drifted")
    if blocker_lane.get("direct_anchor_followup_helper_count") != len(EXPECTED_DIRECT_HELPERS):
        raise PacketError("phase1 replay blockers direct helper count drifted")
    if blocker_lane.get("direct_anchor_followup_helpers") != EXPECTED_DIRECT_HELPERS:
        raise PacketError("phase1 replay blockers direct helper roster drifted")
    if blocker_lane.get("anti_overlap_rule") != EXPECTED_ANTI_OVERLAP_RULE:
        raise PacketError("phase1 replay blockers anti-overlap rule drifted")

    replay = blockers.get("replay")
    if not isinstance(replay, dict):
        raise PacketError("phase1 replay blockers replay packet must be an object")
    if replay.get("path") != "zigux/tests/phase1_helpers.zig":
        raise PacketError("phase1 replay blockers replay path drifted")
    if replay.get("state") != "blocked":
        raise PacketError("phase1 replay blockers replay state drifted")

    c_harness = blockers.get("c_harness")
    if not isinstance(c_harness, dict):
        raise PacketError("phase1 replay blockers c_harness packet must be an object")
    if c_harness.get("path") != "zigux/tests/fixtures/phase1_helpers_c_harness.c":
        raise PacketError("phase1 replay blockers c_harness path drifted")
    if c_harness.get("state") != "blocked":
        raise PacketError("phase1 replay blockers c_harness state drifted")
    if c_harness.get("helper_count") != len(EXPECTED_HELPERS):
        raise PacketError("phase1 replay blockers c_harness helper_count drifted")
    if c_harness.get("blocker_id") != "phase1_helpers_c_harness_missing_c_sources":
        raise PacketError("phase1 replay blockers c_harness blocker_id drifted")

    return [
        "PHASE1_PARITY_ARTIFACT_PACKET=pass",
        f"PHASE1_PARITY_ARTIFACT_PACKET_REQUIRED_FILE_COUNT={len(EXPECTED_REQUIRED_FILES)}",
        f"PHASE1_PARITY_ARTIFACT_PACKET_ARTIFACT_MODE_COUNT={len(modes)}",
        f"PHASE1_PARITY_ARTIFACT_PACKET_FIXTURE_SECTION_COUNT={len(fixture_sections)}",
        f"PHASE1_PARITY_ARTIFACT_PACKET_HELPER_COUNT={len(EXPECTED_HELPERS)}",
        f"PHASE1_PARITY_ARTIFACT_PACKET_SHARED_HELPER_COUNT={len(EXPECTED_SHARED_HELPERS)}",
        f"PHASE1_PARITY_ARTIFACT_PACKET_DIRECT_HELPER_COUNT={len(EXPECTED_DIRECT_HELPERS)}",
        f"PHASE1_PARITY_ARTIFACT_PACKET_REPLAY_STATE={replay['state']}",
        f"PHASE1_PARITY_ARTIFACT_PACKET_C_HARNESS_STATE={c_harness['state']}",
    ]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root / HELPER_REL, ARTIFACT_HELPER_TEXT)
    write_text(root / FIXTURE_REL, FIXTURE_TEXT)
    write_text(root / MANIFEST_REL, MANIFEST_TEXT)
    write_text(root / BLOCKERS_REL, BLOCKERS_TEXT)


def assert_case(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def run_self_test() -> int:
    import tempfile

    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_lane09_parity_artifact_") as tmp_dir:
        root = Path(tmp_dir) / "current_like"
        write_sample_root(root)
        assert_case(
            validate(root)[0] == "PHASE1_PARITY_ARTIFACT_PACKET=pass",
            "pass_current_like_packet",
        )
        covered.append("pass_current_like_packet")

        missing_root = Path(tmp_dir) / "missing"
        write_sample_root(missing_root)
        (missing_root / BLOCKERS_REL).unlink()
        try:
            validate(missing_root)
        except PacketError as exc:
            assert_case("missing required file" in str(exc), "missing_required_file")
            covered.append("missing_required_file")
        else:
            raise AssertionError("missing_required_file")

        dir_root = Path(tmp_dir) / "directory"
        write_sample_root(dir_root)
        (dir_root / FIXTURE_REL).unlink()
        (dir_root / FIXTURE_REL).mkdir(parents=True)
        try:
            validate(dir_root)
        except PacketError as exc:
            assert_case("required path is not a file" in str(exc), "required_path_is_directory")
            covered.append("required_path_is_directory")
        else:
            raise AssertionError("required_path_is_directory")

        invalid_root = Path(tmp_dir) / "invalid"
        write_sample_root(invalid_root)
        write_text(invalid_root / FIXTURE_REL, "{\n")
        try:
            validate(invalid_root)
        except PacketError as exc:
            assert_case("invalid JSON" in str(exc), "invalid_fixture_json")
            covered.append("invalid_fixture_json")
        else:
            raise AssertionError("invalid_fixture_json")

        mode_root = Path(tmp_dir) / "mode"
        write_sample_root(mode_root)
        write_text(mode_root / HELPER_REL, ARTIFACT_HELPER_TEXT.replace('"bytes"', '"sha256"', 1))
        try:
            validate(mode_root)
        except PacketError as exc:
            assert_case("mode drift" in str(exc), "artifact_mode_drift")
            covered.append("artifact_mode_drift")
        else:
            raise AssertionError("artifact_mode_drift")

        section_root = Path(tmp_dir) / "sections"
        write_sample_root(section_root)
        section_data = json.loads((section_root / FIXTURE_REL).read_text(encoding="utf-8"))
        section_data["phase1_extra"] = {}
        write_text(section_root / FIXTURE_REL, json.dumps(section_data, indent=2) + "\n")
        try:
            validate(section_root)
        except PacketError as exc:
            assert_case("fixture section drift" in str(exc), "fixture_section_drift")
            covered.append("fixture_section_drift")
        else:
            raise AssertionError("fixture_section_drift")

        helper_count_root = Path(tmp_dir) / "helper_count"
        write_sample_root(helper_count_root)
        manifest_data = json.loads((helper_count_root / MANIFEST_REL).read_text(encoding="utf-8"))
        manifest_data["helper_count"] = 12
        write_text(helper_count_root / MANIFEST_REL, json.dumps(manifest_data, indent=2) + "\n")
        try:
            validate(helper_count_root)
        except PacketError as exc:
            assert_case("helper_count drifted" in str(exc), "manifest_helper_count_drift")
            covered.append("manifest_helper_count_drift")
        else:
            raise AssertionError("manifest_helper_count_drift")

        shared_root = Path(tmp_dir) / "shared"
        write_sample_root(shared_root)
        manifest_data = json.loads((shared_root / MANIFEST_REL).read_text(encoding="utf-8"))
        manifest_data["lane_sequencing"]["shared_replay_parked_helpers"] = EXPECTED_SHARED_HELPERS[:-1]
        write_text(shared_root / MANIFEST_REL, json.dumps(manifest_data, indent=2) + "\n")
        try:
            validate(shared_root)
        except PacketError as exc:
            assert_case("shared replay split drifted" in str(exc), "manifest_shared_split_drift")
            covered.append("manifest_shared_split_drift")
        else:
            raise AssertionError("manifest_shared_split_drift")

        pointer_root = Path(tmp_dir) / "pointer"
        write_sample_root(pointer_root)
        blocker_data = json.loads((pointer_root / BLOCKERS_REL).read_text(encoding="utf-8"))
        blocker_data["lane_sequencing"]["manifest"] = "zigux/tests/fixtures/other.json"
        write_text(pointer_root / BLOCKERS_REL, json.dumps(blocker_data, indent=2) + "\n")
        try:
            validate(pointer_root)
        except PacketError as exc:
            assert_case("manifest pointer drifted" in str(exc), "blocker_manifest_pointer_drift")
            covered.append("blocker_manifest_pointer_drift")
        else:
            raise AssertionError("blocker_manifest_pointer_drift")

        blocker_split_root = Path(tmp_dir) / "blocker_split"
        write_sample_root(blocker_split_root)
        blocker_data = json.loads((blocker_split_root / BLOCKERS_REL).read_text(encoding="utf-8"))
        blocker_data["lane_sequencing"]["direct_anchor_followup_helper_count"] = 3
        write_text(blocker_split_root / BLOCKERS_REL, json.dumps(blocker_data, indent=2) + "\n")
        try:
            validate(blocker_split_root)
        except PacketError as exc:
            assert_case("direct helper count drifted" in str(exc), "blocker_split_drift")
            covered.append("blocker_split_drift")
        else:
            raise AssertionError("blocker_split_drift")

        rule_root = Path(tmp_dir) / "rule"
        write_sample_root(rule_root)
        blocker_data = json.loads((rule_root / BLOCKERS_REL).read_text(encoding="utf-8"))
        blocker_data["lane_sequencing"]["anti_overlap_rule"] = "changed"
        write_text(rule_root / BLOCKERS_REL, json.dumps(blocker_data, indent=2) + "\n")
        try:
            validate(rule_root)
        except PacketError as exc:
            assert_case("anti-overlap rule drifted" in str(exc), "anti_overlap_rule_drift")
            covered.append("anti_overlap_rule_drift")
        else:
            raise AssertionError("anti_overlap_rule_drift")

        state_root = Path(tmp_dir) / "state"
        write_sample_root(state_root)
        blocker_data = json.loads((state_root / BLOCKERS_REL).read_text(encoding="utf-8"))
        blocker_data["replay"]["state"] = "open"
        write_text(state_root / BLOCKERS_REL, json.dumps(blocker_data, indent=2) + "\n")
        try:
            validate(state_root)
        except PacketError as exc:
            assert_case("replay state drifted" in str(exc), "blocked_state_drift")
            covered.append("blocked_state_drift")
        else:
            raise AssertionError("blocked_state_drift")

    if covered != SELF_TEST_CASES:
        raise AssertionError(f"self-test catalog drifted: {covered} != {SELF_TEST_CASES}")

    print("PHASE1_PARITY_ARTIFACT_PACKET_SELF_TEST=pass")
    print(f"PHASE1_PARITY_ARTIFACT_PACKET_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    print("PHASE1_PARITY_ARTIFACT_PACKET_SELF_TEST_CASES=" + ",".join(SELF_TEST_CASES))
    return 0


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
    if args.self_test:
        return run_self_test()
    try:
        lines = validate(args.root)
    except PacketError as exc:
        print("PHASE1_PARITY_ARTIFACT_PACKET=fail")
        print(f"PHASE1_PARITY_ARTIFACT_PACKET_ERROR={exc}")
        return 1
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
