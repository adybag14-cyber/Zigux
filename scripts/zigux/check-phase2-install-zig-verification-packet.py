#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
INSTALL_ZIG = ROOT / "scripts" / "zigux" / "install-zig.py"
ARCHIVE_VERIFICATION_CHECKER = ROOT / "scripts" / "zigux" / "check-lane05-install-zig-archive-verification.py"
POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

BOOTSTRAP_MARKERS = (
    "`scripts/zigux/install-zig.py` is directly readable on current `master` and keeps the pinned-channel archive download, SHA-256 verification, and install-root replay path explicit beside the reminder guards.",
    "`python3 scripts/zigux/install-zig.py --self-test`",
)

SCRIPTS_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
)

REVIEW_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
)

TESTS_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
)

MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
)

INSTALL_ZIG_MARKERS = (
    "policy_channel = load_policy_channel()",
    "channel = args.channel or policy_channel",
    "if channel == policy_channel:",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "if args.resolve_only:",
    "print('ZIG_INSTALL_STATUS=resolved')",
    "actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
)

ARCHIVE_VERIFICATION_MARKERS = (
    'INSTALL_ZIG = Path("scripts/zigux/install-zig.py")',
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
)


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def replace_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_line_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, BOOTSTRAP_NOTES)),
            BOOTSTRAP_MARKERS,
            "MISSING_BOOTSTRAP_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, SCRIPTS_README)),
            SCRIPTS_MARKERS,
            "MISSING_SCRIPTS_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, REVIEW_CHECKLIST)),
            REVIEW_MARKERS,
            "MISSING_REVIEW_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TESTS_README)),
            TESTS_MARKERS,
            "MISSING_TESTS_MARKERS",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, WORKFLOW)),
            WORKFLOW_LINES,
            "MISSING_WORKFLOW_LINES",
            "DUPLICATE_WORKFLOW_LINES",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, MAKEFILE)),
            MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINES",
            "DUPLICATE_MAKEFILE_LINES",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, INSTALL_ZIG)),
            INSTALL_ZIG_MARKERS,
            "MISSING_INSTALL_ZIG_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, ARCHIVE_VERIFICATION_CHECKER)),
            ARCHIVE_VERIFICATION_MARKERS,
            "MISSING_ARCHIVE_VERIFICATION_MARKERS",
        )
    )

    for path in (POLICY,):
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_INSTALL_ZIG_VERIFICATION_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(BOOTSTRAP_MARKERS) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_MARKERS) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(resolve_path(root, INSTALL_ZIG), "\n".join(INSTALL_ZIG_MARKERS) + "\n")
    write_text(
        resolve_path(root, ARCHIVE_VERIFICATION_CHECKER),
        "\n".join(ARCHIVE_VERIFICATION_MARKERS) + "\n",
    )
    write_text(resolve_path(root, POLICY), '{"phase":"Phase 2"}\n')


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = (
        1
        + len(BOOTSTRAP_MARKERS)
        + len(SCRIPTS_MARKERS)
        + len(REVIEW_MARKERS)
        + len(TESTS_MARKERS)
        + len(WORKFLOW_LINES)
        + len(WORKFLOW_LINES)
        + len(MAKEFILE_LINES)
        + len(MAKEFILE_LINES)
        + len(INSTALL_ZIG_MARKERS)
        + len(ARCHIVE_VERIFICATION_MARKERS)
        + 1
    )

    with tempfile.TemporaryDirectory(prefix="zigux_install_zig_verification_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in BOOTSTRAP_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_BOOTSTRAP_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in SCRIPTS_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_SCRIPTS_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in REVIEW_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_REVIEW_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in TESTS_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TESTS_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINES", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINES", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in INSTALL_ZIG_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, INSTALL_ZIG)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_INSTALL_ZIG_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in ARCHIVE_VERIFICATION_MARKERS:
            build_sample_root(root)
            path = resolve_path(root, ARCHIVE_VERIFICATION_CHECKER)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_ARCHIVE_VERIFICATION_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        resolve_path(root, POLICY).unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/zig-toolchain-policy.json") in collect_issues(root)
        checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_INSTALL_ZIG_VERIFICATION_PACKET_SELF_TEST=pass")
    print(f"PHASE2_INSTALL_ZIG_VERIFICATION_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the install-zig archive-verification packet aligned across the current Phase 2 toolchain surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample root for packet replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_INSTALL_ZIG_VERIFICATION_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_INSTALL_ZIG_VERIFICATION_PACKET=pass")
    print(f"PHASE2_INSTALL_ZIG_VERIFICATION_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_INSTALL_ZIG_VERIFICATION_PACKET_INSTALL_MARKER_COUNT={len(INSTALL_ZIG_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
