# Phase 12 Libbpf Segment Survey

This document records the bounded Phase 12 survey lane around `tools/lib/bpf/libbpf.c` and the existing `tools/lib/bpf/zigux_segments/` rollout.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=libbpf-segment-survey`
- scope: Phase 12 survey manifest, dedicated survey gate, shared build wiring, and a lane note that compares the current `zigux_segments/` footing against the roadmap's heavy-helper consumer plan
- product boundary:
  - `zigux/tests/phase12_libbpf_manifest.json`
  - `zigux/tests/phase12_libbpf_segments.zig`
  - `zigux/tests/phase12_libbpf_reviewability.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`

## Why this slice exists

The roadmap now places `tools/lib/bpf/libbpf.c` in Phase 12, alongside the other high-risk production-facing consumers, because the file is both large and semantically dense even though it lives under `tools/`.

That matters because the live repo already has real helper-first progress under `tools/lib/bpf/zigux_segments/`: a segment catalog, dense type-name tables, a CPU-mask helper with the deferred chunk-reader path for sysfs-style buffered input, a bounded logging helper, and bounded bpffs pin-path helpers. Those are useful footholds, but they still need a current Phase 12 survey checkpoint that explains how the earlier helper work fits the modern roadmap instead of leaving libbpf stranded in older Phase 8 wording or stale Phase 12 reviewability assumptions.

The highest-value honest step in this lane is therefore a survey checkpoint that records the existing segmented footing, keeps the Phase 12 build gate aware of it, verifies that the landed helper files still match the segment plan, and points to the next helper-sized slice without widening into object loading, relocation, or syscall-backed behavior.

This checkpoint has now been re-verified against current `master` head `a61c5a2e199c76045061acfe6dcf83853ef53071`, with the same landed helper set and the same blocked skeleton and loader split still holding.

## Survey findings

- `tools/lib/bpf/libbpf.c` is present on `master` at 14,771 lines, which is large enough to cross helper, loader, object-model, relocation, and verifier-facing concerns in one file.
- the live repo already ships the earlier `tools/lib/bpf/zigux_segments/manifest.json` survey plus four landed helper slices:
  - `type_names.zig` for exported attach, link, map, and program type string tables
  - `cpu_mask.zig` for bounded CPU-mask parsing, set-bit counting, and a deferred reader interface that still stops short of direct file I/O
  - `logging.zig` for bounded print-level parsing, version reporting, and libbpf-specific error text formatting
  - `pin_path.zig` for bounded bpffs path joining, pin-name and root-path validation, and dot-sanitization without directory or syscall parity
- the earlier Phase 8 tooling lane proved that helper-first segmentation works for libbpf, but the current roadmap places the broader heavy-consumer rollout in Phase 12 because the remaining work depends on object-model discipline, loader boundaries, and high-risk validation gates.
- the current Phase 12 build now re-checks the landed helper-first foundations directly by compiling `type_names.zig`, `cpu_mask.zig`, `logging.zig`, and `pin_path.zig` through a reviewability gate and by confirming that the manifest's landed versus deferred file expectations match the real `tools/lib/bpf/zigux_segments/` directory.
- the repo still has no `skeleton.zig`, `object_loader.zig`, or relocation-facing Zig slice, and it still intentionally avoids direct ELF collection, `bpf_object` parity, BTF relocation, and load-time verifier interactions.
- the current risk split is now explicit again: `skeleton.zig` remains the nearest post-helper cluster but is still blocked on the missing object model, while loader and program-load work stay deferred as the heavier follow-on after that boundary.
- with the bounded helper-first utility slices now landed, the next honest libbpf-facing step is to keep reviewability aligned and avoid collapsing the nearer skeleton-population blocker into the broader loader risk unless fresh repo reality changes the actual segment boundaries.

## Recorded gaps

The survey manifest now records:

- the landed `phase12-build-gate`
- the landed `phase12-make-target`
- the landed `phase12-libbpf-segment-manifest-foundation`
- the landed `phase12-libbpf-type-name-helper-foundation`
- the landed `phase12-libbpf-cpu-mask-helper-foundation`
- the landed `phase12-libbpf-logging-helper-foundation`
- the landed `phase12-libbpf-pin-path-helper-foundation`
- the landed `phase12-libbpf-survey-gate`
- the landed `phase12-libbpf-reviewability-gate`
- the landed `phase12-libbpf-survey-note`
- the still-blocked `phase12-libbpf-skeleton-population`
- the still-blocked `phase12-libbpf-object-loader-and-program-load`

This keeps the lane explicit without overstating progress: Zigux already has real libbpf helper footholds, including the deferred CPU-mask reader path plus bounded logging and pin-path validation helpers, but the heavy helper consumer still stops first at the missing skeleton or object-model boundary and then well short of loader, relocation, or syscall-backed surfaces.

## Rollback And Reversible Delivery

- owner: `BPF Tooling Lane`
- rollback owner: `BPF Tooling Lane`
- fallback path: keep `tools/lib/bpf/libbpf.c` as the source of truth, keep the already-landed `type_names.zig`, `cpu_mask.zig`, `logging.zig`, and `pin_path.zig` helper slices on their bounded helper footing, and drop the Phase 12 libbpf survey packet back out of `zigux/tests/phase12_build.zig` if the shared reviewability packet regresses.
- reversible delivery evidence: this Phase 12 packet only adds `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, and this survey note around preexisting helper foundations, so the survey can be removed without inventing a second libbpf implementation or mutating `tools/lib/bpf/libbpf.c`.
- rollback drill: run `make -C zigux phase12-validate`; if the libbpf survey packet is the only failing slice, remove the `phase12-libbpf-segment-survey-tests` and `phase12-libbpf-reviewability-tests` entries from `zigux/tests/phase12_build.zig`, keep the C anchor and landed helper files unchanged, then rerun `make -C zigux phase12-validate` followed by `zig build test --build-file zigux/tests/phase12_build.zig --summary all` so the shared Phase 12 packet stays truthful while the libbpf survey note or gate is repaired.

## Non-goals

This survey slice does not claim:

- direct Zig parity for `tools/lib/bpf/libbpf.c`
- object-model parity for `bpf_object`, `bpf_map`, or `bpf_program`
- ELF collection or object loading
- BTF relocation recording
- load-time verifier interactions
- syscall-backed libbpf runtime behavior

## Gates

1. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig`

2. run the convenience target
- `make -C zigux phase12`

## Next bounded step

Keep the Phase 12 libbpf survey and reviewability lane aligned with the live helper set and the current blocked-risk split, and only reopen `tools/lib/bpf/zigux_segments/` for another bounded utility slice if fresh repo reality shows something materially smaller than the still-blocked skeleton, loader, and relocation work.
