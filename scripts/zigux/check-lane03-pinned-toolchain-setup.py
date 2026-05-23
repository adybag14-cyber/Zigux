#!/usr/bin/env python3
"""Guard the current pinned Zig bootstrap setup block."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

EXPECTED_ARCHIVE_TARGET_SCOPE = ["x86_64-linux"]
EXPECTED_REQUIRED_MAKE_ROUTES = ["phase2-toolchain", "phase2-validate", "phase2-cross"]
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_ARCHIVE_SHA256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"

WORKFLOW_REQUIRED_LINES = (
    "      - name: Setup pinned Zig toolchain",
    "        run: |",
    '          policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    '          targets = policy["upgrade_policy"]["archive_target_scope"]',
    '          if len(targets) != 1:',
    '              raise SystemExit(f"expected exactly one pinned archive target, got {len(targets)}")',
    "          filename = f\"zig-{target}-{channel}.tar.xz\"",
    '          url = f"https://ziglang.org/builds/{filename}"',
    '          print(f"ZIGUX_ZIG_TARGET=\'{target}\'")',
    '          print(f"ZIGUX_ZIG_CHANNEL=\'{channel}\'")',
    '          print(f"ZIGUX_ZIG_FILENAME=\'{filename}\'")',
    '          print(f"ZIGUX_ZIG_URL=\'{url}\'")',
    '          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
    '          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"',
    '          mirror_file=".zig-toolchain/community-mirrors.txt"',
    '          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    "          try_local_archive() {",
    '            if [ ! -f "$repo_archive_path" ]; then',
    '            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    '              tar -xJf "$repo_archive_path" -C .zig-toolchain',
    '              if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
    "          try_download() {",
    '            if curl -L --fail "$url" -o "$archive_path"; then',
    '              if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    '                tar -xJf "$archive_path" -C .zig-toolchain',
    '                if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
    "          if try_local_archive; then",
    '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    '              if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then',
    '            if try_download "$ZIGUX_ZIG_URL"; then',
    "            echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
    '          echo "$extract_root" >> "$GITHUB_PATH"',
    '          "$zig_path" version',
)

WORKFLOW_SEQUENCE = (
    "      - name: Setup pinned Zig toolchain",
    '          targets = policy["upgrade_policy"]["archive_target_scope"]',
    '          print(f"ZIGUX_ZIG_TARGET=\'{target}\'")',
    '          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
    "          try_local_archive() {",
    "          try_download() {",
    "          if try_local_archive; then",
    '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    '            if try_download "$ZIGUX_ZIG_URL"; then',
    "            echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
    '          "$zig_path" version',
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
    return sum(1 for line in text.splitlines() if line == marker)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            if replacement:
                lines[index] = replacement
            else:
                del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_line_issues(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in WORKFLOW_REQUIRED_LINES:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
    return issues


def collect_sequence_issues(text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    lines = text.splitlines()
    positions: list[int] = []

    for marker in WORKFLOW_SEQUENCE:
        count = count_exact_lines(text, marker)
        if count != 1:
            continue
        positions.append(lines.index(marker))

    for index in range(1, len(positions)):
        if positions[index] <= positions[index - 1]:
            issues.append(
                ("MISORDERED_WORKFLOW_SETUP", f"{WORKFLOW_SEQUENCE[index - 1]} -> {WORKFLOW_SEQUENCE[index]}")
            )
    return issues


def collect_policy_issues(policy_path: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    try:
        payload = json.loads(read_text(policy_path))
    except json.JSONDecodeError as exc:
        return [("INVALID_POLICY_JSON", exc.msg)]

    if not isinstance(payload, dict):
        return [("INVALID_POLICY", "expected JSON object")]

    if payload.get("phase") != "Phase 2":
        issues.append(("INVALID_POLICY", f"phase={payload.get('phase')!r}"))

    channel = payload.get("channel")
    minimum_version = payload.get("minimum_version")
    if channel != EXPECTED_CHANNEL:
        issues.append(("INVALID_POLICY", f"channel={channel!r}"))
    if minimum_version != EXPECTED_CHANNEL:
        issues.append(("INVALID_POLICY", f"minimum_version={minimum_version!r}"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_POLICY", "archive_sha256"))
    else:
        if list(archive_sha256.keys()) != EXPECTED_ARCHIVE_TARGET_SCOPE:
            issues.append(("INVALID_POLICY", f"archive_sha256_keys={list(archive_sha256.keys())!r}"))
        digest = archive_sha256.get("x86_64-linux")
        if digest != EXPECTED_ARCHIVE_SHA256:
            issues.append(("INVALID_POLICY", f"archive_sha256['x86_64-linux']={digest!r}"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY", "upgrade_policy"))
    else:
        if upgrade_policy.get("channel_minimum_lockstep") is not True:
            issues.append(("INVALID_POLICY", "channel_minimum_lockstep"))
        if upgrade_policy.get("archive_target_scope") != EXPECTED_ARCHIVE_TARGET_SCOPE:
            issues.append(("INVALID_POLICY", f"archive_target_scope={upgrade_policy.get('archive_target_scope')!r}"))
        if upgrade_policy.get("required_make_routes") != EXPECTED_REQUIRED_MAKE_ROUTES:
            issues.append(("INVALID_POLICY", f"required_make_routes={upgrade_policy.get('required_make_routes')!r}"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)

    issues: list[tuple[str, str]] = []
    issues.extend(collect_line_issues(workflow_text))
    issues.extend(collect_sequence_issues(workflow_text))
    issues.extend(collect_policy_issues(policy_path))
    return issues


def build_happy_path_root(root: Path) -> None:
    write_text(resolve_path(root, WORKFLOW), "\n".join(("name: zigux-bootstrap", *WORKFLOW_REQUIRED_LINES)) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {"x86_64-linux": EXPECTED_ARCHIVE_SHA256},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_ARCHIVE_TARGET_SCOPE,
                    "required_make_routes": EXPECTED_REQUIRED_MAKE_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane03_pinned_toolchain_setup_") as tmp_dir:
        root = Path(tmp_dir)

        build_happy_path_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_REQUIRED_LINES:
            build_happy_path_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_REQUIRED_LINES:
            build_happy_path_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_happy_path_root(root)
        path = resolve_path(root, WORKFLOW)
        workflow_text = path.read_text(encoding="utf-8")
        later = WORKFLOW_SEQUENCE[7]
        earlier = WORKFLOW_SEQUENCE[6]
        workflow_text = replace_exact_line(workflow_text, later)
        workflow_text = replace_exact_line(workflow_text, earlier)
        workflow_text += f"{later}\n{earlier}\n"
        path.write_text(workflow_text, encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISORDERED_WORKFLOW_SETUP", f"{WORKFLOW_SEQUENCE[6]} -> {WORKFLOW_SEQUENCE[7]}") in issues
        checks_run += 1

        policy_cases = (
            ('{"phase":"Phase 3"}\n', ("INVALID_POLICY", "phase='Phase 3'")),
            ('{"phase":"Phase 2","channel":"","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain","phase2-validate","phase2-cross"]}}\n', ("INVALID_POLICY", "channel=''")),
            ('{"phase":"Phase 2","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.16.0","archive_sha256":{"x86_64-linux":"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain","phase2-validate","phase2-cross"]}}\n', ("INVALID_POLICY", "minimum_version='0.16.0'")),
            ('{"phase":"Phase 2","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"aarch64-linux":"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain","phase2-validate","phase2-cross"]}}\n', ("INVALID_POLICY", "archive_sha256_keys=['aarch64-linux']")),
            ('{"phase":"Phase 2","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"deadbeef"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain","phase2-validate","phase2-cross"]}}\n', ("INVALID_POLICY", "archive_sha256['x86_64-linux']='deadbeef'")),
            ('{"phase":"Phase 2","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"},"upgrade_policy":{"channel_minimum_lockstep":false,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain","phase2-validate","phase2-cross"]}}\n', ("INVALID_POLICY", "channel_minimum_lockstep")),
            ('{"phase":"Phase 2","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["aarch64-linux"],"required_make_routes":["phase2-toolchain","phase2-validate","phase2-cross"]}}\n', ("INVALID_POLICY", "archive_target_scope=['aarch64-linux']")),
            ('{"phase":"Phase 2","channel":"0.17.0-dev.87+9b177a7d2","minimum_version":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"},"upgrade_policy":{"channel_minimum_lockstep":true,"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain"]}}\n', ("INVALID_POLICY", "required_make_routes=['phase2-toolchain']")),
            ("[]\n", ("INVALID_POLICY", "expected JSON object")),
            ("{not-json}\n", ("INVALID_POLICY_JSON", "Expecting property name enclosed in double quotes")),
        )

        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        for payload, expected_issue in policy_cases:
            build_happy_path_root(root)
            policy_path.write_text(payload, encoding="utf-8")
            assert expected_issue in collect_issues(root)
            checks_run += 1

        for path in (WORKFLOW, TOOLCHAIN_POLICY):
            build_happy_path_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    print("LANE03_PINNED_TOOLCHAIN_SETUP_SELF_TEST=pass")
    print(f"LANE03_PINNED_TOOLCHAIN_SETUP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the pinned Zig bootstrap setup block stays aligned with the current policy-driven install flow."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("LANE03_PINNED_TOOLCHAIN_SETUP=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("LANE03_PINNED_TOOLCHAIN_SETUP=pass")
    print(f"LANE03_PINNED_TOOLCHAIN_SETUP_WORKFLOW_LINE_COUNT={len(WORKFLOW_REQUIRED_LINES)}")
    print("LANE03_PINNED_TOOLCHAIN_SETUP_ARCHIVE_TARGETS=" + ",".join(EXPECTED_ARCHIVE_TARGET_SCOPE))
    print("LANE03_PINNED_TOOLCHAIN_SETUP_REQUIRED_MAKE_ROUTES=" + ",".join(EXPECTED_REQUIRED_MAKE_ROUTES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
