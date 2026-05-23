#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
SURVEY_NOTE_PATH = "Documentation/zigux/phase9-runtime-bitmap-survey.md"
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-bitmap-module-slice.md"
MANIFEST_PATH = "zigux/tests/runtime_bitmap_manifest.json"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"


REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "keep the partial runtime bitmap reminder packet distinct from that returned loader shard too:",
        "`Documentation/zigux/phase9-runtime-bitmap-survey.md`",
        "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`",
        "`zigux/tests/runtime_bitmap_manifest.json`",
        "`zigux/tests/runtime_bitmap_module.zig`",
        "`zigux/tests/runtime_bitmap_diff.zig`",
        "`samples/zigux/runtime_bitmap_top_bit_contract.zig`",
    ],
    REVIEW_CHECKLIST_PATH: [
        "the partial separate runtime bitmap reminder packet stays explicit",
        "`Documentation/zigux/phase9-runtime-bitmap-survey.md`",
        "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`",
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
        "`zigux/tests/runtime_bitmap_manifest.json`",
        "`zigux/tests/runtime_bitmap_module.zig`",
        "`zigux/tests/runtime_bitmap_diff.zig`",
        "there is no standalone `samples/zigux/*bitmap*` reference sample",
    ],
    SCRIPTS_README_PATH: [
        "keep the partial runtime bitmap reminder distinct too:",
        "`Documentation/zigux/phase9-runtime-bitmap-survey.md`",
        "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`",
        "`zigux/tests/runtime_bitmap_manifest.json`",
        "`zigux/tests/runtime_bitmap_module.zig`",
        "`zigux/tests/runtime_bitmap_diff.zig`",
        "`phase9-runtime-bitmap-test` plus `phase9-test` routes",
    ],
    SAMPLES_README_PATH: [
        "Fresh trusted mixed reread on 2026-05-23 also confirms a broader runtime bitmap sample-side packet on current `master`",
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
        "`zigux/tests/runtime_bitmap_manifest.json`",
        "`zigux/tests/runtime_bitmap_module.zig`",
        "`zigux/tests/runtime_bitmap_diff.zig`",
        "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage selftest, exit, mutation, and source-lifecycle guard companion proof for the same runtime bitmap starter.",
        "Keep `zigux/tests/runtime_bitmap_manifest.json` explicit as the manifest-backed ownership packet for the same runtime bitmap reminder family.",
    ],
    TESTS_README_PATH: [
        "the separate runtime bitmap reminder packet stays explicit",
        "`Documentation/zigux/phase9-runtime-bitmap-survey.md`",
        "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`",
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
        "`zigux/tests/runtime_bitmap_manifest.json`",
        "`zigux/tests/runtime_bitmap_module.zig`",
        "`zigux/tests/runtime_bitmap_diff.zig`",
        "Keep that broader bitmap-side visibility from being used to imply that the broader shared runtime-loader packet returned or that blocked publication boundaries are complete.",
    ],
    SURVEY_NOTE_PATH: [
        "`PHASE9_LANE_KEY=P9-L08`",
        "manifest-backed ownership packet",
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
        "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage sample-root guard companion",
        "current runtime bitmap reminder packet is still `partial_packet_with_diff_but_without_broader_runtime_loader_parity`",
        "the blocked deliverable remains `loadable Phase 9 runtime bitmap pilot module parity`",
    ],
    MODULE_SLICE_PATH: [
        "`PHASE9_LANE_KEY=P9-L08`",
        "`zigux/tests/runtime_bitmap_manifest.json`",
        "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`",
        "The current visible packet includes the direct bitmap sample, direct cold-stage guard companion, direct loader companion, direct module proof, direct diff proof, focused top-bit companion, manifest-backed ownership packet, survey note, module-slice note, survey gate, and bounded build bundle.",
        "blocked follow-through remains `broader shared runtime-loader family completion plus loadable runtime bitmap module parity`",
    ],
    MANIFEST_PATH: [
        '"lane_key": "P9-L08"',
        '"scope": "partial runtime bitmap reminder packet, direct sample proof, direct loader proof, direct module proof, direct diff proof, manifest-backed ownership packet, top-bit companion proof, and no broader shared runtime-loader parity claim"',
        '"cold_stage_guard_path": "samples/zigux/runtime_bitmap_cold_stage_guard.zig"',
        '"module_path": "zigux/tests/runtime_bitmap_module.zig"',
        '"diff_path": "zigux/tests/runtime_bitmap_diff.zig"',
        '"survey_note_path": "Documentation/zigux/phase9-runtime-bitmap-survey.md"',
        '"module_slice_note_path": "Documentation/zigux/phase9-runtime-bitmap-module-slice.md"',
        '"validation_entrypoint": "phase9-runtime-bitmap-tests"',
        '"Keep the cold-stage selftest, exit, mutation, and source-lifecycle guard companion explicit when the manifest summarizes the sample-root runtime bitmap packet."',
        '"loadable runtime bitmap module parity"',
    ],
    PHASE9_BUILD_PATH: [
        '.name = "phase9-runtime-bitmap-sample-tests"',
        '.name = "phase9-runtime-bitmap-loader-tests"',
        '.name = "phase9-runtime-bitmap-survey-tests"',
        '.name = "phase9-runtime-bitmap-module-tests"',
        '.name = "phase9-runtime-bitmap-diff-tests"',
        '.name = "phase9-runtime-bitmap-top-bit-tests"',
        '"phase9-runtime-bitmap-tests"',
    ],
}

