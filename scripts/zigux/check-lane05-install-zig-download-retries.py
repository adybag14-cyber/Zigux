#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
INSTALL_ZIG_PATH = Path("scripts/zigux/install-zig.py")

REQUIRED_MARKERS = (
    "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}",
    "DOWNLOAD_RETRIES = 4",
    "DOWNLOAD_TIMEOUT = 120.0",
    "MAX_RETRY_DELAY = 30.0",
    "def parse_retry_after(headers) -> float | None:",
    "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:",
    "return min(parsed_retry_after, MAX_RETRY_DELAY)",
    "return min(default_delay, MAX_RETRY_DELAY)",
    "def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:",
    "return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})",
    "def copy_url_to_file_with_curl(",
    "'--retry-all-errors',",
    "'--continue-at',",
    "'-',",
    "'--speed-limit',",
    "'--speed-time',",
    "resume_offset = destination.stat().st_size if destination.exists() else 0",
    "request = build_download_request(url, resume_offset)",
    "append = resume_offset > 0 and status == 206",
    "copy_response_chunks(response, destination, append=append)",
    "    except (TimeoutError, urllib.error.URLError):\n        if not is_explicit_version(channel):\n            raise\n        return {}",
    "throttled_open_attempts = 0",
    "code=429,",
    "resume_headers: list[str | None] = []",
    "assert resume_headers == [None, 'bytes=4-']",
    "throttled_download_attempts = 0",
    "assert '--continue-at' in curl_commands[0]",
    "assert '--retry-all-errors' in curl_commands[0]",
    "assert curl_copy_calls == [",
    "ZIG_INSTALL_SELF_TEST=pass",
)

EXACT_COUNT_MARKERS = (
    "def parse_retry_after(headers) -> float | None:",
    "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:",
    "def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:",
    "def copy_url_to_file_with_curl(",
    "resume_offset = destination.stat().st_size if destination.exists() else 0",
    "append = resume_offset > 0 and status == 206",
    "throttled_open_attempts = 0",
    "resume_headers: list[str | None] = []",
    "throttled_download_attempts = 0",
)

