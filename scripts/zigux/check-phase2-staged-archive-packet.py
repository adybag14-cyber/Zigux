#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
README_PATH = Path("third_party/README.md")
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")
STAGE_CONTRACT_PATH = Path("scripts/zigux/check-lane05-stage-helper-contract.py")
STAGE_SELFTEST_PATH = Path("scripts/zigux/check-lane05-stage-helper-selftest.py")
TOOLCHAIN_CHECKER_PATH = Path("scripts/zigux/check-zig-toolchain.py")
INSTALL_HELPER_PATH = Path("scripts/zigux/install-zig.py")

EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}

REQUIRED_PATHS = (
    str(POLICY_PATH),
    str(README_PATH),
    str(STAGE_HELPER_PATH),
    str(STAGE_CONTRACT_PATH),
    str(STAGE_SELFTEST_PATH),
    str(TOOLCHAIN_CHECKER_PATH),
    str(INSTALL_HELPER_PATH),
    str(WORKFLOW_PATH),
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
)

WORKFLOW_STEP_ORDER = (
    "- name: Check current pinned Zig archive packet",
    "- name: Self-test current Zig installer helper",
    "- name: Self-test current staged pinned Zig archive helper",
    "- name: Self-test current Lane 05 stage helper contract checker",
    "- name: Check current Lane 05 stage helper contract packet",
    "- name: Self-test current Lane 05 stage helper selftest checker",
    "- name: Check current Lane 05 stage helper selftest packet",
    "- name: Self-test current Phase 2 fixdep gate checker",
)

STAGE_HELPER_MARKERS = (
    'THIRD_PARTY_DIR = Path("third_party")',
    "EXPECTED_ARCHIVE_SIZES = {",
    "duplicate_archive_name(",
    "archive_name_has_duplicate_suffix(",
    "STAGE_PINNED_ZIG_ARCHIVE=pass",
    "STAGE_PINNED_ZIG_ARCHIVE=fail",
    "STAGE_PINNED_ZIG_ARCHIVE_STATUS=",
)

CONTRACT_MARKERS = (
    'STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")',
    'README_PATH = Path("third_party/README.md")',
    "LANE05_STAGE_HELPER_CONTRACT=pass",
    "LANE05_STAGE_HELPER_MARKER_COUNT=",
    "LANE05_STAGE_HELPER_README_MARKER_COUNT=",
)

SELFTEST_MARKERS = (
    "STAGE_HELPER_SELF_TEST_STEP = ",
    "CONTRACT_SELF_TEST_STEP = ",
    "SELF_TEST_STEP = ",
    "CHECK_STEP = ",
    "LANE05_STAGE_HELPER_SELFTEST=pass",
    "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST=pass",
)


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_marker(text: str, marker: str, code: str, issues: list[tuple[str, str]]) -> None:
    if marker not in text:
        issues.append((code, marker))


def require_exact_line(text: str, marker: str, code: str, issues: list[tuple[str, str]]) -> None:
    count = sum(1 for line in text.splitlines() if line.strip() == marker)
    if count == 0:
        issues.append((code, marker))
    elif count != 1:
        issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))


def require_order(text: str, markers: tuple[str, ...], issues: list[tuple[str, str]]) -> None:
    last_index = -1
    for marker in markers:
        index = text.find(marker)
        if index == -1:
            issues.append(("MISSING_WORKFLOW_STEP", marker))
            return
        if index <= last_index:
            issues.append(("WORKFLOW_STEP_ORDER_DRIFT", marker))
            return
        last_index = index


