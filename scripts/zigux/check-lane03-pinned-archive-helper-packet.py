#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
README = "scripts/zigux/README.md"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
THIRD_PARTY_README = "third_party/README.md"

REQUIRED_PATHS = (
    WORKFLOW,
    MAKEFILE,
    README,
    POLICY,
    THIRD_PARTY_README,
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
)

README_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`,",
    "`third_party/README.md`, `scripts/zigux/stage-pinned-zig-archive.py`,",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py`",
    "`scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`,",
)

MAKEFILE_LINES = (
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

WORKFLOW_LINES = tuple(f"run: {line.replace('$(PYTHON) $(PHASE2_SCRIPT_ROOT)/', 'python3 scripts/zigux/')}" for line in MAKEFILE_LINES)

WORKFLOW_STEPS = (
    "- name: Check current pinned Zig archive packet",
    "- name: Self-test current Lane 05 install-zig archive verification checker",
    "- name: Check current Lane 05 install-zig archive verification packet",
    "- name: Self-test current Zig installer helper",
    "- name: Self-test current staged pinned Zig archive helper",
    "- name: Self-test current Lane 05 stage helper contract checker",
    "- name: Check current Lane 05 stage helper contract packet",
    "- name: Self-test current Lane 05 stage helper selftest checker",
    "- name: Check current Lane 05 stage helper selftest packet",
)

HELPER_MARKERS = {
    "scripts/zigux/check-zig-toolchain.py": (
        "ZIG_TOOLCHAIN_ARCHIVE_STATUS=",
        "archive_target_scope",
        "--archive-only",
    ),
    "scripts/zigux/check-lane05-install-zig-archive-verification.py": (
        "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass",
        "INSTALL_ZIG_MARKERS",
        "LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST=pass",
    ),
    "scripts/zigux/stage-pinned-zig-archive.py": (
        "STAGE_PINNED_ZIG_ARCHIVE=pass",
        "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=",
        "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
    ),
    "scripts/zigux/check-lane05-stage-helper-contract.py": (
        "LANE05_STAGE_HELPER_CONTRACT=pass",
        "LANE05_STAGE_HELPER_MARKER_COUNT=",
        "LANE05_STAGE_HELPER_CONTRACT_SELF_TEST=pass",
    ),
    "scripts/zigux/check-lane05-stage-helper-selftest.py": (
        "LANE05_STAGE_HELPER_SELFTEST=pass",
        "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST=pass",
        "NEXT_STEP = \"- name: Self-test current Phase 2 fixdep gate checker\"",
    ),
}

POLICY_REQUIRED_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
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


def read_policy(root: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(root, POLICY))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {root / POLICY}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {root / POLICY}")
    return payload


def collect_policy_issues(policy: dict[str, object]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    archive_sha256 = policy.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        issues.append(("INVALID_POLICY_FIELD", "archive_sha256"))
        return issues

    digest = archive_sha256.get("x86_64-linux")
    if digest != "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77":
        issues.append(("INVALID_ARCHIVE_SHA256", "x86_64-linux"))

    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
        return issues

    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("INVALID_POLICY_FIELD", "channel_minimum_lockstep"))

    archive_targets = upgrade_policy.get("archive_target_scope")
    if archive_targets != ["x86_64-linux"]:
        issues.append(("INVALID_ARCHIVE_TARGET_SCOPE", json.dumps(archive_targets)))

    required_routes = upgrade_policy.get("required_make_routes")
    if required_routes != list(POLICY_REQUIRED_ROUTES):
        issues.append(("INVALID_REQUIRED_MAKE_ROUTES", json.dumps(required_routes)))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    readme = read_text(root, README)
    makefile = read_text(root, MAKEFILE)
    workflow = read_text(root, WORKFLOW)
    policy = read_policy(root)

    for marker in README_MARKERS:
        if marker not in readme:
            issues.append(("MISSING_README_MARKER", marker))

    for rel, markers in HELPER_MARKERS.items():
        text = read_text(root, rel)
        for marker in markers:
            if marker not in text:
                issues.append(("MISSING_HELPER_MARKER", f"{rel}:{marker}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in WORKFLOW_STEPS:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_STEP", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_STEP", f"{marker}:count={count}"))

    issues.extend(collect_policy_issues(policy))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("LANE03_PINNED_ARCHIVE_HELPER_PACKET=fail")
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
                "## Phase 2",
                "",
                "- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, and the other Phase 2 guards remain the shipped toolchain packet.",
                "- `.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned Zig toolchain guard explicit.",
                "- `third_party/README.md`, `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the staged repo-local archive helper packet explicit.",
                "- `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, and `zigux/tests/fixtures/phase2_cross_targets.json` are directly readable on current `master`.",
            )
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                "phase2-toolchain:",
                *[f"\t{line}" for line in MAKEFILE_LINES],
            )
        )
        + "\n",
    )
    workflow_lines = []
    for step, line in zip(WORKFLOW_STEPS, WORKFLOW_LINES):
        workflow_lines.append(f"      {step}")
        workflow_lines.append(f"        {line}")
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                *workflow_lines,
            )
        )
        + "\n",
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
        )
        + "\n",
    )
    write_text(
        root,
        THIRD_PARTY_README,
        "\n".join(
            (
                "# Zigux third-party archives",
                "- target: `x86_64-linux`",
                "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
            )
        )
        + "\n",
    )
    write_text(root, "scripts/zigux/install-zig.py", "install-zig helper\n")
    for rel, markers in HELPER_MARKERS.items():
        write_text(root, rel, "\n".join(markers) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="lane03_pinned_archive_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(root, README, read_text(root, README).replace(README_MARKERS[2], "missing marker", 1))
        assert ("MISSING_README_MARKER", README_MARKERS[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            replace_exact_line(read_text(root, MAKEFILE), MAKEFILE_LINES[4], "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/other-helper.py"),
        )
        assert ("MISSING_MAKEFILE_LINE", MAKEFILE_LINES[4]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, duplicate_exact_line(read_text(root, MAKEFILE), MAKEFILE_LINES[-1]))
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[-1]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(read_text(root, WORKFLOW), WORKFLOW_LINES[1], "        run: python3 scripts/zigux/other.py"),
        )
        assert ("MISSING_WORKFLOW_LINE", WORKFLOW_LINES[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), WORKFLOW_STEPS[-1]))
        assert ("DUPLICATE_WORKFLOW_STEP", f"{WORKFLOW_STEPS[-1]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        payload = read_policy(root)
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        write_text(root, POLICY, json.dumps(payload, indent=2) + "\n")
        assert any(code == "INVALID_REQUIRED_MAKE_ROUTES" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        write_text(root, "scripts/zigux/stage-pinned-zig-archive.py", "missing\n")
        assert any(
            code == "MISSING_HELPER_MARKER" and value.startswith("scripts/zigux/stage-pinned-zig-archive.py:")
            for code, value in collect_issues(root)
        )
        checks += 1

    print("LANE03_PINNED_ARCHIVE_HELPER_PACKET_SELF_TEST=pass")
    print(f"LANE03_PINNED_ARCHIVE_HELPER_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current pinned-archive helper packet stays aligned across the workflow, scripts root, policy, and helper surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for local validation and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"LANE03_PINNED_ARCHIVE_HELPER_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE03_PINNED_ARCHIVE_HELPER_PACKET=pass")
    print(f"LANE03_PINNED_ARCHIVE_HELPER_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"LANE03_PINNED_ARCHIVE_HELPER_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"LANE03_PINNED_ARCHIVE_HELPER_WORKFLOW_STEP_COUNT={len(WORKFLOW_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
