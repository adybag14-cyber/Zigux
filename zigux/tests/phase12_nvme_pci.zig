const std = @import("std");
const nvme_pci = @import("nvme_pci");

test "phase12 nvme pci direct replay keeps queue reservation reviewable without shared build wiring" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(32, 64, false);

    const reservation = try lab.reserveIoQueues(6, 4);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", reservation.anchor);
    try std.testing.expectEqual(@as(usize, 6), reservation.requested_io_queues);
    try std.testing.expectEqual(@as(usize, 4), reservation.reserved_io_queues);
    try std.testing.expect(reservation.controller_limited);
    try std.testing.expect(!reservation.planner_limited);
    try std.testing.expectEqual(@as(u16, 1), reservation.first_queue_id);
    try std.testing.expectEqual(@as(u16, 4), reservation.last_queue_id);
}

test "phase12 nvme pci direct replay keeps recovery budgeting and PRP metadata pressure explicit" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    _ = try lab.planAdminQueue(64, 64, false);
    _ = try lab.planIoQueue(64, 64, true);
    _ = try lab.planIoQueue(32, 64, false);

    const metadata = try lab.planPrpMetadataBudget(4096 * 5, 0);
    try std.testing.expect(metadata.uses_prp_list);
    try std.testing.expectEqual(@as(u16, 3), metadata.prp_list_entries);
    try std.testing.expectEqual(@as(u16, 1), metadata.metadata_host_dma_pages);

    _ = lab.beginReset();
    const restore = try lab.recoveryQueueRestoreSummary();
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", restore.anchor);
    try std.testing.expectEqual(@as(u16, 64), restore.admin_queue_depth);
    try std.testing.expectEqual(@as(usize, 2), restore.io_queue_count);
    try std.testing.expectEqual(@as(u32, 4), restore.total_host_dma_pages);
    try std.testing.expect(restore.restores_admin_first);
    try std.testing.expect(restore.restores_io_after_admin);
}
