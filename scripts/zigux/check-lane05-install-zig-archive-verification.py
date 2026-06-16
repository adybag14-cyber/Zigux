#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
INSTALL_ZIG = Path("scripts/zigux/install_zig.zig")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

INSTALL_ZIG_MARKERS = (
    "pub fn loadPolicyArchiveSha256(",
    "expected_archive_sha256 = try loadPolicyArchiveSha256(io, allocator, policy_path, resolved.target_key)",
                "const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator)",
                "if (expected_archive_sha256) |digest| {",
    "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
    "ZIG_INSTALL_ARCHIVE_SHA256={s}",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified",
    "const extracted_name = try extractArchive(io, allocator, staged_archive_path, extract_root)",
    "try copyDirRecursive(io, extracted_root, final_root)",
)

EXACT_COUNT_MARKERS = (
    "expected_archive_sha256 = try loadPolicyArchiveSha256(io, allocator, policy_path, resolved.target_key)",
    "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified",
)

ORDERED_MARKERS = (
    (
        "const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator)",
        "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
    ),
    (
        "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
        "const extracted_name = try extractArchive(io, allocator, staged_archive_path, extract_root)",
    ),
    (
        "const extracted_name = try extractArchive(io, allocator, staged_archive_path, extract_root)",
        "try copyDirRecursive(io, extracted_root, final_root)",
    ),
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
                "pub fn loadPolicyArchiveSha256(io: std.Io, allocator: std.mem.Allocator, policy_path: []const u8, target_key: []const u8) !?[]const u8 {",
                "    _ = .{ io, allocator, policy_path, target_key };",
                "    return '3' ** 64;",
                "}",
                "",
                "pub fn verifyArchiveSha256(io: std.Io, allocator: std.mem.Allocator, path: []const u8, expected_sha256: []const u8) ![]const u8 {",
                "    _ = .{ io, allocator, path };",
                "    return expected_sha256;",
                "}",
                "",
                "pub fn stageArchive(io: std.Io, local_archive: ?[]const u8, tarball_url: []const u8, archive_path: []const u8, allocator: std.mem.Allocator) !void {",
                "    _ = .{ io, local_archive, tarball_url, archive_path, allocator };",
                "}",
                "",
                "pub fn extractArchive(io: std.Io, allocator: std.mem.Allocator, archive_path: []const u8, dest_path: []const u8) ![]const u8 {",
                "    _ = .{ io, allocator, archive_path };",
                "    return dest_path;",
                "}",
                "",
                "pub fn copyDirRecursive(io: std.Io, source: []const u8, destination: []const u8) !void {",
                "    _ = .{ io, source, destination };",
                "}",
                "",
                "pub fn main() !void {",
                "    const io = undefined;",
                "    const allocator = undefined;",
                "    const policy_path = \"scripts/zigux/zig-toolchain-policy.json\";",
                "    const resolved = .{ .target_key = \"x86_64-linux\", .tarball_url = \"https://example.invalid/archive.tar.xz\" };",
                "    const expanded_archive: ?[]const u8 = null;",
                "    const staged_archive_path = \"archive.tar.xz\";",
                "    const extract_root = \"tmp/extract\";",
                "    const extracted_root = \"tmp/extract/root\";",
                "    const final_root = \"out\";",
                "    var expected_archive_sha256 = try loadPolicyArchiveSha256(io, allocator, policy_path, resolved.target_key);",
                "    const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator);",
                "    if (expected_archive_sha256) |digest| {",
                "        const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest);",
                "        try std.Io.File.stdout().writer(io, undefined).interface.print(\"ZIG_INSTALL_ARCHIVE_SHA256={s}\\n\", .{actual});",
                "        try std.Io.File.stdout().writer(io, undefined).interface.print(\"ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified\\n\", .{});",
                "    } else {",
                "        try std.Io.File.stdout().writer(io, undefined).interface.print(\"ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified\\n\", .{});",
                "    }",
                "    const extracted_name = try extractArchive(io, allocator, staged_archive_path, extract_root);",
                "    try copyDirRecursive(io, extracted_root, final_root);",
                "    _ = .{ archive_source, extracted_name };",
                "}",
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
                "channel": "0.17.0-dev.877+a3ae499dc",
                "minimum_version": "0.17.0-dev.877+a3ae499dc",
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
                "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
                "",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_INSTALL_MARKER",
            "const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        install_path = root / INSTALL_ZIG
        marker = "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified"
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
                "const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator);\n    if (expected_archive_sha256) |digest| {",
                "if (expected_archive_sha256) |digest| {\n        const actual = try verifyArchiveSha256(io, allocator, staged_archive_path, digest)\n    const archive_source = try stageArchive(io, expanded_archive, resolved.tarball_url, staged_archive_path, allocator);",
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
            raise AssertionError("missing install_zig.zig did not abort")

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
