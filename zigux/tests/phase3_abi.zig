const std = @import("std");
const abi = @import("abi_bindings");
const layout_assert = @import("layout_assert");
const panic_policy = @import("panic_policy");
const allocator_policy = @import("allocator_policy");
const atomic = @import("atomic_helpers");
const barrier = @import("barrier_helpers");
const mmio = @import("mmio_helpers");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");
const list_view = @import("list_view");
const hlist_view = @import("hlist_view");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");
const idr_slot_view = @import("idr_slot_view");
const ida_bitmap_view = @import("ida_bitmap_view");
const ida_alloc_view = @import("ida_alloc_view");
const ida_range_view = @import("ida_range_view");
const ida_range_set_view = @import("ida_range_set_view");
const ida_policy_view = @import("ida_policy_view");
const minor_alloc_plan = @import("minor_alloc_plan");
const dev_region_plan = @import("dev_region_plan");
const cdev_add_plan = @import("cdev_add_plan");
const cdev_lookup_plan = @import("cdev_lookup_plan");
const chrdev_open_plan = @import("chrdev_open_plan");
const chrdev_fops_plan = @import("chrdev_fops_plan");
const chrdev_route_plan = @import("chrdev_route_plan");
const chrdev_io_plan = @import("chrdev_io_plan");
const chrdev_xfer_plan = @import("chrdev_xfer_plan");
const chrdev_resume_plan = @import("chrdev_resume_plan");
const export_shim = @import("export_shim");
const narrow = @import("narrow_unsafe");
const uapi_version = @import("uapi_version");

