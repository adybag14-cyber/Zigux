#!/usr/bin/env python3
"""Guard the pinned-toolchain bootstrap setup block in zigux-bootstrap.yml."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
SETUP_HEADING = "- name: Setup pinned Zig toolchain"

SETUP_MARKERS = (
    "set -euxo pipefail",
    "eval \"$(python3 - <<'PY'",
    "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
    "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]",
    "if len(targets) != 1:",
    "filename = f\"zig-{target}-{channel}.tar.xz\"",
    "url = f\"https://ziglang.org/builds/{filename}\"",
    "mkdir -p .zig-toolchain",
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "try_local_archive() {",
    "python3 scripts/zigux/stage-pinned-zig-archive.py",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
    "try_download() {",
    "curl -L --fail \"$url\" -o \"$archive_path\"",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
    "if try_local_archive; then",
    "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
    "if try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"; then",
    "if try_download \"$ZIGUX_ZIG_URL\"; then",
    "echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
    "echo \"$extract_root\" >> \"$GITHUB_PATH\"",
    "\"$zig_path\" version",
)

EXPECTED_SELF_TEST_CASE_COUNT = 8


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


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def duplicate_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, f"{marker}\n{marker}", 1)


def swap_once(text: str, first: str, second: str) -> str:
    if first not in text or second not in text:
        raise AssertionError("swap markers not found")
    placeholder = "__zigux_phase2_toolchain_setup_swap__"
    text = text.replace(first, placeholder, 1)
    text = text.replace(second, first, 1)
    return text.replace(placeholder, second, 1)


def count_substring(text: str, marker: str) -> int:
    return text.count(marker)


def extract_setup_block(text: str) -> str:
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == SETUP_HEADING:
            start = index
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("      - name: "):
            end = index
            break
    return "\n".join(lines[start:end]) + "\n"


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root, WORKFLOW)
    block = extract_setup_block(workflow_text)

    if not block:
        return [("MISSING_SETUP_HEADING", SETUP_HEADING)]

    indices: list[int] = []
    for marker in SETUP_MARKERS:
        count = count_substring(block, marker)
        if count == 0:
            issues.append(("MISSING_SETUP_MARKER", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_SETUP_MARKER", f"{marker}:count={count}"))
            continue
        indices.append(block.index(marker))

    if not issues and indices != sorted(indices):
        issues.append(("OUT_OF_ORDER_SETUP_MARKER", " -> ".join(SETUP_MARKERS)))

    archive_only_count = count_substring(block, "check-zig-toolchain.py --archive-only")
    if archive_only_count != 2:
        issues.append(("INVALID_ARCHIVE_ONLY_CALL_COUNT", str(archive_only_count)))

    zig_verify_count = count_substring(block, "check-zig-toolchain.py --zig \"$zig_path\"")
    if zig_verify_count != 2:
        issues.append(("INVALID_ZIG_VERIFY_CALL_COUNT", str(zig_verify_count)))

    if "third_party, mirrors, or ziglang.org" not in block:
        issues.append(("MISSING_FALLBACK_SUMMARY", "third_party, mirrors, or ziglang.org"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_SETUP_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - name: Setup pinned Zig toolchain",
                "        run: |",
                "          set -euxo pipefail",
                "          eval \"$(python3 - <<'PY'",
                "          import json",
                "          from pathlib import Path",
                "",
                "          policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
                "          targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]",
                "          if len(targets) != 1:",
                "              raise SystemExit(f\"expected exactly one pinned archive target, got {len(targets)}\")",
                "          target = targets[0]",
                "          channel = policy[\"channel\"]",
                "          filename = f\"zig-{target}-{channel}.tar.xz\"",
                "          url = f\"https://ziglang.org/builds/{filename}\"",
                "          print(f\"ZIGUX_ZIG_TARGET='{target}'\")",
                "          print(f\"ZIGUX_ZIG_CHANNEL='{channel}'\")",
                "          print(f\"ZIGUX_ZIG_FILENAME='{filename}'\")",
                "          print(f\"ZIGUX_ZIG_URL='{url}'\")",
                "          PY",
                "          )\"",
                "          mkdir -p .zig-toolchain",
                "          archive_path=\".zig-toolchain/$ZIGUX_ZIG_FILENAME\"",
                "          extract_root=\"$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL\"",
                "          mirror_file=\".zig-toolchain/community-mirrors.txt\"",
                "          repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
                "          repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
                "          try_local_archive() {",
                "            if [ ! -f \"$repo_archive_path\" ]; then",
                "              if [ ! -d \"$repo_archive_parts_dir\" ]; then",
                "                return 1",
                "              fi",
                "              python3 scripts/zigux/stage-pinned-zig-archive.py --root \"$GITHUB_WORKSPACE\" --parts-dir \"$repo_archive_parts_dir\" || return 1",
                "            fi",
                "            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"; then",
                "              tar -xJf \"$repo_archive_path\" -C .zig-toolchain",
                "              zig_path=\"$extract_root/zig\"",
                "              if python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"; then",
                "                return 0",
                "              fi",
                "            fi",
                "            rm -rf \"$extract_root\"",
                "            return 1",
                "          }",
                "          try_download() {",
                "            local url=\"$1\"",
                "            if curl -L --fail \"$url\" -o \"$archive_path\"; then",
                "              if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"; then",
                "                tar -xJf \"$archive_path\" -C .zig-toolchain",
                "                zig_path=\"$extract_root/zig\"",
                "                if python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"; then",
                "                  return 0",
                "                fi",
                "              fi",
                "              rm -f \"$archive_path\"",
                "              rm -rf \"$extract_root\"",
                "            fi",
                "            return 1",
                "          }",
                "          download_success=0",
                "          if try_local_archive; then",
                "            download_success=1",
                "          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
                "            while IFS= read -r mirror_url; do",
                "              [ -n \"$mirror_url\" ] || continue",
                "              if try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"; then",
                "                download_success=1",
                "                break",
                "              fi",
                "            done < \"$mirror_file\"",
                "          fi",
                "          if [ \"$download_success\" -ne 1 ]; then",
                "            if try_download \"$ZIGUX_ZIG_URL\"; then",
                "              download_success=1",
                "            fi",
                "          fi",
                "          if [ \"$download_success\" -ne 1 ]; then",
                "            echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
                "            exit 1",
                "          fi",
                "          zig_path=\"$extract_root/zig\"",
                "          echo \"$extract_root\" >> \"$GITHUB_PATH\"",
                "          \"$zig_path\" version",
                "      - name: Next step",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_setup_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_once(read_text(root, WORKFLOW), SETUP_HEADING, "- name: Other step"))
        assert ("MISSING_SETUP_HEADING", SETUP_HEADING) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_once(read_text(root, WORKFLOW), SETUP_MARKERS[11]))
        assert ("MISSING_SETUP_MARKER", SETUP_MARKERS[11]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_once(read_text(root, WORKFLOW), SETUP_MARKERS[18]))
        assert any(code == "DUPLICATE_SETUP_MARKER" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, swap_once(read_text(root, WORKFLOW), SETUP_MARKERS[18], SETUP_MARKERS[19]))
        assert any(code == "OUT_OF_ORDER_SETUP_MARKER" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_once(
                read_text(root, WORKFLOW),
                "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
            ),
        )
        assert ("INVALID_ARCHIVE_ONLY_CALL_COUNT", "1") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_once(read_text(root, WORKFLOW), "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\""))
        assert ("INVALID_ZIG_VERIFY_CALL_COUNT", "1") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, replace_once(read_text(root, WORKFLOW), "third_party, mirrors, or ziglang.org", "third_party only"))
        assert ("MISSING_FALLBACK_SUMMARY", "third_party, mirrors, or ziglang.org") in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_SETUP_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_SETUP_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the pinned-toolchain bootstrap setup block stays aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_SETUP_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_SETUP_PACKET_MARKER_COUNT={len(SETUP_MARKERS)}")
    print("PHASE2_TOOLCHAIN_SETUP_PACKET_ARCHIVE_ONLY_CALL_COUNT=2")
    print("PHASE2_TOOLCHAIN_SETUP_PACKET_ZIG_VERIFY_CALL_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
