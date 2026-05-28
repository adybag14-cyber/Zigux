#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SPLIT_HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")
TOOLCHAIN_POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}

HELPER_MARKERS = (
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    "DEFAULT_CHUNK_BYTES = 786_429",
    "MAX_SHARD_TEXT_BYTES = 1_048_576",
    '    "x86_64-linux": 58_159_088,',
    'assert ((4 * math.ceil(DEFAULT_CHUNK_BYTES / 3)) + 1) <= MAX_SHARD_TEXT_BYTES',
    'with tempfile.TemporaryDirectory(prefix="split_archive_pass_") as tmp_dir:',
    'assert part_count == math.ceil(len(payload) / 1024)',
    'assert (root / "rebuilt.tar.xz").read_bytes() == payload',
    "expect_split_failure(",
    '"output directory must be empty"',
    '"chunk_bytes must be positive"',
    '"chunk_bytes 786432 would emit base64 shard text larger than 1048576 bytes"',
    '"missing expected shard"',
    '"expected sha mismatch failure"',
    '"expected invalid base64 failure"',
    '(output_dir / "part-000.b64").write_text("not base64!\\n", encoding="utf-8")',
    'print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")',
)

EXACT_ONCE_MARKERS = (
    'print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")',
    'with tempfile.TemporaryDirectory(prefix="split_archive_pass_") as tmp_dir:',
)

ORDERED_MARKERS = (
    ('"chunk_bytes must be positive"', '"chunk_bytes 786432 would emit base64 shard text larger than 1048576 bytes"'),
    ('"chunk_bytes 786432 would emit base64 shard text larger than 1048576 bytes"', '"missing expected shard"'),
    ('"missing expected shard"', '"expected invalid base64 failure"'),
    ('"expected invalid base64 failure"', '"expected sha mismatch failure"'),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def require_non_empty_string(value: object, field_name: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {field_name} in {path}")
    return value.strip()


def require_string_list(value: object, field_name: str, path: Path) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"invalid {field_name} in {path}")
    items: list[str] = []
    seen: set[str] = set()
    for entry in value:
        normalized = require_non_empty_string(entry, field_name, path)
        if normalized in seen:
            raise ValueError(f"duplicate {field_name} entry in {path}: {normalized}")
        items.append(normalized)
        seen.add(normalized)
    return items


def load_contract(root: Path) -> dict[str, object]:
    policy_path = root / TOOLCHAIN_POLICY_PATH
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing toolchain policy: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")

    channel = require_non_empty_string(payload.get("channel"), "channel", policy_path)
    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise ValueError(f"invalid archive_sha256 in {policy_path}")

    normalized_archives: dict[str, str] = {}
    for target, digest in archive_sha256.items():
        normalized_target = require_non_empty_string(target, "archive_sha256 target", policy_path)
        normalized_digest = require_non_empty_string(
            digest, f"archive_sha256[{normalized_target}]", policy_path
        )
        normalized_archives[normalized_target] = normalized_digest

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")
    archive_targets = require_string_list(
        upgrade_policy.get("archive_target_scope"),
        "archive_target_scope",
        policy_path,
    )
    if len(archive_targets) != 1:
        raise ValueError(f"expected exactly one archive target in {policy_path}, got {len(archive_targets)}")
    target = archive_targets[0]
    if target not in normalized_archives:
        raise ValueError(
            f"archive_target_scope references missing archive_sha256 entry in {policy_path}: {target}"
        )
    if target not in EXPECTED_ARCHIVE_SIZES:
        raise ValueError(f"missing expected archive size for {target}")

    return {
        "target": target,
        "channel": channel,
        "sha256": normalized_archives[target],
        "size": EXPECTED_ARCHIVE_SIZES[target],
        "filename": f"zig-{target}-{channel}.tar.xz",
    }


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 split-helper selftest checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"lane05 split-helper selftest checker expected exactly {expected} occurrences of {label} `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 split-helper selftest checker missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            f"lane05 split-helper selftest checker expected {label} `{earlier}` before `{later}`"
        )