ORDERED_MARKERS = (
    ("def parse_retry_after(headers) -> float | None:", "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:"),
    ("def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:", "def copy_response_chunks(response, destination: Path, *, append: bool) -> None:"),
    ("def copy_url_to_file_with_curl(", "def copy_url_to_file("),
    ("resume_offset = destination.stat().st_size if destination.exists() else 0", "request = build_download_request(url, resume_offset)"),
    ("request = build_download_request(url, resume_offset)", "append = resume_offset > 0 and status == 206"),
    ("append = resume_offset > 0 and status == 206", "copy_response_chunks(response, destination, append=append)"),
    ("throttled_open_attempts = 0", "resume_headers: list[str | None] = []"),
    ("resume_headers: list[str | None] = []", "throttled_download_attempts = 0"),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_exact_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    install_text = read_text(root / INSTALL_ZIG_PATH)

    for marker in REQUIRED_MARKERS:
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

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("LANE05_INSTALL_ZIG_DOWNLOAD_RETRIES=fail")
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
        root / INSTALL_ZIG_PATH,
        "\n".join(
            (
                "from __future__ import annotations",
                "import urllib.error",
                "import urllib.request",
                "from pathlib import Path",
                "",
                "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}",
                "DOWNLOAD_RETRIES = 4",
                "DOWNLOAD_TIMEOUT = 120.0",
                "MAX_RETRY_DELAY = 30.0",
                "",
                "def parse_retry_after(headers) -> float | None:",
                "    return None",
                "",
                "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:",
                "    parsed_retry_after = parse_retry_after(headers)",
                "    if parsed_retry_after is not None:",
                "        return min(parsed_retry_after, MAX_RETRY_DELAY)",
                "    return min(default_delay, MAX_RETRY_DELAY)",
                "",
                "def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:",
                "    if start_offset <= 0:",
                "        return url",
                "    return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})",
                "",
                "def copy_response_chunks(response, destination: Path, *, append: bool) -> None:",
                "    return None",
                "",
                "def copy_url_to_file_with_curl(",
                "    url: str,",
                "    destination: Path,",
                ") -> None:",
                "    cmd = [",
                "        'curl',",
                "        '--retry-all-errors',",
                "        '--continue-at',",
                "        '-',",
                "        '--speed-limit',",
                "        '1',",
                "        '--speed-time',",
                "        '30',",
                "    ]",
                "    return None",
                "",
                "def copy_url_to_file(url: str, destination: Path) -> None:",
                "    resume_offset = destination.stat().st_size if destination.exists() else 0",
                "    request = build_download_request(url, resume_offset)",
                "    status = 206",
                "    append = resume_offset > 0 and status == 206",
                "    response = None",
                "    copy_response_chunks(response, destination, append=append)",
                "",
                "def is_explicit_version(channel: str) -> bool:",
                "    return True",
                "",
                "def load_index(channel: str) -> dict:",
                "    try:",
                "        return {}",
                "    except (TimeoutError, urllib.error.URLError):",
                "        if not is_explicit_version(channel):",
                "            raise",
                "        return {}",
                "",
                "def run_self_test() -> int:",
                "    throttled_open_attempts = 0",
                "    code=429,",
                "    resume_headers: list[str | None] = []",
                "    assert resume_headers == [None, 'bytes=4-']",
                "    throttled_download_attempts = 0",
                "    curl_commands = [['curl', '--continue-at', '-', '--retry-all-errors']]",
                "    assert '--continue-at' in curl_commands[0]",
                "    assert '--retry-all-errors' in curl_commands[0]",
                "    curl_copy_calls = [('https://example.invalid/archive.tar.xz', Path('/tmp/archive.tar.xz'), 7, 9.0)]",
                "    assert curl_copy_calls == [",
                "        ('https://example.invalid/archive.tar.xz', Path('/tmp/archive.tar.xz'), 7, 9.0)",
                "    ]",
                "    print('ZIG_INSTALL_SELF_TEST=pass')",
                "    return 0",
            )
        )
        + "\n",
    )


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 7

    with tempfile.TemporaryDirectory(prefix="lane05_install_download_retries_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        install_path = root / INSTALL_ZIG_PATH
        install_path.write_text(
            replace_once(
                install_path.read_text(encoding="utf-8"),
                "'--retry-all-errors',\n",
                "",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_INSTALL_MARKER", "'--retry-all-errors',") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        install_path = root / INSTALL_ZIG_PATH
        marker = "resume_headers: list[str | None] = []"
        install_path.write_text(
            install_path.read_text(encoding="utf-8") + marker + "\n",
            encoding="utf-8",
        )
        assert ("DUPLICATE_INSTALL_MARKER", f"{marker}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        install_path = root / INSTALL_ZIG_PATH
        install_path.write_text(
            replace_once(
                install_path.read_text(encoding="utf-8"),
                "    resume_offset = destination.stat().st_size if destination.exists() else 0\n"
                "    request = build_download_request(url, resume_offset)\n",
                "    request = build_download_request(url, resume_offset)\n"
                "    resume_offset = destination.stat().st_size if destination.exists() else 0\n",
            ),
            encoding="utf-8",
        )
        assert any(code == "ORDER_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        install_path = root / INSTALL_ZIG_PATH
        install_path.write_text(
            replace_once(
                install_path.read_text(encoding="utf-8"),
                "    except (TimeoutError, urllib.error.URLError):\n        if not is_explicit_version(channel):\n            raise\n        return {}\n",
                "",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_INSTALL_MARKER",
            "    except (TimeoutError, urllib.error.URLError):\n        if not is_explicit_version(channel):\n            raise\n        return {}",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (root / INSTALL_ZIG_PATH).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing install-zig.py did not abort")

        build_self_test_root(root)
        install_path = root / INSTALL_ZIG_PATH
        install_path.write_text(
            replace_once(
                install_path.read_text(encoding="utf-8"),
                "assert '--continue-at' in curl_commands[0]\n",
                "",
            ),
            encoding="utf-8",
        )
        assert ("MISSING_INSTALL_MARKER", "assert '--continue-at' in curl_commands[0]") in collect_issues(root)
        checks_run += 1

    assert checks_run == expected_case_count
    print("LANE05_INSTALL_ZIG_DOWNLOAD_RETRIES_SELF_TEST=pass")
    print(f"LANE05_INSTALL_ZIG_DOWNLOAD_RETRIES_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that install-zig keeps the Lane 05 resumable download and retry posture explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE05_INSTALL_ZIG_DOWNLOAD_RETRIES=pass")
    print(f"LANE05_INSTALL_ZIG_DOWNLOAD_RETRIES_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
