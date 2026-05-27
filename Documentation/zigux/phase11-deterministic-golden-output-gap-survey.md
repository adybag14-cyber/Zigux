# Phase 11 Deterministic Golden-Output Tooling Gap Survey

This note records the current deterministic fixture-refresh and golden-output
tooling gap for the shared Phase 11 simple-driver packet on `master`.

## Status

- `PHASE11_DETERMINISTIC_TOOLING_GAP_STATUS=refresh_route_and_artifact_diff_guard_missing`
- lane: `P11-L07`
- phase: `Phase 11`
- scope: keep the roadmap-facing deterministic tooling gap explicit without
  widening into driver-local execution, broader shared-manifest ownership, or
  unrelated reminder-surface churn

## Roadmap Anchor

Phase 11 still covers the bounded simple-production-driver packet around
`gpio_wdt`, `bcm2835_wdt`, `dw_wdt`, and `hvc_console`.

The roadmap still expects:

- a hardware validation matrix
- teardown or failure-mode parity
- machine-reviewable validation tooling instead of reminder-only claims

For this lane, that means the shared validator packet needs to stay honest about
what it can inventory today and what it still cannot refresh or diff.

## Current Deterministic Packet

Current `master` already ships the narrower machine-readable deterministic
surfaces through:

- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/fixtures/phase11_validate_checks.json`
- `zigux/tests/phase11_dw_wdt_manifest.json`

The shared route is now:

- `scripts/zigux/validate-phase11.py`
- `make -C zigux phase11-validate`

The shared packet also keeps the focused teardown-or-failure-mode proof builds
explicit through:

- `zigux/tests/phase11_hvc_modem_control_proof_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
- `zigux/tests/phase11_dw_wdt_restart_build.zig`
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`

The shared validator roster already fail-closes around the current route and
check inventory through:

- `scripts/zigux/check-phase11-validate-check-roster.py`
- `scripts/zigux/check-phase11-validate-route-alignment.py`

## Live Gap Versus The Roadmap

Current `master` can prove that the bounded Phase 11 proof builds still compile
and that the validator roster still names the expected checks.

Current `master` still does not ship:

- a dedicated refresh helper route for shared Phase 11 expected outputs
- an artifact-diff-style deterministic output guard for the driver-local proof
  builds

That leaves the live deterministic gap narrower than the older missing-validator
story but still real against the roadmap: the shared packet is inventory-backed
and build-proof-first, yet it cannot refresh and diff stable golden outputs for
the same bounded driver packet.

## Review Rules

- Do not claim that golden-output refresh tooling already exists just because
  `phase11-validate` and the focused build fan-out exist.
- Keep this lane scoped to deterministic tooling truthfulness, not driver
  behavior.
- Treat `zigux/tests/fixtures/phase11_validate_checks.json` as a validator
  roster, not as proof that refresh or artifact-diff tooling already landed.

## Next Bounded Step

If a dedicated refresh helper route or artifact-diff-style guard lands later,
update this note together with the machine-readable deterministic packet in the
same bounded pass.
