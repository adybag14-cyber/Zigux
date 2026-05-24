#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
STAGE_HELPER = Path("scripts/zigux/stage-pinned-zig-archive.py")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")

EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}

REQUIRED_MARKERS = (
    'EXPECTED_ARCHIVE_SIZES = {',
    '    "x86_64-linux": 58_159_088,',
    'with tempfile.TemporaryDirectory(prefix="stage_archive_pass_") as tmp_dir:',
    'assert status == "staged"',
    'assert status == "already_present"',
    'assert status == "checked"',
    'with tempfile.TemporaryDirectory(prefix="stage_archive_parts_pass_") as tmp_dir:',
    'write_parts_fixture(',
    'parts_dir = root / "parts"',
    'parts_dir=parts_dir,',
    'assert input_mode == "parts_dir"',
    'use_parts_dir: bool = False,',
    'expected_substring="missing shard manifest"',
    'expected_substring="expected shard manifest filename"',
    'expected_substring="missing expected shard"',
    'expected_substring="invalid base64 shard"',
    '"--parts-dir",',
    'help="Directory containing manifest.json plus part-XXX.b64 shard files."',
    'exactly one of --source or --parts-dir is required unless --self-test is used',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
    'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")',
)

EXACT_ONCE_MARKERS = (
    'with tempfile.TemporaryDirectory(prefix="stage_archive_parts_pass_") as tmp_dir:',
    'assert input_mode == "parts_dir"',
    'expected_substring="missing shard manifest"',
    'expected_substring="expected shard manifest filename"',
    'expected_substring="missing expected shard"',
    'expected_substring="invalid base64 shard"',
    '"--parts-dir",',
    'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
)

