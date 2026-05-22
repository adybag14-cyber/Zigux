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
)

PUBLIC_TREE_COMPANION_PATHS = (
    "zigux/tests/phase5_kobject_example_survey.zig",
    "zigux/tests/phase5_build.zig",
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "samples/zigux/trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample_manifest.json",
    "zigux/tests/phase5_trace_events_sample_survey.zig",
)

GUIDE_MARKERS = (
    "Treat those four anchors as the approved Phase 5 destination set unless the roadmap changes.",
    "Fresh 2026-05-20 follow-up reread also keeps the current direct packet shape explicit: `samples/zigux/bytestream_fifo.zig` now carries four in-file self-checks, `zigux/tests/phase5_bytestream_fifo.zig` keeps five focused replay tests, and `zigux/tests/phase5_bytestream_fifo_survey.zig` keeps five survey-packet checks aligned with the survey note and manifest.",
    "Fresh public current-`master` fallback on 2026-05-19 also keeps the broader non-runtime trace-events sample packet visible",
    "The roadmap still includes the `kobject` anchor, and fresh Phase 5 reread in this run kept the split evidence explicit: authenticated current-`master` contents readback in this runtime directly returned `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and the shared build-route companion `zigux/tests/phase5_build.zig`, while the same reread also directly returned `samples/zigux/kobject_example_attr_group_contract.zig` as the bounded attr-group companion and fresh public current-`master` GitHub file readback kept `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` visible beside that direct packet.",
    "The same authenticated route also directly returns the shared build-route companion `zigux/tests/phase5_build.zig` for this packet.",
    "Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample, and it still ships no standalone broad `*format*` Phase 5 reference sample outside the bounded trace-events cues carried by `samples/zigux/trace_events_string_formatting_sample.zig` and the shared reminder packet.",
)

DOCS_ROOT_MARKERS = (
    "keep the current four-anchor non-runtime sample packet explicit from the docs root instead of letting the shared contributor reminder drift away from the live sample-root, scripts-root, guide, sequencing, checklist, and tests-root packet.",
    "keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.",
    "keep the current `kobject` ownership-and-lifetime split explicit too:",
    "keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.",
    "keep the bounded `kobject` attr-group companion explicit here too: `samples/zigux/kobject_example_attr_group_contract.zig` is current direct sample-root evidence for the `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, and NULL-terminated attribute-list slot rather than a fifth Phase 5 sample family.",
    "keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the current `kobject` anchor split explicit instead of falling back to older repo-reality-gap wording.",
)

APPROVED_IDIOM_MARKERS = (
    "Fresh mixed reread on 2026-05-20 keeps the broader non-runtime trace-events sample-local companions in a split state rather than a missing state:",
    "Those paths are again carried by the live trace-events reminder packet and current public-tree-backed reread surfaces, but the authenticated contents route used for this lane still did not return them directly on 2026-05-20.",
    "Keep the approved formatting idiom bounded to the current landed reminder packet:",
    "Keep the direct modulo-selected cycle explicit too: `runStringFormattingCycleReplay()` now walks all five selected strings through the bounded `iter=%d` formatter while keeping the companion in `.initialized` and leaving `replay_runs` unchanged.",
    "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
)

REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 5 sample packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-kobject-sample-survey.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/check-phase5-review-guide-surface.py`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still agree on the current four-anchor reminder packet,",
    "keep `samples/zigux/trace_events_string_formatting_sample.zig` framed only as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample,",
    "keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording,",
    "keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `samples/zigux/kobject_example_attr_group_contract.zig` explicit as the current direct survey-note, sample-root, focused-test, manifest-backed, and bounded attr-group companion evidence in this runtime, keep `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` framed as current public-tree-backed companion evidence until a fresh reread proves broader direct authenticated proof again,",
)

SCRIPTS_ROOT_MARKERS = (
    "Phase 5 flow - the current scripts-root sample packet stays reviewable through the shipped guide-surface guard, the restored direct bytestream sample-plus-tests packet, the restored direct non-runtime kretprobe packet, the narrower trace-events formatting companion, and the split-readback kobject reminder packet instead of flattening all four roadmap anchors into sample-root-only proof, guide-only prose, or a blanket missing-sample story",
    "`python3 scripts/zigux/check-phase5-review-guide-surface.py --self-test` replays the shipped shared Phase 5 scripts-root reminder guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording",
    "keep the kobject split explicit too: `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are current direct reminder or packet evidence again, while `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those three routes directly again",
    "keep the bytestream build split explicit too: `zigux/tests/phase5_build.zig` remains current public-tree-backed companion evidence for this scripts-root packet until a fresh authenticated reread returns that shared build route directly again",
)

TESTS_ROOT_MARKERS = (
    "Keep the current bounded Phase 5 tests-root reminder packet explicit through `Documentation/zigux/README.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-kobject-sample-survey.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase5-review-guide-surface.py`, and `zigux/tests/README.md`.",
    "Keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording instead of treating the Phase 5 tests-root packet as docs-only guidance.",
    "Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` and `zigux/tests/phase5_kobject_example_manifest.json` are direct tests-root packet evidence again, `samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract plus the shared `0664`, unnamed-group, and NULL-terminated attribute-list cues, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those two routes directly again.",
)

LANE_SEQUENCING_MARKERS = (
    "Keep the dedicated scripts-side review-guide guard explicit too: `scripts/zigux/check-phase5-review-guide-surface.py` is the shipped checker for the guide's direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording, so same-lane follow-through should not describe the shared Phase 5 packet as guide-only reminder prose anymore.",
    "Keep shared contributor guidance honest about that mixed direct-versus-public-tree-backed split instead of repeating older kobject-reread-needed wording, collapsing the packet into repo absence, or overstating fully direct authenticated proof.",
    "Treat `samples/zigux/kobject_example.zig` as current direct sample-root evidence inside the mixed kobject packet recorded by `Documentation/zigux/phase5-kobject-current-readback-note.md`, while `zigux/tests/phase5_kobject_example_survey.zig` remains the public-tree-backed companion in this runtime and `zigux/tests/phase5_build.zig` stays directly readable as the shared build-route companion.",
    "Keep `samples/zigux/kobject_example_attr_group_contract.zig` explicit as direct current sample-root evidence for the bounded kobject attr-group companion rather than leaving that shipped reviewability file outside the sample-root inventory.",
)

SAMPLE_ROOT_MARKERS = (
    "Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime: `samples/zigux/kobject_example.zig` and `zigux/tests/phase5_kobject_example.zig` are direct authenticated reminder or packet evidence again, `zigux/tests/phase5_build.zig` is the current directly readable shared build-route companion for that packet, and `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those three routes directly again.",
    "Current `master` also ships `samples/zigux/kobject_example_attr_group_contract.zig` as a bounded kobject companion. Keep that file framed as reviewability help for the current `foo`/`baz`/`bar` attribute-group contract, `0664` modes, unnamed-group cue, and NULL-terminated attribute-list slot rather than as a fifth Phase 5 sample family.",
    "Current `master` still ships no standalone Phase 5 sample-root files here for:\n\n* `*string*`\n* `*kasprintf*`\n* `*strarray*`\n* `*cmdline*`\n* `*argv*`\n* `*rbtree*`\n* `*bitmap*`\n* `*printf*`\n* `*vsprintf*`",
    "Current `master` does ship one bounded `*string*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace_events` anchor instead of treating it as a standalone helper packet or a fifth Phase 5 sample.",
    "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here. Keep that formatting boundary tied to `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` and the bounded `samples/zigux/trace_events_string_formatting_sample.zig` companion.",
    "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.",
    "Fresh trusted mixed reread on 2026-05-20 also restored a narrower runtime bitmap sample-side packet on current `master`: direct authenticated contents reads now materialize `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and `zigux/tests/runtime_bitmap_manifest.json`, while `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and the shared `zigux/tests/phase9_build.zig` bundle keep the same sample-side reminder packet explicit, and `zigux/tests/runtime_bitmap_module.zig` plus `zigux/tests/runtime_bitmap_diff.zig` still remain absent on the same trusted path. Keep that bitmap packet framed as a separate Phase 9 runtime reminder rather than as proof that the broader shared runtime-loader packet returned or as evidence that a fifth approved Phase 5 sample family landed here.",
)

FORBIDDEN_GUIDE_TEXT = (
    "Treat `samples/zigux/trace_events_string_formatting_sample.zig` as a returned full trace-events port or a fifth sample.",
    "Treat the whole `kobject` packet as fully direct authenticated proof.",
    "Treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence.",
)

