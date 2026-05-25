const std = @import("std");
const build_options = @import("build_options");

const note_path = "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md";
const helper_path = "tools/lib/bpf/zigux_segments/cpu_mask.zig";
const verify_path = "tools/lib/bpf/zigux_segments/cpu_mask_verify.zig";
const focused_build_path = "zigux/tests/phase8_cpu_mask_only_build.zig";
const local_build_path = "zigux/tests/phase8_cpu_mask_local_build.zig";

fn loadRepoText(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    const full_path = try std.fs.path.join(allocator, &.{ build_options.repo_root, relative_path });
    defer allocator.free(full_path);
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, full_path, allocator, .limited(1024 * 1024));
}

fn expectContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

test "phase 8 cpu mask slice note keeps helper-local packet explicit" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const note = try loadRepoText(allocator, note_path);
    try expectContains(note, "helper-local cpu-mask parsing, summary, and auto-count truthfulness only");
    try expectContains(note, "`tools/lib/bpf/zigux_segments/cpu_mask.zig`");
    try expectContains(note, "`tools/lib/bpf/zigux_segments/cpu_mask_verify.zig`");
    try expectContains(note, "parseCpuMaskString()");
    try expectContains(note, "parseCpuMaskFromReader()");
    try expectContains(note, "summarizePossibleCpusFromReader()");
    try expectContains(note, "derivePerfBufferAutoCpuCountFromReader()");
    try expectContains(note, "isOnlineCpuEligible()");
    try expectContains(note, "perf-buffer-online-cpu-routing");
}

test "phase 8 cpu mask helper and verifier shards keep bounded witnesses explicit" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const helper = try loadRepoText(allocator, helper_path);
    try expectContains(helper, "pub fn parseCpuMaskString(");
    try expectContains(helper, "pub fn parseCpuMaskFromReader(");
    try expectContains(helper, "pub fn summarizePossibleCpusFromReader(");
    try expectContains(helper, "pub fn derivePerfBufferAutoCpuCountFromReader(");
    try expectContains(helper, "pub fn isOnlineCpuEligible(");

    const verify = try loadRepoText(allocator, verify_path);
    try expectContains(verify, "phase8 cpu-mask helper entrypoints stay explicit");
    try expectContains(verify, "phase8 cpu-mask helpers keep delimiter-heavy reader inputs and injected read errors explicit");
    try expectContains(verify, "phase8 cpu-mask helpers keep invalid direct and reader-backed inputs fail-closed");
    try expectContains(verify, "derivePerfBufferAutoCpuCountFromReader");
    try expectContains(verify, "parseCpuMaskFromReader");
}

test "phase 8 cpu mask build shards keep the focused replay wired" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const focused_build = try loadRepoText(allocator, focused_build_path);
    try expectContains(focused_build, "phase8_cpu_mask.zig");
    try expectContains(focused_build, "phase8_cpu_mask_packet_sync.zig");
    try expectContains(focused_build, "../../tools/lib/bpf/zigux_segments/cpu_mask.zig");
    try expectContains(focused_build, "../../tools/lib/bpf/zigux_segments/cpu_mask_verify.zig");
    try expectContains(focused_build, "phase8-cpu-mask-verify-tests");
    try expectContains(focused_build, "Run focused Phase 8 cpu-mask tests");

    const local_build = try loadRepoText(allocator, local_build_path);
    try expectContains(local_build, "phase8_cpu_mask.zig");
    try expectContains(local_build, "phase8_cpu_mask_packet_sync.zig");
    try expectContains(local_build, "../../tools/lib/bpf/zigux_segments/cpu_mask.zig");
    try expectContains(local_build, "../../tools/lib/bpf/zigux_segments/cpu_mask_verify.zig");
    try expectContains(local_build, "phase8-cpu-mask-verify-tests");
    try expectContains(local_build, "Run focused Phase 8 cpu-mask build");
}
