# Phase 3 Notifier Chain Slice

This slice closes a bounded shared-subsystems gap around `zigux/helpers/notifier_chain_view.zig`.

Scope

- keep the packet focused on traversal order, chain length, and nonincreasing-priority checks
- reuse `zigux/bindings/notifier_abi.zig` as the shared ABI anchor for the bounded sample chain
- keep the replay small enough to review without joining the wider chrdev helper-plan churn

Packet

- `zigux/helpers/notifier_chain_view.zig`
- `zigux/bindings/notifier_abi.zig`
- `zigux/tests/phase3_notifier_chain_dump.zig`
- `zigux/tests/fixtures/phase3_notifier_chain/expected.json`
- `zigux/tests/fixtures/phase3_notifier_chain/phase3_notifier_chain_c_harness.c`
- `scripts/zigux/check-phase3-notifier-chain.py`

Review gate

- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug notifier-chain`

Why this packet exists

- the helper was already present on `master`, but it was not yet backed by a discoverable Phase 3 slice packet
- this packet turns that helper into a reusable shared-subsystems replay instead of leaving it as an orphaned implementation detail
