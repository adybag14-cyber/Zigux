#!/usr/bin/env python3
"""Guard the pinned-toolchain bootstrap fallback order on current master."""

from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"


@dataclass(frozen=True)
class OrderedMarker:
    text: str
    occurrence: int = 1


ORDERED_SETUP_MARKERS = (
    OrderedMarker('      - name: Setup pinned Zig toolchain'),
    OrderedMarker('          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"'),
    OrderedMarker('          repo_archive_parts_dir="${repo_archive_path}.parts"'),
    OrderedMarker('          try_local_archive() {'),
    OrderedMarker('              python3 scripts/zigux/stage-pinned-zig-archive.py                 --root "$GITHUB_WORKSPACE"                 --parts-dir "$repo_archive_parts_dir" || return 1'),
    OrderedMarker(
        '            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then'
    ),
    OrderedMarker('          try_download() {'),
    OrderedMarker('          download_success=0'),
    OrderedMarker('          if try_local_archive; then'),
    OrderedMarker('          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then'),
    OrderedMarker('            while IFS= read -r mirror_url; do'),
    OrderedMarker(
        '              if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then'
    ),
    OrderedMarker('          if [ "$download_success" -ne 1 ]; then', 1),
    OrderedMarker('            if try_download "$ZIGUX_ZIG_URL"; then'),
    OrderedMarker('          if [ "$download_success" -ne 1 ]; then', 2),
    OrderedMarker(
        "            echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2"
    ),
)

COUNTED_SETUP_MARKERS = (
    ('          rm -f "$archive_path" "$mirror_file"', 1),
    ('          rm -rf "$extract_root"', 1),
    ('            rm -rf "$extract_root"', 1),
    ('              rm -rf "$extract_root"', 1),
    ('              rm -f "$archive_path"', 1),
    ('                return 0', 1),
    ('                  return 0', 1),
)

EXPECTED_ARCHIVE_TARGET_SCOPE = ["x86_64-linux"]
EXPECTED_REQUIRED_MAKE_ROUTES = [
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
]
EXPECTED_SELF_TEST_CASE_COUNT = 14


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


def locate_nth_line(lines: list[str], marker: str, occurrence: int) -> int | None:
    seen = 0
    for index, line in enumerate(lines):
        if line == marker:
            seen += 1
            if seen == occurrence:
                return index
    return None


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


def extract_setup_block(workflow_text: str) -> list[str]:
    lines = workflow_text.splitlines()
    start = locate_nth_line(lines, '      - name: Setup pinned Zig toolchain', 1)
    if start is None:
        raise SystemExit("required workflow step missing: Setup pinned Zig toolchain")

    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith("      - name: ") and line != '      - name: Setup pinned Zig toolchain':
            end = index
            break
    return lines[start:end]


