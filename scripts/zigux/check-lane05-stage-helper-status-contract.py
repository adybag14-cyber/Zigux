#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
EXPECTED_TARGET = "x86_64-linux"
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_FILENAME = f"zig-{EXPECTED_TARGET}-{EXPECTED_CHANNEL}.tar.xz"
EXPECTED_SIZE = 58_159_088
EXPECTED_SHA256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"

REQUIRED_HELPER_MARKERS = (
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    'THIRD_PARTY_DIR = Path("third_party")',
    '"x86_64-linux": 58_159_088',
    'ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(r"^(?P<stem>.+)',
    "def stage_archive(root: Path, source: Path, *, check_only: bool)",
    'return metadata, "checked", existing_destination[1] if existing_destination else actual_sha, destination',
    'return metadata, existing_destination[0], existing_destination[1], destination',
    'return metadata, "staged", staged_sha, destination',
    'parser.add_argument("--source", type=Path, help="Path to the candidate Zig archive payload.")',
    '"--check-only"',
    '"--self-test"',
    'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
    'print("STAGE_PINNED_ZIG_ARCHIVE=fail")',
    'print("STAGE_PINNED_ZIG_ARCHIVE=pass")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_ROOT={root}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_SOURCE={source}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_TARGET={metadata[\'target\']}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE={metadata[\'size\']}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={metadata[\'sha256\']}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256={actual_sha}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_NOTE={exc}")',
)

ORDERED_MARKERS = (
    'print("STAGE_PINNED_ZIG_ARCHIVE=pass")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_ROOT={root}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_SOURCE={source}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_TARGET={metadata[\'target\']}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE={metadata[\'size\']}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={metadata[\'sha256\']}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256={actual_sha}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}")',
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 stage-helper status contract missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"lane05 stage-helper status contract expected exactly {expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 stage-helper status contract missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            f"lane05 stage-helper status contract expected {label} `{earlier}` before `{later}`"
        )


