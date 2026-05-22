#!/usr/bin/env python3
"""Fail-close guard for the Lane 05 install-zig self-test hook."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
INSTALLER_PATH = ROOT / "scripts" / "zigux" / "install-zig.py"
POLICY_PATH = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

SELF_TEST_STEP = "- name: Self-test current Zig installer helper"
SELF_TEST_CMD = "run: python3 scripts/zigux/install-zig.py --self-test"
PREVIOUS_STEP = "- name: Check current Lane 05 local archive README packet"
NEXT_STEP = "- name: Self-test current Phase 2 fixdep gate checker"
POLICY_ONLY_STEP = "- name: Check current Zig toolchain policy packet"

INSTALLER_MARKERS = (
    "TOOLCHAIN_POLICY = ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json'",
    "def load_policy_channel(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_CHANNEL) -> str:",
    "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
    "parser.add_argument('--self-test', action='store_true', help='Run built-in target-resolution coverage without downloading')",
    "if args.self_test:",
    "return run_self_test()",
    "policy_channel = load_policy_channel()",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "print('ZIG_INSTALL_SELF_TEST=pass')",
    "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=39')",
    "print(f'ZIG_INSTALL_CHANNEL={channel}')",
    "print(f'ZIG_INSTALL_TARGET={target_key}')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
    "print('ZIG_INSTALL_STATUS=resolved')",
    "print('ZIG_INSTALL_STATUS=pass')",
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 stage-helper selftest checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 stage-helper selftest checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 stage-helper selftest checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 stage-helper selftest checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_policy(text: str) -> None:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"lane05 stage-helper selftest checker found invalid toolchain policy JSON: {exc.msg}"
        ) from exc

    if not isinstance(payload, dict):
        raise SystemExit("lane05 stage-helper selftest checker expected policy JSON object")

    channel = payload.get("channel")
    if channel != "0.17.0-dev.87+9b177a7d2":
        raise SystemExit(
            "lane05 stage-helper selftest checker expected pinned toolchain channel "
            "0.17.0-dev.87+9b177a7d2"
        )

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or "x86_64-linux" not in archive_sha256:
        raise SystemExit(
            "lane05 stage-helper selftest checker expected archive_sha256 entry for x86_64-linux"
        )

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit("lane05 stage-helper selftest checker expected upgrade_policy object")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if archive_target_scope != ["x86_64-linux"]:
        raise SystemExit(
            "lane05 stage-helper selftest checker expected archive_target_scope "
            "to stay pinned to x86_64-linux"
        )


def check_root(root: Path) -> None:
    workflow_text = (root / WORKFLOW_PATH.relative_to(ROOT)).read_text(encoding="utf-8")
    installer_text = (root / INSTALLER_PATH.relative_to(ROOT)).read_text(encoding="utf-8")
    policy_text = (root / POLICY_PATH.relative_to(ROOT)).read_text(encoding="utf-8")

    require_marker(workflow_text, SELF_TEST_STEP, "workflow self-test step name")
    require_marker(workflow_text, SELF_TEST_CMD, "workflow self-test command")
    require_marker(workflow_text, PREVIOUS_STEP, "workflow previous step anchor")
    require_marker(workflow_text, NEXT_STEP, "workflow next step anchor")
    require_marker(workflow_text, POLICY_ONLY_STEP, "workflow policy step anchor")

    require_exact_count(workflow_text, SELF_TEST_STEP, 1, "workflow step name")
    require_exact_count(workflow_text, SELF_TEST_CMD, 1, "workflow run line")

    require_order(workflow_text, POLICY_ONLY_STEP, SELF_TEST_STEP, "workflow Lane 05 order")
    require_order(workflow_text, PREVIOUS_STEP, SELF_TEST_STEP, "workflow Lane 05 order")
    require_order(workflow_text, SELF_TEST_STEP, NEXT_STEP, "workflow Lane 05 order")

    for marker in INSTALLER_MARKERS:
        require_marker(installer_text, marker, "installer marker")

    require_exact_count(
        installer_text,
        "print('ZIG_INSTALL_SELF_TEST=pass')",
        1,
        "installer self-test status output",
    )
    require_exact_count(
        installer_text,
        "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=39')",
        1,
        "installer self-test case-count output",
    )
    require_exact_count(
        installer_text,
        "parser.add_argument('--self-test', action='store_true', help='Run built-in target-resolution coverage without downloading')",
        1,
        "installer self-test flag",
    )

    require_order(
        installer_text,
        "if args.self_test:",
        "return run_self_test()",
        "installer self-test gate order",
    )
    require_order(
        installer_text,
        "policy_channel = load_policy_channel()",
        "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
        "installer policy-resolution order",
    )
    require_order(
        installer_text,
        "print('ZIG_INSTALL_SELF_TEST=pass')",
        "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=39')",
        "installer self-test output order",
    )
    require_order(
        installer_text,
        "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
        "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
        "installer archive-status branches",
    )

    check_policy(policy_text)


def write_sample_root(root: Path) -> None:
    (root / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)

    (root / ".github" / "workflows" / "zigux-bootstrap.yml").write_text(
        "\n".join(
            [
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                f"      {POLICY_ONLY_STEP}",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
                "      - name: Check current Lane 05 local archive README packet",
                "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
                f"      {SELF_TEST_STEP}",
                f"        {SELF_TEST_CMD}",
                f"      {NEXT_STEP}",
                "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (root / "scripts" / "zigux" / "install-zig.py").write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "ROOT = Path.cwd()",
                "TOOLCHAIN_POLICY = ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json'",
                "FALLBACK_CHANNEL = 'master'",
                "def load_policy_channel(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_CHANNEL) -> str:",
                "    return fallback",
                "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
                "    return None",
                "def run_self_test() -> int:",
                "    print('ZIG_INSTALL_SELF_TEST=pass')",
                "    print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=39')",
                "    return 0",
                "def main() -> int:",
                "    parser = type('P', (), {'add_argument': lambda *args, **kwargs: None, 'parse_args': lambda self: type('A', (), {'self_test': True, 'channel': None, 'system': None, 'arch': None, 'resolve_only': False, 'dest': '.zig-toolchain'})()})()",
                "    parser.add_argument('--self-test', action='store_true', help='Run built-in target-resolution coverage without downloading')",
                "    args = parser.parse_args()",
                "    if args.self_test:",
                "        return run_self_test()",
                "    policy_channel = load_policy_channel()",
                "    channel = args.channel or policy_channel",
                "    target_key = 'x86_64-linux'",
                "    expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
                "    print(f'ZIG_INSTALL_CHANNEL={channel}')",
                "    print(f'ZIG_INSTALL_TARGET={target_key}')",
                "    if expected_archive_sha256 is not None:",
                "        print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
                "    else:",
                "        print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
                "    if args.resolve_only:",
                "        print('ZIG_INSTALL_STATUS=resolved')",
                "        return 0",
                "    print('ZIG_INSTALL_STATUS=pass')",
                "    return 0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (root / "scripts" / "zigux" / "zig-toolchain-policy.json").write_text(
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": true,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    import tempfile

    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_stage_helper_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        check_root(root)
        case_count += 1

        missing_step = root / ".github" / "workflows" / "zigux-bootstrap.yml"
        original = missing_step.read_text(encoding="utf-8")
        missing_step.write_text(original.replace(f"      {SELF_TEST_STEP}\n        {SELF_TEST_CMD}\n", "", 1), encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert SELF_TEST_STEP in str(exc) or SELF_TEST_CMD in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing workflow self-test step failure")
        missing_step.write_text(original, encoding="utf-8")

        installer_path = root / "scripts" / "zigux" / "install-zig.py"
        original_installer = installer_path.read_text(encoding="utf-8")
        installer_path.write_text(
            original_installer.replace(
                "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=39')",
                "print('ZIG_INSTALL_SELF_TEST_CASE_TOTAL=39')",
                1,
            ),
            encoding="utf-8",
        )
        try:
            check_root(root)
        except SystemExit as exc:
            assert "ZIG_INSTALL_SELF_TEST_CASE_COUNT=39" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing self-test case count failure")
        installer_path.write_text(original_installer, encoding="utf-8")

        policy_path = root / "scripts" / "zigux" / "zig-toolchain-policy.json"
        original_policy = policy_path.read_text(encoding="utf-8")
        policy_path.write_text(original_policy.replace('"archive_target_scope": [\n      "x86_64-linux"\n    ]', '"archive_target_scope": [\n      "aarch64-linux"\n    ]', 1), encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "archive_target_scope" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected archive_target_scope failure")
        policy_path.write_text(original_policy, encoding="utf-8")

        workflow_reordered = missing_step.read_text(encoding="utf-8").replace(
            f"      {SELF_TEST_STEP}\n        {SELF_TEST_CMD}\n      {NEXT_STEP}",
            f"      {NEXT_STEP}\n        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test\n      {SELF_TEST_STEP}\n        {SELF_TEST_CMD}",
            1,
        )
        missing_step.write_text(workflow_reordered, encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "workflow Lane 05 order" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected workflow order failure")

    print("LANE05_STAGE_HELPER_SELFTEST=pass")
    print(f"LANE05_STAGE_HELPER_SELFTEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 bootstrap workflow keeps the install-zig self-test hook explicit."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for local replay.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    check_root(args.root.resolve())
    print("LANE05_STAGE_HELPER_SELFTEST=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
