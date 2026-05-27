#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

GUIDE_PATH = Path("Documentation/zigux/phase5-sample-review-guide.md")
DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")
APPROVED_IDIOM_PATH = Path("Documentation/zigux/phase5-trace-events-approved-idiom-gap.md")
KOBJECT_SURVEY_PATH = Path("Documentation/zigux/phase5-kobject-sample-survey.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_ROOT_PATH = Path("scripts/zigux/README.md")
TESTS_ROOT_PATH = Path("zigux/tests/README.md")
LANE_SEQUENCING_PATH = Path("Documentation/zigux/phase5-sample-lane-sequencing.md")
SAMPLE_ROOT_PATH = Path("samples/zigux/README.md")

DIRECT_PACKET_PATHS = (
    "Documentation/zigux/phase5-kfifo-sample-survey.md",
    "Documentation/zigux/phase5-kretprobe-sample-survey.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-trace-events-approved-idiom-gap.md",
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "samples/zigux/bytestream_fifo.zig",
    "samples/zigux/bytestream_fifo_window_contract.zig",
    "samples/zigux/kobject_example.zig",
    "samples/zigux/kobject_example_attr_group_contract.zig",
    "samples/zigux/kretprobe_example.zig",
    "samples/zigux/kretprobe_example_instance_budget_contract.zig",
    "samples/zigux/kretprobe_example_probe_spec.zig",
    "samples/zigux/trace_events_callback_focus_contract.zig",
    "samples/zigux/trace_events_string_formatting_sample.zig",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase5-review-guide-surface.py",
    "zigux/tests/README.md",
    "zigux/tests/phase5_bytestream_fifo.zig",
    "zigux/tests/phase5_bytestream_fifo_manifest.json",
    "zigux/tests/phase5_bytestream_fifo_survey.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_kretprobe_example.zig",
    "zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig",
    "zigux/tests/phase5_kretprobe_example_manifest.json",
    "zigux/tests/phase5_kretprobe_example_probe_spec.zig",
    "zigux/tests/phase5_kretprobe_example_survey.zig",
    "zigux/tests/phase5_build.zig",
)

PUBLIC_TREE_COMPANION_PATHS = (
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "zigux/tests/phase5_kobject_example_manifest.json",
    "zigux/tests/phase5_kobject_example_survey.zig",
    "samples/zigux/trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample_manifest.json",
    "zigux/tests/phase5_trace_events_sample_survey.zig",
)

KOBJECT_DIRECT_PACKET_PATHS = (
    "samples/zigux/kobject_example_attr_group_contract.zig",
    "zigux/tests/phase5_kobject_attr_group_contract.zig",
    "zigux/tests/phase5_kobject_attr_group_contract_survey.zig",
)

MARKERS = {
    GUIDE_PATH: (
        "Treat those four anchors as the approved Phase 5 destination set unless the roadmap changes.",
        "The same authenticated route also directly returns the shared build-route companion `zigux/tests/phase5_build.zig` for this packet.",
        "Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample, and it still ships no standalone broad `*format*` Phase 5 reference sample outside the bounded trace-events cues carried by `samples/zigux/trace_events_string_formatting_sample.zig` and the shared reminder packet.",
        "Keep the direct validation routes explicit in that same guidance too: `zig test samples/zigux/bytestream_fifo.zig`, `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig`, and `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` stay visible as the sample-owned self-check route, the focused replay route, and the survey-packet guard, while the shared `zigux/tests/phase5_build.zig` line stays visible as current directly readable shared build-route companion evidence for this bytestream packet rather than as sample-local proof.",
        "keep the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit alongside the registered teardown, post-`exit()` rejection, and anchor-replay rejection packet",
        "Fresh 2026-05-20 follow-up reread also keeps the current direct packet shape explicit: `samples/zigux/bytestream_fifo.zig` now carries four in-file self-checks, `zigux/tests/phase5_bytestream_fifo.zig` keeps five focused replay tests, and `zigux/tests/phase5_bytestream_fifo_survey.zig` keeps five survey-packet checks aligned with the survey note and manifest.",
        "`zig test samples/zigux/kobject_example_attr_group_contract.zig` stays the companion-only validation route for the attr-group contract while `zigux/tests/phase5_build.zig` remains the directly readable shared build-route companion for this packet",
        "`samples/zigux/trace_events_callback_focus_contract.zig` keeps the shared `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` `checked_focus` order plus the callback-registration recovery cues explicit at the sample root without turning that companion into a fifth Phase 5 sample.",
        "`samples/zigux/kretprobe_example_probe_spec.zig` plus `zigux/tests/phase5_kretprobe_example_probe_spec.zig` keep the direct Linux anchor path, default symbol, one-word private-data width, default `maxactive`, replay return and duration summary, missed-instance cue, and the pre-init-only symbol-selection and maxactive-tuning rules explicit beside the main replay packet instead of leaving that probe-spec reviewability trapped in the dedicated survey note alone",
    ),
    DOCS_ROOT_PATH: (
        "keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.",
        "keep the bounded `kobject` attr-group companion explicit here too: `samples/zigux/kobject_example_attr_group_contract.zig` is current direct sample-root evidence for the `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, and NULL-terminated attribute-list slot rather than a fifth Phase 5 sample family.",
        "keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the current `kobject` anchor split explicit instead of falling back to older repo-reality-gap wording.",
        "keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.",
        "keep the current `kobject` ownership-and-lifetime split explicit too: `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are current direct reminder or packet evidence again, while `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` stay public-tree-backed companion evidence until a fresh authenticated reread restores direct proof for those three routes.",
    ),
    APPROVED_IDIOM_PATH: (
        "Keep the approved formatting idiom bounded to the current landed reminder packet:",
        "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
        "Keep the sample-owned review contract explicit too: the bounded formatting companion now centralizes the exact `checked_focus` order `string_selection,formatted_message,bounded_destination_discipline,non_allocating_runtime_safe`, and the approved-idiom reminder should preserve that same reading order beside the selected-string slot and `iter=%d` cue instead of reducing the trace-events packet to message text alone.",
        "Keep the bounded destination discipline explicit in that same reminder packet too: `formatIterationMessageInto(12, [5]u8)` still returns `error.NoSpaceLeft` without advancing the sample stage or `replay_runs`, while `formatIterationMessageInto(12, [7]u8)` still returns `\"iter=12\"` and keeps the sample in `.initialized`.",
        "Keep the direct modulo-selected cycle explicit too: `runStringFormattingCycleReplay()` now walks all five selected strings through the bounded `iter=%d` formatter while keeping the companion in `.initialized` and leaving `replay_runs` unchanged.",
        "Keep the selected-string iteration companion explicit too: `formatSelectedIterationMessageInto(3, [12]u8)` still returns `\"Frodo iter=3\"` while keeping the sample in `.initialized`, so the approved-idiom note must preserve the selected-string-plus-iteration wording instead of reducing the packet to the bare `iter=%d` formatter.",
        "The same authenticated sample-root reread now directly exposes this bounded callback-focus companion too:",
        "## Exact checks run on 2026-05-20",
        "This run verified the current formatting companion with the attached Zig toolchain `0.17.0-dev.87+9b177a7d2` using a focused `zig test` against the current `master` file body.",
        "The exact checks that passed were:",
        "- `phase 5 trace-events formatting companion keeps the selected-string cue reviewable`",
        "- `phase 5 trace-events formatting companion keeps the modulo-selected string cycle reviewable`",
        "- `phase 5 trace-events formatting companion keeps lifecycle boundaries explicit`",
        "- `phase 5 trace-events formatting companion keeps bounded destination failures explicit`",
        "This survey note is directly readable again on current `master` and should stay grouped with the shared reminder packet rather than with the still-split sample-local companion set:",
    ),
    KOBJECT_SURVEY_PATH: (
        "`samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` together keep the bounded `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, NULL-terminated attribute-list slot, and shared build-route linkage explicit rather than turning that companion into a fifth Phase 5 sample",
        "`zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` stays the focused replay route for the same attr-group packet",
        "`zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` stays the survey-guard route that checks the companion, focused replay, and shared build-route markers together",
    ),
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the shared Phase 5 sample packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-kobject-sample-survey.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/check-phase5-review-guide-surface.py`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still agree on the current four-anchor reminder packet,",
        "keep `samples/zigux/trace_events_string_formatting_sample.zig` framed only as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample,",
        "keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording,",
        "keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` explicit as the current direct reminder or replay surfaces in this runtime, keep `samples/zigux/kobject_example.zig` framed as the current shared-reminder-backed owner path, keep `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` framed as current public-tree-backed companion evidence until a fresh reread proves broader direct authenticated proof again,",
    ),
    SCRIPTS_ROOT_PATH: (
        "`python3 scripts/zigux/check-phase5-review-guide-surface.py --self-test` replays the shipped shared Phase 5 scripts-root reminder guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording",
        "keep the current kobject split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the direct reminder or replay surfaces in this runtime, while `samples/zigux/kobject_example.zig` remains the current shared-reminder-backed owner path and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again",
        "keep the bytestream build split explicit too: `zigux/tests/phase5_build.zig` is current directly readable shared build-route companion evidence for this scripts-root packet rather than public-tree-backed support or sample-local proof",
        "keep the no-extra-sample boundary explicit from the scripts root too: do not treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence, and do not treat standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 scripts-root packet.",
    ),
    TESTS_ROOT_PATH: (
        "Keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording instead of treating the Phase 5 tests-root packet as docs-only guidance.",
        "Keep `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` explicit as the direct bytestream replay, manifest, and survey packet while `zigux/tests/phase5_build.zig` stays current directly readable shared build-route companion evidence in this runtime.",
        "Keep `Documentation/zigux/phase5-trace-events-sample-survey.md` explicit with the shared Phase 5 reminder packet as the directly readable survey note for that anchor, while `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` stay framed as public-tree-backed companion or repo-reality-gap references until a fresh authenticated reread returns that broader four-file trace-events packet directly again.",
        "Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` is direct tests-root packet evidence again, `samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract plus the shared `0664`, unnamed-group, and NULL-terminated attribute-list cues, keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet, while `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those routes directly again.",
        "Keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 tests-root packet.",
    ),
    LANE_SEQUENCING_PATH: (
        "Keep the dedicated scripts-side review-guide guard explicit too: `scripts/zigux/check-phase5-review-guide-surface.py` is the shipped checker for the guide's direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording, so same-lane follow-through should not describe the shared Phase 5 packet as guide-only reminder prose anymore.",
        "Treat `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` as the current direct reminder or replay surfaces inside the mixed kobject packet recorded by `Documentation/zigux/phase5-kobject-sample-survey.md`, while `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain the public-tree-backed owner-plus-companion set in this runtime.",
        "Keep `samples/zigux/kobject_example_attr_group_contract.zig` explicit as direct current sample-root evidence for the bounded kobject attr-group companion rather than leaving that shipped reviewability file outside the sample-root inventory.",
        "Treat `samples/zigux/trace_events_string_formatting_sample.zig` as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.",
        "the current trace-events packet split: the bounded formatting companion stays directly readable through `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, and the shared Phase 5 reminder surfaces; authenticated contents reread in this run also directly returned `zigux/tests/phase5_build.zig`; the broader sample-local companions `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` still depend on fresh public GitHub blob or tree fallback in this runtime, so keep those four broader trace-events companions explicit as public-tree-backed or shared-reminder evidence rather than direct authenticated proof, and keep the returned `zigux/tests/phase5_build.zig` route framed separately as the shared rerun handle rather than sample-local proof",
        "Keep the returned runtime bitmap reminder packet separate too: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` are current direct sample-root evidence for the separate Phase 9 runtime bitmap family, not extra Phase 5 sample proof.",
        "Keep `samples/zigux/kretprobe_example_instance_budget_contract.zig` and `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig` explicit too as the current direct sample-root companion and focused replay for the bounded kretprobe instance-budget packet, so the shared lane note reflects that shipped reviewability surface already on `master`.",
        "there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`",
        "Keep `phase5-kobject-example-sample-selfcheck` explicit too as the named shared `zigux/tests/phase5_build.zig` step that reruns the sample-owned `zig test samples/zigux/kobject_example.zig` self-check, so contributor guidance does not leave that owner-side rerun handle buried in the build wiring alone.",
    ),
    SAMPLE_ROOT_PATH: (
        "Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the current direct reminder or replay surfaces, while `samples/zigux/kobject_example.zig` remains the current shared-reminder-backed owner path and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again.",
        "Current `master` also ships `samples/zigux/kobject_example_attr_group_contract.zig` as a bounded kobject companion. Keep that file framed as reviewability help for the current `foo`/`baz`/`bar` attribute-group contract, `0664` modes, unnamed-group cue, and NULL-terminated attribute-list slot rather than as a fifth Phase 5 sample family.",
        "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.",
        "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here. Keep that formatting boundary tied to `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` and the bounded `samples/zigux/trace_events_string_formatting_sample.zig` companion.",
        "* `samples/zigux/trace_events_callback_focus_contract.zig` keeps the shared `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` focus order explicit as trace-events reviewability help at the sample root rather than as a separate Phase 5 sample family",
        "* `*kasprintf*`\n* `*strarray*`",
        "* `*rbtree*`",
        "Keep `zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` explicit as the focused replay route for that bounded attr-group packet, and keep `zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` explicit as the survey-guard route that checks the companion, focused replay, and shared build-route markers together while `zigux/tests/phase5_build.zig` stays the current directly readable shared build-route companion for the broader kobject packet.",
    ),
}

