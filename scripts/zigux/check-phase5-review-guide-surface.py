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
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/phase5-trace-events-approved-idiom-gap.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "samples/zigux/bytestream_fifo.zig",
    "samples/zigux/kretprobe_example.zig",
    "samples/zigux/trace_events_string_formatting_sample.zig",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase5-review-guide-surface.py",
    "zigux/tests/README.md",
    "zigux/tests/phase5_bytestream_fifo.zig",
    "zigux/tests/phase5_bytestream_fifo_manifest.json",
    "zigux/tests/phase5_bytestream_fifo_survey.zig",
    "zigux/tests/phase5_kretprobe_example.zig",
    "zigux/tests/phase5_kretprobe_example_manifest.json",
    "zigux/tests/phase5_kretprobe_example_survey.zig",
)

KOBJECT_DIRECT_PACKET_PATHS = (
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "samples/zigux/kobject_example.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_kobject_example_manifest.json",
)

KOBJECT_PUBLIC_TREE_PACKET_PATHS = (
    "zigux/tests/phase5_kobject_example_survey.zig",
    "zigux/tests/phase5_build.zig",
)

TRACE_EVENTS_COMPANION_GAP_PATHS = (
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "samples/zigux/trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample_manifest.json",
    "zigux/tests/phase5_trace_events_sample_survey.zig",
)

REQUIRED_TEXT = (
    "Treat those four anchors as the approved Phase 5 destination set unless the roadmap changes.",
    "Fresh repo-first inspection on 2026-05-19 confirmed that current `master` now directly serves the bounded bytestream sample-plus-tests packet through these paths:",
    "Fresh 2026-05-19 reread also keeps the current direct packet shape explicit: `samples/zigux/bytestream_fifo.zig` now carries three in-file self-checks, `zigux/tests/phase5_bytestream_fifo.zig` keeps four focused replay tests, and `zigux/tests/phase5_bytestream_fifo_survey.zig` keeps five survey-packet checks aligned with the survey note and manifest.",
    "The same 2026-05-19 repo-first inspection also confirmed a narrower current non-runtime trace-events packet: authenticated contents reread still directly proves the bounded formatting companion, and the shared reminder surfaces below still keep that smaller packet explicit:",
    "For the shared tracing and probe lane, ground reviewer guidance in the restored direct kretprobe packet plus the narrower trace-events packet above and these shared reminder surfaces:",
    "The roadmap still includes the `kobject` anchor, and fresh Phase 5 reread in this run kept the split evidence explicit: authenticated current-`master` contents readback directly returned the survey note, sample root, focused test, and manifest-backed contract again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` still need public-tree fallback in this runtime.",
    "Keep shared contributor guidance honest about that split instead of flattening the whole kobject packet into public-tree-only support material, treating the sample-local direct proof as gone, or promoting the survey replay plus shared build route into returned authenticated proof.",
    "Because current `master` keeps the restored direct bytestream sample-plus-tests packet, the restored direct kretprobe packet, the shared trace-events side in a narrower posture with a direct formatting companion and older broader companion paths still in the repo-reality-gap bucket, and the `kobject` anchor in a mixed direct-plus-public-tree-backed split packet, same-lane follow-through should stay inside these bounded categories:",
    "Keep the current ten-cue review contract explicit in shared contributor guidance when a bytestream reminder surface is refreshed:",
    "Use the direct sample-plus-tests packet to keep the primary review surfaces visible too: `previewInto()`, `snapshotInto()`, `occupancySummary()`, `writableSpanSummary()`, `visibleSpanSummary()`, and `usesWrappedStorageWindow()`, and the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle should stay easy to find from shared guidance instead of being left implicit in sample-local code only.",
    "Respect the freeze map too.",
)

