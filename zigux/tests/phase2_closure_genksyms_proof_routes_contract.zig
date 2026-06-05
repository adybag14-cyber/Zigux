const std = @import("std");

const closure_path = "Documentation/zigux/phase2-closure.md";
const manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";
const makefile_path = "zigux/Makefile";

const proof_paths = [_][]const u8{
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "scripts/zigux/genksyms_inline_short_option_argument_test.zig",
    "scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig",
    "scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig",
};

fn readRepoFile(path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn expectExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    try std.testing.expectEqual(expected, count);
}

test "phase 2 closure genksyms standalone proof packet is named across closure and manifest" {
    const closure = try readRepoFile(closure_path);
    defer std.testing.allocator.free(closure);

    const manifest = try readRepoFile(manifest_path);
    defer std.testing.allocator.free(manifest);

    try expectContains(closure, "standalone proof packet carried by the shipped bridge route");
    try expectContains(manifest, "standalone invalid-long-option, ambiguous-long-option, inline-short-option, repeated-version, and abbreviated-warning terminator proofs");

    for (proof_paths) |path| {
        try expectContains(closure, path);
        try expectContains(manifest, path);
    }

    try expectOrder(
        closure,
        proof_paths[0],
        proof_paths[proof_paths.len - 1],
    );
    try expectOrder(
        manifest,
        proof_paths[0],
        proof_paths[proof_paths.len - 1],
    );
}

test "phase 2 Makefile runs every genksyms standalone proof under phase2-genksyms" {
    const makefile = try readRepoFile(makefile_path);
    defer std.testing.allocator.free(makefile);

    try expectContains(makefile, "phase2-genksyms: phase2-toolchain");
    try expectContains(makefile, "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig");

    var previous_index = std.mem.indexOf(
        u8,
        makefile,
        "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig",
    ) orelse return error.MissingBaseGenksymsRoute;
    for (proof_paths) |path| {
        const prefix = "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test ";
        var line_buffer: [160]u8 = undefined;
        const route = try std.fmt.bufPrint(&line_buffer, "{s}{s}", .{ prefix, path });

        try expectContains(makefile, route);
        try expectExactCount(makefile, route, 1);
        const route_index = std.mem.indexOf(u8, makefile, route) orelse return error.MissingProofRoute;
        try std.testing.expect(previous_index < route_index);
        previous_index = route_index;
    }

    const alignment_index = std.mem.indexOf(
        u8,
        makefile,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    ) orelse return error.MissingAlignmentRoute;
    try std.testing.expect(previous_index < alignment_index);
}

test "phase 2 closure keeps genksyms proof packet before aggregate replay routes" {
    const closure = try readRepoFile(closure_path);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "zig test scripts/zigux/genksyms.zig");
    try expectContains(closure, "make -C zigux phase2-genksyms");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");

    try expectOrder(
        closure,
        proof_paths[proof_paths.len - 1],
        "zig test scripts/zigux/genksyms.zig",
    );
    try expectOrder(
        closure,
        "zig test scripts/zigux/genksyms.zig",
        "make -C zigux phase2-genksyms",
    );
    try expectOrder(
        closure,
        "make -C zigux phase2-genksyms",
        "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain",
    );
}