def load_policy(root: Path) -> dict[str, object]:
    policy_path = root / POLICY_PATH
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing policy file: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid policy JSON in {policy_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid policy payload in {policy_path}: expected object")
    return payload


def validate_helper(root: Path) -> tuple[int, int]:
    helper_path = root / HELPER_PATH
    try:
        helper_text = helper_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing stage helper: {helper_path}") from exc

    policy = load_policy(root)
    archive_sha = policy.get("archive_sha256")
    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(archive_sha, dict) or archive_sha.get(EXPECTED_TARGET) != EXPECTED_SHA256:
        raise ValueError(f"policy archive_sha256 for {EXPECTED_TARGET} drifted from the pinned Lane 05 contract")
    if policy.get("channel") != EXPECTED_CHANNEL:
        raise ValueError("policy channel drifted from the pinned Lane 05 contract")
    if policy.get("minimum_version") != EXPECTED_CHANNEL:
        raise ValueError("policy minimum_version drifted from the pinned Lane 05 contract")
    if not isinstance(upgrade_policy, dict):
        raise ValueError("policy upgrade_policy is missing")
    if upgrade_policy.get("archive_target_scope") != [EXPECTED_TARGET]:
        raise ValueError("policy archive_target_scope drifted from the pinned Lane 05 contract")

    for marker in REQUIRED_HELPER_MARKERS:
        require_marker(helper_text, marker, "helper marker")

    require_exact_count(
        helper_text,
        'print("STAGE_PINNED_ZIG_ARCHIVE=pass")',
        1,
        "success status print",
    )
    require_exact_count(
        helper_text,
        'print("STAGE_PINNED_ZIG_ARCHIVE=fail")',
        1,
        "failure status print",
    )
    require_exact_count(
        helper_text,
        'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
        1,
        "self-test status print",
    )
    require_exact_count(
        helper_text,
        'return metadata, "checked", existing_destination[1] if existing_destination else actual_sha, destination',
        1,
        "check-only status return",
    )
    require_exact_count(
        helper_text,
        'return metadata, existing_destination[0], existing_destination[1], destination',
        1,
        "already-present status return",
    )
    require_exact_count(
        helper_text,
        'return metadata, "staged", staged_sha, destination',
        1,
        "staged status return",
    )
    require_exact_count(
        helper_text,
        'THIRD_PARTY_DIR = Path("third_party")',
        1,
        "third-party destination marker",
    )
    require_exact_count(
        helper_text,
        '"x86_64-linux": 58_159_088',
        1,
        "expected-size marker",
    )

    for earlier, later in zip(ORDERED_MARKERS, ORDERED_MARKERS[1:]):
        require_order(helper_text, earlier, later, "success output order")

    require_order(
        helper_text,
        'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
        'THIRD_PARTY_DIR = Path("third_party")',
        "helper constant order",
    )
    require_order(
        helper_text,
        "def stage_archive(root: Path, source: Path, *, check_only: bool)",
        'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
        "stage helper before self-test status",
    )
    require_order(
        helper_text,
        'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
        'print("STAGE_PINNED_ZIG_ARCHIVE=fail")',
        "self-test output before runtime output",
    )
    require_order(
        helper_text,
        'print("STAGE_PINNED_ZIG_ARCHIVE=fail")',
        'print("STAGE_PINNED_ZIG_ARCHIVE=pass")',
        "failure output before success output",
    )

    return len(REQUIRED_HELPER_MARKERS), len(ORDERED_MARKERS)


def write_sample_root(root: Path) -> Path:
    helper_dir = root / "scripts" / "zigux"
    helper_dir.mkdir(parents=True, exist_ok=True)
    (root / "third_party").mkdir(parents=True, exist_ok=True)

    helper_text = """#!/usr/bin/env python3
from pathlib import Path
import argparse
import re

TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")
THIRD_PARTY_DIR = Path(\"third_party\")
EXPECTED_ARCHIVE_SIZES = {
    \"x86_64-linux\": 58_159_088,
}
ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(r\"^(?P<stem>.+) \\((?P<copy>\\d+)\\)(?P<suffix>\\.tar\\.xz)$\")

def stage_archive(root: Path, source: Path, *, check_only: bool):
    if check_only:
        return metadata, \"checked\", existing_destination[1] if existing_destination else actual_sha, destination
    if existing_destination is not None:
        return metadata, existing_destination[0], existing_destination[1], destination
    return metadata, \"staged\", staged_sha, destination

def run_self_test():
    print(\"STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass\")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(\"--source\", type=Path, help=\"Path to the candidate Zig archive payload.\")
    parser.add_argument(\"--root\", type=Path, default=Path.cwd())
    parser.add_argument(
        \"--check-only\",
        action=\"store_true\",
    )
    parser.add_argument(
        \"--self-test\",
        action=\"store_true\",
    )
    if args.self_test:
        return run_self_test()
    print(\"STAGE_PINNED_ZIG_ARCHIVE=fail\")
    print(f\"STAGE_PINNED_ZIG_ARCHIVE_NOTE={exc}\")
    print(\"STAGE_PINNED_ZIG_ARCHIVE=pass\")
    print(f\"STAGE_PINNED_ZIG_ARCHIVE_ROOT={root}\")
    print(f\"STAGE_PINNED_ZIG_ARCHIVE_SOURCE={source}\")
    print(f\"STAGE_PINNED_ZIG_ARCHIVE_TARGET={metadata['target']}\")
    print(f\"STAGE_PINNED_ZIG_ARCHIVE_FILENAME={metadata['filename']}\")
    print(f\"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE={metadata['size']}\")
    print(f\"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={metadata['sha256']}\")
    print(f\"STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256={actual_sha}\")
    print(f\"STAGE_PINNED_ZIG_ARCHIVE_DESTINATION={destination}\")
    print(f\"STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}\")
"""
    (helper_dir / "stage-pinned-zig-archive.py").write_text(helper_text, encoding="utf-8")

    policy = {
        "phase": "Phase 2",
        "channel": EXPECTED_CHANNEL,
        "minimum_version": EXPECTED_CHANNEL,
        "archive_sha256": {EXPECTED_TARGET: EXPECTED_SHA256},
        "upgrade_policy": {
            "channel_minimum_lockstep": True,
            "archive_target_scope": [EXPECTED_TARGET],
            "required_make_routes": ["phase2-toolchain", "phase2-validate"],
        },
    }
    (helper_dir / "zig-toolchain-policy.json").write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    return root


def run_self_test() -> int:
    case_count = 0

    def expect_pass() -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_status_pass_") as tmp_dir:
            root = write_sample_root(Path(tmp_dir))
            assert validate_helper(root) == (len(REQUIRED_HELPER_MARKERS), len(ORDERED_MARKERS))
            case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_status_fail_") as tmp_dir:
            root = write_sample_root(Path(tmp_dir))
            mutator(root)
            try:
                validate_helper(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected validate_helper to fail")

    expect_pass()
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                '    parser.add_argument(\n        "--check-only",\n        action="store_true",\n    )\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "--check-only",
    )
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                'print(f"STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "STAGE_PINNED_ZIG_ARCHIVE_STATUS",
    )
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                'THIRD_PARTY_DIR = Path("third_party")',
                'THIRD_PARTY_DIR = Path("payloads")',
                1,
            ),
            encoding="utf-8",
        ),
        'THIRD_PARTY_DIR = Path("third_party")',
    )
    expect_failure(
        lambda root: (root / POLICY_PATH).write_text(
            json.dumps(
                {
                    "phase": "Phase 2",
                    "channel": EXPECTED_CHANNEL,
                    "minimum_version": EXPECTED_CHANNEL,
                    "archive_sha256": {EXPECTED_TARGET: EXPECTED_SHA256},
                    "upgrade_policy": {
                        "channel_minimum_lockstep": True,
                        "archive_target_scope": ["aarch64-linux"],
                        "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        ),
        "archive_target_scope drifted",
    )
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                'print("STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
    )

    print("LANE05_STAGE_HELPER_STATUS_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_STATUS_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 pinned-archive staging helper emitted-status contract."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for local checker replay.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker coverage.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"LANE05_STAGE_HELPER_STATUS_CONTRACT_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    try:
        marker_count, output_field_count = validate_helper(args.root.resolve())
    except ValueError as exc:
        print("LANE05_STAGE_HELPER_STATUS_CONTRACT=fail")
        print(f"LANE05_STAGE_HELPER_STATUS_CONTRACT_ROOT={args.root.resolve()}")
        print(f"LANE05_STAGE_HELPER_STATUS_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_STAGE_HELPER_STATUS_CONTRACT=pass")
    print(f"LANE05_STAGE_HELPER_STATUS_CONTRACT_ROOT={args.root.resolve()}")
    print(f"LANE05_STAGE_HELPER_STATUS_CONTRACT_TARGET={EXPECTED_TARGET}")
    print(f"LANE05_STAGE_HELPER_STATUS_CONTRACT_CHANNEL={EXPECTED_CHANNEL}")
    print(f"LANE05_STAGE_HELPER_STATUS_CONTRACT_FILENAME={EXPECTED_FILENAME}")
    print(f"LANE05_STAGE_HELPER_STATUS_CONTRACT_EXPECTED_SIZE={EXPECTED_SIZE}")
    print(f"LANE05_STAGE_HELPER_STATUS_CONTRACT_EXPECTED_SHA256={EXPECTED_SHA256}")
    print(f"LANE05_STAGE_HELPER_STATUS_CONTRACT_HELPER_MARKER_COUNT={marker_count}")
    print(f"LANE05_STAGE_HELPER_STATUS_CONTRACT_OUTPUT_FIELD_COUNT={output_field_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
