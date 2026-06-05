const std = @import("std");
const testing = std.testing;

const shared_build = @embedFile("build.zig");
const policy_build = @embedFile("phase3_policy_starter_packet_build.zig");
const idr_build = @embedFile("phase3_idr_slot_starter_packet_build.zig");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "lane04 shared tests root keeps phase3 policy and idr starter routes explicit" {
    try expectContains(shared_build, "addPhase3IdrSlotStarterPacket(b, target, optimize)");
    try expectContains(shared_build, "addPhase3PolicyStarterPacket(b, target, optimize)");
    try expectContains(shared_build, "\"phase3-idr-slot\"");
    try expectContains(shared_build, "\"phase3-policy-starter-packet\"");
    try expectContains(shared_build, "\"phase3-test\"");

    try expectBefore(shared_build, "\"phase3-idr-slot\"", "phase3_idr_slot_step.dependOn(&phase3_idr_slot_starter_packet.step)");
    try expectBefore(shared_build, "\"phase3-policy-starter-packet\"", "phase3_policy_step.dependOn(&phase3_policy_starter_packet.step)");
}

test "lane04 aggregate phase3 smoke keeps policy and idr starter packets in scope" {
    try expectContains(shared_build, "phase3_test_step.dependOn(&phase3_idr_slot_starter_packet.step)");
    try expectContains(shared_build, "phase3_test_step.dependOn(&phase3_policy_starter_packet.step)");
    try expectContains(shared_build, "phase3_idr_slot_step.dependOn(&phase3_idr_slot_dump.step)");
}

test "lane04 standalone policy wrapper keeps policy dependencies wired" {
    try expectContains(policy_build, "\"phase3-policy-starter-packet-test\"");
    try expectContains(policy_build, ".root_source_file = b.path(\"phase3_policy_starter_packet.zig\")");
    try expectContains(policy_build, "root_module.addImport(\"abi_bindings\", abi_bindings)");
    try expectContains(policy_build, "root_module.addImport(\"panic_policy\", panic_policy)");
    try expectContains(policy_build, "root_module.addImport(\"allocator_policy\", allocator_policy)");
    try expectContains(policy_build, "root_module.addImport(\"unsafe_policy\", unsafe_policy)");
    try expectContains(policy_build, "root_module.addImport(\"layout_assert\", layout_assert)");
    try expectContains(policy_build, "root_module.addImport(\"narrow_surface\", narrow_surface)");
}

test "lane04 standalone idr wrapper keeps slot dependencies wired" {
    try expectContains(idr_build, "\"phase3-idr-slot-starter-packet-test\"");
    try expectContains(idr_build, ".root_source_file = b.path(\"phase3_idr_slot_starter_packet.zig\")");
    try expectContains(idr_build, "xa_value.addImport(\"err_ptr\", err_ptr)");
    try expectContains(idr_build, "xarray_slot_view.addImport(\"err_ptr\", err_ptr)");
    try expectContains(idr_build, "xarray_slot_view.addImport(\"xa_value\", xa_value)");
    try expectContains(idr_build, "idr_slot_view.addImport(\"xarray_slot_view\", xarray_slot_view)");
    try expectContains(idr_build, "idr_slot_view.addImport(\"xa_value\", xa_value)");
    try expectContains(idr_build, "root_module.addImport(\"idr_slot_view\", idr_slot_view)");
}
