#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
INDEX_FALLBACK_CHECKER = Path("scripts/zigux/check-lane05-install-zig-index-fallback.py")
DOWNLOAD_RETRIES_CHECKER = Path("scripts/zigux/check-lane05-install-zig-download-retries.py")
DOWNLOAD_RETRIES_WORKFLOW_CHECKER = Path("scripts/zigux/check-lane05-install-zig-download-retries-workflow.py")

INDEX_FALLBACK_STEP = "- name: Check current Lane 05 install-zig index fallback packet"
INDEX_FALLBACK_RUN = "run: python3 scripts/zigux/check-lane05-install-zig-index-fallback.py"
DOWNLOAD_RETRIES_SELF_TEST = "run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py --self-test"
DOWNLOAD_RETRIES_RUN = "run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py"

REQUIRED_FILES = (
    INDEX_FALLBACK_CHECKER,
    DOWNLOAD_RETRIES_CHECKER,
    DOWNLOAD_RETRIES_WORKFLOW_CHECKER,
)

REQUIRED_INDEX_FALLBACK_MARKERS = (
    "LANE05_INSTALL_ZIG_INDEX_FALLBACK_SELF_TEST=pass",
    "def infer_tarball_url(channel: str, target_key: str, system_key: str) -> str:",
    "def load_index(channel: str) -> dict:",
)

REQUIRED_DOWNLOAD_RETRIES_MARKERS = (
    "LANE05_INSTALL_ZIG_DOWNLOAD_RETRIES_SELF_TEST=pass",
    "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}",
    "def copy_url_to_file_with_curl(",
    "assert '--retry-all-errors' in curl_commands[0]",
)

REQUIRED_WORKFLOW_CHECKER_MARKERS = (
    f"INDEX_FALLBACK_CHECK_STEP = \"{INDEX_FALLBACK_STEP}\"",
    f"DOWNLOAD_RETRIES_SELF_TEST_CMD = (\n    \"{DOWNLOAD_RETRIES_SELF_TEST}\"\n)",
    f"DOWNLOAD_RETRIES_CHECK_CMD = (\n    \"{DOWNLOAD_RETRIES_RUN}\"\n)",
    "LANE05_INSTALL_ZIG_DOWNLOAD_RETRIES_WORKFLOW_SELF_TEST=pass",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"lane05 install-zig checker packet missing {label}: {marker}")


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(f"lane05 install-zig checker packet missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise SystemExit(
            f"lane05 install-zig checker packet expected {label} `{earlier}` before `{later}`"
        )


def collect_packet(root: Path) -> tuple[int, int]:
    existing_count = 0
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            raise SystemExit(f"required file missing: {root / rel}")
        existing_count += 1

    index_text = read_text(root / INDEX_FALLBACK_CHECKER)
    retries_text = read_text(root / DOWNLOAD_RETRIES_CHECKER)
    workflow_text = read_text(root / DOWNLOAD_RETRIES_WORKFLOW_CHECKER)

    require_markers(index_text, REQUIRED_INDEX_FALLBACK_MARKERS, "index-fallback marker")
    require_markers(retries_text, REQUIRED_DOWNLOAD_RETRIES_MARKERS, "download-retries marker")
    require_markers(workflow_text, REQUIRED_WORKFLOW_CHECKER_MARKERS, "workflow-checker marker")

    require_order(
        workflow_text,
        INDEX_FALLBACK_STEP,
        "DOWNLOAD_RETRIES_SELF_TEST_STEP =",
        "workflow checker anchor order",
    )
    require_order(
        workflow_text,
        "DOWNLOAD_RETRIES_SELF_TEST_CMD = (",
        "DOWNLOAD_RETRIES_CHECK_CMD = (",
        "workflow checker command order",
    )
    require_order(
        retries_text,
        "def parse_retry_after(headers) -> float | None:",
        "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:",
        "download-retries helper order",
    )

    marker_count = (
        len(REQUIRED_INDEX_FALLBACK_MARKERS)
        + len(REQUIRED_DOWNLOAD_RETRIES_MARKERS)
        + len(REQUIRED_WORKFLOW_CHECKER_MARKERS)
    )
    return existing_count, marker_count


