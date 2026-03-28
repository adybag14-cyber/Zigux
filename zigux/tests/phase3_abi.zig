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
