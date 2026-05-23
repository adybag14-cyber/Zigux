#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
README_PATH = Path("third_party/README.md")

WORKFLOW_MARKERS = (
    'mirror_file=".zig-toolchain/community-mirrors.txt"',
    'rm -f "$archive_path" "$mirror_file"',
    'rm -rf "$extract_root"',
    "try_local_archive() {",
    "try_download() {",
    'rm -f "$archive_path"',
    'done < "$mirror_file"',
)

README_MARKERS = (
    "Before retrying the mirror or direct-download path",
    "clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle",
    "stale partial recovery state is discarded before the next fallback attempt",
)

REQUIRED_LINE_COUNTS = (
    ('mirror_file=".zig-toolchain/community-mirrors.txt"', 1, "mirror-file declaration"),
    ('rm -f "$archive_path" "$mirror_file"', 1, "initial cleanup line"),
    ('rm -rf "$extract_root"', 3, "extract-root cleanup lines"),
    ('rm -f "$archive_path"', 1, "archive cleanup lines"),
)

ORDERED_MARKERS = (
    ('mirror_file=".zig-toolchain/community-mirrors.txt"', 'rm -f "$archive_path" "$mirror_file"', "setup cleanup order"),
    ('rm -f "$archive_path" "$mirror_file"', 'rm -rf "$extract_root"', "setup cleanup order"),
    ('rm -rf "$extract_root"', "try_local_archive() {", "cleanup before local helper"),
    ("try_local_archive() {", "try_download() {", "helper definition order"),
    ('rm -f "$archive_path"', 'rm -rf "$extract_root"', "download failure cleanup order"),
    ('rm -f "$archive_path" "$mirror_file"', 'done < "$mirror_file"', "mirror-file lifecycle order"),
)


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


def require_marker(text: str, marker: str, label: str) -> list[tuple[str, str]]:
    if marker not in text:
        return [("MISSING_MARKER", f"{label}:{marker}")]
    return []


def require_line_count(text: str, marker: str, expected: int, label: str) -> list[tuple[str, str]]:
    actual = count_exact_lines(text, marker)
    if actual != expected:
        return [("UNEXPECTED_LINE_COUNT", f"{label}:{marker}:expected={expected}:actual={actual}")]
    return []


def require_order(text: str, earlier: str, later: str, label: str) -> list[tuple[str, str]]:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        return [("MISSING_ORDER_MARKER", label)]
    if earlier_index >= later_index:
        return [("ORDER_MISMATCH", f"{label}:{earlier} -> {later}")]
    return []


def collect_issues(root: Path) -> list[tuple[str, str]]:
    workflow_text = read_text(root / WORKFLOW_PATH)
    readme_text = read_text(root / README_PATH)
    issues: list[tuple[str, str]] = []

    for marker in WORKFLOW_MARKERS:
        issues.extend(require_marker(workflow_text, marker, "workflow"))
    for marker in README_MARKERS:
        issues.extend(require_marker(readme_text, marker, "readme"))
    for marker, expected, label in REQUIRED_LINE_COUNTS:
        issues.extend(require_line_count(workflow_text, marker, expected, label))
    for earlier, later, label in ORDERED_MARKERS:
        issues.extend(require_order(workflow_text, earlier, later, label))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("LANE05_SETUP_CLEANUP_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root / WORKFLOW_PATH,
        """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Setup pinned Zig toolchain
        run: |
          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
          mirror_file=".zig-toolchain/community-mirrors.txt"
          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
          rm -f "$archive_path" "$mirror_file"
          rm -rf "$extract_root"
          try_local_archive() {
            if [ ! -f "$repo_archive_path" ]; then
              return 1
            fi
            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
              tar -xJf "$repo_archive_path" -C .zig-toolchain
              zig_path="$extract_root/zig"
              if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then
                return 0
              fi
            fi
            rm -rf "$extract_root"
            return 1
          }
          try_download() {
            local url="$1"
            if curl -L --fail "$url" -o "$archive_path"; then
              if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
                tar -xJf "$archive_path" -C .zig-toolchain
                zig_path="$extract_root/zig"
                if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then
                  return 0
                fi
              fi
              rm -f "$archive_path"
              rm -rf "$extract_root"
            fi
            return 1
          }
          if try_local_archive; then
            download_success=1
          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
            while IFS= read -r mirror_url; do
              [ -n "$mirror_url" ] || continue
              if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
                download_success=1
                break
              fi
            done < "$mirror_file"
          fi
          if [ "$download_success" -ne 1 ]; then
            if try_download "$ZIGUX_ZIG_URL"; then
              download_success=1
            fi
          fi
""",
    )
    write_text(
        root / README_PATH,
        """# Zigux third-party archives

Before retrying the mirror or direct-download path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.
""",
    )


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="lane05_setup_cleanup_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(
            root / WORKFLOW_PATH,
            replace_once(
                read_text(root / WORKFLOW_PATH),
                'mirror_file=".zig-toolchain/community-mirrors.txt"\n',
                "",
            ),
        )
        assert ("MISSING_MARKER", 'workflow:mirror_file=".zig-toolchain/community-mirrors.txt"') in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root / WORKFLOW_PATH,
            replace_once(
                read_text(root / WORKFLOW_PATH),
                '          rm -f "$archive_path" "$mirror_file"\n',
                "",
            ),
        )
        assert any(code == "UNEXPECTED_LINE_COUNT" and "initial cleanup line" in value for code, value in collect_issues(root))
        checks += 1

        build_sample_root(root)
        write_text(
            root / WORKFLOW_PATH,
            replace_once(
                read_text(root / WORKFLOW_PATH),
                '            rm -rf "$extract_root"\n',
                "",
            ),
        )
        assert any(code == "UNEXPECTED_LINE_COUNT" and "extract-root cleanup lines" in value for code, value in collect_issues(root))
        checks += 1

        build_sample_root(root)
        write_text(
            root / WORKFLOW_PATH,
            replace_once(
                read_text(root / WORKFLOW_PATH),
                '              rm -f "$archive_path"\n',
                "",
            ),
        )
        assert any(code == "UNEXPECTED_LINE_COUNT" and "archive cleanup lines" in value for code, value in collect_issues(root))
        checks += 1

        build_sample_root(root)
        write_text(
            root / README_PATH,
            replace_once(
                read_text(root / README_PATH),
                "stale partial recovery state is discarded before the next fallback attempt.\n",
                "",
            ),
        )
        assert any(code == "MISSING_MARKER" and "readme:" in value for code, value in collect_issues(root))
        checks += 1

    print("LANE05_SETUP_CLEANUP_PACKET_SELF_TEST=pass")
    print(f"LANE05_SETUP_CLEANUP_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 setup block clears stale archive, mirror-cache, and extract state across fallback retries."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like sample root and exit")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"LANE05_SETUP_CLEANUP_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE05_SETUP_CLEANUP_PACKET=pass")
    print(f"LANE05_SETUP_CLEANUP_PACKET_WORKFLOW_MARKER_COUNT={len(WORKFLOW_MARKERS)}")
    print(f"LANE05_SETUP_CLEANUP_PACKET_README_MARKER_COUNT={len(README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