def write_sample_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)

    (root / INDEX_FALLBACK_CHECKER).write_text(
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "LANE05_INSTALL_ZIG_INDEX_FALLBACK_SELF_TEST=pass",
                "def infer_tarball_url(channel: str, target_key: str, system_key: str) -> str:",
                "    return ''",
                "def load_index(channel: str) -> dict:",
                "    return {}",
            )
        )
        + "\n",
        encoding="utf-8",
    )

    (root / DOWNLOAD_RETRIES_CHECKER).write_text(
        "\n".join(
            (
                "#!/usr/bin/env python3",
                "LANE05_INSTALL_ZIG_DOWNLOAD_RETRIES_SELF_TEST=pass",
                "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}",
                "def parse_retry_after(headers) -> float | None:",
                "    return None",
                "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:",
                "    return default_delay",
                "def copy_url_to_file_with_curl(",
                "    url: str,",
                ") -> None:",
                "    pass",
                "assert '--retry-all-errors' in curl_commands[0]",
            )
        )
        + "\n",
        encoding="utf-8",
    )

    (root / DOWNLOAD_RETRIES_WORKFLOW_CHECKER).write_text(
        "\n".join(
            (
                "#!/usr/bin/env python3",
                f"INDEX_FALLBACK_CHECK_STEP = \"{INDEX_FALLBACK_STEP}\"",
                "DOWNLOAD_RETRIES_SELF_TEST_STEP = (",
                "    \"- name: Self-test current Lane 05 install-zig download retries checker\"",
                ")",
                "DOWNLOAD_RETRIES_SELF_TEST_CMD = (",
                f"    \"{DOWNLOAD_RETRIES_SELF_TEST}\"",
                ")",
                "DOWNLOAD_RETRIES_CHECK_STEP = (",
                "    \"- name: Check current Lane 05 install-zig download retries packet\"",
                ")",
                "DOWNLOAD_RETRIES_CHECK_CMD = (",
                f"    \"{DOWNLOAD_RETRIES_RUN}\"",
                ")",
                f"{INDEX_FALLBACK_STEP}",
                "DOWNLOAD_RETRIES_SELF_TEST_STEP =",
                DOWNLOAD_RETRIES_SELF_TEST,
                DOWNLOAD_RETRIES_RUN,
                "LANE05_INSTALL_ZIG_DOWNLOAD_RETRIES_WORKFLOW_SELF_TEST=pass",
            )
        )
        + "\n",
        encoding="utf-8",
    )


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 6

    with tempfile.TemporaryDirectory(prefix="lane05_install_checker_packet_") as tmp_dir:
        root = Path(tmp_dir)

        write_sample_root(root)
        assert collect_packet(root) == (3, 11)
        checks_run += 1

        write_sample_root(root)
        (root / INDEX_FALLBACK_CHECKER).unlink()
        try:
            collect_packet(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing index-fallback checker did not abort")

        write_sample_root(root)
        workflow_path = root / DOWNLOAD_RETRIES_WORKFLOW_CHECKER
        workflow_path.write_text(
            replace_once(
                workflow_path.read_text(encoding="utf-8"),
                INDEX_FALLBACK_STEP,
                "- name: wrong index fallback packet",
            ),
            encoding="utf-8",
        )
        try:
            collect_packet(root)
        except SystemExit as exc:
            assert "workflow-checker marker" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("expected missing workflow marker failure")

        write_sample_root(root)
        retries_path = root / DOWNLOAD_RETRIES_CHECKER
        retries_path.write_text(
            replace_once(
                retries_path.read_text(encoding="utf-8"),
                "def parse_retry_after(headers) -> float | None:\n    return None\n"
                "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:\n",
                "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:\n"
                "def parse_retry_after(headers) -> float | None:\n    return None\n",
            ),
            encoding="utf-8",
        )
        try:
            collect_packet(root)
        except SystemExit as exc:
            assert "download-retries helper order" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("expected download-retries order failure")

        write_sample_root(root)
        workflow_path = root / DOWNLOAD_RETRIES_WORKFLOW_CHECKER
        workflow_path.write_text(
            replace_once(
                workflow_path.read_text(encoding="utf-8"),
                DOWNLOAD_RETRIES_SELF_TEST,
                "run: python3 wrong.py --self-test",
            ),
            encoding="utf-8",
        )
        try:
            collect_packet(root)
        except SystemExit as exc:
            assert "workflow-checker marker" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("expected missing retries self-test marker failure")

        write_sample_root(root)
        index_path = root / INDEX_FALLBACK_CHECKER
        index_path.write_text(
            replace_once(
                index_path.read_text(encoding="utf-8"),
                "def load_index(channel: str) -> dict:",
                "def wrong_load_index(channel: str) -> dict:",
            ),
            encoding="utf-8",
        )
        try:
            collect_packet(root)
        except SystemExit as exc:
            assert "index-fallback marker" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("expected missing index-fallback marker failure")

    assert checks_run == expected_case_count
    print("LANE05_INSTALL_ZIG_CHECKER_PACKET_SELF_TEST=pass")
    print(f"LANE05_INSTALL_ZIG_CHECKER_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 install-zig checker packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in packet checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    file_count, marker_count = collect_packet(args.root.resolve())
    print("LANE05_INSTALL_ZIG_CHECKER_PACKET=pass")
    print(f"LANE05_INSTALL_ZIG_CHECKER_PACKET_FILE_COUNT={file_count}")
    print(f"LANE05_INSTALL_ZIG_CHECKER_PACKET_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
