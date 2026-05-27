const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    const io = std.testing.io;
    return std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        std.testing.allocator,
        .limited(128 * 1024),
    );
}

fn expectContains(contents: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, contents, needle) != null);
}

test "phase 8 verify routing witness records the current CPU-index verifier closure" {
    const helper = try readRepoFile("tools/lib/bpf/zigux_segments/online_cpu_routing.zig");
    defer std.testing.allocator.free(helper);

    try expectContains(helper, "pub fn resolveNextOnlineCpuRouteCpuIndex(");
    try expectContains(helper, "pub fn resolveNextOnlineCpuRouteCpuIndexAtIndex(");
    try expectContains(helper, "pub fn resolveNextOnlineCpuRouteCpuIndexReturn(summary: OnlineCpuRouteAttemptSummary) i32 {");
    try expectContains(helper, "pub fn resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(");
    try expectContains(helper, "test \"resolveNextOnlineCpuRouteCpuIndex keeps typed route-cpu wrappers aligned\" {");
    try expectContains(helper, "test \"resolveNextOnlineCpuRouteCpuIndexReturn keeps errno-shaped route-cpu wrappers aligned\" {");
    try expectContains(helper, "test \"resolveNextOnlineCpuRouteCpuIndexAtIndex keeps direct route-cpu wrappers aligned\" {");
    try expectContains(helper, "test \"resolveNextOnlineCpuRouteCpuIndexReturnAtIndex keeps direct errno-shaped route-cpu wrappers aligned\" {");

    const verify = try readRepoFile("tools/lib/bpf/zigux_segments/verify.zig");
    defer std.testing.allocator.free(verify);

    try expectContains(verify, "resolveNextOnlineCpuRouteBufferFdReturnAtIndex");
    try expectContains(verify, "resolveNextOnlineCpuRouteCpuIndex");
    try expectContains(verify, "resolveNextOnlineCpuRouteCpuIndexAtIndex");
    try expectContains(verify, "resolveNextOnlineCpuRouteCpuIndexReturn");
    try expectContains(verify, "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex");
    try expectContains(verify, "test \"materialized tools/lib/bpf Zigux segments keep stable online-CPU route-fd wrappers explicit\" {");
    try expectContains(verify, "test \"materialized tools/lib/bpf Zigux segments keep stable online-CPU route-cpu wrappers explicit\" {");
}

test "phase 8 verify routing witness records the current dedicated verifier shards" {
    const online_cpu_verify = try readRepoFile(
        "tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig",
    );
    defer std.testing.allocator.free(online_cpu_verify);

    try expectContains(
        online_cpu_verify,
        "test \"phase8 online-cpu route helpers keep typed cpu-index wrappers stable\" {",
    );
    try expectContains(online_cpu_verify, "resolveNextOnlineCpuRouteCpuIndex(");
    try expectContains(online_cpu_verify, "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(");
    try expectContains(
        online_cpu_verify,
        "test \"phase8 online-cpu route helpers keep typed buffer-fd wrappers stable\" {",
    );
    try expectContains(online_cpu_verify, "resolveNextOnlineCpuRouteBufferFd(");
    try expectContains(
        online_cpu_verify,
        "test \"phase8 online-cpu route helpers keep errno-shaped buffer-fd wrappers stable\" {",
    );
    try expectContains(online_cpu_verify, "resolveNextOnlineCpuRouteBufferFdReturn(");
    try expectContains(
        online_cpu_verify,
        "test \"phase8 online-cpu route helpers fail closed when a hand-built CPU index exceeds i32\" {",
    );

    const online_cpu_bridge_verify = try readRepoFile(
        "tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig",
    );
    defer std.testing.allocator.free(online_cpu_bridge_verify);

    try expectContains(
        online_cpu_bridge_verify,
        "test \"phase8 online-cpu routing mask bridge entrypoints stay explicit\" {",
    );
    try expectContains(
        online_cpu_bridge_verify,
        "summarizeNextOnlineCpuRouteFromString(",
    );
    try expectContains(
        online_cpu_bridge_verify,
        "resolveNextOnlineCpuRouteCpuIndexFromReader(",
    );
    try expectContains(
        online_cpu_bridge_verify,
        "resolveNextOnlineCpuRouteBufferFdReturnFromReader(",
    );
    try expectContains(
        online_cpu_bridge_verify,
        "test \"phase8 online-cpu routing mask bridge keeps route failures explicit across mask-backed wrappers\" {",
    );

    const ready_buffer_attempt_verify = try readRepoFile(
        "tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig",
    );
    defer std.testing.allocator.free(ready_buffer_attempt_verify);

    try expectContains(
        ready_buffer_attempt_verify,
        "test \"phase8 ready-buffer attempt helper entrypoints stay explicit\" {",
    );
    try expectContains(ready_buffer_attempt_verify, "resolveReadyBufferAttemptIndex(");
    try expectContains(ready_buffer_attempt_verify, "resolveReadyBufferAttemptLookupReturn(");

    const ready_buffer_fd_verify = try readRepoFile(
        "tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig",
    );
    defer std.testing.allocator.free(ready_buffer_fd_verify);

    try expectContains(
        ready_buffer_fd_verify,
        "test \"phase8 ready-buffer fd helper entrypoints stay explicit\" {",
    );
    try expectContains(ready_buffer_fd_verify, "resolveReadyBufferFdAtAttempt");
    try expectContains(ready_buffer_fd_verify, "resolveReadyBufferFdLookupReturnAtAttempt");

    const ready_buffer_window_verify = try readRepoFile(
        "tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig",
    );
    defer std.testing.allocator.free(ready_buffer_window_verify);

    try expectContains(
        ready_buffer_window_verify,
        "test \"phase8 ready-buffer window helper entrypoints stay explicit\" {",
    );
    try expectContains(
        ready_buffer_window_verify,
        "resolveReadyBufferWindowMappedSizeAtAttempt",
    );
    try expectContains(
        ready_buffer_window_verify,
        "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
    );
    try expectContains(
        ready_buffer_window_verify,
        "resolveReadyBufferWindowLookupReturnAtAttempt",
    );

    const type_names_verify = try readRepoFile(
        "tools/lib/bpf/zigux_segments/type_names_verify.zig",
    );
    defer std.testing.allocator.free(type_names_verify);

    try expectContains(
        type_names_verify,
        "test \"phase8 libbpf type-name helper entrypoints stay explicit\" {",
    );
    try expectContains(type_names_verify, "libbpfBpfMapTypeStr(27)");
    try expectContains(type_names_verify, "formatLibbpfBpfProgType(prog_buffer[0..], 33)");
}

