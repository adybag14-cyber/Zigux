# Phase 14 Attached Toolchain Guidance Gap

## Scope
- lane: `P14-L10`
- phase: `Phase 14`
- packet: shared attached-toolchain and environment-guidance reminder packet for the bounded Phase 14 smoke route
- status: `current-master reminder truthfulness follow-through`

## Why this note exists
The Phase 14 roadmap keeps the shared smoke packet in a study-only, reviewability-first posture. That means the shipped guidance needs to stay explicit about how reviewers reason about the attached Zig toolchain when it is the only available compiler, and this note needs to describe the current reminder split truthfully instead of replaying older route-gap wording that current `master` has already closed.

## Current repo readback
Fresh rereads on 2026-05-22 show that the attached-toolchain reminder split is narrower than this note previously recorded.

Fresh builder-environment validation on 2026-05-22 also confirms that the attached Zig bundle used by this lane still behaves like a usable bounded-check fallback rather than a stale archival assumption:
- unpacking `agent_files/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` into the scheduled runtime succeeded without extra environment overrides
- `/workspace/.toolchains/p14-l10/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig version` returned `0.17.0-dev.87+9b177a7d2`
- `/workspace/.toolchains/p14-l10/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig env` returned a normal `x86_64-linux` environment payload with the expected library and cache paths
- readable current `zigux/Makefile` evidence now makes the attached-toolchain fallback narrower than older note wording implied: `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)` prefers the pinned extracted bundle or a local `.zig-toolchain/*/zig` candidate before falling back to `zig` on `PATH`, so manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides are optional packet-local escape hatches rather than the primary current rerun path when a checkout can stage the bundle where the Makefile already looks for it

That local replay does not change current repo evidence or promote a broader Phase 14 rerun claim. It does keep the narrower same-lane environment evidence explicit while the readable current `zigux/Makefile` continues to expose only `phase14-validate` from the shared Phase 14 route family.

- `Documentation/zigux/phase14-end-to-end-smoke-survey.md` keeps the attached-toolchain boundary explicit, but it no longer presents the older `phase14-*` wrapper examples as current usable fallback commands; instead it records those names only as historical packet-local rerun vocabulary while the readable `zigux/Makefile` body now exposes `phase14-validate` but still lacks `phase14-smoke`, `phase14-test`, and `phase14`
- `Documentation/zigux/phase14-release-boundary-survey.md` matches that narrower posture too: it keeps the same older `phase14-*` wrapper names only as archival packet-local vocabulary and explicitly avoids restating the attached-toolchain triplet as current fallback guidance while the readable `zigux/Makefile` still omits those broader targets
- `Documentation/zigux/README.md` no longer lags the returned Phase 14 route split: its Phase 14 docs-root reminder block now says the readable `zigux/Makefile` exposes `phase14-validate` while the broader `phase14-smoke`, `phase14-test`, and `phase14` routes remain absent
- `Documentation/zigux/review-checklist.md` is already aligned with the returned Phase 14 route split: its shared-smoke checkpoint keeps the readable `zigux/Makefile` posture explicit, keeps the returned `make -C zigux phase14-validate` gate explicit, and still leaves the broader `phase14-smoke`, `phase14-test`, and `phase14` wrappers in packet-local or repo-reality-gap vocabulary
- `scripts/zigux/README.md` still spells out the older attached-toolchain wrapper triplet directly, but it already frames those names only as packet-local traceability vocabulary rather than active Makefile-backed fallback guidance
- `zigux/tests/README.md` is aligned on the returned route split and now keeps `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, and `zigux/tests/phase14_ring_buffer_survey.zig` explicit in the shared Phase 14 tests-root reminder packet beside the shared smoke note, the productization note, the shared-gap note, the route checker, the validator, the release-boundary checker, the readable Makefile posture, and the workqueue reviewability shard without promoting the missing executable-layer paths
- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` is directly readable again through the current contents path and now keeps that aligned tests-root reminder section machine-checkable instead of leaving the current packet split implicit in neighboring note prose
- `scripts/zigux/check-phase14-shared-smoke-route.py` is directly readable again through the current contents path and keeps the returned `phase14-validate` Makefile route plus workflow gate explicit rather than leaving that shared-smoke route proof implicit in neighboring reminder text
- `scripts/zigux/validate-phase14.py` is directly readable again through the current contents path and carries a real shared-smoke validator surface rather than the older placeholder-only body
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py` is directly readable again through the current contents path and keeps the release-facing exact-count posture aligned with the same reminder packet
- `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` remain directly readable as the workqueue-local reviewability shard, so the attached-toolchain note should keep that returned study-only foothold explicit beside the reminder split

That means the older stale-summary framing recorded by this note is no longer the active same-lane gap on current `master`, and the previous tests-root alignment claim should now record the landed shared Phase 14 tests-root reminder section literally instead of describing it as still missing.

The remaining readback split is narrower:
- the shared smoke note, release-boundary note, docs-root summary, scripts-root summary, and review checklist all keep the attached-toolchain boundary explicit while treating the older `phase14-*` wrapper names as historical packet-local vocabulary rather than current fallback guidance
- `Documentation/zigux/review-checklist.md` now matches that returned route split too, so the checklist no longer needs a same-lane truthfulness repair before the next executable-layer reread
- `zigux/tests/README.md` now keeps the dedicated shared Phase 14 tests-root section explicit, preserving the recovered release-boundary survey note, this attached-toolchain guidance note, the returned ring-buffer survey companion, and the checker-backed route split without overstating missing executable-layer paths
- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py` now keeps that aligned tests-root reminder section machine-checkable, so later same-lane follow-through should treat the checker as current reminder evidence instead of assuming the tests-root packet is still open
- `scripts/zigux/check-phase14-shared-smoke-route.py` keeps the shared `phase14-validate` gate explicit in both the readable Makefile body and the readable bootstrap workflow, so later same-lane follow-through should treat that checker as current route evidence instead of leaving it implied by adjacent reminder prose
- `zigux/Makefile` is readable again, and its live body currently exposes the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes together with the returned `phase14-validate` gate, but no `phase14-smoke`, `phase14-test`, or `phase14` targets; the same readable body now also prefers the pinned extracted bundle or a local `.zig-toolchain/*/zig` candidate before falling back to `zig` on `PATH`, so this note should treat manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides as optional packet-local escapes rather than the default current fallback
- the broader executable packet still remains only partially recoverable in this lane even though the directly readable route checker, the directly readable validator surface, the directly readable release-boundary guard, and the directly readable workqueue reviewability shard have returned

