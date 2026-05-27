#!/usr/bin/env python3
"""Guard the Lane 03 Zig installer retry and resume packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
INSTALLER = ROOT / "scripts" / "zigux" / "install-zig.py"
VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"

INSTALLER_MARKERS = (
    "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}",
    "DOWNLOAD_RETRIES = 4",
    "DOWNLOAD_TIMEOUT = 120.0",
    "MAX_RETRY_DELAY = 30.0",
    "def parse_retry_after(headers) -> float | None:",
    "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:",
    "def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:",
    "'Range': f'bytes={start_offset}-'",
    "def copy_response_chunks(response, destination: Path, *, append: bool) -> None:",
    "def copy_url_to_file_with_curl(",
    "'--retry-all-errors',",
    "'--continue-at',",
    "def copy_url_to_file(",
    "resume_offset = destination.stat().st_size if destination.exists() else 0",
    "request = build_download_request(url, resume_offset)",
    "append = resume_offset > 0 and status == 206",
    "if not append and destination.exists():",
    "def verify_archive_sha256(path: Path, expected_sha256: str) -> str:",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_SELF_TEST=pass')",
)

VALIDATOR_MARKERS = (
    '"scripts/zigux/check-phase2-toolchain-installer-retry-packet.py",',
    '"run: python3 scripts/zigux/check-phase2-toolchain-installer-retry-packet.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-toolchain-installer-retry-packet.py",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-installer-retry-packet.py --self-test",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-installer-retry-packet.py",',
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
)

WORKFLOW_ORDER = (
    WORKFLOW_LINES[0],
    WORKFLOW_LINES[1],
    WORKFLOW_LINES[2],
    WORKFLOW_LINES[3],
    WORKFLOW_LINES[4],
)

WORKFLOW_MARKERS: tuple[str, ...] = ()

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
)

MAKEFILE_ORDER = (
    MAKEFILE_LINES[1],
    MAKEFILE_LINES[2],
    MAKEFILE_LINES[3],
    MAKEFILE_LINES[4],
    MAKEFILE_LINES[5],
)

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(INSTALLER_MARKERS)
    + len(VALIDATOR_MARKERS)
    + len(WORKFLOW_LINES)
    + len(WORKFLOW_LINES)
    + len(MAKEFILE_LINES)
    + 1
    + 1
)


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
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_order_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    lines = text.splitlines()
    previous = -1
    for marker in markers:
        matches = [index for index, line in enumerate(lines) if line.strip() == marker]
        if len(matches) != 1:
            return issues
        index = matches[0]
        if index <= previous:
            issues.append((code, marker))
            break
        previous = index
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    installer_text = read_text(resolve_path(root, INSTALLER))
    for marker in INSTALLER_MARKERS:
        if marker not in installer_text:
            issues.append(("MISSING_INSTALLER_MARKER", marker))

    validator_text = read_text(resolve_path(root, VALIDATOR))
    for marker in VALIDATOR_MARKERS:
        if marker not in validator_text:
            issues.append(("MISSING_VALIDATOR_MARKER", marker))

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
    for marker in WORKFLOW_MARKERS:
        if marker not in workflow_text:
            issues.append(("MISSING_WORKFLOW_MARKER", marker))
    issues.extend(collect_order_issues(workflow_text, WORKFLOW_ORDER, "WORKFLOW_ORDER_DRIFT"))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))
    issues.extend(collect_order_issues(makefile_text, MAKEFILE_ORDER, "MAKEFILE_ORDER_DRIFT"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_TOOLCHAIN_INSTALLER_RETRY_PACKET=fail")
    for code, value in issues:
        print(f"{code}:{value}")
    return 1


def build_current_like_root(root: Path) -> None:
    write_text(resolve_path(root, INSTALLER), "\n".join(INSTALLER_MARKERS) + "\n")
    write_text(resolve_path(root, VALIDATOR), "\n".join(VALIDATOR_MARKERS) + "\n")
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
                "          retry_delay_seconds(",
                "          copy_url_to_file_with_curl(",
                "          copy_url_to_file(",
                "          verify_archive_sha256(",
                *WORKFLOW_LINES,
            )
        )
        + "\n",
    )
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_installer_retry_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_current_like_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in INSTALLER_MARKERS:
            build_current_like_root(root)
            installer_path = resolve_path(root, INSTALLER)
            installer_path.write_text(
                replace_once(installer_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_INSTALLER_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in VALIDATOR_MARKERS:
            build_current_like_root(root)
            validator_path = resolve_path(root, VALIDATOR)
            validator_path.write_text(
                replace_once(validator_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_VALIDATOR_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_current_like_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_current_like_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_current_like_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        build_current_like_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_text = workflow_text.replace(
            WORKFLOW_LINES[2] + "\n" + WORKFLOW_LINES[3],
            WORKFLOW_LINES[3] + "\n" + WORKFLOW_LINES[2],
            1,
        )
        workflow_path.write_text(workflow_text, encoding="utf-8")
        assert ("WORKFLOW_ORDER_DRIFT", WORKFLOW_LINES[3]) in collect_issues(root)
        checks_run += 1

        build_current_like_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_text = makefile_path.read_text(encoding="utf-8")
        makefile_text = makefile_text.replace(
            MAKEFILE_LINES[3] + "\n" + MAKEFILE_LINES[4],
            MAKEFILE_LINES[4] + "\n" + MAKEFILE_LINES[3],
            1,
        )
        makefile_path.write_text(makefile_text, encoding="utf-8")
        assert ("MAKEFILE_ORDER_DRIFT", MAKEFILE_LINES[4]) in collect_issues(root)
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_INSTALLER_RETRY_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_INSTALLER_RETRY_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 03 Zig installer retry and resume packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like sample root and exit")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_current_like_root(args.write_sample_root.resolve())
        print("PHASE2_TOOLCHAIN_INSTALLER_RETRY_PACKET_SAMPLE_ROOT=pass")
        print(f"PHASE2_TOOLCHAIN_INSTALLER_RETRY_PACKET_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_INSTALLER_RETRY_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_INSTALLER_RETRY_PACKET_INSTALLER_MARKER_COUNT={len(INSTALLER_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_INSTALLER_RETRY_PACKET_VALIDATOR_MARKER_COUNT={len(VALIDATOR_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_INSTALLER_RETRY_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_TOOLCHAIN_INSTALLER_RETRY_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