DOCS_ROOT_REQUIRED_TEXT = (
    "keep the current four-anchor non-runtime sample packet explicit from the docs root instead of letting the shared contributor reminder drift away from the live sample-root, scripts-root, guide, sequencing, checklist, and tests-root packet.",
    "while `samples/zigux/trace_events_string_formatting_sample.zig` stays only the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.",
    "keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.",
    "keep the current `kobject` ownership-and-lifetime split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh reread restores direct authenticated proof for those two routes.",
)

APPROVED_IDIOM_REQUIRED_TEXT = (
    "The roadmap-backed Phase 5 trace-events anchor is still:",
    "Authenticated sample-root readback still directly exposes this bounded non-runtime formatting companion:",
    "Fresh mixed reread on 2026-05-19 keeps the broader non-runtime trace-events sample-local companions in a split state rather than a missing state:",
    "Those paths are again carried by the live trace-events reminder packet and current public-tree-backed reread surfaces, but the authenticated contents route used for this lane still did not return them directly on 2026-05-19.",
    "The shared `zigux/tests/phase5_build.zig` route remains useful support material too, but keep it framed as current public-tree-backed companion evidence until authenticated contents reread returns that path directly again.",
    "Keep the approved formatting idiom bounded to the current landed reminder packet:",
    "That packet should keep the selected-string plus `iter=%d` formatting cue explicit while staying honest about the current split: the bounded formatting companion remains directly readable through the authenticated sample-root route, the broader non-runtime trace-events sample-local companions are visible again through the live public-tree-backed packet but are not yet returned authenticated proof in this lane, the shared `zigux/tests/phase5_build.zig` path is still public-tree-backed companion evidence rather than returned authenticated proof, and `scripts/zigux/check-phase5-review-guide-surface.py` remains the shipped shared guard for that reminder family rather than an optional extra.",
    "Keep the bounded destination discipline explicit in that same reminder packet too: `formatIterationMessageInto(12, [5]u8)` still returns `error.NoSpaceLeft` without advancing the sample stage or `replay_runs`,",
    "while `formatIterationMessageInto(12, [7]u8)` still returns",
    "and keeps the sample in `.initialized`.",
    "Current `master` also still ships no standalone Phase 5 `samples/zigux/*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
    "Keep standalone formatting-helper evidence under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 helper reminders, keep `cmdline`, `argv_split`, and `rbtree` evidence under the bounded Phase 7 helper packet, keep direct bitmap helper reviewability under the closed Phase 1 plus bounded Phase 4 reminder packet, and keep runtime-facing trace-events loader work under the separate Phase 9 lane.",
)

APPROVED_IDIOM_BOUNDARY_MARKERS = (
    "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
    "Do not treat this note as proof of:",
    "- standalone formatting-helper delivery",
    "- standalone broad `*format*` sample delivery",
    "- standalone `printf` parity",
    "- standalone `vsprintf` parity",
    "- standalone string-helper delivery",
    "- standalone `*cmdline*` sample delivery",
    "- standalone `*argv*` sample delivery",
    "- standalone `*rbtree*` sample delivery",
    "- standalone `*bitmap*` sample delivery",
    "- a fifth approved Phase 5 sample",
)

REVIEW_CHECKLIST_REQUIRED_TEXT = (
    "if the change touches the shared Phase 5 sample packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still agree on the current four-anchor reminder packet,",
    "keep `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` explicit as the direct bytestream proof,",
    "keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` explicit as current direct reminder or packet evidence, keep `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` framed as current public-tree-backed companion evidence until a fresh reread proves direct authenticated proof for those two routes again,",
    "keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording,",
    "and keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of the Phase 5 packet?",
)

