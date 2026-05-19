#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GUIDE_PATH = Path("Documentation/zigux/phase5-sample-review-guide.md")
DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")
APPROVED_IDIOM_PATH = Path("Documentation/zigux/phase5-trace-events-approved-idiom-gap.md")

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
    "The shared `zigux/tests/phase5_build.zig` route remains useful support material too, but keep it framed as current public-tree-backed companion evidence until authenticated contents reread returns that path directly again.",
    "Keep the approved formatting idiom bounded to the current landed reminder packet:",
    "That packet should keep the selected-string plus `iter=%d` formatting cue explicit while staying honest about the current split:",
    "Current `master` also still ships no standalone Phase 5 `samples/zigux/*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
    "Keep standalone formatting-helper evidence under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 helper reminders, keep `cmdline`, `argv_split`, and `rbtree` evidence under the bounded Phase 7 helper packet, keep direct bitmap helper reviewability under the closed Phase 1 plus bounded Phase 4 reminder packet, and keep runtime-facing trace-events loader work under the separate Phase 9 lane.",
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


def collect_failures(root: Path) -> list[str]:
    guide = _read(root / GUIDE_PATH)
    docs_root = _read(root / DOCS_ROOT_PATH)
    approved_idiom = _read(root / APPROVED_IDIOM_PATH)
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
    direct = "\n".join(
        f"* `{rel}`"
        for rel in DIRECT_PACKET_PATHS
        if rel.startswith("Documentation/zigux/phase5-")
        or rel.startswith("samples/zigux/")
        or rel.startswith("zigux/tests/phase5_")
    )
    kobject_direct = "\n".join(f"* `{rel}`" for rel in KOBJECT_DIRECT_PACKET_PATHS)
    kobject_public_tree = "\n".join(f"* `{rel}`" for rel in KOBJECT_PUBLIC_TREE_PACKET_PATHS)
    trace_gaps = "\n".join(f"* `{rel}`" for rel in TRACE_EVENTS_COMPANION_GAP_PATHS)
    bytestream_contract = "\n".join(f"* {marker}" for marker in BYTESTREAM_CONTRACT_MARKERS)
    kobject_contract = "\n".join(f"* {marker}" for marker in KOBJECT_CONTRACT_MARKERS)
    no_extra = "\n".join(f"* {marker}" for marker in NO_EXTRA_SAMPLE_MARKERS)
    return f"""# Phase 5 Sample Review Guide

Treat those four anchors as the approved Phase 5 destination set unless the roadmap changes.

Fresh repo-first inspection on 2026-05-19 confirmed that current `master` now directly serves the bounded bytestream sample-plus-tests packet through these paths:

{direct}

That same reread also confirmed that the shared build companion still needs to stay in the split-readback bucket for now:

* `zigux/tests/phase5_build.zig`

Keep the direct bytestream sample-plus-tests packet explicit while the shared build companion stays framed as current public-tree-backed evidence instead of flattening the packet back into a sample-only story or treating the shared build route as returned authenticated proof.
Fresh 2026-05-19 reread also keeps the current direct packet shape explicit: `samples/zigux/bytestream_fifo.zig` now carries three in-file self-checks, `zigux/tests/phase5_bytestream_fifo.zig` keeps four focused replay tests, and `zigux/tests/phase5_bytestream_fifo_survey.zig` keeps five survey-packet checks aligned with the survey note and manifest.

The same 2026-05-19 repo-first inspection also confirmed a narrower current non-runtime trace-events packet: authenticated contents reread still directly proves the bounded formatting companion, and the shared reminder surfaces below still keep that smaller packet explicit:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
* `Documentation/zigux/phase5-sample-lane-sequencing.md`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `scripts/zigux/README.md`
* `scripts/zigux/check-phase5-review-guide-surface.py`
* `zigux/tests/README.md`

Keep the missing-companion boundary explicit too:

{trace_gaps}
* `zigux/tests/phase5_build.zig`

For the shared tracing and probe lane, ground reviewer guidance in the restored direct kretprobe packet plus the narrower trace-events packet above and these shared reminder surfaces:

* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `Documentation/zigux/phase5-sample-lane-sequencing.md`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/README.md`
* `scripts/zigux/check-phase5-review-guide-surface.py`
* `zigux/tests/README.md`

Keep the current ten-cue review contract explicit in shared contributor guidance when a bytestream reminder surface is refreshed:

{bytestream_contract}

Use the direct sample-plus-tests packet to keep the primary review surfaces visible too: `previewInto()`, `snapshotInto()`, `occupancySummary()`, `writableSpanSummary()`, `visibleSpanSummary()`, and `usesWrappedStorageWindow()`, and the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle should stay easy to find from shared guidance instead of being left implicit in sample-local code only.

The roadmap still includes the `kobject` anchor, and fresh Phase 5 reread in this run kept the split evidence explicit: authenticated current-`master` contents readback directly returned the survey note, sample root, focused test, and manifest-backed contract again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` still need public-tree fallback in this runtime.

Authenticated contents readback now directly returns these kobject packet members:

{kobject_direct}

Fresh public current-`master` fallback still carries these companion paths:

{kobject_public_tree}

Keep shared contributor guidance honest about that split instead of flattening the whole kobject packet into public-tree-only support material, treating the sample-local direct proof as gone, or promoting the survey replay plus shared build route into returned authenticated proof.

Keep the approved Phase 5 in-memory ownership-and-lifetime idiom reviewable from the shared guide too:

{kobject_contract}

Because current `master` keeps the restored direct bytestream sample-plus-tests packet, the restored direct kretprobe packet, the shared trace-events side in a narrower posture with a direct formatting companion and older broader companion paths still in the repo-reality-gap bucket, and the `kobject` anchor in a mixed direct-plus-public-tree-backed split packet, same-lane follow-through should stay inside these bounded categories:

* one bytestream reminder-surface truthfulness repair at a time
* one trace-events reminder-surface truthfulness repair at a time
* one trace-events approved-idiom-gap repair at a time
* one trace-events sample-root, tests-root, approved-idiom-gap, or shared-build reminder alignment repair at a time
* one kobject split-evidence reminder repair at a time

Keep later runtime-facing sample work under the separate Phase 9 lane.

{no_extra}

Respect the freeze map too.
"""


