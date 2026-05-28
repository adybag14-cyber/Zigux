# Phase 7 Rbtree Slice

The current helper-local packet on `master` covers cached-leftmost insertion, cached replacement, cached non-leftmost erase, singleton cached erase, and plain erase-init reset and reseed boundaries after root removal.

The current helper-local replay keeps these proofs explicit:
- cached-leftmost promotion, non-leftmost cached erase, singleton cached erase, plain erase-init reseed, and cached-churn invariants boundaries stay reviewable through the dedicated replay, the parity checker, the returned JSON fixture, and the returned C harness
- the readable legacy companion at `tools/lib/rbtree.zig` now stays reviewable only while its reverse-traversal alias, postorder alias, and plain erase-init markers remain readable beside the direct helper packet
- public-fallback provenance stays explicit through the now-empty `public_fallback_non_owner_paths` field in `zigux/tests/phase7_rbtree_manifest.json`, because `zigux/tests/phase7_build.zig` and the other listed legacy or shared non-owner surfaces all rematerialized through authenticated rereads in this slot

## Next Bounded Step

Keep same-lane follow-through inside this slice-backed direct-helper packet by leaving `zigux/tests/fixtures/phase7_rbtree.json` and `zigux/tests/fixtures/phase7_rbtree_c_harness.c` reviewable as returned parity evidence, including the non-leftmost cached erase, singleton cached erase, plain erase-init reseed, and cached-churn invariants cases, while keeping the readable legacy `tools/lib/rbtree.zig` companion aligned on the reverse-traversal alias, postorder alias, and plain erase-init markers and keeping the returned `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers aligned with `zigux/tests/phase7_build.zig`.
