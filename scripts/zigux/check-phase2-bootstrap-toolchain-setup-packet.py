#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
SCRIPTS_README = "scripts/zigux/README.md"
THIRD_PARTY_README = "third_party/README.md"
POLICY = "scripts/zigux/zig-toolchain-policy.json"

REQUIRED_PATHS = (
    WORKFLOW,
    MAKEFILE,
    SCRIPTS_README,
    THIRD_PARTY_README,
    POLICY,
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`",
    "`.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`third_party/README.md`, `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
)

THIRD_PARTY_README_MARKERS = (
    "- target: `x86_64-linux`",
    "- channel: `0.17.0-dev.87+9b177a7d2`",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the archive-verification, staged-helper contract, and staged-helper self-test packet explicit beside that same local-first archive path.",
)

MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
)

WORKFLOW_SETUP_MARKERS = (
    "- name: Setup pinned Zig toolchain",
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'targets = policy["upgrade_policy"]["archive_target_scope"]',
    'filename = f"zig-{target}-{channel}.tar.xz"',
    'url = f"https://ziglang.org/builds/{filename}"',
    'archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_parts_dir="${repo_archive_path}.parts"',
    'try_local_archive() {',
    'python3 scripts/zigux/stage-pinned-zig-archive.py                 --root "$GITHUB_WORKSPACE"                 --parts-dir "$repo_archive_parts_dir" || return 1',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"',
    'if try_download "$ZIGUX_ZIG_URL"; then',
    "echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
)

WORKFLOW_RUN_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
)

POLICY_REQUIRED_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)

HELPER_MARKERS = {
    "scripts/zigux/check-zig-toolchain.py": (
        "ZIG_TOOLCHAIN_POLICY_STATUS=present",
        "ZIG_TOOLCHAIN_ARCHIVE_STATUS=present",
        "archive_name_matches_policy",
        "describe_missing_archive",
    ),
    "scripts/zigux/install-zig.py": (
        "load_policy_archive_sha256",
        "verify_archive_sha256",
        "copy_url_to_file(tarball_url, archive_path)",
        "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified",
    ),
    "scripts/zigux/stage-pinned-zig-archive.py": (
        "STAGE_PINNED_ZIG_ARCHIVE=pass",
        "reconstruct_archive_from_parts",
        "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=",
        "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
    ),
    "scripts/zigux/check-lane05-local-first-archive-workflow.py": (
        "LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW=pass",
        "WORKFLOW_REQUIRED_MARKERS",
    ),
    "scripts/zigux/check-lane05-local-archive-readme.py": (
        "LANE05_LOCAL_ARCHIVE_README=pass",
        "README_REQUIRED_MARKERS",
    ),
    "scripts/zigux/check-lane05-install-zig-archive-verification.py": (
        "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass",
        "INSTALL_ZIG_MARKERS",
    ),
    "scripts/zigux/check-lane05-stage-helper-contract.py": (
        "LANE05_STAGE_HELPER_CONTRACT=pass",
        "LANE05_STAGE_HELPER_MARKER_COUNT=",
    ),
    "scripts/zigux/check-lane05-stage-helper-selftest.py": (
        "LANE05_STAGE_HELPER_SELFTEST=pass",
        "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST=pass",
    ),
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


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker text not found: {marker}")
    return text.replace(marker, replacement, 1)


def collect_policy_issues(payload: dict[str, object]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if payload.get("phase") != "Phase 2":
        issues.append(("INVALID_POLICY_FIELD", "phase"))
    if payload.get("channel") != "0.17.0-dev.87+9b177a7d2":
        issues.append(("INVALID_POLICY_FIELD", "channel"))
    if payload.get("minimum_version") != "0.17.0-dev.87+9b177a7d2":
        issues.append(("INVALID_POLICY_FIELD", "minimum_version"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_POLICY_FIELD", "archive_sha256"))
    else:
        digest = archive_sha256.get("x86_64-linux")
        if digest != "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77":
            issues.append(("INVALID_ARCHIVE_SHA256", "x86_64-linux"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
        return issues

    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("INVALID_POLICY_FIELD", "channel_minimum_lockstep"))

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if archive_target_scope != ["x86_64-linux"]:
        issues.append(("INVALID_ARCHIVE_TARGET_SCOPE", json.dumps(archive_target_scope)))

    required_routes = upgrade_policy.get("required_make_routes")
    if required_routes != list(POLICY_REQUIRED_ROUTES):
        issues.append(("INVALID_REQUIRED_MAKE_ROUTES", json.dumps(required_routes)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    scripts_readme = read_text(root, SCRIPTS_README)
    third_party_readme = read_text(root, THIRD_PARTY_README)
    makefile = read_text(root, MAKEFILE)
    workflow = read_text(root, WORKFLOW)
    policy = json.loads(read_text(root, POLICY))

    for marker in SCRIPTS_README_MARKERS:
        if marker not in scripts_readme:
            issues.append(("MISSING_SCRIPTS_README_MARKER", marker))

    for marker in THIRD_PARTY_README_MARKERS:
        if marker not in third_party_readme:
            issues.append(("MISSING_THIRD_PARTY_README_MARKER", marker))

    for rel, markers in HELPER_MARKERS.items():
        text = read_text(root, rel)
        for marker in markers:
            if marker not in text:
                issues.append(("MISSING_HELPER_MARKER", f"{rel}:{marker}"))

    phase2_toolchain_block = []
    capture = False
    for line in makefile.splitlines():
        stripped = line.rstrip()
        if stripped == "phase2-toolchain:":
            capture = True
            continue
        if capture:
            if line.startswith("\t"):
                phase2_toolchain_block.append(line.strip())
                continue
            if stripped and not line.startswith((" ", "\t")):
                break

    if phase2_toolchain_block != list(MAKEFILE_LINES):
        issues.append(("PHASE2_TOOLCHAIN_BLOCK_MISMATCH", f"count={len(phase2_toolchain_block)}"))

    for marker in MAKEFILE_LINES:
        count = phase2_toolchain_block.count(marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in WORKFLOW_SETUP_MARKERS:
        if marker not in workflow:
            issues.append(("MISSING_WORKFLOW_SETUP_MARKER", marker))

    for marker in WORKFLOW_RUN_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_RUN_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_RUN_LINE", f"{marker}:count={count}"))

    issues.extend(collect_policy_issues(policy))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        if rel in {WORKFLOW, MAKEFILE, SCRIPTS_README, THIRD_PARTY_README, POLICY}:
            continue
        if rel == "scripts/zigux/check-zig-toolchain.py":
            write_text(
                root,
                rel,
                "\n".join((
                    "ZIG_TOOLCHAIN_POLICY_STATUS=present",
                    "ZIG_TOOLCHAIN_ARCHIVE_STATUS=present",
                    "archive_name_matches_policy",
                    "describe_missing_archive",
                )) + "\n",
            )
            continue
        if rel == "scripts/zigux/install-zig.py":
            write_text(
                root,
                rel,
                "\n".join((
                    "load_policy_archive_sha256",
                    "verify_archive_sha256",
                    "copy_url_to_file(tarball_url, archive_path)",
                    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified",
                )) + "\n",
            )
            continue
        if rel == "scripts/zigux/stage-pinned-zig-archive.py":
            write_text(
                root,
                rel,
                "\n".join((
                    "STAGE_PINNED_ZIG_ARCHIVE=pass",
                    "reconstruct_archive_from_parts",
                    "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=",
                    "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
                )) + "\n",
            )
            continue
        if rel == "scripts/zigux/check-lane05-local-first-archive-workflow.py":
            write_text(root, rel, "LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW=pass\nWORKFLOW_REQUIRED_MARKERS\n")
            continue
        if rel == "scripts/zigux/check-lane05-local-archive-readme.py":
            write_text(root, rel, "LANE05_LOCAL_ARCHIVE_README=pass\nREADME_REQUIRED_MARKERS\n")
            continue
        if rel == "scripts/zigux/check-lane05-install-zig-archive-verification.py":
            write_text(root, rel, "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass\nINSTALL_ZIG_MARKERS\n")
            continue
        if rel == "scripts/zigux/check-lane05-stage-helper-contract.py":
            write_text(root, rel, "LANE05_STAGE_HELPER_CONTRACT=pass\nLANE05_STAGE_HELPER_MARKER_COUNT=\n")
            continue
        if rel == "scripts/zigux/check-lane05-stage-helper-selftest.py":
            write_text(root, rel, "LANE05_STAGE_HELPER_SELFTEST=pass\nLANE05_STAGE_HELPER_SELFTEST_SELF_TEST=pass\n")
            continue
        write_text(root, rel, "present\n")

    write_text(root, SCRIPTS_README, "\n".join(("# scripts/zigux", "", *SCRIPTS_README_MARKERS)) + "\n")
    write_text(root, THIRD_PARTY_README, "\n".join(("# Zigux third-party archives", "", *THIRD_PARTY_README_MARKERS)) + "\n")
    write_text(
        root,
        MAKEFILE,
        "\n".join((
            "PYTHON ?= python3",
            "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
            "",
            "phase2-toolchain:",
            *[f"\t{line}" for line in MAKEFILE_LINES],
            "",
            "phase2-tools:",
            "\t@true",
        )) + "\n",
    )
    write_text(
        root,
        WORKFLOW,
        "\n".join((
            "name: zigux-bootstrap",
            "jobs:",
            "  bootstrap:",
            "    steps:",
            "      - name: Setup pinned Zig toolchain",
            '        run: |',
            '          policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
            '          targets = policy["upgrade_policy"]["archive_target_scope"]',
            '          filename = f"zig-{target}-{channel}.tar.xz"',
            '          url = f"https://ziglang.org/builds/{filename}"',
            '          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
            '          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
            '          repo_archive_parts_dir="${repo_archive_path}.parts"',
            '          try_local_archive() {',
            '            python3 scripts/zigux/stage-pinned-zig-archive.py                 --root "$GITHUB_WORKSPACE"                 --parts-dir "$repo_archive_parts_dir" || return 1',
            '            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
            '              return 0',
            '            fi',
            '          }',
            '          curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"',
            '          if try_download "$ZIGUX_ZIG_URL"; then',
            '            download_success=1',
            '          fi',
            "          echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
            *[f"      - name: step-{index}" if line.startswith('run:') else line for index, line in enumerate(())],
            *[f"        {line}" if line.startswith('run:') else line for line in WORKFLOW_RUN_LINES],
        )) + "\n",
    )
    write_text(
        root,
        POLICY,
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
                    "required_make_routes": list(POLICY_REQUIRED_ROUTES),
                },
            },
            indent=2,
        ) + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="lane03_setup_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(root, SCRIPTS_README, read_text(root, SCRIPTS_README).replace(SCRIPTS_README_MARKERS[1], "missing", 1))
        assert ("MISSING_SCRIPTS_README_MARKER", SCRIPTS_README_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            THIRD_PARTY_README,
            read_text(root, THIRD_PARTY_README).replace(THIRD_PARTY_README_MARKERS[-1], "missing", 1),
        )
        assert ("MISSING_THIRD_PARTY_README_MARKER", THIRD_PARTY_README_MARKERS[-1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, replace_exact_line(read_text(root, MAKEFILE), MAKEFILE_LINES[9], "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --wrong"))
        issues = collect_issues(root)
        assert ("PHASE2_TOOLCHAIN_BLOCK_MISMATCH", f"count={len(MAKEFILE_LINES)}") in issues
        assert ("MISSING_MAKEFILE_LINE", MAKEFILE_LINES[9]) in issues
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, duplicate_exact_line(read_text(root, MAKEFILE), MAKEFILE_LINES[-1]))
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[-1]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, replace_once(read_text(root, WORKFLOW), WORKFLOW_SETUP_MARKERS[-1], "echo missing"))
        assert ("MISSING_WORKFLOW_SETUP_MARKER", WORKFLOW_SETUP_MARKERS[-1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), WORKFLOW_RUN_LINES[0], "run: python3 scripts/zigux/other.py"))
        assert ("MISSING_WORKFLOW_RUN_LINE", WORKFLOW_RUN_LINES[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), WORKFLOW_RUN_LINES[-1]))
        assert ("DUPLICATE_WORKFLOW_RUN_LINE", f"{WORKFLOW_RUN_LINES[-1]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy = json.loads(read_text(root, POLICY))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        write_text(root, POLICY, json.dumps(policy, indent=2) + "\n")
        assert any(code == "INVALID_REQUIRED_MAKE_ROUTES" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        write_text(root, "scripts/zigux/install-zig.py", "missing\n")
        assert any(
            code == "MISSING_HELPER_MARKER" and value.startswith("scripts/zigux/install-zig.py:")
            for code, value in collect_issues(root)
        )
        checks += 1

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the pinned bootstrap toolchain setup packet stays aligned across workflow, policy, docs, and helper surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="write a focused sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print("PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_PACKET_SAMPLE_ROOT=pass")
        print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_PACKET_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_SETUP_WORKFLOW_LINE_COUNT={len(WORKFLOW_RUN_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