def check_helper(root: Path, contract: dict[str, object]) -> int:
    helper_text = read_text(root / SPLIT_HELPER_PATH)

    for marker in HELPER_MARKERS:
        require_marker(helper_text, marker, "helper marker")
    for marker in EXACT_ONCE_MARKERS:
        require_exact_count(helper_text, marker, 1, "helper marker")
    for earlier, later in ORDERED_MARKERS:
        require_order(helper_text, earlier, later, "self-test case order")

    require_marker(helper_text, f'"{contract["target"]}": {contract["size"]:_},', "target-size marker")
    require_marker(
        helper_text,
        'write_policy(root, expected_sha, len(payload))',
        "policy-backed size fixture",
    )
    return len(HELPER_MARKERS) + 2


def write_sample_root(root: Path) -> None:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / TOOLCHAIN_POLICY_PATH).write_text(
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
    (root / SPLIT_HELPER_PATH).write_text(
        "\n".join(
            (
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                "DEFAULT_CHUNK_BYTES = 786_429",
                "MAX_SHARD_TEXT_BYTES = 1_048_576",
                "EXPECTED_ARCHIVE_SIZES = {",
                '    "x86_64-linux": 58_159_088,',
                "}",
                "",
                "def run_self_test() -> int:",
                "    assert ((4 * math.ceil(DEFAULT_CHUNK_BYTES / 3)) + 1) <= MAX_SHARD_TEXT_BYTES",
                '    with tempfile.TemporaryDirectory(prefix="split_archive_pass_") as tmp_dir:',
                '        write_policy(root, expected_sha, len(payload))',
                "        assert part_count == math.ceil(len(payload) / 1024)",
                '        assert (root / "rebuilt.tar.xz").read_bytes() == payload',
                "",
                "    expect_split_failure(",
                '        lambda root, source, output_dir, metadata: output_dir.mkdir(parents=True, exist_ok=True),',
                '        "output directory must be empty",',
                "    )",
                "    expect_split_failure(",
                '        lambda root, source, output_dir, metadata: None,',
                '        "chunk_bytes must be positive",',
                "    )",
                "    expect_split_failure(",
                '        lambda root, source, output_dir, metadata: None,',
                '        "chunk_bytes 786432 would emit base64 shard text larger than 1048576 bytes",',
                "    )",
                "    expect_split_failure(",
                '        lambda root, source, output_dir, metadata: None,',
                '        "missing expected shard",',
                "    )",
                '(output_dir / "part-000.b64").write_text("not base64!\\n", encoding="utf-8")',
                '    raise AssertionError("expected invalid base64 failure")',
                '    raise AssertionError("expected sha mismatch failure")',
                '    print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
                '    print(f"SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        contract = load_contract(root)
        assert check_helper(root, contract) == len(HELPER_MARKERS) + 2
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_split_helper_selftest_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                contract = load_contract(root)
                check_helper(root, contract)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing helper marker",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                'print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                '"chunk_bytes must be positive"',
                '"different failure"',
                1,
            ),
            encoding="utf-8",
        ),
        "chunk_bytes must be positive",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                'print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
                'print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")\n'
                '    print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
                1,
            ),
            encoding="utf-8",
        ),
        "exactly 1 occurrences",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                'assert (root / "rebuilt.tar.xz").read_bytes() == payload\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        'assert (root / "rebuilt.tar.xz").read_bytes() == payload',
    )
    expect_failure(
        lambda root: (root / TOOLCHAIN_POLICY_PATH).write_text(
            (root / TOOLCHAIN_POLICY_PATH).read_text(encoding="utf-8").replace(
                '"archive_target_scope": [\n      "x86_64-linux"\n    ]',
                '"archive_target_scope": [\n      "x86_64-linux",\n      "aarch64-linux"\n    ]',
                1,
            ),
            encoding="utf-8",
        ),
        "expected exactly one archive target",
    )

    print("LANE05_SPLIT_HELPER_SELFTEST_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split helper keeps its self-test coverage explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a compact sample root that should satisfy this checker and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    try:
        root = args.root.resolve()
        contract = load_contract(root)
        marker_count = check_helper(root, contract)
    except ValueError as exc:
        print("LANE05_SPLIT_HELPER_SELFTEST=fail")
        print(f"LANE05_SPLIT_HELPER_SELFTEST_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_HELPER_SELFTEST_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_HELPER_SELFTEST=pass")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_ROOT={root}")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_TARGET={contract['target']}")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_FILENAME={contract['filename']}")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_SHA256={contract['sha256']}")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_SIZE={contract['size']}")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())