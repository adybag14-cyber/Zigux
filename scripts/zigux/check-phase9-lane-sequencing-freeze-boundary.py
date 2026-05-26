#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
STUDY_ONLY_ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
MAKEFILE_PATH = "zigux/Makefile"

EXPECTED_STUDY_ONLY_ANCHORS = [
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
]

FREEZE_MAP_REQUIRED_MARKERS = [
    "# Zigux Freeze Map",
    "## Study / Boundary Only",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "shared Phase 9 runtime-pilot freeze-boundary packet must keep",
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`",
    "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`",
    "`scripts/zigux/check-phase9-freeze-map-study-boundaries.py`",
]

STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS = [
    "# Phase 15 Study-Only Anchor Accounting",
    "PHASE15_STATUS=study_only_accounting_slice_landed",
    "current-master-readback-2026-05-25",
    "boundary-study target first, not a rewrite target",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    "any future status-bucket change for either anchor must update the freeze map",
]

LANE_SEQUENCING_REQUIRED_MARKERS = [
    "# Phase 9 Runtime Pilot Lane Sequencing",
    "Trusted mixed rereads on 2026-05-25 confirm four distinct current-master Phase 9 postures.",
    "the returned shared runtime-loader allocator/init-flow and command/environment boundary packet stay neighboring shared-owner evidence",
    "the bitmap side keeps a broader direct packet on trusted rereads",
    "the kretprobe side now keeps a returned family-local pilot packet on trusted rereads",
    "keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "Treat stale shared-owner undercount or overclaim as the active blocker before reopening checker-local or runtime-behavior work.",
    "do not treat `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-pilot expansion evidence",
]

CURRENT_PHASE9_MAKE_ROUTES = [
    "phase9-runtime-atomic64-test",
    "phase9-runtime-bitmap-test",
    "phase9-runtime-loader-shared-test",
    "phase9-runtime-loader-command-env-boundary-guard-test",
    "phase9-runtime-trace-events-test",
    "phase9-runtime-kretprobe-test",
    "phase9-first-loadable-runtime-module-parity-test",
    "phase9-test",
]