test "phase3 abi slice uses stable canonical layouts" {
    comptime {
        layout_assert.assertSize(abi.BoundaryHeader, 8);
        layout_assert.assertSize(abi.ExportStatus, 8);
        layout_assert.assertSize(abi.InteropPolicy, 4);
        layout_assert.assertOffset(abi.BitmapView, "nbits", @sizeOf(usize));
        layout_assert.assertOffset(abi.BitmapView, "word_count", @sizeOf(usize) + 4);
        layout_assert.assertOffset(abi.CpuMaskView, "nr_cpu_ids", @sizeOf(usize));
        layout_assert.assertSize(abi.BitmapSummary, 16);
        layout_assert.assertSize(abi.CpuMaskSummary, 16);
        layout_assert.assertSize(abi.ListSummary, 8);
        layout_assert.assertSize(abi.HListSummary, 8);
        layout_assert.assertSize(abi.ErrPtrSummary, 8);
        layout_assert.assertSize(abi.XaValueSummary, @sizeOf(usize) + 8);
        layout_assert.assertSize(abi.XaSlotView, @sizeOf(usize) + 8);
        layout_assert.assertSize(abi.XaSlotSummary, 24);
        layout_assert.assertSize(abi.IdrSlotView, @sizeOf(usize) + 16);
        layout_assert.assertSize(abi.IdrSlotSummary, 32);
        layout_assert.assertSize(abi.IdaBitmapView, @sizeOf(usize) + 16);
        layout_assert.assertSize(abi.IdaBitmapSummary, 24);
        layout_assert.assertSize(abi.IdaAllocView, @sizeOf(usize) + 24);
        layout_assert.assertSize(abi.IdaAllocSummary, 24);
        layout_assert.assertSize(abi.IdaRangeView, @sizeOf(usize) + 24);
        layout_assert.assertSize(abi.IdaRangeSummary, 24);
        layout_assert.assertSize(abi.IdaRangeSetView, @sizeOf(usize) + 32);
        layout_assert.assertSize(abi.IdaRangeSetSummary, 32);
        layout_assert.assertSize(abi.IdaPolicyView, @sizeOf(usize) + 24);
        layout_assert.assertSize(abi.IdaPolicySummary, 24);
        layout_assert.assertSize(abi.MinorAllocView, @sizeOf(usize) + 32);
        layout_assert.assertSize(abi.MinorAllocSummary, 32);
        layout_assert.assertSize(abi.DevRegionView, @sizeOf(usize) + 32);
        layout_assert.assertSize(abi.DevRegionSummary, 32);
        layout_assert.assertSize(abi.CdevAddView, @sizeOf(usize) + 32);
        layout_assert.assertSize(abi.CdevAddSummary, 32);
        layout_assert.assertSize(abi.CdevLookupView, @sizeOf(usize) + 32);
        layout_assert.assertSize(abi.CdevLookupSummary, 36);
        layout_assert.assertSize(abi.ChrdevOpenView, @sizeOf(usize) + 40);
        layout_assert.assertSize(abi.ChrdevOpenSummary, 40);
        layout_assert.assertSize(abi.ChrdevFopsView, @sizeOf(usize) + 48);
        layout_assert.assertSize(abi.ChrdevFopsSummary, 40);
        layout_assert.assertSize(abi.ChrdevRouteView, @sizeOf(usize) + 48);
        layout_assert.assertSize(abi.ChrdevRouteSummary, 44);
        layout_assert.assertSize(abi.ChrdevIoView, @sizeOf(usize) + 56);
        layout_assert.assertSize(abi.ChrdevIoSummary, 56);
        layout_assert.assertSize(abi.ChrdevXferView, @sizeOf(usize) + 80);
        layout_assert.assertSize(abi.ChrdevXferSummary, 96);
        layout_assert.assertSize(abi.ChrdevResumeView, @sizeOf(usize) + 80);
        layout_assert.assertSize(abi.ChrdevResumeSummary, 88);
        layout_assert.assertOffset(abi.BitmapSummary, "first_zero", 4);
        layout_assert.assertOffset(abi.CpuMaskSummary, "next_cpu", 4);
        layout_assert.assertOffset(abi.ListHeadRef, "prev_addr", @sizeOf(usize));
        layout_assert.assertOffset(abi.ListView, "max_nodes", @sizeOf(usize));
        layout_assert.assertOffset(abi.HListNodeRef, "pprev_addr", @sizeOf(usize));
        layout_assert.assertOffset(abi.HListView, "max_nodes", @sizeOf(usize));
        layout_assert.assertOffset(abi.ErrPtrSummary, "flags", 4);
        layout_assert.assertOffset(abi.XaValueSummary, "decoded_value", @sizeOf(usize));
        layout_assert.assertOffset(abi.XaSlotView, "slot_count", @sizeOf(usize));
        layout_assert.assertOffset(abi.XaSlotSummary, "flags", 20);
        layout_assert.assertOffset(abi.IdrSlotView, "base_id", @sizeOf(usize));
        layout_assert.assertOffset(abi.IdrSlotSummary, "first_present_id", 20);
        layout_assert.assertOffset(abi.IdrSlotSummary, "flags", 28);
        layout_assert.assertOffset(abi.IdaBitmapView, "base_id", @sizeOf(usize));
        layout_assert.assertOffset(abi.IdaBitmapSummary, "first_allocated_id", 8);
        layout_assert.assertOffset(abi.IdaBitmapSummary, "flags", 16);
        layout_assert.assertOffset(abi.IdaAllocView, "base_id", @sizeOf(usize));
        layout_assert.assertOffset(abi.IdaAllocView, "request_count", @sizeOf(usize) + 12);
        layout_assert.assertOffset(abi.IdaAllocSummary, "first_fit_id", 8);
        layout_assert.assertOffset(abi.IdaAllocSummary, "flags", 16);
        layout_assert.assertOffset(abi.IdaRangeView, "base_id", @sizeOf(usize));
        layout_assert.assertOffset(abi.IdaRangeView, "max_ranges", @sizeOf(usize) + 16);
        layout_assert.assertOffset(abi.IdaRangeSummary, "candidate_range_count", 8);
        layout_assert.assertOffset(abi.IdaRangeSummary, "flags", 20);
        layout_assert.assertOffset(abi.IdaRangeSetView, "base_id", @sizeOf(usize));
        layout_assert.assertOffset(abi.IdaRangeSetView, "max_selected", @sizeOf(usize) + 20);
        layout_assert.assertOffset(abi.IdaRangeSetSummary, "selected_range_count", 12);
        layout_assert.assertOffset(abi.IdaRangeSetSummary, "flags", 24);
        layout_assert.assertOffset(abi.IdaPolicyView, "base_id", @sizeOf(usize));
        layout_assert.assertOffset(abi.IdaPolicyView, "policy", @sizeOf(usize) + 16);
        layout_assert.assertOffset(abi.IdaPolicySummary, "alternate_fit_id", 12);
        layout_assert.assertOffset(abi.IdaPolicySummary, "flags", 20);
        layout_assert.assertOffset(abi.MinorAllocView, "major", @sizeOf(usize));
        layout_assert.assertOffset(abi.MinorAllocView, "policy", @sizeOf(usize) + 20);
        layout_assert.assertOffset(abi.MinorAllocSummary, "selected_minor_start", 12);
        layout_assert.assertOffset(abi.MinorAllocSummary, "flags", 28);
        layout_assert.assertOffset(abi.DevRegionView, "major", @sizeOf(usize));
        layout_assert.assertOffset(abi.DevRegionView, "policy", @sizeOf(usize) + 20);
        layout_assert.assertOffset(abi.DevRegionSummary, "selected_minor_start", 12);
        layout_assert.assertOffset(abi.DevRegionSummary, "flags", 28);
        layout_assert.assertOffset(abi.CdevAddView, "major", @sizeOf(usize));
        layout_assert.assertOffset(abi.CdevAddView, "policy", @sizeOf(usize) + 20);
        layout_assert.assertOffset(abi.CdevAddSummary, "selected_count", 12);
        layout_assert.assertOffset(abi.CdevAddSummary, "flags", 28);
        layout_assert.assertOffset(abi.CdevLookupView, "major", @sizeOf(usize));
        layout_assert.assertOffset(abi.CdevLookupView, "target_minor", @sizeOf(usize) + 24);
        layout_assert.assertOffset(abi.CdevLookupSummary, "selected_count", 12);
        layout_assert.assertOffset(abi.CdevLookupSummary, "flags", 32);
        layout_assert.assertOffset(abi.ChrdevOpenView, "major", @sizeOf(usize));
        layout_assert.assertOffset(abi.ChrdevOpenView, "target_minor", @sizeOf(usize) + 24);
        layout_assert.assertOffset(abi.ChrdevOpenView, "requested_mode", @sizeOf(usize) + 28);
        layout_assert.assertOffset(abi.ChrdevOpenSummary, "selected_count", 8);
        layout_assert.assertOffset(abi.ChrdevOpenSummary, "granted_mode", 28);
        layout_assert.assertOffset(abi.ChrdevOpenSummary, "flags", 36);
        layout_assert.assertOffset(abi.ChrdevFopsView, "major", @sizeOf(usize));
        layout_assert.assertOffset(abi.ChrdevFopsView, "target_minor", @sizeOf(usize) + 24);
        layout_assert.assertOffset(abi.ChrdevFopsView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevFopsSummary, "selected_count", 8);
        layout_assert.assertOffset(abi.ChrdevFopsSummary, "granted_mode", 20);
        layout_assert.assertOffset(abi.ChrdevFopsSummary, "flags", 36);
        layout_assert.assertOffset(abi.ChrdevRouteView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevRouteSummary, "selected_count", 8);
        layout_assert.assertOffset(abi.ChrdevRouteSummary, "entry_ops", 24);
        layout_assert.assertOffset(abi.ChrdevRouteSummary, "blocked_ops", 36);
        layout_assert.assertOffset(abi.ChrdevRouteSummary, "flags", 40);
        layout_assert.assertOffset(abi.ChrdevIoView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevIoView, "io_op", @sizeOf(usize) + 40);
        layout_assert.assertOffset(abi.ChrdevIoView, "max_chunk_bytes", @sizeOf(usize) + 48);
        layout_assert.assertOffset(abi.ChrdevIoSummary, "selected_count", 8);
        layout_assert.assertOffset(abi.ChrdevIoSummary, "io_op", 24);
        layout_assert.assertOffset(abi.ChrdevIoSummary, "chunk_bytes", 32);
        layout_assert.assertOffset(abi.ChrdevIoSummary, "blocked_ops", 48);
        layout_assert.assertOffset(abi.ChrdevIoSummary, "flags", 52);
        layout_assert.assertOffset(abi.ChrdevXferView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevXferView, "file_offset", @sizeOf(usize) + 56);
        layout_assert.assertOffset(abi.ChrdevXferView, "max_segments", @sizeOf(usize) + 68);
        layout_assert.assertOffset(abi.ChrdevXferSummary, "start_offset", 32);
        layout_assert.assertOffset(abi.ChrdevXferSummary, "next_offset", 40);
        layout_assert.assertOffset(abi.ChrdevXferSummary, "segment_count", 56);
        layout_assert.assertOffset(abi.ChrdevXferSummary, "entry_ops", 76);
        layout_assert.assertOffset(abi.ChrdevXferSummary, "flags", 92);
        layout_assert.assertOffset(abi.ChrdevResumeView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevResumeView, "file_offset", @sizeOf(usize) + 56);
        layout_assert.assertOffset(abi.ChrdevResumeView, "resume_passes", @sizeOf(usize) + 72);
        layout_assert.assertOffset(abi.ChrdevResumeView, "reserved", @sizeOf(usize) + 76);
        layout_assert.assertOffset(abi.ChrdevResumeSummary, "start_offset", 32);
        layout_assert.assertOffset(abi.ChrdevResumeSummary, "next_offset", 40);
        layout_assert.assertOffset(abi.ChrdevResumeSummary, "initial_bytes_completed", 48);
        layout_assert.assertOffset(abi.ChrdevResumeSummary, "pass_count", 56);
        layout_assert.assertOffset(abi.ChrdevResumeSummary, "entry_ops", 68);
        layout_assert.assertOffset(abi.ChrdevResumeSummary, "flags", 84);
        layout_assert.assertOffset(abi.MmioRange, "length", @sizeOf(usize));
    }
}

