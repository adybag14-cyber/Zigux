#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")

REQUIRED_PATHS = (
    WORKFLOW,
    MAKEFILE,
    Path("scripts/zigux/check-phase4-repo-reality-warning.py"),
    Path("scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    Path("scripts/zigux/check-phase4-tests-readme-packet.py"),
    Path("scripts/zigux/validate-phase4.py"),
    Path("zigux/tests/phase4_build.zig"),
)

STEP_BOUNDARY_BEFORE = "- name: Run current Phase 2 validate make route"
REQUIRED_STEP_NAMES = (
    "- name: Self-test current Phase 4 repo-reality warning checker",
    "- name: Check current Phase 4 repo-reality warning packet",
    "- name: Self-test current Phase 4 reversible-delivery pin checker",
    "- name: Check current Phase 4 reversible-delivery pin packet",
    "- name: Self-test current Phase 4 tests README checker",
    "- name: Check current Phase 4 tests README packet",
    "- name: Validate Phase 4 rollback routes",
    "- name: Run Phase 4 rollback tests",
)
STEP_BOUNDARY_AFTER = "- name: Self-test current Phase 4 artifact-diff helper"

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
    "run: python3 scripts/zigux/check-phase4-repo-reality-warning.py",
    "run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test",
    "run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "run: python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase4-tests-readme-packet.py",
    "run: make -C zigux phase4-validate",
    "run: make -C zigux phase4-test",
)

REQUIRED_MAKEFILE_MARKERS = (
    "phase4-validate:",
    "scripts/zigux/validate-phase4.py --self-test",
    "scripts/zigux/validate-phase4.py",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test",
    "scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "scripts/zigux/check-phase4-perf-baseline-packet.py",
    "phase4-test:",
    "zigux/tests/phase4_build.zig",
)


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


def line_index(text: str, marker: str) -> int:
    for index, line in enumerate(text.splitlines()):
        if line.strip() == marker:
            return index
    raise AssertionError(f"marker line not found: {marker}")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
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


def insert_after_exact_line(text: str, marker: str, addition: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, addition)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel.as_posix()))

    workflow = read_text(root, WORKFLOW)
    makefile = read_text(root, MAKEFILE)

    packet_lines = (STEP_BOUNDARY_BEFORE, *REQUIRED_STEP_NAMES, STEP_BOUNDARY_AFTER)
    for marker in packet_lines:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_STEP", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_STEP", f"{marker}:count={count}"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile:
            issues.append(("MISSING_MAKEFILE_MARKER", marker))

    if not any(code.startswith("MISSING_WORKFLOW_STEP") or code.startswith("DUPLICATE_WORKFLOW_STEP") for code, _ in issues):
        positions = [line_index(workflow, marker) for marker in packet_lines]
        if positions != sorted(positions):
            issues.append(("MISORDERED_WORKFLOW_PACKET", "phase4 rollback packet order drifted"))
        else:
            lines = workflow.splitlines()
            slice_lines = lines[positions[0] : positions[-1] + 1]
            slice_step_count = sum(1 for line in slice_lines if line.strip().startswith("- name: "))
            expected_step_count = len(packet_lines)
            if slice_step_count != expected_step_count:
                issues.append(
                    (
                        "NONCONTIGUOUS_WORKFLOW_PACKET",
                        f"expected {expected_step_count} step headers between packet boundaries, saw {slice_step_count}",
                    )
                )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE4_BOOTSTRAP_ROLLBACK_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    workflow_lines = [
        "name: zigux-bootstrap",
        STEP_BOUNDARY_BEFORE,
        "  run: make -C zigux phase2-validate",
        REQUIRED_STEP_NAMES[0],
        "  run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
        REQUIRED_STEP_NAMES[1],
        "  run: python3 scripts/zigux/check-phase4-repo-reality-warning.py",
        REQUIRED_STEP_NAMES[2],
        "  run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test",
        REQUIRED_STEP_NAMES[3],
        "  run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py",
        REQUIRED_STEP_NAMES[4],
        "  run: python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test",
        REQUIRED_STEP_NAMES[5],
        "  run: python3 scripts/zigux/check-phase4-tests-readme-packet.py",
        REQUIRED_STEP_NAMES[6],
        "  run: make -C zigux phase4-validate",
        REQUIRED_STEP_NAMES[7],
        "  run: make -C zigux phase4-test",
        STEP_BOUNDARY_AFTER,
        "  run: python3 scripts/zigux/artifact_diff.py --self-test",
    ]
    write_text(root, WORKFLOW, "\n".join(workflow_lines) + "\n")

    makefile_lines = [
        "phase4-validate:",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-reversible-delivery-pins.py",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-perf-baseline-packet.py",
        "phase4-test:",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase4_build.zig",
    ]
    write_text(root, MAKEFILE, "\n".join(makefile_lines) + "\n")

    for rel in REQUIRED_PATHS:
        if rel in {WORKFLOW, MAKEFILE}:
            continue
        write_text(root, rel, "present\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_bootstrap_rollback_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                REQUIRED_STEP_NAMES[3],
                "- name: Check current Phase 4 reversible delivery pin packet drifted",
            ),
        )
        assert ("MISSING_WORKFLOW_STEP", REQUIRED_STEP_NAMES[3]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), REQUIRED_STEP_NAMES[5]))
        assert ("DUPLICATE_WORKFLOW_STEP", f"{REQUIRED_STEP_NAMES[5]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                STEP_BOUNDARY_AFTER,
                REQUIRED_STEP_NAMES[2],
            ),
        )
        assert ("DUPLICATE_WORKFLOW_STEP", f"{REQUIRED_STEP_NAMES[2]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            insert_after_exact_line(
                read_text(root, WORKFLOW),
                REQUIRED_STEP_NAMES[7],
                "- name: Unexpected Phase 4 extra bootstrap step",
            ),
        )
        assert any(code == "NONCONTIGUOUS_WORKFLOW_PACKET" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        (root / REQUIRED_PATHS[-1]).unlink()
        assert ("MISSING_REQUIRED_PATH", REQUIRED_PATHS[-1].as_posix()) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            read_text(root, MAKEFILE).replace(REQUIRED_MAKEFILE_MARKERS[5] + "\n", "", 1),
        )
        assert ("MISSING_MAKEFILE_MARKER", REQUIRED_MAKEFILE_MARKERS[5]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                REQUIRED_WORKFLOW_LINES[6],
                "run: make -C zigux phase4-validate-drifted",
            ),
        )
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[6]) in collect_issues(root)
        checks += 1

    print("PHASE4_BOOTSTRAP_ROLLBACK_PACKET_SELF_TEST=pass")
    print(f"PHASE4_BOOTSTRAP_ROLLBACK_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current bootstrap Phase 4 rollback packet in the Zigux workflow."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like sample root and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in checker tests")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE4_BOOTSTRAP_ROLLBACK_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE4_BOOTSTRAP_ROLLBACK_PACKET=pass")
    print(f"PHASE4_BOOTSTRAP_ROLLBACK_PACKET_WORKFLOW_STEP_COUNT={len(REQUIRED_STEP_NAMES)}")
    print(f"PHASE4_BOOTSTRAP_ROLLBACK_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE4_BOOTSTRAP_ROLLBACK_PACKET_MAKEFILE_MARKER_COUNT={len(REQUIRED_MAKEFILE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
