const std = @import("std");

const read_limit = 64 * 1024;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(read_limit));
}

test "phase5 kretprobe focused test keeps the restored helper surface explicit" {
    const sample_source = try readFile(std.testing.allocator, "samples/zigux/kretprobe_example.zig");
    defer std.testing.allocator.free(sample_source);

    try std.testing.expect(std.mem.indexOf(u8, sample_source, "pub const SampleStage") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "requires_runtime_substrate = false") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "default_symbol_name = \"kernel_clone\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "runRetargetReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "runLifecycleGuardReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "runOwnershipReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "runRecoveryReplay") != null);
}

test "phase5 kretprobe focused test keeps the exact anchor and recovery cues explicit" {
    const sample_source = try readFile(std.testing.allocator, "samples/zigux/kretprobe_example.zig");
    defer std.testing.allocator.free(sample_source);

    try std.testing.expect(std.mem.indexOf(u8, sample_source, "samples/kprobes/kretprobe_example.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "private_data_size_bytes: usize = 8") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "maxactive_budget: usize = 20") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try self.retHandler(42, 175)") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "self.retHandler(9, 199)") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "const recovered_duration_ns = try self.retHandler(9, 260)") != null);
}

test "phase5 kretprobe focused test keeps manifest and survey note aligned with the restored packet" {
    const manifest = try readFile(std.testing.allocator, "zigux/tests/phase5_kretprobe_example_manifest.json");
    defer std.testing.allocator.free(manifest);
    const survey_note = try readFile(std.testing.allocator, "Documentation/zigux/phase5-kretprobe-sample-survey.md");
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, manifest, "\"lane_key\": \"P5-L18\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest, "\"sample_path\": \"samples/zigux/kretprobe_example.zig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest, "runRetargetReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest, "runRecoveryReplay") != null);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE5_LANE_KEY=P5-L18") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "samples/zigux/kretprobe_example.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase5_kretprobe_example.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runRetargetReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runRecoveryReplay") != null);
}
