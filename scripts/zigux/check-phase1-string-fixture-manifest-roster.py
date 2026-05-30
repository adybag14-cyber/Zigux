#!/usr/bin/env python3
"""Guard Phase 1 string fixture keys against manifest roster drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
STRING_HELPER = "tools/lib/string.zig"


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=DuplicateTrackingDict)


def duplicate_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(duplicate_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(duplicate_paths(item, prefix))
    return paths


def json_error(label: str, exc: json.JSONDecodeError) -> str:
    return f"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"


def require_mapping(label: str, value: object) -> tuple[dict[str, object] | None, list[str]]:
    if isinstance(value, dict):
        return value, []
    return None, [f"{label}:expected=dict:actual={type(value).__name__}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    manifest_path = root / MANIFEST_REL
    fixture_path = root / FIXTURE_REL
    for path in (manifest_path, fixture_path):
        if not path.exists():
            failures.append(f"missing_file:{path.relative_to(root).as_posix()}")
    if failures:
        return failures

    try:
        manifest = load_json(manifest_path)
    except json.JSONDecodeError as exc:
        return [json_error("manifest", exc)]
    try:
        fixture = load_json(fixture_path)
    except json.JSONDecodeError as exc:
        return [json_error("fixture", exc)]

    for path in duplicate_paths(manifest):
        failures.append(f"manifest:duplicate_json_key:{path}")
    for path in duplicate_paths(fixture):
        failures.append(f"fixture:duplicate_json_key:{path}")
    if failures:
        return failures

    manifest_map, mapping_failures = require_mapping("manifest", manifest)
    failures.extend(mapping_failures)
    fixture_map, mapping_failures = require_mapping("fixture", fixture)
    failures.extend(mapping_failures)
    if failures:
        return failures

    review_anchors, mapping_failures = require_mapping("manifest.review_anchors", manifest_map.get("review_anchors"))
    failures.extend(mapping_failures)
    if review_anchors is None:
        return failures
    string_packet, mapping_failures = require_mapping(
        f"manifest.review_anchors.{STRING_HELPER}", review_anchors.get(STRING_HELPER)
    )
    failures.extend(mapping_failures)
    string_fixture, mapping_failures = require_mapping("fixture.string", fixture_map.get("string"))
    failures.extend(mapping_failures)
    if failures or string_packet is None or string_fixture is None:
        return failures

    manifest_keys = string_packet.get("parity_fixture_keys")
    if not isinstance(manifest_keys, list) or not all(isinstance(item, str) for item in manifest_keys):
        return [
            "manifest.review_anchors.tools/lib/string.zig.parity_fixture_keys:expected=list[str]"
        ]

    manifest_key_set = set(manifest_keys)
    fixture_key_set = set(string_fixture.keys())
    missing = [key for key in manifest_keys if key not in fixture_key_set]
    extra = sorted(fixture_key_set - manifest_key_set)
    duplicate_manifest_keys = sorted({key for key in manifest_keys if manifest_keys.count(key) > 1})

    if duplicate_manifest_keys:
        failures.append(
            "string_fixture_manifest_roster:duplicate_manifest_parity_keys="
            + ",".join(duplicate_manifest_keys)
        )
    if missing:
        failures.append("string_fixture_manifest_roster:missing_fixture_keys=" + ",".join(missing))
    if extra:
        failures.append("string_fixture_manifest_roster:extra_fixture_keys=" + ",".join(extra))

    return failures


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def write_sample(root: Path) -> None:
    write_json(
        root / MANIFEST_REL,
        {
            "review_anchors": {
                STRING_HELPER: {
                    "parity_fixture_keys": [
                        "strtobool_y",
                        "strlcpy_len",
                        "replace_char_cstr_bytes",
                    ]
                }
            }
        },
    )
    write_json(
        root / FIXTURE_REL,
        {
            "string": {
                "strtobool_y": True,
                "strlcpy_len": 5,
                "replace_char_cstr_bytes": [97, 95, 0, 45, 122],
            }
        },
    )


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-string-roster-") as tmp:
        root = Path(tmp)
        if "missing_file:zigux/tests/fixtures/phase1_helper_manifest.json" not in collect_failures(root):
            raise SystemExit("phase1-string-roster:self-test:missing_manifest")

        write_sample(root)
        if collect_failures(root):
            raise SystemExit("phase1-string-roster:self-test:baseline")

        fixture_path = root / FIXTURE_REL
        fixture = load_json(fixture_path)
        assert isinstance(fixture, dict)
        fixture["string"]["unreviewed_new_key"] = "drift"
        write_json(fixture_path, fixture)
        failures = collect_failures(root)
        if "string_fixture_manifest_roster:extra_fixture_keys=unreviewed_new_key" not in failures:
            raise SystemExit("phase1-string-roster:self-test:extra_fixture_key")

        write_sample(root)
        fixture = load_json(fixture_path)
        assert isinstance(fixture, dict)
        del fixture["string"]["strlcpy_len"]
        write_json(fixture_path, fixture)
        failures = collect_failures(root)
        if "string_fixture_manifest_roster:missing_fixture_keys=strlcpy_len" not in failures:
            raise SystemExit("phase1-string-roster:self-test:missing_fixture_key")

        write_sample(root)
        manifest_path = root / MANIFEST_REL
        manifest = load_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["review_anchors"][STRING_HELPER]["parity_fixture_keys"].append("strlcpy_len")
        write_json(manifest_path, manifest)
        failures = collect_failures(root)
        if "string_fixture_manifest_roster:duplicate_manifest_parity_keys=strlcpy_len" not in failures:
            raise SystemExit("phase1-string-roster:self-test:duplicate_manifest_key")

    print("PHASE1_STRING_FIXTURE_MANIFEST_ROSTER_SELF_TEST=pass")
    print("PHASE1_STRING_FIXTURE_MANIFEST_ROSTER_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    failures = collect_failures(Path(args.root).resolve() if args.root else DEFAULT_ROOT.resolve())
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("phase1-string-fixture-manifest-roster:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
