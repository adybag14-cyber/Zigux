const std = @import("std");
const Io = std.Io;
const abi = @import("abi_bindings");

fn writeLayoutPrefix(writer: anytype, comptime name: []const u8, size: usize, alignment: usize) !void {
    try writer.writeAll("\"");
    try writer.writeAll(name);
    try writer.writeAll("\":{\"size\":");
    try writer.print("{d}", .{size});
    try writer.writeAll(",\"align\":");
    try writer.print("{d}", .{alignment});
    try writer.writeAll(",\"offsets\":{");
}

fn writeOffset(writer: anytype, comptime name: []const u8, value: usize, comma: bool) !void {
    try writer.writeAll("\"");
    try writer.writeAll(name);
    try writer.writeAll("\":");
    try writer.print("{d}", .{value});
    if (comma) try writer.writeAll(",");
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const writer = &stdout_writer.interface;

    try writer.writeAll("{\"abi_version\":");
    try writer.print("{d}", .{abi.ABI_VERSION});
    try writer.writeAll(",\"constants\":{\"facility_kernel\":");
    try writer.print("{d}", .{@intFromEnum(abi.Facility.kernel)});
    try writer.writeAll(",\"status_flag_error\":");
    try writer.print("{d}", .{abi.STATUS_FLAG_ERROR});
    try writer.writeAll(",\"panic_abort\":");
    try writer.print("{d}", .{@intFromEnum(abi.PanicMode.abort)});
    try writer.writeAll(",\"allocator_caller_provided\":");
    try writer.print("{d}", .{@intFromEnum(abi.AllocatorMode.caller_provided)});
    try writer.writeAll(",\"unsafe_scope_raw_pointer_bridge\":");
    try writer.print("{d}", .{@intFromEnum(abi.UnsafeScope.raw_pointer_bridge)});
    try writer.writeAll("},\"structs\":{");

    try writeLayoutPrefix(writer, "zigux_boundary_header", @sizeOf(abi.BoundaryHeader), @alignOf(abi.BoundaryHeader));
    try writeOffset(writer, "size", @offsetOf(abi.BoundaryHeader, "size"), true);
    try writeOffset(writer, "abi_version", @offsetOf(abi.BoundaryHeader, "abi_version"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.BoundaryHeader, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_export_status", @sizeOf(abi.ExportStatus), @alignOf(abi.ExportStatus));
    try writeOffset(writer, "code", @offsetOf(abi.ExportStatus, "code"), true);
    try writeOffset(writer, "facility", @offsetOf(abi.ExportStatus, "facility"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.ExportStatus, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_bitmap_view", @sizeOf(abi.BitmapView), @alignOf(abi.BitmapView));
    try writeOffset(writer, "words_addr", @offsetOf(abi.BitmapView, "words_addr"), true);
    try writeOffset(writer, "nbits", @offsetOf(abi.BitmapView, "nbits"), true);
    try writeOffset(writer, "word_count", @offsetOf(abi.BitmapView, "word_count"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_cpumask_view", @sizeOf(abi.CpuMaskView), @alignOf(abi.CpuMaskView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.CpuMaskView, "bits_addr"), true);
    try writeOffset(writer, "nr_cpu_ids", @offsetOf(abi.CpuMaskView, "nr_cpu_ids"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.CpuMaskView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_bitmap_summary", @sizeOf(abi.BitmapSummary), @alignOf(abi.BitmapSummary));
    try writeOffset(writer, "first_set", @offsetOf(abi.BitmapSummary, "first_set"), true);
    try writeOffset(writer, "first_zero", @offsetOf(abi.BitmapSummary, "first_zero"), true);
    try writeOffset(writer, "weight", @offsetOf(abi.BitmapSummary, "weight"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.BitmapSummary, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_cpumask_summary", @sizeOf(abi.CpuMaskSummary), @alignOf(abi.CpuMaskSummary));
    try writeOffset(writer, "first_cpu", @offsetOf(abi.CpuMaskSummary, "first_cpu"), true);
    try writeOffset(writer, "next_cpu", @offsetOf(abi.CpuMaskSummary, "next_cpu"), true);
    try writeOffset(writer, "weight", @offsetOf(abi.CpuMaskSummary, "weight"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.CpuMaskSummary, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_mmio_range", @sizeOf(abi.MmioRange), @alignOf(abi.MmioRange));
    try writeOffset(writer, "base_addr", @offsetOf(abi.MmioRange, "base_addr"), true);
    try writeOffset(writer, "length", @offsetOf(abi.MmioRange, "length"), true);
    try writeOffset(writer, "stride", @offsetOf(abi.MmioRange, "stride"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_interop_policy", @sizeOf(abi.InteropPolicy), @alignOf(abi.InteropPolicy));
    try writeOffset(writer, "panic_mode", @offsetOf(abi.InteropPolicy, "panic_mode"), true);
    try writeOffset(writer, "allocator_mode", @offsetOf(abi.InteropPolicy, "allocator_mode"), true);
    try writeOffset(writer, "unsafe_scope", @offsetOf(abi.InteropPolicy, "unsafe_scope"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.InteropPolicy, "reserved"), false);
    try writer.writeAll("}}}}\n");

    try stdout_writer.interface.flush();
}