SCRIPTS_ROOT_REQUIRED_TEXT = (
    "Phase 5 flow - the current scripts-root sample packet stays reviewable through the shipped guide-surface guard, the restored direct bytestream sample-plus-tests packet, the restored direct non-runtime kretprobe packet, the narrower trace-events formatting companion, and the split-readback kobject reminder packet instead of flattening all four roadmap anchors into sample-root-only proof, guide-only prose, or a blanket missing-sample story",
    "`python3 scripts/zigux/check-phase5-review-guide-surface.py --self-test` replays the shipped shared Phase 5 scripts-root reminder guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording",
    "`scripts/zigux/check-phase5-review-guide-surface.py` keeps the current guide-surface packet explicit from the scripts root, and `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that shared non-runtime sample packet",
    "`samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` keep the restored direct bytestream packet explicit from the scripts root, with the ten-cue `reviewContract().focus` packet and the queue-shape cues around `previewInto()`, `snapshotInto()`, `occupancySummary()`, `writableSpanSummary()`, `visibleSpanSummary()`, and `usesWrappedStorageWindow()` staying reviewable without reopening sample behavior in this shared reminder surface",
    "keep the kobject split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those two routes directly again",
    "keep the no-extra-sample boundary explicit from the scripts root too: do not treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence, and do not treat standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` sample claims as landed Phase 5 proof on current `master`",
)

TESTS_ROOT_REQUIRED_TEXT = (
    "Keep the current bounded Phase 5 tests-root reminder packet explicit through `Documentation/zigux/README.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-kobject-sample-survey.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase5-review-guide-surface.py`, and `zigux/tests/README.md`.",
    "Keep `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` explicit as the direct bytestream replay, manifest, and survey packet while `zigux/tests/phase5_build.zig` stays current public-tree-backed companion evidence in this runtime.",
    "Keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording instead of treating the Phase 5 tests-root packet as docs-only guidance.",
    "Keep `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` explicit as the direct non-runtime kretprobe tests-root packet, and keep `samples/zigux/trace_events_string_formatting_sample.zig` framed only as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample. Keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` framed as public-tree-backed companion or repo-reality-gap references until a fresh authenticated reread returns that broader trace-events packet directly again.",
    "Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` and `zigux/tests/phase5_kobject_example_manifest.json` are direct tests-root packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those two routes directly again.",
    "Keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 tests-root packet.",
    "Tests-root reviewer prompt:",
)

LANE_SEQUENCING_REQUIRED_TEXT = (
    "Keep the dedicated scripts-side review-guide guard explicit too: `scripts/zigux/check-phase5-review-guide-surface.py` is the shipped checker for the guide's direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording, so same-lane follow-through should not describe the shared Phase 5 packet as guide-only reminder prose anymore.",
    "Keep shared contributor guidance honest about that mixed tree-visible-versus-authenticated-readback split instead of repeating older split-readback wording, collapsing the packet into repo absence, or overstating fully direct authenticated proof.",
    "The next honest Phase 5 step is another one-file reminder-surface repair that keeps the approved anchors explicit without flattening the narrower trace-events formatting packet, collapsing the still-visible kobject packet into repo absence, or overstating the shared `zigux/tests/phase5_build.zig` route as direct authenticated proof.",
)

SAMPLE_ROOT_REQUIRED_TEXT = (
    "The same mixed reread also kept the roadmap-backed `kobject` packet split explicit in this runtime: authenticated contents readback again directly returned `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`, while fresh public-tree readback still carried `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` as the current companion-evidence pair.",
    "Keep the kobject anchor framed as a roadmap-backed Phase 5 target with the current mixed packet explicit in this runtime: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh authenticated reread returns those two routes directly. Keep shared contributor guidance honest about that split-readback packet instead of repeating the older kobject-reread-needed sample-root wording, collapsing the packet into repo absence, or overstating fully direct authenticated proof.",
    "For the trace-events anchor, current `master` still keeps the direct non-runtime evidence narrowed to the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig` plus the shared reminder packet carried by `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`. Keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` framed as repo-reality-gap, historical-support, or public-tree-backed companion references until a fresh authenticated reread proves they returned directly. Keep the shared `zigux/tests/phase5_build.zig` route framed as current public-tree-backed companion evidence rather than direct authenticated proof.",
)

