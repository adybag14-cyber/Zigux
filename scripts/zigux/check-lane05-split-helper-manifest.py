#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def load_policy(root: Path) -> dict[str, object]:
    policy_path = root / POLICY_PATH
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing toolchain policy: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")
    return payload


def require_string(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {key} in {POLICY_PATH}")
    return value.strip()


def require_string_list(payload: dict[str, object], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"invalid {key} in {POLICY_PATH}")
    items: list[str] = []
    for entry in value:
        if not isinstance(entry, str) or not entry.strip():
            raise ValueError(f"invalid {key} entry in {POLICY_PATH}")
        items.append(entry.strip())
    return items


def require_string_map(payload: dict[str, object], key: str) -> dict[str, str]:
    value = payload.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"invalid {key} in {POLICY_PATH}")
    normalized: dict[str, str] = {}
    for map_key, map_value in value.items():
        if not isinstance(map_key, str) or not map_key.strip():
            raise ValueError(f"invalid {key} target in {POLICY_PATH}")
        if not isinstance(map_value, str) or not map_value.strip():
            raise ValueError(f"invalid {key}[{map_key}] in {POLICY_PATH}")
        normalized[map_key.strip()] = map_value.strip().lower()
    return normalized


def resolve_contract(root: Path) -> dict[str, object]:
    payload = load_policy(root)
    channel = require_string(payload, "channel")
    archives = require_string_map(payload, "archive_sha256")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {POLICY_PATH}")
    targets = require_string_list(upgrade_policy, "archive_target_scope")
    if len(targets) != 1:
        raise ValueError(f"expected exactly one archive target in {POLICY_PATH}, got {len(targets)}")

    target = targets[0]
    if target not in archives:
        raise ValueError(f"archive_target_scope target {target} missing from archive_sha256 in {POLICY_PATH}")
    if target not in EXPECTED_ARCHIVE_SIZES:
        raise ValueError(f"missing expected archive size for {target}")

    return {
        "target": target,
        "channel": channel,
        "sha256": archives[target],
        "size": EXPECTED_ARCHIVE_SIZES[target],
        "filename": f"zig-{target}-{channel}.tar.xz",
    }


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 split helper manifest checker missing {label}: {marker}")


