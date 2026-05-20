#!/usr/bin/env python3
"""Guard the current pinned-Zig bootstrap setup-step packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
TOOLCHAIN_CHECKER = Path("scripts/zigux/check-zig-toolchain.py")
INSTALLER = Path("scripts/zigux/install-zig.py")

REQUIRED_PATHS = (
    WORKFLOW,
    POLICY,
    TOOLCHAIN_CHECKER,
    INSTALLER,
)

SETUP_MARKERS = (
    "- name: Setup pinned Zig toolchain",
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    "print(f\"ZIGUX_ZIG_TARGET='{target}'\")",
    "print(f\"ZIGUX_ZIG_CHANNEL='{channel}'\")",
    "print(f\"ZIGUX_ZIG_FILENAME='{filename}'\")",
    "print(f\"ZIGUX_ZIG_URL='{url}'\")",
    'archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
    'extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"',
    'mirror_file=".zig-toolchain/community-mirrors.txt"',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'rm -f "$archive_path" "$mirror_file"',
    'rm -rf "$extract_root"',
    "try_local_archive() {",
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'tar -xJf "$repo_archive_path" -C .zig-toolchain',
    "try_download() {",
    'if curl -L --fail "$url" -o "$archive_path"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'tar -xJf "$archive_path" -C .zig-toolchain',
    'if try_local_archive; then',
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'while IFS= read -r mirror_url; do',
    'if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then',
    'if try_download "$ZIGUX_ZIG_URL"; then',
    "echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
    'echo "$extract_root" >> "$GITHUB_PATH"',
    '"$zig_path" version',
)

ORDERED_MARKERS = (
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    "try_local_archive() {",
    "try_download() {",
    'if try_local_archive; then',
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if try_download "$ZIGUX_ZIG_URL"; then',
    'echo "$extract_root" >> "$GITHUB_PATH"',
    '"$zig_path" version',
)

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "channel": "0.17.0-dev.87+9b177a7d2",
    "minimum_version": "0.17.0-dev.87+9b177a7d2",
    "archive_sha256": {
        "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
    },
    "upgrade_policy": {
        "channel_minimum_lockstep": True,
        "archive_target_scope": ["x86_64-linux"],
        "required_make_routes": ["phase2-toolchain", "phase2-validate"],
    },
}

EXPECTED_SELF_TEST_CASE_COUNT = 1 + len(SETUP_MARKERS) + len(ORDERED_MARKERS) + 3 + len(REQUIRED_PATHS)


def resolve_path(root: Path, path: Path) -> Path:
    return root / path


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


def load_policy(root: Path) -> object:
    return json.loads(read_text(resolve_path(root, POLICY)))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for path in REQUIRED_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_REQUIRED_PATH", path.as_posix()))

    workflow_path = resolve_path(root, WORKFLOW)
    if not workflow_path.exists():
        return issues

    workflow_text = read_text(workflow_path)
    for marker in SETUP_MARKERS:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_SETUP_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_SETUP_MARKER", f"{marker}:count={count}"))

    positions: list[tuple[str, int]] = []
    for marker in ORDERED_MARKERS:
        position = workflow_text.find(marker)
        if position == -1:
            continue
        positions.append((marker, position))
    for index in range(1, len(positions)):
        previous_marker, previous_position = positions[index - 1]
        marker, position = positions[index]
        if position <= previous_position:
            issues.append(
                ("SETUP_ORDER_DRIFT", f"{previous_marker} -> {marker}")
            )

    policy_path = resolve_path(root, POLICY)
    if policy_path.exists():
        try:
            policy = load_policy(root)
        except json.JSONDecodeError as exc:
            issues.append(("INVALID_POLICY_JSON", exc.msg))
        else:
            if policy != EXPECTED_POLICY:
                issues.append(("POLICY_PAYLOAD_MISMATCH", "scripts/zigux/zig-toolchain-policy.json"))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_BOOTSTRAP_SETUP_STEP=fail")
    for code, value in issues:
        print(f"{code}:{value}")
    return 1


def build_sample_root(root: Path) -> None:
    workflow_text = "\n".join(
        (
            "name: zigux-bootstrap",
            "jobs:",
            "  bootstrap:",
            "    steps:",
            "      - name: Setup pinned Zig toolchain",
            "        run: |",
            "          set -euxo pipefail",
            "          eval \"$(python3 - <<'PY'",
            "          import json",
            "          from pathlib import Path",
            "",
            '          policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
            '          targets = policy["upgrade_policy"]["archive_target_scope"]',
            '          target = targets[0]',
            '          channel = policy["channel"]',
            '          filename = f"zig-{target}-{channel}.tar.xz"',
            '          url = f"https://ziglang.org/builds/{filename}"',
            '          print(f"ZIGUX_ZIG_TARGET=\'{target}\'")',
            '          print(f"ZIGUX_ZIG_CHANNEL=\'{channel}\'")',
            '          print(f"ZIGUX_ZIG_FILENAME=\'{filename}\'")',
            '          print(f"ZIGUX_ZIG_URL=\'{url}\'")',
            "          PY",
            '          )\"',
            "          mkdir -p .zig-toolchain",
            '          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
            '          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"',
            '          mirror_file=".zig-toolchain/community-mirrors.txt"',
            '          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
            '          rm -f "$archive_path" "$mirror_file"',
            '          rm -rf "$extract_root"',
            "          try_local_archive() {",
            '            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
            '              tar -xJf "$repo_archive_path" -C .zig-toolchain',
            '              return 0',
            "            fi",
            "            return 1",
            "          }",
            "          try_download() {",
            '            if curl -L --fail "$url" -o "$archive_path"; then',
            '              if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
            '                tar -xJf "$archive_path" -C .zig-toolchain',
            "                return 0",
            "              fi",
            "            fi",
            "            return 1",
            "          }",
            "          download_success=0",
            "          if try_local_archive; then",
            "            download_success=1",
            '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
            "            while IFS= read -r mirror_url; do",
            '              if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then',
            "                download_success=1",
            "                break",
            "              fi",
            '            done < "$mirror_file"',
            "          fi",
            '          if try_download "$ZIGUX_ZIG_URL"; then',
            "            download_success=1",
            "          fi",
            "          if [ \"$download_success\" -ne 1 ]; then",
            "            echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
            "            exit 1",
            "          fi",
            '          zig_path="$extract_root/zig"',
            '          echo "$extract_root" >> "$GITHUB_PATH"',
            '          "$zig_path" version',
        )
    ) + "\n"
    write_text(resolve_path(root, WORKFLOW), workflow_text)
    write_text(resolve_path(root, POLICY), json.dumps(EXPECTED_POLICY, indent=2) + "\n")
    write_text(resolve_path(root, TOOLCHAIN_CHECKER), "present\n")
    write_text(resolve_path(root, INSTALLER), "present\n")


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
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_setup_step_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in SETUP_MARKERS:
            build_sample_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_SETUP_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in ORDERED_MARKERS:
            build_sample_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_text = workflow_path.read_text(encoding="utf-8")
            workflow_text = duplicate_exact_line(workflow_text, marker)
            workflow_path.write_text(workflow_text, encoding="utf-8")
            assert any(issue[0] == "DUPLICATE_SETUP_MARKER" and issue[1] == f"{marker}:count=2" for issue in collect_issues(root))
            checks_run += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_text = workflow_path.read_text(encoding="utf-8")
        moved = 'if try_download "$ZIGUX_ZIG_URL"; then'
        workflow_text = replace_exact_line(workflow_text, moved)
        workflow_text += f"{moved}\n"
        workflow_path.write_text(workflow_text, encoding="utf-8")
        assert any(issue[0] == "SETUP_ORDER_DRIFT" for issue in collect_issues(root))
        checks_run += 1

        build_sample_root(root)
        policy_path = resolve_path(root, POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("POLICY_PAYLOAD_MISMATCH", "scripts/zigux/zig-toolchain-policy.json") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        policy_path = resolve_path(root, POLICY)
        policy_path.write_text("{\n", encoding="utf-8")
        assert any(issue[0] == "INVALID_POLICY_JSON" for issue in collect_issues(root))
        checks_run += 1

        for path in REQUIRED_PATHS:
            build_sample_root(root)
            resolve_path(root, path).unlink()
            issues = collect_issues(root)
            assert ("MISSING_REQUIRED_PATH", path.as_posix()) in issues
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_BOOTSTRAP_SETUP_STEP_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_SETUP_STEP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the pinned-Zig bootstrap setup-step packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_SETUP_STEP=pass")
    print(f"PHASE2_BOOTSTRAP_SETUP_REQUIRED_MARKER_COUNT={len(SETUP_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_SETUP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
