#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
README = "scripts/zigux/README.md"
CHECK_ZIG = "scripts/zigux/check-zig-toolchain.py"
INSTALL_ZIG = "scripts/zigux/install-zig.py"
STAGE_ARCHIVE = "scripts/zigux/stage-pinned-zig-archive.py"
LANE05_INSTALL_ARCHIVE = "scripts/zigux/check-lane05-install-zig-archive-verification.py"
LANE05_STAGE_CONTRACT = "scripts/zigux/check-lane05-stage-helper-contract.py"
LANE05_STAGE_SELFTEST = "scripts/zigux/check-lane05-stage-helper-selftest.py"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
MAKEFILE = "zigux/Makefile"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_PATHS = (
    README,
    CHECK_ZIG,
    INSTALL_ZIG,
    STAGE_ARCHIVE,
    LANE05_INSTALL_ARCHIVE,
    LANE05_STAGE_CONTRACT,
    LANE05_STAGE_SELFTEST,
    POLICY,
    MAKEFILE,
    WORKFLOW,
)

README_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`",
    "`scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py`",
)

CHECK_ZIG_MARKERS = (
    'add_search_root(root / "third_party")',
    'add_search_root(root / "agent_files")',
    'parser.add_argument("--archive-only"',
    'archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)',
    'validate_policy_archive(',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}")',
)

INSTALL_ZIG_MARKERS = (
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
)

STAGE_ARCHIVE_MARKERS = (
    "def reconstruct_archive_from_parts(",
    '"parts_glob": "part-*.b64"',
    '"--parts-dir"',
    'print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
)

POLICY_MARKERS = (
    '"channel": "0.17.0-dev.87+9b177a7d2"',
    '"x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"',
    '"phase2-toolchain"',
    '"phase2-validate"',
)

MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
)

WORKFLOW_STEP_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: make -C zigux phase2-toolchain",
)

WORKFLOW_SETUP_MARKERS = (
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_parts_dir="${repo_archive_path}.parts"',
    "python3 scripts/zigux/stage-pinned-zig-archive.py",
    '--parts-dir "$repo_archive_parts_dir"',
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org",
)


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


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line marker not found: {marker}")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    readme = read_text(root, README)
    check_zig = read_text(root, CHECK_ZIG)
    install_zig = read_text(root, INSTALL_ZIG)
    stage_archive = read_text(root, STAGE_ARCHIVE)
    policy = read_text(root, POLICY)
    makefile = read_text(root, MAKEFILE)
    workflow = read_text(root, WORKFLOW)

    for marker in README_MARKERS:
        if marker not in readme:
            issues.append(("MISSING_README_MARKER", marker))
    for marker in CHECK_ZIG_MARKERS:
        if marker not in check_zig:
            issues.append(("MISSING_CHECK_ZIG_MARKER", marker))
    for marker in INSTALL_ZIG_MARKERS:
        if marker not in install_zig:
            issues.append(("MISSING_INSTALL_ZIG_MARKER", marker))
    for marker in STAGE_ARCHIVE_MARKERS:
        if marker not in stage_archive:
            issues.append(("MISSING_STAGE_ARCHIVE_MARKER", marker))
    for marker in POLICY_MARKERS:
        if marker not in policy:
            issues.append(("MISSING_POLICY_MARKER", marker))
    for marker in WORKFLOW_SETUP_MARKERS:
        if marker not in workflow:
            issues.append(("MISSING_WORKFLOW_SETUP_MARKER", marker))

    for line in MAKEFILE_LINES:
        count = count_exact_lines(makefile, line)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", line))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{line}:count={count}"))

    for line in WORKFLOW_STEP_LINES:
        count = count_exact_lines(workflow, line)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_STEP_LINE", line))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_STEP_LINE", f"{line}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("LANE03_BOOTSTRAP_TOOLCHAIN_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        README,
        "\n".join(
            (
                "# scripts/zigux",
                "",
                "This directory holds shipped Zigux validation helpers and compact reminder surfaces.",
                "",
                "- `scripts/zigux/check-zig-toolchain.py`",
                "- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`",
                "- `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`",
                "- `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py`",
            )
        )
        + "\n",
    )
    write_text(
        root,
        CHECK_ZIG,
        "\n".join(
            (
                'def add_search_root(path):',
                '    add_search_root(root / "third_party")',
                '    add_search_root(root / "agent_files")',
                'def validate_policy_archive():',
                '    return None',
                'def main():',
                '    parser.add_argument("--archive-only", action="store_true")',
                '    archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)',
                '    validate_policy_archive(',
                '    print(f"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}")',
            )
        )
        + "\n",
    )
    write_text(
        root,
        INSTALL_ZIG,
        "\n".join(
            (
                "from pathlib import Path",
                "TOOLCHAIN_POLICY = Path('scripts/zigux/zig-toolchain-policy.json')",
                "target_key = 'x86_64-linux'",
                "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
                "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
                "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
                "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
            )
        )
        + "\n",
    )
    write_text(
        root,
        STAGE_ARCHIVE,
        "\n".join(
            (
                "def reconstruct_archive_from_parts():",
                '    manifest = {"parts_glob": "part-*.b64"}',
                '    parser.add_argument("--parts-dir")',
                '    print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")',
            )
        )
        + "\n",
    )
    write_text(root, LANE05_INSTALL_ARCHIVE, "present\n")
    write_text(root, LANE05_STAGE_CONTRACT, "present\n")
    write_text(root, LANE05_STAGE_SELFTEST, "present\n")
    write_text(
        root,
        POLICY,
        "\n".join(
            (
                "{",
                '  "channel": "0.17.0-dev.87+9b177a7d2",',
                '  "archive_sha256": {',
                '    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"',
                "  },",
                '  "upgrade_policy": {',
                '    "required_make_routes": ["phase2-toolchain", "phase2-validate"]',
                "  }",
                "}",
            )
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        ".PHONY: phase2-toolchain\n\nphase2-toolchain:\n\t"
        + "\n\t".join(MAKEFILE_LINES)
        + "\n",
    )
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
                'repo_archive_parts_dir="${repo_archive_path}.parts"',
                "python3 scripts/zigux/stage-pinned-zig-archive.py",
                '--parts-dir "$repo_archive_parts_dir"',
                'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
                "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org",
                *WORKFLOW_STEP_LINES,
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="lane03_bootstrap_toolchain_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            README,
            replace_once(read_text(root, README), README_MARKERS[2], "`scripts/zigux/stage-pinned-zig-archive.py`"),
        )
        assert ("MISSING_README_MARKER", README_MARKERS[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            CHECK_ZIG,
            replace_once(read_text(root, CHECK_ZIG), CHECK_ZIG_MARKERS[1], ""),
        )
        assert ("MISSING_CHECK_ZIG_MARKER", CHECK_ZIG_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            duplicate_exact_line(read_text(root, MAKEFILE), MAKEFILE_LINES[0]),
        )
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[0]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_once(read_text(root, WORKFLOW), WORKFLOW_STEP_LINES[-1] + "\n", ""),
        )
        assert ("MISSING_WORKFLOW_STEP_LINE", WORKFLOW_STEP_LINES[-1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_once(read_text(root, WORKFLOW), WORKFLOW_SETUP_MARKERS[4], ""),
        )
        assert ("MISSING_WORKFLOW_SETUP_MARKER", WORKFLOW_SETUP_MARKERS[4]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            POLICY,
            replace_once(read_text(root, POLICY), POLICY_MARKERS[1], '"x86_64-linux": "short"'),
        )
        assert ("MISSING_POLICY_MARKER", POLICY_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        (root / LANE05_STAGE_SELFTEST).unlink()
        assert ("MISSING_REQUIRED_PATH", LANE05_STAGE_SELFTEST) in collect_issues(root)
        checks += 1

    print("LANE03_BOOTSTRAP_TOOLCHAIN_PACKET_SELF_TEST=pass")
    print(f"LANE03_BOOTSTRAP_TOOLCHAIN_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the live Lane 03 bootstrap toolchain packet stays aligned across README, scripts, policy, Makefile, and workflow surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root and exit")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"LANE03_BOOTSTRAP_TOOLCHAIN_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE03_BOOTSTRAP_TOOLCHAIN_PACKET=pass")
    print(f"LANE03_BOOTSTRAP_TOOLCHAIN_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"LANE03_BOOTSTRAP_TOOLCHAIN_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"LANE03_BOOTSTRAP_TOOLCHAIN_WORKFLOW_STEP_COUNT={len(WORKFLOW_STEP_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