def collect_setup_issues(workflow_text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    setup_lines = extract_setup_block(workflow_text)
    setup_text = "\n".join(setup_lines) + "\n"

    positions: list[int] = []
    for marker in ORDERED_SETUP_MARKERS:
        count = count_exact_lines(setup_text, marker.text)
        if count < marker.occurrence:
            issues.append(("MISSING_SETUP_MARKER", f"{marker.text}:occurrence={marker.occurrence}"))
            continue
        expected_count = sum(1 for candidate in ORDERED_SETUP_MARKERS if candidate.text == marker.text)
        if marker.occurrence == 1 and count != expected_count:
            issues.append(("DUPLICATE_SETUP_MARKER", f"{marker.text}:count={count}"))
            continue
        position = locate_nth_line(setup_lines, marker.text, marker.occurrence)
        if position is None:
            issues.append(("MISSING_SETUP_MARKER", f"{marker.text}:occurrence={marker.occurrence}"))
            continue
        positions.append(position)

    for index in range(1, len(positions)):
        if positions[index] <= positions[index - 1]:
            issues.append(
                (
                    "MISORDERED_SETUP_MARKER",
                    f"{ORDERED_SETUP_MARKERS[index - 1].text} -> {ORDERED_SETUP_MARKERS[index].text}",
                )
            )

    for marker, expected_count in COUNTED_SETUP_MARKERS:
        count = count_exact_lines(setup_text, marker)
        if count != expected_count:
            issues.append(("INVALID_SETUP_COUNT", f"{marker}:expected={expected_count}:actual={count}"))

    return issues


def collect_policy_issues(policy_text: str) -> list[tuple[str, str]]:
    try:
        payload = json.loads(policy_text)
    except json.JSONDecodeError as exc:
        return [("INVALID_POLICY_JSON", exc.msg)]

    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", "expected object")]

    upgrade_policy = payload.get("upgrade_policy")
    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(upgrade_policy, dict):
        return [("INVALID_POLICY_FIELD", "upgrade_policy")]
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        return [("INVALID_POLICY_FIELD", "archive_sha256")]

    issues: list[tuple[str, str]] = []
    archive_targets = upgrade_policy.get("archive_target_scope")
    if archive_targets != EXPECTED_ARCHIVE_TARGET_SCOPE:
        issues.append(("INVALID_ARCHIVE_TARGET_SCOPE", repr(archive_targets)))
    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("INVALID_CHANNEL_MINIMUM_LOCKSTEP", repr(upgrade_policy.get("channel_minimum_lockstep"))))
    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != EXPECTED_REQUIRED_MAKE_ROUTES:
        issues.append(("INVALID_REQUIRED_MAKE_ROUTES", repr(required_make_routes)))
    if archive_targets == EXPECTED_ARCHIVE_TARGET_SCOPE:
        missing_targets = [target for target in EXPECTED_ARCHIVE_TARGET_SCOPE if target not in archive_sha256]
        if missing_targets:
            issues.append(("MISSING_ARCHIVE_SHA_TARGET", ",".join(missing_targets)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    policy_text = read_text(resolve_path(root, TOOLCHAIN_POLICY))
    issues = collect_setup_issues(workflow_text)
    issues.extend(collect_policy_issues(policy_text))
    return issues


def build_sample_root(root: Path) -> None:
    write_text(
        resolve_path(root, WORKFLOW),
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Setup pinned Zig toolchain",
                "        run: |",
                "          set -euxo pipefail",
                '          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
                '          repo_archive_parts_dir="${repo_archive_path}.parts"',
                '          try_local_archive() {',
                '            if [ ! -f "$repo_archive_path" ]; then',
                '              if [ ! -d "$repo_archive_parts_dir" ]; then',
                "                return 1",
                "              fi",
                '              python3 scripts/zigux/stage-pinned-zig-archive.py                 --root "$GITHUB_WORKSPACE"                 --parts-dir "$repo_archive_parts_dir" || return 1',
                "            fi",
                '            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
                '              tar -xJf "$repo_archive_path" -C .zig-toolchain',
                '              zig_path="$extract_root/zig"',
                '              if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
                "                return 0",
                "              fi",
                "            fi",
                '            rm -rf "$extract_root"',
                "            return 1",
                "          }",
                '          try_download() {',
                '            local url="$1"',
                '            if curl -L --fail "$url" -o "$archive_path"; then',
                '              if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
                '                tar -xJf "$archive_path" -C .zig-toolchain',
                '                zig_path="$extract_root/zig"',
                '                if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
                "                  return 0",
                "                fi",
                "              fi",
                '              rm -f "$archive_path"',
                '              rm -rf "$extract_root"',
                "            fi",
                "            return 1",
                "          }",
                "          download_success=0",
                '          rm -f "$archive_path" "$mirror_file"',
                '          rm -rf "$extract_root"',
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
                '          if [ "$download_success" -ne 1 ]; then',
                '            if try_download "$ZIGUX_ZIG_URL"; then',
                "              download_success=1",
                "            fi",
                "          fi",
                '          if [ "$download_success" -ne 1 ]; then',
                "            echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
                "            exit 1",
                "          fi",
                "      - name: Compile current scripts",
                "        run: python3 -m py_compile scripts/zigux/check-zig-toolchain.py",
            )
        )
        + "\n",
    )
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
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
                    "archive_target_scope": EXPECTED_ARCHIVE_TARGET_SCOPE,
                    "required_make_routes": EXPECTED_REQUIRED_MAKE_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane03_toolchain_fallback_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), "          if try_local_archive; then"),
            encoding="utf-8",
        )
        assert ("MISSING_SETUP_MARKER", "          if try_local_archive; then:occurrence=1") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                '              python3 scripts/zigux/stage-pinned-zig-archive.py                 --root "$GITHUB_WORKSPACE"                 --parts-dir "$repo_archive_parts_dir" || return 1',
            ),
            encoding="utf-8",
        )
        assert any(
            code == "MISSING_SETUP_MARKER" and "stage-pinned-zig-archive.py" in value
            for code, value in collect_issues(root)
        )
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            duplicate_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
            ),
            encoding="utf-8",
        )
        assert any(code == "DUPLICATE_SETUP_MARKER" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        lines = workflow_path.read_text(encoding="utf-8").splitlines()
        local_index = lines.index("          if try_local_archive; then")
        mirror_index = lines.index('          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then')
        local_line = lines.pop(local_index)
        if local_index < mirror_index:
            mirror_index -= 1
        lines.insert(mirror_index + 1, local_line)
        workflow_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        assert any(code == "MISORDERED_SETUP_MARKER" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                "            echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
            ),
            encoding="utf-8",
        )
        assert any(code == "MISSING_SETUP_MARKER" and "failed to install" in value for code, value in collect_issues(root))
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), '          rm -rf "$extract_root"'),
            encoding="utf-8",
        )
        assert any(code == "INVALID_SETUP_COUNT" and 'rm -rf "$extract_root"' in value for code, value in collect_issues(root))
        checks += 1

        build_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "aarch64-linux"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_ARCHIVE_TARGET_SCOPE", "['x86_64-linux', 'aarch64-linux']") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["channel_minimum_lockstep"] = False
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CHANNEL_MINIMUM_LOCKSTEP", "False") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_REQUIRED_MAKE_ROUTES", "['phase2-toolchain']") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["archive_sha256"] = {}
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_FIELD", "archive_sha256") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_path.write_text("{not-json}\n", encoding="utf-8")
        assert any(code == "INVALID_POLICY_JSON" for code, _ in collect_issues(root))
        checks += 1

        for path in (WORKFLOW, TOOLCHAIN_POLICY):
            build_sample_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT, checks
    print("LANE03_TOOLCHAIN_FALLBACK_ORDER_SELF_TEST=pass")
    print(f"LANE03_TOOLCHAIN_FALLBACK_ORDER_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the pinned-toolchain bootstrap block keeps its local-first, mirror-second, canonical-last fallback order."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="write a current-like sample root and exit")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print("LANE03_TOOLCHAIN_FALLBACK_ORDER_SAMPLE_ROOT=pass")
        print(f"LANE03_TOOLCHAIN_FALLBACK_ORDER_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("LANE03_TOOLCHAIN_FALLBACK_ORDER=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("LANE03_TOOLCHAIN_FALLBACK_ORDER=pass")
    print(f"LANE03_TOOLCHAIN_FALLBACK_ORDER_MARKER_COUNT={len(ORDERED_SETUP_MARKERS)}")
    print("LANE03_TOOLCHAIN_FALLBACK_ARCHIVE_TARGET_SCOPE=" + ",".join(EXPECTED_ARCHIVE_TARGET_SCOPE))
    print("LANE03_TOOLCHAIN_FALLBACK_REQUIRED_MAKE_ROUTES=" + ",".join(EXPECTED_REQUIRED_MAKE_ROUTES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