ORDERED_MARKERS = (
    (
        'with tempfile.TemporaryDirectory(prefix="stage_archive_pass_") as tmp_dir:',
        'with tempfile.TemporaryDirectory(prefix="stage_archive_parts_pass_") as tmp_dir:',
    ),
    (
        'with tempfile.TemporaryDirectory(prefix="stage_archive_parts_pass_") as tmp_dir:',
        'expected_substring="missing shard manifest"',
    ),
    (
        'parts_dir=parts_dir,',
        'assert input_mode == "parts_dir"',
    ),
    (
        'expected_substring="missing shard manifest"',
        'expected_substring="expected shard manifest filename"',
    ),
    (
        'expected_substring="expected shard manifest filename"',
        'expected_substring="missing expected shard"',
    ),
    (
        'expected_substring="missing expected shard"',
        'expected_substring="invalid base64 shard"',
    ),
    (
        'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
        'print(f"STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")',
    ),
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
        raise ValueError(f"lane05 stage-helper selftest alignment missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"lane05 stage-helper selftest alignment expected exactly {expected} occurrences of {label} `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 stage-helper selftest alignment missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            f"lane05 stage-helper selftest alignment expected {label} `{earlier}` before `{later}`"
        )


def check_helper(root: Path, contract: dict[str, object]) -> int:
    helper_text = read_text(root / STAGE_HELPER)

    for marker in REQUIRED_MARKERS:
        require_marker(helper_text, marker, "self-test marker")
    for marker in EXACT_ONCE_MARKERS:
        require_exact_count(helper_text, marker, 1, "self-test marker")

    require_marker(
        helper_text,
        f'assert metadata["filename"] == "{contract["filename"]}"',
        "filename assertion",
    )

    for earlier, later in ORDERED_MARKERS:
        require_order(helper_text, earlier, later, "self-test flow")

    return len(REQUIRED_MARKERS) + 1


def write_sample_root(root: Path) -> None:
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
                    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    (root / STAGE_HELPER).write_text(
        "\n".join(
            (
                "import tempfile",
                "",
                "EXPECTED_ARCHIVE_SIZES = {",
                '    "x86_64-linux": 58_159_088,',
                "}",
                "",
                "def run_self_test() -> int:",
                '    with tempfile.TemporaryDirectory(prefix="stage_archive_pass_") as tmp_dir:',
                '        assert status == "staged"',
                '        assert metadata["filename"] == "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"',
                '        assert status == "already_present"',
                '        assert status == "checked"',
                '    with tempfile.TemporaryDirectory(prefix="stage_archive_parts_pass_") as tmp_dir:',
                '        parts_dir = root / "parts"',
                '        write_parts_fixture(',
                '            parts_dir,',
                '            source.read_bytes(),',
                '            filename=str(metadata["filename"]),',
                '            sha256=str(metadata["sha256"]),',
                '            chunk_bytes=786432,',
                "        )",
                "        stage_archive(",
                "            root,",
                "            None,",
                "            parts_dir=parts_dir,",
                "            check_only=False,",
                "        )",
                '        assert input_mode == "parts_dir"',
                "",
                "def expect_failure(",
                "    *,",
                "    use_parts_dir: bool = False,",
                "):",
                '    pass  # use_parts_dir: bool = False,',
                '    expect_failure(expected_substring="missing shard manifest", use_parts_dir=True)',
                '    expect_failure(expected_substring="expected shard manifest filename", use_parts_dir=True)',
                '    expect_failure(expected_substring="missing expected shard", use_parts_dir=True)',
                '    expect_failure(expected_substring="invalid base64 shard", use_parts_dir=True)',
                "",
                'parser.add_argument("--parts-dir", help="Directory containing manifest.json plus part-XXX.b64 shard files.")',
                'raise SystemExit("exactly one of --source or --parts-dir is required unless --self-test is used")',
                'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
                'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
                'print(f"STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_selftest_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        contract = load_contract(root)
        assert check_helper(root, contract) == len(REQUIRED_MARKERS) + 1
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_selftest_alignment_fail_") as tmp_dir:
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
        lambda root: (root / STAGE_HELPER).write_text("missing\n", encoding="utf-8"),
        "missing self-test marker",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER).write_text(
            (root / STAGE_HELPER).read_text(encoding="utf-8").replace(
                'expected_substring="missing expected shard"',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        'expected_substring="missing expected shard"',
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER).write_text(
            (root / STAGE_HELPER).read_text(encoding="utf-8").replace(
                'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")\n',
                'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")\nprint("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")\n',
                1,
            ),
            encoding="utf-8",
        ),
        "exactly 1 occurrences",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER).write_text(
            (root / STAGE_HELPER).read_text(encoding="utf-8").replace(
                '    expect_failure(expected_substring="missing shard manifest", use_parts_dir=True)\n'
                '    expect_failure(expected_substring="expected shard manifest filename", use_parts_dir=True)\n',
                '    expect_failure(expected_substring="expected shard manifest filename", use_parts_dir=True)\n'
                '    expect_failure(expected_substring="missing shard manifest", use_parts_dir=True)\n',
                1,
            ),
            encoding="utf-8",
        ),
        "self-test flow",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER).write_text(
            (root / STAGE_HELPER).read_text(encoding="utf-8").replace(
                'assert input_mode == "parts_dir"',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        'assert input_mode == "parts_dir"',
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER).write_text(
            (root / STAGE_HELPER).read_text(encoding="utf-8").replace(
                '    expect_failure(expected_substring="invalid base64 shard", use_parts_dir=True)\n',
                '    expect_failure(expected_substring="invalid base64 shard", use_parts_dir=True)\n'
                '    expect_failure(expected_substring="invalid base64 shard", use_parts_dir=True)\n',
                1,
            ),
            encoding="utf-8",
        ),
        "exactly 1 occurrences",
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

    print("LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 staged pinned-archive helper self-test packet against the pinned shard path."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Optional output root for a minimal passing sample packet",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
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
        print("LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT=fail")
        print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_ROOT={args.root.resolve()}")
        print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_NOTE={exc}")
        return 1

    print("LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT=pass")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_ROOT={root}")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_TARGET={contract['target']}")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_FILENAME={contract['filename']}")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_SHA256={contract['sha256']}")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_SIZE={contract['size']}")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
