#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

GUIDE_PATH = Path("Documentation/zigux/phase5-sample-review-guide.md")
DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")
APPROVED_IDIOM_PATH = Path("Documentation/zigux/phase5-trace-events-approved-idiom-gap.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_ROOT_PATH = Path("scripts/zigux/README.md")
TESTS_ROOT_PATH = Path("zigux/tests/README.md")
LANE_SEQUENCING_PATH = Path("Documentation/zigux/phase5-sample-lane-sequencing.md")
SAMPLE_ROOT_PATH = Path("samples/zigux/README.md")

DIRECT_PACKET_PATHS = (
    "Documentation/zigux/phase5-kfifo-sample-survey.md",
    "Documentation/zigux/phase5-kretprobe-sample-survey.md",
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-trace-events-approved-idiom-gap.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "samples/zigux/bytestream_fifo.zig",
    "samples/zigux/kobject_example.zig",
    "samples/zigux/kobject_example_attr_group_contract.zig",
    "samples/zigux/kretprobe_example.zig",
    "samples/zigux/trace_events_string_formatting_sample.zig",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase5-review-guide-surface.py",
    "zigux/tests/README.md",
    "zigux/tests/phase5_bytestream_fifo.zig",
    "zigux/tests/phase5_bytestream_fifo_manifest.json",
    "zigux/tests/phase5_bytestream_fifo_survey.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_kobject_example_manifest.json",
    "zigux/tests/phase5_kretprobe_example.zig",
    "zigux/tests/phase5_kretprobe_example_manifest.json",
    "zigux/tests/phase5_kretprobe_example_survey.zig",
    "zigux/tests/phase5_build.zig",
)

PUBLIC_TREE_COMPANION_PATHS = (
    "zigux/tests/phase5_kobject_example_survey.zig",
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "samples/zigux/trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample_manifest.json",
    "zigux/tests/phase5_trace_events_sample_survey.zig",
)

MARKERS = {
    GUIDE_PATH: (
        "Treat those four anchors as the approved Phase 5 destination set unless the roadmap changes.",
        "The same authenticated route also directly returns the shared build-route companion `zigux/tests/phase5_build.zig` for this packet.",
        "Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample, and it still ships no standalone broad `*format*` Phase 5 reference sample outside the bounded trace-events cues carried by `samples/zigux/trace_events_string_formatting_sample.zig` and the shared reminder packet.",
        "Keep the direct validation routes explicit in that same guidance too: `zig test samples/zigux/bytestream_fifo.zig`, `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig`, and `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` stay visible as the sample-owned self-check route, the focused replay route, and the survey-packet guard, while the shared `zigux/tests/phase5_build.zig` line stays visible as current directly readable shared build-route companion evidence for this bytestream packet rather than as sample-local proof.",
        "keep the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit alongside the registered teardown, post-`exit()` rejection, and anchor-replay rejection packet",
    ),
    DOCS_ROOT_PATH: (
        "keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.",
        "keep the bounded `kobject` attr-group companion explicit here too: `samples/zigux/kobject_example_attr_group_contract.zig` is current direct sample-root evidence for the `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, and NULL-terminated attribute-list slot rather than a fifth Phase 5 sample family.",
        "keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the current `kobject` anchor split explicit instead of falling back to older repo-reality-gap wording.",
        "keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.",
    ),
    APPROVED_IDIOM_PATH: (
        "Keep the approved formatting idiom bounded to the current landed reminder packet:",
        "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
        "Keep the sample-owned review contract explicit too: the bounded formatting companion now centralizes the exact `checked_focus` order `string_selection,formatted_message,bounded_destination_discipline,non_allocating_runtime_safe`, and the approved-idiom reminder should preserve that same reading order beside the selected-string slot and `iter=%d` cue instead of reducing the trace-events packet to message text alone.",
    ),
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the shared Phase 5 sample packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-kobject-sample-survey.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/check-phase5-review-guide-surface.py`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still agree on the current four-anchor reminder packet,",
        "keep `samples/zigux/trace_events_string_formatting_sample.zig` framed only as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample,",
        "keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording,",
        "keep `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `samples/zigux/kobject_example_attr_group_contract.zig` explicit as the current direct sample-root, focused-test, and bounded attr-group companion evidence in this runtime, keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` framed as current public-tree-backed companion evidence until a fresh reread proves broader direct authenticated proof again, keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet,",
    ),
    SCRIPTS_ROOT_PATH: (
        "`python3 scripts/zigux/check-phase5-review-guide-surface.py --self-test` replays the shipped shared Phase 5 scripts-root reminder guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording",
        "keep the kobject split explicit too: `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are current direct reminder or packet evidence again, while `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those three routes directly again",
        "keep the no-extra-sample boundary explicit from the scripts root too: do not treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence, and do not treat standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` sample claims as landed Phase 5 proof on current `master`",
    ),
    TESTS_ROOT_PATH: (
        "Keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording instead of treating the Phase 5 tests-root packet as docs-only guidance.",
        "Keep `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` explicit as the direct bytestream replay, manifest, and survey packet while `zigux/tests/phase5_build.zig` stays current directly readable shared build-route companion evidence in this runtime.",
        "Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` is direct tests-root packet evidence again, `samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract plus the shared `0664`, unnamed-group, and NULL-terminated attribute-list cues, keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet, while `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those routes directly again.",
        "Keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 tests-root packet.",
    ),
    LANE_SEQUENCING_PATH: (
        "Keep the dedicated scripts-side review-guide guard explicit too: `scripts/zigux/check-phase5-review-guide-surface.py` is the shipped checker for the guide's direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording, so same-lane follow-through should not describe the shared Phase 5 packet as guide-only reminder prose anymore.",
        "Treat `samples/zigux/kobject_example.zig` as current direct sample-root evidence inside the mixed kobject packet recorded by `Documentation/zigux/phase5-kobject-current-readback-note.md`, while `zigux/tests/phase5_kobject_example_survey.zig` remains the public-tree-backed companion in this runtime and `zigux/tests/phase5_build.zig` stays directly readable as the shared build-route companion.",
        "Keep `samples/zigux/kobject_example_attr_group_contract.zig` explicit as direct current sample-root evidence for the bounded kobject attr-group companion rather than leaving that shipped reviewability file outside the sample-root inventory.",
        "Treat `samples/zigux/trace_events_string_formatting_sample.zig` as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.",
    ),
    SAMPLE_ROOT_PATH: (
        "Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime: `samples/zigux/kobject_example.zig` and `zigux/tests/phase5_kobject_example.zig` are direct authenticated reminder or packet evidence again, `zigux/tests/phase5_build.zig` is the current directly readable shared build-route companion for that packet, and `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those three routes directly again.",
        "Current `master` also ships `samples/zigux/kobject_example_attr_group_contract.zig` as a bounded kobject companion. Keep that file framed as reviewability help for the current `foo`/`baz`/`bar` attribute-group contract, `0664` modes, unnamed-group cue, and NULL-terminated attribute-list slot rather than as a fifth Phase 5 sample family.",
        "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.",
    ),
}