## Why this matters
This is still a real operational-truthfulness issue rather than a new delivery claim:
- the roadmap says Phase 14 stays bounded, study-only, and reviewability-first
- the bootstrap ledger favors exact rerun guidance over implied routes
- the attached toolchain is already part of the operating environment for bounded Zig validation
- the current reminder packet should now record the narrower split truthfully, so later same-lane work does not reopen already-closed docs-root or checklist alignment points, does not re-promote the older wrapper names as active Makefile-backed proof by mistake, does not imply that manual `ZIG=/...` overrides are the primary current rerun path when the readable Makefile already prefers a staged bundle automatically, and does not overstate the tests-root packet as still missing when the shared Phase 14 section is already landed and checker-backed

## Smallest honest same-lane conclusion
The attached-toolchain boundary itself is no longer the gap.

The active same-lane follow-through now lives in keeping the shared reminder family aligned around the returned `phase14-validate` split:
1. keep `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-productization-gap-survey.md`, `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` aligned on the fact that the attached-toolchain boundary is still explicit, the readable `zigux/Makefile` now exposes `phase14-validate`, the readable `ZIG ?=` chain already prefers a staged bundle when present, and the broader `phase14-smoke`, `phase14-test`, and `phase14` names remain historical packet-local or repo-reality-gap vocabulary
2. keep the landed tests-root packet section explicit so it continues to preserve the recovered release-boundary survey note, this attached-toolchain guidance note, and the returned ring-buffer survey companion beside the already-listed shared smoke packet members without promoting the missing executable-layer paths
3. if a future same-lane reread finds a fresh docs-root, checklist, scripts-root, or tests-root drift against the returned `phase14-validate` split or the readable Makefile toolchain-selection chain, repair only that smallest shared reminder surface instead of reopening already-aligned notes by default

## Non-goals
- do not reopen workqueue, ring-buffer, skbuff, or RCU packet contents
- do not introduce a new Phase 14 replay route
- do not imply any live deep-core execution ownership or status change
- do not widen into Phase 15 freeze-map governance
