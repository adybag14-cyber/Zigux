#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GUIDE_PATH = Path("Documentation/zigux/phase5-sample-review-guide.md")

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

PUBLIC_TREE_PACKET_PATHS = (
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "samples/zigux/kobject_example.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_kobject_example_manifest.json",
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
    "The roadmap still includes the `kobject` anchor, and fresh Phase 5 reread in this run kept the split evidence explicit: authenticated current-`master` contents readback still did not return the older sample-root or tests-root packet members that earlier reminder surfaces cited, while public-tree fallback still exposes the bounded packet below:",
    "Keep shared contributor guidance honest about that split instead of restating the older kobject packet as direct authenticated proof or flattening it into a pure missing-packet story.",
    "Because current `master` keeps the restored direct bytestream sample-plus-tests packet, the restored direct kretprobe packet, the shared trace-events side in a narrower posture with a direct formatting companion and older broader companion paths still in the repo-reality-gap bucket, and the `kobject` anchor in the public-tree-backed-companion-plus-authenticated-gap bucket, same-lane follow-through should stay inside these bounded categories:",
    "Keep the current ten-cue review contract explicit in shared contributor guidance when a bytestream reminder surface is refreshed:",
    "Use the direct sample-plus-tests packet to keep the primary review surfaces visible too: `previewInto()`, `snapshotInto()`, `occupancySummary()`, `writableSpanSummary()`, `visibleSpanSummary()`, `usesWrappedStorageWindow()`, and the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle should stay easy to find from shared guidance instead of being left implicit in sample-local code only.",
    "Respect the freeze map too.",
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
    "Treat `samples/zigux/kobject_example.zig` as direct authenticated proof.",
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
    failures: list[str] = []

    for marker in REQUIRED_TEXT:
        if marker not in guide:
            failures.append(f"guide:missing_text:{marker}")

    for marker in BYTESTREAM_CONTRACT_MARKERS:
        if marker not in guide:
            failures.append(f"guide:missing_bytestream_contract:{marker}")

    for marker in NO_EXTRA_SAMPLE_MARKERS:
        if marker not in guide:
            failures.append(f"guide:missing_boundary:{marker}")

    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in guide:
            failures.append(f"guide:missing_direct_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    for rel in PUBLIC_TREE_PACKET_PATHS:
        if f"`{rel}`" not in guide:
            failures.append(f"guide:missing_public_tree_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_public_tree_path:{rel}")

    for rel in TRACE_EVENTS_COMPANION_GAP_PATHS:
        if f"`{rel}`" not in guide:
            failures.append(f"guide:missing_trace_events_gap_path:`{rel}`")

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
    public_tree = "\n".join(f"* `{rel}`" for rel in PUBLIC_TREE_PACKET_PATHS)
    trace_gaps = "\n".join(f"* `{rel}`" for rel in TRACE_EVENTS_COMPANION_GAP_PATHS)
    bytestream_contract = "\n".join(f"* {marker}" for marker in BYTESTREAM_CONTRACT_MARKERS)
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

Use the direct sample-plus-tests packet to keep the primary review surfaces visible too: `previewInto()`, `snapshotInto()`, `occupancySummary()`, `writableSpanSummary()`, `visibleSpanSummary()`, `usesWrappedStorageWindow()`, and the bounded `init()` -> `runAnchorReplay()` -> `exit()` lifecycle should stay easy to find from shared guidance instead of being left implicit in sample-local code only.

The roadmap still includes the `kobject` anchor, and fresh Phase 5 reread in this run kept the split evidence explicit: authenticated current-`master` contents readback still did not return the older sample-root or tests-root packet members that earlier reminder surfaces cited, while public-tree fallback still exposes the bounded packet below:

{public_tree}

Keep shared contributor guidance honest about that split instead of restating the older kobject packet as direct authenticated proof or flattening it into a pure missing-packet story.

Because current `master` keeps the restored direct bytestream sample-plus-tests packet, the restored direct kretprobe packet, the shared trace-events side in a narrower posture with a direct formatting companion and older broader companion paths still in the repo-reality-gap bucket, and the `kobject` anchor in the public-tree-backed-companion-plus-authenticated-gap bucket, same-lane follow-through should stay inside these bounded categories:

* one bytestream reminder-surface truthfulness repair at a time
* one trace-events reminder-surface truthfulness repair at a time
* one trace-events approved-idiom-gap repair at a time
* one trace-events sample-root, tests-root, approved-idiom-gap, or shared-build reminder alignment repair at a time
* one kobject split-evidence reminder repair at a time

Keep later runtime-facing sample work under the separate Phase 9 lane.

{no_extra}

Respect the freeze map too.
"""


def _seed(root: Path) -> None:
    _write(root / GUIDE_PATH, _sample_guide())
    for rel in DIRECT_PACKET_PATHS:
        _write(root / rel, "present\n")
    for rel in PUBLIC_TREE_PACKET_PATHS:
        _write(root / rel, "present\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 8
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
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_PUBLIC_TREE_PACKET_COUNT={len(PUBLIC_TREE_PACKET_PATHS)}")
    print(f"PHASE5_REVIEW_GUIDE_SURFACE_BYTESTREAM_CONTRACT_COUNT={len(BYTESTREAM_CONTRACT_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
