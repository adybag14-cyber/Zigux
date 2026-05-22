#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
INSTALL_ZIG = Path("scripts/zigux/install-zig.py")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
ARCHIVE_VERIFICATION_CHECKER = Path("scripts/zigux/check-lane05-install-zig-archive-verification.py")

REQUIRED_FILES = (
    WORKFLOW,
    MAKEFILE,
    INSTALL_ZIG,
    TOOLCHAIN_POLICY,
    ARCHIVE_VERIFICATION_CHECKER,
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
)

REQUIRED_MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
)

REQUIRED_CHECKER_MARKERS = (
    'INSTALL_ZIG = Path("scripts/zigux/install-zig.py")',
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    'print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass")',
    'print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST=pass")',
)

REQUIRED_INSTALL_ZIG_MARKERS = (
    "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def load_policy(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


def collect_policy_issues(policy: dict[str, object]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    archive_sha256 = policy.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        issues.append(("INVALID_POLICY_FIELD", "archive_sha256"))
        return issues

    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
        return issues

    targets = upgrade_policy.get("archive_target_scope")
    if not isinstance(targets, list) or not targets:
        issues.append(("INVALID_POLICY_FIELD", "archive_target_scope"))
        return issues
    if len(targets) != 1:
        issues.append(("UNEXPECTED_ARCHIVE_TARGET_COUNT", str(len(targets))))

    for target in targets:
        if not isinstance(target, str) or not target:
            issues.append(("INVALID_ARCHIVE_TARGET", repr(target)))
            continue
        digest = archive_sha256.get(target)
        if not isinstance(digest, str) or len(digest) != 64:
            issues.append(("INVALID_ARCHIVE_SHA256", target))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    workflow_text = read_text(root / WORKFLOW)
    makefile_text = read_text(root / MAKEFILE)
    checker_text = read_text(root / ARCHIVE_VERIFICATION_CHECKER)
    install_text = read_text(root / INSTALL_ZIG)
    policy = load_policy(root / TOOLCHAIN_POLICY)

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_line(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_line(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_CHECKER_MARKERS:
        count = checker_text.count(marker)
        if count == 0:
            issues.append(("MISSING_CHECKER_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CHECKER_MARKER", f"{marker}:count={count}"))

    for marker in REQUIRED_INSTALL_ZIG_MARKERS:
        count = install_text.count(marker)
        if count == 0:
            issues.append(("MISSING_INSTALL_ZIG_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_INSTALL_ZIG_MARKER", f"{marker}:count={count}"))

    issues.extend(collect_policy_issues(policy))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root / WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                *REQUIRED_WORKFLOW_LINES,
            )
        )
        + "\n",
    )
    write_text(
        root / MAKEFILE,
        "\n".join(
            (
                "PYTHON ?= python3",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "",
                "phase2-toolchain:",
                f"\t{REQUIRED_MAKEFILE_LINES[0]}",
                f"\t{REQUIRED_MAKEFILE_LINES[1]}",
            )
        )
        + "\n",
    )
    write_text(
        root / INSTALL_ZIG,
        "\n".join(
            (
                "from pathlib import Path",
                "",
                "TOOLCHAIN_POLICY = Path('scripts/zigux/zig-toolchain-policy.json')",
                "",
                "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
                "    return '3' * 64",
                "",
                "def verify_archive_sha256(path, expected):",
                "    return expected",
                "",
                "def main() -> int:",
                "    target_key = 'x86_64-linux'",
                "    archive_path = Path('archive.tar.xz')",
                "    expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
                "    if expected_archive_sha256 is not None:",
                "        actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
                "        print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
                "        print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
                "    else:",
                "        print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
                "    return 0",
            )
        )
        + "\n",
    )
    write_text(
        root / TOOLCHAIN_POLICY,
        json.dumps(
            {
                "channel": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {"archive_target_scope": ["x86_64-linux"]},
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / ARCHIVE_VERIFICATION_CHECKER,
        "\n".join(
            (
                'INSTALL_ZIG = Path("scripts/zigux/install-zig.py")',
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                'print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass")',
                'print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST=pass")',
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 6

    with tempfile.TemporaryDirectory(prefix="phase2_install_archive_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW
        workflow_path.write_text(
            replace_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                REQUIRED_WORKFLOW_LINES[0],
                "run: python3 scripts/zigux/other.py --self-test",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        makefile_path = root / MAKEFILE
        makefile_path.write_text(
            replace_exact_line(
                makefile_path.read_text(encoding="utf-8"),
                REQUIRED_MAKEFILE_LINES[1],
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/other.py",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[1]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        checker_path = root / ARCHIVE_VERIFICATION_CHECKER
        checker_path.write_text(
            checker_path.read_text(encoding="utf-8").replace(
                'print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass")', "", 1
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_CHECKER_MARKER",
            'print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass")',
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        install_path = root / INSTALL_ZIG
        install_path.write_text(
            install_path.read_text(encoding="utf-8").replace(
                "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)", "", 1
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_INSTALL_ZIG_MARKER",
            "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        policy_path = root / TOOLCHAIN_POLICY
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["archive_sha256"] = {}
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_FIELD", "archive_sha256") in collect_issues(root)
        checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET_SELF_TEST=pass")
    print(f"PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 install-zig archive-verification packet explicit across the current workflow and make route."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like sample repository root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET=pass")
    print(f"PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_INSTALL_ZIG_ARCHIVE_VERIFICATION_PACKET_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
