const std = @import("std");

fn readFileAlloc(path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(max_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase9 first-loadable parity note tracks returned family-local loader companions without overclaiming shared parity" {
    const parity_note = try readFileAlloc(
        "../../Documentation/zigux/phase9-first-loadable-runtime-module-parity.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(parity_note);

    const atomic64_loader = try readFileAlloc(
        "../../samples/zigux/runtime_atomic64_loader.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(atomic64_loader);

    const bitmap_loader = try readFileAlloc(
        "../../samples/zigux/runtime_bitmap_loader.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(bitmap_loader);

    const kretprobe_loader = try readFileAlloc(
        "../../samples/zigux/runtime_kretprobe_loader.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(kretprobe_loader);

    try expectContains(parity_note, "`PHASE9_STATUS=active`");
    try expectContains(parity_note, "`PHASE9_SLICE=first-loadable-runtime-module-parity`");
    try expectContains(parity_note, "`PHASE9_LANE_KEY=P9-L01`");
    try expectContains(
        parity_note,
        "returned atomic64 and kretprobe direct packets with their family-local loader companions",
    );
    try expectContains(
        parity_note,
        "the atomic64 and kretprobe sides return direct packets with family-local loader companions",
    );
    try expectContains(parity_note, "`samples/zigux/runtime_atomic64_loader.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_kretprobe_loader.zig`");
    try expectContains(
        parity_note,
        "Current `master` now directly materializes the atomic64 sample, family-local loader companion, survey, and manifest packet",
    );
    try expectContains(
        parity_note,
        "Current `master` now directly materializes the kretprobe sample, family-local loader companion, and module lifecycle packet",
    );
    try expectContains(
        parity_note,
        "the atomic64 side now exposes a direct trusted-path packet around the sample, family-local loader companion, module, diff, survey, manifest, and family-local notes",
    );
    try expectContains(
        parity_note,
        "the kretprobe side now exposes a direct trusted-path packet around the sample, family-local loader companion, module-boundary lifecycle replay, and shared build shard",
    );
    try expectContains(parity_note, "the build-local `phase9-runtime-atomic64-loader-tests` route name");
    try expectContains(parity_note, "the build-local `phase9-runtime-kretprobe-loader-tests` route name");
    try expectContains(
        parity_note,
        "must not claim shipped cross-family loader parity, shipped runtime-loader handoff parity, or shipped end-to-end module lifecycle parity on current `master`.",
    );
    try expectContains(
        parity_note,
        "broader shared loader completion surfaces still remain absent on the same trusted path",
    );

    try expectContains(
        atomic64_loader,
        "runtime atomic64 loader keeps loader-facing seed and descriptor explicit",
    );
    try expectContains(
        atomic64_loader,
        "runtime atomic64 loader keeps loaded seed stable through selftest and exit",
    );
    try expectContains(
        atomic64_loader,
        "runtime atomic64 loader keeps blocked publication and depmod surfaces out of the loader-facing payload",
    );

    try expectContains(
        bitmap_loader,
        "runtime bitmap loader keeps loader-facing bitmap payload explicit",
    );
    try expectContains(
        bitmap_loader,
        "runtime bitmap loader keeps loaded cross-word summary stable through selftest and exit",
    );
    try expectContains(
        bitmap_loader,
        "runtime bitmap loader rejects malformed loader payloads without leaving initialized state",
    );

    try expectContains(
        kretprobe_loader,
        "runtime kretprobe loader keeps initialized-stage shared contract plans explicit",
    );
    try expectContains(
        kretprobe_loader,
        "runtime kretprobe loader keeps invalid loader transitions fail-closed without disturbing shared-request snapshots",
    );
    try expectContains(
        kretprobe_loader,
        "runtime kretprobe loader keeps selftest-complete shared requests blocked by the current loader family contract",
    );
}
