#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
INSTALL_ZIG_PATH = Path("scripts/zigux/install-zig.py")
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")
THIRD_PARTY_README_PATH = Path("third_party/README.md")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

WORKFLOW_MARKERS = (
    "- name: Setup pinned Zig toolchain",
    'filename = f"zig-{target}-{channel}.tar.xz"',
    'url = f"https://ziglang.org/builds/{filename}"',
    'archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_parts_dir="${repo_archive_path}.parts"',
    'rm -f "$archive_path" "$mirror_file"',
    'rm -rf "$extract_root"',
    "try_local_archive() {",
    'python3 scripts/zigux/stage-pinned-zig-archive.py',
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    'tar -xJf "$repo_archive_path" -C .zig-toolchain',
    'zig_path="$extract_root/zig"',
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if try_download "$ZIGUX_ZIG_URL"; then',
    "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org",
)

INSTALL_ZIG_MARKERS = (
    "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
    "copy_url_to_file(tarball_url, archive_path)",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
)

EXACT_WORKFLOW_LINE_MARKERS = {
    "- name: Setup pinned Zig toolchain",
    'archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_parts_dir="${repo_archive_path}.parts"',
    'rm -f "$archive_path" "$mirror_file"',
    'rm -rf "$extract_root"',
    "try_local_archive() {",
    'tar -xJf "$repo_archive_path" -C .zig-toolchain',
    'zig_path="$extract_root/zig"',
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if try_download "$ZIGUX_ZIG_URL"; then',
}


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