def load_contract(root: Path) -> dict[str, str]:
    policy_path = root / POLICY_PATH
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")

    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        raise ValueError(f"invalid channel in {policy_path}")
    archives = payload.get("archive_sha256")
    if not isinstance(archives, dict) or not archives:
        raise ValueError(f"invalid archive_sha256 in {policy_path}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")
    targets = upgrade_policy.get("archive_target_scope")
    if not isinstance(targets, list) or len(targets) != 1:
        raise ValueError(f"expected exactly one archive target in {policy_path}")
    target = targets[0]
    if not isinstance(target, str) or not target.strip():
        raise ValueError(f"invalid archive_target_scope entry in {policy_path}")
    if target not in archives:
        raise ValueError(f"archive_target_scope target missing from archive_sha256 in {policy_path}: {target}")
    if target not in EXPECTED_ARCHIVE_SIZES:
        raise ValueError(f"missing expected archive size for {target}")

    filename = f"zig-{target}-{channel}.tar.xz"
    duplicate_name = f"{filename[:-len('.tar.xz')]} (1).tar.xz"
    return {
        "target": target,
        "channel": channel,
        "filename": filename,
        "duplicate_name": duplicate_name,
        "sha256": str(archives[target]),
        "size": str(EXPECTED_ARCHIVE_SIZES[target]),
        "archive_path": f"third_party/{filename}",
    }


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    if any(code == "MISSING_REQUIRED_PATH" for code, _ in issues):
        return issues

    contract = load_contract(root)
    workflow = read_text(root, str(WORKFLOW_PATH))
    readme = read_text(root, str(README_PATH))
    stage_helper = read_text(root, str(STAGE_HELPER_PATH))
    contract_checker = read_text(root, str(STAGE_CONTRACT_PATH))
    selftest_checker = read_text(root, str(STAGE_SELFTEST_PATH))

    for marker in REQUIRED_WORKFLOW_LINES:
        require_exact_line(workflow, marker, "MISSING_WORKFLOW_LINE", issues)
    require_order(workflow, WORKFLOW_STEP_ORDER, issues)

    for marker in STAGE_HELPER_MARKERS:
        require_marker(stage_helper, marker, "MISSING_STAGE_HELPER_MARKER", issues)
    require_marker(stage_helper, f'"{contract["target"]}": {contract["size"]},', "MISSING_STAGE_HELPER_MARKER", issues)

    for marker in CONTRACT_MARKERS:
        require_marker(contract_checker, marker, "MISSING_STAGE_CONTRACT_MARKER", issues)

    for marker in SELFTEST_MARKERS:
        require_marker(selftest_checker, marker, "MISSING_STAGE_SELFTEST_MARKER", issues)

    readme_markers = (
        "# Zigux third-party archives",
        f"`{contract['target']}`",
        f"`{contract['channel']}`",
        f"`{contract['archive_path']}`",
        f"`{contract['sha256']}`",
        f"`{contract['size']}` bytes",
        f"`{contract['duplicate_name']}`",
    )
    for marker in readme_markers:
        require_marker(readme, marker, "MISSING_README_MARKER", issues)

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_STAGED_ARCHIVE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        str(POLICY_PATH),
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
    )
    write_text(root, str(TOOLCHAIN_CHECKER_PATH), "check-zig-toolchain\n")
    write_text(root, str(INSTALL_HELPER_PATH), "install-zig\n")
    write_text(
        root,
        str(README_PATH),
        "\n".join(
            (
                "# Zigux third-party archives",
                "- target: `x86_64-linux`",
                "- channel: `0.17.0-dev.87+9b177a7d2`",
                "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
                "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
                "- size: `58159088` bytes",
                "- duplicate: `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz`",
            )
        )
        + "\n",
    )
    write_text(
        root,
        str(STAGE_HELPER_PATH),
        "\n".join(
            (
                'THIRD_PARTY_DIR = Path("third_party")',
                "EXPECTED_ARCHIVE_SIZES = {",
                '    "x86_64-linux": 58159088,',
                "}",
                "def duplicate_archive_name(expected_filename: str) -> str:",
                "    return expected_filename",
                "def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:",
                "    return False",
                "STAGE_PINNED_ZIG_ARCHIVE=pass",
                "STAGE_PINNED_ZIG_ARCHIVE=fail",
                "STAGE_PINNED_ZIG_ARCHIVE_STATUS=",
            )
        )
        + "\n",
    )
    write_text(
        root,
        str(STAGE_CONTRACT_PATH),
        "\n".join(
            (
                'STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")',
                'README_PATH = Path("third_party/README.md")',
                "LANE05_STAGE_HELPER_CONTRACT=pass",
                "LANE05_STAGE_HELPER_MARKER_COUNT=19",
                "LANE05_STAGE_HELPER_README_MARKER_COUNT=7",
            )
        )
        + "\n",
    )
    write_text(
        root,
        str(STAGE_SELFTEST_PATH),
        "\n".join(
            (
                'STAGE_HELPER_SELF_TEST_STEP = "- name: Self-test current staged pinned Zig archive helper"',
                'CONTRACT_SELF_TEST_STEP = "- name: Self-test current Lane 05 stage helper contract checker"',
                'SELF_TEST_STEP = "- name: Self-test current Lane 05 stage helper selftest checker"',
                'CHECK_STEP = "- name: Check current Lane 05 stage helper selftest packet"',
                "LANE05_STAGE_HELPER_SELFTEST=pass",
                "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST=pass",
            )
        )
        + "\n",
    )
    write_text(root, str(WORKFLOW_PATH), "name: zigux-bootstrap\njobs:\n  bootstrap:\n    steps:\n" + "\n".join(
        f"      {step}\n        {line}"
        for step, line in zip(
            WORKFLOW_STEP_ORDER,
            (
                "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
                "run: python3 scripts/zigux/install-zig.py --self-test",
                "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
                "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
                "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
                "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
                "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
                "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
            ),
        )
    ) + "\n")