APPROVED_IDIOM_REQUIRED_PATHS = (
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

BYTESTREAM_CONTRACT_MARKERS = (
    "`bounded_fifo_order`",
    "`wraparound_requeue`",
    "`peek_and_skip`",
    "`non_destructive_snapshot`",
    "`preview_truncation`",
    "`remaining_capacity`",
    "`queue_shape_boundaries`",
    "`helper_boundaries`",
    "`reset_and_replay`",
    "`ownership_and_lifetime`",
)

KOBJECT_CONTRACT_MARKERS = (
    "`runSingleInitBoundaryReplay()` keeps the one-time `init()` rule executable so a second `init()` still returns `InvalidLifecycleTransition` while the sample stays initialized with zero active attributes and `1/0/0` counters",
    "the initialized-but-not-registered zero-active-attributes boundary stays explicit through `runPreRegistrationBoundaryReplay()` instead of dissolving into broader lifecycle prose",
    "`ownershipSummary()` plus sample-owned `runOwnershipReplay()` keep the cold, initialized, registered, and exited snapshots plus the active-attribute-count progression visible from contributor-facing guidance",
    "the unnamed attribute-group shape, shared `baz`/`bar` dispatch, and the registered replay packet stay reviewable without reopening runtime-substrate claims",
    "keep the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit alongside the registered teardown, post-`exit()` rejection, and anchor-replay rejection packet",
)

NO_EXTRA_SAMPLE_MARKERS = (
    "`samples/zigux/trace_events_string_formatting_sample.zig` is a bounded trace-events formatting companion, not a fifth Phase 5 anchor and not a standalone helper packet",
    "there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master` outside the bounded trace-events formatting companion and the shared reminder packet",
    "there is no standalone `samples/zigux/*kasprintf*` Phase 5 reference sample on current `master`",
    "there is no standalone `samples/zigux/*strarray*` Phase 5 reference sample on current `master`",
    "there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`",
    "there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`",
    "there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`",
    "there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`",
    "there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`",
)

FORBIDDEN_TEXT = (
    "Treat `samples/zigux/trace_events_string_formatting_sample.zig` as a returned full trace-events port or a fifth sample.",
    "Treat the whole `kobject` packet as fully direct authenticated proof.",
    "Treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence.",
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _bullet_list(paths: tuple[str, ...]) -> str:
    return "\n".join(f"* `{path}`" for path in paths)


def collect_failures(root: Path) -> list[str]:
    guide = _read(root / GUIDE_PATH)
    docs_root = _read(root / DOCS_ROOT_PATH)
    approved_idiom = _read(root / APPROVED_IDIOM_PATH)
    review_checklist = _read(root / REVIEW_CHECKLIST_PATH)
    scripts_root = _read(root / SCRIPTS_ROOT_PATH)
    tests_root = _read(root / TESTS_ROOT_PATH)
    lane_sequencing = _read(root / LANE_SEQUENCING_PATH)
    sample_root = _read(root / SAMPLE_ROOT_PATH)
    failures: list[str] = []

    for marker in REQUIRED_TEXT:
        if marker not in guide:
            failures.append(f"guide:missing_text:{marker}")

    for marker in DOCS_ROOT_REQUIRED_TEXT:
        if marker not in docs_root:
            failures.append(f"docs_root:missing_text:{marker}")

    for marker in APPROVED_IDIOM_REQUIRED_TEXT:
        if marker not in approved_idiom:
            failures.append(f"approved_idiom:missing_text:{marker}")

    for marker in APPROVED_IDIOM_BOUNDARY_MARKERS:
        if marker not in approved_idiom:
            failures.append(f"approved_idiom:missing_boundary:{marker}")

    for marker in REVIEW_CHECKLIST_REQUIRED_TEXT:
        if marker not in review_checklist:
            failures.append(f"review_checklist:missing_text:{marker}")

    for marker in SCRIPTS_ROOT_REQUIRED_TEXT:
        if marker not in scripts_root:
            failures.append(f"scripts_root:missing_text:{marker}")

    for marker in TESTS_ROOT_REQUIRED_TEXT:
        if marker not in tests_root:
            failures.append(f"tests_root:missing_text:{marker}")

    for marker in LANE_SEQUENCING_REQUIRED_TEXT:
        if marker not in lane_sequencing:
            failures.append(f"lane_sequencing:missing_text:{marker}")

    for marker in SAMPLE_ROOT_REQUIRED_TEXT:
        if marker not in sample_root:
            failures.append(f"sample_root:missing_text:{marker}")

    for marker in BYTESTREAM_CONTRACT_MARKERS:
        if marker not in guide:
            failures.append(f"guide:missing_bytestream_contract:{marker}")

    for marker in KOBJECT_CONTRACT_MARKERS:
        if marker not in guide:
            failures.append(f"guide:missing_kobject_contract:{marker}")

    for marker in NO_EXTRA_SAMPLE_MARKERS:
        if marker not in guide:
            failures.append(f"guide:missing_boundary:{marker}")

    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in guide:
            failures.append(f"guide:missing_direct_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    for rel in KOBJECT_DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in guide:
            failures.append(f"guide:missing_kobject_direct_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_kobject_direct_path:{rel}")

    for rel in KOBJECT_PUBLIC_TREE_PACKET_PATHS:
        if f"`{rel}`" not in guide:
            failures.append(f"guide:missing_public_tree_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_public_tree_path:{rel}")

    for rel in TRACE_EVENTS_COMPANION_GAP_PATHS:
        if f"`{rel}`" not in guide:
            failures.append(f"guide:missing_trace_events_gap_path:`{rel}`")

    for rel in APPROVED_IDIOM_REQUIRED_PATHS:
        if f"`{rel}`" not in approved_idiom:
            failures.append(f"approved_idiom:missing_path:`{rel}`")

    for text in FORBIDDEN_TEXT:
        if text in guide:
            failures.append(f"guide:forbidden_text:{text}")

    return failures


def _sample_guide() -> str:
    sections = [
        "# Phase 5 Sample Review Guide",
        "",
        *REQUIRED_TEXT,
        "",
        _bullet_list(DIRECT_PACKET_PATHS),
        "",
        _bullet_list(KOBJECT_DIRECT_PACKET_PATHS),
        "",
        _bullet_list(KOBJECT_PUBLIC_TREE_PACKET_PATHS),
        "",
        _bullet_list(TRACE_EVENTS_COMPANION_GAP_PATHS),
        "",
        *BYTESTREAM_CONTRACT_MARKERS,
        "",
        *KOBJECT_CONTRACT_MARKERS,
        "",
        *NO_EXTRA_SAMPLE_MARKERS,
        "",
        "Keep later runtime-facing sample work under the separate Phase 9 lane.",
    ]
    return "\n".join(sections) + "\n"


def _sample_docs_root() -> str:
    return "\n".join(("# Zigux Documentation", "", *DOCS_ROOT_REQUIRED_TEXT)) + "\n"


def _sample_approved_idiom_gap() -> str:
    sections = [
        "# Phase 5 Trace-Events Approved Idiom Gap",
        "",
        *APPROVED_IDIOM_REQUIRED_TEXT,
        "",
        _bullet_list(APPROVED_IDIOM_REQUIRED_PATHS),
        "",
        *APPROVED_IDIOM_BOUNDARY_MARKERS,
    ]
    return "\n".join(sections) + "\n"


def _sample_review_checklist() -> str:
    return "\n".join(("# Zigux Review Checklist", "", *REVIEW_CHECKLIST_REQUIRED_TEXT)) + "\n"


def _sample_scripts_root() -> str:
    return "\n".join(("# scripts/zigux", "", *SCRIPTS_ROOT_REQUIRED_TEXT)) + "\n"


def _sample_tests_root() -> str:
    return "\n".join(("# zigux/tests", "", *TESTS_ROOT_REQUIRED_TEXT)) + "\n"


def _sample_lane_sequencing() -> str:
    return "\n".join(("# Phase 5 Sample Lane Sequencing", "", *LANE_SEQUENCING_REQUIRED_TEXT)) + "\n"


def _sample_sample_root() -> str:
    return "\n".join(("# samples/zigux", "", *SAMPLE_ROOT_REQUIRED_TEXT)) + "\n"


def _seed(root: Path) -> None:
    _write(root / GUIDE_PATH, _sample_guide())
    _write(root / DOCS_ROOT_PATH, _sample_docs_root())
    _write(root / APPROVED_IDIOM_PATH, _sample_approved_idiom_gap())
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / SCRIPTS_ROOT_PATH, _sample_scripts_root())
    _write(root / TESTS_ROOT_PATH, _sample_tests_root())
    _write(root / LANE_SEQUENCING_PATH, _sample_lane_sequencing())
    _write(root / SAMPLE_ROOT_PATH, _sample_sample_root())
    for rel in DIRECT_PACKET_PATHS + KOBJECT_DIRECT_PACKET_PATHS + KOBJECT_PUBLIC_TREE_PACKET_PATHS:
        if Path(rel) in {
            GUIDE_PATH,
            DOCS_ROOT_PATH,
            APPROVED_IDIOM_PATH,
            REVIEW_CHECKLIST_PATH,
            SCRIPTS_ROOT_PATH,
            TESTS_ROOT_PATH,
            LANE_SEQUENCING_PATH,
            SAMPLE_ROOT_PATH,
        }:
            continue
        _write(root / rel, "present\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 16
    with tempfile.TemporaryDirectory(prefix="phase5_review_guide_surface_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        checks_run += 1

        missing_direct_marker_root = root / "missing_direct_marker"
        _seed(missing_direct_marker_root)
        _write(
            missing_direct_marker_root / GUIDE_PATH,
            _sample_guide().replace("`zigux/tests/phase5_bytestream_fifo_manifest.json`", "", 1),
        )
        failures = collect_failures(missing_direct_marker_root)
        expected = ["guide:missing_direct_path:`zigux/tests/phase5_bytestream_fifo_manifest.json`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct-marker failure: {failures}")
        checks_run += 1

        missing_public_tree_file_root = root / "missing_public_tree_file"
        _seed(missing_public_tree_file_root)
        (missing_public_tree_file_root / "zigux/tests/phase5_build.zig").unlink()
        failures = collect_failures(missing_public_tree_file_root)
        expected = ["repo:missing_public_tree_path:zigux/tests/phase5_build.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-public-tree-file failure: {failures}")
        checks_run += 1

        missing_bytestream_contract_root = root / "missing_bytestream_contract"
        _seed(missing_bytestream_contract_root)
        _write(
            missing_bytestream_contract_root / GUIDE_PATH,
            _sample_guide().replace(BYTESTREAM_CONTRACT_MARKERS[6], "", 1),
        )
        failures = collect_failures(missing_bytestream_contract_root)
        expected = [f"guide:missing_bytestream_contract:{BYTESTREAM_CONTRACT_MARKERS[6]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-bytestream-contract failure: {failures}")
        checks_run += 1

        missing_kobject_contract_root = root / "missing_kobject_contract"
        _seed(missing_kobject_contract_root)
        _write(
            missing_kobject_contract_root / GUIDE_PATH,
            _sample_guide().replace(KOBJECT_CONTRACT_MARKERS[1], "", 1),
        )
        failures = collect_failures(missing_kobject_contract_root)
        expected = [f"guide:missing_kobject_contract:{KOBJECT_CONTRACT_MARKERS[1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-kobject-contract failure: {failures}")
        checks_run += 1

        missing_boundary_root = root / "missing_boundary"
        _seed(missing_boundary_root)
        _write(
            missing_boundary_root / GUIDE_PATH,
            _sample_guide().replace(NO_EXTRA_SAMPLE_MARKERS[3], "", 1),
        )
        failures = collect_failures(missing_boundary_root)
        expected = [f"guide:missing_boundary:{NO_EXTRA_SAMPLE_MARKERS[3]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-boundary failure: {failures}")
        checks_run += 1

        forbidden_text_root = root / "forbidden_text"
        _seed(forbidden_text_root)
        _write(forbidden_text_root / GUIDE_PATH, _sample_guide() + FORBIDDEN_TEXT[2] + "\n")
        failures = collect_failures(forbidden_text_root)
        expected = [f"guide:forbidden_text:{FORBIDDEN_TEXT[2]}"]
        if failures != expected:
            raise AssertionError(f"unexpected forbidden-text failure: {failures}")
        checks_run += 1

        missing_docs_root_marker_root = root / "missing_docs_root_marker"
        _seed(missing_docs_root_marker_root)
        _write(
            missing_docs_root_marker_root / DOCS_ROOT_PATH,
            _sample_docs_root().replace(DOCS_ROOT_REQUIRED_TEXT[2], "", 1),
        )
        failures = collect_failures(missing_docs_root_marker_root)
        expected = [f"docs_root:missing_text:{DOCS_ROOT_REQUIRED_TEXT[2]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-docs-root-marker failure: {failures}")
        checks_run += 1

        missing_approved_idiom_marker_root = root / "missing_approved_idiom_marker"
        _seed(missing_approved_idiom_marker_root)
        _write(
            missing_approved_idiom_marker_root / APPROVED_IDIOM_PATH,
            _sample_approved_idiom_gap().replace(APPROVED_IDIOM_REQUIRED_TEXT[6], "", 1),
        )
        failures = collect_failures(missing_approved_idiom_marker_root)
        expected = [f"approved_idiom:missing_text:{APPROVED_IDIOM_REQUIRED_TEXT[6]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-approved-idiom-marker failure: {failures}")
        checks_run += 1

        missing_approved_idiom_boundary_root = root / "missing_approved_idiom_boundary"
        _seed(missing_approved_idiom_boundary_root)
        _write(
            missing_approved_idiom_boundary_root / APPROVED_IDIOM_PATH,
            _sample_approved_idiom_gap().replace(APPROVED_IDIOM_BOUNDARY_MARKERS[0], "", 1),
        )
        failures = collect_failures(missing_approved_idiom_boundary_root)
        expected = [f"approved_idiom:missing_boundary:{APPROVED_IDIOM_BOUNDARY_MARKERS[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-approved-idiom-boundary failure: {failures}")
        checks_run += 1

        missing_review_checklist_marker_root = root / "missing_review_checklist_marker"
        _seed(missing_review_checklist_marker_root)
        _write(
            missing_review_checklist_marker_root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(REVIEW_CHECKLIST_REQUIRED_TEXT[3], "", 1),
        )
        failures = collect_failures(missing_review_checklist_marker_root)
        expected = [f"review_checklist:missing_text:{REVIEW_CHECKLIST_REQUIRED_TEXT[3]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-review-checklist-marker failure: {failures}")
        checks_run += 1

        missing_scripts_root_marker_root = root / "missing_scripts_root_marker"
        _seed(missing_scripts_root_marker_root)
        _write(
            missing_scripts_root_marker_root / SCRIPTS_ROOT_PATH,
            _sample_scripts_root().replace(SCRIPTS_ROOT_REQUIRED_TEXT[4], "", 1),
        )
        failures = collect_failures(missing_scripts_root_marker_root)
        expected = [f"scripts_root:missing_text:{SCRIPTS_ROOT_REQUIRED_TEXT[4]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-scripts-root-marker failure: {failures}")
        checks_run += 1

        missing_tests_root_marker_root = root / "missing_tests_root_marker"
        _seed(missing_tests_root_marker_root)
        _write(
            missing_tests_root_marker_root / TESTS_ROOT_PATH,
            _sample_tests_root().replace(TESTS_ROOT_REQUIRED_TEXT[2], "", 1),
        )
        failures = collect_failures(missing_tests_root_marker_root)
        expected = [f"tests_root:missing_text:{TESTS_ROOT_REQUIRED_TEXT[2]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-tests-root-marker failure: {failures}")
        checks_run += 1

        missing_lane_sequencing_marker_root = root / "missing_lane_sequencing_marker"
        _seed(missing_lane_sequencing_marker_root)
        _write(
            missing_lane_sequencing_marker_root / LANE_SEQUENCING_PATH,
            _sample_lane_sequencing().replace(LANE_SEQUENCING_REQUIRED_TEXT[0], "", 1),
        )
        failures = collect_failures(missing_lane_sequencing_marker_root)
        expected = [f"lane_sequencing:missing_text:{LANE_SEQUENCING_REQUIRED_TEXT[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-lane-sequencing-marker failure: {failures}")
        checks_run += 1

        missing_sample_root_marker_root = root / "missing_sample_root_marker"
        _seed(missing_sample_root_marker_root)
        _write(
            missing_sample_root_marker_root / SAMPLE_ROOT_PATH,
            _sample_sample_root().replace(SAMPLE_ROOT_REQUIRED_TEXT[1], "", 1),
        )
        failures = collect_failures(missing_sample_root_marker_root)
        expected = [f"sample_root:missing_text:{SAMPLE_ROOT_REQUIRED_TEXT[1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-sample-root-marker failure: {failures}")
        checks_run += 1

        missing_scripts_root_file = root / "missing_scripts_root_file"
        _seed(missing_scripts_root_file)
        (missing_scripts_root_file / SCRIPTS_ROOT_PATH).unlink()
        try:
            collect_failures(missing_scripts_root_file)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise AssertionError(f"unexpected missing-scripts-root abort: {exc}") from exc
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
        description="Verify that the Phase 5 review guide stays aligned with the current shared sample packet."
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
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_KOBJECT_DIRECT_PACKET_COUNT={len(KOBJECT_DIRECT_PACKET_PATHS)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_PUBLIC_TREE_PACKET_COUNT={len(KOBJECT_PUBLIC_TREE_PACKET_PATHS)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_BYTESTREAM_CONTRACT_COUNT={len(BYTESTREAM_CONTRACT_MARKERS)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_KOBJECT_CONTRACT_COUNT={len(KOBJECT_CONTRACT_MARKERS)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_DOCS_ROOT_REQUIRED_TEXT_COUNT={len(DOCS_ROOT_REQUIRED_TEXT)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_APPROVED_IDIOM_REQUIRED_TEXT_COUNT={len(APPROVED_IDIOM_REQUIRED_TEXT)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_APPROVED_IDIOM_REQUIRED_PATH_COUNT={len(APPROVED_IDIOM_REQUIRED_PATHS)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_APPROVED_IDIOM_BOUNDARY_COUNT={len(APPROVED_IDIOM_BOUNDARY_MARKERS)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_REVIEW_CHECKLIST_REQUIRED_TEXT_COUNT={len(REVIEW_CHECKLIST_REQUIRED_TEXT)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_SCRIPTS_ROOT_REQUIRED_TEXT_COUNT={len(SCRIPTS_ROOT_REQUIRED_TEXT)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_TESTS_ROOT_REQUIRED_TEXT_COUNT={len(TESTS_ROOT_REQUIRED_TEXT)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_LANE_SEQUENCING_REQUIRED_TEXT_COUNT={len(LANE_SEQUENCING_REQUIRED_TEXT)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_SAMPLE_ROOT_REQUIRED_TEXT_COUNT={len(SAMPLE_ROOT_REQUIRED_TEXT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
