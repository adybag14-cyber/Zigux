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

    try writeLayoutPrefix(writer, "zigux_list_head_ref", @sizeOf(abi.ListHeadRef), @alignOf(abi.ListHeadRef));
    try writeOffset(writer, "next_addr", @offsetOf(abi.ListHeadRef, "next_addr"), true);
    try writeOffset(writer, "prev_addr", @offsetOf(abi.ListHeadRef, "prev_addr"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_list_view", @sizeOf(abi.ListView), @alignOf(abi.ListView));
    try writeOffset(writer, "head_addr", @offsetOf(abi.ListView, "head_addr"), true);
    try writeOffset(writer, "max_nodes", @offsetOf(abi.ListView, "max_nodes"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.ListView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_list_summary", @sizeOf(abi.ListSummary), @alignOf(abi.ListSummary));
    try writeOffset(writer, "length", @offsetOf(abi.ListSummary, "length"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.ListSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_hlist_head_ref", @sizeOf(abi.HListHeadRef), @alignOf(abi.HListHeadRef));
    try writeOffset(writer, "first_addr", @offsetOf(abi.HListHeadRef, "first_addr"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_hlist_node_ref", @sizeOf(abi.HListNodeRef), @alignOf(abi.HListNodeRef));
    try writeOffset(writer, "next_addr", @offsetOf(abi.HListNodeRef, "next_addr"), true);
    try writeOffset(writer, "pprev_addr", @offsetOf(abi.HListNodeRef, "pprev_addr"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_hlist_view", @sizeOf(abi.HListView), @alignOf(abi.HListView));
    try writeOffset(writer, "head_addr", @offsetOf(abi.HListView, "head_addr"), true);
    try writeOffset(writer, "max_nodes", @offsetOf(abi.HListView, "max_nodes"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.HListView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_hlist_summary", @sizeOf(abi.HListSummary), @alignOf(abi.HListSummary));
    try writeOffset(writer, "length", @offsetOf(abi.HListSummary, "length"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.HListSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_err_ptr_summary", @sizeOf(abi.ErrPtrSummary), @alignOf(abi.ErrPtrSummary));
    try writeOffset(writer, "errno_code", @offsetOf(abi.ErrPtrSummary, "errno_code"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.ErrPtrSummary, "flags"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.ErrPtrSummary, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_xa_value_summary", @sizeOf(abi.XaValueSummary), @alignOf(abi.XaValueSummary));
    try writeOffset(writer, "raw_addr", @offsetOf(abi.XaValueSummary, "raw_addr"), true);
    try writeOffset(writer, "decoded_value", @offsetOf(abi.XaValueSummary, "decoded_value"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.XaValueSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_xa_slot_view", @sizeOf(abi.XaSlotView), @alignOf(abi.XaSlotView));
    try writeOffset(writer, "slots_addr", @offsetOf(abi.XaSlotView, "slots_addr"), true);
    try writeOffset(writer, "slot_count", @offsetOf(abi.XaSlotView, "slot_count"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.XaSlotView, "max_scan"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_xa_slot_summary", @sizeOf(abi.XaSlotSummary), @alignOf(abi.XaSlotSummary));
    try writeOffset(writer, "scanned_count", @offsetOf(abi.XaSlotSummary, "scanned_count"), true);
    try writeOffset(writer, "null_count", @offsetOf(abi.XaSlotSummary, "null_count"), true);
    try writeOffset(writer, "value_count", @offsetOf(abi.XaSlotSummary, "value_count"), true);
    try writeOffset(writer, "error_count", @offsetOf(abi.XaSlotSummary, "error_count"), true);
    try writeOffset(writer, "plain_count", @offsetOf(abi.XaSlotSummary, "plain_count"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.XaSlotSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_idr_slot_view", @sizeOf(abi.IdrSlotView), @alignOf(abi.IdrSlotView));
    try writeOffset(writer, "slots_addr", @offsetOf(abi.IdrSlotView, "slots_addr"), true);
    try writeOffset(writer, "base_id", @offsetOf(abi.IdrSlotView, "base_id"), true);
    try writeOffset(writer, "slot_count", @offsetOf(abi.IdrSlotView, "slot_count"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.IdrSlotView, "max_scan"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.IdrSlotView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_idr_slot_summary", @sizeOf(abi.IdrSlotSummary), @alignOf(abi.IdrSlotSummary));
    try writeOffset(writer, "scanned_count", @offsetOf(abi.IdrSlotSummary, "scanned_count"), true);
    try writeOffset(writer, "present_count", @offsetOf(abi.IdrSlotSummary, "present_count"), true);
    try writeOffset(writer, "value_count", @offsetOf(abi.IdrSlotSummary, "value_count"), true);
    try writeOffset(writer, "error_count", @offsetOf(abi.IdrSlotSummary, "error_count"), true);
    try writeOffset(writer, "plain_count", @offsetOf(abi.IdrSlotSummary, "plain_count"), true);
    try writeOffset(writer, "first_present_id", @offsetOf(abi.IdrSlotSummary, "first_present_id"), true);
    try writeOffset(writer, "next_free_id", @offsetOf(abi.IdrSlotSummary, "next_free_id"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.IdrSlotSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_ida_bitmap_view", @sizeOf(abi.IdaBitmapView), @alignOf(abi.IdaBitmapView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.IdaBitmapView, "bits_addr"), true);
    try writeOffset(writer, "base_id", @offsetOf(abi.IdaBitmapView, "base_id"), true);
    try writeOffset(writer, "nbits", @offsetOf(abi.IdaBitmapView, "nbits"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.IdaBitmapView, "max_scan"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.IdaBitmapView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_ida_bitmap_summary", @sizeOf(abi.IdaBitmapSummary), @alignOf(abi.IdaBitmapSummary));
    try writeOffset(writer, "scanned_count", @offsetOf(abi.IdaBitmapSummary, "scanned_count"), true);
    try writeOffset(writer, "allocated_count", @offsetOf(abi.IdaBitmapSummary, "allocated_count"), true);
    try writeOffset(writer, "first_allocated_id", @offsetOf(abi.IdaBitmapSummary, "first_allocated_id"), true);
    try writeOffset(writer, "first_free_id", @offsetOf(abi.IdaBitmapSummary, "first_free_id"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.IdaBitmapSummary, "flags"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.IdaBitmapSummary, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_ida_alloc_view", @sizeOf(abi.IdaAllocView), @alignOf(abi.IdaAllocView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.IdaAllocView, "bits_addr"), true);
    try writeOffset(writer, "base_id", @offsetOf(abi.IdaAllocView, "base_id"), true);
    try writeOffset(writer, "nbits", @offsetOf(abi.IdaAllocView, "nbits"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.IdaAllocView, "max_scan"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.IdaAllocView, "request_count"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.IdaAllocView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_ida_alloc_summary", @sizeOf(abi.IdaAllocSummary), @alignOf(abi.IdaAllocSummary));
    try writeOffset(writer, "scanned_count", @offsetOf(abi.IdaAllocSummary, "scanned_count"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.IdaAllocSummary, "request_count"), true);
    try writeOffset(writer, "first_fit_id", @offsetOf(abi.IdaAllocSummary, "first_fit_id"), true);
    try writeOffset(writer, "longest_free_run", @offsetOf(abi.IdaAllocSummary, "longest_free_run"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.IdaAllocSummary, "flags"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.IdaAllocSummary, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_ida_range_view", @sizeOf(abi.IdaRangeView), @alignOf(abi.IdaRangeView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.IdaRangeView, "bits_addr"), true);
    try writeOffset(writer, "base_id", @offsetOf(abi.IdaRangeView, "base_id"), true);
    try writeOffset(writer, "nbits", @offsetOf(abi.IdaRangeView, "nbits"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.IdaRangeView, "max_scan"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.IdaRangeView, "request_count"), true);
    try writeOffset(writer, "max_ranges", @offsetOf(abi.IdaRangeView, "max_ranges"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.IdaRangeView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_ida_range_summary", @sizeOf(abi.IdaRangeSummary), @alignOf(abi.IdaRangeSummary));
    try writeOffset(writer, "scanned_count", @offsetOf(abi.IdaRangeSummary, "scanned_count"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.IdaRangeSummary, "request_count"), true);
    try writeOffset(writer, "candidate_range_count", @offsetOf(abi.IdaRangeSummary, "candidate_range_count"), true);
    try writeOffset(writer, "first_range_id", @offsetOf(abi.IdaRangeSummary, "first_range_id"), true);
    try writeOffset(writer, "last_range_id", @offsetOf(abi.IdaRangeSummary, "last_range_id"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.IdaRangeSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_ida_range_set_view", @sizeOf(abi.IdaRangeSetView), @alignOf(abi.IdaRangeSetView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.IdaRangeSetView, "bits_addr"), true);
    try writeOffset(writer, "base_id", @offsetOf(abi.IdaRangeSetView, "base_id"), true);
    try writeOffset(writer, "nbits", @offsetOf(abi.IdaRangeSetView, "nbits"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.IdaRangeSetView, "max_scan"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.IdaRangeSetView, "request_count"), true);
    try writeOffset(writer, "max_ranges", @offsetOf(abi.IdaRangeSetView, "max_ranges"), true);
    try writeOffset(writer, "max_selected", @offsetOf(abi.IdaRangeSetView, "max_selected"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.IdaRangeSetView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_ida_range_set_summary", @sizeOf(abi.IdaRangeSetSummary), @alignOf(abi.IdaRangeSetSummary));
    try writeOffset(writer, "scanned_count", @offsetOf(abi.IdaRangeSetSummary, "scanned_count"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.IdaRangeSetSummary, "request_count"), true);
    try writeOffset(writer, "candidate_range_count", @offsetOf(abi.IdaRangeSetSummary, "candidate_range_count"), true);
    try writeOffset(writer, "selected_range_count", @offsetOf(abi.IdaRangeSetSummary, "selected_range_count"), true);
    try writeOffset(writer, "first_selected_id", @offsetOf(abi.IdaRangeSetSummary, "first_selected_id"), true);
    try writeOffset(writer, "last_selected_id", @offsetOf(abi.IdaRangeSetSummary, "last_selected_id"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.IdaRangeSetSummary, "flags"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.IdaRangeSetSummary, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_ida_policy_view", @sizeOf(abi.IdaPolicyView), @alignOf(abi.IdaPolicyView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.IdaPolicyView, "bits_addr"), true);
    try writeOffset(writer, "base_id", @offsetOf(abi.IdaPolicyView, "base_id"), true);
    try writeOffset(writer, "nbits", @offsetOf(abi.IdaPolicyView, "nbits"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.IdaPolicyView, "max_scan"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.IdaPolicyView, "request_count"), true);
    try writeOffset(writer, "policy", @offsetOf(abi.IdaPolicyView, "policy"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.IdaPolicyView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_ida_policy_summary", @sizeOf(abi.IdaPolicySummary), @alignOf(abi.IdaPolicySummary));
    try writeOffset(writer, "scanned_count", @offsetOf(abi.IdaPolicySummary, "scanned_count"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.IdaPolicySummary, "request_count"), true);
    try writeOffset(writer, "selected_fit_id", @offsetOf(abi.IdaPolicySummary, "selected_fit_id"), true);
    try writeOffset(writer, "alternate_fit_id", @offsetOf(abi.IdaPolicySummary, "alternate_fit_id"), true);
    try writeOffset(writer, "longest_free_run", @offsetOf(abi.IdaPolicySummary, "longest_free_run"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.IdaPolicySummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_minor_alloc_view", @sizeOf(abi.MinorAllocView), @alignOf(abi.MinorAllocView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.MinorAllocView, "bits_addr"), true);
    try writeOffset(writer, "major", @offsetOf(abi.MinorAllocView, "major"), true);
    try writeOffset(writer, "first_minor", @offsetOf(abi.MinorAllocView, "first_minor"), true);
    try writeOffset(writer, "minor_count", @offsetOf(abi.MinorAllocView, "minor_count"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.MinorAllocView, "max_scan"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.MinorAllocView, "request_count"), true);
    try writeOffset(writer, "policy", @offsetOf(abi.MinorAllocView, "policy"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.MinorAllocView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_minor_alloc_summary", @sizeOf(abi.MinorAllocSummary), @alignOf(abi.MinorAllocSummary));
    try writeOffset(writer, "major", @offsetOf(abi.MinorAllocSummary, "major"), true);
    try writeOffset(writer, "scanned_count", @offsetOf(abi.MinorAllocSummary, "scanned_count"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.MinorAllocSummary, "request_count"), true);
    try writeOffset(writer, "selected_minor_start", @offsetOf(abi.MinorAllocSummary, "selected_minor_start"), true);
    try writeOffset(writer, "selected_minor_end", @offsetOf(abi.MinorAllocSummary, "selected_minor_end"), true);
    try writeOffset(writer, "alternate_minor_start", @offsetOf(abi.MinorAllocSummary, "alternate_minor_start"), true);
    try writeOffset(writer, "longest_free_run", @offsetOf(abi.MinorAllocSummary, "longest_free_run"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.MinorAllocSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_dev_region_view", @sizeOf(abi.DevRegionView), @alignOf(abi.DevRegionView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.DevRegionView, "bits_addr"), true);
    try writeOffset(writer, "major", @offsetOf(abi.DevRegionView, "major"), true);
    try writeOffset(writer, "first_minor", @offsetOf(abi.DevRegionView, "first_minor"), true);
    try writeOffset(writer, "minor_count", @offsetOf(abi.DevRegionView, "minor_count"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.DevRegionView, "max_scan"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.DevRegionView, "request_count"), true);
    try writeOffset(writer, "policy", @offsetOf(abi.DevRegionView, "policy"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.DevRegionView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_dev_region_summary", @sizeOf(abi.DevRegionSummary), @alignOf(abi.DevRegionSummary));
    try writeOffset(writer, "major", @offsetOf(abi.DevRegionSummary, "major"), true);
    try writeOffset(writer, "scanned_count", @offsetOf(abi.DevRegionSummary, "scanned_count"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.DevRegionSummary, "request_count"), true);
    try writeOffset(writer, "selected_minor_start", @offsetOf(abi.DevRegionSummary, "selected_minor_start"), true);
    try writeOffset(writer, "selected_minor_end", @offsetOf(abi.DevRegionSummary, "selected_minor_end"), true);
    try writeOffset(writer, "first_dev", @offsetOf(abi.DevRegionSummary, "first_dev"), true);
    try writeOffset(writer, "last_dev", @offsetOf(abi.DevRegionSummary, "last_dev"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.DevRegionSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_cdev_add_view", @sizeOf(abi.CdevAddView), @alignOf(abi.CdevAddView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.CdevAddView, "bits_addr"), true);
    try writeOffset(writer, "major", @offsetOf(abi.CdevAddView, "major"), true);
    try writeOffset(writer, "first_minor", @offsetOf(abi.CdevAddView, "first_minor"), true);
    try writeOffset(writer, "minor_count", @offsetOf(abi.CdevAddView, "minor_count"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.CdevAddView, "max_scan"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.CdevAddView, "request_count"), true);
    try writeOffset(writer, "policy", @offsetOf(abi.CdevAddView, "policy"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.CdevAddView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_cdev_add_summary", @sizeOf(abi.CdevAddSummary), @alignOf(abi.CdevAddSummary));
    try writeOffset(writer, "major", @offsetOf(abi.CdevAddSummary, "major"), true);
    try writeOffset(writer, "scanned_count", @offsetOf(abi.CdevAddSummary, "scanned_count"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.CdevAddSummary, "request_count"), true);
    try writeOffset(writer, "selected_count", @offsetOf(abi.CdevAddSummary, "selected_count"), true);
    try writeOffset(writer, "first_minor", @offsetOf(abi.CdevAddSummary, "first_minor"), true);
    try writeOffset(writer, "first_dev", @offsetOf(abi.CdevAddSummary, "first_dev"), true);
    try writeOffset(writer, "last_dev", @offsetOf(abi.CdevAddSummary, "last_dev"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.CdevAddSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_cdev_lookup_view", @sizeOf(abi.CdevLookupView), @alignOf(abi.CdevLookupView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.CdevLookupView, "bits_addr"), true);
    try writeOffset(writer, "major", @offsetOf(abi.CdevLookupView, "major"), true);
    try writeOffset(writer, "first_minor", @offsetOf(abi.CdevLookupView, "first_minor"), true);
    try writeOffset(writer, "minor_count", @offsetOf(abi.CdevLookupView, "minor_count"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.CdevLookupView, "max_scan"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.CdevLookupView, "request_count"), true);
    try writeOffset(writer, "policy", @offsetOf(abi.CdevLookupView, "policy"), true);
    try writeOffset(writer, "target_minor", @offsetOf(abi.CdevLookupView, "target_minor"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.CdevLookupView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_cdev_lookup_summary", @sizeOf(abi.CdevLookupSummary), @alignOf(abi.CdevLookupSummary));
    try writeOffset(writer, "major", @offsetOf(abi.CdevLookupSummary, "major"), true);
    try writeOffset(writer, "scanned_count", @offsetOf(abi.CdevLookupSummary, "scanned_count"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.CdevLookupSummary, "request_count"), true);
    try writeOffset(writer, "selected_count", @offsetOf(abi.CdevLookupSummary, "selected_count"), true);
    try writeOffset(writer, "first_minor", @offsetOf(abi.CdevLookupSummary, "first_minor"), true);
    try writeOffset(writer, "target_minor", @offsetOf(abi.CdevLookupSummary, "target_minor"), true);
    try writeOffset(writer, "resolved_index", @offsetOf(abi.CdevLookupSummary, "resolved_index"), true);
    try writeOffset(writer, "resolved_dev", @offsetOf(abi.CdevLookupSummary, "resolved_dev"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.CdevLookupSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_chrdev_open_view", @sizeOf(abi.ChrdevOpenView), @alignOf(abi.ChrdevOpenView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.ChrdevOpenView, "bits_addr"), true);
    try writeOffset(writer, "major", @offsetOf(abi.ChrdevOpenView, "major"), true);
    try writeOffset(writer, "first_minor", @offsetOf(abi.ChrdevOpenView, "first_minor"), true);
    try writeOffset(writer, "minor_count", @offsetOf(abi.ChrdevOpenView, "minor_count"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.ChrdevOpenView, "max_scan"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.ChrdevOpenView, "request_count"), true);
    try writeOffset(writer, "policy", @offsetOf(abi.ChrdevOpenView, "policy"), true);
    try writeOffset(writer, "target_minor", @offsetOf(abi.ChrdevOpenView, "target_minor"), true);
    try writeOffset(writer, "requested_mode", @offsetOf(abi.ChrdevOpenView, "requested_mode"), true);
    try writeOffset(writer, "supported_mode", @offsetOf(abi.ChrdevOpenView, "supported_mode"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.ChrdevOpenView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_chrdev_open_summary", @sizeOf(abi.ChrdevOpenSummary), @alignOf(abi.ChrdevOpenSummary));
    try writeOffset(writer, "major", @offsetOf(abi.ChrdevOpenSummary, "major"), true);
    try writeOffset(writer, "target_minor", @offsetOf(abi.ChrdevOpenSummary, "target_minor"), true);
    try writeOffset(writer, "selected_count", @offsetOf(abi.ChrdevOpenSummary, "selected_count"), true);
    try writeOffset(writer, "resolved_index", @offsetOf(abi.ChrdevOpenSummary, "resolved_index"), true);
    try writeOffset(writer, "resolved_dev", @offsetOf(abi.ChrdevOpenSummary, "resolved_dev"), true);
    try writeOffset(writer, "requested_mode", @offsetOf(abi.ChrdevOpenSummary, "requested_mode"), true);
    try writeOffset(writer, "supported_mode", @offsetOf(abi.ChrdevOpenSummary, "supported_mode"), true);
    try writeOffset(writer, "granted_mode", @offsetOf(abi.ChrdevOpenSummary, "granted_mode"), true);
    try writeOffset(writer, "denied_mode", @offsetOf(abi.ChrdevOpenSummary, "denied_mode"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.ChrdevOpenSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_chrdev_fops_view", @sizeOf(abi.ChrdevFopsView), @alignOf(abi.ChrdevFopsView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.ChrdevFopsView, "bits_addr"), true);
    try writeOffset(writer, "major", @offsetOf(abi.ChrdevFopsView, "major"), true);
    try writeOffset(writer, "first_minor", @offsetOf(abi.ChrdevFopsView, "first_minor"), true);
    try writeOffset(writer, "minor_count", @offsetOf(abi.ChrdevFopsView, "minor_count"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.ChrdevFopsView, "max_scan"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.ChrdevFopsView, "request_count"), true);
    try writeOffset(writer, "policy", @offsetOf(abi.ChrdevFopsView, "policy"), true);
    try writeOffset(writer, "target_minor", @offsetOf(abi.ChrdevFopsView, "target_minor"), true);
    try writeOffset(writer, "requested_mode", @offsetOf(abi.ChrdevFopsView, "requested_mode"), true);
    try writeOffset(writer, "supported_mode", @offsetOf(abi.ChrdevFopsView, "supported_mode"), true);
    try writeOffset(writer, "available_ops", @offsetOf(abi.ChrdevFopsView, "available_ops"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.ChrdevFopsView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_chrdev_fops_summary", @sizeOf(abi.ChrdevFopsSummary), @alignOf(abi.ChrdevFopsSummary));
    try writeOffset(writer, "major", @offsetOf(abi.ChrdevFopsSummary, "major"), true);
    try writeOffset(writer, "target_minor", @offsetOf(abi.ChrdevFopsSummary, "target_minor"), true);
    try writeOffset(writer, "selected_count", @offsetOf(abi.ChrdevFopsSummary, "selected_count"), true);
    try writeOffset(writer, "resolved_index", @offsetOf(abi.ChrdevFopsSummary, "resolved_index"), true);
    try writeOffset(writer, "resolved_dev", @offsetOf(abi.ChrdevFopsSummary, "resolved_dev"), true);
    try writeOffset(writer, "granted_mode", @offsetOf(abi.ChrdevFopsSummary, "granted_mode"), true);
    try writeOffset(writer, "available_ops", @offsetOf(abi.ChrdevFopsSummary, "available_ops"), true);
    try writeOffset(writer, "required_ops", @offsetOf(abi.ChrdevFopsSummary, "required_ops"), true);
    try writeOffset(writer, "missing_ops", @offsetOf(abi.ChrdevFopsSummary, "missing_ops"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.ChrdevFopsSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_chrdev_route_view", @sizeOf(abi.ChrdevRouteView), @alignOf(abi.ChrdevRouteView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.ChrdevRouteView, "bits_addr"), true);
    try writeOffset(writer, "major", @offsetOf(abi.ChrdevRouteView, "major"), true);
    try writeOffset(writer, "first_minor", @offsetOf(abi.ChrdevRouteView, "first_minor"), true);
    try writeOffset(writer, "minor_count", @offsetOf(abi.ChrdevRouteView, "minor_count"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.ChrdevRouteView, "max_scan"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.ChrdevRouteView, "request_count"), true);
    try writeOffset(writer, "policy", @offsetOf(abi.ChrdevRouteView, "policy"), true);
    try writeOffset(writer, "target_minor", @offsetOf(abi.ChrdevRouteView, "target_minor"), true);
    try writeOffset(writer, "requested_mode", @offsetOf(abi.ChrdevRouteView, "requested_mode"), true);
    try writeOffset(writer, "supported_mode", @offsetOf(abi.ChrdevRouteView, "supported_mode"), true);
    try writeOffset(writer, "available_ops", @offsetOf(abi.ChrdevRouteView, "available_ops"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.ChrdevRouteView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_chrdev_route_summary", @sizeOf(abi.ChrdevRouteSummary), @alignOf(abi.ChrdevRouteSummary));
    try writeOffset(writer, "major", @offsetOf(abi.ChrdevRouteSummary, "major"), true);
    try writeOffset(writer, "target_minor", @offsetOf(abi.ChrdevRouteSummary, "target_minor"), true);
    try writeOffset(writer, "selected_count", @offsetOf(abi.ChrdevRouteSummary, "selected_count"), true);
    try writeOffset(writer, "resolved_index", @offsetOf(abi.ChrdevRouteSummary, "resolved_index"), true);
    try writeOffset(writer, "resolved_dev", @offsetOf(abi.ChrdevRouteSummary, "resolved_dev"), true);
    try writeOffset(writer, "granted_mode", @offsetOf(abi.ChrdevRouteSummary, "granted_mode"), true);
    try writeOffset(writer, "entry_ops", @offsetOf(abi.ChrdevRouteSummary, "entry_ops"), true);
    try writeOffset(writer, "data_ops", @offsetOf(abi.ChrdevRouteSummary, "data_ops"), true);
    try writeOffset(writer, "exit_ops", @offsetOf(abi.ChrdevRouteSummary, "exit_ops"), true);
    try writeOffset(writer, "blocked_ops", @offsetOf(abi.ChrdevRouteSummary, "blocked_ops"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.ChrdevRouteSummary, "flags"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_chrdev_io_view", @sizeOf(abi.ChrdevIoView), @alignOf(abi.ChrdevIoView));
    try writeOffset(writer, "bits_addr", @offsetOf(abi.ChrdevIoView, "bits_addr"), true);
    try writeOffset(writer, "major", @offsetOf(abi.ChrdevIoView, "major"), true);
    try writeOffset(writer, "first_minor", @offsetOf(abi.ChrdevIoView, "first_minor"), true);
    try writeOffset(writer, "minor_count", @offsetOf(abi.ChrdevIoView, "minor_count"), true);
    try writeOffset(writer, "max_scan", @offsetOf(abi.ChrdevIoView, "max_scan"), true);
    try writeOffset(writer, "request_count", @offsetOf(abi.ChrdevIoView, "request_count"), true);
    try writeOffset(writer, "policy", @offsetOf(abi.ChrdevIoView, "policy"), true);
    try writeOffset(writer, "target_minor", @offsetOf(abi.ChrdevIoView, "target_minor"), true);
    try writeOffset(writer, "requested_mode", @offsetOf(abi.ChrdevIoView, "requested_mode"), true);
    try writeOffset(writer, "supported_mode", @offsetOf(abi.ChrdevIoView, "supported_mode"), true);
    try writeOffset(writer, "available_ops", @offsetOf(abi.ChrdevIoView, "available_ops"), true);
    try writeOffset(writer, "io_op", @offsetOf(abi.ChrdevIoView, "io_op"), true);
    try writeOffset(writer, "requested_bytes", @offsetOf(abi.ChrdevIoView, "requested_bytes"), true);
    try writeOffset(writer, "max_chunk_bytes", @offsetOf(abi.ChrdevIoView, "max_chunk_bytes"), true);
    try writeOffset(writer, "reserved", @offsetOf(abi.ChrdevIoView, "reserved"), false);
    try writer.writeAll("}},");

    try writeLayoutPrefix(writer, "zigux_chrdev_io_summary", @sizeOf(abi.ChrdevIoSummary), @alignOf(abi.ChrdevIoSummary));
    try writeOffset(writer, "major", @offsetOf(abi.ChrdevIoSummary, "major"), true);
    try writeOffset(writer, "target_minor", @offsetOf(abi.ChrdevIoSummary, "target_minor"), true);
    try writeOffset(writer, "selected_count", @offsetOf(abi.ChrdevIoSummary, "selected_count"), true);
    try writeOffset(writer, "resolved_index", @offsetOf(abi.ChrdevIoSummary, "resolved_index"), true);
    try writeOffset(writer, "resolved_dev", @offsetOf(abi.ChrdevIoSummary, "resolved_dev"), true);
    try writeOffset(writer, "granted_mode", @offsetOf(abi.ChrdevIoSummary, "granted_mode"), true);
    try writeOffset(writer, "io_op", @offsetOf(abi.ChrdevIoSummary, "io_op"), true);
    try writeOffset(writer, "requested_bytes", @offsetOf(abi.ChrdevIoSummary, "requested_bytes"), true);
    try writeOffset(writer, "chunk_bytes", @offsetOf(abi.ChrdevIoSummary, "chunk_bytes"), true);
    try writeOffset(writer, "entry_ops", @offsetOf(abi.ChrdevIoSummary, "entry_ops"), true);
    try writeOffset(writer, "data_ops", @offsetOf(abi.ChrdevIoSummary, "data_ops"), true);
    try writeOffset(writer, "exit_ops", @offsetOf(abi.ChrdevIoSummary, "exit_ops"), true);
    try writeOffset(writer, "blocked_ops", @offsetOf(abi.ChrdevIoSummary, "blocked_ops"), true);
    try writeOffset(writer, "flags", @offsetOf(abi.ChrdevIoSummary, "flags"), false);
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