FORBIDDEN_GUIDE_TEXT = (
    "Treat `samples/zigux/trace_events_string_formatting_sample.zig` as a returned full trace-events port or a fifth sample.",
    "Treat the whole `kobject` packet as fully direct authenticated proof.",
    "Treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence.",
)

FORBIDDEN_SAMPLE_ROOT_TEXT = (
    "Keep the kobject anchor framed as a roadmap-backed Phase 5 target with the current mixed packet explicit in this runtime:",
)


def read_text(root: Path, path: Path) -> str:
    return (root / path).read_text(encoding="utf-8")


def write_text(root: Path, path: Path, text: str) -> None:
    full_path = root / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(text, encoding="utf-8")


def placeholder(path: Path) -> str:
    lines = [f"# {path.name}"]
    lines.extend(MARKERS[path])
    if path == GUIDE_PATH:
        lines.extend(f"`{rel}`" for rel in DIRECT_PACKET_PATHS)
        lines.extend(f"`{rel}`" for rel in PUBLIC_TREE_COMPANION_PATHS)
    if path == KOBJECT_SURVEY_PATH:
        lines.extend(f"`{rel}`" for rel in KOBJECT_DIRECT_PACKET_PATHS)
    if path == APPROVED_IDIOM_PATH:
        lines.extend(
            f"`{rel}`"
            for rel in (
                "samples/trace_events/trace-events-sample.c",
                "samples/zigux/trace_events_string_formatting_sample.zig",
                "samples/zigux/trace_events_callback_focus_contract.zig",
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


def strip_standalone_path(text: str, rel: str) -> str:
    standalone = f"\n\n`{rel}`"
    if standalone in text:
        return text.replace(standalone, "", 1)
    return text


def seed(root: Path) -> None:
    tracked = set(MARKERS)
    for path in MARKERS:
        write_text(root, path, placeholder(path))
    for rel in DIRECT_PACKET_PATHS + PUBLIC_TREE_COMPANION_PATHS + KOBJECT_DIRECT_PACKET_PATHS + (
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
    kobject_survey = texts[KOBJECT_SURVEY_PATH]
    sample_root = texts[SAMPLE_ROOT_PATH]
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
    for rel in KOBJECT_DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in kobject_survey and rel not in kobject_survey:
            failures.append(f"kobject_survey:missing_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_path:{rel}")
    for rel in (
        "samples/trace_events/trace-events-sample.c",
        "samples/zigux/trace_events_string_formatting_sample.zig",
        "samples/zigux/trace_events_callback_focus_contract.zig",
        "zigux/tests/phase5_build.zig",
    ):
        if all(token not in approved for token in (f"`{rel}`", rel)):
            failures.append(f"approved_idiom:missing_path:{rel}")
    for forbidden in FORBIDDEN_GUIDE_TEXT:
        if forbidden in guide:
            failures.append(f"guide:forbidden_text:{forbidden}")
    for forbidden in FORBIDDEN_SAMPLE_ROOT_TEXT:
        if forbidden in sample_root:
            failures.append(f"sample_root:forbidden_text:{forbidden}")
    return failures


def expect_exact(label: str, failures: list[str], expected: list[str]) -> None:
    if failures != expected:
        raise AssertionError(f"{label}: expected {expected}, got {failures}")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 48
    with tempfile.TemporaryDirectory(prefix="phase5_review_guide_surface_") as tmpdir:
        root = Path(tmpdir)
        seed(root)
        expect_exact("baseline", collect_failures(root), [])
        checks_run += 1
        mutated = root / "missing_guide_validation_marker"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, placeholder(GUIDE_PATH).replace(MARKERS[GUIDE_PATH][3], ""))
        expect_exact("missing guide validation marker", collect_failures(mutated), [f"{GUIDE_PATH}:missing_text:{MARKERS[GUIDE_PATH][3]}"])
        checks_run += 1
        mutated = root / "missing_docs_root_marker"
        seed(mutated)
        write_text(mutated, DOCS_ROOT_PATH, placeholder(DOCS_ROOT_PATH).replace(MARKERS[DOCS_ROOT_PATH][1], ""))
        expect_exact("missing docs-root marker", collect_failures(mutated), [f"{DOCS_ROOT_PATH}:missing_text:{MARKERS[DOCS_ROOT_PATH][1]}"])
        checks_run += 1
        mutated = root / "missing_docs_root_kobject_split_marker"
        seed(mutated)
        write_text(mutated, DOCS_ROOT_PATH, placeholder(DOCS_ROOT_PATH).replace(MARKERS[DOCS_ROOT_PATH][4], ""))
        expect_exact("missing docs-root kobject split marker", collect_failures(mutated), [f"{DOCS_ROOT_PATH}:missing_text:{MARKERS[DOCS_ROOT_PATH][4]}"])
        checks_run += 1
        mutated = root / "missing_approved_idiom_marker"
        seed(mutated)
        write_text(mutated, APPROVED_IDIOM_PATH, placeholder(APPROVED_IDIOM_PATH).replace(MARKERS[APPROVED_IDIOM_PATH][2], ""))
        expect_exact("missing approved idiom marker", collect_failures(mutated), [f"{APPROVED_IDIOM_PATH}:missing_text:{MARKERS[APPROVED_IDIOM_PATH][2]}"])
        checks_run += 1
        mutated = root / "missing_approved_selected_iteration_marker"
        seed(mutated)
        write_text(mutated, APPROVED_IDIOM_PATH, placeholder(APPROVED_IDIOM_PATH).replace(MARKERS[APPROVED_IDIOM_PATH][5], ""))
        expect_exact("missing approved selected iteration marker", collect_failures(mutated), [f"{APPROVED_IDIOM_PATH}:missing_text:{MARKERS[APPROVED_IDIOM_PATH][5]}"])
        checks_run += 1
        mutated = root / "missing_approved_callback_focus_marker"
        seed(mutated)
        write_text(mutated, APPROVED_IDIOM_PATH, placeholder(APPROVED_IDIOM_PATH).replace(MARKERS[APPROVED_IDIOM_PATH][6], ""))
        expect_exact("missing approved callback-focus marker", collect_failures(mutated), [f"{APPROVED_IDIOM_PATH}:missing_text:{MARKERS[APPROVED_IDIOM_PATH][6]}"])
        checks_run += 1
        mutated = root / "missing_kobject_survey_marker"
        seed(mutated)
        write_text(mutated, KOBJECT_SURVEY_PATH, placeholder(KOBJECT_SURVEY_PATH).replace(MARKERS[KOBJECT_SURVEY_PATH][1], ""))
        expect_exact("missing kobject survey marker", collect_failures(mutated), [f"{KOBJECT_SURVEY_PATH}:missing_text:{MARKERS[KOBJECT_SURVEY_PATH][1]}"])
        checks_run += 1
        mutated = root / "missing_review_checklist_marker"
        seed(mutated)
        write_text(mutated, REVIEW_CHECKLIST_PATH, placeholder(REVIEW_CHECKLIST_PATH).replace(MARKERS[REVIEW_CHECKLIST_PATH][2], ""))
        expect_exact("missing review checklist marker", collect_failures(mutated), [f"{REVIEW_CHECKLIST_PATH}:missing_text:{MARKERS[REVIEW_CHECKLIST_PATH][2]}"])
        checks_run += 1
        mutated = root / "missing_review_checklist_trace_events_marker"
        seed(mutated)
        write_text(mutated, REVIEW_CHECKLIST_PATH, placeholder(REVIEW_CHECKLIST_PATH).replace(MARKERS[REVIEW_CHECKLIST_PATH][1], ""))
        expect_exact("missing review checklist trace-events marker", collect_failures(mutated), [f"{REVIEW_CHECKLIST_PATH}:missing_text:{MARKERS[REVIEW_CHECKLIST_PATH][1]}"])
        checks_run += 1
        mutated = root / "missing_scripts_root_marker"
        seed(mutated)
        write_text(mutated, SCRIPTS_ROOT_PATH, placeholder(SCRIPTS_ROOT_PATH).replace(MARKERS[SCRIPTS_ROOT_PATH][3], ""))
        expect_exact("missing scripts-root marker", collect_failures(mutated), [f"{SCRIPTS_ROOT_PATH}:missing_text:{MARKERS[SCRIPTS_ROOT_PATH][3]}"])
        checks_run += 1
        mutated = root / "missing_tests_root_marker"
        seed(mutated)
        write_text(mutated, TESTS_ROOT_PATH, placeholder(TESTS_ROOT_PATH).replace(MARKERS[TESTS_ROOT_PATH][4], ""))
        expect_exact("missing tests-root marker", collect_failures(mutated), [f"{TESTS_ROOT_PATH}:missing_text:{MARKERS[TESTS_ROOT_PATH][4]}"])
        checks_run += 1
        mutated = root / "missing_lane_sequencing_marker"
        seed(mutated)
        write_text(mutated, LANE_SEQUENCING_PATH, placeholder(LANE_SEQUENCING_PATH).replace(MARKERS[LANE_SEQUENCING_PATH][5], ""))
        expect_exact("missing lane sequencing marker", collect_failures(mutated), [f"{LANE_SEQUENCING_PATH}:missing_text:{MARKERS[LANE_SEQUENCING_PATH][5]}"])
        checks_run += 1
        mutated = root / "missing_lane_sequencing_kretprobe_companion_marker"
        seed(mutated)
        write_text(mutated, LANE_SEQUENCING_PATH, placeholder(LANE_SEQUENCING_PATH).replace(MARKERS[LANE_SEQUENCING_PATH][6], ""))
        expect_exact("missing lane sequencing kretprobe companion marker", collect_failures(mutated), [f"{LANE_SEQUENCING_PATH}:missing_text:{MARKERS[LANE_SEQUENCING_PATH][6]}"])
        checks_run += 1
        mutated = root / "missing_lane_sequencing_rbtree_boundary_marker"
        seed(mutated)
        write_text(mutated, LANE_SEQUENCING_PATH, placeholder(LANE_SEQUENCING_PATH).replace(MARKERS[LANE_SEQUENCING_PATH][7], ""))
        expect_exact("missing lane sequencing rbtree boundary marker", collect_failures(mutated), [f"{LANE_SEQUENCING_PATH}:missing_text:{MARKERS[LANE_SEQUENCING_PATH][7]}"])
        checks_run += 1
        mutated = root / "missing_sample_root_marker"
        seed(mutated)
        write_text(mutated, SAMPLE_ROOT_PATH, placeholder(SAMPLE_ROOT_PATH).replace(MARKERS[SAMPLE_ROOT_PATH][6], ""))
        expect_exact("missing sample-root marker", collect_failures(mutated), [f"{SAMPLE_ROOT_PATH}:missing_text:{MARKERS[SAMPLE_ROOT_PATH][6]}"])
        checks_run += 1
        mutated = root / "missing_guide_trace_callback_marker"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, placeholder(GUIDE_PATH).replace(MARKERS[GUIDE_PATH][7], ""))
        expect_exact("missing guide trace callback marker", collect_failures(mutated), [f"{GUIDE_PATH}:missing_text:{MARKERS[GUIDE_PATH][7]}"])
        checks_run += 1
        mutated = root / "missing_guide_kretprobe_probe_spec_marker"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, placeholder(GUIDE_PATH).replace(MARKERS[GUIDE_PATH][8], ""))
        expect_exact("missing guide kretprobe probe-spec marker", collect_failures(mutated), [f"{GUIDE_PATH}:missing_text:{MARKERS[GUIDE_PATH][8]}"])
        checks_run += 1
        mutated = root / "missing_guide_kretprobe_instance_budget_path"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, strip_standalone_path(placeholder(GUIDE_PATH), "samples/zigux/kretprobe_example_instance_budget_contract.zig"))
        expect_exact("missing guide kretprobe instance-budget path", collect_failures(mutated), ["guide:missing_path:samples/zigux/kretprobe_example_instance_budget_contract.zig"])
        checks_run += 1
        mutated = root / "missing_sample_root_trace_callback_marker"
        seed(mutated)
        write_text(mutated, SAMPLE_ROOT_PATH, placeholder(SAMPLE_ROOT_PATH).replace(MARKERS[SAMPLE_ROOT_PATH][4], ""))
        expect_exact("missing sample-root trace callback marker", collect_failures(mutated), [f"{SAMPLE_ROOT_PATH}:missing_text:{MARKERS[SAMPLE_ROOT_PATH][4]}"])
        checks_run += 1
        mutated = root / "missing_direct_packet_path"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, strip_standalone_path(placeholder(GUIDE_PATH), "Documentation/zigux/phase5-kfifo-sample-survey.md"))
        expect_exact("missing direct packet path", collect_failures(mutated), ["guide:missing_path:Documentation/zigux/phase5-kfifo-sample-survey.md"])
        checks_run += 1
        mutated = root / "missing_companion_path"
        seed(mutated)
        approved_text = strip_standalone_path(placeholder(APPROVED_IDIOM_PATH), "samples/zigux/trace_events_sample.zig")
        guide_text = strip_standalone_path(placeholder(GUIDE_PATH), "samples/zigux/trace_events_sample.zig")
        write_text(mutated, APPROVED_IDIOM_PATH, approved_text)
        write_text(mutated, GUIDE_PATH, guide_text)
        expect_exact("missing companion path", collect_failures(mutated), ["packet:missing_companion_path:samples/zigux/trace_events_sample.zig"])
        checks_run += 1
        mutated = root / "missing_kobject_direct_path"
        seed(mutated)
        write_text(mutated, KOBJECT_SURVEY_PATH, placeholder(KOBJECT_SURVEY_PATH).replace("zigux/tests/phase5_kobject_attr_group_contract_survey.zig", ""))
        expect_exact("missing kobject direct path", collect_failures(mutated), [f"{KOBJECT_SURVEY_PATH}:missing_text:{MARKERS[KOBJECT_SURVEY_PATH][0]}", f"{KOBJECT_SURVEY_PATH}:missing_text:{MARKERS[KOBJECT_SURVEY_PATH][2]}", "kobject_survey:missing_path:zigux/tests/phase5_kobject_attr_group_contract_survey.zig"])
        checks_run += 1
        mutated = root / "missing_approved_anchor_path"
        seed(mutated)
        write_text(mutated, APPROVED_IDIOM_PATH, placeholder(APPROVED_IDIOM_PATH).replace("`samples/trace_events/trace-events-sample.c`", ""))
        expect_exact("missing approved anchor path", collect_failures(mutated), ["approved_idiom:missing_path:samples/trace_events/trace-events-sample.c"])
        checks_run += 1
        mutated = root / "missing_direct_repo_path"
        seed(mutated)
        (mutated / "samples/zigux/bytestream_fifo.zig").unlink()
        expect_exact("missing direct repo path", collect_failures(mutated), ["repo:missing_path:samples/zigux/bytestream_fifo.zig"])
        checks_run += 1
        mutated = root / "missing_companion_repo_path"
        seed(mutated)
        (mutated / "samples/zigux/trace_events_sample.zig").unlink()
        expect_exact("missing companion repo path", collect_failures(mutated), ["repo:missing_companion_path:samples/zigux/trace_events_sample.zig"])
        checks_run += 1
        mutated = root / "missing_kobject_repo_path"
        seed(mutated)
        (mutated / "zigux/tests/phase5_kobject_attr_group_contract_survey.zig").unlink()
        expect_exact("missing kobject repo path", collect_failures(mutated), ["repo:missing_path:zigux/tests/phase5_kobject_attr_group_contract_survey.zig"])
        checks_run += 1
        mutated = root / "forbidden_full_trace_events_claim"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, placeholder(GUIDE_PATH) + FORBIDDEN_GUIDE_TEXT[0] + "\n")
        expect_exact("forbidden full trace-events claim", collect_failures(mutated), [f"guide:forbidden_text:{FORBIDDEN_GUIDE_TEXT[0]}"])
        checks_run += 1
        mutated = root / "forbidden_full_kobject_claim"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, placeholder(GUIDE_PATH) + FORBIDDEN_GUIDE_TEXT[1] + "\n")
        expect_exact("forbidden full kobject claim", collect_failures(mutated), [f"guide:forbidden_text:{FORBIDDEN_GUIDE_TEXT[1]}"])
        checks_run += 1
        mutated = root / "forbidden_runtime_phase5_claim"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, placeholder(GUIDE_PATH) + FORBIDDEN_GUIDE_TEXT[2] + "\n")
        expect_exact("forbidden runtime-as-phase5 claim", collect_failures(mutated), [f"guide:forbidden_text:{FORBIDDEN_GUIDE_TEXT[2]}"])
        checks_run += 1
        mutated = root / "forbidden_sample_root_kobject_inversion"
        seed(mutated)
        write_text(mutated, SAMPLE_ROOT_PATH, placeholder(SAMPLE_ROOT_PATH) + FORBIDDEN_SAMPLE_ROOT_TEXT[0] + "\n")
        expect_exact("forbidden sample-root kobject inversion", collect_failures(mutated), [f"sample_root:forbidden_text:{FORBIDDEN_SAMPLE_ROOT_TEXT[0]}"])
        checks_run += 1
        mutated = root / "guide_allows_public_tree_companion_reference"
        seed(mutated)
        custom = placeholder(GUIDE_PATH).replace("`samples/zigux/trace_events_sample.zig`", "samples/zigux/trace_events_sample.zig")
        write_text(mutated, GUIDE_PATH, custom)
        expect_exact("guide allows plain companion reference", collect_failures(mutated), [])
        checks_run += 1
        mutated = root / "approved_allows_plain_anchor_reference"
        seed(mutated)
        custom = strip_standalone_path(placeholder(APPROVED_IDIOM_PATH), "zigux/tests/phase5_build.zig") + "\n\nzigux/tests/phase5_build.zig"
        write_text(mutated, APPROVED_IDIOM_PATH, custom)
        expect_exact("approved allows plain anchor reference", collect_failures(mutated), [])
        checks_run += 1
        mutated = root / "kobject_survey_allows_plain_direct_reference"
        seed(mutated)
        custom = strip_standalone_path(placeholder(KOBJECT_SURVEY_PATH), "zigux/tests/phase5_kobject_attr_group_contract.zig") + "\n\nzigux/tests/phase5_kobject_attr_group_contract.zig"
        write_text(mutated, KOBJECT_SURVEY_PATH, custom)
        expect_exact("kobject survey allows plain direct reference", collect_failures(mutated), [])
        checks_run += 1
        mutated = root / "missing_phase5_build_in_approved"
        seed(mutated)
        write_text(mutated, APPROVED_IDIOM_PATH, strip_standalone_path(placeholder(APPROVED_IDIOM_PATH), "zigux/tests/phase5_build.zig"))
        expect_exact("missing phase5 build in approved idiom", collect_failures(mutated), ["approved_idiom:missing_path:zigux/tests/phase5_build.zig"])
        checks_run += 1
        mutated = root / "missing_trace_formatting_companion_in_approved"
        seed(mutated)
        write_text(mutated, APPROVED_IDIOM_PATH, strip_standalone_path(placeholder(APPROVED_IDIOM_PATH), "samples/zigux/trace_events_string_formatting_sample.zig"))
        expect_exact("missing trace formatting companion in approved idiom", collect_failures(mutated), ["approved_idiom:missing_path:samples/zigux/trace_events_string_formatting_sample.zig"])
        checks_run += 1
        mutated = root / "missing_trace_callback_focus_companion_in_approved"
        seed(mutated)
        write_text(mutated, APPROVED_IDIOM_PATH, strip_standalone_path(placeholder(APPROVED_IDIOM_PATH), "samples/zigux/trace_events_callback_focus_contract.zig"))
        expect_exact("missing trace callback-focus companion in approved idiom", collect_failures(mutated), ["approved_idiom:missing_path:samples/zigux/trace_events_callback_focus_contract.zig"])
        checks_run += 1
        mutated = root / "missing_public_tree_companion_repo_path"
        seed(mutated)
        (mutated / "zigux/tests/phase5_kobject_example_manifest.json").unlink()
        expect_exact("missing public-tree companion repo path", collect_failures(mutated), ["repo:missing_companion_path:zigux/tests/phase5_kobject_example_manifest.json"])
        checks_run += 1
        mutated = root / "missing_direct_docs_path_from_guide"
        seed(mutated)
        write_text(mutated, GUIDE_PATH, strip_standalone_path(placeholder(GUIDE_PATH), "Documentation/zigux/phase5-kretprobe-sample-survey.md"))
        expect_exact("missing direct docs path from guide", collect_failures(mutated), ["guide:missing_path:Documentation/zigux/phase5-kretprobe-sample-survey.md"])
        checks_run += 1
        mutated = root / "missing_kobject_attr_replay_repo_path"
        seed(mutated)
        (mutated / "zigux/tests/phase5_kobject_attr_group_contract.zig").unlink()
        expect_exact("missing kobject attr replay repo path", collect_failures(mutated), ["repo:missing_path:zigux/tests/phase5_kobject_attr_group_contract.zig"])
        checks_run += 1
        mutated = root / "missing_trace_companion_manifest_repo_path"
        seed(mutated)
        (mutated / "zigux/tests/phase5_trace_events_sample_manifest.json").unlink()
        expect_exact("missing trace companion manifest repo path", collect_failures(mutated), ["repo:missing_companion_path:zigux/tests/phase5_trace_events_sample_manifest.json"])
        checks_run += 1
        mutated = root / "docs_root_allows_extra_context_line"
        seed(mutated)
        write_text(mutated, DOCS_ROOT_PATH, placeholder(DOCS_ROOT_PATH) + "\nSupporting note: keep Phase 5 shared reminder wording aligned with the shipped sample packet.\n")
        expect_exact("docs root allows extra context line", collect_failures(mutated), [])
        checks_run += 1
        mutated = root / "missing_sample_root_attr_guard_marker"
        seed(mutated)
        write_text(mutated, SAMPLE_ROOT_PATH, placeholder(SAMPLE_ROOT_PATH).replace(MARKERS[SAMPLE_ROOT_PATH][5], ""))
        expect_exact("missing sample root attr guard marker", collect_failures(mutated), [f"{SAMPLE_ROOT_PATH}:missing_text:{MARKERS[SAMPLE_ROOT_PATH][5]}"])
        checks_run += 1
        mutated = root / "missing_tests_root_kobject_split_marker"
        seed(mutated)
        write_text(mutated, TESTS_ROOT_PATH, placeholder(TESTS_ROOT_PATH).replace(MARKERS[TESTS_ROOT_PATH][3], ""))
        expect_exact("missing tests root kobject split marker", collect_failures(mutated), [f"{TESTS_ROOT_PATH}:missing_text:{MARKERS[TESTS_ROOT_PATH][3]}"])
        checks_run += 1
        mutated = root / "missing_scripts_root_kobject_split_marker"
        seed(mutated)
        write_text(mutated, SCRIPTS_ROOT_PATH, placeholder(SCRIPTS_ROOT_PATH).replace(MARKERS[SCRIPTS_ROOT_PATH][1], ""))
        expect_exact("missing scripts root kobject split marker", collect_failures(mutated), [f"{SCRIPTS_ROOT_PATH}:missing_text:{MARKERS[SCRIPTS_ROOT_PATH][1]}"])
        checks_run += 1
        mutated = root / "missing_review_checklist_kobject_marker"
        seed(mutated)
        write_text(mutated, REVIEW_CHECKLIST_PATH, placeholder(REVIEW_CHECKLIST_PATH).replace(MARKERS[REVIEW_CHECKLIST_PATH][3], ""))
        expect_exact("missing review checklist kobject marker", collect_failures(mutated), [f"{REVIEW_CHECKLIST_PATH}:missing_text:{MARKERS[REVIEW_CHECKLIST_PATH][3]}"])
        checks_run += 1
        mutated = root / "missing_lane_sequencing_kobject_attr_marker"
        seed(mutated)
        write_text(mutated, LANE_SEQUENCING_PATH, placeholder(LANE_SEQUENCING_PATH).replace(MARKERS[LANE_SEQUENCING_PATH][2], ""))
        expect_exact("missing lane sequencing kobject attr marker", collect_failures(mutated), [f"{LANE_SEQUENCING_PATH}:missing_text:{MARKERS[LANE_SEQUENCING_PATH][2]}"])
        checks_run += 1
        mutated = root / "missing_lane_sequencing_kobject_selfcheck_marker"
        seed(mutated)
        write_text(mutated, LANE_SEQUENCING_PATH, placeholder(LANE_SEQUENCING_PATH).replace(MARKERS[LANE_SEQUENCING_PATH][8], ""))
        expect_exact("missing lane sequencing kobject selfcheck marker", collect_failures(mutated), [f"{LANE_SEQUENCING_PATH}:missing_text:{MARKERS[LANE_SEQUENCING_PATH][8]}"])
        checks_run += 1
    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} self-test cases, ran {checks_run}")
    print("PHASE5_REVIEW_GUIDE_SURFACE_SELF_TEST=pass")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_SELF_TEST_CASES={checks_run}")
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
        print("PHASE5_REVIEW_GUIDE_SURFACE=fail")
        for failure in failures:
            print(failure)
        return 1
    print("PHASE5_REVIEW_GUIDE_SURFACE=pass")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_DIRECT_PATH_COUNT={len(DIRECT_PACKET_PATHS)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_COMPANION_PATH_COUNT={len(PUBLIC_TREE_COMPANION_PATHS)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_KOBJECT_DIRECT_PATH_COUNT={len(KOBJECT_DIRECT_PACKET_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())