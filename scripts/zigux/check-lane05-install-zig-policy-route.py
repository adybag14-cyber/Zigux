#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
INSTALLER_PATH = Path("scripts/zigux/install-zig.py")

SELF_TEST_STEP = "- name: Self-test current Zig installer helper"
SELF_TEST_CMD = "python3 scripts/zigux/install-zig.py --self-test"
README_CHECK_STEP = "- name: Check current Lane 05 local archive README packet"
NEXT_PHASE2_STEP = "- name: Self-test current Phase 2 fixdep gate checker"
SCRIPTS_PATH = "- 'scripts/zigux/**'"
THIRD_PARTY_PATH = "- 'third_party/**'"

INSTALLER_REQUIRED_MARKERS = (
    "def load_policy_channel(",
    "def load_policy_archive_sha256(",
    "def verify_archive_sha256(",
    "policy_channel = load_policy_channel()",
    "channel = args.channel or policy_channel",
    "expected_archive_sha256 = None",
    "if channel == policy_channel:",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "if expected_archive_sha256 is not None:",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
    "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
)

INSTALLER_SINGLETON_MARKERS = (
    "policy_channel = load_policy_channel()",
    "channel = args.channel or policy_channel",
    "expected_archive_sha256 = None",
    "if channel == policy_channel:",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 install-zig policy-route checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 install-zig policy-route checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_exact_line_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = sum(1 for line in text.splitlines() if line.strip() == marker)
    if actual != expected:
        raise SystemExit(
            "lane05 install-zig policy-route checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(f"lane05 install-zig policy-route checker missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 install-zig policy-route checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_root(root: Path) -> tuple[int, int]:
    workflow_text = (root / WORKFLOW_PATH).read_text(encoding="utf-8")
    installer_text = (root / INSTALLER_PATH).read_text(encoding="utf-8")

    require_marker(workflow_text, SELF_TEST_STEP, "workflow step name")
    require_marker(workflow_text, f"run: {SELF_TEST_CMD}", "workflow step command")
    require_marker(workflow_text, README_CHECK_STEP, "workflow readme-check step")
    require_marker(workflow_text, NEXT_PHASE2_STEP, "workflow next phase anchor")
    require_marker(workflow_text, SCRIPTS_PATH, "workflow scripts path filter")
    require_marker(workflow_text, THIRD_PARTY_PATH, "workflow third-party path filter")

    require_exact_count(workflow_text, SELF_TEST_STEP, 1, "workflow step name")
    require_exact_line_count(workflow_text, f"run: {SELF_TEST_CMD}", 1, "workflow run line")
    require_order(workflow_text, README_CHECK_STEP, SELF_TEST_STEP, "workflow lane05 helper order")
    require_order(workflow_text, SELF_TEST_STEP, NEXT_PHASE2_STEP, "workflow phase handoff order")
    require_order(workflow_text, SCRIPTS_PATH, THIRD_PARTY_PATH, "workflow path filter order")

    for marker in INSTALLER_REQUIRED_MARKERS:
        require_marker(installer_text, marker, "install-zig policy marker")
    for marker in INSTALLER_SINGLETON_MARKERS:
        require_exact_count(installer_text, marker, 1, "install-zig policy marker")

    require_order(
        installer_text,
        "policy_channel = load_policy_channel()",
        "channel = args.channel or policy_channel",
        "install-zig channel resolution order",
    )
    require_order(
        installer_text,
        "channel = args.channel or policy_channel",
        "expected_archive_sha256 = None",
        "install-zig sha setup order",
    )
    require_order(
        installer_text,
        "expected_archive_sha256 = None",
        "if channel == policy_channel:",
        "install-zig policy lockstep order",
    )
    require_order(
        installer_text,
        "if channel == policy_channel:",
        "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
        "install-zig policy sha-load order",
    )
    require_order(
        installer_text,
        "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
        "if expected_archive_sha256 is not None:",
        "install-zig verification branch order",
    )
    require_order(
        installer_text,
        "if expected_archive_sha256 is not None:",
        "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
        "install-zig verification call order",
    )

    return 6, len(INSTALLER_REQUIRED_MARKERS)


def write_sample_root(root: Path) -> None:
    workflow_path = root / WORKFLOW_PATH
    installer_path = root / INSTALLER_PATH
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    installer_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        "\n".join(
            [
                "name: zigux-bootstrap",
                "on:",
                "  pull_request:",
                "    paths:",
                "      - 'scripts/zigux/**'",
                "      - 'third_party/**'",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                f"      {README_CHECK_STEP}",
                "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
                f"      {SELF_TEST_STEP}",
                f"        run: {SELF_TEST_CMD}",
                f"      {NEXT_PHASE2_STEP}",
                "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
                "",
            ]
        ),
        encoding="utf-8",
    )
    installer_path.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "def load_policy_channel(policy_path=None, fallback='master'):",
                "    return fallback",
                "",
                "def load_policy_archive_sha256(policy_path, target_key):",
                "    return None",
                "",
                "def verify_archive_sha256(path, expected_sha256):",
                "    return expected_sha256",
                "",
                "def main(args):",
                "    policy_channel = load_policy_channel()",
                "    channel = args.channel or policy_channel",
                "    expected_archive_sha256 = None",
                "    if channel == policy_channel:",
                "        expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
                "    print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
                "    if expected_archive_sha256 is not None:",
                "        actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
                "        print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
                "        print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
                "    else:",
                "        print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
                "",
            ]
        ),
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane05_install_zig_policy_route_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert check_root(root) == (6, 14)
        case_count += 1

        missing_step_root = root / "missing-step"
        write_sample_root(missing_step_root)
        workflow_path = missing_step_root / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                f"      {SELF_TEST_STEP}\n        run: {SELF_TEST_CMD}\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        try:
            check_root(missing_step_root)
        except SystemExit as exc:
            assert SELF_TEST_STEP in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing install-zig self-test step failure")

        missing_policy_route_root = root / "missing-policy-route"
        write_sample_root(missing_policy_route_root)
        installer_path = missing_policy_route_root / INSTALLER_PATH
        installer_path.write_text(
            installer_path.read_text(encoding="utf-8").replace(
                "policy_channel = load_policy_channel()\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        try:
            check_root(missing_policy_route_root)
        except SystemExit as exc:
            assert "policy_channel = load_policy_channel()" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing policy-channel route failure")

        missing_verified_status_root = root / "missing-verified-status"
        write_sample_root(missing_verified_status_root)
        installer_path = missing_verified_status_root / INSTALLER_PATH
        installer_path.write_text(
            installer_path.read_text(encoding="utf-8").replace(
                "        print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        try:
            check_root(missing_verified_status_root)
        except SystemExit as exc:
            assert "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing verified-status failure")

    print("LANE05_INSTALL_ZIG_POLICY_ROUTE_SELF_TEST=pass")
    print(f"LANE05_INSTALL_ZIG_POLICY_ROUTE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 bootstrap keeps the install-zig policy and sha route explicit."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    workflow_marker_count, installer_marker_count = check_root(args.root.resolve())
    print("LANE05_INSTALL_ZIG_POLICY_ROUTE=pass")
    print(f"LANE05_INSTALL_ZIG_POLICY_ROUTE_ROOT={args.root.resolve()}")
    print(f"LANE05_INSTALL_ZIG_POLICY_ROUTE_WORKFLOW_MARKER_COUNT={workflow_marker_count}")
    print(f"LANE05_INSTALL_ZIG_POLICY_ROUTE_INSTALLER_MARKER_COUNT={installer_marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