test "phase 8 verify routing witness records the current direct-readback libbpf survey packet" {
    const survey = try readRepoFile("Documentation/zigux/phase8-libbpf-segment-survey.md");
    defer std.testing.allocator.free(survey);

    try expectContains(survey, "`tools/lib/bpf/zigux_segments/verify.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/cpu_mask.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/cpu_mask_verify.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/logging.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/logging_verify.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/pin_path.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/pin_path_verify.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/type_names.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/type_names_verify.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`");
    try expectContains(survey, "`tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`");
    try expectContains(
        survey,
        "The directly readable stable-output helper set therefore now keeps the aggregate verifier plus `cpu_mask.zig`, `cpu_mask_verify.zig`, `logging.zig`, `logging_verify.zig`, `pin_path.zig`, `pin_path_verify.zig`, `type_names.zig`, `type_names_verify.zig`, `perf_buffer_poll.zig`, `perf_buffer_poll_verify.zig`, `perf_buffer_ready_window.zig`, `online_cpu_routing.zig`, `online_cpu_routing_mask_bridge.zig`, `online_cpu_routing_mask_bridge_verify.zig`, `online_cpu_routing_verify.zig`, `ready_buffer_attempt_verify.zig`, `ready_buffer_fd_verify.zig`, and `ready_buffer_window_verify.zig` explicit.",
    );
    try expectContains(
        survey,
        "`tools/lib/bpf/zigux_segments/cpu_mask_verify.zig` now keeps direct parse, string-backed summary, reader-backed summary, auto-count, and fail-closed cpu-mask outputs explicit beside that same stable-output helper packet.",
    );
    try expectContains(
        survey,
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig` now keeps wait classification, poll summary, execution summary, and impossible-summary fail-closed outputs explicit beside that same stable-output helper packet.",
    );
    try expectContains(
        survey,
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig` keeps `advanceOnlineCpuCursor()`, `summarizeNextOnlineCpuRoute()`, and `summarizeOnlineCpuRouting()` explicit as bounded helper-local review surfaces below the still-deferred setup-side routing boundary.",
    );
    try expectContains(
        survey,
        "`tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig` now keeps `summarizeNextOnlineCpuRouteFromString()`, `summarizeNextOnlineCpuRouteFromReader()`, `resolveNextOnlineCpuRouteCpuIndexFromString()`, `resolveNextOnlineCpuRouteCpuIndexFromReader()`, `resolveNextOnlineCpuRouteBufferFdFromString()`, and `resolveNextOnlineCpuRouteBufferFdFromReader()` explicit as cpu-mask-backed helper-local routing bridges below the still-deferred setup-side routing boundary.",
    );
    try expectContains(
        survey,
        "The directly readable verifier packet now also keeps dedicated stable-output witnesses for cpu-mask parse, string-backed summary, reader-backed summary, auto-count, and fail-closed outputs, online-CPU mask-bridge next-route CPU-index and buffer-FD wrappers, logging env/version/error outputs, perf-buffer wait-classification, poll-summary, execution-summary, and impossible-summary fail-closed outputs, pin-path map/program output and validation wrappers, online-CPU route CPU-index and buffer-FD wrappers, ready-buffer attempt wrappers, ready-buffer FD wrappers, ready-buffer window mapped-size and lookup-return wrappers, and type-name lookup plus formatter wrappers explicit beside the aggregate `verify.zig` replay surface.",
    );
    try expectContains(
        survey,
        "The remaining repo-reality gap in this note is no longer a helper-local code omission. It is reminder-surface discipline: older bridge, manifest, and focused build names may still appear in shared Phase 8 vocabulary, but this survey should now treat the manifest, the two bridge reminder docs, the bridge helper, and the focused bridge witness as direct-readback companion evidence, while the focused bridge-only build shard stays outside the exact stable-output helper set.",
    );
    try expectContains(
        survey,
        "That older mixed-source wording now needs the same caution: the bridge-side reminder docs, the bridge helper, and the focused bridge witness stay reviewable on current `master`, but the focused bridge-only build shard still stays outside the exact stable-output helper set because it documents the deferred bridge boundary rather than extending helper semantics.",
    );
    try expectContains(
        survey,
        "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit.",
    );
}

