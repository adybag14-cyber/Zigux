#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
TOOLCHAIN_CHECKER = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
THIRD_PARTY_README = ROOT / "third_party" / "README.md"

REQUIRED_NOTE_MARKERS = (
    "# Phase 2 Toolchain Bootstrap Notes",
    "## Current direct packet",
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master`",
    "`third_party/README.md` is directly readable on current `master`",
    "tries `community-mirrors.txt` before the direct Zig download URL",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, returned archive-verification and staged-archive helper packet, or returned fixdep packet on current `master`.",
)

NOTE_EXACT_COUNT_MARKERS = (
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
)

WORKFLOW_MARKERS = (
    "community-mirrors.txt",
    "try_local_archive()",
    'python3 scripts/zigux/check-zig-toolchain.py --policy-only',
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing',
    'python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"',
)

THIRD_PARTY_MARKERS = (
    "# Zigux third-party archives",
    "## Current pinned Zig archive contract",
    "## Validation",
    "## Bootstrap order",
    "do not keep duplicate-suffix copies",
)

TOOLCHAIN_CHECKER_MARKERS = (
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
    "def expected_archive_metadata(",
    "def validate_policy_archive(",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_substring(text: str, marker: str) -> int:
    return text.count(marker)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def load_policy(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"required json invalid: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"required json has invalid top-level shape: {path}")
    return payload


def load_required_routes(policy: dict[str, object], policy_path: Path) -> list[str]:
    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"required json has invalid upgrade_policy: {policy_path}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise SystemExit(f"required json has invalid required_make_routes: {policy_path}")
    normalized: list[str] = []
    seen: set[str] = set()
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise SystemExit(f"required json has invalid required_make_routes entry: {policy_path}")
        value = route.strip()
        if value in seen:
            raise SystemExit(f"required json has duplicate required_make_routes entry: {policy_path}: {value}")
        seen.add(value)
        normalized.append(value)
    return normalized


def required_archive_filename(policy: dict[str, object], policy_path: Path) -> tuple[str, str]:
    channel = policy.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        raise SystemExit(f"required json has invalid channel: {policy_path}")
    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"required json has invalid upgrade_policy: {policy_path}")
    targets = upgrade_policy.get("archive_target_scope")
    if not isinstance(targets, list) or len(targets) != 1 or not isinstance(targets[0], str) or not targets[0].strip():
        raise SystemExit(f"required json has invalid archive_target_scope: {policy_path}")
    target = targets[0].strip()
    return target, f"zig-{target}-{channel.strip()}.tar.xz"


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    policy = load_policy(policy_path)
    required_routes = load_required_routes(policy, policy_path)
    target, archive_filename = required_archive_filename(policy, policy_path)

    note_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    third_party_text = read_text(resolve_path(root, THIRD_PARTY_README))
    checker_text = read_text(resolve_path(root, TOOLCHAIN_CHECKER))

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_NOTE_MARKER", marker))
    for marker in NOTE_EXACT_COUNT_MARKERS:
        count = count_substring(note_text, marker)
        if count != 1:
            issues.append(("NOTE_EXACT_COUNT", f"{count}::{marker}"))

    channel = str(policy["channel"])
    if f"`{channel}`" not in note_text:
        issues.append(("MISSING_NOTE_CHANNEL", channel))
    if f"`{target}`" not in note_text:
        issues.append(("MISSING_NOTE_TARGET", target))
    if f"`{archive_filename}`" not in note_text:
        issues.append(("MISSING_NOTE_ARCHIVE_FILENAME", archive_filename))

    for route in required_routes:
        route_marker = f"`make -C zigux {route}`"
        if route_marker not in note_text:
            issues.append(("MISSING_NOTE_REQUIRED_ROUTE", route_marker))
        workflow_line = f"run: make -C zigux {route}"
        if count_exact_lines(workflow_text, workflow_line) != 1:
            issues.append(("WORKFLOW_REQUIRED_ROUTE_COUNT", f"{count_exact_lines(workflow_text, workflow_line)}::{workflow_line}"))
        target_line = f"{route}:"
        if count_exact_lines(makefile_text, target_line) != 1:
            issues.append(("MAKEFILE_REQUIRED_ROUTE_COUNT", f"{count_exact_lines(makefile_text, target_line)}::{target_line}"))

    for marker in WORKFLOW_MARKERS:
        if marker not in workflow_text:
            issues.append(("MISSING_WORKFLOW_MARKER", marker))

    if f"- target: `{target}`" not in third_party_text:
        issues.append(("MISSING_THIRD_PARTY_TARGET", target))
    if f"- channel: `{channel}`" not in third_party_text:
        issues.append(("MISSING_THIRD_PARTY_CHANNEL", channel))
    if f"- file: `third_party/{archive_filename}`" not in third_party_text:
        issues.append(("MISSING_THIRD_PARTY_FILENAME", archive_filename))
    expected_archive_check = (
        f"`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/{archive_filename} --archive-target {target}`"
    )
    if expected_archive_check not in third_party_text:
        issues.append(("MISSING_THIRD_PARTY_ARCHIVE_CHECK", expected_archive_check))
    for marker in THIRD_PARTY_MARKERS:
        if marker not in third_party_text:
            issues.append(("MISSING_THIRD_PARTY_MARKER", marker))

    for marker in TOOLCHAIN_CHECKER_MARKERS:
        if marker not in checker_text:
            issues.append(("MISSING_TOOLCHAIN_CHECKER_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    policy = {
        "phase": "Phase 2",
        "channel": "0.17.0-dev.87+9b177a7d2",
        "minimum_version": "0.17.0-dev.87+9b177a7d2",
        "archive_sha256": {
            "x86_64-linux": "3" * 64,
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
    write_text(resolve_path(root, TOOLCHAIN_POLICY), json.dumps(policy, indent=2) + "\n")
    write_text(
        resolve_path(root, BOOTSTRAP_NOTES),
        "\n".join(
            REQUIRED_NOTE_MARKERS
            + (
                "`0.17.0-dev.87+9b177a7d2`",
                "`x86_64-linux`",
                "`zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
            )
        )
        + "\n",
    )
    write_text(
        resolve_path(root, WORKFLOW),
        "\n".join(
            WORKFLOW_MARKERS
            + tuple(f"run: make -C zigux {route}" for route in policy["upgrade_policy"]["required_make_routes"])
        )
        + "\n",
    )
    write_text(
        resolve_path(root, MAKEFILE),
        "\n".join(f"{route}:" for route in policy["upgrade_policy"]["required_make_routes"]) + "\n",
    )
    write_text(
        resolve_path(root, THIRD_PARTY_README),
        "\n".join(
            THIRD_PARTY_MARKERS
            + (
                "- target: `x86_64-linux`",
                "- channel: `0.17.0-dev.87+9b177a7d2`",
                "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
                "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
            )
        )
        + "\n",
    )
    write_text(resolve_path(root, TOOLCHAIN_CHECKER), "\n".join(TOOLCHAIN_CHECKER_MARKERS) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_bootstrap_note_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        note_path = resolve_path(root, BOOTSTRAP_NOTES)
        for marker in REQUIRED_NOTE_MARKERS:
            build_self_test_root(root)
            note_path.write_text(replace_once(read_text(note_path), marker), encoding="utf-8")
            assert ("MISSING_NOTE_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in NOTE_EXACT_COUNT_MARKERS:
            build_self_test_root(root)
            note_path.write_text(duplicate_exact_line(read_text(note_path), marker), encoding="utf-8")
            assert ("NOTE_EXACT_COUNT", f"2::{marker}") in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = load_policy(policy_path)
        policy["channel"] = "0.18.0-dev.1+abcdef"
        write_text(policy_path, json.dumps(policy, indent=2) + "\n")
        assert ("MISSING_NOTE_CHANNEL", "0.18.0-dev.1+abcdef") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(replace_once(read_text(workflow_path), WORKFLOW_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_WORKFLOW_MARKER", WORKFLOW_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(replace_once(read_text(makefile_path), "phase2-cross:"), encoding="utf-8")
        assert ("MAKEFILE_REQUIRED_ROUTE_COUNT", "0::phase2-cross:") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        third_party_path = resolve_path(root, THIRD_PARTY_README)
        third_party_path.write_text(replace_once(read_text(third_party_path), "- target: `x86_64-linux`"), encoding="utf-8")
        assert ("MISSING_THIRD_PARTY_TARGET", "x86_64-linux") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        checker_path = resolve_path(root, TOOLCHAIN_CHECKER)
        checker_path.write_text(replace_once(read_text(checker_path), TOOLCHAIN_CHECKER_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_TOOLCHAIN_CHECKER_MARKER", TOOLCHAIN_CHECKER_MARKERS[0]) in collect_issues(root)
        checks += 1

    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the live Phase 2 toolchain bootstrap note aligned with the current pinned-toolchain, archive, workflow, and make-route packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    policy = load_policy(resolve_path(args.root.resolve(), TOOLCHAIN_POLICY))
    routes = load_required_routes(policy, resolve_path(args.root.resolve(), TOOLCHAIN_POLICY))
    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_PACKET_REQUIRED_ROUTE_COUNT={len(routes)}")
    print("PHASE2_TOOLCHAIN_BOOTSTRAP_NOTE_PACKET_REQUIRED_ROUTE_LIST=" + ",".join(routes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