test "phase3 abi slice wires policies and exports" {
    try std.testing.expectEqual(abi.ABI_VERSION, uapi_version.abi_version);
    try std.testing.expect(panic_policy.canReturn(.warn));
    try std.testing.expect(allocator_policy.requiresExplicitCaller(.caller_provided));

    const status = export_shim.errno(-12, .kernel);
    try std.testing.expectEqual(@as(i32, -12), status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), status.flags);
}

test "phase3 abi slice wires atomic and mmio helpers" {
    var value: u32 = 3;
    try std.testing.expectEqual(@as(u32, 3), atomic.load(u32, &value, .seq_cst));
    atomic.store(u32, &value, 5, .seq_cst);
    try std.testing.expectEqual(@as(u32, 5), value);
    _ = atomic.exchange(u32, &value, 7, .seq_cst);
    try std.testing.expectEqual(@as(u32, 7), value);

    var regs = [_]u32{ 0, 0 };
    const base = narrow.addressOf(&regs[0]);
    mmio.write32(base, @sizeOf(u32), 0x12345678);
    try std.testing.expectEqual(@as(u32, 0x12345678), mmio.read32(base, @sizeOf(u32)));

    barrier.acquire();
    barrier.release();
    barrier.full();
}

test "phase3 bitmap/cpumask interop helpers stay aligned with the ABI substrate" {
    var bitmap_words = [_]usize{
        (@as(usize, 1) << 1) | (@as(usize, 1) << 5) | (@as(usize, 1) << 63),
        (@as(usize, 1) << 4) | (@as(usize, 1) << 9),
    };
    const bitmap = bitmap_view.viewFromWords(bitmap_words[0..], bitmap_view.bits_per_long + 10);
    const bitmap_summary = bitmap_view.summarize(bitmap);

    try std.testing.expect(bitmap_view.isValid(bitmap));
    try std.testing.expectEqual(@as(u32, 1), bitmap_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), bitmap_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 5), bitmap_summary.weight);

    var cpumask_bits = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 6) | (@as(usize, 1) << 9)};
    const cpumask = cpumask_view.viewFromBits(cpumask_bits[0..], 12);
    const cpumask_summary = cpumask_view.summarize(cpumask);

    try std.testing.expect(cpumask_view.isValid(cpumask));
    try std.testing.expectEqual(@as(u32, 0), cpumask_summary.first_cpu);
    try std.testing.expectEqual(@as(u32, 2), cpumask_summary.next_cpu);
    try std.testing.expectEqual(@as(u32, 4), cpumask_summary.weight);
}

test "phase3 list/hlist interop helpers stay aligned with the ABI substrate" {
    var list_head = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    var list_node_a = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    var list_node_b = abi.ListHeadRef{ .next_addr = undefined, .prev_addr = undefined };
    const list_head_addr = narrow.addressOf(&list_head);
    const list_node_a_addr = narrow.addressOf(&list_node_a);
    const list_node_b_addr = narrow.addressOf(&list_node_b);

    list_head.next_addr = list_node_a_addr;
    list_head.prev_addr = list_node_b_addr;
    list_node_a.next_addr = list_node_b_addr;
    list_node_a.prev_addr = list_head_addr;
    list_node_b.next_addr = list_head_addr;
    list_node_b.prev_addr = list_node_a_addr;

    const list = list_view.viewFromHead(&list_head, 8);
    const list_summary = list_view.summarize(list);
    try std.testing.expect(list_view.isValid(list));
    try std.testing.expectEqual(@as(u32, 2), list_summary.length);
    try std.testing.expectEqual(@as(u32, abi.LIST_FLAG_CIRCULAR), list_summary.flags);

    var hlist_head = abi.HListHeadRef{ .first_addr = undefined };
    var hlist_node_a = abi.HListNodeRef{ .next_addr = undefined, .pprev_addr = undefined };
    var hlist_node_b = abi.HListNodeRef{ .next_addr = undefined, .pprev_addr = undefined };
    const hlist_node_a_addr = narrow.addressOf(&hlist_node_a);
    const hlist_node_b_addr = narrow.addressOf(&hlist_node_b);

    hlist_head.first_addr = hlist_node_a_addr;
    hlist_node_a.next_addr = hlist_node_b_addr;
    hlist_node_a.pprev_addr = narrow.addressOf(&hlist_head.first_addr);
    hlist_node_b.next_addr = 0;
    hlist_node_b.pprev_addr = narrow.addressOf(&hlist_node_a.next_addr);

    const hlist = hlist_view.viewFromHead(&hlist_head, 8);
    const hlist_summary = hlist_view.summarize(hlist);
    try std.testing.expect(hlist_view.isValid(hlist));
    try std.testing.expectEqual(@as(u32, 2), hlist_summary.length);
    try std.testing.expectEqual(@as(u32, abi.HLIST_FLAG_TERMINATED), hlist_summary.flags);
}

test "phase3 err_ptr and encoded value helpers stay aligned with the ABI substrate" {
    const err_addr = err_ptr.fromErrno(-22);
    const err_summary = err_ptr.summarize(err_addr);
    const null_summary = err_ptr.summarize(0);
    const plain_addr: usize = 0x1000;
    const plain_summary = xa_value.summarize(plain_addr);
    const encoded = xa_value.make(37);
    const encoded_summary = xa_value.summarize(encoded);

    try std.testing.expect(err_ptr.isErr(err_addr));
    try std.testing.expectEqual(@as(i32, -22), err_ptr.toErrno(err_addr));
    try std.testing.expectEqual(@as(i32, -22), err_summary.errno_code);
    try std.testing.expectEqual(@as(u16, abi.ERR_PTR_FLAG_ERROR), err_summary.flags);
    try std.testing.expectEqual(@as(u16, abi.ERR_PTR_FLAG_NULL), null_summary.flags);

    try std.testing.expect(!xa_value.isValue(plain_addr));
    try std.testing.expectEqual(@as(u32, abi.XA_VALUE_FLAG_PLAIN), plain_summary.flags);
    try std.testing.expect(xa_value.isValue(encoded));
    try std.testing.expectEqual(@as(u32, 37), xa_value.toValue(encoded));
    try std.testing.expectEqual(@as(u32, 37), encoded_summary.decoded_value);
    try std.testing.expectEqual(@as(u32, abi.XA_VALUE_FLAG_VALUE), encoded_summary.flags);
}

