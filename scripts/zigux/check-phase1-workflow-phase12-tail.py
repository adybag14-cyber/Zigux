#!/usr/bin/env python3
"""Guard Lane 17's current Phase 11-to-Phase 12 workflow tail."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
NOTE_REL = Path("Documentation/zigux/phase1-workflow-viability.md")

TAIL_NOTE_LINE = (
    "- `PHASE1_WORKFLOW_PHASE11_PHASE12_TAIL=Self-test current Phase 11 build inventory checker,"
    "Check current Phase 11 build inventory packet,Self-test current Phase 11 HVC cleanup current-head checker,"
    "Check current Phase 11 HVC cleanup current-head packet,Run current Phase 11 HVC hv_ops layout proof,"
    "Run current Phase 11 HVC export surface layout proof,Run current Phase 11 HVC cleanup packet proof,"
    "Self-test current Phase 12 tail guard,Check current Phase 12 tail guard,"
    "Self-test current Phase 12 build-only surface checker,Check current Phase 12 build-only surface,"
    "Self-test current Phase 12 release-readiness packet checker,Check current Phase 12 release-readiness packet,"
    "Validate current Phase 12 support bundle,Run current Phase 12 smoke packet,Run current Phase 12 shared test packet,"
    "Run current Phase 12 aggregate route,Self-test current Phase 14 shared smoke route checker,"
    "Run current Phase 14 validate route,Run current Phase 12 throughput-parity anchor`"
)
GUARD_NOTE_LINE = "- `PHASE1_WORKFLOW_PHASE12_TAIL_GUARD=scripts/zigux/check-phase1-workflow-phase12-tail.py`"
ADJACENCY_NOTE_LINE = (
    "- `PHASE1_WORKFLOW_PHASE12_TAIL_ADJACENCY=Run current Phase 11 HVC cleanup packet proof,"
    "Self-test current Phase 12 tail guard,Check current Phase 12 tail guard,"
    "Self-test current Phase 12 build-only surface checker`"
)

TAIL_STEPS = (
    ("Self-test current Phase 11 build inventory checker", "python3 scripts/zigux/check-phase11-build-inventory.py --self-test"),
    ("Check current Phase 11 build inventory packet", "python3 scripts/zigux/check-phase11-build-inventory.py"),
    ("Self-test current Phase 11 HVC cleanup current-head checker", "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test"),
    ("Check current Phase 11 HVC cleanup current-head packet", "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py"),
    ("Run current Phase 11 HVC hv_ops layout proof", "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig"),
    ("Run current Phase 11 HVC export surface layout proof", "zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig"),
    ("Run current Phase 11 HVC cleanup packet proof", "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig"),
    ("Self-test current Phase 12 tail guard", "python3 scripts/zigux/check-phase1-workflow-phase12-tail.py --self-test"),
    ("Check current Phase 12 tail guard", "python3 scripts/zigux/check-phase1-workflow-phase12-tail.py"),
    ("Self-test current Phase 12 build-only surface checker", "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test"),
    ("Check current Phase 12 build-only surface", "python3 scripts/zigux/check-build-only-phase12-surface.py"),
    ("Self-test current Phase 12 release-readiness packet checker", "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test"),
    ("Check current Phase 12 release-readiness packet", "python3 scripts/zigux/check-phase12-release-readiness-packet.py"),
    ("Validate current Phase 12 support bundle", "python3 scripts/zigux/validate-phase12.py"),
    ("Run current Phase 12 smoke packet", "make -C zigux phase12-smoke"),
    ("Run current Phase 12 shared test packet", "make -C zigux phase12-test"),
    ("Run current Phase 12 aggregate route", "make -C zigux phase12"),
    ("Self-test current Phase 14 shared smoke route checker", "python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test"),
    ("Run current Phase 14 validate route", "make -C zigux phase14-validate"),
    ("Run current Phase 12 throughput-parity anchor", "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/build.zig"),
)

FULL_CHAIN = tuple(step for step, _ in TAIL_STEPS)
ADJACENCY_CHAIN = (
    "Run current Phase 11 HVC cleanup packet proof",
    "Self-test current Phase 12 tail guard",
    "Check current Phase 12 tail guard",
    "Self-test current Phase 12 build-only surface checker",
)


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line(text: str, line: str) -> int:
    return sum(1 for current in text.splitlines() if current == line)


def require_once(text: str, label: str, line: str) -> list[str]:
    count = count_exact_line(text, line)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_step(workflow_text: str, step_name: str, run_command: str) -> list[str]:
    failures: list[str] = []
    failures.extend(require_once(workflow_text, f"workflow_step:{step_name}", f"      - name: {step_name}"))
    pair = f"      - name: {step_name}\n        run: {run_command}"
    pair_count = workflow_text.count(pair)
    if pair_count != 1:
        failures.append(f"workflow_run:{step_name}:expected=1:actual={pair_count}")
    return failures


def workflow_step_names(workflow_text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix) :] for line in workflow_text.splitlines() if line.startswith(prefix)]


def require_adjacent_chain(workflow_text: str, step_names: tuple[str, ...]) -> list[str]:
    names = workflow_step_names(workflow_text)
    chain = list(step_names)
    max_start = len(names) - len(chain) + 1
    for index in range(max_start):
        if names[index : index + len(chain)] == chain:
            return []
    return [f"workflow_adjacent_chain:missing:{'->'.join(step_names)}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (WORKFLOW_REL, NOTE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    note_text = load_text(root, NOTE_REL)

    failures.extend(require_once(note_text, "note", TAIL_NOTE_LINE))
    failures.extend(require_once(note_text, "note", GUARD_NOTE_LINE))
    failures.extend(require_once(note_text, "note", ADJACENCY_NOTE_LINE))
    for step_name, run_command in TAIL_STEPS:
        failures.extend(require_step(workflow_text, step_name, run_command))
    failures.extend(require_adjacent_chain(workflow_text, FULL_CHAIN))
    failures.extend(require_adjacent_chain(workflow_text, ADJACENCY_CHAIN))
    return failures


def build_note_text() -> str:
    return "\n".join(("# Phase 1 Workflow Viability", "", TAIL_NOTE_LINE, GUARD_NOTE_LINE, ADJACENCY_NOTE_LINE, ""))


def build_workflow_text() -> str:
    lines = ["name: zigux-bootstrap", "jobs:", "  bootstrap:", "    runs-on: ubuntu-latest", "    steps:"]
    for step_name, run_command in TAIL_STEPS:
        lines.append(f"      - name: {step_name}")
        lines.append(f"        run: {run_command}")
    lines.append("")
    return "\n".join(lines)


def build_sample_repo(root: Path) -> None:
    write_file(root, NOTE_REL, build_note_text())
    write_file(root, WORKFLOW_REL, build_workflow_text())


def rewrite_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"missing sample text: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-workflow-phase12-tail-") as tmpdir:
        root = Path(tmpdir)

        build_sample_repo(root)
        if collect_failures(root):
            print("self-test:unexpected_failures")
            return 1
        case_count += 1

        for note_line, label in (
            (TAIL_NOTE_LINE, "tail_note"),
            (GUARD_NOTE_LINE, "guard_note"),
            (ADJACENCY_NOTE_LINE, "adjacency_note"),
        ):
            note_text = load_text(root, NOTE_REL)
            write_file(root, NOTE_REL, rewrite_once(note_text, note_line + "\n"))
            failures = collect_failures(root)
            if "note:expected=1:actual=0" not in failures:
                print(f"self-test:missing_{label}_not_detected")
                return 1
            case_count += 1
            build_sample_repo(root)

            note_text = load_text(root, NOTE_REL)
            write_file(root, NOTE_REL, note_text + note_line + "\n")
            failures = collect_failures(root)
            if "note:expected=1:actual=2" not in failures:
                print(f"self-test:duplicate_{label}_not_detected")
                return 1
            case_count += 1
            build_sample_repo(root)

        for step_name, run_command in TAIL_STEPS:
            workflow_text = load_text(root, WORKFLOW_REL)
            write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, f"      - name: {step_name}\n"))
            failures = collect_failures(root)
            if f"workflow_step:{step_name}:expected=1:actual=0" not in failures:
                print(f"self-test:missing_{step_name}_step_not_detected")
                return 1
            case_count += 1
            build_sample_repo(root)

            workflow_text = load_text(root, WORKFLOW_REL)
            block = f"      - name: {step_name}\n        run: {run_command}\n"
            write_file(root, WORKFLOW_REL, workflow_text + block)
            failures = collect_failures(root)
            if f"workflow_step:{step_name}:expected=1:actual=2" not in failures:
                print(f"self-test:duplicate_{step_name}_step_not_detected")
                return 1
            if f"workflow_run:{step_name}:expected=1:actual=2" not in failures:
                print(f"self-test:duplicate_{step_name}_run_not_detected")
                return 1
            case_count += 1
            build_sample_repo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        old = "\n".join((
            "      - name: Run current Phase 11 HVC cleanup packet proof",
            "        run: zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
            "      - name: Self-test current Phase 12 tail guard",
            "        run: python3 scripts/zigux/check-phase1-workflow-phase12-tail.py --self-test",
            "      - name: Check current Phase 12 tail guard",
            "        run: python3 scripts/zigux/check-phase1-workflow-phase12-tail.py",
            "      - name: Self-test current Phase 12 build-only surface checker",
            "        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        ))
        new = "\n".join((
            "      - name: Run current Phase 11 HVC cleanup packet proof",
            "        run: zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
            "      - name: Self-test current Phase 12 build-only surface checker",
            "        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
            "      - name: Self-test current Phase 12 tail guard",
            "        run: python3 scripts/zigux/check-phase1-workflow-phase12-tail.py --self-test",
            "      - name: Check current Phase 12 tail guard",
            "        run: python3 scripts/zigux/check-phase1-workflow-phase12-tail.py",
        ))
        write_file(root, WORKFLOW_REL, rewrite_once(workflow_text, old, new))
        failures = collect_failures(root)
        expected = f"workflow_adjacent_chain:missing:{'->'.join(ADJACENCY_CHAIN)}"
        if expected not in failures:
            print("self-test:broken_adjacency_chain_not_detected")
            return 1
        case_count += 1
        build_sample_repo(root)

        workflow_text = load_text(root, WORKFLOW_REL)
        reordered = list(TAIL_STEPS)
        reordered[6], reordered[7] = reordered[7], reordered[6]
        lines = ["name: zigux-bootstrap", "jobs:", "  bootstrap:", "    runs-on: ubuntu-latest", "    steps:"]
        for step_name, run_command in reordered:
            lines.append(f"      - name: {step_name}")
            lines.append(f"        run: {run_command}")
        lines.append("")
        write_file(root, WORKFLOW_REL, "\n".join(lines))
        failures = collect_failures(root)
        expected = f"workflow_adjacent_chain:missing:{'->'.join(FULL_CHAIN)}"
        if expected not in failures:
            print("self-test:broken_full_chain_not_detected")
            return 1
        case_count += 1

    print("PHASE1_WORKFLOW_PHASE12_TAIL_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_PHASE12_TAIL_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root.resolve())
    if failures:
        for failure in failures:
            print(f"phase1-workflow-phase12-tail:{failure}")
        return 1

    print("phase1-workflow-phase12-tail:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
