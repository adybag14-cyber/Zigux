#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
INSTALLER = ROOT / "scripts" / "zigux" / "install-zig.py"
POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_ARCHIVE_TARGET = "x86_64-linux"
EXPECTED_ARCHIVE_SHA256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"

WORKFLOW_SELF_TEST_STEP = "- name: Self-test current Zig installer helper"
WORKFLOW_SELF_TEST_CMD = "python3 scripts/zigux/install-zig.py --self-test"
WORKFLOW_PREVIOUS_STEP = "- name: Check current Lane 05 local archive README packet"
WORKFLOW_NEXT_STEP = "- name: Self-test current Phase 2 fixdep gate checker"
WORKFLOW_SCOPE_MARKERS = (
    "- 'scripts/zigux/**'",
    "- 'third_party/**'",
    "- '.github/workflows/zigux-bootstrap.yml'",
)

INSTALLER_MARKERS = (
    "def run_self_test() -> int:",
    "assert load_policy_channel(policy_path, '0.15.0') == '0.17.0-dev.87+9b177a7d2'",
    "assert load_policy_archive_sha256(policy_path, 'x86_64-linux') == '313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77'",
    "assert verify_archive_sha256(archive_path, expected_sha256) == expected_sha256",
    "copy_url_to_file_with_curl(",
    "copy_url_to_file(",
    "parser.add_argument('--self-test', action='store_true', help='Run built-in target-resolution coverage without downloading')",
    "if args.self_test:",
    "return run_self_test()",
    "policy_channel = load_policy_channel()",
    "print('ZIG_INSTALL_SELF_TEST=pass')",
    "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=27')",
)


def load_text(path: Path, *, label: str) -> str:
    if not path.is_file():
        raise SystemExit(f"{label}:missing_file:{path}")
    return path.read_text(encoding="utf-8")


def load_policy(path: Path) -> dict[str, object]:
    payload = json.loads(load_text(path, label="policy"))
    if not isinstance(payload, dict):
        raise SystemExit("policy:expected_object")
    return payload


def require_marker(text: str, marker: str, *, label: str, issues: list[str]) -> None:
    if marker not in text:
        issues.append(f"{label}:missing_marker:{marker}")


def require_exact_line(text: str, marker: str, *, label: str, issues: list[str]) -> None:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    if count != 1:
        issues.append(f"{label}:exact_line:{marker}:count={count}:expected=1")


def require_order(text: str, earlier: str, later: str, *, label: str, issues: list[str]) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        issues.append(f"{label}:missing_order_marker:{earlier}->{later}")
        return
    if earlier_index >= later_index:
        issues.append(f"{label}:order:{earlier}->{later}")


def validate_workflow(text: str) -> list[str]:
    issues: list[str] = []
    require_marker(text, WORKFLOW_SELF_TEST_STEP, label="workflow", issues=issues)
    require_exact_line(text, f"run: {WORKFLOW_SELF_TEST_CMD}", label="workflow", issues=issues)
    require_order(text, WORKFLOW_PREVIOUS_STEP, WORKFLOW_SELF_TEST_STEP, label="workflow", issues=issues)
    require_order(text, WORKFLOW_SELF_TEST_STEP, WORKFLOW_NEXT_STEP, label="workflow", issues=issues)
    require_exact_line(text, WORKFLOW_SELF_TEST_STEP, label="workflow", issues=issues)
    for marker in WORKFLOW_SCOPE_MARKERS:
        require_exact_line(text, marker, label="workflow_scope", issues=issues)
    return issues


def validate_installer(text: str) -> list[str]:
    issues: list[str] = []
    for marker in INSTALLER_MARKERS:
        require_marker(text, marker, label="installer", issues=issues)
    require_order(
        text,
        "parser.add_argument('--self-test', action='store_true', help='Run built-in target-resolution coverage without downloading')",
        "if args.self_test:",
        label="installer",
        issues=issues,
    )
    require_order(text, "if args.self_test:", "return run_self_test()", label="installer", issues=issues)
    require_order(text, "return run_self_test()", "policy_channel = load_policy_channel()", label="installer", issues=issues)
    return issues