ALL_TEXT_CHECKS = (
    (GUIDE_PATH, GUIDE_MARKERS),
    (DOCS_ROOT_PATH, DOCS_ROOT_MARKERS),
    (APPROVED_IDIOM_PATH, APPROVED_IDIOM_MARKERS),
    (REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_MARKERS),
    (SCRIPTS_ROOT_PATH, SCRIPTS_ROOT_MARKERS),
    (TESTS_ROOT_PATH, TESTS_ROOT_MARKERS),
    (LANE_SEQUENCING_PATH, LANE_SEQUENCING_MARKERS),
    (SAMPLE_ROOT_PATH, SAMPLE_ROOT_MARKERS),
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _placeholder_text(path: Path, markers: tuple[str, ...]) -> str:
    header = f"# {path.name}"
    extra_lines: list[str] = []
    if path == GUIDE_PATH:
        extra_lines.extend(f"`{rel}`" for rel in DIRECT_PACKET_PATHS)
        extraLines = [f"`{rel}`" for rel in PUBLIC_TREE_COMPANION_PATHS]
        extra_lines.extend(extraLines)
    if path == APPROVED_IDIOM_PATH:
        extra_lines.extend(
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
    body = "\n\n".join((*markers, *extra_lines))
    return f"{header}\n\n{body}\n"


def collect_failures(root: Path) -> list[str]:
    texts = {path: _read(root / path) for path, _ in ALL_TEXT_CHECKS}
    failures: list[str] = []

    for path, markers in ALL_TEXT_CHECKS:
        text = texts[path]
        for marker in markers:
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
        if f"`{rel}`" not in guide and rel not in guide and f"`{rel}`" not in approved and rel not in approved:
            failures.append(f"packet:missing_companion_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_companion_path:{rel}")

    for rel in (
        "samples/trace_events/trace-events-sample.c",
        "samples/zigux/trace_events_string_formatting_sample.zig",
        "zigux/tests/phase5_build.zig",
    ):
        if f"`{rel}`" not in approved and rel not in approved:
            failures.append(f"approved_idiom:missing_path:{rel}")

    for text in FORBIDDEN_GUIDE_TEXT:
        if text in guide:
            failures.append(f"guide:forbidden_text:{text}")

    return failures


def _seed(root: Path) -> None:
    tracked_text_paths = {path for path, _ in ALL_TEXT_CHECKS}
    for path, markers in ALL_TEXT_CHECKS:
        _write(root / path, _placeholder_text(path, markers))
    for rel in DIRECT_PACKET_PATHS + PUBLIC_TREE_COMPANION_PATHS + (
        "samples/trace_events/trace-events-sample.c",
    ):
        if Path(rel) in tracked_text_paths:
            continue
        _write(root / rel, "present\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 19
    with tempfile.TemporaryDirectory(prefix="phase5_review_guide_surface_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        checks_run += 1

        missing_guide_kobject_build_marker_root = root / "missing_guide_kobject_build_marker"
        _seed(missing_guide_kobject_build_marker_root)
        _write(
            missing_guide_kobject_build_marker_root / GUIDE_PATH,
            _placeholder_text(
                GUIDE_PATH,
                (
                    GUIDE_MARKERS[0],
                    GUIDE_MARKERS[1],
                    GUIDE_MARKERS[2],
                    GUIDE_MARKERS[3],
                    GUIDE_MARKERS[5],
                ),
            ),
        )
        failures = collect_failures(missing_guide_kobject_build_marker_root)
        expected = [f"{GUIDE_PATH}:missing_text:{GUIDE_MARKERS[4]}"]
        if failures != expected:
            raise AssertionError(f"unexpected guide kobject-build failure: {failures}")
        checks_run += 1

        missing_approved_marker_root = root / "missing_approved_marker"
        _seed(missing_approved_marker_root)
        _write(
            missing_approved_marker_root / APPROVED_IDIOM_PATH,
            _placeholder_text(APPROVED_IDIOM_PATH, APPROVED_IDIOM_MARKERS[1:]),
        )
        failures = collect_failures(missing_approved_marker_root)
        expected = [f"{APPROVED_IDIOM_PATH}:missing_text:{APPROVED_IDIOM_MARKERS[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected approved-idiom failure: {failures}")
        checks_run += 1

        missing_review_checklist_marker_root = root / "missing_review_checklist_marker"
        _seed(missing_review_checklist_marker_root)
        _write(
            missing_review_checklist_marker_root / REVIEW_CHECKLIST_PATH,
            _placeholder_text(
                REVIEW_CHECKLIST_PATH,
                (
                    REVIEW_CHECKLIST_MARKERS[0],
                    REVIEW_CHECKLIST_MARKERS[2],
                    REVIEW_CHECKLIST_MARKERS[3],
                ),
            ),
        )
        failures = collect_failures(missing_review_checklist_marker_root)
        expected = [f"{REVIEW_CHECKLIST_PATH}:missing_text:{REVIEW_CHECKLIST_MARKERS[1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected review-checklist failure: {failures}")
        checks_run += 1

        missing_docs_root_marker_root = root / "missing_docs_root_marker"
        _seed(missing_docs_root_marker_root)
        _write(
            missing_docs_root_marker_root / DOCS_ROOT_PATH,
            _placeholder_text(
                DOCS_ROOT_PATH,
                (
                    DOCS_ROOT_MARKERS[0],
                    DOCS_ROOT_MARKERS[1],
                    DOCS_ROOT_MARKERS[2],
                    DOCS_ROOT_MARKERS[4],
                    DOCS_ROOT_MARKERS[5],
                ),
            ),
        )
        failures = collect_failures(missing_docs_root_marker_root)
        expected = [f"{DOCS_ROOT_PATH}:missing_text:{DOCS_ROOT_MARKERS[3]}"]
        if failures != expected:
            raise AssertionError(f"unexpected docs-root failure: {failures}")
        checks_run += 1

        missing_docs_root_attr_group_marker_root = root / "missing_docs_root_attr_group_marker"
        _seed(missing_docs_root_attr_group_marker_root)
        _write(
            missing_docs_root_attr_group_marker_root / DOCS_ROOT_PATH,
            _placeholder_text(
                DOCS_ROOT_PATH,
                (
                    DOCS_ROOT_MARKERS[0],
                    DOCS_ROOT_MARKERS[1],
                    DOCS_ROOT_MARKERS[2],
                    DOCS_ROOT_MARKERS[3],
                    DOCS_ROOT_MARKERS[5],
                ),
            ),
        )
        failures = collect_failures(missing_docs_root_attr_group_marker_root)
        expected = [f"{DOCS_ROOT_PATH}:missing_text:{DOCS_ROOT_MARKERS[4]}"]
        if failures != expected:
            raise AssertionError(f"unexpected docs-root attr-group failure: {failures}")
        checks_run += 1

        missing_docs_root_runtime_boundary_root = root / "missing_docs_root_runtime_boundary"
        _seed(missing_docs_root_runtime_boundary_root)
        _write(
            missing_docs_root_runtime_boundary_root / DOCS_ROOT_PATH,
            _placeholder_text(
                DOCS_ROOT_PATH,
                (
                    DOCS_ROOT_MARKERS[0],
                    DOCS_ROOT_MARKERS[1],
                    DOCS_ROOT_MARKERS[2],
                    DOCS_ROOT_MARKERS[3],
                    DOCS_ROOT_MARKERS[4],
                ),
            ),
        )
        failures = collect_failures(missing_docs_root_runtime_boundary_root)
        expected = [f"{DOCS_ROOT_PATH}:missing_text:{DOCS_ROOT_MARKERS[5]}"]
        if failures != expected:
            raise AssertionError(f"unexpected docs-root runtime-boundary failure: {failures}")
        checks_run += 1

        missing_scripts_root_bytestream_build_marker_root = root / "missing_scripts_root_bytestream_build_marker"
        _seed(missing_scripts_root_bytestream_build_marker_root)
        _write(
            missing_scripts_root_bytestream_build_marker_root / SCRIPTS_ROOT_PATH,
            _placeholder_text(
                SCRIPTS_ROOT_PATH,
                (
                    SCRIPTS_ROOT_MARKERS[0],
                    SCRIPTS_ROOT_MARKERS[1],
                    SCRIPTS_ROOT_MARKERS[2],
                ),
            ),
        )
        failures = collect_failures(missing_scripts_root_bytestream_build_marker_root)
        expected = [f"{SCRIPTS_ROOT_PATH}:missing_text:{SCRIPTS_ROOT_MARKERS[3]}"]
        if failures != expected:
            raise AssertionError(f"unexpected scripts-root bytestream-build failure: {failures}")
        checks_run += 1

        missing_tests_root_kobject_marker_root = root / "missing_tests_root_kobject_marker"
        _seed(missing_tests_root_kobject_marker_root)
        _write(
            missing_tests_root_kobject_marker_root / TESTS_ROOT_PATH,
            _placeholder_text(
                TESTS_ROOT_PATH,
                (
                    TESTS_ROOT_MARKERS[0],
                    TESTS_ROOT_MARKERS[1],
                ),
            ),
        )
        failures = collect_failures(missing_tests_root_kobject_marker_root)
        expected = [f"{TESTS_ROOT_PATH}:missing_text:{TESTS_ROOT_MARKERS[2]}"]
        if failures != expected:
            raise AssertionError(f"unexpected tests-root kobject failure: {failures}")
        checks_run += 1

        missing_lane_sequencing_kobject_build_marker_root = root / "missing_lane_sequencing_kobject_build_marker"
        _seed(missing_lane_sequencing_kobject_build_marker_root)
        _write(
            missing_lane_sequencing_kobject_build_marker_root / LANE_SEQUENCING_PATH,
            _placeholder_text(
                LANE_SEQUENCING_PATH,
                (
                    LANE_SEQUENCING_MARKERS[0],
                    LANE_SEQUENCING_MARKERS[1],
                    LANE_SEQUENCING_MARKERS[3],
                ),
            ),
        )
        failures = collect_failures(missing_lane_sequencing_kobject_build_marker_root)
        expected = [f"{LANE_SEQUENCING_PATH}:missing_text:{LANE_SEQUENCING_MARKERS[2]}"]
        if failures != expected:
            raise AssertionError(f"unexpected lane-sequencing kobject-build failure: {failures}")
        checks_run += 1

        missing_sample_root_marker_root = root / "missing_sample_root_marker"
        _seed(missing_sample_root_marker_root)
        _write(
            missing_sample_root_marker_root / SAMPLE_ROOT_PATH,
            _placeholder_text(
                SAMPLE_ROOT_PATH,
                (
                    SAMPLE_ROOT_MARKERS[1],
                    SAMPLE_ROOT_MARKERS[2],
                    SAMPLE_ROOT_MARKERS[3],
                    SAMPLE_ROOT_MARKERS[4],
                    SAMPLE_ROOT_MARKERS[5],
                    SAMPLE_ROOT_MARKERS[6],
                ),
            ),
        )
        failures = collect_failures(missing_sample_root_marker_root)
        expected = [f"{SAMPLE_ROOT_PATH}:missing_text:{SAMPLE_ROOT_MARKERS[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected sample-root failure: {failures}")
        checks_run += 1

        missing_sample_root_attr_group_marker_root = root / "missing_sample_root_attr_group_marker"
        _seed(missing_sample_root_attr_group_marker_root)
        _write(
            missing_sample_root_attr_group_marker_root / SAMPLE_ROOT_PATH,
            _placeholder_text(
                SAMPLE_ROOT_PATH,
                (
                    SAMPLE_ROOT_MARKERS[0],
                    SAMPLE_ROOT_MARKERS[2],
                    SAMPLE_ROOT_MARKERS[3],
                    SAMPLE_ROOT_MARKERS[4],
                    SAMPLE_ROOT_MARKERS[5],
                    SAMPLE_ROOT_MARKERS[6],
                ),
            ),
        )
        failures = collect_failures(missing_sample_root_attr_group_marker_root)
        expected = [f"{SAMPLE_ROOT_PATH}:missing_text:{SAMPLE_ROOT_MARKERS[1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected sample-root attr-group failure: {failures}")
        checks_run += 1

        missing_sample_root_boundary_root = root / "missing_sample_root_boundary"
        _seed(missing_sample_root_boundary_root)
        _write(
            missing_sample_root_boundary_root / SAMPLE_ROOT_PATH,
            _placeholder_text(
                SAMPLE_ROOT_PATH,
                (
                    SAMPLE_ROOT_MARKERS[0],
                    SAMPLE_ROOT_MARKERS[1],
                    SAMPLE_ROOT_MARKERS[3],
                    SAMPLE_ROOT_MARKERS[4],
                    SAMPLE_ROOT_MARKERS[5],
                    SAMPLE_ROOT_MARKERS[6],
                ),
            ),
        )
        failures = collect_failures(missing_sample_root_boundary_root)
        expected = [f"{SAMPLE_ROOT_PATH}:missing_text:{SAMPLE_ROOT_MARKERS[2]}"]
        if failures != expected:
            raise AssertionError(f"unexpected sample-root boundary failure: {failures}")
        checks_run += 1

        missing_sample_root_bitmap_marker_root = root / "missing_sample_root_bitmap_marker"
        _seed(missing_sample_root_bitmap_marker_root)
        _write(
            missing_sample_root_bitmap_marker_root / SAMPLE_ROOT_PATH,
            _placeholder_text(
                SAMPLE_ROOT_PATH,
                (
                    SAMPLE_ROOT_MARKERS[0],
                    SAMPLE_ROOT_MARKERS[1],
                    SAMPLE_ROOT_MARKERS[2],
                    SAMPLE_ROOT_MARKERS[3],
                    SAMPLE_ROOT_MARKERS[4],
                    SAMPLE_ROOT_MARKERS[6],
                ),
            ),
        )
        failures = collect_failures(missing_sample_root_bitmap_marker_root)
        expected = [f"{SAMPLE_ROOT_PATH}:missing_text:{SAMPLE_ROOT_MARKERS[5]}"]
        if failures != expected:
            raise AssertionError(f"unexpected sample-root bitmap failure: {failures}")
        checks_run += 1

        missing_sample_root_runtime_bitmap_packet_root = root / "missing_sample_root_runtime_bitmap_packet"
        _seed(missing_sample_root_runtime_bitmap_packet_root)
        _write(
            missing_sample_root_runtime_bitmap_packet_root / SAMPLE_ROOT_PATH,
            _placeholder_text(
                SAMPLE_ROOT_PATH,
                (
                    SAMPLE_ROOT_MARKERS[0],
                    SAMPLE_ROOT_MARKERS[1],
                    SAMPLE_ROOT_MARKERS[2],
                    SAMPLE_ROOT_MARKERS[3],
                    SAMPLE_ROOT_MARKERS[4],
                    SAMPLE_ROOT_MARKERS[5],
                ),
            ),
        )
        failures = collect_failures(missing_sample_root_runtime_bitmap_packet_root)
        expected = [f"{SAMPLE_ROOT_PATH}:missing_text:{SAMPLE_ROOT_MARKERS[6]}"]
        if failures != expected:
            raise AssertionError(f"unexpected sample-root runtime-bitmap-packet failure: {failures}")
        checks_run += 1

        missing_direct_path_root = root / "missing_direct_path"
        _seed(missing_direct_path_root)
        (missing_direct_path_root / DIRECT_PACKET_PATHS[8]).unlink()
        failures = collect_failures(missing_direct_path_root)
        expected = [f"repo:missing_path:{DIRECT_PACKET_PATHS[8]}"]
        if failures != expected:
            raise AssertionError(f"unexpected direct-path failure: {failures}")
        checks_run += 1

        missing_attr_group_guide_path_root = root / "missing_attr_group_guide_path"
        _seed(missing_attr_group_guide_path_root)
        _write(
            missing_attr_group_guide_path_root / GUIDE_PATH,
            _placeholder_text(GUIDE_PATH, GUIDE_MARKERS).replace(
                "`samples/zigux/kobject_example_attr_group_contract.zig`\n\n",
                "",
            ),
        )
        failures = collect_failures(missing_attr_group_guide_path_root)
        expected = ["guide:missing_path:samples/zigux/kobject_example_attr_group_contract.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected attr-group guide-path failure: {failures}")
        checks_run += 1

        forbidden_text_root = root / "forbidden_text"
        _seed(forbidden_text_root)
        _write(
            forbidden_text_root / GUIDE_PATH,
            _placeholder_text(GUIDE_PATH, GUIDE_MARKERS) + FORBIDDEN_GUIDE_TEXT[0] + "\n",
        )
        failures = collect_failures(forbidden_text_root)
        expected = [f"guide:forbidden_text:{FORBIDDEN_GUIDE_TEXT[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected forbidden-text failure: {failures}")
        checks_run += 1

        missing_scripts_root_file = root / "missing_scripts_root_file"
        _seed(missing_scripts_root_file)
        (missing_scripts_root_file / SCRIPTS_ROOT_PATH).unlink()
        try:
            collect_failures(missing_scripts_root_file)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise AssertionError(f"unexpected missing-file abort: {exc}") from exc
        else:
            raise AssertionError("missing scripts root did not abort")
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} checks, ran {checks_run}")
    print("PHASE5_REVIEW_GUIDE_SURFACE_SELF_TEST=pass")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 5 review guide packet stays aligned with the current shared sample surfaces."
    )
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