FORBIDDEN_GUIDE_TEXT = (
    "Treat `samples/zigux/trace_events_string_formatting_sample.zig` as a returned full trace-events port or a fifth sample.",
    "Treat the whole `kobject` packet as fully direct authenticated proof.",
    "Treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence.",
)


def read_text(root: Path, path: Path) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, path: Path, text: str) -> None:
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(text, encoding="utf-8")


def placeholder(path: Path) -> str:
    lines = [f"# {path.name}"]
    lines.extend(MARKERS[path])
    if path == GUIDE_PATH:
        lines.extend(f"`{rel}`" for rel in DIRECT_PACKET_PATHS)
        lines.extend(f"`{rel}`" for rel in PUBLIC_TREE_COMPANION_PATHS)
    if path == APPROVED_IDIOM_PATH:
        lines.extend(
            f"`{rel}`"
            for rel in (
                "samples/trace_events/trace-events-sample.c",
                "samples/zigux/trace_events_string_formatting_sample.zig",
                "Documentation/zigux/phase5-trace-events-sample-survey.md",
                "samples/zigux/trace_events_sample.zig",
                "zigux/tests/phase5_trace_events_sample.zig",
                "zigux/tests/phase5_trace_events_sample_manifest.json",
                "zigux/tests/phase5_trace_events_sample_survey.zig",
                "zigux/tests/phase5_build.zig",
                "scripts/zigux/check-phase5-review-guide-surface.py",
            )
        )
    return "\n\n".join(lines) + "\n"


def seed(root: Path) -> None:
    tracked = set(MARKERS)
    for path in MARKERS:
        write_text(root, path, placeholder(path))
    for rel in DIRECT_PACKET_PATHS + PUBLIC_TREE_COMPANION_PATHS + (
        "samples/trace_events/trace-events-sample.c",
    ):
        rel_path = Path(rel)
        if rel_path in tracked:
            continue
        write_text(root, rel_path, "present\n")