EXACT_ONCE_MARKERS = {
    SAMPLES_README_PATH: [
        "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage selftest, exit, mutation, and source-lifecycle guard companion proof for the same runtime bitmap starter.",
    ],
    SURVEY_NOTE_PATH: [
        "Keep `samples/zigux/runtime_bitmap_cold_stage_guard.zig` explicit as the returned cold-stage sample-root guard companion; it is visible on the trusted path but still sits outside the shared `zigux/tests/phase9_build.zig` bundle.",
    ],
}

FORBIDDEN_MARKERS = {
    DOCS_README_PATH: [
        "proof that the broader shared runtime-loader packet returned",
    ],
    SCRIPTS_README_PATH: [
        "full bitmap-family return",
    ],
    SAMPLES_README_PATH: [
        "fifth approved Phase 5 sample family",
    ],
}


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / DOCS_README_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_line_occurrences(content: str, marker: str) -> int:
    return sum(1 for line in content.splitlines() if line == marker)


def duplicate_marker_occurrence(content: str, marker: str) -> str:
    return content.replace(marker, f"{marker}\n{marker}", 1)


def break_marker(marker: str) -> str:
    if len(marker) == 1:
        return "_"
    replacement_tail = "_" if marker[-1] != "_" else "-"
    return marker[:-1] + replacement_tail


def tamper_marker_occurrences(content: str, marker: str) -> str:
    return content.replace(marker, break_marker(marker))


def build_fixture_text(rel_path: str) -> str:
    markers = list(REQUIRED_MARKERS[rel_path])
    for marker in EXACT_ONCE_MARKERS.get(rel_path, []):
        if marker not in markers:
            markers.append(marker)
    prefix = "# fixture\n\n" if rel_path.endswith(".md") else ""
    return prefix + "\n".join(markers) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_MARKERS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in EXACT_ONCE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            count = count_exact_line_occurrences(text, marker)
            if count != 1:
                failures.append(f"expected_exact_once:{rel_path}:{marker}:count={count}")

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker in text:
                failures.append(f"forbidden_marker:{rel_path}:{marker}")

    return failures


def seed_fixture_tree(base: Path) -> None:
    for rel_path in REQUIRED_MARKERS:
        write_text(base / rel_path, build_fixture_text(rel_path))


def write_sample_root(base: Path) -> None:
    if base.exists():
        shutil.rmtree(base)
    seed_fixture_tree(base)


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-runtime-bitmap-reminder-packet-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, tamper_marker_occurrences(current, marker))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path, markers in EXACT_ONCE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, duplicate_marker_occurrence(current, marker))
                expect_failure(base, f"expected_exact_once:{rel_path}:{marker}:count=2")

        for rel_path, markers in FORBIDDEN_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, current + f"\n{marker}\n")
                expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        for rel_path in REQUIRED_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SELF_TEST=pass")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_ONCE_MARKERS.values())}"
    )
    print(
        "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the shared Phase 9 runtime bitmap reminder packet keeps the "
            "survey note, module-slice note, manifest-backed ownership packet, "
            "shared reminder surfaces, and bounded build-route vocabulary aligned "
            "without promoting the bitmap packet into broader shared runtime-loader "
            "parity or a Phase 5 sample claim."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal current-like sample tree for focused checker replay",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_ERROR={failure}")
        return 1

    print("PHASE9_RUNTIME_BITMAP_REMINDER_PACKET=pass")
    print(f"PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_ONCE_MARKERS.values())}"
    )
    print(
        "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())