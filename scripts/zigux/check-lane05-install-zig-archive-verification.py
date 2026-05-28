#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
INSTALL_ZIG = Path("scripts/zigux/install-zig.py")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

INSTALL_ZIG_MARKERS = (
    "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "copy_url_to_file(tarball_url, archive_path)",
    "if expected_archive_sha256 is not None:",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
    "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
    "shutil.copytree(extracted_root, final_root)",
)

EXACT_COUNT_MARKERS = (
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
)

ORDERED_MARKERS = (
    ("copy_url_to_file(tarball_url, archive_path)", "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)"),
    ("actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)", "extracted_root = extract_archive(archive_path, tmpdir / 'extract')"),
    ("extracted_root = extract_archive(archive_path, tmpdir / 'extract')", "shutil.copytree(extracted_root, final_root)"),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_policy(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


def count_exact_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_policy_issues(policy: dict[str, object]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    archive_sha256 = policy.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        issues.append(("INVALID_POLICY_FIELD", "archive_sha256"))
        return issues

    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
        return issues

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        issues.append(("INVALID_POLICY_FIELD", "archive_target_scope"))
        return issues

    if len(archive_target_scope) != 1:
        issues.append(("UNEXPECTED_ARCHIVE_TARGET_COUNT", str(len(archive_target_scope))))

    for index, target in enumerate(archive_target_scope):
        if not isinstance(target, str) or not target.strip():
            issues.append(("INVALID_ARCHIVE_TARGET", f"index={index}"))
            continue
        digest = archive_sha256.get(target)
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            issues.append(("INVALID_ARCHIVE_SHA256", target))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    install_text = read_text(root / INSTALL_ZIG)
    policy = read_policy(root / TOOLCHAIN_POLICY)

    for marker in INSTALL_ZIG_MARKERS:
        count = count_exact_occurrences(install_text, marker)
        if count == 0:
            issues.append(("MISSING_INSTALL_MARKER", marker))
        elif marker in EXACT_COUNT_MARKERS and count != 1:
            issues.append(("DUPLICATE_INSTALL_MARKER", f"{marker}:count={count}"))

    for earlier, later in ORDERED_MARKERS:
        earlier_index = install_text.find(earlier)
        later_index = install_text.find(later)
        if earlier_index == -1 or later_index == -1:
            continue
        if earlier_index >= later_index:
            issues.append(("ORDER_MISMATCH", f"{earlier} -> {later}"))

    issues.extend(collect_policy_issues(policy))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(
        root / INSTALL_ZIG,
        "\n".join(
            (
                "from pathlib import Path",
                "import shutil",
                "",
                "TOOLCHAIN_POLICY = Path('scripts/zigux/zig-toolchain-policy.json')",
                "",
                "def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:",
                "    return '3' * 64",
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
                "    target_key = 'x86_64-linux'",
                "    tarball_url = 'https://example.invalid/archive.tar.xz'",
                "    archive_path = Path('archive.tar.xz')",
                "    tmpdir = Path('tmp')",
                "    final_root = Path('out')",
                "    expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
                "    copy_url_to_file(tarball_url, archive_path)",
                "    if expected_archive_sha256 is not None:",
                "        actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
                "        print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')",
                "        print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
                "    else:",
                "        print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
                "    extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
                "    shutil.copytree(extracted_root, final_root)",
                "",
            )
        )
        + "\n",
    )
    write_text(
        root / TOOLCHAIN_POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "3" * 64,
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
    )


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 8

    with tempfile.TemporaryDirectory(prefix="lane05_install_archive_verify_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        install_path = root / INSTALL_ZIG
        install_path.write_text(
            replace_once(
                install_path.read_text(encoding="utf-8"),
                "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
                "",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_INSTALL_MARKER",
            "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        install_path = root / INSTALL_ZIG
        marker = "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')"
        install_path.write_text(
            install_path.read_text(encoding="utf-8") + marker + "\n",
            encoding="utf-8",
        )
        assert ("DUPLICATE_INSTALL_MARKER", f"{marker}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        install_path = root / INSTALL_ZIG
        install_path.write_text(
            replace_once(
                install_path.read_text(encoding="utf-8"),
                "copy_url_to_file(tarball_url, archive_path)\n    if expected_archive_sha256 is not None:",
                "if expected_archive_sha256 is not None:\n        actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)\n    copy_url_to_file(tarball_url, archive_path)",
            ),
            encoding="utf-8",
        )
        assert any(code == "ORDER_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        policy_path = root / TOOLCHAIN_POLICY
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["archive_sha256"] = {}
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_FIELD", "archive_sha256") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = root / TOOLCHAIN_POLICY
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "aarch64-linux"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("UNEXPECTED_ARCHIVE_TARGET_COUNT", "2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = root / TOOLCHAIN_POLICY
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["archive_sha256"]["x86_64-linux"] = "short"
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_ARCHIVE_SHA256", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (root / INSTALL_ZIG).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing install-zig.py did not abort")

    assert checks_run == expected_case_count
    print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST=pass")
    print(f"LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that install-zig keeps the policy-backed archive verification path explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION=pass")
    print(f"LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_MARKER_COUNT={len(INSTALL_ZIG_MARKERS)}")
    print("LANE05_INSTALL_ZIG_ARCHIVE_VERIFICATION_TARGET_COUNT=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
