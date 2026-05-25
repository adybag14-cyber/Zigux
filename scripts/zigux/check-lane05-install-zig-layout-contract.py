#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
INSTALL_ZIG_PATH = Path("scripts/zigux/install-zig.py")

SELF_TEST_STEP = "- name: Self-test current Zig installer helper"
SELF_TEST_CMD = "python3 scripts/zigux/install-zig.py --self-test"
NEXT_STEP = "- name: Self-test current staged pinned Zig archive helper"

INSTALL_MARKERS = (
    "def extract_archive(archive_path: Path, dest: Path) -> Path:",
    "def resolve_bin_dir(final_root: Path) -> Path:",
    "def append_github_path(path: Path) -> None:",
    "with tempfile.TemporaryDirectory(prefix='zigux_install_zig_') as tmpdir_str:",
    "archive_name = tarball_url.rsplit('/', 1)[-1]",
    "archive_path = tmpdir / archive_name",
    "copy_url_to_file(tarball_url, archive_path)",
    "extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
    "final_root = install_root / extracted_root.name",
    "if final_root.exists():",
    "shutil.rmtree(final_root)",
    "shutil.copytree(extracted_root, final_root)",
    "bin_dir = resolve_bin_dir(final_root)",
    "append_github_path(bin_dir)",
    "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')",
    "print('ZIG_INSTALL_STATUS=pass')",
)

