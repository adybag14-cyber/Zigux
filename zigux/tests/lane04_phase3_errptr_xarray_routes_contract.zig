const std = @import("std");
const testing = std.testing;

const shared_build_root =
    \\fn addPhase3ErrPtrXarrayStarterPacket(
    \\    const err_ptr = b.createModule(.{
    \\        .root_source_file = b.path("../helpers/err_ptr.zig"),
    \\    const xa_value = b.createModule(.{
    \\        .root_source_file = b.path("../helpers/xa_value.zig"),
    \\    xa_value.addImport("err_ptr", err_ptr);
    \\        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
    \\    root_module.addImport("err_ptr", err_ptr);
    \\    root_module.addImport("xa_value", xa_value);
    \\        .name = "phase3-errptr-xarray-starter-packet",
    \\
;

const shared_step_root =
    \\    const phase3_errptr_xarray_step = b.step(
    \\        "phase3-errptr-xarray-starter-packet",
    \\        "Run the shared Phase 3 err_ptr/xarray starter packet from zigux/tests",
    \\    phase3_errptr_xarray_step.dependOn(&phase3_errptr_xarray_starter_packet.step);
    \\
;

const shared_slice_root =
    \\    const phase3_errptr_xarray_slice_step = b.step(
    \\        "phase3-errptr-xarray",
    \\        "Run the shared Phase 3 err_ptr/xarray starter packet, xarray-slot starter packet, and dump from zigux/tests",
    \\    phase3_errptr_xarray_slice_step.dependOn(&phase3_errptr_xarray_starter_packet.step);
    \\    phase3_errptr_xarray_slice_step.dependOn(&phase3_xarray_slot_starter_packet.step);
    \\    phase3_errptr_xarray_slice_step.dependOn(&phase3_errptr_xarray_dump.step);
    \\
;

const shared_phase3_test_root =
    \\    const phase3_test_step = b.step(
    \\        "phase3-test",
    \\        "Run the current shared Phase 3 starter packet bundle from zigux/tests",
    \\    phase3_test_step.dependOn(&phase3_errptr_xarray_starter_packet.step);
    \\
;

const standalone_build_root =
    \\const std = @import("std");
    \\        .root_source_file = b.path("../helpers/err_ptr.zig"),
    \\        .root_source_file = b.path("../helpers/xa_value.zig"),
    \\    xa_value.addImport("err_ptr", err_ptr);
    \\        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
    \\    root_module.addImport("err_ptr", err_ptr);
    \\    root_module.addImport("xa_value", xa_value);
    \\        "phase3-errptr-xarray-starter-packet-test",
    \\        "Run the Phase 3 err_ptr/xarray starter-packet self-check",
    \\
;

const packet_root =
    \\const err_ptr = @import("err_ptr");
    \\const xa_value = @import("xa_value");
    \\test "err_ptr encodes the Linux error band as a tagged pointer-sized value" {
    \\test "xa_value round-trips a bounded inline value without entering the err_ptr band" {
    \\test "xa_value rejects inline values that would overlap err_ptr encodings" {
    \\test "safe inline limit stays the highest tagged value below the err_ptr floor" {
    \\
;

fn expectMarkers(haystack: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
    }
}

test "shared tests root keeps the direct errptr/xarray starter packet route wired" {
    try expectMarkers(shared_build_root, &.{
        "fn addPhase3ErrPtrXarrayStarterPacket(",
        ".root_source_file = b.path(\"../helpers/err_ptr.zig\")",
        ".root_source_file = b.path(\"../helpers/xa_value.zig\")",
        "xa_value.addImport(\"err_ptr\", err_ptr)",
        ".root_source_file = b.path(\"phase3_errptr_xarray_starter_packet.zig\")",
        "root_module.addImport(\"err_ptr\", err_ptr)",
        "root_module.addImport(\"xa_value\", xa_value)",
        ".name = \"phase3-errptr-xarray-starter-packet\"",
    });

    try expectMarkers(shared_step_root, &.{
        "const phase3_errptr_xarray_step = b.step(",
        "\"phase3-errptr-xarray-starter-packet\"",
        "phase3_errptr_xarray_step.dependOn(&phase3_errptr_xarray_starter_packet.step)",
    });
}

test "shared tests root keeps the errptr/xarray slice and phase3 aggregate anchored" {
    try expectMarkers(shared_slice_root, &.{
        "const phase3_errptr_xarray_slice_step = b.step(",
        "\"phase3-errptr-xarray\"",
        "phase3_errptr_xarray_slice_step.dependOn(&phase3_errptr_xarray_starter_packet.step)",
        "phase3_errptr_xarray_slice_step.dependOn(&phase3_xarray_slot_starter_packet.step)",
        "phase3_errptr_xarray_slice_step.dependOn(&phase3_errptr_xarray_dump.step)",
    });

    try expectMarkers(shared_phase3_test_root, &.{
        "const phase3_test_step = b.step(",
        "\"phase3-test\"",
        "phase3_test_step.dependOn(&phase3_errptr_xarray_starter_packet.step)",
    });
}

test "standalone wrapper still mirrors the live errptr/xarray packet dependencies" {
    try expectMarkers(standalone_build_root, &.{
        ".root_source_file = b.path(\"../helpers/err_ptr.zig\")",
        ".root_source_file = b.path(\"../helpers/xa_value.zig\")",
        "xa_value.addImport(\"err_ptr\", err_ptr)",
        ".root_source_file = b.path(\"phase3_errptr_xarray_starter_packet.zig\")",
        "root_module.addImport(\"err_ptr\", err_ptr)",
        "root_module.addImport(\"xa_value\", xa_value)",
        "\"phase3-errptr-xarray-starter-packet-test\"",
        "\"Run the Phase 3 err_ptr/xarray starter-packet self-check\"",
    });
}

test "starter packet keeps the four Linux-tagging boundary checks visible" {
    try expectMarkers(packet_root, &.{
        "const err_ptr = @import(\"err_ptr\")",
        "const xa_value = @import(\"xa_value\")",
        "err_ptr encodes the Linux error band as a tagged pointer-sized value",
        "xa_value round-trips a bounded inline value without entering the err_ptr band",
        "xa_value rejects inline values that would overlap err_ptr encodings",
        "safe inline limit stays the highest tagged value below the err_ptr floor",
    });
}
