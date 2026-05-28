#!/usr/bin/env python3
"""Guard the Lane 03 Zig toolchain helper status surface."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CHECKER = Path("scripts/zigux/check-zig-toolchain.py")

FUNCTION_HEADERS = (
    "def describe_missing_archive(",
    "def describe_invalid_explicit_archive_path(archive_path: Path) -> str | None:",
    "def describe_missing_zig(",
    "def emit_policy_summary(policy_path: Path = TOOLCHAIN_POLICY) -> None:",
    "def evaluate_toolchain_version(",
    "def main() -> int:",
)

POLICY_LINES = (
    'print("ZIG_TOOLCHAIN_POLICY_STATUS=present")',
    'print(f"ZIG_TOOLCHAIN_POLICY_PATH={policy_path}")',
    'print(f"ZIG_TOOLCHAIN_PHASE={payload[\'phase\']}")',
    'print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={payload[\'channel\']}")',
    'print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={payload[\'minimum_version\']}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET_COUNT={len(archive_sha256)}")',
    'print("ZIG_TOOLCHAIN_ARCHIVE_TARGETS=" + ",".join(str(target) for target in upgrade_policy["archive_target_scope"]))',
    'print("ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=" + ",".join(str(route) for route in upgrade_policy["required_make_routes"]))',
    'print("ZIG_TOOLCHAIN_PIN_POLICY=" + ("exact" if upgrade_policy["channel_minimum_lockstep"] else "minimum_only"))',
)

ARCHIVE_PRESENCE_MARKERS = (
    'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid")',
    'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_PATH={args.archive or \'unresolved\'}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path or args.archive or \'unresolved\'}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={args.archive_target}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or \'unresolved\'}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={validated_expected_sha}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={actual_sha}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}")',
    'print(f"ZIG_TOOLCHAIN_NOTE={invalid_archive_note}")',
    'print(f"ZIG_TOOLCHAIN_NOTE={message}")',
    'print(f"ZIG_TOOLCHAIN_NOTE={note}")',
    'return 0 if args.allow_missing else 1',
)

TOOLCHAIN_PRESENCE_MARKERS = (
    'print("ZIG_TOOLCHAIN_STATUS=invalid")',
    'print("ZIG_TOOLCHAIN_STATUS=missing")',
    'print(f"ZIG_TOOLCHAIN_STATUS={status}")',
    'print(f"ZIG_TOOLCHAIN_PATH={zig or args.zig or \'unresolved\'}")',
    'print("ZIG_TOOLCHAIN_PATH=unresolved")',
    'print(f"ZIG_TOOLCHAIN_PATH={zig}")',
    'print(f"ZIG_TOOLCHAIN_VERSION={version}")',
    'print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or \'unresolved\'}")',
    'print(f"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}")',
    'print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}")',
    'print("ZIG_TOOLCHAIN_PIN_POLICY=exact")',
    'print("ZIG_TOOLCHAIN_PIN_POLICY=minimum_only")',
    'print("ZIG_TOOLCHAIN_PIN_POLICY=unresolved")',
    'print(f"ZIG_TOOLCHAIN_SEARCH_ROOTS={search_roots_summary}")',
    'print(f"ZIG_TOOLCHAIN_NOTE={exc}")',
    'print(f"ZIG_TOOLCHAIN_NOTE={note}")',
    'exit_code = 0 if status == "present" else 1',
)

SELFTEST_PRESENCE_MARKERS = (
    '("not_pinned", "expected pinned Zig channel 0.17.0-dev.87+9b177a7d2"),',
    '("too_old", None),',
    '"zig not found on PATH or in repo-local toolchain search roots for pinned channel 0.17.0-dev.87+9b177a7d2",',
    '"pinned Zig archive not found in archive search roots",',
    'f"explicit archive path does not exist: {missing_explicit_path}",',
    '"ZIG_TOOLCHAIN_SELF_TEST=pass"',
    'print(f"ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT={case_count}")',
)

BRANCH_ORDER_LINES = (
    "if args.self_test:",
    "if args.policy_only:",
    "if args.archive_only:",
    "if zig is None:",
    'exit_code = 0 if status == "present" else 1',
)

EXPECTED_SELF_TEST_CASE_COUNT = 10


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            if replacement:
                lines[index] = replacement
            else:
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


def swap_exact_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index = next(index for index, line in enumerate(lines) if line.strip() == first)
    second_index = next(index for index, line in enumerate(lines) if line.strip() == second)
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def find_exact_line_indices(text: str, markers: tuple[str, ...]) -> list[int]:
    indices: list[int] = []
    lines = text.splitlines()
    for marker in markers:
        matches = [index for index, line in enumerate(lines) if line.strip() == marker]
        if len(matches) != 1:
            return []
        indices.append(matches[0])
    return indices


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


def collect_presence_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    checker_path = root / CHECKER
    if not checker_path.exists():
        return [("MISSING_REQUIRED_PATH", CHECKER.as_posix())]

    checker_text = read_text(root, CHECKER)
    issues.extend(
        collect_exact_line_issues(
            checker_text,
            FUNCTION_HEADERS,
            "MISSING_FUNCTION_HEADER",
            "DUPLICATE_FUNCTION_HEADER",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            checker_text,
            POLICY_LINES,
            "MISSING_POLICY_LINE",
            "DUPLICATE_POLICY_LINE",
        )
    )
    issues.extend(
        collect_presence_issues(
            checker_text,
            ARCHIVE_PRESENCE_MARKERS,
            "MISSING_ARCHIVE_MARKER",
        )
    )
    issues.extend(
        collect_presence_issues(
            checker_text,
            TOOLCHAIN_PRESENCE_MARKERS,
            "MISSING_TOOLCHAIN_MARKER",
        )
    )
    issues.extend(
        collect_presence_issues(
            checker_text,
            SELFTEST_PRESENCE_MARKERS,
            "MISSING_SELFTEST_MARKER",
        )
    )

    if not issues:
        for code, markers in (
            ("FUNCTION_HEADER_ORDER_MISMATCH", FUNCTION_HEADERS),
            ("BRANCH_ORDER_MISMATCH", BRANCH_ORDER_LINES),
        ):
            indices = find_exact_line_indices(checker_text, markers)
            if indices != sorted(indices):
                issues.append((code, " -> ".join(markers)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOLCHAIN_STATUS_SURFACE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        CHECKER,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "",
                "TOOLCHAIN_POLICY = Path('scripts/zigux/zig-toolchain-policy.json')",
                "",
                "def describe_missing_archive(",
                "    archive_path: Path | None,",
                "    * ,",
                "    explicit_archive: str | None,",
                "    search_roots: list[Path],",
                ") -> tuple[str, str | None]:",
                '    return "pinned Zig archive not found in archive search roots", None',
                "",
                "def describe_invalid_explicit_archive_path(archive_path: Path) -> str | None:",
                '    return f"explicit archive path does not exist: {archive_path}"',
                "",
                "def describe_missing_zig(",
                "    *,",
                "    pinned_channel: str | None,",
                "    search_roots: list[Path],",
                ") -> tuple[str, str]:",
                '    return "zig not found on PATH or in repo-local toolchain search roots for pinned channel 0.17.0-dev.87+9b177a7d2", ""',
                "",
                "def emit_policy_summary(policy_path: Path = TOOLCHAIN_POLICY) -> None:",
                *[f"    {line}" for line in POLICY_LINES],
                "",
                "def evaluate_toolchain_version(",
                "    version: str,",
                "    min_version_raw: str,",
                "    expected_channel_raw: str | None = None,",
                ") -> tuple[str, str | None]:",
                '    return "present", None',
                "",
                "def run_self_test() -> int:",
                *[f"    {line}" for line in SELFTEST_PRESENCE_MARKERS],
                "    return 0",
                "",
                "def main() -> int:",
                "    args = type('Args', (), {'self_test': False, 'policy_only': False, 'archive_only': False, 'allow_missing': False, 'archive': None, 'archive_target': None, 'min_version': None, 'zig': None})()",
                "    zig = None",
                "    archive_path = Path('archive.tar.xz')",
                "    archive_target = 'x86_64-linux'",
                "    expected_sha = '3' * 64",
                "    expected_filename = 'zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz'",
                "    validated_expected_sha = expected_sha",
                "    actual_sha = expected_sha",
                "    search_roots_summary = '/tmp/.zig-toolchain'",
                "    min_version_raw = '0.17.0-dev.87+9b177a7d2'",
                "    expected_channel_raw = '0.17.0-dev.87+9b177a7d2'",
                "    version = '0.17.0-dev.87+9b177a7d2'",
                "    status = 'present'",
                "    note = None",
                "    message = 'pinned Zig archive not found in archive search roots'",
                "    invalid_archive_note = 'bad archive'",
                "    exc = ValueError('bad zig')",
                "    if args.self_test:",
                "        return run_self_test()",
                "    if args.policy_only:",
                "        emit_policy_summary()",
                "        return 0",
                "    if args.archive_only:",
                *[f"        {line}" for line in ARCHIVE_PRESENCE_MARKERS],
                "        return 0",
                "    if zig is None:",
                *[f"        {line}" for line in TOOLCHAIN_PRESENCE_MARKERS[:-1]],
                "        return 0",
                f"    {TOOLCHAIN_PRESENCE_MARKERS[-1]}",
                "    return 0",
                "",
                'if __name__ == "__main__":',
                "    raise SystemExit(main())",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_status_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        checker_path = root / CHECKER
        checker_path.unlink()
        assert ("MISSING_REQUIRED_PATH", CHECKER.as_posix()) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        checker_path = root / CHECKER
        checker_path.write_text(replace_exact_line(checker_path.read_text(encoding="utf-8"), POLICY_LINES[0]), encoding="utf-8")
        assert ("MISSING_POLICY_LINE", POLICY_LINES[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        checker_path = root / CHECKER
        checker_path.write_text(replace_exact_line(checker_path.read_text(encoding="utf-8"), ARCHIVE_PRESENCE_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_ARCHIVE_MARKER", ARCHIVE_PRESENCE_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        checker_path = root / CHECKER
        checker_path.write_text(replace_exact_line(checker_path.read_text(encoding="utf-8"), TOOLCHAIN_PRESENCE_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_TOOLCHAIN_MARKER", TOOLCHAIN_PRESENCE_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        checker_path = root / CHECKER
        checker_path.write_text(replace_exact_line(checker_path.read_text(encoding="utf-8"), SELFTEST_PRESENCE_MARKERS[-1]), encoding="utf-8")
        assert ("MISSING_SELFTEST_MARKER", SELFTEST_PRESENCE_MARKERS[-1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        checker_path = root / CHECKER
        checker_path.write_text(
            swap_exact_lines(checker_path.read_text(encoding="utf-8"), FUNCTION_HEADERS[0], FUNCTION_HEADERS[1]),
            encoding="utf-8",
        )
        assert any(code == "FUNCTION_HEADER_ORDER_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        checker_path = root / CHECKER
        checker_path.write_text(
            swap_exact_lines(checker_path.read_text(encoding="utf-8"), BRANCH_ORDER_LINES[1], BRANCH_ORDER_LINES[2]),
            encoding="utf-8",
        )
        assert any(code == "BRANCH_ORDER_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        checker_path = root / CHECKER
        checker_path.write_text(replace_exact_line(checker_path.read_text(encoding="utf-8"), FUNCTION_HEADERS[-1]), encoding="utf-8")
        assert ("MISSING_FUNCTION_HEADER", FUNCTION_HEADERS[-1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        checker_path = root / CHECKER
        checker_path.write_text(duplicate_exact_line(checker_path.read_text(encoding="utf-8"), POLICY_LINES[-1]), encoding="utf-8")
        assert ("DUPLICATE_POLICY_LINE", f"{POLICY_LINES[-1]}:count=2") in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT, checks
    print("PHASE2_TOOLCHAIN_STATUS_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_STATUS_SURFACE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 03 Zig toolchain helper keeps its policy, archive, and toolchain status surface aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like sample root and exit")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_self_test_root(args.write_sample_root.resolve())
        print("PHASE2_TOOLCHAIN_STATUS_SURFACE_SAMPLE_ROOT=pass")
        print(f"PHASE2_TOOLCHAIN_STATUS_SURFACE_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_STATUS_SURFACE=pass")
    print(f"PHASE2_TOOLCHAIN_STATUS_SURFACE_FUNCTION_HEADER_COUNT={len(FUNCTION_HEADERS)}")
    print(f"PHASE2_TOOLCHAIN_STATUS_SURFACE_POLICY_LINE_COUNT={len(POLICY_LINES)}")
    print(f"PHASE2_TOOLCHAIN_STATUS_SURFACE_ARCHIVE_MARKER_COUNT={len(ARCHIVE_PRESENCE_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_STATUS_SURFACE_TOOLCHAIN_MARKER_COUNT={len(TOOLCHAIN_PRESENCE_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_STATUS_SURFACE_SELFTEST_MARKER_COUNT={len(SELFTEST_PRESENCE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
