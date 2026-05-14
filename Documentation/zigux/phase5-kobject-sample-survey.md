# Phase 5 Kobject Sample Survey

This note tracks the bounded Phase 5 approved-idiom packet for the roadmap's `samples/kobject/kobject-example.c` anchor.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_LANE_KEY=P5-L20`
- `PHASE5_SURVEYED_COMMIT=28a3bde2b3d68612f18d9bdd786be50c71c3173e`
- scope: keep the approved idiom truthful against the roadmap while recording the current split between connector-first readback and public current-`master` blob fallback
- current kobject packet evidence on `master`:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `samples/zigux/README.md`
  - `samples/zigux/kobject_example.zig`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
  - public current-`master` blob fallback also shows `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig`, even though connector-first contents reads still returned `404` for those two paths on 2026-05-14

## Why this note exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and still names `samples/kobject/kobject-example.c` as one of the approved Linux anchors. The same product goal still says to make approved Zigux idioms reviewable and repeatable.

This note exists to keep that approved idiom scoped to one landed non-runtime packet. The current packet is no longer a pure missing-file story and no longer a pure all-surfaces-readable story either: connector-first contents reads still narrow the packet to the sample root, focused test, and manifest-backed contract, while public current-`master` blob fallback also exposes the dedicated survey replay and the shared build route again.

## Approved idiom for the landed kobject-style sample

The current kobject packet still describes the approved Phase 5 in-memory ownership-and-lifetime idiom for the roadmap anchor without implying runtime parity. That approved idiom stays reviewable through the sample root, focused test, manifest-backed replay, and the public fallback copy of the dedicated survey replay.

- `runAnchorReplay()` still requires `init()` first, registers exactly three attributes, leaves the sample in the registered stage, keeps the unnamed attribute group explicit, and still reads back default values `42`, `7`, and `-5` for `foo`, `baz`, and `bar`
- before `registerAttributes()`, the sample still reports zero active attributes and blocks `showValue()` or `storeValue()`
- `runPreRegistrationBoundaryReplay()` keeps that initialized-but-not-registered access boundary executable instead of implied
- `runRegisteredBoundaryReplay()` keeps that already-registered duplicate-registration and replay-restart packet executable while still proving the registered sample can accept a bounded foo write/read roundtrip afterward
- `runInputValidationReplay()` keeps the shared `baz`/`bar` dispatch, invalid-integer rejection, and unknown-attribute rejection packet executable while the sample remains in the `registered` stage
- `ownershipSummary()` and sample-owned `runOwnershipReplay()` still keep the lifecycle packet explicit across cold, initialized, registered, and exited snapshots with active attribute counts `0`, `0`, `3`, and `0` and counter progression `0/0/0`, `1/0/0`, `1/1/0`, and `1/1/1`
- `runTeardownReplay()` keeps the registered teardown reset, post-`exit()` show-or-store rejection, second-`exit()` rejection, and anchor-replay rejection explicit
- the exit split still stays explicit as `abandoned_before_registration` for the initialized-only exit path and `tore_down_registered_attributes` for the registered exit path
- keep sysfs creation, `kernel_kobj` integration, uevents, and module-registration claims out of scope

## Current readback split on 2026-05-14

Fresh repo-first inspection on 2026-05-14 confirmed a real split between read paths:

- the GitHub contents API still returned `404` for `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig`
- public current-`master` blob fallback still exposed those same two paths
- the focused sample root, focused test, and manifest remained readable through the primary GitHub read path

That means the precise same-lane gap is reminder-surface truthfulness rather than missing sample behavior. Shared reminder surfaces should keep both facts explicit instead of collapsing the state into either a missing-packet claim or a fully recovered connector-readback claim.

## Exact checks recorded today

The current manifest-backed exact checks for the kobject packet remain the bounded review contract this note should preserve:

