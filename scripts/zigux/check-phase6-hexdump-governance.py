#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
MANIFEST_REL = Path("zigux/tests/fixtures/phase6_hexdump_manifest.json")
HELPER_REL = Path("lib/hexdump.zig")

REQUIRED_TOP_LEVEL = {
    "phase": "Phase 6",
    "helper": "lib/hexdump.zig",
    "status": "pass",
}

REQUIRED_ANCHORS = [
    'test "hex_to_bin alias stays aligned"',
    'test "hex2bin and bin2hex snake-case aliases stay aligned"',
    'test "bin2hexUpper emits uppercase bulk output and alias stays aligned"',
    'test "hexBytePack helpers chain bytes and preserve destination on bounds errors"',
    'test "hexDumpLineLength mirrors formatter normalization"',
    'test "hexDumpToBuffer follows kernel fixture normalization cases"',
    'test "hexDumpToBuffer reports normalized required length for empty and zero-sized buffers"',
]

REQUIRED_ALIAS_EXPORTS = [
    "pub const hex_to_bin = hexToBin;",
    "pub const hex2Bin = hex2bin;",
    "pub const bin2Hex = bin2hex;",
    "pub const bin2HexUpper = bin2hexUpper;",
]

REQUIRED_MARKERS = REQUIRED_ANCHORS + REQUIRED_ALIAS_EXPORTS


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


def manifest_path(root: Path) -> Path:
    return root / MANIFEST_REL


def helper_path(root: Path) -> Path:
    return root / HELPER_REL


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    zig = shutil.which("zig")
    if zig:
        return zig
    raise SystemExit("zig not found; pass --zig or add zig to PATH")


def load_json_text(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_json(path: Path) -> object:
    return load_json_text(path.read_text(encoding="utf-8"))


def validate_manifest(payload: object) -> tuple[str, object]:
    if not isinstance(payload, dict):
        return ("manifest_type", type(payload).__name__)
    if isinstance(payload, DuplicateTrackingDict) and payload.duplicate_keys:
        return ("manifest_duplicate_keys", payload.duplicate_keys)

    for key, expected in REQUIRED_TOP_LEVEL.items():
        if payload.get(key) != expected:
            return ("manifest_field", (key, expected, payload.get(key)))

    anchors = payload.get("helper_test_anchors")
    if not isinstance(anchors, list):
        return ("manifest_anchors_type", type(anchors).__name__)
    if anchors != REQUIRED_ANCHORS:
        return ("manifest_anchor_order", anchors)

    alias_exports = payload.get("alias_exports")
    if not isinstance(alias_exports, list):
        return ("manifest_alias_exports_type", type(alias_exports).__name__)
    if alias_exports != REQUIRED_ALIAS_EXPORTS:
        return ("manifest_alias_export_order", alias_exports)

    for key in ("governance_summary", "next_safe_step_note"):
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            return ("manifest_text_field", key)

    return ("pass", payload)


def validate_helper_source(text: str) -> tuple[str, object]:
    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    if missing:
        return ("helper_source_missing_markers", missing)
    return ("pass", text)


def build_helper_stub(omit_marker: str | None = None) -> str:
    lines = [
        "pub fn hexToBin(ch: u8) i32 {",
        "    _ = ch;",
        "    return 0;",
        "}",
        "pub fn hex2bin(dst: []u8, src: []const u8) error{}!void {",
        "    _ = dst;",
        "    _ = src;",
        "}",
        "pub fn bin2hex(dst: []u8, src: []const u8) error{}![]u8 {",
        "    _ = src;",
        "    return dst[0..0];",
        "}",
        "pub fn bin2hexUpper(dst: []u8, src: []const u8) error{}![]u8 {",
        "    _ = src;",
        "    return dst[0..0];",
        "}",
        'test "hex_to_bin alias stays aligned" {}',
        'test "hex2bin and bin2hex snake-case aliases stay aligned" {}',
        'test "bin2hexUpper emits uppercase bulk output and alias stays aligned" {}',
        'test "hexBytePack helpers chain bytes and preserve destination on bounds errors" {}',
        'test "hexDumpLineLength mirrors formatter normalization" {}',
        'test "hexDumpToBuffer follows kernel fixture normalization cases" {}',
        'test "hexDumpToBuffer reports normalized required length for empty and zero-sized buffers" {}',
        "pub const hex_to_bin = hexToBin;",
        "pub const hex2Bin = hex2bin;",
        "pub const bin2Hex = bin2hex;",
        "pub const bin2HexUpper = bin2hexUpper;",
    ]
    if omit_marker is not None:
        lines = [line for line in lines if omit_marker not in line]
    return "\n".join(lines) + "\n"


def base_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 6",
        "helper": "lib/hexdump.zig",
        "status": "pass",
        "helper_test_anchors": list(REQUIRED_ANCHORS),
        "alias_exports": list(REQUIRED_ALIAS_EXPORTS),
        "governance_summary": "Phase 6 hexdump ownership stays bounded to alias parity, bulk encoder boundaries, formatter normalization, kernel-style fixture replay, and empty-buffer length reporting.",
        "next_safe_step_note": "If this lane reopens, keep it on helper-local normalization, alias, or fixture drift inside lib/hexdump.zig before widening into broader Phase 6 batching.",
    }


def assert_case(condition: bool, name: str, payload: object = None) -> None:
    if not condition:
        raise AssertionError((name, payload))