def run_self_test() -> int:
    checks = 0

    with tempfile.TemporaryDirectory(prefix="phase2_staged_archive_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            str(WORKFLOW_PATH),
            read_text(root, str(WORKFLOW_PATH)).replace(
                "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\n",
                "",
                1,
            ),
        )
        assert ("MISSING_WORKFLOW_LINE", "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        workflow_lines = read_text(root, str(WORKFLOW_PATH)).splitlines()
        contract_self_test_index = workflow_lines.index("      - name: Self-test current Lane 05 stage helper contract checker")
        contract_check_index = workflow_lines.index("      - name: Check current Lane 05 stage helper contract packet")
        contract_cluster = workflow_lines[contract_self_test_index : contract_check_index + 2]
        workflow_lines[contract_self_test_index : contract_check_index + 2] = contract_cluster[2:] + contract_cluster[:2]
        write_text(root, str(WORKFLOW_PATH), "\n".join(workflow_lines) + "\n")
        assert ("WORKFLOW_STEP_ORDER_DRIFT", "- name: Check current Lane 05 stage helper contract packet") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            str(README_PATH),
            read_text(root, str(README_PATH)).replace("`58159088` bytes", "`1` bytes", 1),
        )
        assert ("MISSING_README_MARKER", "`58159088` bytes") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, str(STAGE_HELPER_PATH), "missing\n")
        assert ("MISSING_STAGE_HELPER_MARKER", 'THIRD_PARTY_DIR = Path("third_party")') in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / STAGE_SELFTEST_PATH).unlink()
        assert ("MISSING_REQUIRED_PATH", str(STAGE_SELFTEST_PATH)) in collect_issues(root)
        checks += 1

    print("PHASE2_STAGED_ARCHIVE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_STAGED_ARCHIVE_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the returned staged pinned-Zig bootstrap packet across workflow, helper, and README surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a passing sample root to the given path and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_STAGED_ARCHIVE_PACKET=pass")
    print(f"PHASE2_STAGED_ARCHIVE_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_STAGED_ARCHIVE_PACKET_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_STAGED_ARCHIVE_PACKET_WORKFLOW_STEP_COUNT={len(WORKFLOW_STEP_ORDER)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