- `directory-name`: the in-memory sample keeps the Linux directory name `kobject_example` and an unnamed attribute group
- `registration-step`: `runAnchorReplay()` requires `init()` first, registers exactly three attributes, leaves the sample in the registered stage, and keeps duplicate `registerAttributes()` plus registered-stage `runAnchorReplay()` calls blocked by `InvalidLifecycleTransition`
- `pre-registration-boundary`: `runPreRegistrationBoundaryReplay()` leaves the sample initialized, keeps the active attribute count at zero, and shows that `show` or `store` still return `InvalidLifecycleTransition` before `registerAttributes()` opens the sample
- `single-init-boundary`: calling `init()` twice keeps the sample initialized, leaves the active attribute count at zero, and returns `InvalidLifecycleTransition` on the second init without advancing `register_runs` or `exit_runs`
- `registered-boundary`: `runRegisteredBoundaryReplay()` leaves the sample registered, keeps the active attribute count at three, keeps `register_runs` pinned at one across duplicate registration plus registered-stage anchor-replay rejection, and still allows a bounded `foo` write/read roundtrip afterward
- `ownership-summary`: `ownershipSummary()` and `runOwnershipReplay()` report the cold, initialized, registered, and exited stages with active attribute counts `0`, `0`, `3`, and `0`
- `ownership-counters`: `runOwnershipReplay()` keeps the init/register/exit counter progression explicit as `0/0/0`, `1/0/0`, `1/1/0`, and `1/1/1`
- `initialized-exit-disposition`: `exit()` reports `abandoned_before_registration` when the sample leaves the initialized stage before attributes are registered
- `foo-roundtrip`: storing `42` into `foo` renders back as the string `42` followed by a newline
- `shared-b-dispatch`: `runInputValidationReplay()` keeps `baz` and `bar` on the same `show` and `store` path while rendering `9` and `10` through their own attribute names after the replay stores those exact values
- `parse-failure`: `runInputValidationReplay()` keeps invalid-integer writes returning `InvalidInteger` and unknown attribute names as explicit errors while the sample remains in the registered stage
- `exit-boundary`: `runTeardownReplay()` reports `tore_down_registered_attributes`, clears the tracked values, removes the active attribute count, and keeps reinit, reregister, post-exit `show`, post-exit `store`, second `exit()`, and anchor-replay rejection explicit

## Contributor Checklist

When a contributor updates `samples/zigux/kobject_example.zig` or one of its directly coupled review surfaces, keep these packet-local questions explicit here instead of relying on the broader shared guides alone:

- does the packet still keep the one-time `init()` rule explicit so a second `init()` returns `InvalidLifecycleTransition` without advancing `register_runs` or `exit_runs`?
- do `runPreRegistrationBoundaryReplay()`, `runRegisteredBoundaryReplay()`, `runInputValidationReplay()`, `runOwnershipReplay()`, and `runTeardownReplay()` still describe the same bounded ownership-and-lifetime packet across the sample root, focused test, manifest, and public fallback survey replay?
- if a shared reminder surface mentions `zigux/tests/phase5_kobject_example_survey.zig` or `zigux/tests/phase5_build.zig`, does it say clearly whether that claim comes from public fallback, connector-first readback, or both?
- shared docs-root, sample-root, scripts-root, and tests-root contributor packet should stay explicit here too: `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- keep the validation routes explicit for the currently landed packet: `zig build test --build-file zigux/tests/phase5_build.zig --summary all`, `make -C zigux phase5-test`, and `make -C zigux phase5`

## Non-goals

This note still does not claim:

- sysfs file creation parity
- `kernel_kobj` integration
- uevent delivery
- loadable module registration

## Next bounded step

Leave this lane parked unless a fresh kobject reread changes one bounded fact inside the same packet:

- connector-first readback for `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` converges with the already-visible public fallback, so the note can retire the split-readback wording
- another shared reminder surface still presents the kobject packet without saying whether it is using connector-first readback or public fallback and needs one more lane-local truthfulness repair

Do not widen that follow-up into sample behavior unless the sample-root file, focused test, manifest, or dedicated survey replay actually changes.
