#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 Zig toolchain policy packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
POLICY_PATH = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
MAKEFILE = ROOT / "zigux" / "Makefile"

EXPECTED_PHASE = "Phase 2"
EXPECTED_TARGETS = ["x86_64-linux"]
EXPECTED_REQUIRED_ROUTES = ["phase2-toolchain", "phase2-validate"]

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: make -C zigux phase2-toolchain",
)

BOOTSTRAP_MARKERS = (
    "`scripts/zigux/zig-toolchain-policy.json`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "keeps the minimum version in lockstep",
    "limits archive digests to `x86_64-linux`",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_LINES)
    + len(WORKFLOW_LINES)
    + 1
    + len(MAKEFILE_LINES)
    + len(MAKEFILE_LINES)
    + 4
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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        payload = json.loads(read_text(resolve_path(root, POLICY_PATH)))
    except json.JSONDecodeError as exc:
        return [("INVALID_POLICY_JSON", exc.msg)]

    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("POLICY_PHASE_MISMATCH", repr(payload.get("phase"))))

    channel = payload.get("channel")
    minimum_version = payload.get("minimum_version")
    if not isinstance(channel, str) or not channel:
        issues.append(("INVALID_POLICY_FIELD", "channel"))
    if not isinstance(minimum_version, str) or not minimum_version:
        issues.append(("INVALID_POLICY_FIELD", "minimum_version"))
    if isinstance(channel, str) and isinstance(minimum_version, str) and channel != minimum_version:
        issues.append(("POLICY_LOCKSTEP_MISMATCH", f"{channel!r} != {minimum_version!r}"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_POLICY_FIELD", "archive_sha256"))
    else:
        if list(archive_sha256.keys()) != EXPECTED_TARGETS:
            issues.append(("POLICY_ARCHIVE_TARGETS_MISMATCH", repr(list(archive_sha256.keys()))))
        for target, digest in archive_sha256.items():
            if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest.lower()):
                issues.append(("INVALID_POLICY_DIGEST", target))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
        return issues

    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("POLICY_LOCKSTEP_FLAG_MISMATCH", repr(upgrade_policy.get("channel_minimum_lockstep"))))
    if upgrade_policy.get("archive_target_scope") != EXPECTED_TARGETS:
        issues.append(("POLICY_ARCHIVE_SCOPE_MISMATCH", repr(upgrade_policy.get("archive_target_scope"))))
    if upgrade_policy.get("required_make_routes") != EXPECTED_REQUIRED_ROUTES:
        issues.append(("POLICY_REQUIRED_ROUTES_MISMATCH", repr(upgrade_policy.get("required_make_routes"))))

    return issues


def collect_marker_issues(root: Path, path: Path, markers: tuple[str, ...], missing_code: str) -> list[tuple[str, str]]:
    text = read_text(resolve_path(root, path))
    return [(missing_code, marker) for marker in markers if marker not in text]


def collect_exact_line_issues(
    root: Path,
    path: Path,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    text = read_text(resolve_path(root, path))
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_policy_issues(root))
    issues.extend(collect_exact_line_issues(root, WORKFLOW, WORKFLOW_LINES, "MISSING_WORKFLOW_LINES", "DUPLICATE_WORKFLOW_LINES"))
    issues.extend(collect_marker_issues(root, BOOTSTRAP_NOTES, BOOTSTRAP_MARKERS, "MISSING_BOOTSTRAP_MARKERS"))
    issues.extend(collect_exact_line_issues(root, MAKEFILE, MAKEFILE_LINES, "MISSING_MAKEFILE_LINES", "DUPLICATE_MAKEFILE_LINES"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_TOOLCHAIN_POLICY_PACKET=fail")
    print("INVALID_PHASE2_TOOLCHAIN_POLICY_PACKET_START")
    for code, value in issues:
        print(f"{code}:{value}")
    print("INVALID_PHASE2_TOOLCHAIN_POLICY_PACKET_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, POLICY_PATH),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "channel": "0.17.0-dev.758+748e7c5e3",
                "minimum_version": "0.17.0-dev.758+748e7c5e3",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_TARGETS,
                    "required_make_routes": EXPECTED_REQUIRED_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(BOOTSTRAP_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_policy_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for line in WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(replace_exact_line(workflow_path.read_text(encoding="utf-8"), line), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINES", line) in collect_issues(root)
            checks_run += 1

        for line in WORKFLOW_LINES:
            build_self_test_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), line), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINES", f"{line}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        notes_path = resolve_path(root, BOOTSTRAP_NOTES)
        notes_path.write_text(replace_once(notes_path.read_text(encoding="utf-8"), BOOTSTRAP_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_BOOTSTRAP_MARKERS", BOOTSTRAP_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        for line in MAKEFILE_LINES:
            build_self_test_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_path.write_text(replace_exact_line(makefile_path.read_text(encoding="utf-8"), line), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINES", line) in collect_issues(root)
            checks_run += 1

        for line in MAKEFILE_LINES:
            build_self_test_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_path.write_text(duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), line), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINES", f"{line}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, POLICY_PATH)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["minimum_version"] = "0.16.0"
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("POLICY_LOCKSTEP_MISMATCH", "'0.17.0-dev.758+748e7c5e3' != '0.16.0'") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("POLICY_ARCHIVE_SCOPE_MISMATCH", "['aarch64-linux']") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("POLICY_REQUIRED_ROUTES_MISMATCH", "['phase2-toolchain']") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["archive_sha256"]["x86_64-linux"] = "oops"
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_DIGEST", "x86_64-linux") in collect_issues(root)
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT, (checks_run, EXPECTED_SELF_TEST_CASE_COUNT)
    print("PHASE2_TOOLCHAIN_POLICY_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_POLICY_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the current Phase 2 Zig toolchain policy packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Override the repo root used for packet inspection.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_POLICY_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_POLICY_PACKET_POLICY_PATH={resolve_path(args.root, POLICY_PATH)}")
    print(f"PHASE2_TOOLCHAIN_POLICY_PACKET_WORKFLOW_PATH={resolve_path(args.root, WORKFLOW)}")
    print(f"PHASE2_TOOLCHAIN_POLICY_PACKET_REQUIRED_ROUTE_COUNT={len(EXPECTED_REQUIRED_ROUTES)}")
    print(f"PHASE2_TOOLCHAIN_POLICY_PACKET_ARCHIVE_TARGET_COUNT={len(EXPECTED_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
