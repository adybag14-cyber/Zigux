# Phase 3 Rbtree Boundary

This packet adds one bounded Phase 3 binding step for the `lib/rbtree` roadmap anchor without widening into traversal helpers or another wrapper family.

## Status

- `PHASE3_RBTREE_STATUS=active`
- `PHASE3_RBTREE_SCOPE=root-view-only`
- `PHASE3_RBTREE_BOUNDARY_HEADER=include/zigux/rbtree.h`
- `PHASE3_RBTREE_BINDING=zigux/bindings/rbtree.zig`
- `PHASE3_RBTREE_TEST_GATE=zig build phase3-rbtree-test --build-file zigux/tests/phase3_rbtree_build.zig`
- `PHASE3_RBTREE_DUMP_GATE=zig build phase3-rbtree-dump --build-file zigux/tests/phase3_rbtree_build.zig`
- `PHASE3_RBTREE_DIFF_GATE=python3 scripts/zigux/check-phase3-rbtree.py`

## Why this slice exists

The Phase 3 roadmap still names `lib/rbtree.c` as one of the core boundary anchors.

Current Zigux Phase 3 work already covers several view and planning families, but it does not yet carry a small dedicated rbtree-facing binding surface. This packet closes that exact gap with one compact root-summary ABI shape:

- `root_addr`: pointer-sized address of the current root node
- `leftmost_addr`: cached leftmost node address when the producer can provide it
- `flags`: explicit empty or cached state markers
- `reserved`: forced zero so future expansion stays reviewable

## Rules

- keep this packet root-view only for now
- do not add node traversal, mutation, or balancing helpers here
- leave `include/zigux/abi.h` untouched until a later Phase 3 consolidation packet is justified
- require C and Zig dump parity before widening the view shape
