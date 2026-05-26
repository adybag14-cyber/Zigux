#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")
TOOLCHAIN_POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")

REQUIRED_MARKERS = (
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    'part-*.b64',
    'raise SystemExit("choose either split mode (--source/--output-dir) or reconstruct mode (--parts-dir/--destination)")',
    'raise SystemExit("--source and --output-dir are required for split mode")',
    'raise SystemExit("--parts-dir and --destination are required for reconstruct mode")',
    'print("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
    'print("SPLIT_PINNED_ZIG_ARCHIVE=fail")',
    'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
    'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=fail")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SOURCE={source}")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_OUTPUT_DIR={output_dir}")',
    'print(f"SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={manifest_path}")',
    'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
    'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")',
    'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={metadata[\'part_count\']}")',
    'parser.add_argument("--source", type=Path, help="Path to the validated pinned Zig archive payload.")',
    'parser.add_argument("--output-dir",',
    'parser.add_argument("--parts-dir",',
    'parser.add_argument("--destination",',
    'parser.add_argument("--self-test", action="store_true", help="Run built-in shard helper coverage.")',
)

EXACT_ONCE_MARKERS = (
    'raise SystemExit("choose either split mode (--source/--output-dir) or reconstruct mode (--parts-dir/--destination)")',
    'raise SystemExit("--source and --output-dir are required for split mode")',
    'raise SystemExit("--parts-dir and --destination are required for reconstruct mode")',
    'print("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
    'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
)

ORDERED_MARKERS = (
    (
        'raise SystemExit("choose either split mode (--source/--output-dir) or reconstruct mode (--parts-dir/--destination)")',
        'if split_mode:',
    ),
    (
        'if split_mode:',
        'if reconstruct_mode:',
    ),
    (
        'print("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
        'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
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


def load_contract(root: Path) -> dict[str, str]:
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

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or len(archive_target_scope) != 1:
        raise ValueError(f"expected exactly one archive target in {policy_path}")

    target = require_non_empty_string(archive_target_scope[0], "archive target", policy_path)
    digest = require_non_empty_string(archive_sha256.get(target), f"archive_sha256[{target}]", policy_path)
    filename = f"zig-{target}-{channel}.tar.xz"
    return {"target": target, "filename": filename, "sha256": digest}


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 split-helper cli checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"lane05 split-helper cli checker expected exactly {expected} occurrences of {label} `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 split-helper cli checker missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(f"lane05 split-helper cli checker expected {label} `{earlier}` before `{later}`")


def check_helper(root: Path, contract: dict[str, str]) -> int:
    helper_text = read_text(root / HELPER_PATH)

    for marker in REQUIRED_MARKERS:
        require_marker(helper_text, marker, "helper marker")
    for marker in EXACT_ONCE_MARKERS:
        require_exact_count(helper_text, marker, 1, "helper marker")
    for earlier, later in ORDERED_MARKERS:
        require_order(helper_text, earlier, later, "cli flow")

    require_marker(
        helper_text,
        f'"filename": f"zig-{{target}}-{{channel}}.tar.xz"',
        "policy filename assembly",
    )
    require_marker(
        helper_text,
        f'print(f"SPLIT_PINNED_ZIG_ARCHIVE_FILENAME={{metadata[\'filename\']}}")',
        "split filename status",
    )
    require_marker(
        helper_text,
        f'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME={{metadata[\'filename\']}}")',
        "reconstruct filename status",
    )
    require_marker(
        helper_text,
        f'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SHA256={{metadata[\'sha256\']}}")',
        "split sha status",
    )
    require_marker(
        helper_text,
        f'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256={{metadata[\'sha256\']}}")',
        "reconstruct sha status",
    )
    require_marker(helper_text, contract["filename"], "current filename contract")
    return len(REQUIRED_MARKERS) + 6


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
    (root / HELPER_PATH).write_text(
        "\n".join(
            (
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                "",
                'metadata = { "filename": f"zig-{target}-{channel}.tar.xz" }',
                'manifest = { "parts_glob": "part-*.b64" }',
                'parser.add_argument("--source", type=Path, help="Path to the validated pinned Zig archive payload.")',
                'parser.add_argument("--output-dir", type=Path, help="Directory that will receive manifest.json plus part-XXX.b64 files.")',
                'parser.add_argument("--parts-dir", type=Path, help="Directory containing manifest.json plus part-XXX.b64 files to reconstruct.")',
                'parser.add_argument("--destination", type=Path, help="Where to write the reconstructed archive when --parts-dir is used.")',
                'parser.add_argument("--self-test", action="store_true", help="Run built-in shard helper coverage.")',
                'raise SystemExit("choose either split mode (--source/--output-dir) or reconstruct mode (--parts-dir/--destination)")',
                "if split_mode:",
                '    raise SystemExit("--source and --output-dir are required for split mode")',
                "if reconstruct_mode:",
                '    raise SystemExit("--parts-dir and --destination are required for reconstruct mode")',
                'print("SPLIT_PINNED_ZIG_ARCHIVE=fail")',
                'print("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SOURCE={source}")',
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_OUTPUT_DIR={output_dir}")',
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_MANIFEST={manifest_path}")',
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
                'print(f"SPLIT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")',
                'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=fail")',
                'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
                'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PARTS_DIR={parts_dir}")',
                'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")',
                'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_FILENAME={metadata[\'filename\']}")',
                'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_SHA256={metadata[\'sha256\']}")',
                'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={metadata[\'part_count\']}")',
                '# zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_cli_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        contract = load_contract(root)
        assert check_helper(root, contract) == len(REQUIRED_MARKERS) + 6
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_split_helper_cli_fail_") as tmp_dir:
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
        lambda root: (root / HELPER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing helper marker",
    )
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                'raise SystemExit("--source and --output-dir are required for split mode")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "--source and --output-dir are required for split mode",
    )
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                'print("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
                'print("SPLIT_PINNED_ZIG_ARCHIVE=pass")\nprint("SPLIT_PINNED_ZIG_ARCHIVE=pass")',
                1,
            ),
            encoding="utf-8",
        ),
        "exactly 1 occurrences",
    )
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                'print(f"RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT={metadata[\'part_count\']}")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "RECONSTRUCT_PINNED_ZIG_ARCHIVE_PART_COUNT",
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
    expect_failure(
        lambda root: (root / HELPER_PATH).write_text(
            (root / HELPER_PATH).read_text(encoding="utf-8").replace(
                'if split_mode:\n',
                'if reconstruct_mode:\n',
                1,
            ),
            encoding="utf-8",
        ),
        "ordered markers for cli flow",
    )

    print("LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split helper keeps its CLI and status contract explicit."
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
        print("LANE05_SPLIT_HELPER_CLI_CONTRACT=fail")
        print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_HELPER_CLI_CONTRACT=pass")
    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_ROOT={root}")
    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_TARGET={contract['target']}")
    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_FILENAME={contract['filename']}")
    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_SHA256={contract['sha256']}")
    print(f"LANE05_SPLIT_HELPER_CLI_CONTRACT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())