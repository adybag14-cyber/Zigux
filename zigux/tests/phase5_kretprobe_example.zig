const std = @import("std");

const read_limit = 64 * 1024;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(read_limit));
}

fn findRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingExpectedMarker;
}

test "phase5 kretprobe focused test keeps the review contract and helper surface explicit" {
    const sample_source = try readFile(std.testing.allocator, "samples/zigux/kretprobe_example.zig");
    defer std.testing.allocator.free(sample_source);

    try std.testing.expect(std.mem.indexOf(u8, sample_source, "pub const SampleStage") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "pub const SampleFocus = enum") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "pub const sample_review_focus = [_]SampleFocus{") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "pub const ReviewContract = struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "pub fn reviewContract() ReviewContract {") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".focus = &sample_review_focus,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".default_symbol_name = default_symbol_name,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".maxactive_budget = maxactive_budget,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "requires_runtime_substrate = false") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "runLifecycleGuardReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "runOwnershipReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "runRecoveryReplay") != null);

    const descriptor_anchor_idx = try findRequired(sample_source, ".descriptor_anchor,");
    const symbol_retargeting_idx = try findRequired(sample_source, ".symbol_retargeting,");
    const entry_return_flow_idx = try findRequired(sample_source, ".entry_and_return_flow,");
    const lifecycle_guards_idx = try findRequired(sample_source, ".lifecycle_guards,");
    const ownership_lifetime_idx = try findRequired(sample_source, ".ownership_and_lifetime,");
    const recovery_exit_idx = try findRequired(sample_source, ".recovery_and_exit_rejections,");

    try std.testing.expect(descriptor_anchor_idx < symbol_retargeting_idx);
    try std.testing.expect(symbol_retargeting_idx < entry_return_flow_idx);
    try std.testing.expect(entry_return_flow_idx < lifecycle_guards_idx);
    try std.testing.expect(lifecycle_guards_idx < ownership_lifetime_idx);
    try std.testing.expect(ownership_lifetime_idx < recovery_exit_idx);
}

test "phase5 kretprobe focused test keeps the exact anchor, retarget, and recovery cues explicit" {
    const sample_source = try readFile(std.testing.allocator, "samples/zigux/kretprobe_example.zig");
    defer std.testing.allocator.free(sample_source);

    try std.testing.expect(std.mem.indexOf(u8, sample_source, "samples/kprobes/kretprobe_example.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "default_symbol_name = \"kernel_clone\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "maxactive_budget: usize = 20") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "runRetargetReplay(\"do_sys_openat2\")") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "error.InvalidSymbolName => rejected_empty_symbol = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "error.InvalidLifecycleTransition => rejected_post_init_retarget = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try self.retHandler(42, 175)") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "self.retHandler(9, 199)") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "const recovered_duration_ns = try self.retHandler(9, 260)") != null);
}

test "phase5 kretprobe focused test keeps manifest and survey note aligned with the restored packet" {
    const manifest = try readFile(std.testing.allocator, "zigux/tests/phase5_kretprobe_example_manifest.json");
    defer std.testing.allocator.free(manifest);
    const survey_note = try readFile(std.testing.allocator, "Documentation/zigux/phase5-kretprobe-sample-survey.md");
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, manifest, "\"lane_key\": \"P5-L13\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest, "\"sample_path\": \"samples/zigux/kretprobe_example.zig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest, "reviewContract()") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest, "default symbol kernel_clone") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest, "maxactive budget 20") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest, "do_sys_openat2") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest, "runRetargetReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest, "runRecoveryReplay") != null);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE5_LANE_KEY=P5-L13") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "samples/zigux/kretprobe_example.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/tests/phase5_kretprobe_example.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase5_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`kernel_clone`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runRetargetReplay(\"do_sys_openat2\")") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`maxactive = 20`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runRetargetReplay") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runRecoveryReplay") != null);
}
