#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_PATHS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    "third_party/README.md",
    WORKFLOW,
)

SCRIPTS_README_MARKERS = (
    "`check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-docs-shared-reminder.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-toolchain-pinning.py`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/check-phase2-required-make-routes.py` remain the shipped Phase 2 toolchain",
    "`third_party/README.md`, `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the staged repo-local archive helper, contract, and self-test packet explicit from the scripts root beside that same shipped Lane 05 local-first archive path",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`",
)

THIRD_PARTY_README_MARKERS = (
    "# Zigux third-party archives",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
    "`scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/",
    "`scripts/zigux/install-zig.py`",
)

CHECK_ZIG_TOOLCHAIN_MARKERS = (
    "POLICY_KEYS = {\"phase\", \"channel\", \"minimum_version\", \"archive_sha256\", \"upgrade_policy\"}",
    "UPGRADE_POLICY_KEYS = {\"channel_minimum_lockstep\", \"archive_target_scope\", \"required_make_routes\"}",
    "def load_policy(policy_path: Path = TOOLCHAIN_POLICY) -> dict[str, object] | None:",
    "def load_min_version(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_MIN_VERSION) -> str:",
    "def load_pinned_channel(policy_path: Path = TOOLCHAIN_POLICY) -> str | None:",
    "print(f\"ZIG_TOOLCHAIN_POLICY_REQUIRED_MAKE_ROUTE_COUNT={len(required_make_routes)}\")",
    "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target}\")",
)

INSTALL_ZIG_MARKERS = (
    "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
)

STAGE_HELPER_MARKERS = (
    "TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")",
    "THIRD_PARTY_DIR = Path(\"third_party\")",
    "EXPECTED_ARCHIVE_SIZES = {",
    "def validate_source_archive(source: Path, *, expected_size: int, expected_sha: str) -> str:",
    "def reconstruct_archive_from_parts(",
    "print(f\"STAGE_PINNED_ZIG_ARCHIVE_TARGET={contract['target']}\")",
    "print(f\"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={contract['sha256']}\")",
)

