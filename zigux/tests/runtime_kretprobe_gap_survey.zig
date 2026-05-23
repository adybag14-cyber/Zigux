const std = @import("std");

fn readRepoFileAlloc(path: []const u8, max_bytes: usize) ![]u8 {
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

fn expectMissing(path: []const u8) !void {
    try std.testing.expectError(error.FileNotFound, readRepoFileAlloc(path, 1024));
}

test "phase9 runtime kretprobe gap survey matches current repo reality" {
    const gap_note = try readRepoFileAlloc(
        "../../Documentation/zigux/phase9-runtime-kretprobe-gap-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(gap_note);

    const sequencing_note = try readRepoFileAlloc(
        "../../Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(sequencing_note);

    const samples_readme = try readRepoFileAlloc(
        "../../samples/zigux/README.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(samples_readme);

    const phase5_sample = try readRepoFileAlloc(
        "../../samples/zigux/kretprobe_example.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase5_sample);

    const runtime_loader = try readRepoFileAlloc(
        "../kernel/runtime_loader.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader);

    try expectContains(gap_note, "`PHASE9_STATUS=active`");
    try expectContains(gap_note, "`PHASE9_SLICE=runtime-kretprobe-gap-survey`");
    try expectContains(gap_note, "`PHASE9_LANE_KEY=P9-L13`");
    try expectContains(gap_note, "`samples/kprobes/kretprobe_example.c`");
    try expectContains(gap_note, "`samples/zigux/kretprobe_example.zig`");
    try expectContains(gap_note, "`Documentation/zigux/phase5-kretprobe-sample-survey.md`");
    try expectContains(gap_note, "`zigux/tests/phase5_kretprobe_example.zig`");
    try expectContains(gap_note, "`zigux/tests/phase5_kretprobe_example_manifest.json`");
    try expectContains(gap_note, "`zigux/tests/phase5_kretprobe_example_survey.zig`");
    try expectContains(gap_note, "`register_kretprobe parity`");
    try expectContains(gap_note, "`unregister_kretprobe parity`");
    try expectContains(gap_note, "`module_name = \"runtime_kretprobe\"`");
    try expectContains(gap_note, "`entry_symbol = \"zigux_runtime_kretprobe_init\"`");
    try expectContains(gap_note, "`exit_symbol = \"zigux_runtime_kretprobe_exit\"`");
    try expectContains(gap_note, "`samples/zigux/runtime_kretprobe.zig`");
    try expectContains(gap_note, "`samples/zigux/runtime_kretprobe_loader.zig`");
    try expectContains(gap_note, "`Documentation/zigux/phase9-runtime-kretprobe-survey.md`");
    try expectContains(gap_note, "`Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`");
    try expectContains(gap_note, "`zigux/tests/runtime_kretprobe_manifest.json`");
    try expectContains(gap_note, "`zigux/tests/runtime_kretprobe_survey.zig`");
    try expectContains(gap_note, "`zigux/tests/runtime_kretprobe_module.zig`");
    try expectContains(gap_note, "`zigux/tests/runtime_kretprobe_diff.zig`");
    try expectContains(gap_note, "must not claim shipped Phase 9 kretprobe runtime-module parity");

    try expectContains(sequencing_note, "`samples/kprobes/kretprobe_example.c`");
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "runtime_kretprobe") == null);

    try expectContains(samples_readme, "`samples/zigux/kretprobe_example.zig`");
    try expectContains(samples_readme, "Current `master` also keeps the direct non-runtime kretprobe packet visible");
    try expectContains(samples_readme, "keep `register_kretprobe`, `unregister_kretprobe`, `pt_regs or regs_return_value`, and loadable module wiring out of scope");
    try std.testing.expect(std.mem.indexOf(u8, samples_readme, "`samples/zigux/runtime_kretprobe.zig`") == null);

    try expectContains(phase5_sample, "register_kretprobe parity");
    try expectContains(phase5_sample, "unregister_kretprobe parity");
    try expectContains(phase5_sample, "loadable module wiring");

    try expectContains(runtime_loader, ".module_name = \"runtime_kretprobe\"");
    try expectContains(runtime_loader, ".anchor = \"samples/kprobes/kretprobe_example.c\"");
    try expectContains(runtime_loader, ".entry_symbol = \"zigux_runtime_kretprobe_init\"");
    try expectContains(runtime_loader, ".exit_symbol = \"zigux_runtime_kretprobe_exit\"");

    try expectMissing("../../samples/zigux/runtime_kretprobe.zig");
    try expectMissing("../../samples/zigux/runtime_kretprobe_loader.zig");
    try expectMissing("../../Documentation/zigux/phase9-runtime-kretprobe-survey.md");
    try expectMissing("../../Documentation/zigux/phase9-runtime-kretprobe-module-slice.md");
    try expectMissing("runtime_kretprobe_manifest.json");
    try expectMissing("runtime_kretprobe_survey.zig");
    try expectMissing("runtime_kretprobe_module.zig");
    try expectMissing("runtime_kretprobe_diff.zig");
}
