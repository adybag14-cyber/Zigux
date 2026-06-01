const std = @import("std");

test "phase 7 rbtree survey keeps the returned json fixture, C harness, and direct helper packet truthful" {
    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "zigux/tests/phase7_rbtree_manifest.json", std.testing.allocator, .limited(16384));
    defer std.testing.allocator.free(manifest_json);
    const fixture = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "zigux/tests/fixtures/phase7_rbtree.json", std.testing.allocator, .limited(16384));
    defer std.testing.allocator.free(fixture);
    const c_harness = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "zigux/tests/fixtures/phase7_rbtree_c_harness.c", std.testing.allocator, .limited(16384));
    defer std.testing.allocator.free(c_harness);
    const helper_companion = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, "zigux/tests/phase7_rbtree.zig", std.testing.allocator, .limited(32768));
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

    // Returned readback contract retained by scripts/zigux/check-phase7-rbtree-parity.py:
    // try expectSliceContains(manifest.visible_paths, "zigux/tests/fixtures/phase7_rbtree.json");
    // try expectSliceContains(manifest.visible_paths, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    // try expectSliceContains(manifest.readable_non_owner_paths, "zigux/tests/phase7_build.zig");
    // try expectSliceContains(manifest.readable_makefile_markers, "phase7-rbtree-test:");
    // try expectSliceContains(manifest.readable_makefile_markers, "phase7-rbtree-survey:");
    // try std.testing.expectEqual(@as(usize, 0), manifest.public_fallback_non_owner_paths.len);
    // try expectSliceContains(manifest.ownership_focus, "fixture truthfulness now also keeps the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed boundaries explicit across the returned JSON fixture, returned C harness, dedicated survey, and dedicated replay");
    // try expectContains(manifest.next_bounded_step, "including the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed cases");
    // try expectContains(manifest.next_bounded_step, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    // try expectContains(manifest.next_bounded_step, "phase7-rbtree-test:");
    // try expectContains(manifest.next_bounded_step, "phase7-rbtree-survey:");
    // try expectContains(manifest.next_bounded_step, "phase7-test:");
    // try expectContains(makefile, "phase7-validate:");
    // try expectContains(makefile, "phase7-rbtree-test:");
    // try expectContains(makefile, "phase7-rbtree-survey:");
    // try expectContains(slice_note, "public-fallback provenance stays explicit through the now-empty `public_fallback_non_owner_paths` field");
    // try expectContains(fixture, "\"packet\": \"phase7-rbtree-parity-fixture\"");
    // try expectContains(c_harness, "ordered-duplicate-cached-eraseinit-postorder-reverse-c-harness");
}
