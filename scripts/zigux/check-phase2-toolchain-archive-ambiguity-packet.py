#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_CHECKER = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"

REQUIRED_MARKERS = (
    "def select_matching_policy_archive(",
    "multiple repo-local pinned archive candidates matched",
    "candidate_target, candidate_path = select_matching_policy_archive(",
    "conflicting_archive_path = duplicate_archive_path.with_name(",
    "expect_raises(",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def collect_issues(text: str) -> list[str]:
    issues: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            issues.append(f"missing:{marker}")
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_checker_text(*, include_helper: bool = True, include_error: bool = True, include_selftest: bool = True) -> str:
    lines = [
        "#!/usr/bin/env python3",
        "def iter_repo_local_archive_candidates():",
        "    return []",
    ]
    if include_helper:
        lines.extend(
            [
                "def select_matching_policy_archive(candidates, *, target, policy_path):",
                "    if len(candidates) > 1:",
                (
                    "        raise ValueError("
                    "\\\"multiple repo-local pinned archive candidates matched\\\""
                    ")"
                    if include_error
                    else
                    "        raise ValueError(\\\"different archive failure\\\")"
                ),
                "    return (target, None)",
            ]
        )
    lines.extend(
        [
            "def resolve_policy_archive():",
            "    candidates = iter_repo_local_archive_candidates()",
            (
                "    candidate_target, candidate_path = select_matching_policy_archive("
                "candidates, target=None, policy_path='policy.json')"
                if include_helper
                else
                "    candidate_target, candidate_path = (None, None)"
            ),
            "    return candidate_target, candidate_path",
        ]
    )
    if include_selftest:
        lines.extend(
            [
                "def run_self_test():",
                "    duplicate_archive_path = Path('zig.tar.xz')",
                "    conflicting_archive_path = duplicate_archive_path.with_name(",
                "        'zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (2).tar.xz'",
                "    )",
                "    expect_raises(",
                "        lambda: resolve_policy_archive(),",
                "        'multiple repo-local pinned archive candidates matched',",
                "    )",
            ]
        )
    return "\n".join(lines) + "\n"


def write_sample_root(root: Path) -> None:
    write_text(
        root / "scripts/zigux/check-zig-toolchain.py",
        build_sample_checker_text(),
    )


def run_self_test() -> int:
    case_count = 0

    healthy = collect_issues(build_sample_checker_text())
    assert healthy == []
    case_count += 1

    missing_helper = collect_issues(build_sample_checker_text(include_helper=False))
    assert any(issue.startswith("missing:def select_matching_policy_archive(") for issue in missing_helper)
    assert any(
        issue.startswith("missing:candidate_target, candidate_path = select_matching_policy_archive(")
        for issue in missing_helper
    )
    case_count += 1

    missing_error = collect_issues(
        build_sample_checker_text(include_error=False, include_selftest=False)
    )
    assert any(issue == "missing:multiple repo-local pinned archive candidates matched" for issue in missing_error)
    case_count += 1

    missing_selftest = collect_issues(build_sample_checker_text(include_selftest=False))
    assert any(
        issue.startswith("missing:conflicting_archive_path = duplicate_archive_path.with_name(")
        for issue in missing_selftest
    )
    case_count += 1

    with tempfile.TemporaryDirectory(prefix="zigux_archive_ambiguity_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        issues = collect_issues(read_text(root / "scripts/zigux/check-zig-toolchain.py"))
        assert issues == []
        case_count += 1

    print("PHASE2_TOOLCHAIN_ARCHIVE_AMBIGUITY_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_ARCHIVE_AMBIGUITY_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Zigux toolchain checker fail-closes on ambiguous repo-local "
            "pinned archive matches instead of silently accepting the first visible copy."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for replay validation.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_TOOLCHAIN_ARCHIVE_AMBIGUITY_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    checker_path = TOOLCHAIN_CHECKER if args.root.resolve() == ROOT else args.root.resolve() / "scripts/zigux/check-zig-toolchain.py"
    issues = collect_issues(read_text(checker_path))
    if issues:
        print("PHASE2_TOOLCHAIN_ARCHIVE_AMBIGUITY_PACKET=fail")
        print(f"PHASE2_TOOLCHAIN_ARCHIVE_AMBIGUITY_PACKET_PATH={checker_path}")
        print("PHASE2_TOOLCHAIN_ARCHIVE_AMBIGUITY_PACKET_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_TOOLCHAIN_ARCHIVE_AMBIGUITY_PACKET_ISSUES_END")
        return 1

    print("PHASE2_TOOLCHAIN_ARCHIVE_AMBIGUITY_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_ARCHIVE_AMBIGUITY_PACKET_PATH={checker_path}")
    print(f"PHASE2_TOOLCHAIN_ARCHIVE_AMBIGUITY_PACKET_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
