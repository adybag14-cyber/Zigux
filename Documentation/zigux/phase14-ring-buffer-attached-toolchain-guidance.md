# Phase 14 Ring Buffer Attached Toolchain Guidance

## Scope
- lane: `P14-L08`
- phase: `Phase 14`
- packet posture: `packet_local_only`
- anchor: `kernel/trace/ring_buffer.c`

## Why this companion exists
The Phase 14 roadmap keeps the ring-buffer lane in a study-only, reviewability-first posture.
That means the attached Zig bundle can help future scheduled runs check whether the builder runtime still has a usable compiler, but it must not be confused with proof that the ring-buffer packet was replayed from a checkout-capable Zigux tree.

This companion keeps that operational boundary explicit in one small place.
It narrows the guidance to the ring-buffer packet and avoids reopening the broader shared Phase 14 reminder surfaces.

## Attached bundle
- attached archive name: `agent_files/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz`
- lane-local extraction command example: `mkdir -p /workspace/.toolchains/p14-l08 && tar -xf "/workspace/agent_files/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz" -C /workspace/.toolchains/p14-l08`
- run-local extraction example: `/workspace/.toolchains/p14-l08/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2`
- compiler version expected after extraction: `0.17.0-dev.87+9b177a7d2`

## Environment-only sanity checks
If the run has the attached archive but no checkout-capable Zigux tree, stop at environment-only sanity checks:
- `/workspace/.toolchains/p14-l08/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig version`
- `/workspace/.toolchains/p14-l08/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig env`

Passing those checks confirms that the attached compiler bundle is usable in the scheduled builder runtime.
Do not treat them as ring-buffer replay evidence without a checkout-capable Zigux tree in the same run.

## Replay boundary
Keep the packet-local replay vocabulary subordinate to that environment rule:
- `zig test zigux/tests/phase14_ring_buffer_survey.zig`
- `zig build test --build-file zigux/tests/phase14_build.zig --summary all`

Only count those commands as completed evidence when the checkout-capable tree and the attached toolchain are available together.
If the same run can only read the repo through GitHub and local bundle extraction, record the toolchain as environment context only.

## Shared route reminder
This lane-local note does not restore the older wrapper family.
The readable shared route surface still centers on `make -C zigux phase14-validate`, while `phase14-smoke`, `phase14-test`, and `phase14` remain outside the current returned Makefile route split.

## Non-goals
- do not treat bundle extraction alone as a ring-buffer replay
- do not imply `kernel/trace/ring_buffer.zig`
- do not reopen the shared attached-toolchain reminder packet
- do not claim a new Phase 14 Makefile route
