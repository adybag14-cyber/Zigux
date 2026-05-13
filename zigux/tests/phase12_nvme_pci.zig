const std = @import("std");
const nvme_pci = @import("nvme_pci");

test "phase12 nvme pci queue planner keeps host DMA budget smaller when IO queues use CMB" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);

    const admin = try lab.planAdminQueue(128, 64, false);
    const io = try lab.planIoQueue(128, 64, true);

    try std.testing.expectEqual(@as(u16, 3), admin.required_host_dma_pages);
    try std.testing.expectEqual(@as(u16, 1), io.required_host_dma_pages);
    try std.testing.expect(io.host_dma_bytes < io.queue_memory_bytes);
    try std.testing.expectEqual(@as(u32, 16), io.sq_doorbell_offset);
    try std.testing.expectEqual(@as(u32, 24), io.cq_doorbell_offset);
}

test "phase12 nvme pci prp shape reports multi-page throughput fanout" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 4);
    const shape = try lab.planPrpBufferShape(16384, 512);

    try std.testing.expectEqual(@as(u32, 3584), shape.first_prp_bytes);
    try std.testing.expectEqual(@as(u32, 20480), shape.rounded_span_bytes);
    try std.testing.expectEqual(@as(u16, 5), shape.spanned_pages);
    try std.testing.expectEqual(@as(u16, 4), shape.tail_page_count);
    try std.testing.expect(shape.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 3), shape.prp_list_entries);
}
