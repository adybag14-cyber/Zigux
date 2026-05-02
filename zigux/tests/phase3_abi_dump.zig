const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");

fn writeStructLayout(writer: anytype, comptime name: []const u8, comptime T: type, comma: bool) !void {
    try writer.writeAll("\"");
    try writer.writeAll(name);
    try writer.writeAll("\":{\"size\":");
    try writer.print("{d}", .{@sizeOf(T)});
    try writer.writeAll(",\"align\":");
    try writer.print("{d}", .{@alignOf(T)});
    try writer.writeAll(",\"offsets\":{");
    const fields = std.meta.fields(T);
    inline for (fields, 0..) |field, index| {
        try writer.writeAll("\"");
        try writer.writeAll(field.name);
        try writer.writeAll("\":");
        try writer.print("{d}", .{@offsetOf(T, field.name)});
        if (index + 1 < fields.len) try writer.writeAll(",");
    }
    try writer.writeAll("}}");
    if (comma) try writer.writeAll(",");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [1024]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    try writer.writeAll("{\"abi_version\":");
    try writer.print("{d}", .{abi.ABI_VERSION});
    try writer.writeAll(",\"constants\":{\"facility_kernel\":");
    try writer.print("{d}", .{@intFromEnum(abi.Facility.kernel)});
    try writer.writeAll(",\"facility_helpers\":");
    try writer.print("{d}", .{@intFromEnum(abi.Facility.helpers)});
    try writer.writeAll(",\"facility_drivers\":");
    try writer.print("{d}", .{@intFromEnum(abi.Facility.drivers)});
    try writer.writeAll(",\"status_flag_error\":");
    try writer.print("{d}", .{abi.STATUS_FLAG_ERROR});
    try writer.writeAll(",\"panic_abort\":");
    try writer.print("{d}", .{@intFromEnum(abi.PanicMode.abort)});
    try writer.writeAll(",\"panic_bug\":");
    try writer.print("{d}", .{@intFromEnum(abi.PanicMode.bug)});
    try writer.writeAll(",\"panic_warn\":");
    try writer.print("{d}", .{@intFromEnum(abi.PanicMode.warn)});
    try writer.writeAll(",\"allocator_caller_provided\":");
    try writer.print("{d}", .{@intFromEnum(abi.AllocatorMode.caller_provided)});
    try writer.writeAll(",\"allocator_kernel_heap\":");
    try writer.print("{d}", .{@intFromEnum(abi.AllocatorMode.kernel_heap)});
    try writer.writeAll(",\"allocator_arena\":");
    try writer.print("{d}", .{@intFromEnum(abi.AllocatorMode.arena)});
    try writer.writeAll(",\"unsafe_scope_none\":");
    try writer.print("{d}", .{@intFromEnum(abi.UnsafeScope.none)});
    try writer.writeAll(",\"unsafe_scope_volatile_mmio\":");
    try writer.print("{d}", .{@intFromEnum(abi.UnsafeScope.volatile_mmio)});
    try writer.writeAll(",\"unsafe_scope_raw_pointer_bridge\":");
    try writer.print("{d}", .{@intFromEnum(abi.UnsafeScope.raw_pointer_bridge)});
    try writer.writeAll(",\"minor_alloc_flag_truncated\":");
    try writer.print("{d}", .{abi.MINOR_ALLOC_FLAG_TRUNCATED});
    try writer.writeAll(",\"minor_alloc_flag_found\":");
    try writer.print("{d}", .{abi.MINOR_ALLOC_FLAG_FOUND});
    try writer.writeAll(",\"minor_alloc_flag_exhausted\":");
    try writer.print("{d}", .{abi.MINOR_ALLOC_FLAG_EXHAUSTED});
    try writer.writeAll("},\"structs\":{");
    try writeStructLayout(writer, "zigux_boundary_header", abi.BoundaryHeader, true);
    try writeStructLayout(writer, "zigux_export_status", abi.ExportStatus, true);
    try writeStructLayout(writer, "zigux_mmio_range", abi.MmioRange, true);
    try writeStructLayout(writer, "zigux_interop_policy", abi.InteropPolicy, true);
    try writeStructLayout(writer, "zigux_bitmap_view", abi.BitmapView, true);
    try writeStructLayout(writer, "zigux_cpumask_view", abi.CpuMaskView, false);
    try writer.writeAll("}}\n");
    try writer.flush();
}
