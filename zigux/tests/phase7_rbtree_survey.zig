const std = @import("std");

test "phase 7 rbtree survey keeps the returned json fixture, C harness, and direct helper packet truthful" {
    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "zigux/tests/phase7_rbtree_manifest.json", std.testing.allocator, .limited(16384));
    defer std.testing.allocator.free(manifest_json);
    const fixture = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "zigux/tests/fixtures/phase7_rbtree.json", std.testing.allocator, .limited(16384));
    defer std.testing.allocator.free(fixture);
    const c_harness = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "zigux/tests/fixtures/phase7_rbtree_c_harness.c", std.testing.allocator, .limited(16384));
    defer std.testing.allocator.free(c_harness);
    const helper_companion = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "zigux/tests/phase7_rbtree.zig", std.testing.allocator, .limited(16384));
    defer std.testing.allocator.free(helper_companion);

    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "cached-churn invariants witness aligned with the dedicated replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "cached-churn invariants boundaries explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, fixture, "\"cached_churn_invariants\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, fixture, "\"leftmost_checkpoints\": [1, 5, 5, 5, 7, 0]") != null);
    try std.testing.expect(std.mem.indexOf(u8, fixture, "\"invariants_hold_after_each_step\": true") != null);
    try std.testing.expect(std.mem.indexOf(u8, c_harness, "struct phase7_rbtree_cached_churn_invariants_case") != null);
    try std.testing.expect(std.mem.indexOf(u8, c_harness, ".cached_churn_invariants = {") != null);
    try std.testing.expect(std.mem.indexOf(u8, c_harness, ".root_stays_black = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, helper_companion, "phase 7 rbtree companion preserves red-black invariants across cached churn") != null);
}