def _sample_docs_root() -> str:
    return """# Zigux Documentation
Phase 5 notes
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/check-phase5-review-guide-surface.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
keep the current four-anchor non-runtime sample packet explicit from the docs root instead of letting the shared contributor reminder drift away from the live sample-root, scripts-root, guide, sequencing, checklist, and tests-root packet.
  * current `master` still directly exposes the restored bytestream packet through `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig`, and it still directly exposes the restored kretprobe packet through `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`, while `samples/zigux/trace_events_string_formatting_sample.zig` stays only the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.
  * keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.
  * keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.
  * keep the current `kobject` ownership-and-lifetime split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json` are current direct reminder or packet evidence again, while `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` stay public-tree-backed companion evidence until a fresh reread restores direct authenticated proof for those two routes.
"""


def _sample_approved_idiom_gap() -> str:
    return """# Phase 5 Trace-Events Approved Idiom Gap

This note keeps the roadmap-backed Phase 5 trace-events packet truthful when shared reviewer surfaces need to mention the bounded formatting idiom that current `master` still approves.

## Current approved cue on `master`

The roadmap-backed Phase 5 trace-events anchor is still:

- `samples/trace_events/trace-events-sample.c`

Authenticated sample-root readback still directly exposes this bounded non-runtime formatting companion:

- `samples/zigux/trace_events_string_formatting_sample.zig`

Fresh mixed reread on 2026-05-19 keeps the broader non-runtime trace-events sample-local companions in a split state rather than a missing state:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

The shared `zigux/tests/phase5_build.zig` route remains useful support material too, but keep it framed as current public-tree-backed companion evidence until authenticated contents reread returns that path directly again.

Keep the approved formatting idiom bounded to the current landed reminder packet:

- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `samples/zigux/trace_events_string_formatting_sample.zig`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase5-review-guide-surface.py`
- `zigux/tests/README.md`

That packet should keep the selected-string plus `iter=%d` formatting cue explicit while staying honest about the current split:

- the bounded formatting companion remains directly readable through the authenticated sample-root route
- the broader non-runtime trace-events sample-local companions are visible again through the live public-tree-backed packet but are not yet returned authenticated proof in this lane
- the shared `zigux/tests/phase5_build.zig` path is still public-tree-backed companion evidence rather than returned authenticated proof

## Review boundary

Current `master` also still ships no standalone Phase 5 `samples/zigux/*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.

Keep standalone formatting-helper evidence under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 helper reminders, keep `cmdline`, `argv_split`, and `rbtree` evidence under the bounded Phase 7 helper packet, keep direct bitmap helper reviewability under the closed Phase 1 plus bounded Phase 4 reminder packet, and keep runtime-facing trace-events loader work under the separate Phase 9 lane.
"""


