#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
README_PATH = Path("third_party/README.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}


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
        normalized[map_key.strip()] = map_value.strip()
    return normalized


def require_string_list(payload: dict[str, object], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"invalid {key} in {POLICY_PATH}")
    normalized: list[str] = []
    for entry in value:
        if not isinstance(entry, str) or not entry.strip():
            raise ValueError(f"invalid {key} entry in {POLICY_PATH}")
        normalized.append(entry.strip())
    return normalized


def expected_archive_filename(target: str, channel: str) -> str:
    return f"zig-{target}-{channel}.tar.xz"


def duplicate_archive_filename(expected_filename: str) -> str:
    stem = expected_filename[: -len(".tar.xz")]
    return f"{stem} (1).tar.xz"


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"missing {label}: {marker}")


def validate_contract(root: Path) -> tuple[str, str, int]:
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
        raise ValueError(f"archive target {target} is missing from archive_sha256 in {POLICY_PATH}")
    if target not in EXPECTED_ARCHIVE_SIZES:
        raise ValueError(f"missing expected archive size for {target}")

    expected_sha = archives[target]
    expected_size = EXPECTED_ARCHIVE_SIZES[target]
    expected_filename = expected_archive_filename(target, channel)
    expected_path = f"third_party/{expected_filename}"
    duplicate_name = duplicate_archive_filename(expected_filename)
    validation_command = (
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "
        f"{expected_path} --archive-target {target}"
    )

    try:
        readme_text = (root / README_PATH).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing archive README: {root / README_PATH}") from exc
    try:
        workflow_text = (root / WORKFLOW_PATH).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing bootstrap workflow: {root / WORKFLOW_PATH}") from exc

    readme_markers = (
        f"- target: `{target}`",
        f"- channel: `{channel}`",
        f"- file: `{expected_path}`",
        f"- sha256: `{expected_sha}`",
        f"- size: `{expected_size}` bytes",
        f"`{validation_command}`",
        f"`{duplicate_name}`",
        f"`{POLICY_PATH}`",
    )
    for marker in readme_markers:
        require_marker(readme_text, marker, "README marker")

    workflow_markers = (
        'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
        'targets = policy["upgrade_policy"]["archive_target_scope"]',
        'channel = policy["channel"]',
        'filename = f"zig-{target}-{channel}.tar.xz"',
        'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
        'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    )
    for marker in workflow_markers:
        require_marker(workflow_text, marker, "workflow marker")

    if expected_path not in readme_text:
        raise ValueError(f"README path drifted away from policy path {expected_path}")
    require_marker(
        workflow_text,
        'filename = f"zig-{target}-{channel}.tar.xz"',
        "workflow filename derivation marker",
    )

    marker_count = len(readme_markers) + len(workflow_markers)
    return target, expected_filename, marker_count


def write_sample_root(root: Path) -> None:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / "third_party").mkdir(parents=True, exist_ok=True)
    (root / ".github" / "workflows").mkdir(parents=True, exist_ok=True)

    policy_text = """{
  "phase": "Phase 2",
  "channel": "0.17.0-dev.87+9b177a7d2",
  "minimum_version": "0.17.0-dev.87+9b177a7d2",
  "archive_sha256": {
    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
  },
  "upgrade_policy": {
    "channel_minimum_lockstep": true,
    "archive_target_scope": [
      "x86_64-linux"
    ],
    "required_make_routes": [
      "phase2-toolchain",
      "phase2-validate"
    ]
  }
}
"""
    readme_text = """# Zigux third-party archives

This directory is reserved for trusted archive payloads that Lane 05 bootstrap CI
can validate locally before it falls back to network downloads.

## Current pinned Zig archive contract

- target: `x86_64-linux`
- channel: `0.17.0-dev.87+9b177a7d2`
- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`
- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`
- size: `58159088` bytes

## Validation

- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`

## Bootstrap order

- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.
- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.
- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.

## Rules

- keep the filename exact so bootstrap can resolve the pinned archive without guessing
- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` in this directory
- update this README and its checker whenever `scripts/zigux/zig-toolchain-policy.json` changes the pinned target, channel, digest, or expected payload size
"""
    workflow_text = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Setup pinned Zig toolchain
        run: |
          eval "$(python3 - <<'PY'
          import json
          from pathlib import Path

          policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))
          targets = policy["upgrade_policy"]["archive_target_scope"]
          channel = policy["channel"]
          filename = f"zig-{target}-{channel}.tar.xz"
          PY
          )"
          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
          python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"
"""

    (root / POLICY_PATH).write_text(policy_text, encoding="utf-8")
    (root / README_PATH).write_text(readme_text, encoding="utf-8")
    (root / WORKFLOW_PATH).write_text(workflow_text, encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    def expect_pass() -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_contract_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            assert validate_contract(root) == (
                "x86_64-linux",
                "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
                14,
            )
            case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_contract_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                validate_contract(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected validate_contract to fail")

    expect_pass()
    expect_failure(
        lambda root: (root / README_PATH).write_text("missing\n", encoding="utf-8"),
        "missing README marker",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text("name: zigux-bootstrap\n", encoding="utf-8"),
        "missing workflow marker",
    )
    expect_failure(
        lambda root: (root / POLICY_PATH).write_text(
            """{
  "phase": "Phase 2",
  "channel": "0.17.0-dev.87+9b177a7d2",
  "minimum_version": "0.17.0-dev.87+9b177a7d2",
  "archive_sha256": {
    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
  },
  "upgrade_policy": {
    "channel_minimum_lockstep": true,
    "archive_target_scope": [
      "x86_64-linux",
      "aarch64-linux"
    ],
    "required_make_routes": [
      "phase2-toolchain",
      "phase2-validate"
    ]
  }
}
""",
            encoding="utf-8",
        ),
        "expected exactly one archive target",
    )
    expect_failure(
        lambda root: (root / README_PATH).write_text(
            (root / README_PATH).read_text(encoding="utf-8").replace(
                "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz",
                "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2-copy.tar.xz",
            ),
            encoding="utf-8",
        ),
        "missing README marker",
    )

    print("LANE05_LOCAL_ARCHIVE_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_LOCAL_ARCHIVE_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Lane 05 local archive cross-file contract."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker coverage.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for local replay validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"LANE05_LOCAL_ARCHIVE_CONTRACT_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    try:
        target, filename, marker_count = validate_contract(args.root.resolve())
    except ValueError as exc:
        print("LANE05_LOCAL_ARCHIVE_CONTRACT=fail")
        print(f"LANE05_LOCAL_ARCHIVE_CONTRACT_ROOT={args.root.resolve()}")
        print(f"LANE05_LOCAL_ARCHIVE_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_LOCAL_ARCHIVE_CONTRACT=pass")
    print(f"LANE05_LOCAL_ARCHIVE_CONTRACT_ROOT={args.root.resolve()}")
    print(f"LANE05_LOCAL_ARCHIVE_TARGET={target}")
    print(f"LANE05_LOCAL_ARCHIVE_FILENAME={filename}")
    print(f"LANE05_LOCAL_ARCHIVE_CONTRACT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
