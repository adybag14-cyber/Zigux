#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_PATHS = (
    WORKFLOW,
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/install-zig.py",
)

REQUIRED_WORKFLOW_SETUP_MARKERS = (
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
    'echo "$extract_root" >> "$GITHUB_PATH"',
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
)

REQUIRED_TOOLCHAIN_SCRIPT_MARKERS = (
    'add_search_root(root / "third_party")',
    'add_search_root(root / "agent_files")',
    'parser.add_argument("--policy-only", action="store_true", help="Validate and summarize the pinned Zig policy without probing a zig executable.")',
    'parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")',
    'parser.add_argument("--archive-target", help="Archive target key from scripts/zigux/zig-toolchain-policy.json.")',
    'print("ZIG_TOOLCHAIN_POLICY_STATUS=present")',
    'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=present")',
)

REQUIRED_POLICY_VALUES = (
    ("phase", "Phase 2"),
    ("channel", "0.17.0-dev.87+9b177a7d2"),
    ("minimum_version", "0.17.0-dev.87+9b177a7d2"),
)

REQUIRED_POLICY_TARGETS = ("x86_64-linux",)
REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
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


def exact_line_index(text: str, marker: str) -> int:
    for index, line in enumerate(text.splitlines()):
        if line.strip() == marker:
            return index
    return -1


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def remove_substring(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def swap_exact_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index = None
    second_index = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == first and first_index is None:
            first_index = index
        if stripped == second and second_index is None:
            second_index = index
    if first_index is None or second_index is None:
        raise AssertionError("swap markers not found")
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    workflow = read_text(root, WORKFLOW)
    toolchain_script = read_text(root, "scripts/zigux/check-zig-toolchain.py")
    policy_text = read_text(root, "scripts/zigux/zig-toolchain-policy.json")

    for marker in REQUIRED_WORKFLOW_SETUP_MARKERS:
        if marker not in workflow:
            issues.append(("MISSING_WORKFLOW_SETUP_MARKER", marker))

    previous_index = -1
    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
            continue
        marker_index = exact_line_index(workflow, marker)
        if marker_index <= previous_index:
            issues.append(("MISORDERED_WORKFLOW_LINE", marker))
        previous_index = marker_index

    for marker in REQUIRED_TOOLCHAIN_SCRIPT_MARKERS:
        if marker not in toolchain_script:
            issues.append(("MISSING_TOOLCHAIN_SCRIPT_MARKER", marker))

    try:
        payload = json.loads(policy_text)
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_POLICY_JSON", exc.msg))
        return issues

    if not isinstance(payload, dict):
        issues.append(("INVALID_POLICY_PAYLOAD", "expected object"))
        return issues

    for key, expected in REQUIRED_POLICY_VALUES:
        if payload.get(key) != expected:
            issues.append(("POLICY_VALUE_MISMATCH", f"{key}={payload.get(key)!r}"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_UPGRADE_POLICY", str(type(upgrade_policy).__name__)))
        return issues

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_ARCHIVE_SHA256", str(type(archive_sha256).__name__)))
        return issues

    archive_targets = upgrade_policy.get("archive_target_scope")
    if archive_targets != list(REQUIRED_POLICY_TARGETS):
        issues.append(("ARCHIVE_TARGET_SCOPE_MISMATCH", repr(archive_targets)))

    missing_archive_targets = [target for target in REQUIRED_POLICY_TARGETS if target not in archive_sha256]
    for target in missing_archive_targets:
        issues.append(("MISSING_ARCHIVE_TARGET", target))

    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(
            ("LOCKSTEP_POLICY_MISMATCH", repr(upgrade_policy.get("channel_minimum_lockstep")))
        )

    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != list(REQUIRED_MAKE_ROUTES):
        issues.append(("REQUIRED_MAKE_ROUTES_MISMATCH", repr(required_make_routes)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Setup pinned Zig toolchain",
                "        run: |",
                '          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
                '          if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
                '            if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
                "              true",
                "            fi",
                "          fi",
                '          if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
                "            true",
                "          fi",
                '          echo "$extract_root" >> "$GITHUB_PATH"',
                "      - name: Self-test current Zig toolchain checker",
                f"        {REQUIRED_WORKFLOW_LINES[0]}",
                "      - name: Check current Zig toolchain policy packet",
                f"        {REQUIRED_WORKFLOW_LINES[1]}",
                "      - name: Check current pinned Zig archive packet",
                f"        {REQUIRED_WORKFLOW_LINES[2]}",
                "      - name: Self-test current Lane 05 local-first archive checker",
                f"        {REQUIRED_WORKFLOW_LINES[3]}",
                "      - name: Check current Lane 05 local-first archive packet",
                f"        {REQUIRED_WORKFLOW_LINES[4]}",
                "      - name: Self-test current Lane 05 local archive README checker",
                f"        {REQUIRED_WORKFLOW_LINES[5]}",
                "      - name: Check current Lane 05 local archive README packet",
                f"        {REQUIRED_WORKFLOW_LINES[6]}",
                "      - name: Self-test current Zig installer helper",
                f"        {REQUIRED_WORKFLOW_LINES[7]}",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "scripts/zigux/check-zig-toolchain.py",
        "\n".join(
            (
                '#!/usr/bin/env python3',
                'add_search_root(root / "third_party")',
                'add_search_root(root / "agent_files")',
                'parser.add_argument("--policy-only", action="store_true", help="Validate and summarize the pinned Zig policy without probing a zig executable.")',
                'parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")',
                'parser.add_argument("--archive-target", help="Archive target key from scripts/zigux/zig-toolchain-policy.json.")',
                'print("ZIG_TOOLCHAIN_POLICY_STATUS=present")',
                'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=present")',
            )
        )
        + "\n",
    )
    write_text(
        root,
        "scripts/zigux/zig-toolchain-policy.json",
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": [
                        "phase2-toolchain",
                        "phase2-validate",
                    ],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root, "scripts/zigux/check-lane05-local-first-archive-workflow.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-local-archive-readme.py", "present\n")
    write_text(root, "scripts/zigux/install-zig.py", "present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_toolchain_checker_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, remove_substring(read_text(root, WORKFLOW), REQUIRED_WORKFLOW_SETUP_MARKERS[0]))
        assert ("MISSING_WORKFLOW_SETUP_MARKER", REQUIRED_WORKFLOW_SETUP_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), REQUIRED_WORKFLOW_LINES[2], "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only"))
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), REQUIRED_WORKFLOW_LINES[0]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[0]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, swap_exact_lines(read_text(root, WORKFLOW), REQUIRED_WORKFLOW_LINES[1], REQUIRED_WORKFLOW_LINES[2]))
        assert ("MISORDERED_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, "scripts/zigux/check-zig-toolchain.py", remove_substring(read_text(root, "scripts/zigux/check-zig-toolchain.py"), REQUIRED_TOOLCHAIN_SCRIPT_MARKERS[0]))
        assert ("MISSING_TOOLCHAIN_SCRIPT_MARKER", REQUIRED_TOOLCHAIN_SCRIPT_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            "scripts/zigux/zig-toolchain-policy.json",
            json.dumps(
                {
                    "phase": "Phase 2",
                    "channel": "0.17.0-dev.87+9b177a7d2",
                    "minimum_version": "0.17.0-dev.87+9b177a7d2",
                    "archive_sha256": {},
                    "upgrade_policy": {
                        "channel_minimum_lockstep": True,
                        "archive_target_scope": [],
                        "required_make_routes": list(REQUIRED_MAKE_ROUTES),
                    },
                }
            )
            + "\n",
        )
        issues = collect_issues(root)
        assert ("ARCHIVE_TARGET_SCOPE_MISMATCH", "[]") in issues
        assert ("MISSING_ARCHIVE_TARGET", "x86_64-linux") in issues
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            "scripts/zigux/zig-toolchain-policy.json",
            json.dumps(
                {
                    "phase": "Phase 2",
                    "channel": "0.17.0-dev.87+9b177a7d2",
                    "minimum_version": "0.17.0-dev.87+9b177a7d2",
                    "archive_sha256": {
                        "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
                    },
                    "upgrade_policy": {
                        "channel_minimum_lockstep": False,
                        "archive_target_scope": ["x86_64-linux"],
                        "required_make_routes": list(REQUIRED_MAKE_ROUTES),
                    },
                }
            )
            + "\n",
        )
        assert ("LOCKSTEP_POLICY_MISMATCH", "False") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, "scripts/zigux/zig-toolchain-policy.json", "{not-json}\n")
        assert collect_issues(root)[0][0] == "INVALID_POLICY_JSON"
        checks += 1

        build_sample_root(root)
        (root / "scripts/zigux/install-zig.py").unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/install-zig.py") in collect_issues(root)
        checks += 1

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the live bootstrap toolchain packet drifts across the workflow, checker, and policy surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_SETUP_MARKER_COUNT={len(REQUIRED_WORKFLOW_SETUP_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
