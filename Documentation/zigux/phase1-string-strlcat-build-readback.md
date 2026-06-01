# Phase 1 string `strlcat` build readback

This note records the bounded `P1-L15` readback for `tools/lib/string.zig` on 2026-05-30. It is intentionally narrow: it verifies the current direct `strlcat` anchor and build-route wiring without reopening the separate helper-local `memparse` compatibility lane.

## Current blobs read

- `tools/lib/string.zig`: blob `4b6d6e201d9892103935bbf08f130ec8bce3bcbb`
- `tools/lib/string_phase1_strlcat_test.zig`: blob `1572caba35237c981ad82884660ea412464528af`
- `zigux/tests/build.zig`: blob `db3d21e99804c0b34f949c00a97b491725215fd1`

## Build-route evidence

Authenticated readback of `zigux/tests/build.zig` showed that the shared tests root still defines `addPhase1StringDirectAnchor(...)` with:

- root source `../../tools/lib/string_phase1_strlcat_test.zig`
- test artifact name `phase1-string-direct-anchor`
- build step name `phase1-string-direct-anchor`

The same file also continues to add `../../tools/lib/string.zig` as the `string` module inside `addPhase1HostToolsSmoke(...)`, so the helper remains wired into the broader `phase1-host-tools-smoke` route as well.

## Exact focused check run

Because this runtime could not clone or raw-fetch the full repository over the network (`CONNECT tunnel failed, response 403`), the check used authenticated GitHub readback plus a scratch Zig replay containing the exact current `strlcat` body from `tools/lib/string.zig` blob `4b6d6e201d9892103935bbf08f130ec8bce3bcbb` and the four direct-anchor test bodies from `tools/lib/string_phase1_strlcat_test.zig` blob `1572caba35237c981ad82884660ea412464528af`.

Command:

```sh
/workspace/.toolchains/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3/zig test /workspace/tmp_p1_l15_string/string_strlcat_current_replay.zig
```

Observed result:

```text
1/4 string_strlcat_current_replay.test.phase1 string strlcat stops at the first source terminator...OK
2/4 string_strlcat_current_replay.test.phase1 string strlcat leaves the destination stable for an empty C-string source...OK
3/4 string_strlcat_current_replay.test.phase1 string strlcat treats an unterminated destination as full...OK
4/4 string_strlcat_current_replay.test.phase1 string strlcat handles a zero-length destination buffer...OK
All 4 tests passed.
```

## Boundary

This readback confirms the current bounded `strlcat` direct-anchor behavior and current build-route wiring. It does not claim a full `phase1-host-tools-smoke` run, because the live repository checkout was unavailable in this runtime. The separate string `memparse` unit-tail compatibility repair remains outside this readback and should stay with its helper-local lane.
