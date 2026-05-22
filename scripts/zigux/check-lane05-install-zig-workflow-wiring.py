#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_MARKERS = (
    "      - name: Check current pinned Zig archive packet\n"
    "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "      - name: Self-test current Lane 05 local-first archive checker\n"
    "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "      - name: Check current Lane 05 local-first archive packet\n"
    "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "      - name: Self-test current Lane 05 local archive README checker\n"
    "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "      - name: Check current Lane 05 local archive README packet\n"
    "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "      - name: Self-test current Lane 05 install-zig workflow wiring checker\n"
    "        run: python3 scripts/zigux/check-lane05-install-zig-workflow-wiring.py --self-test",
    "      - name: Check current Lane 05 install-zig workflow wiring packet\n"
    "        run: python3 scripts/zigux/check-lane05-install-zig-workflow-wiring.py",
    "      - name: Self-test current Zig installer helper\n"
    "        run: python3 scripts/zigux/install-zig.py --self-test",
)

ORDERED_MARKER_PAIRS = (
    (
        "      - name: Check current pinned Zig archive packet",
        "      - name: Self-test current Lane 05 local-first archive checker",
    ),
    (
        "      - name: Self-test current Lane 05 local-first archive checker",
        "      - name: Check current Lane 05 local-first archive packet",
    ),
    (
        "      - name: Check current Lane 05 local-first archive packet",
        "      - name: Self-test current Lane 05 local archive README checker",
    ),
    (
        "      - name: Self-test current Lane 05 local archive README checker",
        "      - name: Check current Lane 05 local archive README packet",
    ),
    (
        "      - name: Check current Lane 05 local archive README packet",
        "      - name: Self-test current Lane 05 install-zig workflow wiring checker",
    ),
    (
        "      - name: Self-test current Lane 05 install-zig workflow wiring checker",
        "      - name: Check current Lane 05 install-zig workflow wiring packet",
    ),
    (
        "      - name: Check current Lane 05 install-zig workflow wiring packet",
        "      - name: Self-test current Zig installer helper",
    ),
)


def load_text(root: Path) -> str:
    path = root / WORKFLOW_PATH
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(
            f"lane05 install-zig workflow wiring checker missing workflow: {path}"
        ) from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 install-zig workflow wiring checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 install-zig workflow wiring checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 install-zig workflow wiring checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 install-zig workflow wiring checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_root(root: Path) -> int:
    text = load_text(root)
    for marker in REQUIRED_MARKERS:
        require_marker(text, marker, "workflow marker")
        require_exact_count(text, marker, 1, "workflow marker")
    for earlier, later in ORDERED_MARKER_PAIRS:
        require_order(text, earlier, later, "workflow order")
    return len(REQUIRED_MARKERS)


def write_sample_root(root: Path) -> None:
    workflow_dir = root / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    (workflow_dir / "zigux-bootstrap.yml").write_text(
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - name: Check current pinned Zig archive packet",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
                "      - name: Self-test current Lane 05 local-first archive checker",
                "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
                "      - name: Check current Lane 05 local-first archive packet",
                "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
                "      - name: Self-test current Lane 05 local archive README checker",
                "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
                "      - name: Check current Lane 05 local archive README packet",
                "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
                "      - name: Self-test current Lane 05 install-zig workflow wiring checker",
                "        run: python3 scripts/zigux/check-lane05-install-zig-workflow-wiring.py --self-test",
                "      - name: Check current Lane 05 install-zig workflow wiring packet",
                "        run: python3 scripts/zigux/check-lane05-install-zig-workflow-wiring.py",
                "      - name: Self-test current Zig installer helper",
                "        run: python3 scripts/zigux/install-zig.py --self-test",
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    def expect_pass() -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_workflow_wiring_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            assert check_root(root) == len(REQUIRED_MARKERS)
            case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_workflow_wiring_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                check_root(root)
            except SystemExit as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected check_root to fail")

    expect_pass()
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text("name: zigux-bootstrap\n", encoding="utf-8"),
        "missing workflow marker",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            load_text(root).replace(
                "      - name: Self-test current Lane 05 install-zig workflow wiring checker\n"
                "        run: python3 scripts/zigux/check-lane05-install-zig-workflow-wiring.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "missing workflow marker",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            load_text(root).replace(
                "      - name: Check current Lane 05 local archive README packet\n"
                "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py\n"
                "      - name: Self-test current Lane 05 install-zig workflow wiring checker\n"
                "        run: python3 scripts/zigux/check-lane05-install-zig-workflow-wiring.py --self-test\n",
                "      - name: Self-test current Lane 05 install-zig workflow wiring checker\n"
                "        run: python3 scripts/zigux/check-lane05-install-zig-workflow-wiring.py --self-test\n"
                "      - name: Check current Lane 05 local archive README packet\n"
                "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py\n",
                1,
            ),
            encoding="utf-8",
        ),
        "expected workflow order",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            load_text(root)
            + "      - name: Self-test current Lane 05 install-zig workflow wiring checker\n"
            + "        run: python3 scripts/zigux/check-lane05-install-zig-workflow-wiring.py --self-test\n",
            encoding="utf-8",
        ),
        "expected exactly 1 occurrences",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            load_text(root).replace(
                "        run: python3 scripts/zigux/check-lane05-install-zig-workflow-wiring.py\n",
                "        run: python3 scripts/zigux/install-zig.py --resolve-only\n",
                1,
            ),
            encoding="utf-8",
        ),
        "missing workflow marker",
    )

    print("LANE05_INSTALL_ZIG_WORKFLOW_WIRING_SELF_TEST=pass")
    print(f"LANE05_INSTALL_ZIG_WORKFLOW_WIRING_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 bootstrap workflow wiring around install-zig guard steps."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker coverage.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for local replay.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    marker_count = check_root(args.root.resolve())
    print("LANE05_INSTALL_ZIG_WORKFLOW_WIRING=pass")
    print(f"LANE05_INSTALL_ZIG_WORKFLOW_WIRING_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
