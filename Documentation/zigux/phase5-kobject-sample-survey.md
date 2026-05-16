# Phase 5 Kobject Sample Survey

This note tracks the bounded Phase 5 approved-idiom packet for the roadmap's `samples/kobject/kobject-example.c` anchor.

## Status

- `PHASE5_STATUS=verified-public-tree-backed-packet`
- `PHASE5_LANE_KEY=P5-L20`
- `PHASE5_SURVEYED_COMMIT=28a3bde2b3d68612f18d9bdd786be50c71c3173e`
- scope: keep the approved idiom truthful against the roadmap while recording the current mixed direct-and-public-tree-backed kobject packet without widening past the landed non-runtime sample
- current kobject packet evidence on `master`:
  - directly readable in this environment:
    - `Documentation/zigux/phase5-kobject-sample-survey.md`
    - `Documentation/zigux/phase5-sample-review-guide.md`
    - `samples/zigux/README.md`
    - `scripts/zigux/README.md`
    - `zigux/tests/README.md`
    - `samples/zigux/kobject_example.zig`
    - `zigux/tests/phase5_kobject_example.zig`
    - `zigux/tests/phase5_kobject_example_manifest.json`
  - current public-tree-backed companion evidence:
    - `zigux/tests/phase5_kobject_example_survey.zig`
    - `zigux/tests/phase5_build.zig`

## Why this note exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and still names `samples/kobject/kobject-example.c` as one of the approved Linux anchors. The same product goal still says to make approved Zigux idioms reviewable and repeatable.

This note exists to keep that approved idiom scoped to one landed non-runtime packet. On the current tree, that packet is the sample root, the focused test, the manifest-backed contract, the dedicated survey replay, the shared Phase 5 build route, and the reminder surfaces that describe them. Authenticated contents readback in this environment still flakes on some `zigux/tests` paths, so the note should record the strongest current repo truth instead of freezing an older narrower packet after a connector-local 404.

## Approved idiom for the landed kobject-style sample

The current kobject packet still describes the approved Phase 5 in-memory ownership-and-lifetime idiom for the roadmap anchor without implying runtime parity. That approved idiom stays reviewable through the sample root, focused test, manifest-backed replay, dedicated survey replay, shared build route, and the shared reminder surfaces that name those same files, including the docs-root, sample-root, scripts-root, and tests-root packet reminders.

- `runAnchorReplay()` still requires `init()` first, registers exactly three attributes, leaves the sample in the registered stage, keeps the unnamed attribute group explicit, and still reads back default values `42`, `7`, and `-5` for `foo`, `baz`, and `bar`
- before `registerAttributes()`, the sample still reports zero active attributes and blocks `showValue()` or `storeValue()`
- `runSingleInitBoundaryReplay()` keeps the one-time `init()` rule executable so a second `init()` still returns `InvalidLifecycleTransition` while the sample stays initialized with zero active attributes and `1/0/0` counters
- `runPreRegistrationBoundaryReplay()` keeps that initialized-but-not-registered access boundary executable instead of implied
- `runRegistrationOwnershipReplay()` keeps the register-before-init rejection, the cold-to-initialized-to-registered handoff, the active attribute count transition from `0` to `3`, and the duplicate-registration rejection executable instead of implied
- `runRegisteredBoundaryReplay()` keeps that already-registered duplicate-registration and replay-restart packet executable while still proving the registered sample can accept a bounded foo write/read roundtrip afterward
- `runInputValidationReplay()` keeps the shared `baz`/`bar` dispatch, invalid-integer rejection, and unknown-attribute rejection packet executable while the sample remains in the `registered` stage
- `ownershipSummary()` and sample-owned `runOwnershipReplay()` still keep the lifecycle packet explicit across cold, initialized, registered, and exited snapshots with active attribute counts `0`, `0`, `3`, and `0` and counter progression `0/0/0`, `1/0/0`, `1/1/0`, and `1/1/1`
- `runTeardownReplay()` keeps the registered teardown reset, post-`exit()` show-or-store rejection, second-`exit()` rejection, and anchor-replay rejection explicit
- the exit split still stays explicit as `abandoned_before_registration` for the initialized-only exit path and `tore_down_registered_attributes` for the registered exit path
- keep sysfs creation, `kernel_kobj` integration, uevents, and module-registration claims out of scope

## Current repo reality on 2026-05-15

Fresh repo-first inspection on 2026-05-15 confirmed that the live packet is broader than the older narrower-note wording implied:

- GitHub contents readback in this environment still returns `404` for `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig`
- public current-`master` readback now shows both `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` present again
- `zigux/tests/phase5_kobject_example_survey.zig` still reads the shared review surfaces, checks the dedicated kobject survey markers, and requires the `phase5_build.zig`, `zigux/Makefile`, and workflow route markers for the kobject packet
- `zigux/tests/phase5_build.zig` still wires `phase5_kobject_example.zig` and `phase5_kobject_example_survey.zig` into the named `phase5-kobject-example-tests` and `phase5-kobject-example-survey-tests` routes

That means the same-lane maintenance target is reminder-surface truthfulness only. Shared reminders should keep the broader public-tree-backed packet explicit while also saying clearly that an authenticated contents `404` here is a connector-local readback gap, not proof that the survey or shared build files vanished from `master`.

## Exact checks recorded today

The current manifest-backed exact checks for the kobject packet remain the bounded review contract this note should preserve:

