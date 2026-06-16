const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn requireMarker(source: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, source, marker) == null) {
        return error.MissingMarker;
    }
}

fn requireOrdered(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingMarker;
    try std.testing.expect(first_index < second_index);
}

test "lane03 toolchain checker keeps executable status output explicit" {
    const checker = try readRepoFile("scripts/zigux/check_zig_toolchain.zig");
    defer std.testing.allocator.free(checker);

    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_STATUS=invalid\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_STATUS=missing\"");
    try requireMarker(checker, "policy.evaluateToolchainVersion");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_STATUS={s}\", .{resolver.toolchainStatusName(evaluation.status)});");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_PATH={s}\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_MIN_SUPPORTED={s}\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_PINNED_CHANNEL={s}\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_PIN_POLICY=exact\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_PIN_POLICY=unresolved\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_SEARCH_ROOTS={s}\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_NOTE={s}\"");
    try requireOrdered(
        checker,
        "version = resolver.readZigVersion(io, allocator, zig.?) catch |err|",
        "const evaluation = try policy.evaluateToolchainVersion(",
    );
}

test "lane03 toolchain checker keeps archive status output explicit" {
    const checker = try readRepoFile("scripts/zigux/check_zig_toolchain.zig");
    defer std.testing.allocator.free(checker);

    try requireMarker(checker, "--archive-only");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_ARCHIVE_STATUS={s}\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_ARCHIVE_PATH={s}\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_ARCHIVE_TARGET={s}\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={s}\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={s}\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={s}\"");
    try requireMarker(checker, "printLine(io, \"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={s}\"");
    try requireMarker(checker, "return if (options.allow_missing) 0 else 1");
    try requireOrdered(
        checker,
        "resolver.describeInvalidExplicitArchivePath(io, allocator, archive_path.?)",
        "printLine(io, \"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={s}\"",
    );
}

test "lane03 self-test covers status and archive failure cases" {
    const checker = try readRepoFile("scripts/zigux/check_zig_toolchain.zig");
    defer std.testing.allocator.free(checker);

    try requireMarker(checker, "resolver.readZigVersion");
    try requireMarker(checker, "runSelfTest(io, allocator)");
    try requireMarker(checker, "policy.evaluateToolchainVersion");
    try requireMarker(checker, "resolver.validatePolicyArchive");
    try requireMarker(checker, "describeInvalidExplicitArchivePath");
    try requireMarker(checker, "describeMissingArchive");
    try requireMarker(checker, "describeMissingZig");
}