# Phase 5 Kobject Sample Survey

This note tracks the bounded Phase 5 verification packet for the roadmap's `samples/kobject/kobject-example.c` anchor.

## Status

- `PHASE5_STATUS=verified-current-checks`
- `PHASE5_LANE_KEY=P5-L20`
- scope: verify current kobject sample behavior and record the exact checks that still define the non-runtime packet on `master`
- current directly verified kobject packet on `master`:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `samples/zigux/README.md`

## Why this note exists

The roadmap's Phase 5 target is still "Samples and Reference Patterns" and still names `samples/kobject/kobject-example.c` as one of the approved Linux anchors.

The bounded job for this note is to record the current kobject behavior that the directly verified replay surfaces still enforce on `master`. The same-lane task is no longer to repeat the older missing-path caveat. The current packet already carries the focused test and manifest-backed exact checks; this note should describe those checks plainly so review work stays inside the landed kobject packet.

## Current verified behavior on `master`

Fresh repo-first inspection on 2026-05-13 confirmed that the current directly verified kobject packet still keeps these sample behaviors explicit:

- `zigux/tests/phase5_kobject_example.zig` still keeps the descriptor contract explicit for the `samples/kobject/kobject-example.c` anchor, including the in-memory `kobject_example` directory name, `requires_runtime_substrate = false`, and `provides_selfcheck = true`
- `runAnchorReplay()` still requires `init()` first, registers exactly three attributes, leaves the sample in the registered stage, keeps the attribute group unnamed, keeps the shared `baz` and `bar` handlers explicit, and still reads back default values `42`, `7`, and `-5` for `foo`, `baz`, and `bar`
- `runPreRegistrationBoundaryReplay()` still keeps the sample initialized, keeps `active_attr_count` at zero, and keeps pre-registration `show` and `store` rejection explicit
- calling `init()` twice still keeps the sample initialized, leaves `active_attr_count` at zero, and returns `InvalidLifecycleTransition` on the second init without advancing `register_runs` or `exit_runs`
- `runRegisteredBoundaryReplay()` still keeps the sample registered with three active attributes, keeps `init_runs = 1`, `register_runs = 1`, and `exit_runs = 0`, rejects duplicate registration and registered-stage anchor replay, and still allows a bounded `foo` write/read roundtrip afterward
- `runInputValidationReplay()` still keeps the sample registered while storing `9` into `baz` and `10` into `bar`, keeps invalid integer writes on `foo` rejected, leaves the `foo` value at `0` after the failed parse, and keeps unknown-attribute `show` and `store` rejection explicit
- `runOwnershipReplay()` still keeps the lifecycle packet explicit across the cold, initialized, registered, and exited snapshots, including active attribute counts `0`, `0`, `3`, and `0` and the counter progression `0/0/0`, `1/0/0`, `1/1/0`, and `1/1/1`
- the initialized-only exit path still reports `abandoned_before_registration`, while the registered exit path still reports `tore_down_registered_attributes`
- `runTeardownReplay()` still keeps the registered teardown reset explicit by clearing tracked values from `42`, `7`, and `-5` to `0`, `0`, and `0`, dropping the active attribute count back to zero, and rejecting reinit, reregister, post-exit `show`, post-exit `store`, second `exit()`, and post-exit anchor replay
- the public sample-facing replay surface still keeps direct `InvalidInteger` and `UnknownAttribute` failures visible through the focused test instead of hiding them behind survey wording alone

## Exact checks recorded today

The current manifest-backed exact checks for the kobject packet are now recorded here as the same bounded review contract this note should preserve:

- `directory-name`: the in-memory sample keeps the Linux directory name `kobject_example` and an unnamed attribute group
- `registration-step`: `runAnchorReplay()` requires `init()` first, registers exactly three attributes, leaves the sample in the registered stage, and keeps duplicate `registerAttributes()` plus registered-stage `runAnchorReplay()` calls blocked by `InvalidLifecycleTransition`
- `pre-registration-boundary`: `runPreRegistrationBoundaryReplay()` leaves the sample initialized, keeps the active attribute count at zero, and shows that `show` or `store` still return `InvalidLifecycleTransition` before `registerAttributes()` opens the sample
- `single-init-boundary`: calling `init()` twice keeps the sample initialized, leaves the active attribute count at zero, and returns `InvalidLifecycleTransition` on the second init without advancing `register_runs` or `exit_runs`
- `registered-boundary`: `runRegisteredBoundaryReplay()` leaves the sample registered, keeps the active attribute count at three, keeps `register_runs` pinned at one across duplicate registration plus registered-stage anchor-replay rejection, and still allows a bounded `foo` write/read roundtrip afterward
- `ownership-summary`: `ownershipSummary()` and `runOwnershipReplay()` report the cold, initialized, registered, and exited stages with active attribute counts `0`, `0`, `3`, and `0`
- `ownership-counters`: `runOwnershipReplay()` keeps the init/register/exit progression explicit as `0/0/0`, `1/0/0`, `1/1/0`, and `1/1/1`
- `initialized-exit-disposition`: `exit()` reports `abandoned_before_registration` when the sample leaves the initialized stage before attributes are registered
- `foo-roundtrip`: storing `42` into `foo` renders back as the string `42` followed by a newline
- `shared-b-dispatch`: `runInputValidationReplay()` keeps `baz` and `bar` on the same `show` and `store` path while rendering `9` and `10` through their own attribute names after the replay stores those exact values
- `parse-failure`: `runInputValidationReplay()` keeps invalid-integer writes returning `InvalidInteger` and unknown attribute names as explicit errors while the sample remains in the registered stage
- `exit-boundary`: `runTeardownReplay()` reports `tore_down_registered_attributes`, clears the tracked values, removes the active attribute count, and keeps reinit, reregister, post-exit `show` and `store`, second `exit()`, and anchor-replay rejection explicit

## Recorded gap vs roadmap

The roadmap still calls for a reviewable Phase 5 kobject reference-pattern anchor, and the current kobject packet still satisfies that bounded goal through the focused test plus manifest-backed replay contract.

The honest same-lane gap was review-note drift: this survey note had fallen behind the current packet and was still missing the now-explicit one-time init ownership boundary even though the focused test and manifest already kept it reviewable. This refresh closes that note-only gap without widening the sample surface.

## Non-goals

This note still does not claim:

- sysfs file creation parity
- `kernel_kobj` integration
- uevent delivery
- loadable module registration

## Next bounded step

Leave this lane parked unless a fresh kobject sample reread shows behavior drift inside the current packet. If the behavior changes, refresh this survey note and `zigux/tests/phase5_kobject_example_manifest.json` together, then rerun the shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` route when a writable checkout is available.
