#!/usr/bin/env python3
"""Check that the Phase 14 scripts-root reminder stays aligned with current repo reality."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

README_REL = "scripts/zigux/README.md"
SHARED_GAP_REL = "Documentation/zigux/phase14-shared-smoke-current-master-gap.md"
SURVEY_REL = "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
ATTACHED_TOOLCHAIN_REL = "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
TESTS_README_REL = "zigux/tests/README.md"
MANIFEST_REL = "zigux/tests/phase14_end_to_end_smoke_manifest.json"
MAKEFILE_REL = "zigux/Makefile"
ROUTE_CHECKER_REL = "scripts/zigux/check-phase14-shared-smoke-route.py"
TESTS_CHECKER_REL = "scripts/zigux/check-phase14-tests-readme-smoke-summary.py"
VALIDATOR_REL = "scripts/zigux/validate-phase14.py"
ROLLBACK_CHECKER_REL = "scripts/zigux/check-phase14-rollback-threshold-sequencing.py"
SKBUFF_STAY_REL = "scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py"
SKBUFF_COMPILE_REL = "scripts/zigux/check-phase14-skbuff-compile-route.py"
RING_BUFFER_COMPILE_REL = "scripts/zigux/check-phase14-ring-buffer-compile-route.py"
RCU_COMPILE_REL = "scripts/zigux/check-phase14-rcu-compile-route.py"
RCU_ROLLBACK_REL = "scripts/zigux/check-phase14-rcu-rollback-guardrail.py"
RELEASE_BOUNDARY_REL = "scripts/zigux/check-phase14-release-boundary-exact-counts.py"

PHASE14_START = "## Phase 14"
PHASE15_START = "## Phase 15"

REQUIRED_FILES = (
    README_REL,
    SHARED_GAP_REL,
    SURVEY_REL,
    ATTACHED_TOOLCHAIN_REL,
    REVIEW_CHECKLIST_REL,
    TESTS_README_REL,
    MANIFEST_REL,
    MAKEFILE_REL,
    ROUTE_CHECKER_REL,
    TESTS_CHECKER_REL,
    VALIDATOR_REL,
    ROLLBACK_CHECKER_REL,
    SKBUFF_STAY_REL,
    SKBUFF_COMPILE_REL,
    RING_BUFFER_COMPILE_REL,
    RCU_COMPILE_REL,
    RCU_ROLLBACK_REL,
    RELEASE_BOUNDARY_REL,
)

README_MARKERS = (
    "Phase 14 flow - the current scripts-root shared smoke packet stays reviewable through the recovered study-only documentation packet, the directly readable route, tests-root, rollback-threshold, dedicated skbuff stay-in-C, skbuff compile-route, ring-buffer compile-route, and RCU compile-route plus rollback guards, the validator and release-boundary guards, the machine-readable shared-smoke manifest, and the returned `phase14-validate` split without promoting the missing `phase14-smoke`, `phase14-test`, or `phase14` wrappers into current proof",
    "`scripts/zigux/check-phase14-shared-smoke-route.py`, `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `scripts/zigux/validate-phase14.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py`, `scripts/zigux/check-phase14-skbuff-compile-route.py`, `scripts/zigux/check-phase14-ring-buffer-compile-route.py`, `scripts/zigux/check-phase14-rcu-compile-route.py`, `scripts/zigux/check-phase14-rcu-rollback-guardrail.py`, `scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, and `zigux/Makefile` keep the directly readable shared-smoke route proof, tests-root reminder proof, validator entrypoint, rollback-threshold sequencing contract, dedicated skbuff stay-in-C guard, dedicated skbuff compile-route guard, dedicated ring-buffer compile-route guard, dedicated RCU compile-route and rollback guards, release-boundary exact-count posture, and machine-readable shared smoke surface inventory explicit from the scripts root while the broader `phase14-smoke`, `phase14-test`, and `phase14` wrappers remain absent on current `master`",
    "`kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` keep the directly readable workqueue reviewability shard explicit from the scripts root without pretending that the broader executable layer or live workqueue execution has returned",
    "keep the directly readable dedicated skbuff stay-in-C, skbuff compile-route, and ring-buffer compile-route guards explicit from the scripts root too: `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py`, `scripts/zigux/check-phase14-skbuff-compile-route.py`, and `scripts/zigux/check-phase14-ring-buffer-compile-route.py` keep those review-only rollback and compile-trigger surfaces visible beside the shared smoke packet instead of leaving them implicit in neighboring notes",
    "keep the directly readable dedicated RCU compile-route and rollback guards explicit from the scripts root too: `scripts/zigux/check-phase14-rcu-compile-route.py`, `scripts/zigux/check-phase14-rcu-rollback-guardrail.py`, and `Documentation/zigux/phase14-rcu-tree-survey.md` keep the freeze-in-C compile-route and rollback posture visible without promoting the still-partial RCU executable layer into direct replay proof",
)

SHARED_GAP_MARKERS = (
    "`scripts/zigux/check-phase14-shared-smoke-route.py` is directly readable again through the current contents path",
    "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py` is directly readable again through the current contents path",
    "`scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` is directly readable again through the current contents path",
    "`scripts/zigux/check-phase14-skbuff-compile-route.py` is directly readable again through the current contents path",
    "`scripts/zigux/check-phase14-rcu-rollback-guardrail.py` is directly readable again through the current contents path",
    "`Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-rcu-tree-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` should stay aligned around the broadened study-only Phase 14 packet",
)

SURVEY_MARKERS = (
    "some shared reminder surfaces may still lag this current route split",
    "the directly readable dedicated skbuff stay-in-C guard:",
    "the directly readable dedicated skbuff compile-route guard:",
    "the directly readable dedicated ring-buffer compile-route guard:",
    "the directly readable dedicated RCU rollback guard:",
)

ATTACHED_TOOLCHAIN_MARKERS = (
    "the staged pinned bundle stays first, the local `.zig-toolchain/*/zig` probe stays second, and the `zig` on `PATH` fallback stays last",
    "manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides remain packet-local escape vocabulary rather than current default rerun guidance",
)

CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 14 smoke packet",
    "`scripts/zigux/validate-phase14.py` and `scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "`zigux/Makefile` framed as readable current evidence for the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes together with the returned `make -C zigux phase14-validate` gate while `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
)

TESTS_README_MARKERS = (
    "## Phase 14 shared smoke packet",
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "`Documentation/zigux/phase14-release-boundary-survey.md`",
    "`Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`",
    "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
)

MANIFEST_MARKERS = (
    '"scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py"',
    '"scripts/zigux/check-phase14-skbuff-compile-route.py"',
    '"scripts/zigux/check-phase14-ring-buffer-compile-route.py"',
    '"scripts/zigux/check-phase14-rcu-compile-route.py"',
    '"scripts/zigux/check-phase14-rcu-rollback-guardrail.py"',
    '"phase14_validate_runs_skbuff_compile_route_checker": true',
    '"phase14_validate_runs_rcu_compile_route_checker": true',
)

MAKEFILE_REQUIRED = (
    "phase14-validate:",
    "scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
    "scripts/zigux/validate-phase14.py --self-test",
)

MAKEFILE_FORBIDDEN = (
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate phase14-smoke phase14-test",
)


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def require_markers(text: str, markers: tuple[str, ...], label: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:missing:{marker}")


def require_absent(text: str, markers: tuple[str, ...], label: str, failures: list[str]) -> None:
    for marker in markers:
        if marker in text:
            failures.append(f"{label}:forbidden:{marker}")


def section(text: str, start: str, end: str, label: str) -> str:
    start_idx = text.find(start)
    if start_idx == -1:
        raise ValueError(f"{label}:missing_section_start:{start}")
    end_idx = text.find(end, start_idx)
    if end_idx == -1:
        raise ValueError(f"{label}:missing_section_end:{end}")
    return text[start_idx:end_idx]


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    readme = read_text(root, README_REL)
    try:
        phase14 = section(readme, PHASE14_START, PHASE15_START, "scripts_readme")
    except ValueError as exc:
        return [str(exc)]

    require_markers(phase14, README_MARKERS, "scripts_readme", failures)
    require_markers(read_text(root, SHARED_GAP_REL), SHARED_GAP_MARKERS, "shared_gap", failures)
    require_markers(read_text(root, SURVEY_REL), SURVEY_MARKERS, "survey", failures)
    require_markers(read_text(root, ATTACHED_TOOLCHAIN_REL), ATTACHED_TOOLCHAIN_MARKERS, "attached_toolchain", failures)
    require_markers(read_text(root, REVIEW_CHECKLIST_REL), CHECKLIST_MARKERS, "review_checklist", failures)
    require_markers(read_text(root, TESTS_README_REL), TESTS_README_MARKERS, "tests_readme", failures)
    require_markers(read_text(root, MANIFEST_REL), MANIFEST_MARKERS, "manifest", failures)

    makefile = read_text(root, MAKEFILE_REL)
    require_markers(makefile, MAKEFILE_REQUIRED, "makefile", failures)
    require_absent(makefile, MAKEFILE_FORBIDDEN, "makefile", failures)
    return failures


def seed_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(
        root / README_REL,
        "# scripts/zigux\n\n## Phase 14\n\n"
        + "\n".join(f"- {marker}" for marker in README_MARKERS)
        + "\n\n## Phase 15\n\n- next section\n",
    )
    write_text(root / SHARED_GAP_REL, "# Phase 14 Shared Smoke Current-Master Gap\n\n" + "\n".join(f"- {m}" for m in SHARED_GAP_MARKERS) + "\n")
    write_text(root / SURVEY_REL, "# Phase 14 End-to-End Smoke Survey\n\n" + "\n".join(f"- {m}" for m in SURVEY_MARKERS) + "\n")
    write_text(root / ATTACHED_TOOLCHAIN_REL, "# Phase 14 Attached Toolchain Guidance Gap\n\n" + "\n".join(f"- {m}" for m in ATTACHED_TOOLCHAIN_MARKERS) + "\n")
    write_text(root / REVIEW_CHECKLIST_REL, "# Zigux Review Checklist\n\n" + "\n".join(f"- {m}" for m in CHECKLIST_MARKERS) + "\n")
    write_text(root / TESTS_README_REL, "# zigux/tests\n\n" + "\n".join(f"- {m}" for m in TESTS_README_MARKERS) + "\n")
    write_text(
        root / MANIFEST_REL,
        json.dumps(
            {
                "shared_smoke_surfaces": [
                    "scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py",
                    "scripts/zigux/check-phase14-skbuff-compile-route.py",
                    "scripts/zigux/check-phase14-ring-buffer-compile-route.py",
                    "scripts/zigux/check-phase14-rcu-compile-route.py",
                    "scripts/zigux/check-phase14-rcu-rollback-guardrail.py",
                ],
                "survey_summary": {
                    "phase14_validate_runs_skbuff_compile_route_checker": True,
                    "phase14_validate_runs_rcu_compile_route_checker": True,
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / MAKEFILE_REL,
        "phase3-validate:\n\t@true\n"
        "phase14-validate:\n"
        "\tpython3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test\n"
        "\tpython3 scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test\n"
        "\tpython3 scripts/zigux/validate-phase14.py --self-test\n",
    )
    for rel in (
        ROUTE_CHECKER_REL,
        TESTS_CHECKER_REL,
        VALIDATOR_REL,
        ROLLBACK_CHECKER_REL,
        SKBUFF_STAY_REL,
        SKBUFF_COMPILE_REL,
        RING_BUFFER_COMPILE_REL,
        RCU_COMPILE_REL,
        RCU_ROLLBACK_REL,
        RELEASE_BOUNDARY_REL,
    ):
        write_text(root / rel, "# checker placeholder\n")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14_scripts_readme_alignment_"))
    try:
        seed_root(base)
        failures = validate(base)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        cases = 1

        missing_section = base / "missing_section"
        seed_root(missing_section)
        write_text(missing_section / README_REL, "# scripts/zigux\n")
        failures = validate(missing_section)
        if failures != ["scripts_readme:missing_section_start:## Phase 14"]:
            raise AssertionError(f"unexpected missing-section failures: {failures}")
        cases += 1

        missing_skbuff_marker = base / "missing_skbuff_marker"
        seed_root(missing_skbuff_marker)
        write_text(
            missing_skbuff_marker / README_REL,
            read_text(missing_skbuff_marker, README_REL).replace(README_MARKERS[3], "", 1),
        )
        failures = validate(missing_skbuff_marker)
        if not any("scripts_readme:missing:" in failure and "skbuff stay-in-C" in failure for failure in failures):
            raise AssertionError(f"expected README marker failure, got: {failures}")
        cases += 1

        stale_gap = base / "stale_gap"
        seed_root(stale_gap)
        write_text(
            stale_gap / SHARED_GAP_REL,
            read_text(stale_gap, SHARED_GAP_REL).replace(SHARED_GAP_MARKERS[3], "", 1),
        )
        failures = validate(stale_gap)
        if not any(failure == f"shared_gap:missing:{SHARED_GAP_MARKERS[3]}" for failure in failures):
            raise AssertionError(f"expected shared gap failure, got: {failures}")
        cases += 1

        missing_manifest = base / "missing_manifest"
        seed_root(missing_manifest)
        manifest = json.loads(read_text(missing_manifest, MANIFEST_REL))
        manifest["survey_summary"]["phase14_validate_runs_skbuff_compile_route_checker"] = False
        write_text(missing_manifest / MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        failures = validate(missing_manifest)
        if not any(failure == 'manifest:missing:"phase14_validate_runs_skbuff_compile_route_checker": true' for failure in failures):
            raise AssertionError(f"expected manifest failure, got: {failures}")
        cases += 1

        forbidden_make_target = base / "forbidden_make_target"
        seed_root(forbidden_make_target)
        write_text(
            forbidden_make_target / MAKEFILE_REL,
            read_text(forbidden_make_target, MAKEFILE_REL) + "phase14-smoke:\n\t@true\n",
        )
        failures = validate(forbidden_make_target)
        if not any(failure == "makefile:forbidden:phase14-smoke:" for failure in failures):
            raise AssertionError(f"expected forbidden make target failure, got: {failures}")
        cases += 1

        missing_attached_toolchain = base / "missing_attached_toolchain"
        seed_root(missing_attached_toolchain)
        write_text(
            missing_attached_toolchain / ATTACHED_TOOLCHAIN_REL,
            read_text(missing_attached_toolchain, ATTACHED_TOOLCHAIN_REL).replace(ATTACHED_TOOLCHAIN_MARKERS[1], "", 1),
        )
        failures = validate(missing_attached_toolchain)
        if not any(failure == f"attached_toolchain:missing:{ATTACHED_TOOLCHAIN_MARKERS[1]}" for failure in failures):
            raise AssertionError(f"expected attached-toolchain failure, got: {failures}")
        cases += 1

        print("PHASE14_SCRIPTS_README_ALIGNMENT_SELF_TEST=pass")
        print(f"PHASE14_SCRIPTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 14 scripts-root reminder stays aligned with current repo reality."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        seed_root(args.write_sample_root)
        print(f"PHASE14_SCRIPTS_README_ALIGNMENT_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE14_SCRIPTS_README_ALIGNMENT=fail")
        print("PHASE14_SCRIPTS_README_ALIGNMENT_ISSUES_START")
        for failure in failures:
            print(failure)
        print("PHASE14_SCRIPTS_README_ALIGNMENT_ISSUES_END")
        return 1

    print("PHASE14_SCRIPTS_README_ALIGNMENT=pass")
    print(f"PHASE14_SCRIPTS_README_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE14_SCRIPTS_README_ALIGNMENT_REQUIRED_MARKER_COUNT="
        f"{len(README_MARKERS) + len(SHARED_GAP_MARKERS) + len(SURVEY_MARKERS) + len(ATTACHED_TOOLCHAIN_MARKERS) + len(CHECKLIST_MARKERS) + len(TESTS_README_MARKERS) + len(MANIFEST_MARKERS) + len(MAKEFILE_REQUIRED)}"
    )
    print(f"PHASE14_SCRIPTS_README_ALIGNMENT_FORBIDDEN_MARKER_COUNT={len(MAKEFILE_FORBIDDEN)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