def _seed(root: Path) -> None:
    _write(root / GUIDE_PATH, _sample_guide())
    _write(root / DOCS_ROOT_PATH, _sample_docs_root())
    _write(root / APPROVED_IDIOM_PATH, _sample_approved_idiom_gap())
    for rel in DIRECT_PACKET_PATHS:
        if Path(rel) == APPROVED_IDIOM_PATH:
            continue
        _write(root / rel, "present\n")
    for rel in KOBJECT_DIRECT_PACKET_PATHS:
        _write(root / rel, "present\n")
    for rel in KOBJECT_PUBLIC_TREE_PACKET_PATHS:
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

        missing_checker_marker_root = root / "missing_checker_marker"
        _seed(missing_checker_marker_root)
        _write(
            missing_checker_marker_root / GUIDE_PATH,
            _sample_guide().replace("* `scripts/zigux/check-phase5-review-guide-surface.py`\n", "", 2),
        )
        failures = collect_failures(missing_checker_marker_root)
        expected = ["guide:missing_direct_path:`scripts/zigux/check-phase5-review-guide-surface.py`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-checker-marker failure: {failures}")
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

        missing_kobject_exit_split_root = root / "missing_kobject_exit_split"
        _seed(missing_kobject_exit_split_root)
        _write(
            missing_kobject_exit_split_root / GUIDE_PATH,
            _sample_guide().replace(KOBJECT_CONTRACT_MARKERS[-1], "", 1),
        )
        failures = collect_failures(missing_kobject_exit_split_root)
        expected = [f"guide:missing_kobject_contract:{KOBJECT_CONTRACT_MARKERS[-1]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-kobject-exit-split failure: {failures}")
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
        _write(
            forbidden_text_root / GUIDE_PATH,
            _sample_guide() + "\n" + FORBIDDEN_TEXT[2] + "\n",
        )
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
            _sample_approved_idiom_gap().replace(APPROVED_IDIOM_REQUIRED_TEXT[5], "", 1),
        )
        failures = collect_failures(missing_approved_idiom_marker_root)
        expected = [f"approved_idiom:missing_text:{APPROVED_IDIOM_REQUIRED_TEXT[5]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-approved-idiom-marker failure: {failures}")
        checks_run += 1

        missing_approved_idiom_path_root = root / "missing_approved_idiom_path"
        _seed(missing_approved_idiom_path_root)
        _write(
            missing_approved_idiom_path_root / APPROVED_IDIOM_PATH,
            _sample_approved_idiom_gap().replace("`scripts/zigux/check-phase5-review-guide-surface.py`", "", 1),
        )
        failures = collect_failures(missing_approved_idiom_path_root)
        expected = ["approved_idiom:missing_path:`scripts/zigux/check-phase5-review-guide-surface.py`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-approved-idiom-path failure: {failures}")
        checks_run += 1

        missing_guide_root = root / "missing_guide"
        _seed(missing_guide_root)
        (missing_guide_root / GUIDE_PATH).unlink()
        try:
            collect_failures(missing_guide_root)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise AssertionError(f"unexpected missing-guide abort: {exc}") from exc
        else:
            raise AssertionError("missing guide did not abort")
        checks_run += 1

        missing_docs_root_file = root / "missing_docs_root_file"
        _seed(missing_docs_root_file)
        (missing_docs_root_file / DOCS_ROOT_PATH).unlink()
        try:
            collect_failures(missing_docs_root_file)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise AssertionError(f"unexpected missing-docs-root abort: {exc}") from exc
        else:
            raise AssertionError("missing docs root did not abort")
        checks_run += 1

        missing_docs_root_boundary_root = root / "missing_docs_root_boundary"
        _seed(missing_docs_root_boundary_root)
        _write(
            missing_docs_root_boundary_root / DOCS_ROOT_PATH,
            _sample_docs_root().replace(DOCS_ROOT_REQUIRED_TEXT[3], "", 1),
        )
        failures = collect_failures(missing_docs_root_boundary_root)
        expected = [f"docs_root:missing_text:{DOCS_ROOT_REQUIRED_TEXT[3]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-docs-root-boundary failure: {failures}")
        checks_run += 1

        missing_approved_idiom_file = root / "missing_approved_idiom_file"
        _seed(missing_approved_idiom_file)
        (missing_approved_idiom_file / APPROVED_IDIOM_PATH).unlink()
        try:
            collect_failures(missing_approved_idiom_file)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise AssertionError(f"unexpected missing-approved-idiom abort: {exc}") from exc
        else:
            raise AssertionError("missing approved idiom note did not abort")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
