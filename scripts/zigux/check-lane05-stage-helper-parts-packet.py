#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
STAGE_HELPER_PATH = Path("scripts/zigux/stage-pinned-zig-archive.py")
README_PATH = Path("third_party/README.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

HELPER_MARKERS = (
    'parser.add_argument(',
    '"--parts-dir"',
    "reconstruct_archive_from_parts(",
    "parts_dir=parts_dir,",
    'input_mode == "parts_dir"',
    'STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=',
    'STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=',
)

README_MARKERS = (
    ".tar.xz.parts",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "If the exact archive file is absent but",
)

WORKFLOW_STEP_MARKERS = (
    "- name: Check current pinned Zig archive packet",
    "- name: Self-test current staged pinned Zig archive helper",
    "- name: Self-test current Lane 05 stage helper contract checker",
)

WORKFLOW_LINE_MARKERS = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 parts packet missing {label}: {marker}")


def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise SystemExit(
            "lane05 parts packet expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(f"lane05 parts packet missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise SystemExit(
            f"lane05 parts packet expected {label} `{earlier}` before `{later}`"
        )


def check_helper(text: str) -> None:
    for marker in HELPER_MARKERS:
        require_marker(text, marker, "stage helper marker")
    require_order(
        text,
        '"--parts-dir"',
        "reconstruct_archive_from_parts(",
        "stage helper parts flow",
    )
    require_order(
        text,
        "reconstruct_archive_from_parts(",
        'STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=',
        "stage helper emitted output",
    )
    require_order(
        text,
        'STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=',
        'STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=',
        "stage helper output order",
    )


def check_readme(text: str) -> None:
    for marker in README_MARKERS:
        require_marker(text, marker, "README marker")


def check_workflow(text: str) -> None:
    for marker in WORKFLOW_STEP_MARKERS:
        require_marker(text, marker, "workflow step")
    for line in WORKFLOW_LINE_MARKERS:
        require_exact_line(text, line, "workflow command")
    require_order(
        text,
        WORKFLOW_STEP_MARKERS[0],
        WORKFLOW_STEP_MARKERS[1],
        "workflow archive-stage order",
    )
    require_order(
        text,
        WORKFLOW_STEP_MARKERS[1],
        WORKFLOW_STEP_MARKERS[2],
        "workflow stage-contract order",
    )


def build_self_test_root(root: Path) -> None:
    helper_path = root / STAGE_HELPER_PATH
    helper_path.parent.mkdir(parents=True, exist_ok=True)
    helper_path.write_text(
        "\n".join(
            (
                "import argparse",
                'parser = argparse.ArgumentParser()',
                'parser.add_argument("--parts-dir")',
                'def reconstruct_archive_from_parts(parts_dir, destination):',
                "    return destination",
                'input_mode = "parts_dir"',
                "parts_dir=parts_dir,",
                "reconstruct_archive_from_parts(",
                'assert input_mode == "parts_dir"',
                'print("STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=/tmp/parts")',
                'print("STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=parts_dir")',
            )
        )
        + "\n",
        encoding="utf-8",
    )

    readme_path = root / README_PATH
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(
        "\n".join(
            (
                "# Zigux third-party archives",
                "If the exact archive file is absent but `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts` is present, `.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally with `scripts/zigux/stage-pinned-zig-archive.py` before mirror or direct-download fallback.",
            )
        )
        + "\n",
        encoding="utf-8",
    )

    workflow_path = root / WORKFLOW_PATH
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Check current pinned Zig archive packet",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
                "      - name: Self-test current staged pinned Zig archive helper",
                "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
                "      - name: Self-test current Lane 05 stage helper contract checker",
                "        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    def expect_failure(mutator, expected_fragment: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_parts_packet_fail_") as tmp_dir:
            root = Path(tmp_dir)
            build_self_test_root(root)
            mutator(root)
            try:
                check_helper(read_text(root / STAGE_HELPER_PATH))
                check_readme(read_text(root / README_PATH))
                check_workflow(read_text(root / WORKFLOW_PATH))
            except SystemExit as exc:
                assert expected_fragment in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    with tempfile.TemporaryDirectory(prefix="lane05_parts_packet_pass_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        check_helper(read_text(root / STAGE_HELPER_PATH))
        check_readme(read_text(root / README_PATH))
        check_workflow(read_text(root / WORKFLOW_PATH))
        case_count += 1

    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text("missing\n", encoding="utf-8"),
        "stage helper marker",
    )
    expect_failure(
        lambda root: (root / README_PATH).write_text("# Zigux third-party archives\n", encoding="utf-8"),
        "README marker",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            read_text(root / WORKFLOW_PATH).replace(
                "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow command",
    )
    expect_failure(
        lambda root: (root / STAGE_HELPER_PATH).write_text(
            read_text(root / STAGE_HELPER_PATH).replace(
                'print("STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=/tmp/parts")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "STAGE_PINNED_ZIG_ARCHIVE_PARTS_DIR=",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            read_text(root / WORKFLOW_PATH).replace(
                "      - name: Check current pinned Zig archive packet\n"
                "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\n"
                "      - name: Self-test current staged pinned Zig archive helper\n"
                "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\n",
                "      - name: Self-test current staged pinned Zig archive helper\n"
                "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\n"
                "      - name: Check current pinned Zig archive packet\n"
                "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\n",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow archive-stage order",
    )

    print("LANE05_STAGE_HELPER_PARTS_PACKET_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_PARTS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split-archive staging packet stays explicit."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to inspect",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    check_helper(read_text(root / STAGE_HELPER_PATH))
    check_readme(read_text(root / README_PATH))
    check_workflow(read_text(root / WORKFLOW_PATH))
    print("LANE05_STAGE_HELPER_PARTS_PACKET=pass")
    print(f"LANE05_STAGE_HELPER_PARTS_HELPER_MARKER_COUNT={len(HELPER_MARKERS)}")
    print(f"LANE05_STAGE_HELPER_PARTS_README_MARKER_COUNT={len(README_MARKERS)}")
    print(f"LANE05_STAGE_HELPER_PARTS_WORKFLOW_COMMAND_COUNT={len(WORKFLOW_LINE_MARKERS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
