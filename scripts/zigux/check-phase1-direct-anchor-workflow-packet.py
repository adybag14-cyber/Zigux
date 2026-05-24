#!/usr/bin/env python3
"""Guard the live Phase 1 direct-anchor workflow packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
DIRECT_OWNER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
DIRECT_ANCHOR_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")
STRING_REVIEW_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")

REQUIRED_FILES = (
    WORKFLOW_REL,
    DIRECT_OWNER_REL,
    DIRECT_ANCHOR_REL,
    STRING_REVIEW_REL,
)

EXACT_ONCE_LINES = (
    "- name: Setup pinned Zig toolchain",
    "- name: Self-test current Phase 1 direct-owner checker",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "- name: Check current Phase 1 direct-owner markers",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "- name: Self-test current Phase 1 direct-anchor manifest gate",
    "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    "- name: Check current Phase 1 direct-anchor manifest gate",
    "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "- name: Self-test current Phase 1 string review checker",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "- name: Check current Phase 1 string review packet",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    "- name: Self-test current Phase 1 route summary checker",
)

ORDERED_LINES = EXACT_ONCE_LINES

FORBIDDEN_LINES = (
    "- name: Self-test Phase 1 direct-owner markers",
    "- name: Check Phase 1 direct-owner markers",
    "- name: Self-test Phase 1 direct-anchor manifest gate",
    "- name: Check Phase 1 direct-anchor manifest gate",
    "- name: Self-test Phase 1 string review checker",
    "- name: Check Phase 1 string review packet",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def count_exact_lines(text: str, marker: str) -> int:
    want = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == want)


def collect_failures(root: Path) -> list[str]:
    failures = [
        f"missing_file:{relative_path.as_posix()}"
        for relative_path in REQUIRED_FILES
        if not (root / relative_path).is_file()
    ]
    if failures:
        return failures

    workflow_text = (root / WORKFLOW_REL).read_text(encoding="utf-8")

    for marker in EXACT_ONCE_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count != 1:
            failures.append(f"missing_or_duplicate:{marker}:count={count}")

    for marker in FORBIDDEN_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count != 0:
            failures.append(f"forbidden_present:{marker}:count={count}")

    if failures:
        return failures

    stripped = [line.strip() for line in workflow_text.splitlines()]
    positions = [stripped.index(marker.strip()) for marker in ORDERED_LINES]
    if positions != sorted(positions):
        failures.append("phase1_direct_anchor_workflow_packet:order_drift")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    for relative_path in (DIRECT_OWNER_REL, DIRECT_ANCHOR_REL, STRING_REVIEW_REL):
        write_text(root / relative_path, "#!/usr/bin/env python3\nprint('stub:ok')\n")

    write_text(
        root / WORKFLOW_REL,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Checkout",
                "        uses: actions/checkout@v6.0.2",
                "      - name: Setup Python",
                "        uses: actions/setup-python@v6.2.0",
                "      - name: Setup pinned Zig toolchain",
                "        run: ./setup-zig.sh",
                "      - name: Self-test current Phase 1 direct-owner checker",
                "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
                "      - name: Check current Phase 1 direct-owner markers",
                "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
                "      - name: Self-test current Phase 1 direct-anchor manifest gate",
                "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
                "      - name: Check current Phase 1 direct-anchor manifest gate",
                "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
                "      - name: Self-test current Phase 1 string review checker",
                "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
                "      - name: Check current Phase 1 string review packet",
                "        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
                "      - name: Self-test current Phase 1 route summary checker",
                "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
            )
        )
        + "\n",
    )


def remove_line(root: Path, marker: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            del lines[idx]
            workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(marker)


def duplicate_line(root: Path, marker: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            lines.insert(idx + 1, line)
            workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(marker)


def swap_lines(root: Path, first: str, second: str) -> None:
    workflow = root / WORKFLOW_REL
    lines = workflow.read_text(encoding="utf-8").splitlines()
    first_idx = next(i for i, line in enumerate(lines) if line.strip() == first.strip())
    second_idx = next(i for i, line in enumerate(lines) if line.strip() == second.strip())
    lines[first_idx], lines[second_idx] = lines[second_idx], lines[first_idx]
    workflow.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_line(root: Path, marker: str) -> None:
    workflow = root / WORKFLOW_REL
    workflow.write_text(workflow.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_workflow", lambda root: (root / WORKFLOW_REL).unlink()),
        (
            "missing_setup_zig_boundary",
            lambda root: remove_line(root, "- name: Setup pinned Zig toolchain"),
        ),
        (
            "missing_direct_anchor_live",
            lambda root: remove_line(root, "run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py"),
        ),
        (
            "duplicate_string_selftest",
            lambda root: duplicate_line(root, "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test"),
        ),
        (
            "missing_route_summary_boundary",
            lambda root: remove_line(root, "- name: Self-test current Phase 1 route summary checker"),
        ),
        (
            "bad_order",
            lambda root: swap_lines(
                root,
                "- name: Check current Phase 1 direct-anchor manifest gate",
                "- name: Self-test current Phase 1 string review checker",
            ),
        ),
        (
            "cluster_before_setup_zig",
            lambda root: swap_lines(
                root,
                "- name: Setup pinned Zig toolchain",
                "- name: Self-test current Phase 1 direct-owner checker",
            ),
        ),
        (
            "forbidden_old_label",
            lambda root: append_line(root, "      - name: Self-test Phase 1 direct-owner markers"),
        ),
        ("missing_direct_owner_file", lambda root: (root / DIRECT_OWNER_REL).unlink()),
        ("missing_string_file", lambda root: (root / STRING_REVIEW_REL).unlink()),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-direct-anchor-workflow-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-direct-anchor-workflow:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-direct-anchor-workflow:{name}:expected_failure")
                return 1

    print("PHASE1_DIRECT_ANCHOR_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_DIRECT_ANCHOR_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample repo root")
    args = parser.parse_args()

    if args.write_sample_root:
        build_sample_root(Path(args.write_sample_root).resolve())
        print("PHASE1_DIRECT_ANCHOR_WORKFLOW_PACKET_SAMPLE_ROOT=written")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_DIRECT_ANCHOR_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_DIRECT_ANCHOR_WORKFLOW_PACKET=pass")
    print(f"PHASE1_DIRECT_ANCHOR_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_DIRECT_ANCHOR_WORKFLOW_PACKET_REQUIRED_LINE_COUNT={len(EXACT_ONCE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