test "phase3 xarray slot interop helpers stay aligned with the ABI substrate" {
    const slots = [_]usize{
        0,
        0x2000,
        xa_value.make(11),
        err_ptr.fromErrno(-2),
        xa_value.make(29),
        err_ptr.fromErrno(-12),
    };

    const truncated_view = xarray_slot_view.viewFromEntries(slots[0..], 5);
    const truncated_summary = xarray_slot_view.summarize(truncated_view);
    try std.testing.expect(xarray_slot_view.isValid(truncated_view));
    try std.testing.expectEqual(@as(usize, slots[3]), xarray_slot_view.entryAt(truncated_view, 3));
    try std.testing.expectEqual(@as(u32, 5), truncated_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 1), truncated_summary.null_count);
    try std.testing.expectEqual(@as(u32, 2), truncated_summary.value_count);
    try std.testing.expectEqual(@as(u32, 1), truncated_summary.error_count);
    try std.testing.expectEqual(@as(u32, 1), truncated_summary.plain_count);
    try std.testing.expectEqual(@as(u32, abi.XA_SLOT_FLAG_TRUNCATED), truncated_summary.flags);

    const full_view = xarray_slot_view.viewFromEntries(slots[0..], 6);
    const full_summary = xarray_slot_view.summarize(full_view);
    try std.testing.expectEqual(@as(u32, 6), full_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 1), full_summary.null_count);
    try std.testing.expectEqual(@as(u32, 2), full_summary.value_count);
    try std.testing.expectEqual(@as(u32, 2), full_summary.error_count);
    try std.testing.expectEqual(@as(u32, 1), full_summary.plain_count);
    try std.testing.expectEqual(@as(u32, 0), full_summary.flags);
}

test "phase3 idr slot interop helpers stay aligned with the ABI substrate" {
    const slots = [_]usize{
        0,
        0x2000,
        xa_value.make(11),
        err_ptr.fromErrno(-2),
        xa_value.make(29),
        err_ptr.fromErrno(-12),
    };

    const truncated_view = idr_slot_view.viewFromEntries(slots[0..], 64, 5);
    const truncated_summary = idr_slot_view.summarize(truncated_view);
    try std.testing.expect(idr_slot_view.isValid(truncated_view));
    try std.testing.expectEqual(@as(usize, slots[2]), idr_slot_view.entryAt(truncated_view, 2));
    try std.testing.expectEqual(@as(u32, 5), truncated_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 4), truncated_summary.present_count);
    try std.testing.expectEqual(@as(u32, 2), truncated_summary.value_count);
    try std.testing.expectEqual(@as(u32, 1), truncated_summary.error_count);
    try std.testing.expectEqual(@as(u32, 1), truncated_summary.plain_count);
    try std.testing.expectEqual(@as(u32, 65), truncated_summary.first_present_id);
    try std.testing.expectEqual(@as(u32, 64), truncated_summary.next_free_id);
    try std.testing.expectEqual(@as(u32, abi.IDR_SLOT_FLAG_TRUNCATED), truncated_summary.flags);

    const full_view = idr_slot_view.viewFromEntries(slots[0..], 64, 6);
    const full_summary = idr_slot_view.summarize(full_view);
    try std.testing.expectEqual(@as(u32, 6), full_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 5), full_summary.present_count);
    try std.testing.expectEqual(@as(u32, 2), full_summary.value_count);
    try std.testing.expectEqual(@as(u32, 2), full_summary.error_count);
    try std.testing.expectEqual(@as(u32, 1), full_summary.plain_count);
    try std.testing.expectEqual(@as(u32, 65), full_summary.first_present_id);
    try std.testing.expectEqual(@as(u32, 64), full_summary.next_free_id);
    try std.testing.expectEqual(@as(u32, 0), full_summary.flags);
}

test "phase3 ida bitmap interop helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 3) | (@as(usize, 1) << 5)};

    const truncated_view = ida_bitmap_view.viewFromBits(words[0..], 100, 7, 6);
    const truncated_summary = ida_bitmap_view.summarize(truncated_view);
    try std.testing.expect(ida_bitmap_view.isValid(truncated_view));
    try std.testing.expectEqual(@as(u32, 6), truncated_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 4), truncated_summary.allocated_count);
    try std.testing.expectEqual(@as(u32, 100), truncated_summary.first_allocated_id);
    try std.testing.expectEqual(@as(u32, 101), truncated_summary.first_free_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_BITMAP_FLAG_TRUNCATED), truncated_summary.flags);

    const full_view = ida_bitmap_view.viewFromBits(words[0..], 100, 6, 6);
    const full_summary = ida_bitmap_view.summarize(full_view);
    try std.testing.expectEqual(@as(u32, 6), full_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 4), full_summary.allocated_count);
    try std.testing.expectEqual(@as(u32, 100), full_summary.first_allocated_id);
    try std.testing.expectEqual(@as(u32, 101), full_summary.first_free_id);
    try std.testing.expectEqual(@as(u32, 0), full_summary.flags);
}

test "phase3 ida allocation interop helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const truncated_view = ida_alloc_view.viewFromBits(words[0..], 100, 8, 6, 2);
    const truncated_summary = ida_alloc_view.summarize(truncated_view);
    try std.testing.expect(ida_alloc_view.isValid(truncated_view));
    try std.testing.expectEqual(@as(u32, 6), truncated_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), truncated_summary.request_count);
    try std.testing.expectEqual(@as(u32, 101), truncated_summary.first_fit_id);
    try std.testing.expectEqual(@as(u32, 2), truncated_summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.IDA_ALLOC_FLAG_TRUNCATED | abi.IDA_ALLOC_FLAG_FOUND), truncated_summary.flags);

    const full_view = ida_alloc_view.viewFromBits(words[0..], 100, 8, 8, 2);
    const full_summary = ida_alloc_view.summarize(full_view);
    try std.testing.expectEqual(@as(u32, 8), full_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), full_summary.request_count);
    try std.testing.expectEqual(@as(u32, 101), full_summary.first_fit_id);
    try std.testing.expectEqual(@as(u32, 3), full_summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.IDA_ALLOC_FLAG_FOUND), full_summary.flags);
}

