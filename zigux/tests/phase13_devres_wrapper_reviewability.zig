const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase13 devres direct ioremap wrapper family stays explicit and individually covered" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const devres_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "lib/devres.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(devres_source);

    try expectContains(devres_source, "pub fn planManagedIoremapAcquirePlain(");
    try expectContains(devres_source, "pub fn planManagedIoremapAcquireUc(");
    try expectContains(devres_source, "pub fn planManagedIoremapAcquireWc(");
    try expectContains(devres_source, "pub fn planManagedIoremapAcquireNp(");
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, devres_source, "fn planManagedIoremapAcquireForKind("));

    const devres_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(devres_tests);

    try expectContains(devres_tests, "test \"phase13 devres plain ioremap wrapper preserves the managed lifetime path\"");
    try expectContains(devres_tests, "test \"phase13 devres plain ioremap wrapper frees the release record on map failure\"");
    try expectContains(devres_tests, "test \"phase13 devres uncached ioremap wrapper forces the uncached lifetime path\"");
    try expectContains(devres_tests, "test \"phase13 devres uncached ioremap wrapper frees the release record on map failure\"");
    try expectContains(devres_tests, "test \"phase13 devres write-combined ioremap wrapper forces the write-combined lifetime path\"");
    try expectContains(devres_tests, "test \"phase13 devres write-combined ioremap wrapper frees the release record on map failure\"");
    try expectContains(devres_tests, "test \"phase13 devres non-posted ioremap wrapper forces the non-posted lifetime path\"");
    try expectContains(devres_tests, "test \"phase13 devres non-posted ioremap wrapper frees the release record on map failure\"");
    try expectContains(devres_tests, "planManagedIoremapAcquirePlain(");
    try expectContains(devres_tests, "planManagedIoremapAcquireUc(");
    try expectContains(devres_tests, "planManagedIoremapAcquireWc(");
    try expectContains(devres_tests, "planManagedIoremapAcquireNp(");

    const phase13_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(phase13_build);

    try expectContains(phase13_build, "phase13_devres_wrapper_reviewability.zig");
    try expectContains(phase13_build, "phase13-devres-wrapper-reviewability-tests");

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-devres-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "- `zigux/tests/phase13_devres_wrapper_reviewability.zig`");
    try expectContains(survey_note, "`zigux/tests/phase13_devres_wrapper_reviewability.zig` now source-scans `lib/devres.zig` for the direct plain, UC, WC, and NP managed ioremap wrapper entrypoints");
    try expectContains(survey_note, "the direct plain, UC, WC, and NP managed ioremap wrapper family plus its dedicated survey-visible reviewability gate");
}
