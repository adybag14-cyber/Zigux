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
INSERTION_LINE = (
    "- `PHASE1_WORKFLOW_INSERTION_POINT=after current Phase 1 shared reminder packet "
    "and before current Phase 3 interop packet`"
)

TOOLCHAIN_STEPS = (
    ("Self-test current Zig toolchain checker", "python3 scripts/zigux/check-zig-toolchain.py --self-test"),
    ("Check current Zig toolchain policy packet", "python3 scripts/zigux/check-zig-toolchain.py --policy-only"),
    ("Check current pinned Zig archive packet", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing"),
)

PHASE2_STEPS = (
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
)

PHASE1_STEPS = (
    ("Self-test current Phase 1 direct-owner checker", "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test"),
    ("Check current Phase 1 direct-owner markers", "python3 scripts/zigux/check-phase1-direct-owner-markers.py"),
    ("Self-test current Phase 1 string review checker", "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test"),
    ("Check current Phase 1 string review packet", "python3 scripts/zigux/check-phase1-string-review-packet.py"),
    ("Self-test current Phase 1 bench checker", "python3 scripts/zigux/check-phase1-bench.py --self-test"),
    ("Self-test current Phase 1 shared reminder checker", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test"),
    ("Check current Phase 1 shared reminder packet", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py"),
    ("Self-test current Phase 1 workflow viability checker", "python3 scripts/zigux/check-phase1-workflow-viability.py --self-test"),
    ("Check current Phase 1 workflow viability", "python3 scripts/zigux/check-phase1-workflow-viability.py"),
)

POST_PHASE1_STEPS = (
    ("Self-test current Phase 3 interop packet", "python3 scripts/zigux/validate_phase3_selftest.py"),
    ("Check current Phase 3 interop packet", "python3 scripts/zigux/run-phase3-checks.py"),
    ("Run current Phase 3 shared tests-root packet", "zig build phase3-test --build-file zigux/tests/build.zig"),
    ("Run current Phase 1 shared tests-root smoke", "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig"),
    ("Self-test current Phase 4 repo-reality warning checker", "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test"),
    ("Check current Phase 4 repo-reality warning packet", "python3 scripts/zigux/check-phase4-repo-reality-warning.py"),
    ("Self-test current Phase 4 reversible-delivery pin checker", "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test"),
    ("Check current Phase 4 reversible-delivery pin packet", "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py"),
    ("Self-test current Phase 4 tests README checker", "python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test"),
    ("Check current Phase 4 tests README packet", "python3 scripts/zigux/check-phase4-tests-readme-packet.py"),
    ("Self-test current Phase 7 shared-control gap checker", "python3 scripts/zigux/check-phase7-shared-control-gap.py --self-test"),
    ("Check current Phase 7 shared-control gap packet", "python3 scripts/zigux/check-phase7-shared-control-gap.py"),
    ("Self-test current Phase 10 bootstrap route checker", "python3 scripts/zigux/check-phase10-bootstrap-route.py --self-test"),
    ("Check current Phase 10 bootstrap route", "python3 scripts/zigux/check-phase10-bootstrap-route.py"),
    ("Validate Phase 10 checker-backed review packet", "make -C zigux phase10-validate"),
    ("Run Phase 10 helper tests", "make -C zigux phase10-test"),
    ("Self-test current Phase 11 HVC cleanup current-head checker", "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test"),
    ("Check current Phase 11 HVC cleanup current-head packet", "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py"),
    ("Self-test current Phase 11 build inventory checker", "python3 scripts/zigux/check-phase11-build-inventory.py --self-test"),
    ("Check current Phase 11 build inventory packet", "python3 scripts/zigux/check-phase11-build-inventory.py"),
    ("Self-test current Phase 11 matrix-gap survey checker", "python3 scripts/zigux/check-phase11-matrix-gap-survey.py --self-test"),
    ("Check current Phase 11 matrix-gap survey packet", "python3 scripts/zigux/check-phase11-matrix-gap-survey.py"),
    ("Self-test current Phase 12 build-only surface checker", "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test"),
    ("Check current Phase 12 build-only surface", "python3 scripts/zigux/check-build-only-phase12-surface.py"),
    ("Self-test current Phase 12 release-readiness packet checker", "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test"),
    ("Validate Phase 12 degraded-workflow bundle", "make -C zigux phase12-validate"),
    ("Check current Phase 12 release-readiness packet", "python3 scripts/zigux/check-phase12-release-readiness-packet.py"),
    ("Run focused Phase 12 smoke shard", "make -C zigux phase12-smoke"),
    ("Run Phase 12 complex driver tests", "zig build test --build-file zigux/tests/phase12_build.zig --summary all"),
    ("Validate Phase 8 tooling gates", "make -C zigux phase8-validate"),
    ("Run focused Phase 8 libbpf segment survey tests", "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all"),
    ("Check current docs-root sanity markers", "__DOCS_SANITY__"),
)

REQUIRED_FILE_RELS = (
    WORKFLOW_REL,
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
    NOTE_REL,
)

REQUIRED_NOTE_LINES = (
    "- `PHASE1_WORKFLOW_STATUS=active`",
    "- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 reminder checks only`",
    "- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-viability`",
    INSERTION_LINE,
)

FORBIDDEN_WORKFLOW_SNIPPETS = (
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/validate-phase1-closure.py",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
    "python3 scripts/zigux/check-phase1-bench.py",
    "Check current Zig toolchain policy surface",
)
ALLOWED_BENCH_LINE = "        run: python3 scripts/zigux/check-phase1-bench.py --self-test"


def marker_line(name: str, steps: tuple[tuple[str, str], ...]) -> str:
    return "- `{name}={steps}`".format(
        name=name,
        steps=",".join(step_name for step_name, _ in steps),
    )


EXPECTED_DYNAMIC_NOTE_LINES = (
    "- `PHASE1_WORKFLOW_REQUIRED_FILES={files}`".format(
        files=",".join(path.as_posix() for path in REQUIRED_FILE_RELS)
    ),
    marker_line("PHASE1_WORKFLOW_NEIGHBOR_TOOLCHAIN_STEPS", TOOLCHAIN_STEPS),
    marker_line("PHASE1_WORKFLOW_NEIGHBOR_PHASE2_STEPS", PHASE2_STEPS),
    marker_line(
        "PHASE1_WORKFLOW_SELFTEST_STEPS",
        tuple(step for step in PHASE1_STEPS if step[0].startswith("Self-test ")),
    ),
    marker_line(
        "PHASE1_WORKFLOW_LIVE_STEPS",
        tuple(step for step in PHASE1_STEPS if not step[0].startswith("Self-test ")),
    ),
    marker_line("PHASE1_WORKFLOW_POST_PHASE1_STEPS", POST_PHASE1_STEPS),
    "- `PHASE1_WORKFLOW_COMMAND_PACKET="
    "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test; "
    "python3 scripts/zigux/check-phase1-direct-owner-markers.py; "
    "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test; "
    "python3 scripts/zigux/check-phase1-string-review-packet.py; "
    "python3 scripts/zigux/check-phase1-bench.py --self-test; "
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test; "
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py; "
    "python3 scripts/zigux/check-phase1-workflow-viability.py --self-test; "
    "python3 scripts/zigux/check-phase1-workflow-viability.py; "
    "python3 scripts/zigux/validate_phase3_selftest.py; "
    "python3 scripts/zigux/run-phase3-checks.py; "
    "zig build phase3-test --build-file zigux/tests/build.zig; "
    "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "- `PHASE1_WORKFLOW_FORBIDDEN_HISTORICAL_SNIPPETS="
    "scripts/zigux/validate-phase1.py,scripts/zigux/validate-phase1-closure.py,"
    "make -C zigux phase1-validate,make -C zigux phase1-test,make -C zigux phase1-bench,"
    "python3 scripts/zigux/check-phase1-bench.py,Check current Zig toolchain policy surface`",
)


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line(text: str, line: str) -> int:
    return sum(1 for current in text.splitlines() if current == line)


def require_once(text: str, label: str, line: str) -> list[str]:
    count = count_exact_line(text, line)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_step(workflow_text: str, step_name: str, run_command: str) -> list[str]:
    failures: list[str] = []
    failures.extend(
        require_once(workflow_text, f"workflow_step:{step_name}", f"      - name: {step_name}")
    )
    if run_command != "__DOCS_SANITY__":
        failures.extend(
            require_once(workflow_text, f"workflow_run:{step_name}", f"        run: {run_command}")
        )
    return failures


def require_order(workflow_text: str, step_names: tuple[str, ...]) -> list[str]:
    positions: list[int] = []
    for step_name in step_names:
        marker = f"- name: {step_name}"
        position = workflow_text.find(marker)
        if position == -1:
            return [f"workflow_order:missing:{step_name}"]
        positions.append(position)
    return [] if positions == sorted(positions) else ["workflow_order:out_of_order"]


def check_bench_forbidden(workflow_text: str, failures: list[str]) -> None:
    if "python3 scripts/zigux/check-phase1-bench.py" not in workflow_text:
        return
    bench_lines = [
        line for line in workflow_text.splitlines()
        if "python3 scripts/zigux/check-phase1-bench.py" in line
    ]
    if bench_lines != [ALLOWED_BENCH_LINE]:
        failures.append("workflow_forbidden:phase1_live_bench:unexpected_present")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILE_RELS:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    note_text = load_text(root, NOTE_REL)

    for line in REQUIRED_NOTE_LINES + EXPECTED_DYNAMIC_NOTE_LINES:
        failures.extend(require_once(note_text, "note", line))

    all_steps = TOOLCHAIN_STEPS + PHASE2_STEPS + PHASE1_STEPS + POST_PHASE1_STEPS
    for step_name, run_command in all_steps:
        failures.extend(require_step(workflow_text, step_name, run_command))
    failures.extend(require_order(workflow_text, tuple(step_name for step_name, _ in all_steps)))

    if DOCS_SANITY_MARKER not in workflow_text:
        failures.append("workflow:docs_sanity_marker:missing")

    shared_reminder_pos = workflow_text.find("- name: Check current Phase 1 shared reminder packet")
    viability_selftest_pos = workflow_text.find("- name: Self-test current Phase 1 workflow viability checker")
    viability_live_pos = workflow_text.find("- name: Check current Phase 1 workflow viability")
    phase3_selftest_pos = workflow_text.find("- name: Self-test current Phase 3 interop packet")
    smoke_pos = workflow_text.find("- name: Run current Phase 1 shared tests-root smoke")
    if not (
        shared_reminder_pos != -1
        and viability_selftest_pos != -1
        and viability_live_pos != -1
        and phase3_selftest_pos != -1
        and smoke_pos != -1
        and shared_reminder_pos < viability_selftest_pos < viability_live_pos < phase3_selftest_pos < smoke_pos
    ):
        failures.append("workflow_insertion_point:unexpected")

    check_bench_forbidden(workflow_text, failures)
    for needle in FORBIDDEN_WORKFLOW_SNIPPETS:
        if needle == "python3 scripts/zigux/check-phase1-bench.py":
            continue
        if needle in workflow_text:
            failures.append(f"workflow_forbidden:{needle}:unexpected_present")

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_note_text() -> str:
    lines = ["# Phase 1 Workflow Viability", ""]
    lines.extend(REQUIRED_NOTE_LINES[:3])
    lines.extend(EXPECTED_DYNAMIC_NOTE_LINES[:7])
    lines.append(REQUIRED_NOTE_LINES[3])
    lines.append(EXPECTED_DYNAMIC_NOTE_LINES[7])
    lines.extend(
        (
            "- keep the workflow-viability lane scoped to the shipped current Phase 1 reminder packet instead of reviving the older installer-backed or closure-side validator family.",
            "- keep the bench checker self-test-only in bootstrap until fresh current-`master` evidence restores the broader live bench packet; a live `python3 scripts/zigux/check-phase1-bench.py` workflow step is still a workflow-viability regression here.",
            "- preserve the newer current-`master` Phase 2 neighbor packet ahead of the lane-local insertion, including the restored kconfig bridge pair, the confdata unit test, the pinned Zig archive probe, the toolchain pin-scope pair, the required-make-routes pair, the shared reminder pair, and the Phase 2 validator.",
            "- preserve the current post-Phase-1 bootstrap tail too: the workflow-viability pair must stay ahead of the current Phase 3 interop packet while leaving the current Phase 3 shared tests-root packet, the Phase 1 shared smoke, and the current Phase 4, Phase 7, Phase 10, Phase 11, Phase 12, Phase 8, and docs-root sanity steps intact.",
            "- if this lane reopens again, refresh the same current workflow packet first instead of widening back into older missing Phase 1 closure routes or unrelated Phase 2 reminder drift.",
        )
    )
    lines.append("")
    return "\n".join(lines)


def build_workflow_text() -> str:
    lines = [
        "name: zigux-bootstrap",
        "",
        "jobs:",
        "  bootstrap:",
        "    runs-on: ubuntu-latest",
        "    steps:",
    ]
    for step_name, run_command in TOOLCHAIN_STEPS + PHASE2_STEPS + PHASE1_STEPS + POST_PHASE1_STEPS:
        lines.append(f"      - name: {step_name}")
        if run_command == "__DOCS_SANITY__":
            lines.extend(
                (
                    "        run: |",
                    "          python3 - <<'PY2'",
                    "          print('shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`')",
                    "          PY2",
                )
            )
        else:
            lines.append(f"        run: {run_command}")
        lines.append("")
    return "\n".join(lines)


def build_sample_repo(root: Path) -> None:
    write_file(root, WORKFLOW_REL, build_workflow_text())
    write_file(root, NOTE_REL, build_note_text())
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
        (root / "scripts/zigux/validate-phase2.py").unlink()
        if "missing_file:scripts/zigux/validate-phase2.py" not in collect_failures(root):
            print("self-test:missing_phase2_validator_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        (root / "scripts/zigux/run-phase3-checks.py").unlink()
        if "missing_file:scripts/zigux/run-phase3-checks.py" not in collect_failures(root):
            print("self-test:missing_phase3_runner_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text(
            rewrite_once(
                workflow_path.read_text(encoding="utf-8"),
                "      - name: Validate current Phase 2 tool packet\n",
            ),
            encoding="utf-8",
        )
        if "workflow_step:Validate current Phase 2 tool packet:expected=1:actual=0" not in collect_failures(root):
            print("self-test:missing_phase2_validator_step_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path.write_text(
            rewrite_once(
                workflow_path.read_text(encoding="utf-8"),
                "      - name: Self-test current Phase 3 interop packet\n",
            ),
            encoding="utf-8",
        )
        if "workflow_step:Self-test current Phase 3 interop packet:expected=1:actual=0" not in collect_failures(root):
            print("self-test:missing_phase3_selftest_step_case_failed")
            return 1
        case_count += 1

        build_sampleRepo(root)
        workflow_path.write_text(
            rewrite_once(
                workflow_path.read_text(encoding="utf-8"),
                "      - name: Self-test current Phase 1 workflow viability checker\n"
                "        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test\n"
                "\n"
                "      - name: Check current Phase 1 workflow viability\n"
                "        run: python3 scripts/zigux/check-phase1-workflow-viability.py\n"
                "\n",
                "      - name: Self-test current Phase 3 interop packet\n"
                "        run: python3 scripts/zigux/validate_phase3_selftest.py\n"
                "\n"
                "      - name: Self-test current Phase 1 workflow viability checker\n"
                "        run: python3 scripts/zigux/check-phase1-workflow-viability.py --self-test\n"
                "\n"
                "      - name: Check current Phase 1 workflow viability\n"
                "        run: python3 scripts/zigux/check-phase1-workflow-viability.py\n"
                "\n",
            ),
            encoding="utf-8",
        )
        if "workflow_insertion_point:unexpected" not in collect_failures(root):
            print("self-test:phase3_before_viability_case_failed")
            return 1
        case_count += 1

        build_sample_repo(root)
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8")
            + "      - name: Forbidden bench live route\n        run: python3 scripts/zigux/check-phase1-bench.py\n",
            encoding="utf-8",
        )
        if "workflow_forbidden:phase1_live_bench:unexpected_present" not in collect_failures(root):
            print("self-test:forbidden_live_bench_case_failed")
            return 1
        case_count += 1

        build_sampleRepo(root)
        note_path = root / NOTE_REL
        note_path.write_text(
            rewrite_once(note_path.read_text(encoding="utf-8"), INSERTION_LINE + "\n"),
            encoding="utf-8",
        )
        if "note:expected=1:actual=0" not in ":".join(collect_failures(root)):
            print("self-test:missing_insertion_note_case_failed")
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