ORDERED_MARKERS = (
    ("archive_path = tmpdir / archive_name", "copy_url_to_file(tarball_url, archive_path)"),
    ("copy_url_to_file(tarball_url, archive_path)", "extracted_root = extract_archive(archive_path, tmpdir / 'extract')"),
    ("extracted_root = extract_archive(archive_path, tmpdir / 'extract')", "final_root = install_root / extracted_root.name"),
    ("if final_root.exists():", "shutil.rmtree(final_root)"),
    ("shutil.rmtree(final_root)", "shutil.copytree(extracted_root, final_root)"),
    ("shutil.copytree(extracted_root, final_root)", "bin_dir = resolve_bin_dir(final_root)"),
    ("bin_dir = resolve_bin_dir(final_root)", "append_github_path(bin_dir)"),
    ("append_github_path(bin_dir)", "print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')"),
    ("print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')", "print('ZIG_INSTALL_STATUS=pass')"),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 install-zig layout checker missing {label}: {marker}")


def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise SystemExit(
            "lane05 install-zig layout checker expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 install-zig layout checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 install-zig layout checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> None:
    require_marker(text, SELF_TEST_STEP, "workflow self-test step")
    require_marker(text, SELF_TEST_CMD, "workflow self-test command")
    require_marker(text, NEXT_STEP, "workflow next-step anchor")
    require_exact_line(text, f"run: {SELF_TEST_CMD}", "workflow run")
    require_exact_line(text, SELF_TEST_STEP, "workflow self-test step")
    require_order(text, SELF_TEST_STEP, NEXT_STEP, "workflow lane05 order")


def check_install_zig(text: str) -> None:
    for marker in INSTALL_MARKERS:
        require_marker(text, marker, "install-zig marker")

    require_exact_line(
        text,
        "print('ZIG_INSTALL_STATUS=pass')",
        "installer status output",
    )

    for earlier, later in ORDERED_MARKERS:
        require_order(text, earlier, later, "installer layout order")



def check_root(root: Path) -> tuple[int, int]:
    workflow_text = read_text(root / WORKFLOW_PATH)
    install_text = read_text(root / INSTALL_ZIG_PATH)
    check_workflow(workflow_text)
    check_install_zig(install_text)
    return (3, len(INSTALL_MARKERS))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(
        root / WORKFLOW_PATH,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Zig installer helper",
                "        run: python3 scripts/zigux/install-zig.py --self-test",
                "      - name: Self-test current staged pinned Zig archive helper",
                "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
            )
        )
        + "\n",
    )
    write_text(
        root / INSTALL_ZIG_PATH,
        "\n".join(
            (
                "from pathlib import Path",
                "import shutil",
                "import tempfile",
                "",
                "def extract_archive(archive_path: Path, dest: Path) -> Path:",
                "    return dest",
                "",
                "def resolve_bin_dir(final_root: Path) -> Path:",
                "    return final_root",
                "",
                "def append_github_path(path: Path) -> None:",
                "    return None",
                "",
                "def copy_url_to_file(url: str, destination: Path) -> None:",
                "    return None",
                "",
                "def main() -> int:",
                "    tarball_url = 'https://example.invalid/archive.tar.xz'",
                "    install_root = Path('.zig-toolchain')",
                "    with tempfile.TemporaryDirectory(prefix='zigux_install_zig_') as tmpdir_str:",
                "        tmpdir = Path(tmpdir_str)",
                "        archive_name = tarball_url.rsplit('/', 1)[-1]",
                "        archive_path = tmpdir / archive_name",
                "        copy_url_to_file(tarball_url, archive_path)",
                "        extracted_root = extract_archive(archive_path, tmpdir / 'extract')",
                "        final_root = install_root / extracted_root.name",
                "        if final_root.exists():",
                "            shutil.rmtree(final_root)",
                "        shutil.copytree(extracted_root, final_root)",
                "    bin_dir = resolve_bin_dir(final_root)",
                "    append_github_path(bin_dir)",
                "    print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')",
                "    print('ZIG_INSTALL_STATUS=pass')",
                "    return 0",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_install_zig_layout_pass_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert check_root(root) == (3, len(INSTALL_MARKERS))
        case_count += 1

    def expect_failure(mutator, expected: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_install_zig_layout_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                check_root(root)
            except SystemExit as exc:
                assert expected in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected layout checker failure")

    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text("name: zigux-bootstrap\n", encoding="utf-8"),
        SELF_TEST_STEP,
    )
    expect_failure(
        lambda root: (root / INSTALL_ZIG_PATH).write_text(
            (root / INSTALL_ZIG_PATH).read_text(encoding="utf-8").replace(
                "append_github_path(bin_dir)\n",
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "append_github_path(bin_dir)",
    )
    expect_failure(
        lambda root: (root / INSTALL_ZIG_PATH).write_text(
            (root / INSTALL_ZIG_PATH).read_text(encoding="utf-8").replace(
                "        extracted_root = extract_archive(archive_path, tmpdir / 'extract')\n"
                "        final_root = install_root / extracted_root.name\n",
                "        final_root = install_root / extracted_root.name\n"
                "        extracted_root = extract_archive(archive_path, tmpdir / 'extract')\n",
                1,
            ),
            encoding="utf-8",
        ),
        "installer layout order",
    )
    expect_failure(
        lambda root: (root / INSTALL_ZIG_PATH).write_text(
            (root / INSTALL_ZIG_PATH).read_text(encoding="utf-8").replace(
                "    print('ZIG_INSTALL_STATUS=pass')\n"
                "    return 0\n",
                "    print('ZIG_INSTALL_STATUS=pass')\n"
                "    print('ZIG_INSTALL_STATUS=pass')\n"
                "    return 0\n",
                1,
            ),
            encoding="utf-8",
        ),
        "installer status output",
    )

    print("LANE05_INSTALL_ZIG_LAYOUT_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_INSTALL_ZIG_LAYOUT_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 install-zig extraction and PATH export packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for no-checkout validation",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    workflow_marker_count, installer_marker_count = check_root(args.root.resolve())
    print("LANE05_INSTALL_ZIG_LAYOUT_CONTRACT=pass")
    print(f"LANE05_INSTALL_ZIG_LAYOUT_CONTRACT_ROOT={args.root.resolve()}")
    print(f"LANE05_INSTALL_ZIG_LAYOUT_WORKFLOW_MARKER_COUNT={workflow_marker_count}")
    print(f"LANE05_INSTALL_ZIG_LAYOUT_INSTALLER_MARKER_COUNT={installer_marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
