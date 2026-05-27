# Phase 5 rbtree sample repo reality check

Date: 2026-05-27
Lane: P5-L21

## Scope

This note records the exact repo-state checks used to verify the current `samples/zigux` posture for a requested Phase 5 `rbtree`-style sample.

## Exact checks

1. Roadmap scope check
   - Read `agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md`.
   - Verified that Phase 5 is scoped to four non-runtime sample anchors only:
     - `samples/kfifo/bytestream-example.c`
     - `samples/kobject/kobject-example.c`
     - `samples/kprobes/kretprobe_example.c`
     - `samples/trace_events/trace-events-sample.c`

2. Sample-root inventory check
   - Read `samples/zigux/README.md` on `master`.
   - Verified that the current sample-root inventory names the shipped sample and companion files and does not list a standalone `samples/zigux/*rbtree*` sample.
   - Verified the existing `No-extra-sample reminders` section already says current `master` still ships no standalone Phase 5 sample-root file for `*rbtree*`.

3. Public tree readback check
   - Read the public `samples/zigux` tree page on `master`.
   - Verified that the visible file list contains the Phase 5 bytestream, kobject, kretprobe, and trace-events packets plus Phase 9 runtime packets, with no `rbtree`-named sample file in the directory.

4. Direct contents probe
   - Requested `samples/zigux/rbtree_style_sample.zig` from the repository contents API on `master`.
   - Result: `404 Not Found`.
   - Interpretation: there is no shipped file at that representative sample path.

5. Phase 5 build-route check
   - Read `zigux/tests/phase5_build.zig` on `master`.
   - Verified that the wired Phase 5 routes cover only the bytestream FIFO, kobject, kretprobe, and trace-events sample families and their bounded companions.
   - Verified that there is no `rbtree` sample module, focused replay shard, survey shard, or aggregate Phase 5 route entry.

6. Neighboring helper-lane separation check
   - Read `tools/lib/rbtree.zig` on `master`.
   - Verified that Zigux does ship a host/helper-side `rbtree` implementation with tests, but that file lives outside `samples/zigux` and belongs to a helper lane rather than a Phase 5 sample-root lane.

## Result

Current `master` does not ship a standalone Phase 5 `rbtree`-style sample under `samples/zigux`.

The present repo evidence supports this narrower statement instead:
- Phase 5 sample-root coverage remains centered on the four approved sample families.
- `rbtree` evidence currently exists in the helper lane through `tools/lib/rbtree.zig`, not as a sample-root packet.
- There is no current sample-local Phase 5 validation route to rerun for `rbtree`, because no Phase 5 `samples/zigux/*rbtree*` sample is wired into `zigux/tests/phase5_build.zig`.

## Validation note

This lane completed exact repo-state verification and documentation only.

No Zig compile or `zig test` run was performed for a Phase 5 `rbtree` sample, because the verification showed that no such shipped sample file or Phase 5 build route currently exists on `master`.

## Next bounded step

If Phase 5 needs a future `rbtree`-style sample at all, treat it as new roadmap discussion first rather than as a missing validation rerun. Until that scope changes, keep `rbtree` work tied to the helper-side lane and keep the sample-root reminder truthful about the absence of a standalone Phase 5 `rbtree` sample.
