#!/usr/bin/env python3
"""Guard the current Phase 1 bootstrap workflow viability packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
NOTE_REL = Path("Documentation/zigux/phase1-workflow-viability.md")
DOCS_SANITY_MARKER = (
    "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`"
)

REQUIRED_FILE_RELS = (
    WORKFLOW_REL,
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/check-phase1-workflow-viability.py"),
    Path("scripts/zigux/check-phase4-repo-reality-warning.py"),
    Path("scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    Path("scripts/zigux/check-phase4-tests-readme-packet.py"),
    Path("scripts/zigux/check-phase7-shared-control-gap.py"),
    Path("scripts/zigux/check-build-only-phase12-surface.py"),
    NOTE_REL,
)

REQUIRED_NOTE_LINES = (
    "- `PHASE1_WORKFLOW_STATUS=active`",
    "- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 reminder checks only`",
    "- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-viability`",
    "- `PHASE1_WORKFLOW_REQUIRED_FILES=.github/workflows/zigux-bootstrap.yml,scripts/zigux/check-zig-toolchain.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/check-phase1-workflow-viability.py,scripts/zigux/check-phase4-repo-reality-warning.py,scripts/zigux/check-phase4-reversible-delivery-pins.py,scripts/zigux/check-phase4-tests-readme-packet.py,scripts/zigux/check-phase7-shared-control-gap.py,scripts/zigux/check-build-only-phase12-surface.py,Documentation/zigux/phase1-workflow-viability.md`",
    "- `PHASE1_WORKFLOW_NEIGHBOR_TOOLCHAIN_STEPS=Self-test current Zig toolchain checker,Check current Zig toolchain policy surface`",
    "- `PHASE1_WORKFLOW_SELFTEST_STEPS=Self-test current Phase 1 direct-owner checker,Self-test current Phase 1 string review checker,Self-test current Phase 1 bench checker,Self-test current Phase 1 shared reminder checker,Self-test current Phase 1 workflow viability checker`",
    "- `PHASE1_WORKFLOW_LIVE_STEPS=Check current Phase 1 direct-owner markers,Check current Phase 1 string review packet,Check current Phase 1 shared reminder packet,Check current Phase 1 workflow viability`",
    "- `PHASE1_WORKFLOW_COMMAND_PACKET=python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test; python3 scripts/zigux/check-phase1-direct-owner-markers.py; python3 scripts/zigux/check-phase1-string-review-packet.py --self-test; python3 scripts/zigux/check-phase1-string-review-packet.py; python3 scripts/zigux/check-phase1-bench.py --self-test; python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test; python3 scripts/zigux/check-phase1-shared-reminder-packet.py; python3 scripts/zigux/check-phase1-workflow-viability.py --self-test; python3 scripts/zigux/check-phase1-workflow-viability.py`",
    "- `PHASE1_WORKFLOW_NEIGHBOR_PHASE2_STEPS=Self-test current Phase 2 kconfig bridge checker,Check current Phase 2 kconfig bridge packet,Self-test current Phase 2 kbuild routes checker,Check current Phase 2 kbuild packet,Self-test current Phase 2 toolchain pinning checker,Check current Phase 2 toolchain pinning packet`",
    "- `PHASE1_WORKFLOW_CURRENT_TAIL_STEPS=Self-test current Phase 4 repo-reality warning checker,Check current Phase 4 repo-reality warning packet,Self-test current Phase 4 reversible-delivery pin checker,Check current Phase 4 reversible-delivery pin packet,Self-test current Phase 4 tests README checker,Check current Phase 4 tests README packet,Self-test current Phase 7 shared-control gap checker,Check current Phase 7 shared-control gap packet,Self-test current Phase 12 build-only checker,Check current docs-root sanity markers`",
    "- current `master` workflow viability stays bounded to the shipped Phase 1 reminder packet, so treat `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` as broader closure-side or make-route packet members until fresh rereads recover them on current `master`.",
    "- the active bootstrap Phase 1 workflow now keeps the direct-owner, string-review, shared-reminder, and workflow-viability live checks together with the direct-owner, string-review, bench, shared-reminder, and workflow-viability self-tests, and should stay narrower than the older installer-backed or live-bench closure stack until those routes materially return.",
    "- keep the newer `scripts/zigux/check-phase1-shared-reminder-packet.py` pair explicit beside direct-owner, string-review, bench, and workflow viability so this lane does not silently regress the already-shipped Phase 1 reminder packet while hardening the workflow shape.",
    "- replay this packet on top of the current bootstrap workflow instead of reviving older Phase 2 neighbor names or dropping the newer current ones; the live non-Phase-1 neighbor packet now keeps the current `scripts/zigux/check-zig-toolchain.py` self-test plus policy-surface pair ahead of the current `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, and `scripts/zigux/check-phase2-toolchain-pinning.py` self-test plus live-check packet.",
    "- keep the current post-Phase-1 bootstrap tail explicit too: the same workflow now carries the shipped `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/check-phase7-shared-control-gap.py`, and `scripts/zigux/check-build-only-phase12-surface.py` packet plus the docs-root sanity marker check after the Lane 17 Phase 1 slice, so this lane must not silently regress those later current-master steps while refreshing the Phase 1 packet.",
    "- if this lane reopens, harden the same current workflow packet first instead of reconstructing the broader missing closure-side Phase 1 validator family from historical route names alone.",
)

WORKFLOW_LINE_RULES = (
    ("workflow:selftest_zig_toolchain_name", "      - name: Self-test current Zig toolchain checker"),
    ("workflow:selftest_zig_toolchain_run", "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test"),
    ("workflow:check_zig_toolchain_name", "      - name: Check current Zig toolchain policy surface"),
    ("workflow:check_zig_toolchain_run", "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only"),
    ("workflow:selftest_phase2_kconfig_name", "      - name: Self-test current Phase 2 kconfig bridge checker"),
    ("workflow:selftest_phase2_kconfig_run", "        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test"),
    ("workflow:check_phase2_kconfig_name", "      - name: Check current Phase 2 kconfig bridge packet"),
    ("workflow:check_phase2_kconfig_run", "        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    ("workflow:selftest_phase2_kbuild_name", "      - name: Self-test current Phase 2 kbuild routes checker"),
    ("workflow:selftest_phase2_kbuild_run", "        run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test"),
    ("workflow:check_phase2_kbuild_name", "      - name: Check current Phase 2 kbuild packet"),
    ("workflow:check_phase2_kbuild_run", "        run: python3 scripts/zigux/check-phase2-kbuild-routes.py"),
    ("workflow:selftest_phase2_toolchain_name", "      - name: Self-test current Phase 2 toolchain pinning checker"),
    ("workflow:selftest_phase2_toolchain_run", "        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test"),
    ("workflow:check_phase2_toolchain_name", "      - name: Check current Phase 2 toolchain pinning packet"),
    ("workflow:check_phase2_toolchain_run", "        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py"),
    ("workflow:selftest_direct_owner_name", "      - name: Self-test current Phase 1 direct-owner checker"),
    ("workflow:selftest_direct_owner_run", "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test"),
    ("workflow:check_direct_owner_name", "      - name: Check current Phase 1 direct-owner markers"),
    ("workflow:check_direct_owner_run", "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py"),
    ("workflow:selftest_string_name", "      - name: Self-test current Phase 1 string review checker"),
    ("workflow:selftest_string_run", "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test"),
    ("workflow:check_string_name", "      - name: Check current Phase 1 string review packet"),
    ("workflow:check_string_run", "        run: python3 scripts/zigux/check-phase1-string-review-packet.py"),
    ("workflow:selftest_bench_name", "      - name: Self-test current Phase 1 bench checker"),
    ("workflow:selftest_bench_run", "        run: python3 scripts/zigux/check-phase1-bench.py --self-test"),
    ("workflow:selftest_shared_reminder_name", "      - name: Self-test current Phase 1 shared reminder checker"),
    ("workflow:selftest_shared_reminder_run", "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test"),
    ("workflow:check_shared_reminder_name", "      - name: Check current Phase 1 shared reminder packet"),
    ("workflow:check_shared_reminder_run", "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py"),
    ("workflow:selftest_viability_name", "      - name: Self-test current Phase 1 workflow viability checker"),
    ("workflow:selftest_viability_run", "        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test"),
    ("workflow:check_viability_name", "      - name: Check current Phase 1 workflow viability"),
    ("workflow:check_viability_run", "        run: python3 scripts/zigux/check-phase1-workflow-viability.py"),
    ("workflow:selftest_phase4_warning_name", "      - name: Self-test current Phase 4 repo-reality warning checker"),
    ("workflow:selftest_phase4_warning_run", "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test"),
    ("workflow:check_phase4_warning_name", "      - name: Check current Phase 4 repo-reality warning packet"),
    ("workflow:check_phase4_warning_run", "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py"),
    ("workflow:selftest_phase4_reversible_name", "      - name: Self-test current Phase 4 reversible-delivery pin checker"),
    ("workflow:selftest_phase4_reversible_run", "        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test"),
    ("workflow:check_phase4_reversible_name", "      - name: Check current Phase 4 reversible-delivery pin packet"),
    ("workflow:check_phase4_reversible_run", "        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    ("workflow:selftest_phase4_tests_name", "      - name: Self-test current Phase 4 tests README checker"),
    ("workflow:selftest_phase4_tests_run", "        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test"),
    ("workflow:check_phase4_tests_name", "      - name: Check current Phase 4 tests README packet"),
    ("workflow:check_phase4_tests_run", "        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py"),
    ("workflow:selftest_phase7_name", "      - name: Self-test current Phase 7 shared-control gap checker"),
    ("workflow:selftest_phase7_run", "        run: python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test"),
    ("workflow:check_phase7_name", "      - name: Check current Phase 7 shared-control gap packet"),
    ("workflow:check_phase7_run", "        run: python3 scripts/zigux/check-phase7-shared-control-gap.py"),
    ("workflow:selftest_phase12_name", "      - name: Self-test current Phase 12 build-only checker"),
    ("workflow:selftest_phase12_run", "        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test"),
    ("workflow:check_docs_sanity_name", "      - name: Check current docs-root sanity markers"),
)

STEP_ORDER = (
    "Self-test current Zig toolchain checker",
    "Check current Zig toolchain policy surface",
    "Self-test current Phase 2 kconfig bridge checker",
    "Check current Phase 2 kconfig bridge packet",
    "Self-test current Phase 2 kbuild routes checker",
    "Check current Phase 2 kbuild packet",
    "Self-test current Phase 2 toolchain pinning checker",
    "Check current Phase 2 toolchain pinning packet",
    "Self-test current Phase 1 direct-owner checker",
    "Check current Phase 1 direct-owner markers",
    "Self-test current Phase 1 string review checker",
    "Check current Phase 1 string review packet",
    "Self-test current Phase 1 bench checker",
    "Self-test current Phase 1 shared reminder checker",
    "Check current Phase 1 shared reminder packet",
    "Self-test current Phase 1 workflow viability checker",
    "Check current Phase 1 workflow viability",
    "Self-test current Phase 4 repo-reality warning checker",
    "Check current Phase 4 repo-reality warning packet",
    "Self-test current Phase 4 reversible-delivery pin checker",
    "Check current Phase 4 reversible-delivery pin packet",
    "Self-test current Phase 4 tests README checker",
    "Check current Phase 4 tests README packet",
    "Self-test current Phase 7 shared-control gap checker",
    "Check current Phase 7 shared-control gap packet",
    "Self-test current Phase 12 build-only checker",
    "Check current docs-root sanity markers",
)

FORBIDDEN_WORKFLOW_SNIPPETS = (
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    "make -C zigux phase1",
    "scripts/zigux/check-kconfig-bridge.py --self-test",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "scripts/zigux/check-phase9-build-only-surface.py",
    "Run Phase 9 runtime helper tests",
)


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line(text: str, line: str) -> int:
    return sum(1 for current in text.splitlines() if current == line)


def require_once(text: str, label: str, line: str) -> list[str]:
    count = count_exact_line(text, line)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_order(text: str) -> list[str]:
    positions: list[int] = []
    for step in STEP_ORDER:
        needle = f"- name: {step}"
        position = text.find(needle)
        if position == -1:
            return [f"workflow_order:missing:{step}"]
        positions.append(position)
    return [] if positions == sorted(positions) else ["workflow_order:out_of_order"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILE_RELS:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    note_text = load_text(root, NOTE_REL)

    for line in REQUIRED_NOTE_LINES:
        failures.extend(require_once(note_text, "note", line))
    for label, line in WORKFLOW_LINE_RULES:
        failures.extend(require_once(workflow_text, label, line))
    if DOCS_SANITY_MARKER not in workflow_text:
        failures.append("workflow:docs_sanity_marker:missing")
    failures.extend(require_order(workflow_text))
    for needle in FORBIDDEN_WORKFLOW_SNIPPETS:
        if needle in workflow_text:
            failures.append(f"workflow_forbidden:{needle}:unexpected_present")
    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_workflow_text() -> str:
    lines = ["name: zigux-bootstrap", "", "jobs:", "  bootstrap:", "    runs-on: ubuntu-latest", "    steps:"]
    for _, line in WORKFLOW_LINE_RULES:
        lines.append(line)
        if line.startswith("        run:"):
            lines.append("")
    lines.extend(
        [
            "        run: |",
            "          python3 - <<'PY2'",
            f"          print('{DOCS_SANITY_MARKER}')",
            "          PY2",
            "",
        ]
    )
    return "\n".join(lines)


def build_sample_repo(root: Path) -> None:
    write_file(root, WORKFLOW_REL, sample_workflow_text())
    write_file(root, NOTE_REL, "# Phase 1 Workflow Viability\n\n" + "\n".join(REQUIRED_NOTE_LINES) + "\n")
    for relative_path in REQUIRED_FILE_RELS[1:-1]:
        write_file(root, relative_path, "# placeholder\n")


def rewrite_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"missing sample text: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase1-workflow-viability-") as tmpdir:
        root = Path(tmpdir)

        build_sample_repo(root)
        if collect_failures(root):
            print("self-test:unexpected_failures")
            return 1
        case_count += 1

        build_sample_repo(root)
        (root / "scripts/zigux/check-zig-toolchain.py").unlink()
        if "missing_file:scripts/zigux/check-zig-toolchain.py" not in collect_failures(root):
            print("self-test:missing_toolchain_file_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        (root / "scripts/zigux/check-phase7-shared-control-gap.py").unlink()
        if "missing_file:scripts/zigux/check-phase7-shared-control-gap.py" not in collect_failures(root):
            print("self-test:missing_phase7_file_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        (root / "scripts/zigux/check-phase4-repo-reality-warning.py").unlink()
        if "missing_file:scripts/zigux/check-phase4-repo-reality-warning.py" not in collect_failures(root):
            print("self-test:missing_file_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text(
            rewrite_once(
                workflow_path.read_text(encoding="utf-8"),
                "      - name: Self-test current Zig toolchain checker\n",
            ),
            encoding="utf-8",
        )
        if "workflow:selftest_zig_toolchain_name:expected=1:actual=0" not in collect_failures(root):
            print("self-test:missing_toolchain_step_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path.write_text(
            rewrite_once(
                workflow_path.read_text(encoding="utf-8"),
                "      - name: Self-test current Phase 2 kbuild routes checker\n",
            ),
            encoding="utf-8",
        )
        if "workflow:selftest_phase2_kbuild_name:expected=1:actual=0" not in collect_failures(root):
            print("self-test:missing_phase2_step_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path.write_text(
            rewrite_once(
                workflow_path.read_text(encoding="utf-8"),
                "      - name: Check current Phase 1 shared reminder packet\n",
            ),
            encoding="utf-8",
        )
        if "workflow:check_shared_reminder_name:expected=1:actual=0" not in collect_failures(root):
            print("self-test:missing_phase1_shared_reminder_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path.write_text(
            rewrite_once(
                workflow_path.read_text(encoding="utf-8"),
                "      - name: Check current Phase 4 reversible-delivery pin packet\n",
            ),
            encoding="utf-8",
        )
        if "workflow:check_phase4_reversible_name:expected=1:actual=0" not in collect_failures(root):
            print("self-test:missing_phase4_step_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path.write_text(
            rewrite_once(
                workflow_path.read_text(encoding="utf-8"),
                "      - name: Check current Phase 4 tests README packet\n",
            ),
            encoding="utf-8",
        )
        if "workflow:check_phase4_tests_name:expected=1:actual=0" not in collect_failures(root):
            print("self-test:missing_phase4_tests_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path.write_text(
            rewrite_once(
                workflow_path.read_text(encoding="utf-8"),
                "      - name: Check current Phase 7 shared-control gap packet\n",
            ),
            encoding="utf-8",
        )
        if "workflow:check_phase7_name:expected=1:actual=0" not in collect_failures(root):
            print("self-test:missing_phase7_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path.write_text(
            rewrite_once(workflow_path.read_text(encoding="utf-8"), DOCS_SANITY_MARKER, "missing"),
            encoding="utf-8",
        )
        if "workflow:docs_sanity_marker:missing" not in collect_failures(root):
            print("self-test:missing_tail_marker_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8")
            + "      - name: Old route\n        run: python3 scripts/zigux/validate-phase1.py\n",
            encoding="utf-8",
        )
        if "workflow_forbidden:scripts/zigux/validate-phase1.py:unexpected_present" not in collect_failures(root):
            print("self-test:forbidden_phase1_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8")
            + "      - name: Run Phase 9 runtime helper tests\n        run: make -C zigux phase9\n",
            encoding="utf-8",
        )
        if "workflow_forbidden:Run Phase 9 runtime helper tests:unexpected_present" not in collect_failures(root):
            print("self-test:forbidden_phase9_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path.write_text(
            rewrite_once(
                workflow_path.read_text(encoding="utf-8"),
                "python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
                "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
            ),
            encoding="utf-8",
        )
        if (
            "workflow_forbidden:scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test:unexpected_present"
            not in collect_failures(root)
        ):
            print("self-test:stale_phase2_neighbor_case_failed")
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

    root = Path(args.root).resolve() if args.root else DEFAULT_ROOT.resolve()
    failures = collect_failures(root)
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-workflow-viability:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
