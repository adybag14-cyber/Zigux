# Zigux Contributor Workflow Guide

Use this note when you need one stable developer-facing workflow for Zigux product work instead of reconstructing the process from scattered phase notes.

This guide is a shared contributor aid. It is not a tranche-closure note, not a substitute for helper-local ownership notes, and not a reason to invent replay routes that current `master` does not ship.

## Purpose

Keep contributor work aligned with the roadmap-backed Zigux packet structure:

- choose work from the current roadmap phase and bounded lane
- reread the shared reminder surfaces before touching helper-local or driver-local notes
- trust current `master` replay routes only when the repo actually ships them
- keep freeze-map boundaries and repo-reality gaps explicit instead of smoothing them over

## Stable Entry Surfaces

Open these four files together before choosing or reviewing a change:

1. `Documentation/zigux/README.md`
2. `Documentation/zigux/review-checklist.md`
3. `scripts/zigux/README.md`
4. `zigux/tests/README.md`

Treat that set as the stable contributor-facing handle for shared workflow questions.

Use the roadmap and freeze-map owners alongside that handle:

- `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
- `Documentation/zigux/freeze-map.md`

## How To Pick Work

Use this triage order:

1. pick the roadmap phase and the bounded lane you are actually touching
2. decide whether the task is shared reminder work, helper-local proof, driver-local proof, or closure evidence
3. keep the change in the smallest packet that can tell the truth
4. if the repo does not ship a route, helper, manifest, or replay on current `master`, leave it in the repo-reality-gap bucket instead of promoting it into shipped evidence

If the work starts feeling like a new packet, a new wrapper chain, or a large reminder-surface fan-out, stop and narrow the task before editing.

## Pre-Edit Loop

Before editing:

1. reread the four stable entry surfaces
2. reread the exact phase note or helper-local note you plan to change
3. check whether `Documentation/zigux/freeze-map.md` applies
4. confirm the current replay path from `zigux/Makefile`, `scripts/zigux/README.md`, or a phase-local validator note
5. keep the change to one shared reminder surface or one helper-local packet unless repo truthfulness clearly requires both

## Replay Route Rules

Prefer the narrowest current replay route that `master` already ships.

Current routed families on `master` include:

- `make -C zigux phase1-route-summary`
- `make -C zigux phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, `phase2-validate`, `phase2`
- `make -C zigux phase3-validate`, `phase3`
- `make -C zigux phase4-validate`, `phase4-test`, `phase4`
- `make -C zigux phase6-validate`
- `make -C zigux phase7-validate`, `phase7-rbtree-test`, `phase7-rbtree-survey`
- `make -C zigux phase8-validate`, `phase8-exec-cmd-test`, `phase8-help-test`, `phase8-help-kallsyms-test`, `phase8-kallsyms-test`, `phase8-libbpf-segments-test`, `phase8-file-path-handle-bridge-test`, `phase8-perf-buffer-poll-test`, `phase8-test`, `phase8`
- `make -C zigux phase9-runtime-atomic64-test`, `phase9-runtime-bitmap-test`, `phase9-runtime-loader-shared-test`, `phase9-runtime-loader-command-env-boundary-guard-test`, `phase9-runtime-trace-events-test`, `phase9-runtime-kretprobe-test`, `phase9-first-loadable-runtime-module-parity-test`, `phase9-test`
- `make -C zigux phase10-validate`, `phase10-test`, `phase10`
- `make -C zigux phase11-validate`
- `make -C zigux phase12-validate`, `phase12-smoke`, `phase12-test`, `phase12-virtio-net-syntax-lab-test`, `phase12`
- `make -C zigux phase14-validate`

Current route gaps still matter:

- `zigux/Makefile` does not currently ship `make -C zigux phase13-validate` or `make -C zigux phase13`
- `zigux/Makefile` does not currently ship `make -C zigux phase15-validate`, `phase15-test`, or `phase15`

When a route is absent, fall back to the exact validator or checker note already named by the phase packet. Do not rewrite docs as if the missing Makefile route exists.

## Validation Order

When a task changes shared docs, checklist, or workflow wording, validate in this order:

1. phase-local checker or validator named by the phase packet
2. shared reminder-surface checker from `scripts/zigux/README.md`
3. tests-root alignment checker from `zigux/tests/README.md` when the packet names one
4. a Makefile route only if the route is present on current `master`

If local replay is unavailable in the runtime, record validation as exact readback and route inspection rather than implying a local rerun.

## Freeze-Map Rule

If a task touches or summarizes:

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

route that work back through `Documentation/zigux/freeze-map.md` first.

Do not present freeze-in-C or study-only anchors as active delivery proof just because a neighboring packet gained better docs, a checker, or a replay route.

## Degraded-Read Fallback

If local checkout access is unavailable:

1. reread the stable entry surfaces through GitHub app reads first
2. reread only the exact phase or helper-local file you plan to change
3. inspect the current route surface from `zigux/Makefile` or the phase validator note
4. keep validation language honest about readback-only verification
5. keep any still-missing route or helper recorded as a repo-reality gap

## Non-Goals

This guide does not:

- replace phase-local ownership notes
- close any phase tranche
- add a new replay route
- justify wrapper proliferation
- turn repo-reality gaps into shipped evidence