def validate_policy(payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if payload.get("channel") != EXPECTED_CHANNEL:
        issues.append(f"policy:channel={payload.get('channel')!r}:expected={EXPECTED_CHANNEL!r}")
    if payload.get("minimum_version") != EXPECTED_CHANNEL:
        issues.append(
            f"policy:minimum_version={payload.get('minimum_version')!r}:expected={EXPECTED_CHANNEL!r}"
        )
    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append("policy:archive_sha256:expected_object")
    else:
        if archive_sha256.get(EXPECTED_ARCHIVE_TARGET) != EXPECTED_ARCHIVE_SHA256:
            issues.append(
                "policy:archive_sha256[x86_64-linux]"
                f"={archive_sha256.get(EXPECTED_ARCHIVE_TARGET)!r}:expected={EXPECTED_ARCHIVE_SHA256!r}"
            )
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append("policy:upgrade_policy:expected_object")
        return issues
    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if archive_target_scope != [EXPECTED_ARCHIVE_TARGET]:
        issues.append(
            f"policy:archive_target_scope={archive_target_scope!r}:expected={[EXPECTED_ARCHIVE_TARGET]!r}"
        )
    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append("policy:channel_minimum_lockstep:expected_true")
    return issues


def run_checks(root: Path) -> list[str]:
    workflow_text = load_text(root / WORKFLOW, label="workflow")
    installer_text = load_text(root / INSTALLER, label="installer")
    policy_payload = load_policy(root / POLICY)
    issues = validate_workflow(workflow_text)
    issues.extend(validate_installer(installer_text))
    issues.extend(validate_policy(policy_payload))
    return issues


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write(
        root / WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "on:",
                "  pull_request:",
                "    paths:",
                "      - 'scripts/zigux/**'",
                "      - 'third_party/**'",
                "      - '.github/workflows/zigux-bootstrap.yml'",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Check current Lane 05 local archive README packet",
                "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
                "      - name: Self-test current Zig installer helper",
                "        run: python3 scripts/zigux/install-zig.py --self-test",
                "      - name: Self-test current Phase 2 fixdep gate checker",
                "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
                "",
            )
        ),
    )
    write(
        root / INSTALLER,
        "\n".join(
            (
                "def load_policy_channel():",
                "    return 'stub'",
                "",
                "def load_policy_archive_sha256(policy_path, target_key):",
                "    return 'stub'",
                "",
                "def verify_archive_sha256(path, expected_sha256):",
                "    return expected_sha256",
                "",
                "def copy_url_to_file_with_curl(url, destination, retries=4, timeout=120.0):",
                "    return None",
                "",
                "def copy_url_to_file(url, destination, retries=4, timeout=120.0):",
                "    return None",
                "",
                "def run_self_test() -> int:",
                "    assert load_policy_channel(policy_path, '0.15.0') == '0.17.0-dev.87+9b177a7d2'",
                "    assert load_policy_archive_sha256(policy_path, 'x86_64-linux') == '313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77'",
                "    assert verify_archive_sha256(archive_path, expected_sha256) == expected_sha256",
                "    copy_url_to_file_with_curl(",
                "    copy_url_to_file(",
                "    print('ZIG_INSTALL_SELF_TEST=pass')",
                "    print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=27')",
                "    return 0",
                "",
                "def main() -> int:",
                "    parser.add_argument('--self-test', action='store_true', help='Run built-in target-resolution coverage without downloading')",
                "    if args.self_test:",
                "        return run_self_test()",
                "    policy_channel = load_policy_channel()",
                "    return 0",
                "",
            )
        ),
    )
    write(
        root / POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {
                    EXPECTED_ARCHIVE_TARGET: EXPECTED_ARCHIVE_SHA256,
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [EXPECTED_ARCHIVE_TARGET],
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_lane05_install_zig_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert run_checks(root) == []

        workflow_text = load_text(root / WORKFLOW, label="workflow")
        write(root / WORKFLOW, workflow_text.replace(WORKFLOW_SELF_TEST_STEP, "- name: Missing installer step"))
        assert any(issue.startswith("workflow:missing_marker:") for issue in run_checks(root))
        write_sample_root(root)

        installer_text = load_text(root / INSTALLER, label="installer")
        write(root / INSTALLER, installer_text.replace("print('ZIG_INSTALL_SELF_TEST=pass')", "print('broken')"))
        assert any(issue.startswith("installer:missing_marker:print('ZIG_INSTALL_SELF_TEST=pass')") for issue in run_checks(root))
        write_sample_root(root)

        policy_payload = load_policy(root / POLICY)
        policy_payload["minimum_version"] = "0.16.0"
        write(root / POLICY, json.dumps(policy_payload, indent=2) + "\n")
        assert "policy:minimum_version='0.16.0':expected='0.17.0-dev.87+9b177a7d2'" in run_checks(root)

    print("LANE05_INSTALL_ZIG_SELFTEST_SELF_TEST=pass")
    print("LANE05_INSTALL_ZIG_SELFTEST_SELF_TEST_CASE_COUNT=4")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail-close guard for the Lane 05 install-zig bootstrap self-test hook."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to inspect.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root and exit.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker self-tests without reading repo files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    issues = run_checks(args.root)
    if issues:
        for issue in issues:
            print(issue)
        return 1

    print("LANE05_INSTALL_ZIG_SELFTEST=pass")
    print("LANE05_INSTALL_ZIG_SELFTEST_WORKFLOW_MARKER_COUNT=6")
    print("LANE05_INSTALL_ZIG_SELFTEST_INSTALLER_MARKER_COUNT=12")
    print(f"LANE05_INSTALL_ZIG_SELFTEST_CHANNEL={EXPECTED_CHANNEL}")
    print(f"LANE05_INSTALL_ZIG_SELFTEST_ARCHIVE_TARGET={EXPECTED_ARCHIVE_TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
