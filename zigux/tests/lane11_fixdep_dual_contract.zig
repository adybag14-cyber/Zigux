const std = @import("std");

const FixdepCase = struct {
    name: []const u8,
    depfile: []const u8,
    target: []const u8,
    cmdline: []const u8,
    expected: []const u8,
    expected_stderr: ?[]const u8 = null,
    expected_exit_code: u8,
};

fn readFileAlloc(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn expectFileContains(path: []const u8, needle: []const u8) !void {
    const bytes = try readFileAlloc(path, 512 * 1024);
    defer std.testing.allocator.free(bytes);

    try std.testing.expect(std.mem.indexOf(u8, bytes, needle) != null);
}

fn hasCase(cases: []const FixdepCase, name: []const u8) bool {
    for (cases) |case| {
        if (std.mem.eql(u8, case.name, name)) return true;
    }
    return false;
}

test "lane11 fixdep dual implementation keeps the live implementation and checker packet" {
    try expectFileContains("scripts/basic/fixdep.c", "parse_config_file");
    try expectFileContains("scripts/zigux/fixdep.zig", "pub fn runFixdep");
    try expectFileContains("scripts/zigux/fixdep.zig", "fn parseDepFile");
    try expectFileContains("scripts/zigux/check-fixdep-diff.py", "FIXDEP_DIFF=pass");
    try expectFileContains("scripts/zigux/check-fixdep-diff.py", "FIXDEP_DETERMINISM=pass");
    try expectFileContains("scripts/zigux/check-phase2-fixdep-gate.py", "PHASE2_FIXDEP_GATE=pass");
    try expectFileContains("scripts/zigux/check-phase2-fixdep-gate.py", "PHASE2_FIXDEP_GATE_SELF_TEST=pass");
}

test "lane11 fixdep fixture manifest keeps the bounded parity cases named" {
    const manifest_json = try readFileAlloc("zigux/tests/fixtures/fixdep/cases.json", 64 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice([]FixdepCase, std.testing.allocator, manifest_json, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const cases = parsed.value;

    try std.testing.expect(cases.len >= 12);
    try std.testing.expect(hasCase(cases, "sample"));
    try std.testing.expect(hasCase(cases, "sample_multi_target"));
    try std.testing.expect(hasCase(cases, "sample_escaped_space"));
    try std.testing.expect(hasCase(cases, "sample_escaped_colon"));
    try std.testing.expect(hasCase(cases, "sample_concatenated"));
    try std.testing.expect(hasCase(cases, "sample_dependency_continuation"));
    try std.testing.expect(hasCase(cases, "sample_comment_continuation"));
    try std.testing.expect(hasCase(cases, "sample_comment_only"));
    try std.testing.expect(hasCase(cases, "sample_missing_dep"));
    try std.testing.expect(hasCase(cases, "sample_output_write"));
}
