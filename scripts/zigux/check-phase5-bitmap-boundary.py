#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

LANE_NOTE_PATH = Path("Documentation/zigux/phase5-sample-lane-sequencing.md")
SAMPLE_ROOT_PATH = Path("samples/zigux/README.md")
GUIDE_PATH = Path("Documentation/zigux/phase5-sample-review-guide.md")
SCRIPTS_ROOT_PATH = Path("scripts/zigux/README.md")
TESTS_ROOT_PATH = Path("zigux/tests/README.md")

MARKERS = {
    LANE_NOTE_PATH: (
        "Keep the returned runtime bitmap reminder packet separate too: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` are current direct sample-root evidence for the separate Phase 9 runtime bitmap family, not extra Phase 5 sample proof.",
        "keep the returned runtime bitmap reminder packet `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` framed as separate Phase 9 runtime evidence rather than extra Phase 5 sample proof",
        "there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`",
    ),
    SAMPLE_ROOT_PATH: (
        "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.",
        "Fresh trusted mixed reread on 2026-05-23 also confirms a broader runtime bitmap sample-side packet on current `master`: direct authenticated contents reads now materialize `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_module.zig`, and `zigux/tests/runtime_bitmap_diff.zig`, while `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and the shared `zigux/tests/phase9_build.zig` bundle keep the same sample-side reminder packet explicit.",
    ),
    GUIDE_PATH: (
        "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
        "treating Phase 9 runtime samples as extra Phase 5 evidence",
    ),
    SCRIPTS_ROOT_PATH: (
        "keep the no-extra-sample boundary explicit from the scripts root too: do not treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence, and do not treat standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 scripts-root packet.",
    ),
    TESTS_ROOT_PATH: (
        "Keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 tests-root packet.",
    ),
}

FORBIDDEN = {
    LANE_NOTE_PATH: (
        "Keep the returned runtime bitmap reminder packet separate too: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` are current direct sample-root evidence for the separate Phase 9 runtime bitmap family, not extra Phase 5 sample proof.",
    ),
    SAMPLE_ROOT_PATH: (
        "Fresh trusted mixed reread on 2026-05-23 also confirms a broader runtime bitmap sample-side packet on current `master`: direct authenticated contents reads now materialize `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_module.zig`, and `zigux/tests/runtime_bitmap_diff.zig`, while `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and the shared `zigux/tests/phase9_build.zig` bundle keep the same sample-side reminder packet explicit.",
    ),
}


def read_text(root: Path, path: Path) -> str:
    return (root / path).read_text(encoding="utf-8")


def write_text(root: Path, path: Path, text: str) -> None:
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(text, encoding="utf-8")


def placeholder(path: Path) -> str:
    lines = [f"# {path.name}"]
    lines.extend(MARKERS[path])
    return "\n\n".join(lines) + "\n"


def seed(root: Path) -> None:
    for path in MARKERS:
        write_text(root, path, placeholder(path))


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for path, markers in MARKERS.items():
        text = read_text(root, path)
        for marker in markers:
            if marker not in text:
                failures.append(f"{path}:missing_text:{marker}")
    for path, markers in FORBIDDEN.items():
        text = read_text(root, path)
        for marker in markers:
            if marker in text:
                failures.append(f"{path}:forbidden_text:{marker}")
    return failures


def expect_exact(label: str, failures: list[str], expected: list[str]) -> None:
    if failures != expected:
        raise AssertionError(f"{label}: expected {expected}, got {failures}")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 7
    with tempfile.TemporaryDirectory(prefix="phase5_bitmap_boundary_") as tmpdir:
        root = Path(tmpdir)
        seed(root)
        expect_exact("baseline", collect_failures(root), [])
        checks_run += 1

        mutated = root / "missing_lane_marker"
        seed(mutated)
        write_text(mutated, LANE_NOTE_PATH, placeholder(LANE_NOTE_PATH).replace(MARKERS[LANE_NOTE_PATH][0], ""))
        expect_exact(
            "missing lane marker",
            collect_failures(mutated),
            [f"{LANE_NOTE_PATH}:missing_text:{MARKERS[LANE_NOTE_PATH][0]}"],
        )
        checks_run += 1

        mutated = root / "missing_sample_root_marker"
        seed(mutated)
        write_text(mutated, SAMPLE_ROOT_PATH, placeholder(SAMPLE_ROOT_PATH).replace(MARKERS[SAMPLE_ROOT_PATH][1], ""))
        expect_exact(
            "missing sample root marker",
            collect_failures(mutated),
            [f"{SAMPLE_ROOT_PATH}:missing_text:{MARKERS[SAMPLE_ROOT_PATH][1]}"],
        )
        checks_run += 1

        mutated = root / "missing_guide_marker"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, placeholder(GUIDE_PATH).replace(MARKERS[GUIDE_PATH][0], ""))
        expect_exact(
            "missing guide marker",
            collect_failures(mutated),
            [f"{GUIDE_PATH}:missing_text:{MARKERS[GUIDE_PATH][0]}"],
        )
        checks_run += 1

        mutated = root / "missing_scripts_root_marker"
        seed(mutated)
        write_text(mutated, SCRIPTS_ROOT_PATH, placeholder(SCRIPTS_ROOT_PATH).replace(MARKERS[SCRIPTS_ROOT_PATH][0], ""))
        expect_exact(
            "missing scripts root marker",
            collect_failures(mutated),
            [f"{SCRIPTS_ROOT_PATH}:missing_text:{MARKERS[SCRIPTS_ROOT_PATH][0]}"],
        )
        checks_run += 1

        mutated = root / "forbidden_lane_variant"
        seed(mutated)
        write_text(mutated, LANE_NOTE_PATH, placeholder(LANE_NOTE_PATH) + FORBIDDEN[LANE_NOTE_PATH][0] + "\n")
        expect_exact(
            "forbidden lane variant",
            collect_failures(mutated),
            [f"{LANE_NOTE_PATH}:forbidden_text:{FORBIDDEN[LANE_NOTE_PATH][0]}"],
        )
        checks_run += 1

        mutated = root / "forbidden_sample_root_variant"
        seed(mutated)
        write_text(mutated, SAMPLE_ROOT_PATH, placeholder(SAMPLE_ROOT_PATH) + FORBIDDEN[SAMPLE_ROOT_PATH][0] + "\n")
        expect_exact(
            "forbidden sample root variant",
            collect_failures(mutated),
            [f"{SAMPLE_ROOT_PATH}:forbidden_text:{FORBIDDEN[SAMPLE_ROOT_PATH][0]}"],
        )
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} self-test cases, ran {checks_run}")
    print("PHASE5_BITMAP_BOUNDARY_SELF_TEST=pass")
    print(f"PHASE5_BITMAP_BOUNDARY_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT.parent.parent, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(args.root)
    if failures:
        print("PHASE5_BITMAP_BOUNDARY=fail")
        for failure in failures:
            print(failure)
        return 1
    print("PHASE5_BITMAP_BOUNDARY=pass")
    print(f"PHASE5_BITMAP_BOUNDARY_FILE_COUNT={len(MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
