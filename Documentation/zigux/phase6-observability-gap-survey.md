# Phase 6 Observability Gap Survey

This note records the current observability posture for the bounded Phase 6 leaf-helper packet on `master`.

## Status

- `PHASE6_OBSERVABILITY_SURVEY_STATUS=active`
- surveyed head: `current-master-readback-2026-05-25`
- lane scope: runtime logging and diagnostics survey only
- roadmap boundary: Phase 6 stays scoped to low-risk leaf helpers rooted in `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c`
- direct Phase 6 shared packet: `Documentation/zigux/phase6-helper-evidence-catalog.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, `scripts/zigux/check-phase6-shared-surface.py`, `scripts/zigux/check-phase6-present-entrypoints.py`, `scripts/zigux/validate-phase6.py`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, and `zigux/Makefile`
- neighboring observability anchors: `Documentation/zigux/phase5-trace-events-sample-survey.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `samples/zigux/runtime_trace_events.zig`, and `zigux/tests/runtime_trace_events_survey.zig`

## Why this survey exists

The current Phase 6 packet is well-covered for helper evidence, parity, and perf, but it does not yet carry an explicit reminder note for runtime logging, diagnostics, or observability boundaries. That omission creates a truthfulness risk: nearby trace-events and runtime-pilot packets make observability evidence visible elsewhere in the tree, while the roadmap still keeps Phase 6 on helper-first ground.

This survey closes that narrower documentation gap without widening Phase 6 into runtime-substrate delivery, trace buffer ownership, or loadable-module claims.

## Current repo reality on `master`

Current Phase 6 evidence is helper-first.

- `Documentation/zigux/phase6-helper-evidence-catalog.md` records the four roadmap-backed helper anchors and their current reviewable replay packet.
- `Documentation/zigux/phase6-helper-parity-catalog.md` records the shared parity companion for those same helper anchors.
- `Documentation/zigux/phase6-perf-gate-survey.md` records the shared perf posture for `base64`, `bsearch`, `checksum`, and `hexdump`.
- `zigux/tests/phase6_build.zig` and `zigux/Makefile` expose helper-local test and perf routes, including `phase6-base64-perf`, `phase6-bsearch-perf`, `phase6-checksum-perf`, `phase6-hexdump-perf`, and `phase6-perf`.

Current Phase 6 evidence is not runtime observability evidence.

- no current Phase 6 note claims ownership of `samples/trace_events/trace-events-sample.c` or the runtime-pilot `samples/zigux/runtime_*` family
- no current Phase 6 shared packet claims a trace-events sample, runtime logging module, runtime diagnostics hook, or runtime loader contract
- no current Phase 6 build route is framed as a runtime-tracing or runtime-diagnostics replay surface

Current observability evidence lives in neighboring phases instead.

- Phase 5 keeps the non-runtime trace-events contributor surface explicit through `Documentation/zigux/phase5-trace-events-sample-survey.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, and `samples/zigux/trace_events_string_formatting_sample.zig`.
- Phase 9 keeps the shipped runtime trace-events packet explicit through `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `samples/zigux/runtime_trace_events.zig`, and `zigux/tests/runtime_trace_events_survey.zig`.
- Phase 9 also keeps the shared runtime-loader and command or environment boundary packet separate from that trace-events family, so current observability evidence there is still bounded rather than a claim of broader runtime-substrate completion.

## Roadmap gap summary

The roadmap does not ask Phase 6 to deliver runtime logging or diagnostics ownership. It asks Phase 6 to prove low-risk leaf helpers with clear parity and perf gates.

That means the honest current gap is not missing helper work. The honest gap is missing boundary wording.

- Phase 6 already has helper evidence, parity, and perf documentation.
- Phase 6 does not yet have a dedicated note that says runtime observability evidence belongs to neighboring Phase 5 and Phase 9 packets instead of the Phase 6 helper tranche.
- Without that note, future shared reminder surfaces could overclaim trace-events or runtime diagnostics maturity inside the Phase 6 packet.

## Guidance for same-lane follow-through

Keep Phase 6 observability follow-through inside reminder truthfulness only.

- treat this note as the owner for the Phase 6 observability boundary until a broader shared reminder surface absorbs it cleanly
- keep Phase 6 scoped to helper evidence, parity, perf thresholds, and helper-local replay routes
- route non-runtime trace-events sample wording back through the existing Phase 5 packet
- route runtime trace-events, loader, and runtime bitmap observability wording back through the existing Phase 9 packet

Do not use this lane to claim:

- runtime module lifecycle parity in Phase 6
- trace buffer, ring buffer, or workqueue ownership in Phase 6
- runtime loader completion in Phase 6
- that helper perf routes are equivalent to runtime observability proof

## Next bounded step

If the shared reminder packet reopens, the next honest same-lane move is one small truthfulness repair in `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, or a dedicated Phase 6 shared checker so those surfaces explicitly point back to this boundary note without promoting Phase 5 or Phase 9 observability evidence into the Phase 6 helper tranche.