test "phase3 ida range interop helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const truncated_view = ida_range_view.viewFromBits(words[0..], 100, 8, 6, 2, 4);
    const truncated_summary = ida_range_view.summarize(truncated_view);
    try std.testing.expect(ida_range_view.isValid(truncated_view));
    try std.testing.expectEqual(@as(u32, 6), truncated_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), truncated_summary.request_count);
    try std.testing.expectEqual(@as(u32, 2), truncated_summary.candidate_range_count);
    try std.testing.expectEqual(@as(u32, 101), truncated_summary.first_range_id);
    try std.testing.expectEqual(@as(u32, 104), truncated_summary.last_range_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_RANGE_FLAG_TRUNCATED | abi.IDA_RANGE_FLAG_FOUND), truncated_summary.flags);

    const capped_view = ida_range_view.viewFromBits(words[0..], 100, 8, 8, 2, 2);
    const capped_summary = ida_range_view.summarize(capped_view);
    try std.testing.expectEqual(@as(u32, 8), capped_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), capped_summary.request_count);
    try std.testing.expectEqual(@as(u32, 2), capped_summary.candidate_range_count);
    try std.testing.expectEqual(@as(u32, 101), capped_summary.first_range_id);
    try std.testing.expectEqual(@as(u32, 104), capped_summary.last_range_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_RANGE_FLAG_TRUNCATED | abi.IDA_RANGE_FLAG_FOUND), capped_summary.flags);
}

test "phase3 ida range-set interop helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const predictable = ida_range_set_view.viewFromBits(words[0..], 100, 8, 6, 2, 4, 2);
    const predictable_summary = ida_range_set_view.summarize(predictable);
    try std.testing.expect(ida_range_set_view.isValid(predictable));
    try std.testing.expectEqual(@as(u32, 6), predictable_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), predictable_summary.request_count);
    try std.testing.expectEqual(@as(u32, 2), predictable_summary.candidate_range_count);
    try std.testing.expectEqual(@as(u32, 2), predictable_summary.selected_range_count);
    try std.testing.expectEqual(@as(u32, 101), predictable_summary.first_selected_id);
    try std.testing.expectEqual(@as(u32, 104), predictable_summary.last_selected_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_RANGE_SET_FLAG_TRUNCATED | abi.IDA_RANGE_SET_FLAG_FOUND | abi.IDA_RANGE_SET_FLAG_SELECTED), predictable_summary.flags);

    const capped = ida_range_set_view.viewFromBits(words[0..], 100, 8, 8, 2, 4, 1);
    const capped_summary = ida_range_set_view.summarize(capped);
    try std.testing.expectEqual(@as(u32, 3), capped_summary.candidate_range_count);
    try std.testing.expectEqual(@as(u32, 1), capped_summary.selected_range_count);
    try std.testing.expectEqual(@as(u32, 101), capped_summary.first_selected_id);
    try std.testing.expectEqual(@as(u32, 101), capped_summary.last_selected_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_RANGE_SET_FLAG_TRUNCATED | abi.IDA_RANGE_SET_FLAG_FOUND | abi.IDA_RANGE_SET_FLAG_SELECTED), capped_summary.flags);

    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted = ida_range_set_view.viewFromBits(exhausted_words[0..], 40, 5, 5, 2, 4, 2);
    const exhausted_summary = ida_range_set_view.summarize(exhausted);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.candidate_range_count);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.selected_range_count);
    try std.testing.expectEqual(@as(u32, 45), exhausted_summary.first_selected_id);
    try std.testing.expectEqual(@as(u32, 45), exhausted_summary.last_selected_id);
    try std.testing.expectEqual(@as(u32, abi.IDA_RANGE_SET_FLAG_EXHAUSTED), exhausted_summary.flags);
}

test "phase3 ida policy interop helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const first_fit = ida_policy_view.viewFromBits(words[0..], 100, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT);
    const first_fit_summary = ida_policy_view.summarize(first_fit);
    try std.testing.expect(ida_policy_view.isValid(first_fit));
    try std.testing.expectEqual(@as(u32, 6), first_fit_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), first_fit_summary.request_count);
    try std.testing.expectEqual(@as(u32, 101), first_fit_summary.selected_fit_id);
    try std.testing.expectEqual(@as(u32, 104), first_fit_summary.alternate_fit_id);
    try std.testing.expectEqual(@as(u32, 2), first_fit_summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.IDA_POLICY_FLAG_TRUNCATED | abi.IDA_POLICY_FLAG_FOUND), first_fit_summary.flags);

    const last_fit = ida_policy_view.viewFromBits(words[0..], 100, 8, 8, 2, abi.IDA_POLICY_LAST_FIT);
    const last_fit_summary = ida_policy_view.summarize(last_fit);
    try std.testing.expectEqual(@as(u32, 8), last_fit_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 104), last_fit_summary.selected_fit_id);
    try std.testing.expectEqual(@as(u32, 101), last_fit_summary.alternate_fit_id);
    try std.testing.expectEqual(@as(u32, 3), last_fit_summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.IDA_POLICY_FLAG_FOUND), last_fit_summary.flags);

    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted = ida_policy_view.viewFromBits(exhausted_words[0..], 40, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT);
    const exhausted_summary = ida_policy_view.summarize(exhausted);
    try std.testing.expectEqual(@as(u32, 45), exhausted_summary.selected_fit_id);
    try std.testing.expectEqual(@as(u32, 45), exhausted_summary.alternate_fit_id);
    try std.testing.expectEqual(@as(u32, 1), exhausted_summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.IDA_POLICY_FLAG_EXHAUSTED), exhausted_summary.flags);
}

test "phase3 minor allocation consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const first_fit_view = minor_alloc_plan.viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT);
    const first_fit_summary = minor_alloc_plan.summarize(first_fit_view);
    try std.testing.expect(minor_alloc_plan.isValid(first_fit_view));
    try std.testing.expectEqual(@as(u32, 240), first_fit_summary.major);
    try std.testing.expectEqual(@as(u32, 6), first_fit_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), first_fit_summary.request_count);
    try std.testing.expectEqual(@as(u32, 33), first_fit_summary.selected_minor_start);
    try std.testing.expectEqual(@as(u32, 34), first_fit_summary.selected_minor_end);
    try std.testing.expectEqual(@as(u32, 36), first_fit_summary.alternate_minor_start);
    try std.testing.expectEqual(@as(u32, 2), first_fit_summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.MINOR_ALLOC_FLAG_TRUNCATED | abi.MINOR_ALLOC_FLAG_FOUND), first_fit_summary.flags);

    const last_fit_view = minor_alloc_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT);
    const last_fit_summary = minor_alloc_plan.summarize(last_fit_view);
    try std.testing.expectEqual(@as(u32, 36), last_fit_summary.selected_minor_start);
    try std.testing.expectEqual(@as(u32, 37), last_fit_summary.selected_minor_end);
    try std.testing.expectEqual(@as(u32, 33), last_fit_summary.alternate_minor_start);
    try std.testing.expectEqual(@as(u32, 3), last_fit_summary.longest_free_run);
    try std.testing.expectEqual(@as(u32, abi.MINOR_ALLOC_FLAG_FOUND), last_fit_summary.flags);
}