def run_self_test() -> None:
    case_count = 0

    kind, payload = validate_manifest(base_manifest())
    assert_case(kind == "pass", "manifest pass", (kind, payload))
    case_count += 1

    kind, payload = validate_helper_source(build_helper_stub())
    assert_case(kind == "pass", "helper source pass", (kind, payload))
    case_count += 1

    duplicate_manifest_text = """{
  "phase": "Phase 6",
  "phase": "Phase 5",
  "helper": "lib/hexdump.zig",
  "status": "pass",
  "helper_test_anchors": ["test \"hex_to_bin alias stays aligned\""],
  "alias_exports": ["pub const hex_to_bin = hexToBin;"],
  "governance_summary": "x",
  "next_safe_step_note": "y"
}"""
    kind, payload = validate_manifest(load_json_text(duplicate_manifest_text))
    assert_case(kind == "manifest_duplicate_keys", "duplicate manifest key", (kind, payload))
    assert_case(payload == ["phase"], "duplicate manifest payload", payload)
    case_count += 1

    bad_manifest = base_manifest()
    bad_manifest["helper_test_anchors"] = bad_manifest["helper_test_anchors"][:-1]
    kind, payload = validate_manifest(bad_manifest)
    assert_case(kind == "manifest_anchor_order", "anchor mismatch", (kind, payload))
    case_count += 1

    missing_marker = REQUIRED_ALIAS_EXPORTS[-1]
    kind, payload = validate_helper_source(build_helper_stub(omit_marker=missing_marker))
    assert_case(kind == "helper_source_missing_markers", "missing marker", (kind, payload))
    assert_case(payload == [missing_marker], "missing marker payload", payload)
    case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase6-hexdump-governance-") as tmp:
        root = Path(tmp)
        helper = helper_path(root)
        helper.parent.mkdir(parents=True, exist_ok=True)
        helper.write_text(build_helper_stub(), encoding="utf-8")

        manifest = manifest_path(root)
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps(base_manifest(), indent=2) + "\n", encoding="utf-8")

        kind, payload = validate_manifest(load_json(manifest))
        assert_case(kind == "pass", "loaded manifest pass", (kind, payload))
        kind, payload = validate_helper_source(helper.read_text(encoding="utf-8"))
        assert_case(kind == "pass", "loaded helper pass", (kind, payload))
        case_count += 2

    print("PHASE6_HEXDUMP_GOVERNANCE_SELF_TEST=pass")
    print(f"PHASE6_HEXDUMP_GOVERNANCE_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded Phase 6 hexdump governance packet.")
    parser.add_argument("--repo-root", "--root", dest="repo_root", help="Override the repository root used for validation.")
    parser.add_argument("--zig", help="Path to Zig executable")
    parser.add_argument("--skip-zig-test", action="store_true", help="Only validate the governance manifest and source markers.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests without using a repository checkout.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.repo_root)
    manifest = manifest_path(root)
    helper = helper_path(root)

    try:
        manifest_payload = load_json(manifest)
    except FileNotFoundError:
        print("PHASE6_HEXDUMP_GOVERNANCE=fail")
        print(f"PHASE6_HEXDUMP_GOVERNANCE_REASON=missing_manifest:{manifest}")
        return 1
    except json.JSONDecodeError as exc:
        print("PHASE6_HEXDUMP_GOVERNANCE=fail")
        print(f"PHASE6_HEXDUMP_GOVERNANCE_REASON=manifest_json_error:{exc.msg}:{exc.lineno}:{exc.colno}")
        return 1

    kind, payload = validate_manifest(manifest_payload)
    if kind != "pass":
        print("PHASE6_HEXDUMP_GOVERNANCE=fail")
        print(f"PHASE6_HEXDUMP_GOVERNANCE_REASON={kind}")
        print(payload)
        return 1

    try:
        helper_source = helper.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("PHASE6_HEXDUMP_GOVERNANCE=fail")
        print(f"PHASE6_HEXDUMP_GOVERNANCE_REASON=missing_helper:{helper}")
        return 1

    kind, payload = validate_helper_source(helper_source)
    if kind != "pass":
        print("PHASE6_HEXDUMP_GOVERNANCE=fail")
        print(f"PHASE6_HEXDUMP_GOVERNANCE_REASON={kind}")
        print(payload)
        return 1

    if args.skip_zig_test:
        print("PHASE6_HEXDUMP_GOVERNANCE=pass")
        print(f"PHASE6_HEXDUMP_MANIFEST={manifest}")
        print(f"PHASE6_HEXDUMP_HELPER={helper}")
        print("PHASE6_HEXDUMP_ZIG_TEST=skipped")
        return 0

    zig = find_zig(args.zig)
    result = subprocess.run(
        [zig, "test", str(helper)],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("PHASE6_HEXDUMP_GOVERNANCE=fail")
        print(f"PHASE6_HEXDUMP_GOVERNANCE_REASON=zig_test_exit:{result.returncode}")
        if result.stdout:
            print(result.stdout.rstrip("\n"))
        if result.stderr:
            print(result.stderr.rstrip("\n"))
        return 1

    print("PHASE6_HEXDUMP_GOVERNANCE=pass")
    print(f"PHASE6_HEXDUMP_MANIFEST={manifest}")
    print(f"PHASE6_HEXDUMP_HELPER={helper}")
    print(f"PHASE6_HEXDUMP_ZIG={zig}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