def require_order(issues: list[tuple[str, str]], text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        return
    if earlier_index >= later_index:
        issues.append(("ORDER_MISMATCH", label))


def load_policy(root: Path) -> dict[str, object]:
    policy_path = root / POLICY_PATH
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {policy_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {policy_path}")
    return payload


def resolve_policy_contract(root: Path) -> dict[str, str]:
    payload = load_policy(root)
    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        raise SystemExit(f"invalid policy channel in {root / POLICY_PATH}")

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise SystemExit(f"invalid policy archive_sha256 in {root / POLICY_PATH}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid policy upgrade_policy in {root / POLICY_PATH}")

    targets = upgrade_policy.get("archive_target_scope")
    if not isinstance(targets, list) or len(targets) != 1 or not isinstance(targets[0], str) or not targets[0].strip():
        raise SystemExit(f"invalid policy archive_target_scope in {root / POLICY_PATH}")

    target = targets[0].strip()
    digest = archive_sha256.get(target)
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        raise SystemExit(f"invalid policy archive_sha256 entry for {target} in {root / POLICY_PATH}")

    return {
        "channel": channel.strip(),
        "target": target,
        "sha256": digest,
        "filename": f"zig-{target}-{channel.strip()}.tar.xz",
    }


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow = read_text(root / WORKFLOW_PATH)
    install_zig = read_text(root / INSTALL_ZIG_PATH)
    stage_helper = read_text(root / STAGE_HELPER_PATH)
    third_party_readme = read_text(root / THIRD_PARTY_README_PATH)
    contract = resolve_policy_contract(root)

    for marker in WORKFLOW_MARKERS:
        if marker in EXACT_WORKFLOW_LINE_MARKERS:
            count = count_exact_lines(workflow, marker)
        else:
            count = workflow.count(marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif marker in EXACT_WORKFLOW_LINE_MARKERS and count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    require_order(
        issues,
        workflow,
        'if try_local_archive; then',
        'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        "local archive before mirror fallback",
    )
    require_order(
        issues,
        workflow,
        'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        'if try_download "$ZIGUX_ZIG_URL"; then',
        "mirror fallback before direct download",
    )
    require_order(
        issues,
        workflow,
        'python3 scripts/zigux/stage-pinned-zig-archive.py',
        'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
        "stage helper before archive verification",
    )
    require_order(
        issues,
        workflow,
        'copy_url_to_file(tarball_url, archive_path)',
        'actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)',
        "download before install-zig sha verification",
    )
    require_order(
        issues,
        install_zig,
        "copy_url_to_file(tarball_url, archive_path)",
        "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
        "install-zig download before sha verification",
    )
    require_order(
        issues,
        install_zig,
        "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
        "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
        "install-zig sha verification before extract",
    )

    for marker in INSTALL_ZIG_MARKERS:
        if marker not in install_zig:
            issues.append(("MISSING_INSTALL_ZIG_MARKER", marker))

    stage_helper_markers = (
        'THIRD_PARTY_DIR = Path("third_party")',
        'duplicate-suffix archive copies',
        'STAGE_PINNED_ZIG_ARCHIVE_TARGET=',
        'STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=',
        'STAGE_PINNED_ZIG_ARCHIVE_STATUS=',
    )
    for marker in stage_helper_markers:
        if marker not in stage_helper:
            issues.append(("MISSING_STAGE_HELPER_MARKER", marker))

    readme_markers = (
        "# Zigux third-party archives",
        f"- target: `{contract['target']}`",
        f"- channel: `{contract['channel']}`",
        f"- file: `third_party/{contract['filename']}`",
        f"- sha256: `{contract['sha256']}`",
        "Bootstrap order",
        "Lane 05 bootstrap first reuses and validates",
        "stages the same pinned payload locally",
        "falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL",
    )
    for marker in readme_markers:
        if marker not in third_party_readme:
            issues.append(("MISSING_THIRD_PARTY_README_MARKER", marker))

    required_make_routes = load_policy(root).get("upgrade_policy", {}).get("required_make_routes")
    if not isinstance(required_make_routes, list) or "phase2-toolchain" not in required_make_routes:
        issues.append(("MISSING_REQUIRED_MAKE_ROUTE", "phase2-toolchain"))
    if not isinstance(required_make_routes, list) or "phase2-validate" not in required_make_routes:
        issues.append(("MISSING_REQUIRED_MAKE_ROUTE", "phase2-validate"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("LANE03_PINNED_TOOLCHAIN_SETUP_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root / POLICY_PATH,
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
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / WORKFLOW_PATH,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Setup pinned Zig toolchain",
                "        run: |",
                "          eval \"$(python3 - <<'PY'",
                '          filename = f"zig-{target}-{channel}.tar.xz"',
                '          url = f"https://ziglang.org/builds/{filename}"',
                "          PY",
                "          )\"",
                '          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
                '          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"',
                '          mirror_file=".zig-toolchain/community-mirrors.txt"',
                '          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
                '          repo_archive_parts_dir="${repo_archive_path}.parts"',
                '          rm -f "$archive_path" "$mirror_file"',
                '          rm -rf "$extract_root"',
                "          try_local_archive() {",
                '            python3 scripts/zigux/stage-pinned-zig-archive.py \\',
                '              --root "$GITHUB_WORKSPACE" \\',
                '              --parts-dir "$repo_archive_parts_dir" || return 1',
                '            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
                '              tar -xJf "$repo_archive_path" -C .zig-toolchain',
                '              zig_path="$extract_root/zig"',
                "              return 0",
                "            fi",
                "            return 1",
                "          }",
                "          try_download() {",
                "            return 0",
                "          }",
                "          if try_local_archive; then",
                "            download_success=1",
                '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
                "            download_success=1",
                "          fi",
                '          if try_download "$ZIGUX_ZIG_URL"; then',
                "            download_success=1",
                "          fi",
                "          echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
            )
        )
        + "\n",
    )
    write_text(
        root / INSTALL_ZIG_PATH,
        "\n".join(
            (
                "from pathlib import Path",
                "",
                "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
                "    return None",
                "",
                "def verify_archive_sha256(path, expected):",
                "    return expected",
                "",
                "def copy_url_to_file(url, path):",
                "    return None",
                "",
                "def extract_archive(path, dest):",
                "    return dest",
                "",
                "def main():",
                "    tarball_url = 'https://example.invalid/zig.tar.xz'",
                "    archive_path = Path('zig.tar.xz')",
                "    tmpdir = Path('tmp')",
                "    expected_archive_sha256 = '3' * 64",
                "    copy_url_to_file(tarball_url, archive_path)",
                "    actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
                "    extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
                "    return actual_archive_sha256, extracted_root",
            )
        )
        + "\n",
    )
    write_text(
        root / STAGE_HELPER_PATH,
        "\n".join(
            (
                'THIRD_PARTY_DIR = Path("third_party")',
                "duplicate-suffix archive copies",
                "STAGE_PINNED_ZIG_ARCHIVE_TARGET=",
                "STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=",
                "STAGE_PINNED_ZIG_ARCHIVE_STATUS=",
            )
        )
        + "\n",
    )
    write_text(
        root / THIRD_PARTY_README_PATH,
        "\n".join(
            (
                "# Zigux third-party archives",
                "",
                "## Current pinned Zig archive contract",
                "",
                "- target: `x86_64-linux`",
                "- channel: `0.17.0-dev.87+9b177a7d2`",
                "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
                "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
                "",
                "## Bootstrap order",
                "",
                "- Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.",
                "- If the exact archive file is absent but `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts` is present, `.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally with `scripts/zigux/stage-pinned-zig-archive.py` before mirror or direct-download fallback.",
                "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 8

    with tempfile.TemporaryDirectory(prefix="lane03_pinned_toolchain_setup_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                'repo_archive_parts_dir="${repo_archive_path}.parts"\n', "", 1
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_WORKFLOW_LINE",
            'repo_archive_parts_dir="${repo_archive_path}.parts"',
        ) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path = root / WORKFLOW_PATH
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "          if try_local_archive; then\n            download_success=1\n          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then\n",
                "          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then\n            download_success=1\n          if try_local_archive; then\n            download_success=1\n",
                1,
            ),
            encoding="utf-8",
        )
        assert ("ORDER_MISMATCH", "local archive before mirror fallback") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        install_path = root / INSTALL_ZIG_PATH
        install_path.write_text(
            install_path.read_text(encoding="utf-8").replace(
                "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert any(code == "MISSING_INSTALL_ZIG_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_sample_root(root)
        install_path = root / INSTALL_ZIG_PATH
        install_path.write_text(
            install_path.read_text(encoding="utf-8").replace(
                "copy_url_to_file(tarball_url, archive_path)\n    actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)\n",
                "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)\n    copy_url_to_file(tarball_url, archive_path)\n",
                1,
            ),
            encoding="utf-8",
        )
        assert ("ORDER_MISMATCH", "install-zig download before sha verification") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        stage_helper_path = root / STAGE_HELPER_PATH
        stage_helper_path.write_text("missing\n", encoding="utf-8")
        assert any(code == "MISSING_STAGE_HELPER_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_sample_root(root)
        readme_path = root / THIRD_PARTY_README_PATH
        readme_path.write_text("# Zigux third-party archives\n", encoding="utf-8")
        assert any(code == "MISSING_THIRD_PARTY_README_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_sample_root(root)
        policy_path = root / POLICY_PATH
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-cross"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_REQUIRED_MAKE_ROUTE", "phase2-toolchain") in collect_issues(root)
        checks_run += 1

    assert checks_run == expected_case_count
    print("LANE03_PINNED_TOOLCHAIN_SETUP_PACKET_SELF_TEST=pass")
    print(f"LANE03_PINNED_TOOLCHAIN_SETUP_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the bootstrap workflow keeps the pinned-toolchain setup packet explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal sample repository root for current-like checker validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"LANE03_PINNED_TOOLCHAIN_SETUP_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE03_PINNED_TOOLCHAIN_SETUP_PACKET=pass")
    print(f"LANE03_PINNED_TOOLCHAIN_SETUP_PACKET_WORKFLOW_MARKER_COUNT={len(WORKFLOW_MARKERS)}")
    print(f"LANE03_PINNED_TOOLCHAIN_SETUP_PACKET_INSTALL_MARKER_COUNT={len(INSTALL_ZIG_MARKERS)}")
    print("LANE03_PINNED_TOOLCHAIN_SETUP_PACKET_REQUIRED_PATH_COUNT=5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())