test "phase3 dev region consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const first_fit_view = dev_region_plan.viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT);
    const first_fit_summary = dev_region_plan.summarize(first_fit_view);
    try std.testing.expect(dev_region_plan.isValid(first_fit_view));
    try std.testing.expectEqual(@as(u32, 240), first_fit_summary.major);
    try std.testing.expectEqual(@as(u32, 6), first_fit_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), first_fit_summary.request_count);
    try std.testing.expectEqual(@as(u32, 33), first_fit_summary.selected_minor_start);
    try std.testing.expectEqual(@as(u32, 34), first_fit_summary.selected_minor_end);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 33), first_fit_summary.first_dev);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 34), first_fit_summary.last_dev);
    try std.testing.expectEqual(@as(u32, abi.DEV_REGION_FLAG_TRUNCATED | abi.DEV_REGION_FLAG_FOUND), first_fit_summary.flags);

    const last_fit_view = dev_region_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT);
    const last_fit_summary = dev_region_plan.summarize(last_fit_view);
    try std.testing.expectEqual(@as(u32, 36), last_fit_summary.selected_minor_start);
    try std.testing.expectEqual(@as(u32, 37), last_fit_summary.selected_minor_end);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 36), last_fit_summary.first_dev);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 37), last_fit_summary.last_dev);
    try std.testing.expectEqual(@as(u32, abi.DEV_REGION_FLAG_FOUND), last_fit_summary.flags);
}

test "phase3 cdev add consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const first_fit_view = cdev_add_plan.viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT);
    const first_fit_summary = cdev_add_plan.summarize(first_fit_view);
    try std.testing.expect(cdev_add_plan.isValid(first_fit_view));
    try std.testing.expectEqual(@as(u32, 240), first_fit_summary.major);
    try std.testing.expectEqual(@as(u32, 6), first_fit_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), first_fit_summary.request_count);
    try std.testing.expectEqual(@as(u32, 2), first_fit_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 33), first_fit_summary.first_minor);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 33), first_fit_summary.first_dev);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 34), first_fit_summary.last_dev);
    try std.testing.expectEqual(@as(u32, abi.CDEV_ADD_FLAG_TRUNCATED | abi.CDEV_ADD_FLAG_FOUND), first_fit_summary.flags);

    const last_fit_view = cdev_add_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT);
    const last_fit_summary = cdev_add_plan.summarize(last_fit_view);
    try std.testing.expectEqual(@as(u32, 2), last_fit_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 36), last_fit_summary.first_minor);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 36), last_fit_summary.first_dev);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 37), last_fit_summary.last_dev);
    try std.testing.expectEqual(@as(u32, abi.CDEV_ADD_FLAG_FOUND), last_fit_summary.flags);
}

test "phase3 cdev lookup consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const hit_view = cdev_lookup_plan.viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT, 34);
    const hit_summary = cdev_lookup_plan.summarize(hit_view);
    try std.testing.expect(cdev_lookup_plan.isValid(hit_view));
    try std.testing.expectEqual(@as(u32, 240), hit_summary.major);
    try std.testing.expectEqual(@as(u32, 6), hit_summary.scanned_count);
    try std.testing.expectEqual(@as(u32, 2), hit_summary.request_count);
    try std.testing.expectEqual(@as(u32, 2), hit_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 33), hit_summary.first_minor);
    try std.testing.expectEqual(@as(u32, 34), hit_summary.target_minor);
    try std.testing.expectEqual(@as(u32, 1), hit_summary.resolved_index);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 34), hit_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CDEV_LOOKUP_FLAG_TRUNCATED | abi.CDEV_LOOKUP_FLAG_FOUND | abi.CDEV_LOOKUP_FLAG_HIT), hit_summary.flags);

    const miss_view = cdev_lookup_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 35);
    const miss_summary = cdev_lookup_plan.summarize(miss_view);
    try std.testing.expectEqual(@as(u32, 2), miss_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 36), miss_summary.first_minor);
    try std.testing.expectEqual(@as(u32, 35), miss_summary.target_minor);
    try std.testing.expectEqual(@as(u32, abi.CDEV_LOOKUP_INDEX_NONE), miss_summary.resolved_index);
    try std.testing.expectEqual(@as(u32, 0), miss_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CDEV_LOOKUP_FLAG_FOUND), miss_summary.flags);
}

test "phase3 chrdev open consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const permitted_view = chrdev_open_plan.viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT, 34, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE);
    const permitted_summary = chrdev_open_plan.summarize(permitted_view);
    try std.testing.expect(chrdev_open_plan.isValid(permitted_view));
    try std.testing.expectEqual(@as(u32, 240), permitted_summary.major);
    try std.testing.expectEqual(@as(u32, 34), permitted_summary.target_minor);
    try std.testing.expectEqual(@as(u32, 2), permitted_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 1), permitted_summary.resolved_index);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 34), permitted_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE), permitted_summary.requested_mode);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE), permitted_summary.supported_mode);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE), permitted_summary.granted_mode);
    try std.testing.expectEqual(@as(u32, 0), permitted_summary.denied_mode);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_OPEN_FLAG_TRUNCATED | abi.CHRDEV_OPEN_FLAG_FOUND | abi.CHRDEV_OPEN_FLAG_HIT | abi.CHRDEV_OPEN_FLAG_PERMITTED), permitted_summary.flags);

    const denied_view = chrdev_open_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ);
    const denied_summary = chrdev_open_plan.summarize(denied_view);
    try std.testing.expectEqual(@as(u32, 2), denied_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 1), denied_summary.resolved_index);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 37), denied_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, 0), denied_summary.granted_mode);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_MODE_WRITE), denied_summary.denied_mode);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_OPEN_FLAG_FOUND | abi.CHRDEV_OPEN_FLAG_HIT | abi.CHRDEV_OPEN_FLAG_DENIED), denied_summary.flags);
}

