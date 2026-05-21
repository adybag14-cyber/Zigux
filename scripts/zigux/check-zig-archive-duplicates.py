#!/usr/bin/env python3
import argparse
import json
import re
import tempfile
from pathlib import Path

ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(r"^(?P<stem>.+) \((?P<copy>\d+)\)(?P<suffix>\.tar\.xz)$")
ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"


def load_policy(policy_path: Path = TOOLCHAIN_POLICY) -> dict[str, object]:
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")
    return payload


def iter_archive_search_roots(root: Path = ROOT) -> list[Path]:
    search_roots: list[Path] = []

    def add_search_root(path: Path) -> None:
        if path not in search_roots:
            search_roots.append(path)

    add_search_root(root / ".zig-toolchain")
    add_search_root(root / "toolchains")
    add_search_root(root / ".toolchains")
    add_search_root(root / "third_party")
    add_search_root(root / "agent_files")

    for parent in root.parents:
        add_search_root(parent / ".toolchains")
        add_search_root(parent / "toolchains")
        add_search_root(parent / "agent_files")

    return search_roots


def policy_archive_filename(target: str, channel: str) -> str:
    return f"zig-{target}-{channel}.tar.xz"


def archive_name_has_duplicate_suffix(path_name: str, expected_filename: str) -> bool:
    if not expected_filename.endswith(".tar.xz"):
        return False
    match = ARCHIVE_DUPLICATE_SUFFIX_RE.fullmatch(path_name)
    if match is None:
        return False
    return match.group("stem") == expected_filename[: -len(".tar.xz")]


def archive_name_matches_policy(path_name: str, expected_filename: str) -> bool:
    return path_name == expected_filename or archive_name_has_duplicate_suffix(path_name, expected_filename)


def find_archive_candidates_for_target(
    target: str,
    *,
    root: Path = ROOT,
    policy_path: Path = TOOLCHAIN_POLICY,
) -> list[Path]:
    payload = load_policy(policy_path)
    channel = str(payload["channel"])
    expected_filename = policy_archive_filename(target, channel)
    candidates: list[Path] = []
    seen: set[Path] = set()

    for base in iter_archive_search_roots(root):
        canonical = base / expected_filename
        if canonical not in seen and canonical.is_file():
            candidates.append(canonical)
            seen.add(canonical)
        if not base.exists():
            continue
        for child in sorted(base.iterdir()):
            if child in seen or not child.is_file():
                continue
            if archive_name_matches_policy(child.name, expected_filename):
                candidates.append(child)
                seen.add(child)
    return candidates


def check_archive_duplicates(
    *,
    root: Path = ROOT,
    policy_path: Path = TOOLCHAIN_POLICY,
) -> tuple[str, list[str]]:
    payload = load_policy(policy_path)
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")
    archive_targets = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_targets, list) or not archive_targets:
        raise ValueError(f"invalid archive_target_scope in {policy_path}")

    findings: list[str] = []
    missing_targets = 0
    for raw_target in archive_targets:
        if not isinstance(raw_target, str) or not raw_target.strip():
            raise ValueError(f"invalid archive target entry in {policy_path}")
        target = raw_target.strip()
        candidates = find_archive_candidates_for_target(target, root=root, policy_path=policy_path)
        if not candidates:
            missing_targets += 1
            findings.append(f"{target}:missing")
            continue
        if len(candidates) == 1:
            findings.append(f"{target}:present:{candidates[0]}")
            continue
        findings.append(f"{target}:duplicate:" + ",".join(str(path) for path in candidates))

    if any(":duplicate:" in finding for finding in findings):
        return "duplicate", findings
    if missing_targets == len(archive_targets):
        return "missing", findings
    return "present", findings


def run_self_test() -> int:
    case_count = 0

    def expect_equal(actual, expected) -> None:
        nonlocal case_count
        assert actual == expected
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="zigux_archive_dupes_") as tmp_dir:
        root = Path(tmp_dir)
        policy_path = root / "scripts" / "zigux" / "zig-toolchain-policy.json"
        policy_path.parent.mkdir(parents=True, exist_ok=True)
        policy_path.write_text(
            json.dumps(
                {
                    "phase": "Phase 2",
                    "channel": "0.17.0-dev.87+9b177a7d2",
                    "minimum_version": "0.17.0-dev.87+9b177a7d2",
                    "archive_sha256": {"x86_64-linux": "3" * 64},
                    "upgrade_policy": {
                        "channel_minimum_lockstep": True,
                        "archive_target_scope": ["x86_64-linux"],
                        "required_make_routes": ["phase2-toolchain"],
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )

        expect_equal(
            archive_name_has_duplicate_suffix(
                "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz",
                "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
            ),
            True,
        )
        expect_equal(
            archive_name_has_duplicate_suffix(
                "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2-copy.tar.xz",
                "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
            ),
            False,
        )

        expect_equal(check_archive_duplicates(root=root, policy_path=policy_path)[0], "missing")

        archive_root = root / "agent_files"
        archive_root.mkdir()
        canonical = archive_root / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
        canonical.write_bytes(b"zigux-archive")
        status, findings = check_archive_duplicates(root=root, policy_path=policy_path)
        expect_equal(status, "present")
        expect_equal(findings, [f"x86_64-linux:present:{canonical}"])

        duplicate = archive_root / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz"
        duplicate.write_bytes(b"zigux-archive")
        status, findings = check_archive_duplicates(root=root, policy_path=policy_path)
        expect_equal(status, "duplicate")
        expect_equal(
            findings,
            [f"x86_64-linux:duplicate:{canonical},{duplicate}"],
        )

    print("ZIG_ARCHIVE_DUPLICATES_SELF_TEST=pass")
    print(f"ZIG_ARCHIVE_DUPLICATES_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check pinned Zig archive search roots for duplicate candidate files.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in archive duplicate checks.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        status, findings = check_archive_duplicates()
    except ValueError as exc:
        print("ZIG_ARCHIVE_DUPLICATES_STATUS=invalid")
        print(f"ZIG_ARCHIVE_DUPLICATES_POLICY_PATH={TOOLCHAIN_POLICY}")
        print(f"ZIG_ARCHIVE_DUPLICATES_NOTE={exc}")
        return 1

    print(f"ZIG_ARCHIVE_DUPLICATES_STATUS={status}")
    print(f"ZIG_ARCHIVE_DUPLICATES_POLICY_PATH={TOOLCHAIN_POLICY}")
    for index, finding in enumerate(findings, start=1):
        print(f"ZIG_ARCHIVE_DUPLICATES_FINDING_{index}={finding}")
    return 1 if status == "duplicate" else 0


if __name__ == "__main__":
    raise SystemExit(main())
