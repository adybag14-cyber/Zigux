#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")

EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}

REQUIRED_SELF_TEST_MARKERS = (
    'with tempfile.TemporaryDirectory(prefix="stage_archive_pass_") as tmp_dir:',
    'metadata, status, actual_sha, destination = stage_archive(root, source, check_only=False)',
    'assert status == "staged"',
    'assert metadata["filename"] == "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"',
    '_, status, actual_sha, destination = stage_archive(root, source, check_only=False)',
    'assert status == "already_present"',
    '_, status, actual_sha, destination = stage_archive(root, source, check_only=True)',
    'assert status == "checked"',
    "def expect_failure(",
    'expected_substring="to be 58159088 bytes, got 1"',
    'expected_substring="to have sha256"',
    'expected_substring="duplicate-suffix archive copies"',
    'expected_substring="destination archive is not a regular file"',
    'expected_substring="duplicate toolchain policy keys"',
    'check_only=False,',
    'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def load_policy(root: Path) -> dict[str, object]:
    policy_path = root / TOOLCHAIN_POLICY_PATH
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing toolchain policy: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")
    return payload


def require_non_empty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {label} in {TOOLCHAIN_POLICY_PATH}")
    return value.strip()


def resolve_contract(root: Path) -> dict[str, object]:
    payload = load_policy(root)
    channel = require_non_empty_string(payload.get("channel"), "channel")
    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise ValueError(f"invalid archive_sha256 in {TOOLCHAIN_POLICY_PATH}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {TOOLCHAIN_POLICY_PATH}")
    archive_targets = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_targets, list) or len(archive_targets) != 1:
        raise ValueError(f"expected exactly one archive target in {TOOLCHAIN_POLICY_PATH}")
    target = archive_targets[0]
    if target not in archive_sha256:
        raise ValueError(f"archive_target_scope target {target} missing from archive_sha256")
    if target not in EXPECTED_ARCHIVE_SIZES:
        raise ValueError(f"missing expected archive size for {target}")
    return {
        "target": target,
        "channel": channel,
        "filename": f"zig-{target}-{channel}.tar.xz",
        "size": EXPECTED_ARCHIVE_SIZES[target],
    }


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 stage-helper selftest checker missing {label}: {marker}")


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 stage-helper selftest checker missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            f"lane05 stage-helper selftest checker expected {label} `{earlier}` before `{later}`"
        )


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"lane05 stage-helper selftest checker expected {expected} occurrences of {label} {marker}, found {actual}"
        )


def check_stage_helper(root: Path) -> tuple[dict[str, object], int]:
    contract = resolve_contract(root)
    helper_text = read_text(root / STAGE_HELPER_PATH)

    for marker in REQUIRED_SELF_TEST_MARKERS:
        require_marker(helper_text, marker, "self-test marker")

    require_marker(
        helper_text,
        f'EXPECTED_ARCHIVE_SIZES = {{\n    "{contract["target"]}": {contract["size"]},',
        "expected archive size contract",
    )
    require_marker(
        helper_text,
        f'assert metadata["filename"] == "{contract["filename"]}"',
        "filename assertion",
    )

    require_exact_count(helper_text, 'assert status == "staged"', 1, "staged assertion")
    require_exact_count(helper_text, 'assert status == "already_present"', 1, "already-present assertion")
    require_exact_count(helper_text, 'assert status == "checked"', 1, "checked assertion")
    require_exact_count(helper_text, "def expect_failure(", 1, "failure helper definition")
    require_exact_count(helper_text, 'expected_substring="to have sha256"', 2, "sha mismatch failure assertions")
    require_exact_count(helper_text, 'check_only=False,', 1, "write-path failure toggle")

    require_order(
        helper_text,
        'assert status == "staged"',
        'assert status == "already_present"',
        "success status assertions",
    )
    require_order(
        helper_text,
        'assert status == "already_present"',
        'assert status == "checked"',
        "success status assertions",
    )
    require_order(
        helper_text,
        'expected_substring="to be 58159088 bytes, got 1"',
        'expected_substring="to have sha256"',
        "failure coverage order",
    )
    require_order(
        helper_text,
        'expected_substring="duplicate-suffix archive copies"',
        'expected_substring="destination archive is not a regular file"',
        "failure coverage order",
    )
    require_order(
        helper_text,
        'expected_substring="destination archive is not a regular file"',
        'expected_substring="duplicate toolchain policy keys"',
        "failure coverage order",
    )
    require_order(
        helper_text,
        'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
        'print(f"STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")',
        "self-test output order",
    )

    return contract, len(REQUIRED_SELF_TEST_MARKERS)


