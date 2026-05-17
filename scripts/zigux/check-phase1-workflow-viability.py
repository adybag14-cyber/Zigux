#!/usr/bin/env python3
"""Guard the current Phase 1 bootstrap workflow viability packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
NOTE_REL = Path("Documentation/zigux/phase1-workflow-viability.md")
REQUIRED_FILE_RELS = [
    WORKFLOW_REL,
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-workflow-viability.py"),
    NOTE_REL,
]

REQUIRED_NOTE_LINES = {
    "status": "- `PHASE1_WORKFLOW_STATUS=active`",
    "scope": "- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 reminder checks only`",
    "owner": "- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-viability`",
    "required_files": "- `PHASE1_WORKFLOW_REQUIRED_FILES=.github/workflows/zigux-bootstrap.yml,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-workflow-viability.py,Documentation/zigux/phase1-workflow-viability.md`",
    "selftest_steps": "- `PHASE1_WORKFLOW_SELFTEST_STEPS=Self-test current Phase 1 direct-owner checker,Self-test current Phase 1 string review checker,Self-test current Phase 1 bench checker,Self-test current Phase 1 workflow viability checker`",
    "live_steps": "- `PHASE1_WORKFLOW_LIVE_STEPS=Check current Phase 1 direct-owner markers,Check current Phase 1 string review packet,Check current Phase 1 workflow viability`",
    "command_packet": "- `PHASE1_WORKFLOW_COMMAND_PACKET=python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test; python3 scripts/zigux/check-phase1-direct-owner-markers.py; python3 scripts/zigux/check-phase1-string-review-packet.py --self-test; python3 scripts/zigux/check-phase1-string-review-packet.py; python3 scripts/zigux/check-phase1-bench.py --self-test; python3 scripts/zigux/check-phase1-workflow-viability.py --self-test; python3 scripts/zigux/check-phase1-workflow-viability.py`",
    "historical_gap": "- current `master` workflow viability stays bounded to the shipped Phase 1 reminder packet, so treat `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` as broader closure-side or make-route packet members until fresh rereads recover them on current `master`.",
    "current_packet": "- the active bootstrap Phase 1 workflow now proves three live checks and one shipped checker self-test: direct-owner markers, string-review packet, the bench checker self-test, and workflow viability, and should stay narrower than the older installer-backed or live-bench closure stack until those routes materially return.",
    "current_neighbor": "- replay this packet on top of the current bootstrap workflow instead of reviving the older `scripts/zigux/check-kconfig-bridge.py --self-test` route name; the live non-Phase-1 neighbor step stays the current `scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test` self-test that already ships on `master`.",
    "next_step": "- if this lane reopens, harden the same current workflow packet first instead of reconstructing the broader missing closure-side Phase 1 validator family from historical route names alone.",
}

REQUIRED_WORKFLOW_LINES = {
    "selftest_direct_owner_name": "      - name: Self-test current Phase 1 direct-owner checker",
    "selftest_direct_owner_run": "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "check_direct_owner_name": "      - name: Check current Phase 1 direct-owner markers",
    "check_direct_owner_run": "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "selftest_string_name": "      - name: Self-test current Phase 1 string review checker",
    "selftest_string_run": "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "check_string_name": "      - name: Check current Phase 1 string review packet",
    "check_string_run": "        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    "selftest_bench_name": "      - name: Self-test current Phase 1 bench checker",
    "selftest_bench_run": "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "selftest_viability_name": "      - name: Self-test current Phase 1 workflow viability checker",
    "selftest_viability_run": "        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test",
    "check_viability_name": "      - name: Check current Phase 1 workflow viability",
    "check_viability_run": "        run: python3 scripts/zigux/check-phase1-workflow-viability.py",
}

STEP_ORDER = [
    "Self-test current Phase 1 direct-owner checker",
    "Check current Phase 1 direct-owner markers",
    "Self-test current Phase 1 string review checker",
    "Check current Phase 1 string review packet",
    "Self-test current Phase 1 bench checker",
    "Self-test current Phase 1 workflow viability checker",
    "Check current Phase 1 workflow viability",
]

FORBIDDEN_WORKFLOW_SNIPPETS = [
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    "make -C zigux phase1",
    "scripts/zigux/check-kconfig-bridge.py --self-test",
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current_line in text.splitlines() if current_line == line)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_absent(text: str, label: str, needle: str) -> list[str]:
    if needle in text:
        return [f"{label}:unexpected_present"]
    return []


def require_order(text: str) -> list[str]:
    positions: list[int] = []
    for label in STEP_ORDER:
        needle = f"- name: {label}"
        position = text.find(needle)
        if position == -1:
            return [f"workflow_order:missing:{label}"]
        positions.append(position)
    if positions != sorted(positions):
        return ["workflow_order:out_of_order"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILE_RELS:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    note_text = load_text(root, NOTE_REL)

    for label, line in REQUIRED_NOTE_LINES.items():
        failures.extend(require_exact_line(note_text, f"note:{label}", line))

    for label, line in REQUIRED_WORKFLOW_LINES.items():
        failures.extend(require_exact_line(workflow_text, f"workflow:{label}", line))

    failures.extend(require_order(workflow_text))

    for needle in FORBIDDEN_WORKFLOW_SNIPPETS:
        failures.extend(require_absent(workflow_text, f"workflow_forbidden:{needle}", needle))

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_note_text() -> str:
    ordered_lines = [
        REQUIRED_NOTE_LINES["status"],
        REQUIRED_NOTE_LINES["scope"],
        REQUIRED_NOTE_LINES["owner"],
        REQUIRED_NOTE_LINES["required_files"],
        REQUIRED_NOTE_LINES["selftest_steps"],
        REQUIRED_NOTE_LINES["live_steps"],
        REQUIRED_NOTE_LINES["command_packet"],
        REQUIRED_NOTE_LINES["historical_gap"],
        REQUIRED_NOTE_LINES["current_packet"],
        REQUIRED_NOTE_LINES["current_neighbor"],
        REQUIRED_NOTE_LINES["next_step"],
    ]
    return "# Phase 1 Workflow Viability\n\n" + "\n".join(ordered_lines) + "\n"


def sample_workflow_text() -> str:
    return """name: zigux-bootstrap

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Self-test current Phase 2 kconfig bridge checker
        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test

      - name: Self-test current Phase 1 direct-owner checker
        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test

      - name: Check current Phase 1 direct-owner markers
        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py

      - name: Self-test current Phase 1 string review checker
        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test

      - name: Check current Phase 1 string review packet
        run: python3 scripts/zigux/check-phase1-string-review-packet.py

      - name: Self-test current Phase 1 bench checker
        run: python3 scripts/zigux/check-phase1-bench.py --self-test

      - name: Self-test current Phase 1 workflow viability checker
        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test

      - name: Check current Phase 1 workflow viability
        run: python3 scripts/zigux/check-phase1-workflow-viability.py
