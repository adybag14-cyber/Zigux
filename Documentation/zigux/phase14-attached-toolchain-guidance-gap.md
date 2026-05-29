# Phase 14 Attached Toolchain Guidance Gap

## Scope

- lane: `P14-L10 / P14-L12`
- phase: `Phase 14`
- packet: shared attached-toolchain and environment-guidance reminder packet for the bounded Phase 14 smoke route
- status: `current-master reminder truthfulness follow-through; P14-L12 attached-toolchain replay addendum`
- refreshed: `2026-05-29`

## Why this note exists

The Phase 14 roadmap keeps the shared smoke packet in a study-only, reviewability-first posture. That means rerun guidance must stay exact about the attached Zig toolchain, the current `zigux/Makefile` route surface, and the missing Phase 14 wrapper targets. This note is an environment truthfulness note, not a new bridge, parity, ownership, or release-readiness claim.

## Current attached-toolchain readback

Fresh builder-environment validation on `2026-05-29` confirms that the attached Zig bundle used by this lane still behaves like a usable bounded-check fallback rather than a stale archival assumption:

- unpacking `agent_files/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz` into `/workspace/.toolchains/p14-l10/` succeeded without extra environment overrides
- `/workspace/.toolchains/p14-l10/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig version` returned `0.17.0-dev.87+9b177a7d2`
- `/workspace/.toolchains/p14-l10/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig env` reported `.lib_dir = ".toolchains/p14-l10/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/lib"`, `.global_cache_dir = "/root/.cache/zig"`, `.version = "0.17.0-dev.87+9b177a7d2"`, and `.target = "x86_64-linux.6.12.47...6.12.47-gnu.2.39"`
- no `ZIG_GLOBAL_CACHE_DIR`, `ZIG_LOCAL_CACHE_DIR`, `ZIG_LIB_DIR`, `ZIG_LIBC`, `CC`, or related Zig environment override was set during that readback

This local replay does not change repo status. It only proves that the attached bundle remains a valid bounded fallback for this scheduled-builder environment when a focused Zig syntax or build check is otherwise justified.

## P14-L12 operational replay addendum

The P14-L12 scheduled run repeated the attached-toolchain replay on `2026-05-29` before changing this note. That replay adds operational evidence without widening Phase 14 delivery scope:

- unpacking the same attached archive into `/workspace/.toolchains/p14-l12/` succeeded in the current scheduled-builder environment
- `/workspace/.toolchains/p14-l12/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig version` returned `0.17.0-dev.87+9b177a7d2`
- `/workspace/.toolchains/p14-l12/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig env` reported `.zig_exe = "/workspace/.toolchains/p14-l12/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig"`, `.lib_dir = ".toolchains/p14-l12/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/lib"`, `.std_dir = ".toolchains/p14-l12/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/lib/std"`, `.global_cache_dir = "/root/.cache/zig"`, and `.version = "0.17.0-dev.87+9b177a7d2"`
- the replay still showed no `ZIG_GLOBAL_CACHE_DIR`, `ZIG_LOCAL_CACHE_DIR`, `ZIG_LIB_DIR`, `ZIG_LIBC`, `CC`, `C_INCLUDE_PATH`, `CPLUS_INCLUDE_PATH`, or `LIBRARY_PATH` override in the toolchain environment

The only conclusion from this addendum is operational: future Phase 14 runs may keep using the attached bundle for narrow Zig syntax or focused build checks when a checkout is available, but this evidence does not create a new Phase 14 Make route or change any study-only or freeze-in-C posture.

## Current Makefile readback

Fresh authenticated readback of current `master` keeps the route split narrow:

- `zigux/Makefile` still resolves `ZIG` through `ZIG_PINNED_TOOLCHAIN`, a staged `.zig-toolchain/*/zig` candidate, or finally `zig` on `PATH`
- the readable Phase 14 Make route remains `phase14-validate`
- the broader `phase14-smoke`, `phase14-test`, and `phase14` Make targets are still absent and must stay historical packet-local or repo-reality-gap vocabulary
- manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides are optional packet-local escape hatches, not the primary current rerun path when a checkout can stage the bundle where the Makefile already looks for it

This refresh intentionally removes the older route-family shorthand that said the live Makefile exposed a selected list of shipped phase routes. That shorthand was not the important P14-L10 claim and had started to obscure the exact current boundary: Phase 14 exposes one shared validation route, while other phase route names include a mix of recipe-backed targets and phony entries outside this lane.

## Aligned reminder surfaces

The current same-lane reminder family should continue to say only this:

- `Documentation/zigux/phase14-end-to-end-smoke-survey.md` may reference older `phase14-*` names only as historical packet-local rerun vocabulary unless a future Makefile change lands those targets
- `Documentation/zigux/phase14-release-boundary-survey.md` should keep the same single-gate posture and avoid restating the attached-toolchain triplet as current fallback guidance
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` should keep the readable `phase14-validate` route, the returned checker-backed shared-smoke packet, and the study-only or freeze-in-C posture explicit without promoting missing executable-layer paths
- the dedicated skbuff, ring-buffer, and RCU checkers stay part of the bounded shared reminder family only where current validators or manifests already require them

## Why this matters

This is still an operational-truthfulness issue rather than a delivery claim:

- the roadmap says Phase 14 stays bounded, study-only, and reviewability-first
- the bootstrap ledger favors exact rerun guidance over implied routes
- the attached toolchain is part of the scheduled-builder environment for bounded Zig validation
- stale route shorthand can make future runs reopen already-closed reminder work or imply a broader Phase 14 executable surface than current `master` actually exposes

## Smallest honest same-lane conclusion

The attached-toolchain boundary itself is not the gap. The attached bundle still extracts cleanly and reports the expected Zig version.

The active same-lane discipline is keeping environment and route wording exact:

1. prefer the staged pinned-toolchain path that the Makefile already detects when a checkout can stage the bundle
2. use a manual `ZIG=/absolute/path/to/attached-zig/zig` override only as an explicit packet-local fallback
3. keep `make -C zigux phase14-validate` as the only current Phase 14 Make route
4. keep `phase14-smoke`, `phase14-test`, and `phase14` out of current fallback guidance until those Make targets exist on `master`
5. do not treat attached-toolchain availability as proof of deep-core execution ownership, parity, or release-readiness

## Non-goals

- do not reopen workqueue, ring-buffer, skbuff, or RCU packet contents
- do not introduce a new Phase 14 replay route
- do not imply any live deep-core execution ownership or status change
- do not widen into Phase 15 freeze-map governance