test "phase3 chrdev fops consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const routable_view = chrdev_fops_plan.viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT, 34, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE);
    const routable_summary = chrdev_fops_plan.summarize(routable_view);
    try std.testing.expect(chrdev_fops_plan.isValid(routable_view));
    try std.testing.expectEqual(@as(u32, 240), routable_summary.major);
    try std.testing.expectEqual(@as(u32, 34), routable_summary.target_minor);
    try std.testing.expectEqual(@as(u32, 2), routable_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 1), routable_summary.resolved_index);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 34), routable_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE), routable_summary.granted_mode);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE), routable_summary.available_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE), routable_summary.required_ops);
    try std.testing.expectEqual(@as(u32, 0), routable_summary.missing_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOPS_FLAG_TRUNCATED | abi.CHRDEV_FOPS_FLAG_FOUND | abi.CHRDEV_FOPS_FLAG_HIT | abi.CHRDEV_FOPS_FLAG_PERMITTED | abi.CHRDEV_FOPS_FLAG_ROUTABLE), routable_summary.flags);

    const missing_view = chrdev_fops_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE);
    const missing_summary = chrdev_fops_plan.summarize(missing_view);
    try std.testing.expectEqual(@as(u32, 2), missing_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 1), missing_summary.resolved_index);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 37), missing_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE), missing_summary.required_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), missing_summary.missing_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOPS_FLAG_FOUND | abi.CHRDEV_FOPS_FLAG_HIT | abi.CHRDEV_FOPS_FLAG_PERMITTED | abi.CHRDEV_FOPS_FLAG_MISSING_OPS), missing_summary.flags);
}

test "phase3 chrdev route consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const routable_view = chrdev_route_plan.viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT, 34, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE);
    const routable_summary = chrdev_route_plan.summarize(routable_view);
    try std.testing.expect(chrdev_route_plan.isValid(routable_view));
    try std.testing.expectEqual(@as(u32, 240), routable_summary.major);
    try std.testing.expectEqual(@as(u32, 34), routable_summary.target_minor);
    try std.testing.expectEqual(@as(u32, 2), routable_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 1), routable_summary.resolved_index);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 34), routable_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE), routable_summary.granted_mode);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_OPEN), routable_summary.entry_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE), routable_summary.data_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_RELEASE), routable_summary.exit_ops);
    try std.testing.expectEqual(@as(u32, 0), routable_summary.blocked_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_ROUTE_FLAG_TRUNCATED | abi.CHRDEV_ROUTE_FLAG_FOUND | abi.CHRDEV_ROUTE_FLAG_HIT | abi.CHRDEV_ROUTE_FLAG_PERMITTED | abi.CHRDEV_ROUTE_FLAG_ROUTABLE), routable_summary.flags);

    const blocked_view = chrdev_route_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE);
    const blocked_summary = chrdev_route_plan.summarize(blocked_view);
    try std.testing.expectEqual(@as(u32, 2), blocked_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 1), blocked_summary.resolved_index);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 37), blocked_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_OPEN), blocked_summary.entry_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE), blocked_summary.data_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_RELEASE), blocked_summary.exit_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), blocked_summary.blocked_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_ROUTE_FLAG_FOUND | abi.CHRDEV_ROUTE_FLAG_HIT | abi.CHRDEV_ROUTE_FLAG_PERMITTED | abi.CHRDEV_ROUTE_FLAG_BLOCKED), blocked_summary.flags);
}

test "phase3 chrdev io consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const read_view = chrdev_io_plan.viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT, 34, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 16, 8);
    const read_summary = chrdev_io_plan.summarize(read_view);
    try std.testing.expect(chrdev_io_plan.isValid(read_view));
    try std.testing.expectEqual(@as(u32, 240), read_summary.major);
    try std.testing.expectEqual(@as(u32, 34), read_summary.target_minor);
    try std.testing.expectEqual(@as(u32, 2), read_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 1), read_summary.resolved_index);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 34), read_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE), read_summary.granted_mode);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_OP_READ), read_summary.io_op);
    try std.testing.expectEqual(@as(u32, 16), read_summary.requested_bytes);
    try std.testing.expectEqual(@as(u32, 8), read_summary.chunk_bytes);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_OPEN), read_summary.entry_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), read_summary.data_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_RELEASE), read_summary.exit_ops);
    try std.testing.expectEqual(@as(u32, 0), read_summary.blocked_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_FLAG_TRUNCATED | abi.CHRDEV_IO_FLAG_FOUND | abi.CHRDEV_IO_FLAG_HIT | abi.CHRDEV_IO_FLAG_PERMITTED | abi.CHRDEV_IO_FLAG_ROUTABLE | abi.CHRDEV_IO_FLAG_DISPATCHABLE), read_summary.flags);

    const partial_write_view = chrdev_io_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 12, 32);
    const partial_write_summary = chrdev_io_plan.summarize(partial_write_view);
    try std.testing.expectEqual(@as(u32, 2), partial_write_summary.selected_count);
    try std.testing.expectEqual(@as(u32, 1), partial_write_summary.resolved_index);
    try std.testing.expectEqual(dev_region_plan.mkdev(240, 37), partial_write_summary.resolved_dev);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_OP_WRITE), partial_write_summary.io_op);
    try std.testing.expectEqual(@as(u32, 12), partial_write_summary.chunk_bytes);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_OPEN), partial_write_summary.entry_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_WRITE), partial_write_summary.data_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_RELEASE), partial_write_summary.exit_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), partial_write_summary.blocked_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_FLAG_FOUND | abi.CHRDEV_IO_FLAG_HIT | abi.CHRDEV_IO_FLAG_PERMITTED | abi.CHRDEV_IO_FLAG_ROUTABLE | abi.CHRDEV_IO_FLAG_DISPATCHABLE), partial_write_summary.flags);

    const blocked_read_view = chrdev_io_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 12, 32);
    const blocked_read_summary = chrdev_io_plan.summarize(blocked_read_view);
    try std.testing.expectEqual(@as(u32, 0), blocked_read_summary.chunk_bytes);
    try std.testing.expectEqual(@as(u32, 0), blocked_read_summary.entry_ops);
    try std.testing.expectEqual(@as(u32, 0), blocked_read_summary.data_ops);
    try std.testing.expectEqual(@as(u32, 0), blocked_read_summary.exit_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), blocked_read_summary.blocked_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_IO_FLAG_FOUND | abi.CHRDEV_IO_FLAG_HIT | abi.CHRDEV_IO_FLAG_PERMITTED | abi.CHRDEV_IO_FLAG_BLOCKED), blocked_read_summary.flags);
}

