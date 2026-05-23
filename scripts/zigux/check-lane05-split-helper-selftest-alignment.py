#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SPLIT_HELPER = Path("scripts/zigux/split-pinned-zig-archive.py")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}

SELFTEST_MARKERS = (
    'def run_self_test() -> int:',
    'payload = (b"lane05-archive-payload-" * 64)[:4097]',
    "part_count == math.ceil(len(payload) / 1024)",
    "manifest_path.exists()",
    'rebuilt = reconstruct_archive(output_dir, root / "rebuilt.tar.xz")',
    'assert (root / "rebuilt.tar.xz").read_bytes() == payload',
    'assert rebuilt["sha256"] == expected_sha',
    "output directory must be empty",
    "expected non-positive chunk_bytes failure",
    "expected missing shard failure",
    "expected invalid base64 failure",
    'manifest["sha256"] = "0" * 64',
    "expected reconstructed archive to have sha256",
    "expected sha mismatch failure",
    "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
    "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=",
)

EXACT_ONCE_MARKERS = (
    'def run_self_test() -> int:',
    'manifest["sha256"] = "0" * 64',
    "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
)

ORDERED_MARKERS = (
    ('payload = (b"lane05-archive-payload-" * 64)[:4097]', "manifest_path.exists()"),
    ("manifest_path.exists()", 'rebuilt = reconstruct_archive(output_dir, root / "rebuilt.tar.xz")'),
    ('rebuilt = reconstruct_archive(output_dir, root / "rebuilt.tar.xz")', 'assert (root / "rebuilt.tar.xz").read_bytes() == payload'),
    ('assert (root / "rebuilt.tar.xz").read_bytes() == payload', 'assert rebuilt["sha256"] == expected_sha'),
    ("output directory must be empty", "expected non-positive chunk_bytes failure"),
    ("expected non-positive chunk_bytes failure", "expected missing shard failure"),
    ("expected missing shard failure", "expected invalid base64 failure"),
    ("expected invalid base64 failure", 'manifest["sha256"] = "0" * 64'),
    ('manifest["sha256"] = "0" * 64', "expected sha mismatch failure"),
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
    policy_path = root / TOOLCHAIN_POLICY
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
        raise ValueError(f"lane05 split-helper selftest alignment missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"lane05 split-helper selftest alignment expected exactly {expected} occurrences of {label} `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 split-helper selftest alignment missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            f"lane05 split-helper selftest alignment expected {label} `{earlier}` before `{later}`"
        )


def check_helper(root: Path, contract: dict[str, object]) -> int:
    helper_text = read_text(root / SPLIT_HELPER)

    for marker in SELFTEST_MARKERS:
        require_marker(helper_text, marker, "self-test marker")
    for marker in EXACT_ONCE_MARKERS:
        require_exact_count(helper_text, marker, 1, "self-test marker")

    require_marker(helper_text, f'"{contract["target"]}": {contract["size"]:_},', "target-size marker")
    require_marker(
        helper_text,
        '"filename": f"zig-{target}-{channel}.tar.xz"',
        "filename contract marker",
    )

    for earlier, later in ORDERED_MARKERS:
        require_order(helper_text, earlier, later, "self-test flow")

    return len(SELFTEST_MARKERS) + 2


def write_fixture(root: Path) -> None:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / TOOLCHAIN_POLICY).write_text(
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
    (root / SPLIT_HELPER).write_text(
        "\n".join(
            (
                "import math",
                "",
                "DEFAULT_CHUNK_BYTES = 786_432",
                "EXPECTED_ARCHIVE_SIZES = {",
                '    "x86_64-linux": 58_159_088,',
                "}",
                'metadata = {"filename": f"zig-{target}-{channel}.tar.xz"}',
                "",
                "def run_self_test() -> int:",
                '    payload = (b"lane05-archive-payload-" * 64)[:4097]',
                "    assert part_count == math.ceil(len(payload) / 1024)",
                "    assert manifest_path.exists()",
                '    rebuilt = reconstruct_archive(output_dir, root / "rebuilt.tar.xz")',
                '    assert (root / "rebuilt.tar.xz").read_bytes() == payload',
                '    assert rebuilt["sha256"] == expected_sha',
                '    raise ValueError("output directory must be empty")',
                '    raise AssertionError("expected non-positive chunk_bytes failure")',
                '    raise AssertionError("expected missing shard failure")',
                '    raise AssertionError("expected invalid base64 failure")',
                '    manifest["sha256"] = "0" * 64',
                '    assert "expected reconstructed archive to have sha256" in str(exc), str(exc)',
                '    raise AssertionError("expected sha mismatch failure")',
                '    print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
                '    print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=7")',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_selftest_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        contract = load_contract(root)
        assert check_helper(root, contract) == len(SELFTEST_MARKERS) + 2
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_split_helper_selftest_alignment_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_fixture(root)
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
        lambda root: (root / SPLIT_HELPER).write_text("missing\n", encoding="utf-8"),
        "missing self-test marker",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER).write_text(
            (root / SPLIT_HELPER).read_text(encoding="utf-8").replace(
                'manifest["sha256"] = "0" * 64\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        'manifest["sha256"] = "0" * 64',
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER).write_text(
            (root / SPLIT_HELPER).read_text(encoding="utf-8").replace(
                'print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")\n',
                'print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")\nprint("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")\n',
                1,
            ),
            encoding="utf-8",
        ),
        "exactly 1 occurrences",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER).write_text(
            (root / SPLIT_HELPER).read_text(encoding="utf-8").replace(
                '    assert (root / "rebuilt.tar.xz").read_bytes() == payload\n    assert rebuilt["sha256"] == expected_sha\n',
                '    assert rebuilt["sha256"] == expected_sha\n    assert (root / "rebuilt.tar.xz").read_bytes() == payload\n',
                1,
            ),
            encoding="utf-8",
        ),
        "self-test flow",
    )
    expect_failure(
        lambda root: (root / TOOLCHAIN_POLICY).write_text(
            (root / TOOLCHAIN_POLICY).read_text(encoding="utf-8").replace(
                '"archive_target_scope": [\n      "x86_64-linux"\n    ]',
                '"archive_target_scope": [\n      "x86_64-linux",\n      "aarch64-linux"\n    ]',
            ),
            encoding="utf-8",
        ),
        "expected exactly one archive target",
    )
    expect_failure(
        lambda root: (root / TOOLCHAIN_POLICY).write_text(
            (root / TOOLCHAIN_POLICY).read_text(encoding="utf-8").replace(
                "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "archive_sha256[x86_64-linux]",
    )

    print("LANE05_SPLIT_HELPER_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 split helper self-test packet against the pinned policy."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        root = args.root.resolve()
        contract = load_contract(root)
        marker_count = check_helper(root, contract)
    except ValueError as exc:
        print("LANE05_SPLIT_HELPER_SELFTEST_ALIGNMENT=fail")
        print(f"LANE05_SPLIT_HELPER_SELFTEST_ALIGNMENT_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_HELPER_SELFTEST_ALIGNMENT_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_HELPER_SELFTEST_ALIGNMENT=pass")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_ALIGNMENT_ROOT={root}")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_ALIGNMENT_TARGET={contract['target']}")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_ALIGNMENT_FILENAME={contract['filename']}")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_ALIGNMENT_SHA256={contract['sha256']}")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_ALIGNMENT_SIZE={contract['size']}")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_ALIGNMENT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