def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise ValueError(
            "lane05 split helper manifest checker expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 split helper manifest checker missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            "lane05 split helper manifest checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_helper(root: Path, contract: dict[str, object]) -> int:
    helper_text = read_text(root / HELPER_PATH)
    target = str(contract["target"])
    filename = str(contract["filename"])
    size = int(contract["size"])

    helper_markers = [
        "DEFAULT_CHUNK_BYTES = 786_432",
        f'"{target}": {size},',
        '"filename": f"zig-{target}-{channel}.tar.xz"',
        '"encoding": "base64"',
        '"parts_glob": "part-*.b64"',
        "split_archive(",
        "reconstruct_archive(",
        "write_manifest(",
        "load_manifest(",
        "SPLIT_PINNED_ZIG_ARCHIVE=pass",
        "SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST=",
        "SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT=",
        "RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass",
        "RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT=",
        "--chunk-bytes",
        "--parts-dir",
        "--destination",
        "choose either split mode (--source/--output-dir) or reconstruct mode (--parts-dir/--destination)",
        "--source and --output-dir are required for split mode",
        "--parts-dir and --destination are required for reconstruct mode",
        "part-*.b64",
        filename,
    ]
    for marker in helper_markers:
        require_marker(helper_text, marker, "split helper marker")

    for line, label in (
        ('print("SPLIT_PINNED_ZIG_ARCHIVE=pass")', "split success output"),
        ('print(f"SPLIT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")', "split filename output"),
        ('print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")', "split part-count output"),
        ('print(f"SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={manifest_path}")', "split manifest output"),
        ('print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")', "reconstruct success output"),
        (
            'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={metadata[\'part_count\']}")',
            "reconstruct part-count output",
        ),
    ):
        require_exact_line(helper_text, line, label)

    require_order(
        helper_text,
        'print("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
        "split output order",
    )
    require_order(
        helper_text,
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")',
        "split output order",
    )
    require_order(
        helper_text,
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")',
        'print(f"SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={manifest_path}")',
        "split output order",
    )
    require_order(
        helper_text,
        'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
        'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={metadata[\'part_count\']}")',
        "reconstruct output order",
    )
    return len(helper_markers)


def write_fixture(root: Path) -> None:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)

    (root / POLICY_PATH).write_text(
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    (root / HELPER_PATH).write_text(
        "\n".join(
            [
                "DEFAULT_CHUNK_BYTES = 786_432",
                'EXPECTED_ARCHIVE_SIZES = {',
                '    "x86_64-linux": 58159088,',
                '}',
                'return {"filename": f"zig-{target}-{channel}.tar.xz"}',
                'manifest = {"encoding": "base64", "parts_glob": "part-*.b64"}',
                "def write_manifest():",
                "    pass",
                "def load_manifest():",
                "    pass",
                "def split_archive():",
                "    pass",
                "def reconstruct_archive():",
                "    pass",
                "--chunk-bytes",
                "--parts-dir",
                "--destination",
                "--source and --output-dir are required for split mode",
                "--parts-dir and --destination are required for reconstruct mode",
                "choose either split mode (--source/--output-dir) or reconstruct mode (--parts-dir/--destination)",
                "part-*.b64",
                "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
                'print("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")',
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={manifest_path}")',
                'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
                'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={metadata[\'part_count\']}")',
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_manifest_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        contract = resolve_contract(root)
        assert check_helper(root, contract) == 22
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_split_helper_manifest_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_fixture(root)
            mutator(root)
            try:
                contract = resolve_contract(root)
                check_helper(root, contract)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: (root / HELPER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing split helper marker",
    )
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                '"parts_glob": "part-*.b64"',
                '"parts_glob": "*.txt"',
                1,
            ),
            encoding="utf-8",
        ),
        '"parts_glob": "part-*.b64"',
    )
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")\n'
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={manifest_path}")',
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={manifest_path}")\n'
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_PART_COUNT={part_count}")',
                1,
            ),
            encoding="utf-8",
        ),
        "split output order",
    )
    expect_failure(
        lambda root: (root / POLICY_PATH).write_text(
            (root / POLICY_PATH).read_text(encoding="utf-8").replace(
                '"archive_target_scope": [\n      "x86_64-linux"\n    ]',
                '"archive_target_scope": [\n      "x86_64-linux",\n      "aarch64-linux"\n    ]',
                1,
            ),
            encoding="utf-8",
        ),
        "expected exactly one archive target",
    )
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                "--parts-dir and --destination are required for reconstruct mode",
                "--partitions-dir and --destination are required for reconstruct mode",
                1,
            ),
            encoding="utf-8",
        ),
        "--parts-dir and --destination are required for reconstruct mode",
    )
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={metadata[\'part_count\']}")',
                'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE_DONE=1")',
                1,
            ),
            encoding="utf-8",
        ),
        "RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT=",
    )

    print("LANE05_SPLIT_HELPER_MANIFEST_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 split pinned-archive helper manifest and reconstruct contract."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for focused no-checkout validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        root = args.write_sample_root.resolve()
        write_fixture(root)
        print(f"LANE05_SPLIT_HELPER_MANIFEST_SAMPLE_ROOT={root}")
        return 0

    try:
        root = args.root.resolve()
        contract = resolve_contract(root)
        helper_marker_count = check_helper(root, contract)
    except ValueError as exc:
        print("LANE05_SPLIT_HELPER_MANIFEST=fail")
        print(f"LANE05_SPLIT_HELPER_MANIFEST_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_HELPER_MANIFEST_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_HELPER_MANIFEST=pass")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_ROOT={root}")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_TARGET={contract['target']}")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_FILENAME={contract['filename']}")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_SHA256={contract['sha256']}")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_SIZE={contract['size']}")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_MARKER_COUNT={helper_marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