test "phase3 chrdev xfer consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const continuable_view = chrdev_xfer_plan.viewFromBits(words[0..], 240, 32, 8, 6, 2, abi.IDA_POLICY_FIRST_FIT, 34, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 16, 8, 4096, 0, 1);
    const continuable_summary = chrdev_xfer_plan.summarize(continuable_view);
    try std.testing.expect(chrdev_xfer_plan.isValid(continuable_view));
    try std.testing.expectEqual(@as(u32, 240), continuable_summary.major);
    try std.testing.expectEqual(@as(u32, 34), continuable_summary.target_minor);
    try std.testing.expectEqual(@as(u32, 1), continuable_summary.segment_count);
    try std.testing.expectEqual(@as(u32, 8), continuable_summary.first_chunk_bytes);
    try std.testing.expectEqual(@as(u32, 8), continuable_summary.final_chunk_bytes);
    try std.testing.expectEqual(@as(u32, 8), continuable_summary.issued_bytes);
    try std.testing.expectEqual(@as(u32, 8), continuable_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u64, 4096), continuable_summary.start_offset);
    try std.testing.expectEqual(@as(u64, 4104), continuable_summary.next_offset);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_XFER_FLAG_TRUNCATED | abi.CHRDEV_XFER_FLAG_FOUND | abi.CHRDEV_XFER_FLAG_HIT | abi.CHRDEV_XFER_FLAG_PERMITTED | abi.CHRDEV_XFER_FLAG_ROUTABLE | abi.CHRDEV_XFER_FLAG_DISPATCHABLE | abi.CHRDEV_XFER_FLAG_CONTINUABLE), continuable_summary.flags);

    const complete_view = chrdev_xfer_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 3);
    const complete_summary = chrdev_xfer_plan.summarize(complete_view);
    try std.testing.expectEqual(@as(u32, 2), complete_summary.segment_count);
    try std.testing.expectEqual(@as(u32, 16), complete_summary.issued_bytes);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), complete_summary.blocked_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_XFER_FLAG_FOUND | abi.CHRDEV_XFER_FLAG_HIT | abi.CHRDEV_XFER_FLAG_PERMITTED | abi.CHRDEV_XFER_FLAG_ROUTABLE | abi.CHRDEV_XFER_FLAG_DISPATCHABLE | abi.CHRDEV_XFER_FLAG_RESUMED | abi.CHRDEV_XFER_FLAG_COMPLETES), complete_summary.flags);

    const blocked_view = chrdev_xfer_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 12, 32, 2048, 4, 2);
    const blocked_summary = chrdev_xfer_plan.summarize(blocked_view);
    try std.testing.expectEqual(@as(u32, 0), blocked_summary.segment_count);
    try std.testing.expectEqual(@as(u32, 8), blocked_summary.requested_remaining);
    try std.testing.expectEqual(@as(u32, 8), blocked_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u64, 2052), blocked_summary.start_offset);
    try std.testing.expectEqual(@as(u64, 2052), blocked_summary.next_offset);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), blocked_summary.blocked_ops);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_XFER_FLAG_FOUND | abi.CHRDEV_XFER_FLAG_HIT | abi.CHRDEV_XFER_FLAG_PERMITTED | abi.CHRDEV_XFER_FLAG_BLOCKED | abi.CHRDEV_XFER_FLAG_RESUMED), blocked_summary.flags);
}

test "phase3 chrdev resume consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const complete_view = chrdev_resume_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3);
    const complete_summary = chrdev_resume_plan.summarize(complete_view);
    try std.testing.expect(chrdev_resume_plan.isValid(complete_view));
    try std.testing.expectEqual(@as(u32, 2), complete_summary.pass_count);
    try std.testing.expectEqual(@as(u32, 16), complete_summary.issued_bytes);
    try std.testing.expectEqual(@as(u32, 20), complete_summary.final_bytes_completed);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u64, 1028), complete_summary.start_offset);
    try std.testing.expectEqual(@as(u64, 1044), complete_summary.next_offset);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_RESUME_FLAG_FOUND | abi.CHRDEV_RESUME_FLAG_HIT | abi.CHRDEV_RESUME_FLAG_PERMITTED | abi.CHRDEV_RESUME_FLAG_ROUTABLE | abi.CHRDEV_RESUME_FLAG_DISPATCHABLE | abi.CHRDEV_RESUME_FLAG_RESUMED | abi.CHRDEV_RESUME_FLAG_CONTINUABLE | abi.CHRDEV_RESUME_FLAG_COMPLETES | abi.CHRDEV_RESUME_FLAG_PROGRESSED | abi.CHRDEV_RESUME_FLAG_COMPLETE_OK), complete_summary.flags);

    const continuable_view = chrdev_resume_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 1);
    const continuable_summary = chrdev_resume_plan.summarize(continuable_view);
    try std.testing.expectEqual(@as(u32, 1), continuable_summary.pass_count);
    try std.testing.expectEqual(@as(u32, 8), continuable_summary.issued_bytes);
    try std.testing.expectEqual(@as(u32, 12), continuable_summary.final_bytes_completed);
    try std.testing.expectEqual(@as(u32, 8), continuable_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_RESUME_FLAG_FOUND | abi.CHRDEV_RESUME_FLAG_HIT | abi.CHRDEV_RESUME_FLAG_PERMITTED | abi.CHRDEV_RESUME_FLAG_ROUTABLE | abi.CHRDEV_RESUME_FLAG_DISPATCHABLE | abi.CHRDEV_RESUME_FLAG_RESUMED | abi.CHRDEV_RESUME_FLAG_CONTINUABLE | abi.CHRDEV_RESUME_FLAG_PROGRESSED), continuable_summary.flags);

    const blocked_view = chrdev_resume_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 12, 32, 2048, 4, 2, 2);
    const blocked_summary = chrdev_resume_plan.summarize(blocked_view);
    try std.testing.expectEqual(@as(u32, 0), blocked_summary.pass_count);
    try std.testing.expectEqual(@as(u32, 8), blocked_summary.remaining_bytes);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_FOP_READ), blocked_summary.blocked_ops);
    try std.testing.expectEqual(@as(u64, 2052), blocked_summary.start_offset);
    try std.testing.expectEqual(@as(u64, 2052), blocked_summary.next_offset);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_RESUME_FLAG_FOUND | abi.CHRDEV_RESUME_FLAG_HIT | abi.CHRDEV_RESUME_FLAG_PERMITTED | abi.CHRDEV_RESUME_FLAG_BLOCKED | abi.CHRDEV_RESUME_FLAG_RESUMED | abi.CHRDEV_RESUME_FLAG_STALLED), blocked_summary.flags);
}
