#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-lane05-install-zig-index-fallback.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-index-fallback.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-download-retries-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-download-retries-workflow.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-checker-packet.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-checker-packet.py",
)

MAKEFILE_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-index-fallback.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-index-fallback.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-download-retries.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-download-retries.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-download-retries-workflow.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-download-retries-workflow.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-checker-packet.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-checker-packet.py",
)

WORKFLOW_PREV = "run: python3 scripts/zigux/check-lane05-local-archive-readme.py"
WORKFLOW_NEXT = "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test"
MAKEFILE_PREV = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py"
MAKEFILE_NEXT = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test"


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_exact_line(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def require_exact_once(text: str, marker: str, label: str) -> None:
    count = count_exact_line(text, marker)
    if count != 1:
        raise SystemExit(
            "lane05 install-zig makefile mirror checker expected exactly "
            f"1 {label} `{marker}`, found {count}"
        )


def require_order(text: str, markers: tuple[str, ...], label: str) -> None:
    lines = [line.strip() for line in text.splitlines()]
    position = -1
    for marker in markers:
        try:
            next_position = lines.index(marker, position + 1)
        except ValueError:
            raise SystemExit(
                f"lane05 install-zig makefile mirror checker missing {label}: {marker}"
            )
        position = next_position


def collect_metrics(root: Path) -> tuple[int, int]:
    workflow_text = read_text(root, WORKFLOW_PATH)
    makefile_text = read_text(root, MAKEFILE_PATH)

    for marker in WORKFLOW_LINES:
        require_exact_once(workflow_text, marker, "workflow run line")
    for marker in MAKEFILE_LINES:
        require_exact_once(makefile_text, marker, "makefile recipe line")

    require_order(
        workflow_text,
        (WORKFLOW_PREV, *WORKFLOW_LINES, WORKFLOW_NEXT),
        "workflow order",
    )
    require_order(
        makefile_text,
        (MAKEFILE_PREV, *MAKEFILE_LINES, MAKEFILE_NEXT),
        "makefile order",
    )

    return len(WORKFLOW_LINES), len(MAKEFILE_LINES)


def write_sample_root(root: Path) -> None:
    workflow_path = root / WORKFLOW_PATH
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Check current Lane 05 local archive README packet",
                f"        {WORKFLOW_PREV}",
                "      - name: Self-test current Lane 05 install-zig index fallback checker",
                f"        {WORKFLOW_LINES[0]}",
                "      - name: Check current Lane 05 install-zig index fallback packet",
                f"        {WORKFLOW_LINES[1]}",
                "      - name: Self-test current Lane 05 install-zig download retries checker",
                f"        {WORKFLOW_LINES[2]}",
                "      - name: Check current Lane 05 install-zig download retries packet",
                f"        {WORKFLOW_LINES[3]}",
                "      - name: Self-test current Lane 05 install-zig download retries workflow checker",
                f"        {WORKFLOW_LINES[4]}",
                "      - name: Check current Lane 05 install-zig download retries workflow packet",
                f"        {WORKFLOW_LINES[5]}",
                "      - name: Self-test current Lane 05 install-zig checker packet",
                f"        {WORKFLOW_LINES[6]}",
                "      - name: Check current Lane 05 install-zig checker packet",
                f"        {WORKFLOW_LINES[7]}",
                "      - name: Self-test current Lane 05 install-zig archive verification checker",
                f"        {WORKFLOW_NEXT}",
            )
        )
        + "\n",
        encoding="utf-8",
    )

    makefile_path = root / MAKEFILE_PATH
    makefile_path.parent.mkdir(parents=True, exist_ok=True)
    makefile_path.write_text(
        "\n".join(
            (
                "phase2-toolchain:",
                f"\t{MAKEFILE_PREV}",
                f"\t{MAKEFILE_LINES[0]}",
                f"\t{MAKEFILE_LINES[1]}",
                f"\t{MAKEFILE_LINES[2]}",
                f"\t{MAKEFILE_LINES[3]}",
                f"\t{MAKEFILE_LINES[4]}",
                f"\t{MAKEFILE_LINES[5]}",
                f"\t{MAKEFILE_LINES[6]}",
                f"\t{MAKEFILE_LINES[7]}",
                f"\t{MAKEFILE_NEXT}",
            )
        )
        + "\n",
        encoding="utf-8",
    )


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise AssertionError(f"marker not found: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="lane05_install_zig_makefile_mirror_") as tmp_dir:
        root = Path(tmp_dir)

        write_sample_root(root)
        assert collect_metrics(root) == (8, 8)
        cases += 1

        write_sample_root(root)
        workflow_path = root / WORKFLOW_PATH
        workflow_path.write_text(
            replace_once(workflow_path.read_text(encoding="utf-8"), WORKFLOW_LINES[4] + "\n", ""),
            encoding="utf-8",
        )
        try:
            collect_metrics(root)
        except SystemExit as exc:
            assert "workflow run line" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected missing workflow line failure")

        write_sample_root(root)
        makefile_path = root / MAKEFILE_PATH
        makefile_path.write_text(
            replace_once(makefile_path.read_text(encoding="utf-8"), MAKEFILE_LINES[5] + "\n", ""),
            encoding="utf-8",
        )
        try:
            collect_metrics(root)
        except SystemExit as exc:
            assert "makefile recipe line" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected missing makefile line failure")

        write_sample_root(root)
        makefile_path = root / MAKEFILE_PATH
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8") + f"\t{MAKEFILE_LINES[7]}\n",
            encoding="utf-8",
        )
        try:
            collect_metrics(root)
        except SystemExit as exc:
            assert "found 2" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected duplicate makefile line failure")

        write_sample_root(root)
        workflow_path = root / WORKFLOW_PATH
        workflow_path.write_text(
            replace_once(
                workflow_path.read_text(encoding="utf-8"),
                "\n".join(
                    (
                        "      - name: Check current Lane 05 install-zig index fallback packet",
                        f"        {WORKFLOW_LINES[1]}",
                        "      - name: Self-test current Lane 05 install-zig download retries checker",
                        f"        {WORKFLOW_LINES[2]}",
                    )
                ),
                "\n".join(
                    (
                        "      - name: Self-test current Lane 05 install-zig download retries checker",
                        f"        {WORKFLOW_LINES[2]}",
                        "      - name: Check current Lane 05 install-zig index fallback packet",
                        f"        {WORKFLOW_LINES[1]}",
                    )
                ),
            ),
            encoding="utf-8",
        )
        try:
            collect_metrics(root)
        except SystemExit as exc:
            assert "workflow order" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected workflow order failure")

        write_sample_root(root)
        (root / MAKEFILE_PATH).unlink()
        try:
            collect_metrics(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            cases += 1
        else:
            raise AssertionError("expected missing makefile failure")

    print("LANE05_INSTALL_ZIG_MAKEFILE_MIRROR_SELF_TEST=pass")
    print(f"LANE05_INSTALL_ZIG_MAKEFILE_MIRROR_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 install-zig checks stay mirrored between workflow and phase2-toolchain."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample repository root for focused replay checks",
    )
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"LANE05_INSTALL_ZIG_MAKEFILE_MIRROR_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    workflow_count, makefile_count = collect_metrics(args.root.resolve())
    print("LANE05_INSTALL_ZIG_MAKEFILE_MIRROR=pass")
    print(f"LANE05_INSTALL_ZIG_MAKEFILE_MIRROR_WORKFLOW_STEP_COUNT={workflow_count}")
    print(f"LANE05_INSTALL_ZIG_MAKEFILE_MIRROR_MAKEFILE_LINE_COUNT={makefile_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