FORBIDDEN_PHASE9_MAKE_ROUTES = [
    "phase9",
    "phase9-validate",
    "phase9-runtime-trace-events-sample-tests",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / FREEZE_MAP_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def extract_section_lines(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    captured: list[str] = []
    in_section = False
    for line in lines:
        if line.strip() == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            captured.append(line)
    return captured


def extract_freeze_map_study_only_anchors(text: str) -> list[str]:
    anchors: list[str] = []
    for line in extract_section_lines(text, "## Study / Boundary Only"):
        stripped = line.strip()
        if stripped.startswith("- `") and stripped.endswith("`"):
            anchors.append(stripped[3:-1])
    return anchors


def extract_study_only_accounting_anchors(text: str) -> list[str]:
    anchors: list[str] = []
    for line in extract_section_lines(text, "## Study-Only Anchor Inventory"):
        stripped = line.strip()
        if stripped.startswith("### `") and stripped.endswith("`"):
            anchors.append(stripped[5:-1])
    return anchors


def find_makefile_phase9_routes(text: str) -> list[str]:
    routes: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(".PHONY:"):
            continue
        if stripped.startswith("phase9") and ":" in stripped:
            routes.append(stripped.split(":", 1)[0])
    return routes


def remove_makefile_route_definition(content: str, route: str) -> str:
    lines = content.splitlines()
    kept: list[str] = []
    skipping = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{route}:"):
            skipping = True
            continue
        if skipping:
            if line.startswith("\t"):
                continue
            skipping = False
        kept.append(line)
    return "\n".join(kept) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = [
        FREEZE_MAP_PATH,
        STUDY_ONLY_ACCOUNTING_PATH,
        LANE_SEQUENCING_PATH,
        MAKEFILE_PATH,
    ]
    for rel_path in required_paths:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    freeze_map = read_text(root, FREEZE_MAP_PATH)
    for marker in FREEZE_MAP_REQUIRED_MARKERS:
        if marker not in freeze_map:
            failures.append(f"missing_marker:{FREEZE_MAP_PATH}:{marker}")
    if extract_freeze_map_study_only_anchors(freeze_map) != EXPECTED_STUDY_ONLY_ANCHORS:
        failures.append(
            "study_only_anchor_mismatch:"
            f"{FREEZE_MAP_PATH}:expected={EXPECTED_STUDY_ONLY_ANCHORS}:"
            f"actual={extract_freeze_map_study_only_anchors(freeze_map)}"
        )

    accounting = read_text(root, STUDY_ONLY_ACCOUNTING_PATH)
    for marker in STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS:
        if marker not in accounting:
            failures.append(f"missing_marker:{STUDY_ONLY_ACCOUNTING_PATH}:{marker}")
    if extract_study_only_accounting_anchors(accounting) != EXPECTED_STUDY_ONLY_ANCHORS:
        failures.append(
            "study_only_anchor_mismatch:"
            f"{STUDY_ONLY_ACCOUNTING_PATH}:expected={EXPECTED_STUDY_ONLY_ANCHORS}:"
            f"actual={extract_study_only_accounting_anchors(accounting)}"
        )

    sequencing = read_text(root, LANE_SEQUENCING_PATH)
    for marker in LANE_SEQUENCING_REQUIRED_MARKERS:
        if marker not in sequencing:
            failures.append(f"missing_marker:{LANE_SEQUENCING_PATH}:{marker}")

    makefile = read_text(root, MAKEFILE_PATH)
    routes = find_makefile_phase9_routes(makefile)
    for route in CURRENT_PHASE9_MAKE_ROUTES:
        if route not in routes:
            failures.append(f"missing_phase9_route:{route}")
    for route in FORBIDDEN_PHASE9_MAKE_ROUTES:
        if route in routes:
            failures.append(f"forbidden_phase9_route:{route}")

    return failures


def create_sample_root(root: Path) -> None:
    write_text(
        root / FREEZE_MAP_PATH,
        """# Zigux Freeze Map

## Freeze In C Initially
- `kernel/sched/core.c`
- `mm/page_alloc.c`

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Governance For Freeze-Map Changes
- shared Phase 9 runtime-pilot freeze-boundary packet must keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, and `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` explicit together
""",
    )
    write_text(
        root / STUDY_ONLY_ACCOUNTING_PATH,
        """# Phase 15 Study-Only Anchor Accounting

- `PHASE15_STATUS=study_only_accounting_slice_landed`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-25`

## Roadmap Basis
- `kernel/workqueue.c` remains a boundary-study target first, not a rewrite target
- `kernel/trace/ring_buffer.c` remains a boundary-study target first, not a rewrite target

## Study-Only Anchor Inventory

### `kernel/workqueue.c`
- posture: `study_only`

### `kernel/trace/ring_buffer.c`
- posture: `study_only`

## Accounting Rules
- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
- any future status-bucket change for either anchor must update the freeze map
""",
    )
    write_text(
        root / LANE_SEQUENCING_PATH,
        """# Phase 9 Runtime Pilot Lane Sequencing

Trusted mixed rereads on 2026-05-25 confirm four distinct current-master Phase 9 postures.

- the returned shared runtime-loader allocator/init-flow and command/environment boundary packet stay neighboring shared-owner evidence
- the bitmap side keeps a broader direct packet on trusted rereads
- the kretprobe side now keeps a returned family-local pilot packet on trusted rereads
- keep the freeze-map study-only anchors explicit through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- Treat stale shared-owner undercount or overclaim as the active blocker before reopening checker-local or runtime-behavior work.
- do not treat `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-pilot expansion evidence
""",
    )
    write_text(
        root / MAKEFILE_PATH,
        """phase9-runtime-atomic64-test:
\t@true

phase9-runtime-bitmap-test:
\t@true

phase9-runtime-loader-shared-test:
\t@true

phase9-runtime-loader-command-env-boundary-guard-test:
\t@true

phase9-runtime-trace-events-test:
\t@true

phase9-runtime-kretprobe-test:
\t@true

phase9-first-loadable-runtime-module-parity-test:
\t@true

phase9-test: phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-loader-command-env-boundary-guard-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-first-loadable-runtime-module-parity-test
""",
    )


def run_self_test() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="phase9_lane_sequencing_freeze_boundary_"))
    try:
        create_sample_root(temp_dir)
        assert not validate(temp_dir)

        broken = temp_dir / "broken"
        shutil.copytree(temp_dir, broken)
        write_text(
            broken / LANE_SEQUENCING_PATH,
            read_text(broken, LANE_SEQUENCING_PATH).replace(
                "do not treat `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-pilot expansion evidence",
                "runtime-pilot expansion evidence removed",
            ),
        )
        assert any(
            failure.startswith(f"missing_marker:{LANE_SEQUENCING_PATH}:")
            for failure in validate(broken)
        )

        broken = temp_dir / "broken_freeze"
        shutil.copytree(temp_dir, broken)
        write_text(
            broken / FREEZE_MAP_PATH,
            read_text(broken, FREEZE_MAP_PATH).replace(
                "- `kernel/trace/ring_buffer.c`\n",
                "",
            ),
        )
        assert any("study_only_anchor_mismatch" in failure for failure in validate(broken))

        broken = temp_dir / "broken_accounting"
        shutil.copytree(temp_dir, broken)
        write_text(
            broken / STUDY_ONLY_ACCOUNTING_PATH,
            read_text(broken, STUDY_ONLY_ACCOUNTING_PATH).replace(
                "### `kernel/trace/ring_buffer.c`\n- posture: `study_only`\n",
                "",
            ),
        )
        assert any("study_only_anchor_mismatch" in failure for failure in validate(broken))

        broken = temp_dir / "broken_makefile"
        shutil.copytree(temp_dir, broken)
        write_text(
            broken / MAKEFILE_PATH,
            remove_makefile_route_definition(
                read_text(broken, MAKEFILE_PATH),
                "phase9-runtime-loader-command-env-boundary-guard-test",
            ),
        )
        assert "missing_phase9_route:phase9-runtime-loader-command-env-boundary-guard-test" in validate(
            broken
        )

        broken = temp_dir / "broken_forbidden"
        shutil.copytree(temp_dir, broken)
        write_text(
            broken / MAKEFILE_PATH,
            read_text(broken, MAKEFILE_PATH) + "\nphase9:\n\t@true\n",
        )
        assert "forbidden_phase9_route:phase9" in validate(broken)

        print("PHASE9_LANE_SEQUENCING_FREEZE_BOUNDARY_SELF_TEST=pass")
        print("PHASE9_LANE_SEQUENCING_FREEZE_BOUNDARY_SELF_TEST_CASES=5")
    finally:
        shutil.rmtree(temp_dir)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 9 lane-sequencing freeze-boundary packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    failures = validate(args.root.resolve())
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE9_LANE_SEQUENCING_FREEZE_BOUNDARY=pass")
    print(f"PHASE9_LANE_SEQUENCING_FREEZE_BOUNDARY_ROOT={args.root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
