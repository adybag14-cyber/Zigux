#!/usr/bin/env python3
"""Guard the policy-driven pinned Zig bootstrap setup packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
NOTES = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
THIRD_PARTY_README = "third_party/README.md"
CHECK_ZIG_TOOLCHAIN = "scripts/zigux/check-zig-toolchain.py"
INSTALL_ZIG = "scripts/zigux/install-zig.py"
STAGE_ARCHIVE = "scripts/zigux/stage-pinned-zig-archive.py"

REQUIRED_PATHS = (
    WORKFLOW,
    POLICY,
    NOTES,
    THIRD_PARTY_README,
    CHECK_ZIG_TOOLCHAIN,
    INSTALL_ZIG,
    STAGE_ARCHIVE,
)

WORKFLOW_MARKERS = (
    "- name: Setup Python",
    "- name: Setup pinned Zig toolchain",
    '- name: Compile current scripts',
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'filename = f"zig-{target}-{channel}.tar.xz"',
    'url = f"https://ziglang.org/builds/{filename}"',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'mirror_file=".zig-toolchain/community-mirrors.txt"',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if try_download "$ZIGUX_ZIG_URL"; then',
    "echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
)

ORDERED_WORKFLOW_LINES = (
    "- name: Setup Python",
    "- name: Setup pinned Zig toolchain",
    "- name: Compile current scripts",
    "- name: Self-test current Zig toolchain checker",
    "- name: Check current Zig toolchain policy packet",
    "- name: Check current pinned Zig archive packet",
    "- name: Self-test current Zig installer helper",
    "- name: Self-test current staged pinned Zig archive helper",
    "- name: Self-test current Phase 2 toolchain pinning checker",
)

WORKFLOW_RUN_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
)

NOTES_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.",
    "tries `community-mirrors.txt` before the direct Zig download URL",
    "reruns `python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"` inside each install attempt",
    "`scripts/zigux/install-zig.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are directly readable on current `master`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`",
)

EXPECTED_POLICY_PHASE = "Phase 2"
EXPECTED_REQUIRED_ROUTES = ("phase2-toolchain", "phase2-validate", "phase2-cross")
EXPECTED_SELF_TEST_CASE_COUNT = 12


def resolve(root: Path, rel: str) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_order_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    cursor = -1
    for marker in markers:
        index = text.find(marker)
        if index == -1:
            issues.append((code, marker))
            continue
        if index <= cursor:
            issues.append((code, marker))
        cursor = index
    return issues


def load_policy(root: Path) -> dict[str, object]:
    payload = json.loads(read_text(resolve(root, POLICY)))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {resolve(root, POLICY)}: expected object")
    return payload


def validate_policy(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = load_policy(root)
    phase = payload.get("phase")
    channel = payload.get("channel")
    minimum_version = payload.get("minimum_version")
    upgrade_policy = payload.get("upgrade_policy")
    archive_sha256 = payload.get("archive_sha256")

    if phase != EXPECTED_POLICY_PHASE:
        issues.append(("POLICY_PHASE_MISMATCH", repr(phase)))
    if not isinstance(channel, str) or not channel.strip():
        issues.append(("POLICY_CHANNEL_INVALID", repr(channel)))
    if minimum_version != channel:
        issues.append(("POLICY_MINIMUM_VERSION_MISMATCH", repr(minimum_version)))
    if not isinstance(upgrade_policy, dict):
        issues.append(("POLICY_UPGRADE_POLICY_INVALID", repr(upgrade_policy)))
        return issues
    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("POLICY_LOCKSTEP_MISMATCH", repr(upgrade_policy.get("channel_minimum_lockstep"))))
    if upgrade_policy.get("required_make_routes") != list(EXPECTED_REQUIRED_ROUTES):
        issues.append(("POLICY_REQUIRED_ROUTES_MISMATCH", repr(upgrade_policy.get("required_make_routes"))))
    archive_targets = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_targets, list) or len(archive_targets) != 1:
        issues.append(("POLICY_ARCHIVE_TARGET_SCOPE_INVALID", repr(archive_targets)))
        return issues
    target = archive_targets[0]
    if not isinstance(target, str) or not target.strip():
        issues.append(("POLICY_ARCHIVE_TARGET_INVALID", repr(target)))
        return issues
    if not isinstance(archive_sha256, dict) or target not in archive_sha256:
        issues.append(("POLICY_ARCHIVE_SHA_MISSING", str(target)))
    return issues


def third_party_markers(channel: str, target: str) -> tuple[str, ...]:
    filename = f"zig-{target}-{channel}.tar.xz"
    return (
        f"`third_party/{filename}`",
        f"`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/{filename} --archive-target {target}`",
        "duplicate-copy boundary",
        "`community-mirrors.txt`",
    )


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    policy_issues = validate_policy(root)
    issues.extend(policy_issues)
    payload = load_policy(root)
    channel = str(payload["channel"])
    target = str(payload["upgrade_policy"]["archive_target_scope"][0])

    workflow = read_text(resolve(root, WORKFLOW))
    notes = read_text(resolve(root, NOTES))
    third_party_readme = read_text(resolve(root, THIRD_PARTY_README))

    issues.extend(collect_missing_markers(workflow, WORKFLOW_MARKERS, "MISSING_WORKFLOW_MARKER"))
    issues.extend(collect_order_issues(workflow, ORDERED_WORKFLOW_LINES, "OUT_OF_ORDER_WORKFLOW_STEP"))
    for marker in WORKFLOW_RUN_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_RUN_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_RUN_LINE", f"{marker}:count={count}"))

    issues.extend(collect_missing_markers(notes, NOTES_MARKERS, "MISSING_NOTES_MARKER"))
    issues.extend(
        collect_missing_markers(
            third_party_readme,
            third_party_markers(channel, target),
            "MISSING_THIRD_PARTY_MARKER",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_PINNED_ZIG_SETUP=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    channel = "0.17.0-dev.87+9b177a7d2"
    target = "x86_64-linux"
    filename = f"zig-{target}-{channel}.tar.xz"

    write_text(
        resolve(root, POLICY),
        json.dumps(
            {
                "phase": EXPECTED_POLICY_PHASE,
                "channel": channel,
                "minimum_version": channel,
                "archive_sha256": {target: "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [target],
                    "required_make_routes": list(EXPECTED_REQUIRED_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )
    workflow_text = "\n".join(
        (
            "      - name: Setup Python",
            "      - name: Setup pinned Zig toolchain",
            '          policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
            '          filename = f"zig-{target}-{channel}.tar.xz"',
            '          url = f"https://ziglang.org/builds/{filename}"',
            '          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
            '          mirror_file=".zig-toolchain/community-mirrors.txt"',
            '          if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
            '          if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
            '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
            '          if try_download "$ZIGUX_ZIG_URL"; then',
            "          echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
            "      - name: Compile current scripts",
            "      - name: Self-test current Zig toolchain checker",
            "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
            "      - name: Check current Zig toolchain policy packet",
            "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
            "      - name: Check current pinned Zig archive packet",
            "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
            "      - name: Self-test current Zig installer helper",
            "        run: python3 scripts/zigux/install-zig.py --self-test",
            "      - name: Self-test current staged pinned Zig archive helper",
            "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
            "      - name: Self-test current Phase 2 toolchain pinning checker",
        )
    )
    write_text(resolve(root, WORKFLOW), workflow_text + "\n")
    notes_text = "\n".join(
        (
            "# Phase 2 Toolchain Bootstrap Notes",
            "",
            NOTES_MARKERS[0],
            NOTES_MARKERS[1],
            NOTES_MARKERS[2],
            NOTES_MARKERS[3],
            NOTES_MARKERS[4],
            NOTES_MARKERS[5],
            NOTES_MARKERS[6],
            NOTES_MARKERS[7],
            NOTES_MARKERS[8],
        )
    )
    write_text(resolve(root, NOTES), notes_text + "\n")
    third_party_text = "\n".join(("# Zigux third-party archives", "", *third_party_markers(channel, target)))
    write_text(resolve(root, THIRD_PARTY_README), third_party_text + "\n")
    for rel in (CHECK_ZIG_TOOLCHAIN, INSTALL_ZIG, STAGE_ARCHIVE):
        write_text(resolve(root, rel), "present\n")


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
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


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_pinned_zig_setup_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        workflow_path = resolve(root, WORKFLOW)
        workflow_path.write_text(
            replace_once(workflow_path.read_text(encoding="utf-8"), WORKFLOW_MARKERS[6]),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_MARKER", WORKFLOW_MARKERS[6]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        workflow_path = resolve(root, WORKFLOW)
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_text = replace_exact_line(workflow_text, ORDERED_WORKFLOW_LINES[2])
        workflow_text += f"{ORDERED_WORKFLOW_LINES[2]}\n"
        workflow_path.write_text(workflow_text, encoding="utf-8")
        assert any(code == "OUT_OF_ORDER_WORKFLOW_STEP" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        workflow_path = resolve(root, WORKFLOW)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_RUN_LINES[0]),
            encoding="utf-8",
        )
        assert ("DUPLICATE_WORKFLOW_RUN_LINE", f"{WORKFLOW_RUN_LINES[0]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        notes_path = resolve(root, NOTES)
        notes_path.write_text(
            replace_once(notes_path.read_text(encoding="utf-8"), NOTES_MARKERS[1]),
            encoding="utf-8",
        )
        assert ("MISSING_NOTES_MARKER", NOTES_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        third_party_path = resolve(root, THIRD_PARTY_README)
        marker = third_party_markers("0.17.0-dev.87+9b177a7d2", "x86_64-linux")[1]
        third_party_path.write_text(
            replace_once(third_party_path.read_text(encoding="utf-8"), marker),
            encoding="utf-8",
        )
        assert ("MISSING_THIRD_PARTY_MARKER", marker) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        resolve(root, INSTALL_ZIG).unlink()
        assert ("MISSING_REQUIRED_PATH", INSTALL_ZIG) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy_path = resolve(root, POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["minimum_version"] = "0.16.0"
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "POLICY_MINIMUM_VERSION_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        policy_path = resolve(root, POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "POLICY_REQUIRED_ROUTES_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        policy_path = resolve(root, POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "aarch64-linux"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "POLICY_ARCHIVE_TARGET_SCOPE_INVALID" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        resolve(root, POLICY).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing policy file did not abort")
        checks += 1

        build_sample_root(root)
        resolve(root, WORKFLOW).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing workflow file did not abort")
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_BOOTSTRAP_PINNED_ZIG_SETUP_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_PINNED_ZIG_SETUP_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the policy-driven pinned Zig bootstrap setup packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a passing current-like sample root and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print("PHASE2_BOOTSTRAP_PINNED_ZIG_SETUP_SAMPLE_ROOT=pass")
        print(f"PHASE2_BOOTSTRAP_PINNED_ZIG_SETUP_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_PINNED_ZIG_SETUP=pass")
    print(f"PHASE2_BOOTSTRAP_PINNED_ZIG_SETUP_ROOT={root}")
    print(f"PHASE2_BOOTSTRAP_PINNED_ZIG_SETUP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_BOOTSTRAP_PINNED_ZIG_SETUP_WORKFLOW_RUN_LINE_COUNT={len(WORKFLOW_RUN_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