def write_fixture(root: Path, *, with_current_contract: bool = True) -> None:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
    if with_current_contract:
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
                        "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    else:
        (root / TOOLCHAIN_POLICY_PATH).write_text("{}", encoding="utf-8")

    (root / STAGE_HELPER_PATH).write_text(
        "\n".join(
            [
                "import json",
                "import tempfile",
                'EXPECTED_ARCHIVE_SIZES = {',
                '    "x86_64-linux": 58159088,',
                '}',
                'def run_self_test() -> int:',
                '    case_count = 0',
                '    with tempfile.TemporaryDirectory(prefix="stage_archive_pass_") as tmp_dir:',
                '        metadata, status, actual_sha, destination = stage_archive(root, source, check_only=False)',
                '        assert status == "staged"',
                '        assert metadata["filename"] == "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"',
                '        _, status, actual_sha, destination = stage_archive(root, source, check_only=False)',
                '        assert status == "already_present"',
                '        _, status, actual_sha, destination = stage_archive(root, source, check_only=True)',
                '        assert status == "checked"',
                '    def expect_failure(',
                '        *,',
                '        expected_substring: str,',
                '        check_only: bool = True,',
                '    ) -> None:',
                '        pass',
                '    expect_failure(expected_substring="to be 58159088 bytes, got 1")',
                '    expect_failure(expected_substring="to have sha256")',
                '    expect_failure(expected_substring="duplicate-suffix archive copies")',
                '    expect_failure(expected_substring="destination archive is not a regular file")',
                '    expect_failure(expected_substring="to have sha256", check_only=False,)',
                '    expect_failure(expected_substring="duplicate toolchain policy keys")',
                '    print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
                '    print(f"STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")',
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_selftest_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        contract, marker_count = check_stage_helper(root)
        assert contract["filename"] == "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
        assert marker_count == len(REQUIRED_SELF_TEST_MARKERS)
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_selftest_alignment_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_fixture(root)
            mutator(root)
            try:
                check_stage_helper(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing self-test marker",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace(
                'assert status == "already_present"',
                'assert status == "present"',
            ),
            encoding="utf-8",
        ),
        'assert status == "already_present"',
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace(
                'expected_substring="duplicate toolchain policy keys"',
                'expected_substring="missing toolchain policy"',
            ),
            encoding="utf-8",
        ),
        "duplicate toolchain policy keys",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            (root / STAGE_HELPER_PATH).read_text(encoding="utf-8").replace(
                'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")\n'
                '    print(f"STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")',
                'print(f"STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}")\n'
                '    print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
            ),
            encoding="utf-8",
        ),
        "self-test output order",
    )
    expect_failure(
        lambda root: (root / TOOLCHAIN_POLICY_PATH).write_text(
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
                        "archive_target_scope": ["x86_64-linux", "aarch64-linux"],
                        "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        ),
        "expected exactly one archive target",
    )

    print("LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 staged pinned-archive helper keeps its self-test packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        root = args.root.resolve()
        contract, marker_count = check_stage_helper(root)
    except ValueError as exc:
        print("LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT=fail")
        print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_ROOT={args.root.resolve()}")
        print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_NOTE={exc}")
        return 1

    print("LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT=pass")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_ROOT={root}")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_TARGET={contract['target']}")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_FILENAME={contract['filename']}")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_SIZE={contract['size']}")
    print(f"LANE05_STAGE_HELPER_SELFTEST_ALIGNMENT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