POLICY_MARKERS = (
    "\"phase2-toolchain\"",
    "\"phase2-tools\"",
    "\"phase2-kconfig\"",
    "\"phase2-cross\"",
    "\"phase2-genksyms\"",
    "\"phase2-fixdep\"",
    "\"phase2-validate\"",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
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

REQUIRED_WORKFLOW_LINES = (
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
)

ORDERED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
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


def find_exact_line_index(text: str, marker: str) -> int:
    for index, line in enumerate(text.splitlines()):
        if line.strip() == marker:
            return index
    return -1


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    if issues:
        return issues

    scripts_readme = read_text(root, "scripts/zigux/README.md")
    third_party_readme = read_text(root, "third_party/README.md")
    check_zig = read_text(root, "scripts/zigux/check-zig-toolchain.py")
    install_zig = read_text(root, "scripts/zigux/install-zig.py")
    stage_helper = read_text(root, "scripts/zigux/stage-pinned-zig-archive.py")
    policy = read_text(root, "scripts/zigux/zig-toolchain-policy.json")
    makefile = read_text(root, "zigux/Makefile")
    workflow = read_text(root, WORKFLOW)

    for marker in SCRIPTS_README_MARKERS:
        if marker not in scripts_readme:
            issues.append(("MISSING_SCRIPTS_README_MARKER", marker))
    for marker in THIRD_PARTY_README_MARKERS:
        if marker not in third_party_readme:
            issues.append(("MISSING_THIRD_PARTY_README_MARKER", marker))
    for marker in CHECK_ZIG_TOOLCHAIN_MARKERS:
        if marker not in check_zig:
            issues.append(("MISSING_TOOLCHAIN_CHECKER_MARKER", marker))
    for marker in INSTALL_ZIG_MARKERS:
        if marker not in install_zig:
            issues.append(("MISSING_INSTALL_HELPER_MARKER", marker))
    for marker in STAGE_HELPER_MARKERS:
        if marker not in stage_helper:
            issues.append(("MISSING_STAGE_HELPER_MARKER", marker))
    for marker in POLICY_MARKERS:
        if marker not in policy:
            issues.append(("MISSING_POLICY_MARKER", marker))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    ordered_positions: list[tuple[str, int]] = []
    for marker in ORDERED_WORKFLOW_LINES:
        index = find_exact_line_index(workflow, marker)
        if index == -1:
            continue
        ordered_positions.append((marker, index))
    for earlier, later in zip(ordered_positions, ordered_positions[1:]):
        if earlier[1] >= later[1]:
            issues.append(("WORKFLOW_ORDER_MISMATCH", f"{earlier[0]} -> {later[0]}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("LANE03_PINNED_TOOLCHAIN_SUPPORT_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    policy_payload = {
        "phase": "Phase 2",
        "channel": "0.17.0-dev.87+9b177a7d2",
        "minimum_version": "0.17.0-dev.87+9b177a7d2",
        "archive_sha256": {
            "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
        },
        "upgrade_policy": {
            "channel_minimum_lockstep": True,
            "archive_target_scope": ["x86_64-linux"],
            "required_make_routes": [
                "phase2-toolchain",
                "phase2-tools",
                "phase2-kconfig",
                "phase2-cross",
                "phase2-genksyms",
                "phase2-fixdep",
                "phase2-validate",
            ],
        },
    }

    write_text(root, "scripts/zigux/zig-toolchain-policy.json", json.dumps(policy_payload, indent=2) + "\n")
    write_text(
        root,
        "scripts/zigux/check-zig-toolchain.py",
        "\n".join(
            (
                'POLICY_KEYS = {"phase", "channel", "minimum_version", "archive_sha256", "upgrade_policy"}',
                'UPGRADE_POLICY_KEYS = {"channel_minimum_lockstep", "archive_target_scope", "required_make_routes"}',
                "FALLBACK_MIN_VERSION = \"0.16.0\"",
                "def load_policy(policy_path: Path = TOOLCHAIN_POLICY) -> dict[str, object] | None:",
                "    return None",
                "def load_min_version(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_MIN_VERSION) -> str:",
                "    return fallback",
                "def load_pinned_channel(policy_path: Path = TOOLCHAIN_POLICY) -> str | None:",
                "    return None",
                "print(f\"ZIG_TOOLCHAIN_POLICY_REQUIRED_MAKE_ROUTE_COUNT={len(required_make_routes)}\")",
                "print(f\"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target}\")",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "scripts/zigux/install-zig.py",
        "\n".join(
            (
                "from pathlib import Path",
                "TOOLCHAIN_POLICY = Path('scripts/zigux/zig-toolchain-policy.json')",
                "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
                "    return None",
                "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
                "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
                "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
                "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "scripts/zigux/stage-pinned-zig-archive.py",
        "\n".join(
            (
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                'THIRD_PARTY_DIR = Path("third_party")',
                "EXPECTED_ARCHIVE_SIZES = {",
                '    "x86_64-linux": 58159088,',
                "}",
                "def validate_source_archive(source: Path, *, expected_size: int, expected_sha: str) -> str:",
                "    return expected_sha",
                "def reconstruct_archive_from_parts(",
                "    parts_dir: Path,",
                ") -> str:",
                "    return ''",
                "print(f\"STAGE_PINNED_ZIG_ARCHIVE_TARGET={contract['target']}\")",
                "print(f\"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={contract['sha256']}\")",
            )
        )
        + "\n",
    )
    write_text(root, "scripts/zigux/check-lane05-install-zig-archive-verification.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-stage-helper-contract.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-stage-helper-selftest.py", "present\n")
    write_text(
        root,
        "scripts/zigux/README.md",
        "\n".join(
            (
                "# scripts/zigux",
                "",
                "## Phase 2",
                "",
                SCRIPTS_README_MARKERS[0],
                SCRIPTS_README_MARKERS[1],
                SCRIPTS_README_MARKERS[2],
            )
        )
        + "\n",
    )
    write_text(
        root,
        "third_party/README.md",
        "\n".join(
            (
                THIRD_PARTY_README_MARKERS[0],
                THIRD_PARTY_README_MARKERS[1],
                THIRD_PARTY_README_MARKERS[2],
                THIRD_PARTY_README_MARKERS[3],
            )
        )
        + "\n",
    )
    write_text(
        root,
        "zigux/Makefile",
        "\n".join(REQUIRED_MAKEFILE_LINES) + "\n",
    )
    write_text(
        root,
        WORKFLOW,
        "\n".join(f"      {line}" for line in REQUIRED_WORKFLOW_LINES + ("run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",))
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane03_pinned_toolchain_support_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        case_count += 1

        build_sample_root(root)
        (root / "scripts/zigux/stage-pinned-zig-archive.py").unlink()
        issues = collect_issues(root)
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/stage-pinned-zig-archive.py") in issues
        case_count += 1

        build_sample_root(root)
        readme_path = root / "scripts/zigux/README.md"
        readme_path.write_text(readme_path.read_text(encoding="utf-8").replace(SCRIPTS_README_MARKERS[1], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_SCRIPTS_README_MARKER", SCRIPTS_README_MARKERS[1]) in issues
        case_count += 1

        build_sample_root(root)
        policy_path = root / "scripts/zigux/zig-toolchain-policy.json"
        policy_path.write_text(policy_path.read_text(encoding="utf-8").replace('"phase2-fixdep"', '"phase2-fixdep-typo"', 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_POLICY_MARKER", '"phase2-fixdep"') in issues
        case_count += 1

        build_sample_root(root)
        makefile_path = root / "zigux/Makefile"
        broken_makefile = replace_exact_line(
            makefile_path.read_text(encoding="utf-8"),
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract-typo.py",
        )
        makefile_path.write_text(broken_makefile, encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_LINE", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py") in issues
        case_count += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW
        broken_workflow = duplicate_exact_line(
            workflow_path.read_text(encoding="utf-8"),
            "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
        )
        workflow_path.write_text(broken_workflow, encoding="utf-8")
        issues = collect_issues(root)
        assert (
            "DUPLICATE_WORKFLOW_LINE",
            "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py:count=2",
        ) in issues
        case_count += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW
        reordered_workflow = workflow_path.read_text(encoding="utf-8").replace(
            "      run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test\n"
            "      run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py\n",
            "      run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py\n"
            "      run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test\n",
            1,
        )
        workflow_path.write_text(reordered_workflow, encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "WORKFLOW_ORDER_MISMATCH" for code, _ in issues)
        case_count += 1

    print("LANE03_PINNED_TOOLCHAIN_SUPPORT_PACKET_SELF_TEST=pass")
    print(f"LANE03_PINNED_TOOLCHAIN_SUPPORT_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> int:
    build_sample_root(root)
    print(f"LANE03_PINNED_TOOLCHAIN_SUPPORT_PACKET_SAMPLE_ROOT={root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current staged pinned-Zig support packet stays aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate",
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("LANE03_PINNED_TOOLCHAIN_SUPPORT_PACKET=pass")
    print(f"LANE03_PINNED_TOOLCHAIN_SUPPORT_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"LANE03_PINNED_TOOLCHAIN_SUPPORT_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"LANE03_PINNED_TOOLCHAIN_SUPPORT_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
