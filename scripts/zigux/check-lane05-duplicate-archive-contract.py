#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_CHECKER = "scripts/zigux/check-zig-toolchain.py"
README = "third_party/README.md"
POLICY = "scripts/zigux/zig-toolchain-policy.json"

REQUIRED_PATHS = (
    TOOLCHAIN_CHECKER,
    README,
    POLICY,
)

REQUIRED_CHECKER_MARKERS = (
    "def archive_name_matches_policy(path_name: str, expected_filename: str) -> bool:",
    "return path_name == expected_filename",
    "expect_equal(resolve_policy_archive(root=root, policy_path=policy_path), (\"x86_64-linux\", None))",
    "\"expected archive filename zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz for x86_64-linux, got zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz\"",
    "workspace_archive_path.write_bytes(b\"zigux-archive-drift\")",
)

FORBIDDEN_CHECKER_MARKERS = (
    "return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)",
    "if archive_name_has_duplicate_suffix(child.name, expected_filename):",
    "expect_equal(resolve_policy_archive(root=root, policy_path=policy_path), (\"x86_64-linux\", duplicate_archive_path))",
)

README_MARKERS = (
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` in this directory",
)

EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_SHA = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"


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


def load_policy(root: Path) -> dict[str, object]:
    policy_path = root / POLICY
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {policy_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid toolchain policy payload in {policy_path}: expected object")
    return payload


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    checker = read_text(root, TOOLCHAIN_CHECKER)
    readme = read_text(root, README)
    try:
        payload = load_policy(root)
    except SystemExit as exc:
        issues.append(("INVALID_POLICY_PAYLOAD", str(exc)))
        return issues

    for marker in REQUIRED_CHECKER_MARKERS:
        if marker not in checker:
            issues.append(("MISSING_CHECKER_MARKER", marker))

    for marker in FORBIDDEN_CHECKER_MARKERS:
        if marker in checker:
            issues.append(("FORBIDDEN_CHECKER_MARKER", marker))

    for marker in README_MARKERS:
        if marker not in readme:
            issues.append(("MISSING_ARCHIVE_README_MARKER", marker))

    if payload.get("channel") != EXPECTED_CHANNEL:
        issues.append(("POLICY_MISMATCH", f"channel={payload.get('channel')!r}"))
    if payload.get("minimum_version") != EXPECTED_CHANNEL:
        issues.append(("POLICY_MISMATCH", f"minimum_version={payload.get('minimum_version')!r}"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_POLICY_FIELD", "archive_sha256"))
    elif archive_sha256.get("x86_64-linux") != EXPECTED_SHA:
        issues.append(
            (
                "POLICY_MISMATCH",
                f"archive_sha256.x86_64-linux={archive_sha256.get('x86_64-linux')!r}",
            )
        )

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
    else:
        if upgrade_policy.get("archive_target_scope") != ["x86_64-linux"]:
            issues.append(
                (
                    "POLICY_MISMATCH",
                    f"archive_target_scope={upgrade_policy.get('archive_target_scope')!r}",
                )
            )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("LANE05_DUPLICATE_ARCHIVE_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        TOOLCHAIN_CHECKER,
        "\n".join(
            (
                "def archive_name_matches_policy(path_name: str, expected_filename: str) -> bool:",
                "    return path_name == expected_filename",
                "",
                "def run_self_test() -> int:",
                "    expect_equal(resolve_policy_archive(root=root, policy_path=policy_path), (\"x86_64-linux\", None))",
                "    expect_equal(",
                "        validate_policy_archive(duplicate_archive_path, \"x86_64-linux\", policy_path=policy_path),",
                "        (",
                "            \"mismatch\",",
                "            \"expected archive filename zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz for x86_64-linux, got zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz\",",
                "            expected_archive_sha,",
                "            expected_archive_sha,",
                "        ),",
                "    )",
                "    workspace_archive_path.write_bytes(b\"zigux-archive-drift\")",
                "",
            )
        ),
    )
    write_text(
        root,
        README,
        "\n".join(
            (
                "# Zigux third-party archives",
                "",
                "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
                "- do not keep duplicate-suffix copies such as `zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` in this directory",
                "",
            )
        ),
    )
    write_text(
        root,
        POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {"x86_64-linux": EXPECTED_SHA},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0

    with tempfile.TemporaryDirectory(prefix="lane05_duplicate_archive_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            TOOLCHAIN_CHECKER,
            read_text(root, TOOLCHAIN_CHECKER).replace(
                "return path_name == expected_filename\n",
                "return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)\n",
                1,
            ),
        )
        assert (
            "FORBIDDEN_CHECKER_MARKER",
            "return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, README, "# Zigux third-party archives\n")
        assert (
            "MISSING_ARCHIVE_README_MARKER",
            README_MARKERS[1],
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        payload = load_policy(root)
        payload["archive_sha256"]["x86_64-linux"] = "0" * 64
        write_text(root, POLICY, json.dumps(payload, indent=2) + "\n")
        assert (
            "POLICY_MISMATCH",
            "archive_sha256.x86_64-linux='0000000000000000000000000000000000000000000000000000000000000000'",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, TOOLCHAIN_CHECKER, "placeholder\n")
        assert (
            "MISSING_CHECKER_MARKER",
            REQUIRED_CHECKER_MARKERS[0],
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, POLICY, "{not-json}\n")
        issues = collect_issues(root)
        assert any(code == "INVALID_POLICY_PAYLOAD" for code, _ in issues)
        checks += 1

    print("LANE05_DUPLICATE_ARCHIVE_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_DUPLICATE_ARCHIVE_CONTRACT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 duplicate-suffix archive rejection stays aligned across the toolchain checker, policy, and archive README."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="write a passing sample root for replay checks")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE05_DUPLICATE_ARCHIVE_CONTRACT=pass")
    print(f"LANE05_DUPLICATE_ARCHIVE_CONTRACT_REQUIRED_FILE_COUNT={len(REQUIRED_PATHS)}")
    print(f"LANE05_DUPLICATE_ARCHIVE_CONTRACT_MARKER_COUNT={len(REQUIRED_CHECKER_MARKERS) + len(README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