def collect_failures(root: Path) -> list[str]:
    texts = {path: read_text(root, path) for path in MARKERS}
    failures: list[str] = []

    for path, required in MARKERS.items():
        text = texts[path]
        for marker in required:
            if marker not in text:
                failures.append(f"{path}:missing_text:{marker}")

    guide = texts[GUIDE_PATH]
    approved = texts[APPROVED_IDIOM_PATH]
    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in guide and rel not in guide:
            failures.append(f"guide:missing_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_path:{rel}")

    for rel in PUBLIC_TREE_COMPANION_PATHS:
        if all(token not in approved and token not in guide for token in (f"`{rel}`", rel)):
            failures.append(f"packet:missing_companion_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_companion_path:{rel}")

    for rel in (
        "samples/trace_events/trace-events-sample.c",
        "samples/zigux/trace_events_string_formatting_sample.zig",
        "zigux/tests/phase5_build.zig",
    ):
        if all(token not in approved for token in (f"`{rel}`", rel)):
            failures.append(f"approved_idiom:missing_path:{rel}")

    for forbidden in FORBIDDEN_GUIDE_TEXT:
        if forbidden in guide:
            failures.append(f"guide:forbidden_text:{forbidden}")

    return failures


def expect_exact(label: str, failures: list[str], expected: list[str]) -> None:
    if failures != expected:
        raise AssertionError(f"{label}: expected {expected}, got {failures}")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 15
    with tempfile.TemporaryDirectory(prefix="phase5_review_guide_surface_") as tmpdir:
        root = Path(tmpdir)
        seed(root)

        expect_exact("baseline", collect_failures(root), [])
        checks_run += 1

        mutated = root / "missing_guide_validation_marker"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, placeholder(GUIDE_PATH).replace(MARKERS[GUIDE_PATH][3], ""))
        expect_exact(
            "guide_validation_marker",
            collect_failures(mutated),
            [f"{GUIDE_PATH}:missing_text:{MARKERS[GUIDE_PATH][3]}"],
        )
        checks_run += 1

        mutated = root / "missing_review_checklist_marker"
        seed(mutated)
        write_text(mutated, REVIEW_CHECKLIST_PATH, placeholder(REVIEW_CHECKLIST_PATH).replace(MARKERS[REVIEW_CHECKLIST_PATH][3], ""))
        expect_exact(
            "review_checklist_marker",
            collect_failures(mutated),
            [f"{REVIEW_CHECKLIST_PATH}:missing_text:{MARKERS[REVIEW_CHECKLIST_PATH][3]}"],
        )
        checks_run += 1

        mutated = root / "missing_scripts_root_marker"
        seed(mutated)
        write_text(mutated, SCRIPTS_ROOT_PATH, placeholder(SCRIPTS_ROOT_PATH).replace(MARKERS[SCRIPTS_ROOT_PATH][1], ""))
        expect_exact(
            "scripts_root_marker",
            collect_failures(mutated),
            [f"{SCRIPTS_ROOT_PATH}:missing_text:{MARKERS[SCRIPTS_ROOT_PATH][1]}"],
        )
        checks_run += 1

        mutated = root / "missing_scripts_root_bitmap_boundary"
        seed(mutated)
        write_text(mutated, SCRIPTS_ROOT_PATH, placeholder(SCRIPTS_ROOT_PATH).replace(MARKERS[SCRIPTS_ROOT_PATH][2], ""))
        expect_exact(
            "scripts_root_bitmap_boundary",
            collect_failures(mutated),
            [f"{SCRIPTS_ROOT_PATH}:missing_text:{MARKERS[SCRIPTS_ROOT_PATH][2]}"],
        )
        checks_run += 1

        mutated = root / "missing_sample_root_marker"
        seed(mutated)
        write_text(mutated, SAMPLE_ROOT_PATH, placeholder(SAMPLE_ROOT_PATH).replace(MARKERS[SAMPLE_ROOT_PATH][0], ""))
        expect_exact(
            "sample_root_marker",
            collect_failures(mutated),
            [f"{SAMPLE_ROOT_PATH}:missing_text:{MARKERS[SAMPLE_ROOT_PATH][0]}"],
        )
        checks_run += 1

        mutated = root / "missing_docs_root_rbtree_boundary_marker"
        seed(mutated)
        write_text(
            mutated,
            DOCS_ROOT_PATH,
            placeholder(DOCS_ROOT_PATH).replace(MARKERS[DOCS_ROOT_PATH][3], ""),
        )
        expect_exact(
            "docs_root_rbtree_boundary_marker",
            collect_failures(mutated),
            [f"{DOCS_ROOT_PATH}:missing_text:{MARKERS[DOCS_ROOT_PATH][3]}"],
        )
        checks_run += 1

        mutated = root / "missing_approved_idiom_checked_focus_marker"
        seed(mutated)
        write_text(
            mutated,
            APPROVED_IDIOM_PATH,
            placeholder(APPROVED_IDIOM_PATH).replace(MARKERS[APPROVED_IDIOM_PATH][2], ""),
        )
        expect_exact(
            "approved_idiom_checked_focus_marker",
            collect_failures(mutated),
            [f"{APPROVED_IDIOM_PATH}:missing_text:{MARKERS[APPROVED_IDIOM_PATH][2]}"],
        )
        checks_run += 1

        mutated = root / "missing_lane_sequencing_trace_events_marker"
        seed(mutated)
        write_text(
            mutated,
            LANE_SEQUENCING_PATH,
            placeholder(LANE_SEQUENCING_PATH).replace(MARKERS[LANE_SEQUENCING_PATH][3], ""),
        )
        expect_exact(
            "lane_sequencing_trace_events_marker",
            collect_failures(mutated),
            [f"{LANE_SEQUENCING_PATH}:missing_text:{MARKERS[LANE_SEQUENCING_PATH][3]}"],
        )
        checks_run += 1

        mutated = root / "missing_tests_root_bytestream_build_route_marker"
        seed(mutated)
        write_text(mutated, TESTS_ROOT_PATH, placeholder(TESTS_ROOT_PATH).replace(MARKERS[TESTS_ROOT_PATH][1], ""))
        expect_exact(
            "tests_root_bytestream_build_route_marker",
            collect_failures(mutated),
            [f"{TESTS_ROOT_PATH}:missing_text:{MARKERS[TESTS_ROOT_PATH][1]}"],
        )
        checks_run += 1

        mutated = root / "missing_tests_root_bitmap_boundary"
        seed(mutated)
        write_text(mutated, TESTS_ROOT_PATH, placeholder(TESTS_ROOT_PATH).replace(MARKERS[TESTS_ROOT_PATH][3], ""))
        expect_exact(
            "tests_root_bitmap_boundary",
            collect_failures(mutated),
            [f"{TESTS_ROOT_PATH}:missing_text:{MARKERS[TESTS_ROOT_PATH][3]}"],
        )
        checks_run += 1

        mutated = root / "missing_direct_path"
        seed(mutated)
        (mutated / DIRECT_PACKET_PATHS[8]).unlink()
        expect_exact("missing_direct_path", collect_failures(mutated), [f"repo:missing_path:{DIRECT_PACKET_PATHS[8]}"])
        checks_run += 1

        mutated = root / "missing_phase5_build_direct_path"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, placeholder(GUIDE_PATH).replace("`zigux/tests/phase5_build.zig`", ""))
        expect_exact(
            "missing_phase5_build_direct_path",
            collect_failures(mutated),
            [
                f"{GUIDE_PATH}:missing_text:{MARKERS[GUIDE_PATH][1]}",
                f"{GUIDE_PATH}:missing_text:{MARKERS[GUIDE_PATH][3]}",
                "guide:missing_path:zigux/tests/phase5_build.zig",
            ],
        )
        checks_run += 1

        mutated = root / "forbidden_text"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, placeholder(GUIDE_PATH) + FORBIDDEN_GUIDE_TEXT[0] + "\n")
        expect_exact("forbidden_text", collect_failures(mutated), [f"guide:forbidden_text:{FORBIDDEN_GUIDE_TEXT[0]}"])
        checks_run += 1

        mutated = root / "missing_required_file"
        seed(mutated)
        (mutated / SCRIPTS_ROOT_PATH).unlink()
        try:
            collect_failures(mutated)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise AssertionError(f"unexpected missing-file abort: {exc}") from exc
        else:
            raise AssertionError("missing required file did not abort")
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} checks, ran {checks_run}")
    print("PHASE5_REVIEW_GUIDE_SURFACE_SELF_TEST=pass")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify that the Phase 5 review guide packet stays aligned with current shared sample surfaces.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE5_REVIEW_GUIDE_SURFACE=pass")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_DIRECT_PACKET_COUNT={len(DIRECT_PACKET_PATHS)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_PUBLIC_TREE_COMPANION_COUNT={len(PUBLIC_TREE_COMPANION_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
