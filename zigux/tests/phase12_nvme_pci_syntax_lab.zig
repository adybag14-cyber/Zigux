const std = @import("std");
const nvme_pci = @import("nvme_pci");

test "phase12 nvme pci syntax lab keeps bounded queue exports reachable" {
    const descriptor = nvme_pci.NvmePciQueueLab.descriptor();

    _ = nvme_pci.ModuleDescriptor;
    _ = nvme_pci.QueueRole;
    _ = nvme_pci.RecoveryState;
    _ = nvme_pci.SglSupport;
    _ = nvme_pci.DataPointerPlan;
    _ = nvme_pci.QueuePairPlanSummary;
    _ = nvme_pci.IoQueueCountPlanSummary;
    _ = nvme_pci.RecoverySummary;
    _ = nvme_pci.PrpBufferShapeSummary;
    _ = nvme_pci.PrpMetadataPlanSummary;
    _ = nvme_pci.DataPointerStrategySummary;
    _ = nvme_pci.DoorbellWindowSummary;
    _ = nvme_pci.NvmePciQueueLab;

    try std.testing.expectEqualStrings("nvme_pci_queue_lab", descriptor.name);
    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_lab_queue_planner);
    try std.testing.expect(descriptor.provides_queue_count_helper);
    try std.testing.expect(descriptor.provides_prp_shape_helper);
    try std.testing.expect(descriptor.provides_prp_metadata_helper);
    try std.testing.expect(descriptor.provides_pointer_selection_helper);
    try std.testing.expect(descriptor.provides_doorbell_window_helper);
    try std.testing.expect(!descriptor.touches_live_dma);
    try std.testing.expect(!descriptor.touches_pci_probe);
    try std.testing.expect(!descriptor.touches_irq_recovery);
}

test "phase12 nvme pci syntax lab keeps review constants and enums stable" {
    try std.testing.expectEqual(@as(u16, 16), nvme_pci.completion_entry_bytes);
    try std.testing.expectEqual(@as(u32, 4096), nvme_pci.min_page_size);
    try std.testing.expectEqual(@as(u16, 2), nvme_pci.min_queue_depth);
    try std.testing.expectEqual(@as(u16, 4095), nvme_pci.max_queue_depth);
    try std.testing.expectEqual(@as(u16, 16), nvme_pci.min_sq_entry_bytes);
    try std.testing.expectEqual(@as(u16, 128), nvme_pci.max_sq_entry_bytes);
    try std.testing.expectEqual(@as(u16, 0), nvme_pci.admin_queue_id);
    try std.testing.expectEqual(@as(usize, 64), nvme_pci.max_planned_io_queues);
    try std.testing.expectEqual(@as(u32, 8), nvme_pci.prp_list_entry_bytes);

    try std.testing.expectEqual(nvme_pci.QueueRole.admin, nvme_pci.QueueRole.admin);
    try std.testing.expectEqual(nvme_pci.QueueRole.io, nvme_pci.QueueRole.io);
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, nvme_pci.RecoveryState.running);
    try std.testing.expectEqual(
        nvme_pci.RecoveryState.reset_frozen,
        nvme_pci.RecoveryState.reset_frozen,
    );
    try std.testing.expectEqual(
        nvme_pci.SglSupport.unavailable,
        nvme_pci.SglSupport.unavailable,
    );
    try std.testing.expectEqual(nvme_pci.SglSupport.optional, nvme_pci.SglSupport.optional);
    try std.testing.expectEqual(nvme_pci.SglSupport.forced, nvme_pci.SglSupport.forced);
    try std.testing.expectEqual(nvme_pci.DataPointerPlan.prp, nvme_pci.DataPointerPlan.prp);
    try std.testing.expectEqual(nvme_pci.DataPointerPlan.sgl, nvme_pci.DataPointerPlan.sgl);
    try std.testing.expectEqual(
        nvme_pci.DataPointerPlan.blocked,
        nvme_pci.DataPointerPlan.blocked,
    );
}

test "phase12 nvme pci syntax lab keeps bounded recovery surface instantiable" {
    var lab = try nvme_pci.NvmePciQueueLab.init(4096, 8);
    const recovery = lab.recoverySummary();

    try std.testing.expectEqualStrings("drivers/nvme/host/pci.c", recovery.anchor);
    try std.testing.expectEqual(nvme_pci.RecoveryState.running, recovery.state);
    try std.testing.expect(!recovery.queues_frozen);
    try std.testing.expectEqual(@as(usize, 0), recovery.planned_io_queues);
    try std.testing.expectEqual(@as(u32, 0), recovery.reset_generation);
    try std.testing.expectEqual(nvme_pci.min_queue_depth, recovery.last_admin_queue_depth);
}