test "phase 8 verify routing witness records the current mixed-source bridge reminder packet" {
    const survey = try readRepoFile("Documentation/zigux/phase8-libbpf-segment-survey.md");
    defer std.testing.allocator.free(survey);

    try expectContains(
        survey,
        "That same reminder-side bridge test packet in `zigux/tests/phase8_file_path_handle_bridge.zig` now also keeps the Linux-style replay route, the manifest-backed split between the landed `fdinfo-path-and-reuse-name-footholds`, `fdinfo-map-info-helpers`, and `map-reuse-compatibility` helper slices plus the deferred `file-path-and-handle-bridge` resource boundary, and the source-level ban on `bpf_obj_get(`, `F_DUPFD_CLOEXEC`, and direct file-open bridge-heavy calls explicit on current `master`.",
    );
    try expectContains(
        survey,
        "`tools/lib/bpf/zigux_segments/manifest.json` has since advanced both `fdinfo-map-info-helpers` and `map-reuse-compatibility` as landed helper-first slices with the newer shared bridge rationale, so the smallest same-family reminder drift is now whether sibling reminder surfaces continue to reflect those same landed `why_now` strings whenever they restate the focused bridge packet.",
    );
    try expectContains(
        survey,
        "That focused libbpf-segment shard is currently carried by `zigux/tests/phase8_verify_routing_gap.zig` plus `zigux/tests/phase8_verify_routing_gap_only_build.zig`, which keep the bounded online-CPU route CPU-index witness explicit without widening into setup-side routing, reopen-flow, or bridge-heavy claims.",
    );

    const manifest = try readRepoFile("tools/lib/bpf/zigux_segments/manifest.json");
    defer std.testing.allocator.free(manifest);

    try expectContains(
        manifest,
        "\"slug\": \"fdinfo-map-info-helpers\",\n      \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow.\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"map-reuse-compatibility\",\n      \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"fdinfo-path-and-reuse-name-footholds\",\n      \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"This materializes the shared bridge destination with side-effect-free pathname shaping and bounded reused-map name retention while keeping procfs reads, fdinfo parsing, and reuse comparison logic deferred.\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"file-path-and-handle-bridge\",\n      \"status\": \"deferred_high_risk\",\n      \"kind\": \"resource_boundary\"",
    );

    const bridge_test = try readRepoFile("zigux/tests/phase8_file_path_handle_bridge.zig");
    defer std.testing.allocator.free(bridge_test);

    try expectContains(
        bridge_test,
        "phase 8 file-path handle bridge proof keeps the manifest-backed helper and deferred bridge split explicit",
    );
    try expectContains(
        bridge_test,
        "phase 8 file-path handle bridge helper stays wired into the Linux-style replay routes",
    );
    try expectContains(bridge_test, "planning-only `resolveReusePinnedMapAttempt()` gating");
    try expectContains(bridge_test, "planning-only `planTokenPreparation()` gating");
}
