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

test "phase 8 libbpf-segment compatibility witness keeps the focused verify-routing replay visible" {
    const routed_review_witness = try readRepoFile("zigux/tests/phase8_verify_routing_gap.zig");
    defer std.testing.allocator.free(routed_review_witness);

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            routed_review_witness,
            "phase 8 verify routing witness records the current CPU-index verifier closure",
        ) != null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            routed_review_witness,
            "phase 8 verify routing witness records the current direct-readback libbpf survey packet",
        ) != null,
    );

    const routed_review_build = try readRepoFile("zigux/tests/phase8_verify_routing_gap_only_build.zig");
    defer std.testing.allocator.free(routed_review_build);

    try std.testing.expect(
        std.mem.indexOf(u8, routed_review_build, "phase8_verify_routing_gap.zig") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, routed_review_build, "phase8_verify_routing_gap") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(
            u8,
            routed_review_build,
            "Run the phase 8 verify routing witness tests.",
        ) != null,
    );
}

test "phase 8 libbpf-segment compatibility witness keeps the shared no-timer poll boundary explicit" {
    const survey = try readRepoFile("Documentation/zigux/phase8-libbpf-segment-survey.md");
    defer std.testing.allocator.free(survey);

    try std.testing.expect(
        std.mem.indexOf(
            u8,
            survey,
            "The timing-adjacent poll boundary is already explicit through `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `make -C zigux phase8-perf-buffer-poll-test`; those reminder surfaces keep the packet honest about no standalone timer or clockevent helper behavior and about no broader timeout-sensitive routing behavior.",
        ) != null,
    );

    const bridge_boundary = try readRepoFile(
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    );
    defer std.testing.allocator.free(bridge_boundary);

    try std.testing.expect(
        std.mem.indexOf(u8, bridge_boundary, "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, bridge_boundary, "`python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, bridge_boundary, "`make -C zigux phase8-perf-buffer-poll-test`") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, bridge_boundary, "standalone timer helper behavior") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, bridge_boundary, "standalone clockevent helper behavior") != null,
    );

    const poll_slice = try readRepoFile("Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer std.testing.allocator.free(poll_slice);

    try std.testing.expect(
        std.mem.indexOf(u8, poll_slice, "no standalone timer helper behavior") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, poll_slice, "no standalone clockevent helper behavior") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, poll_slice, "broader perf-buffer-online-cpu-routing parity") != null,
    );

    const poll_gate = try readRepoFile("scripts/zigux/check-phase8-perf-buffer-poll-gate.py");
    defer std.testing.allocator.free(poll_gate);

    try expectContains(poll_gate, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    try expectContains(poll_gate, "no standalone timer helper behavior");
    try expectContains(poll_gate, "no standalone clockevent helper behavior");
    try expectContains(poll_gate, "broader perf-buffer-online-cpu-routing parity");

    const validator = try readRepoFile("scripts/zigux/validate-phase8.py");
    defer std.testing.allocator.free(validator);

    try expectContains(
        validator,
        "PERF_BUFFER_POLL_GATE_CHECKER = Path(\"scripts/zigux/check-phase8-perf-buffer-poll-gate.py\")",
    );
    try expectContains(
        validator,
        "\"`Documentation/zigux/phase8-perf-buffer-poll-slice.md`\"",
    );
    try expectContains(
        validator,
        "\"`make -C zigux phase8-perf-buffer-poll-test`\"",
    );
    try expectContains(
        validator,
        "\"no standalone timer helper behavior\"",
    );
    try expectContains(
        validator,
        "\"no standalone clockevent helper behavior\"",
    );

    const makefile = try readRepoFile("zigux/Makefile");
    defer std.testing.allocator.free(makefile);

    try std.testing.expect(
        std.mem.indexOf(u8, makefile, "phase8-perf-buffer-poll-test") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, makefile, "phase8-test") != null,
    );
    try std.testing.expect(
        std.mem.indexOf(u8, makefile, "phase8: phase8-validate") != null,
    );
}

test "phase 8 libbpf-segment compatibility witness keeps the mixed-source bridge packet visible" {
    const bridge_review_witness = try readRepoFile("zigux/tests/phase8_file_path_handle_bridge.zig");
    defer std.testing.allocator.free(bridge_review_witness);

    try expectContains(
        bridge_review_witness,
        "phase 8 file-path handle bridge proof keeps helper-local routing evidence smaller than deferred setup-side routing",
    );
    try expectContains(
        bridge_review_witness,
        "phase 8 file-path handle bridge proof keeps the current libbpf survey reminder-only bridge split explicit",
    );
    try expectContains(
        bridge_review_witness,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    );
    try expectContains(
        bridge_review_witness,
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    );
    try expectContains(
        bridge_review_witness,
        "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
    );
    try expectContains(
        bridge_review_witness,
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    );

    const shared_build = try readRepoFile("zigux/tests/phase8_build.zig");
    defer std.testing.allocator.free(shared_build);

    try expectContains(
        shared_build,
        "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    );
    try expectContains(shared_build, "phase8_file_path_handle_bridge.zig");
    try expectContains(shared_build, "phase8_libbpf_segments.zig");
    try expectContains(shared_build, "phase8_verify_routing_gap.zig");
    try expectContains(shared_build, "Run the shared Phase 8 tooling tests.");

    const tests_readme = try readRepoFile("zigux/tests/README.md");
    defer std.testing.allocator.free(tests_readme);

    try expectContains(
        tests_readme,
        "current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:",
    );
    try expectContains(
        tests_readme,
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
    );
    try expectContains(
        tests_readme,
        "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
    );
    try expectContains(
        tests_readme,
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
    );
    try expectContains(
        tests_readme,
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
    );
}

test "phase 8 libbpf-segment compatibility witness keeps stable-output verifier shards visible" {
    const survey = try readRepoFile("Documentation/zigux/phase8-libbpf-segment-survey.md");
    defer std.testing.allocator.free(survey);

    try expectContains(
        survey,
        "`tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`",
    );
    try expectContains(
        survey,
        "`tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`",
    );
    try expectContains(
        survey,
        "`tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`",
    );
    try expectContains(
        survey,
        "`tools/lib/bpf/zigux_segments/type_names_verify.zig`",
    );

    const aggregate_verify = try readRepoFile("tools/lib/bpf/zigux_segments/verify.zig");
    defer std.testing.allocator.free(aggregate_verify);

    try expectContains(
        aggregate_verify,
        "const ready_buffer_attempt_verify = @import(\"ready_buffer_attempt_verify.zig\");",
    );
    try expectContains(
        aggregate_verify,
        "const ready_buffer_fd_verify = @import(\"ready_buffer_fd_verify.zig\");",
    );
    try expectContains(
        aggregate_verify,
        "const ready_buffer_window_verify = @import(\"ready_buffer_window_verify.zig\");",
    );
    try expectContains(
        aggregate_verify,
        "const type_names_verify = @import(\"type_names_verify.zig\");",
    );

    const online_cpu_verify = try readRepoFile("tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig");
    defer std.testing.allocator.free(online_cpu_verify);
    try expectContains(
        online_cpu_verify,
        "phase8 online-cpu route helpers keep typed buffer-fd wrappers stable",
    );
    try expectContains(
        online_cpu_verify,
        "resolveNextOnlineCpuRouteBufferFdAtIndex(",
    );
    try expectContains(
        online_cpu_verify,
        "phase8 online-cpu route helpers keep errno-shaped buffer-fd wrappers stable",
    );
    try expectContains(
        online_cpu_verify,
        "resolveNextOnlineCpuRouteBufferFdReturnAtIndex(",
    );
    try expectContains(
        online_cpu_verify,
        "phase8 online-cpu route helpers fail closed when a hand-built CPU index exceeds i32",
    );
    try expectContains(
        online_cpu_verify,
        "resolveNextOnlineCpuRouteCpuIndexReturn(impossible)",
    );

    const attempt_verify = try readRepoFile("tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig");
    defer std.testing.allocator.free(attempt_verify);
    try expectContains(
        attempt_verify,
        "phase8 ready-buffer attempt helpers keep errno-shaped outputs stable",
    );

    const fd_verify = try readRepoFile("tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig");
    defer std.testing.allocator.free(fd_verify);
    try expectContains(
        fd_verify,
        "phase8 ready-buffer fd helpers keep errno-shaped outputs stable",
    );

    const window_verify = try readRepoFile("tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig");
    defer std.testing.allocator.free(window_verify);
    try expectContains(
        window_verify,
        "phase8 ready-buffer window helpers keep lookup-return outputs stable",
    );

    const type_verify = try readRepoFile("tools/lib/bpf/zigux_segments/type_names_verify.zig");
    defer std.testing.allocator.free(type_verify);
    try expectContains(
        type_verify,
        "phase8 libbpf type-name formatters still fail closed on short buffers",
    );
}