- `directory-name`: the in-memory sample keeps the Linux directory name `kobject_example` and an unnamed attribute group
- `registration-step`: `runAnchorReplay()` requires `init()` first, registers exactly three attributes, leaves the sample in the registered stage, and keeps duplicate `registerAttributes()` plus registered-stage `runAnchorReplay()` calls blocked by `InvalidLifecycleTransition`
- `pre-registration-boundary`: `runPreRegistrationBoundaryReplay()` leaves the sample initialized, keeps the active attribute count at zero, and shows that `show` or `store` still return `InvalidLifecycleTransition` before `registerAttributes()` opens the sample
- `single-init-boundary`: calling `init()` twice keeps the sample initialized, leaves the active attribute count at zero, and returns `InvalidLifecycleTransition` on the second init without advancing `register_runs` or `exit_runs`
- `registration-ownership-boundary`: `runRegistrationOwnershipReplay()` rejects `registerAttributes()` before init, then records the cold to initialized to registered handoff with activeAttrCount moving from `0` to `3`, `init_runs = 1`, `register_runs = 1`, `exit_runs = 0`, and duplicate `registerAttributes()` still rejected after registration`
- `registered-boundary`: `runRegisteredBoundaryReplay()` leaves the sample registered, keeps activeAttrCount at three, keeps `register_runs` pinned at one across duplicate `registerAttributes()` plus registered-stage `runAnchorReplay()` rejection, and still allows a bounded `foo` write/read roundtrip afterward`
- `ownership-summary`: `ownershipSummary()` and `runOwnershipReplay()` report the cold, initialized, registered, and exited stages with active attribute counts `0`, `0`, `3`, and `0`
- `ownership-counters`: `runOwnershipReplay()` keeps the init/register/exit counter progression explicit as `0/0/0`, `1/0/0`, `1/1/0`, and `1/1/1` across the cold, initialized, registered, and exited snapshots`
- `initialized-exit-disposition`: `exit()` reports `abandoned_before_registration` when the sample leaves the initialized stage before attributes are registered`
- `foo-roundtrip`: storing `42` into `foo` renders back as the string `42` followed by a newline`
- `shared-b-dispatch`: `runInputValidationReplay()` keeps `baz` and `bar` on the same `show` and `store` path while rendering `9` and `10` through their own attribute names after the replay stores those exact values`
- `parse-failure`: `runInputValidationReplay()` keeps invalid-integer writes returning `InvalidInteger` and unknown attribute names as explicit errors while the sample remains in the registered stage`
- `exit-boundary`: `runTeardownReplay()` reports `tore_down_registered_attributes`, clears the tracked values, removes the active attribute count, and keeps reinit, reregister, post-exit `show`, post-exit `store`, second-exit, and anchor-replay rejection explicit`

## Contributor Checklist

When a contributor updates `samples/zigux/kobject_example.zig` or one of its directly coupled review surfaces, keep these packet-local questions explicit here instead of relying on the broader shared guides alone:

- does the packet still keep the one-time `init()` rule explicit so a second `init()` returns `InvalidLifecycleTransition` without advancing `register_runs` or `exit_runs`?
- do `runSingleInitBoundaryReplay()`, `runPreRegistrationBoundaryReplay()`, `runRegistrationOwnershipReplay()`, `runRegisteredBoundaryReplay()`, `runInputValidationReplay()`, `runOwnershipReplay()`, and `runTeardownReplay()` still describe the same bounded ownership-and-lifetime packet across the sample root, focused test, manifest, dedicated survey replay, and shared Phase 5 build route?
- if a reminder surface mentions `zigux/tests/phase5_kobject_example_survey.zig` or `zigux/tests/phase5_build.zig`, did a fresh reread confirm whether the current public tree still carries those files instead of treating a connector-local `404` as repo absence?
- if `zigux/tests/README.md` is refreshed for this sample packet, does it keep `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` framed as current public-tree-backed companion evidence rather than falling back to older gap wording?
- if `scripts/zigux/README.md` is refreshed for this sample packet, does it keep `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` framed as current public-tree-backed companion evidence instead of collapsing the kobject packet back to a narrower note-plus-sample-plus-tests description?
- shared docs-root, sample-root, scripts-root, and tests-root contributor packet should stay explicit here too: `Documentation/zigux/phase5-sample-review-guide.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- keep the mixed direct-plus-public-tree-backed packet explicit instead of collapsing back to the older narrower packet unless fresh repo readback truly drops the dedicated survey or shared build routes again

## Non-goals

This note still does not claim:

- sysfs file creation parity
- `kernel_kobj` integration
- uevent delivery
- loadable module registration

## Next bounded step

Leave this lane parked unless a fresh kobject reread changes one bounded fact inside the same packet:

- `scripts/zigux/README.md` still compresses the live kobject packet to a narrower note-plus-sample-plus-tests shape, so the next same-packet follow-through is one scripts-root wording repair that keeps `zigux/tests/phase5_kobject_example_manifest.json` explicit beside the survey note, sample, focused test, public-tree-backed survey replay, and public-tree-backed `zigux/tests/phase5_build.zig` route
- authenticated contents readback starts returning `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` too, so this note can drop the connector-flakiness warning and treat the broader packet as both public-tree-backed and connector-readable

Do not widen that follow-up into sample behavior unless the sample-root file, focused test, manifest-backed contract, dedicated survey replay, or shared build route actually changes.