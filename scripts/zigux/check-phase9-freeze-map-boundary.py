#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
DOCS_README_PATH = "Documentation/zigux/README.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"

LANE_FREEZE_MAP_MARKER = "keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` framed as freeze-map study-only anchors"
LANE_PHASE15_MARKER = "`Documentation/zigux/phase15-study-only-anchor-accounting.md`"
DOCS_FREEZE_MAP_MARKER = "`kernel/workqueue.c` plus `kernel/trace/ring_buffer.c` framed only through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` instead of as runtime-pilot bridge-readiness cues"
SCRIPTS_FREEZE_MAP_MARKER = "keep the freeze-map boundary explicit too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues"

FILE_MARKERS = {
    LANE_SEQUENCING_PATH: [LANE_FREEZE_MAP_MARKER, LANE_PHASE15_MARKER],
    DOCS_README_PATH: [DOCS_FREEZE_MAP_MARKER],
    SCRIPTS_README_PATH: [SCRIPTS_FREEZE_MAP_MARKER],
}


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / LANE_SEQUENCING_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path, markers in FILE_MARKERS.items():
        target = root / rel_path
        if not target.exists():
            failures.append(f"missing_file:{rel_path}")
            continue
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def seed_fixture_tree(base: Path) -> None:
    write_text(
        base / LANE_SEQUENCING_PATH,
        f"# fixture\n\n{LANE_FREEZE_MAP_MARKER}\n{LANE_PHASE15_MARKER}\n",
    )
    write_text(base / DOCS_README_PATH, f"# fixture\n\n{DOCS_FREEZE_MAP_MARKER}\n")
    write_text(base / SCRIPTS_README_PATH, f"# fixture\n\n{SCRIPTS_FREEZE_MAP_MARKER}\n")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-freeze-map-boundary-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in FILE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                write_text(base / rel_path, "# missing marker fixture\n")
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in FILE_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_FREEZE_MAP_BOUNDARY_CHECK=pass")
    print(f"PHASE9_FREEZE_MAP_BOUNDARY_FILE_COUNT={len(FILE_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 9 reminder packet keeps the freeze-map study-only boundary explicit across the lane sequencing note, docs-root summary, and scripts-root reminder."
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_FREEZE_MAP_BOUNDARY_ERROR={failure}")
        return 1

    print("PHASE9_FREEZE_MAP_BOUNDARY_CHECK=pass")
    print(f"PHASE9_FREEZE_MAP_BOUNDARY_FILE_COUNT={len(FILE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
