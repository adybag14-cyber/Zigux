# Phase 3 List/HList Slice

This slice makes the bounded list and hlist interop route reviewable on a
current-head-safe branch.

Scope

- keep the helper packet limited to traversal shape, length, and link-consistency checks
- reuse the shared list/hlist binding packet so the layout contract stays explicit beside the dump
- avoid callback, container-of, mutation, or subsystem-specific ownership claims

Packet

- `Documentation/zigux/phase3-list-hlist-slice.md`
- `include/zigux/list_hlist.h`
- `zigux/uapi/list_hlist.zig`
- `zigux/bindings/list_hlist.zig`
- `zigux/helpers/list_view.zig`
- `zigux/helpers/hlist_view.zig`
- `zigux/tests/phase3_list_hlist_dump.zig`
- `zigux/tests/phase3_list_hlist_dump_build.zig`
- `zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c`
- `zigux/tests/fixtures/phase3_list_hlist/expected.json`
- `zigux/tests/fixtures/phase3_list_hlist_manifest.json`
- `scripts/zigux/check-phase3-list-hlist.py`

Replay routes

- `python3 scripts/zigux/check-phase3-list-hlist.py --self-test`
- `python3 scripts/zigux/check-phase3-list-hlist.py --repo-root . --zig zig --cc gcc`
- `zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig`

Why this packet exists

- the lane already had split helper-only and binding-only review paths
- live `master` still lacked the fixture-backed dump route that proves the list and hlist views agree with a C harness
- this slice lands the shared dump, expected fixture, C harness, and checker route without widening into broader Phase 3 reminder or shared tests-root work