"""


def build_sample_repo(root: Path) -> None:
    write_file(root, WORKFLOW_REL, sample_workflow_text())
    write_file(root, NOTE_REL, sample_note_text())
    for relative_path in REQUIRED_FILE_RELS[1:-1]:
        write_file(root, relative_path, "# placeholder\n")


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase1-workflow-viability-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        if collect_failures(root):
            print("self-test:unexpected_failures")
            return 1
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-workflow-viability-missing-file-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        (root / "scripts/zigux/check-phase1-bench.py").unlink()
        failures = collect_failures(root)
        if "missing_file:scripts/zigux/check-phase1-bench.py" not in failures:
            print("self-test:missing_file_case_failed")
            return 1
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-workflow-viability-missing-step-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "      - name: Self-test current Phase 1 bench checker\n        run: python3 scripts/zigux/check-phase1-bench.py --self-test\n\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if "workflow:selftest_bench_name:expected=1:actual=0" not in failures:
            print("self-test:missing_step_case_failed")
            return 1
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-workflow-viability-forbidden-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8")
            + "      - name: Old route\n        run: python3 scripts/zigux/validate-phase1.py\n",
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if "workflow_forbidden:scripts/zigux/validate-phase1.py:unexpected_present" not in failures:
            print("self-test:forbidden_case_failed")
            return 1
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-workflow-viability-stale-kconfig-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
                "python3 scripts/zigux/check-kconfig-bridge.py --self-test",
                1,
            ),
            encoding="utf-8",
        )
        failures = collect_failures(root)
        if "workflow_forbidden:scripts/zigux/check-kconfig-bridge.py --self-test:unexpected_present" not in failures:
            print("self-test:stale_kconfig_case_failed")
            return 1
        case_count += 1

    print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-workflow-viability:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
