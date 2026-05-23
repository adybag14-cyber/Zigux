#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
CHECK_ZIG_TOOLCHAIN = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

REQUIRED_PATHS = (
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/zig-toolchain-policy.json",
)

STEP_SEQUENCE = (
    "- name: Compile current scripts",
    "- name: Self-test current Zig toolchain checker",
    "- name: Check current Zig toolchain policy packet",
    "- name: Check current pinned Zig archive packet",
    "- name: Self-test current Lane 05 local-first archive checker",
)

WORKFLOW_RUN_COUNTS = {
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test": 1,
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only": 1,
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing": 1,
}

CHECKER_MARKERS = (
    'parser.add_argument("--allow-missing", action="store_true", help="Return success when zig is unavailable.")',
    'parser.add_argument("--policy-only", action="store_true", help="Validate and summarize the pinned Zig policy without probing a zig executable.")',
    'parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")',
    'parser.add_argument("--archive", help="Explicit Zig archive path for archive-integrity validation.")',
    'parser.add_argument("--archive-target", help="Archive target key from scripts/zigux/zig-toolchain-policy.json.")',
    'parser.add_argument("--self-test", action="store_true", help="Run built-in parser and ordering checks.")',
    "if args.policy_only:",
    "if args.archive_only:",
)

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "channel": "0.17.0-dev.87+9b177a7d2",
    "minimum_version": "0.17.0-dev.87+9b177a7d2",
    "archive_target_scope": ["x86_64-linux"],
    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
    "channel_minimum_lockstep": True,
}


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def remove_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def swap_exact_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index: int | None = None
    second_index: int | None = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == first and first_index is None:
            first_index = index
        if stripped == second and second_index is None:
            second_index = index
    if first_index is None or second_index is None:
        raise AssertionError("swap markers not found")
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def replace_text(text: str, old: str, new: str) -> str:
    if old not in text:
        raise AssertionError(f"expected substring not found: {old}")
    return text.replace(old, new, 1)


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_required_path:{rel}")

    workflow = read_text(root, ".github/workflows/zigux-bootstrap.yml")
    checker = read_text(root, "scripts/zigux/check-zig-toolchain.py")
    policy_text = read_text(root, "scripts/zigux/zig-toolchain-policy.json")

    for marker in STEP_SEQUENCE:
        count = count_exact_lines(workflow, marker)
        if count != 1:
            issues.append(f"workflow_step:{marker}:count={count}:expected=1")

    step_positions: list[int] = []
    for marker in STEP_SEQUENCE:
        for index, line in enumerate(workflow.splitlines()):
            if line.strip() == marker:
                step_positions.append(index)
                break
    if len(step_positions) == len(STEP_SEQUENCE) and step_positions != sorted(step_positions):
        issues.append("workflow_step_order:expected_compile_then_toolchain_then_lane05_handoff")

    for marker, expected in WORKFLOW_RUN_COUNTS.items():
        count = count_exact_lines(workflow, marker)
        if count != expected:
            issues.append(f"workflow_run:{marker}:count={count}:expected={expected}")

    for marker in CHECKER_MARKERS:
        if marker not in checker:
            issues.append(f"checker_marker:{marker}")

    try:
        payload = json.loads(policy_text)
    except json.JSONDecodeError as exc:
        issues.append(f"policy_json:{exc.msg}")
        return issues

    if not isinstance(payload, dict):
        issues.append("policy_shape:expected_object")
        return issues

    archive_sha256 = payload.get("archive_sha256")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(archive_sha256, dict):
        issues.append("policy_archive_sha256:expected_object")
    if not isinstance(upgrade_policy, dict):
        issues.append("policy_upgrade_policy:expected_object")
        return issues

    if payload.get("phase") != EXPECTED_POLICY["phase"]:
        issues.append(f"policy_phase:{payload.get('phase')}:expected={EXPECTED_POLICY['phase']}")
    if payload.get("channel") != EXPECTED_POLICY["channel"]:
        issues.append(f"policy_channel:{payload.get('channel')}:expected={EXPECTED_POLICY['channel']}")
    if payload.get("minimum_version") != EXPECTED_POLICY["minimum_version"]:
        issues.append(
            f"policy_minimum_version:{payload.get('minimum_version')}:expected={EXPECTED_POLICY['minimum_version']}"
        )

    if archive_sha256 != {"x86_64-linux": archive_sha256.get("x86_64-linux")}:
        issues.append("policy_archive_targets:expected_only_x86_64_linux")
    expected_digest = archive_sha256.get("x86_64-linux") if isinstance(archive_sha256, dict) else None
    if not isinstance(expected_digest, str) or len(expected_digest) != 64:
        issues.append("policy_archive_sha256_x86_64_linux:expected_64_hex")

    if upgrade_policy.get("channel_minimum_lockstep") != EXPECTED_POLICY["channel_minimum_lockstep"]:
        issues.append(
            "policy_channel_minimum_lockstep:"
            f"{upgrade_policy.get('channel_minimum_lockstep')}:expected={EXPECTED_POLICY['channel_minimum_lockstep']}"
        )
    if upgrade_policy.get("archive_target_scope") != EXPECTED_POLICY["archive_target_scope"]:
        issues.append(
            "policy_archive_target_scope:"
            f"{upgrade_policy.get('archive_target_scope')}:expected={EXPECTED_POLICY['archive_target_scope']}"
        )
    if upgrade_policy.get("required_make_routes") != EXPECTED_POLICY["required_make_routes"]:
        issues.append(
            "policy_required_make_routes:"
            f"{upgrade_policy.get('required_make_routes')}:expected={EXPECTED_POLICY['required_make_routes']}"
        )

    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET=fail")
    for issue in issues:
        print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_ISSUE={issue}")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        ".github/workflows/zigux-bootstrap.yml",
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Compile current scripts",
                "        run: python3 -m py_compile scripts/zigux/check-zig-toolchain.py",
                "      - name: Self-test current Zig toolchain checker",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
                "      - name: Check current Zig toolchain policy packet",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
                "      - name: Check current pinned Zig archive packet",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
                "      - name: Self-test current Lane 05 local-first archive checker",
                "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "scripts/zigux/check-zig-toolchain.py",
        "\n".join(
            (
                "def main() -> int:",
                "    parser = argparse.ArgumentParser(description=\"Check local Zig toolchain availability for Zigux bootstrap work.\")",
                "    parser.add_argument(\"--allow-missing\", action=\"store_true\", help=\"Return success when zig is unavailable.\")",
                "    parser.add_argument(\"--policy-only\", action=\"store_true\", help=\"Validate and summarize the pinned Zig policy without probing a zig executable.\")",
                "    parser.add_argument(\"--archive-only\", action=\"store_true\", help=\"Validate the pinned Zig archive artifact without probing a zig executable.\")",
                "    parser.add_argument(\"--archive\", help=\"Explicit Zig archive path for archive-integrity validation.\")",
                "    parser.add_argument(\"--archive-target\", help=\"Archive target key from scripts/zigux/zig-toolchain-policy.json.\")",
                "    parser.add_argument(\"--self-test\", action=\"store_true\", help=\"Run built-in parser and ordering checks.\")",
                "    if args.policy_only:",
                "        return 0",
                "    if args.archive_only:",
                "        return 0",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "scripts/zigux/zig-toolchain-policy.json",
        json.dumps(
            {
                "phase": EXPECTED_POLICY["phase"],
                "channel": EXPECTED_POLICY["channel"],
                "minimum_version": EXPECTED_POLICY["minimum_version"],
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": EXPECTED_POLICY["channel_minimum_lockstep"],
                    "archive_target_scope": EXPECTED_POLICY["archive_target_scope"],
                    "required_make_routes": EXPECTED_POLICY["required_make_routes"],
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_bootstrap_toolchain_checker_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        case_count += 1

        build_sample_root(root)
        write_text(
            root,
            ".github/workflows/zigux-bootstrap.yml",
            remove_exact_line(
                read_text(root, ".github/workflows/zigux-bootstrap.yml"),
                "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
            ),
        )
        assert any(issue.startswith("workflow_run:run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing") for issue in collect_issues(root))
        case_count += 1

        build_sample_root(root)
        write_text(
            root,
            ".github/workflows/zigux-bootstrap.yml",
            swap_exact_lines(
                read_text(root, ".github/workflows/zigux-bootstrap.yml"),
                "- name: Check current Zig toolchain policy packet",
                "- name: Check current pinned Zig archive packet",
            ),
        )
        assert "workflow_step_order:expected_compile_then_toolchain_then_lane05_handoff" in collect_issues(root)
        case_count += 1

        build_sample_root(root)
        write_text(
            root,
            "scripts/zigux/check-zig-toolchain.py",
            replace_text(
                read_text(root, "scripts/zigux/check-zig-toolchain.py"),
                'parser.add_argument("--policy-only", action="store_true", help="Validate and summarize the pinned Zig policy without probing a zig executable.")\n',
                "",
            ),
        )
        assert any(issue.startswith("checker_marker:parser.add_argument(\"--policy-only\"") for issue in collect_issues(root))
        case_count += 1

        build_sample_root(root)
        payload = json.loads(read_text(root, "scripts/zigux/zig-toolchain-policy.json"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        write_text(root, "scripts/zigux/zig-toolchain-policy.json", json.dumps(payload, indent=2) + "\n")
        assert "policy_required_make_routes:['phase2-toolchain', 'phase2-validate']:expected=['phase2-toolchain', 'phase2-validate', 'phase2-cross']" in collect_issues(root)
        case_count += 1

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the bootstrap workflow packet around check-zig-toolchain.py self-test, policy-only, and archive-only routes."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal current-like sample root and exit.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_REQUIRED_STEP_COUNT={len(STEP_SEQUENCE)}")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_REQUIRED_CHECKER_MARKER_COUNT={len(CHECKER_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_REQUIRED_ROUTE_COUNT={len(EXPECTED_POLICY['required_make_routes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
