#!/usr/bin/env python3
"""Guard the current Phase 1 bootstrap workflow viability packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
NOTE_REL = Path("Documentation/zigux/phase1-workflow-viability.md")
DOCS_SANITY_MARKER = "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`"

REQUIRED_FILES = (
    WORKFLOW_REL,
    NOTE_REL,
    Path("scripts/zigux/check-zig-toolchain.py"),
    Path("scripts/zigux/zig-toolchain-policy.json"),
    Path("scripts/zigux/check-kconfig-bridge.py"),
    Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-kbuild-routes.py"),
    Path("scripts/zigux/check-phase2-tests-readme-alignment.py"),
    Path("scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    Path("scripts/zigux/check-phase2-toolchain-pinning.py"),
    Path("scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    Path("scripts/zigux/check-phase2-required-make-routes.py"),
    Path("scripts/zigux/check-phase2-docs-shared-reminder.py"),
    Path("scripts/zigux/validate-phase2.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/check-phase1-workflow-viability.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
    Path("scripts/zigux/check-phase4-repo-reality-warning.py"),
    Path("scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    Path("scripts/zigux/check-phase4-tests-readme-packet.py"),
    Path("scripts/zigux/check-phase7-shared-control-gap.py"),
    Path("scripts/zigux/check-phase10-bootstrap-route.py"),
    Path("scripts/zigux/check-phase11-hvc-cleanup-current-head.py"),
    Path("scripts/zigux/check-phase11-build-inventory.py"),
    Path("scripts/zigux/check-phase11-matrix-gap-survey.py"),
    Path("scripts/zigux/check-build-only-phase12-surface.py"),
    Path("scripts/zigux/check-phase12-release-readiness-packet.py"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/phase12-release-readiness-survey.md"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/build.zig"),
    Path("zigux/Makefile"),
    Path("zigux/tests/phase12_build.zig"),
    Path("zigux/tests/phase8_libbpf_segments_only_build.zig"),
)

REQUIRED_NOTE_LINES = (
    "- `PHASE1_WORKFLOW_STATUS=active`",
    "- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 reminder checks only`",
    "- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-viability`",
    "- `PHASE1_WORKFLOW_INSERTION_POINT=after current Phase 1 shared reminder packet and before current Phase 3 interop packet`",
    "Validate current Phase 2 tool packet",
    "Self-test current Phase 3 interop packet",
)

REQUIRED_STEPS = (
    ("Self-test current Zig toolchain checker", "python3 scripts/zigux/check-zig-toolchain.py --self-test"),
    ("Check current Zig toolchain policy packet", "python3 scripts/zigux/check-zig-toolchain.py --policy-only"),
    ("Check current pinned Zig archive packet", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing"),
    ("Self-test current kconfig bridge checker", "python3 scripts/zigux/check-kconfig-bridge.py --self-test"),
    ("Check current kconfig bridge packet", "python3 scripts/zigux/check-kconfig-bridge.py"),
    ("Run current Phase 2 confdata bridge unit tests", "zig test scripts/zigux/kconfig/confdata_bridge.zig"),
    ("Self-test current Phase 2 kconfig bridge checker", "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test"),
    ("Check current Phase 2 kconfig bridge packet", "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py"),
    ("Self-test current Phase 2 kbuild routes checker", "python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test"),
    ("Check current Phase 2 kbuild packet", "python3 scripts/zigux/check-phase2-kbuild-routes.py"),
    ("Self-test current Phase 2 tests README checker", "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test"),
    ("Check current Phase 2 tests README packet", "python3 scripts/zigux/check-phase2-tests-readme-alignment.py"),
    ("Self-test current Phase 2 cross selftest alignment checker", "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test"),
    ("Check current Phase 2 cross alignment packet", "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py"),
    ("Self-test current Phase 2 toolchain pinning checker", "python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test"),
    ("Check current Phase 2 toolchain pinning packet", "python3 scripts/zigux/check-phase2-toolchain-pinning.py"),
    ("Self-test current Phase 2 toolchain pin-scope checker", "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test"),
    ("Check current Phase 2 toolchain pin-scope packet", "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py"),
    ("Self-test current Phase 2 required-make-routes checker", "python3 scripts/zigux/check-phase2-required-make-routes.py --self-test"),
    ("Check current Phase 2 required-make-routes packet", "python3 scripts/zigux/check-phase2-required-make-routes.py"),
    ("Self-test current Phase 2 shared reminder checker", "python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test"),
    ("Check current Phase 2 shared reminder packet", "python3 scripts/zigux/check-phase2-docs-shared-reminder.py"),
    ("Validate current Phase 2 tool packet", "python3 scripts/zigux/validate-phase2.py"),
    ("Self-test current Phase 1 direct-owner checker", "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test"),
    ("Check current Phase 1 direct-owner markers", "python3 scripts/zigux/check-phase1-direct-owner-markers.py"),
    ("Self-test current Phase 1 string review checker", "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test"),
    ("Check current Phase 1 string review packet", "python3 scripts/zigux/check-phase1-string-review-packet.py"),
    ("Self-test current Phase 1 bench checker", "python3 scripts/zigux/check-phase1-bench.py --self-test"),
    ("Self-test current Phase 1 shared reminder checker", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test"),
    ("Check current Phase 1 shared reminder packet", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py"),
    ("Self-test current Phase 1 workflow viability checker", "python3 scripts/zigux/check-phase1-workflow-viability.py --self-test"),
    ("Check current Phase 1 workflow viability", "python3 scripts/zigux/check-phase1-workflow-viability.py"),
    ("Self-test current Phase 3 interop packet", "python3 scripts/zigux/validate_phase3_selftest.py"),
    ("Check current Phase 3 interop packet", "python3 scripts/zigux/run-phase3-checks.py"),
    ("Run current Phase 3 shared tests-root packet", "zig build phase3-test --build-file zigux/tests/build.zig"),
    ("Run current Phase 1 shared tests-root smoke", "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig"),
)

ORDER_STEPS = (
    "Check current Phase 1 shared reminder packet",
    "Self-test current Phase 1 workflow viability checker",
    "Check current Phase 1 workflow viability",
    "Self-test current Phase 3 interop packet",
    "Run current Phase 1 shared tests-root smoke",
)

FORBIDDEN_SNIPPETS = (
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
    "Check current Zig toolchain policy surface",
)
ALLOWED_BENCH_LINE = "        run: python3 scripts/zigux/check-phase1-bench.py --self-test"


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel.as_posix()}")
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    note_text = load_text(root, NOTE_REL)

    for line in REQUIRED_NOTE_LINES:
        if line not in note_text:
            failures.append(f"missing_note_line:{line}")

    positions = []
    for step_name, run_command in REQUIRED_STEPS:
        name_line = f"      - name: {step_name}"
        run_line = f"        run: {run_command}"
        if name_line not in workflow_text:
            failures.append(f"missing_step:{step_name}")
        if run_line not in workflow_text:
            failures.append(f"missing_run:{step_name}")
        positions.append(workflow_text.find(name_line))

    if any(pos == -1 for pos in positions):
        return failures
    if positions != sorted(positions):
        failures.append("workflow_order:out_of_order")

    order_positions = [workflow_text.find(f"- name: {name}") for name in ORDER_STEPS]
    if any(pos == -1 for pos in order_positions) or order_positions != sorted(order_positions):
        failures.append("workflow_insertion_point:unexpected")

    if DOCS_SANITY_MARKER not in workflow_text:
        failures.append("workflow:docs_sanity_marker:missing")

    bench_lines = [line for line in workflow_text.splitlines() if "python3 scripts/zigux/check-phase1-bench.py" in line]
    if bench_lines != [ALLOWED_BENCH_LINE]:
        failures.append("workflow_forbidden:phase1_live_bench:unexpected_present")

    for snippet in FORBIDDEN_SNIPPETS:
        if snippet in workflow_text:
            failures.append(f"workflow_forbidden:{snippet}:unexpected_present")

    return failures


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    workflow_lines = ["name: zigux-bootstrap", "", "jobs:", "  bootstrap:", "    runs-on: ubuntu-latest", "    steps:"]
    for step_name, run_command in REQUIRED_STEPS:
        workflow_lines.append(f"      - name: {step_name}")
        workflow_lines.append(f"        run: {run_command}")
        workflow_lines.append("")
    workflow_lines.extend(
        (
            "      - name: Check current docs-root sanity markers",
            "        run: |",
            "          python3 - <<'PY2'",
            f"          print('{DOCS_SANITY_MARKER}')",
            "          PY2",
            "",
        )
    )
    write_file(root / WORKFLOW_REL, "\n".join(workflow_lines))
    write_file(
        root / NOTE_REL,
        "\n".join(
            [
                "# Phase 1 Workflow Viability",
                "",
                "- `PHASE1_WORKFLOW_STATUS=active`",
                "- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 reminder checks only`",
                "- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-viability`",
                "- `PHASE1_WORKFLOW_INSERTION_POINT=after current Phase 1 shared reminder packet and before current Phase 3 interop packet`",
                "- Validate current Phase 2 tool packet",
                "- Self-test current Phase 3 interop packet",
                "",
            ]
        ),
    )
    for rel in REQUIRED_FILES:
        if rel in (WORKFLOW_REL, NOTE_REL):
            continue
        write_file(root / rel, "# placeholder\n")


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
        (root / "scripts/zigux/validate-phase2.py").unlink()
        if "missing_file:scripts/zigux/validate-phase2.py" not in collect_failures(root):
            print("self-test:missing_phase2_validator_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path = root / WORKFLOW_REL
        workflow_text = workflow_path.read_text(encoding="utf-8").replace(
            "      - name: Self-test current Phase 3 interop packet\n        run: python3 scripts/zigux/validate_phase3_selftest.py\n\n",
            "",
            1,
        )
        workflow_path.write_text(workflow_text, encoding="utf-8")
        if "missing_step:Self-test current Phase 3 interop packet" not in collect_failures(root):
            print("self-test:missing_phase3_selftest_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path = root / WORKFLOW_REL
        workflow_text = workflow_path.read_text(encoding="utf-8").replace(
            "      - name: Self-test current Phase 1 workflow viability checker\n        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test\n\n"
            "      - name: Check current Phase 1 workflow viability\n        run: python3 scripts/zigux/check-phase1-workflow-viability.py\n\n",
            "      - name: Self-test current Phase 3 interop packet\n        run: python3 scripts/zigux/validate_phase3_selftest.py\n\n"
            "      - name: Self-test current Phase 1 workflow viability checker\n        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test\n\n"
            "      - name: Check current Phase 1 workflow viability\n        run: python3 scripts/zigux/check-phase1-workflow-viability.py\n\n",
            1,
        )
        workflow_path.write_text(workflow_text, encoding="utf-8")
        if "workflow_insertion_point:unexpected" not in collect_failures(root):
            print("self-test:insertion_order_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8")
            + "      - name: Forbidden bench live route\n        run: python3 scripts/zigux/check-phase1-bench.py\n",
            encoding="utf-8",
        )
        if "workflow_forbidden:phase1_live_bench:unexpected_present" not in collect_failures(root):
            print("self-test:live_bench_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        note_path = root / NOTE_REL
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                "- `PHASE1_WORKFLOW_INSERTION_POINT=after current Phase 1 shared reminder packet and before current Phase 3 interop packet`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        if "missing_note_line:- `PHASE1_WORKFLOW_INSERTION_POINT=after current Phase 1 shared reminder packet and before current Phase 3 interop packet`" not in collect_failures(root):
            print("self-test:missing_note_case_failed")
            return 1
        case_count += 1

    print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve() if args.root else DEFAULT_ROOT.resolve()
    failures = collect_failures(root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase1-workflow-viability:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
