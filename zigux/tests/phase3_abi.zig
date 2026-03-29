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
const chrdev_retry_plan = @import("chrdev_retry_plan");
const chrdev_requeue_plan = @import("chrdev_requeue_plan");
const chrdev_complete_plan = @import("chrdev_complete_plan");
const chrdev_notify_plan = @import("chrdev_notify_plan");
const chrdev_notify_policy_plan = @import("chrdev_notify_policy_plan");
const chrdev_notify_budget_plan = @import("chrdev_notify_budget_plan");
const chrdev_notify_ack_plan = @import("chrdev_notify_ack_plan");
const chrdev_notify_ack_budget_plan = @import("chrdev_notify_ack_budget_plan");
const chrdev_notify_ack_window_plan = @import("chrdev_notify_ack_window_plan");
const chrdev_notify_ack_window_policy_plan = @import("chrdev_notify_ack_window_policy_plan");
const chrdev_notify_ack_window_policy_budget_plan = @import("chrdev_notify_ack_window_policy_budget_plan");
const chrdev_notify_ack_window_policy_budget_window_plan = @import("chrdev_notify_ack_window_policy_budget_window_plan");
const chrdev_notify_ack_window_policy_budget_window_delivery_plan = @import("chrdev_notify_ack_window_policy_budget_window_delivery_plan");
const chrdev_notify_ack_window_policy_budget_window_delivery_window_plan = @import("chrdev_notify_ack_window_policy_budget_window_delivery_window_plan");
const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan = @import("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_plan");
const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan = @import("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_plan");
const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan = @import("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan");
const chrdev_notify_ack_delivery_budget_guard_plan = @import("chrdev_notify_ack_delivery_budget_guard_plan");
const chrdev_notify_ack_delivery_budget_guard_window_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_plan");
const chrdev_notify_ack_delivery_budget_guard_window_policy_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_plan");
const chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan");
const chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan");
const chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan");
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
        layout_assert.assertSize(abi.ChrdevRetryView, @sizeOf(usize) + 96);
        layout_assert.assertSize(abi.ChrdevRetrySummary, 104);
        layout_assert.assertSize(abi.ChrdevRequeueView, @sizeOf(usize) + 104);
        layout_assert.assertSize(abi.ChrdevRequeueSummary, 128);
        layout_assert.assertSize(abi.ChrdevCompleteView, @sizeOf(usize) + 120);
        layout_assert.assertSize(abi.ChrdevCompleteSummary, 152);
        layout_assert.assertSize(abi.ChrdevNotifyView, @sizeOf(usize) + 136);
        layout_assert.assertSize(abi.ChrdevNotifySummary, 192);
        layout_assert.assertSize(abi.ChrdevNotifyPolicyView, @sizeOf(usize) + 144);
        layout_assert.assertSize(abi.ChrdevNotifyPolicySummary, 232);
        layout_assert.assertSize(abi.ChrdevNotifyBudgetView, @sizeOf(usize) + 152);
        layout_assert.assertSize(abi.ChrdevNotifyBudgetSummary, 272);
        layout_assert.assertSize(abi.ChrdevNotifyAckView, @sizeOf(usize) + 176);
        layout_assert.assertSize(abi.ChrdevNotifyAckSummary, 320);
        layout_assert.assertSize(abi.ChrdevNotifyAckBudgetView, @sizeOf(usize) + 200);
        layout_assert.assertSize(abi.ChrdevNotifyAckBudgetSummary, 408);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowView, @sizeOf(usize) + 208);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowSummary, 448);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyView, @sizeOf(usize) + 216);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicySummary, 496);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetView, @sizeOf(usize) + 224);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, 544);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowView, @sizeOf(usize) + 240);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowSummary, 584);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryView, @sizeOf(usize) + 248);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, 632);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, @sizeOf(usize) + 264);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, @sizeOf(usize) + 272);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowView, @sizeOf(usize) + 288);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryView, @sizeOf(usize) + 296);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, 680);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, 728);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowSummary, 768);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, 816);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowView, 320);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetView, 328);
        layout_assert.assertSize(abi.ChrdevNotifyAckDeliveryBudgetGuardView, 344);
        layout_assert.assertSize(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowView, 360);
        layout_assert.assertSize(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyView, 368);
        layout_assert.assertSize(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetView, 384);
        layout_assert.assertSize(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowView, 400);
        layout_assert.assertSize(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryView, 416);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, 864);
        layout_assert.assertSize(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, 912);
        layout_assert.assertSize(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, 976);
        layout_assert.assertSize(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, 1032);
        layout_assert.assertSize(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary, 1072);
        layout_assert.assertSize(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, 1128);
        layout_assert.assertSize(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, 1176);
        layout_assert.assertSize(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, 1232);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetView, "window_policy_budget_window_delivery_window_budget_window_delivery_window_budget", 316);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetView, "deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget", 320);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetView, "window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_reserved", 324);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_flags", 860);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_before", 864);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after", 868);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, "deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_before", 872);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, "deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after", 876);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status", 880);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_acked_count", 884);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_deferred_count", 888);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_suppressed_count", 892);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_coalesced_count", 896);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dropped_count", 900);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_skipped_count", 904);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardView, "primary_guard_floor", 328);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardView, "deferred_guard_floor", 332);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardView, "reserved", 336);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowView, "primary_window", 344);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowView, "deferred_window", 348);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowView, "window_floor", 352);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowView, "reserved", 356);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyView, "policy_flags", 360);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyView, "reserved", 364);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetView, "primary_budget", 368);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetView, "deferred_budget", 372);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetView, "reserved", 376);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowView, "budget_window", 384);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowView, "budget_window_floor", 388);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowView, "reserved", 392);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryView, "primary_delivery_budget", 400);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryView, "deferred_delivery_budget", 404);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryView, "reserved", 408);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "primary_before", 912);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "primary_after", 916);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "deferred_before", 920);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "deferred_after", 924);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "primary_guard_floor", 928);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "deferred_guard_floor", 932);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "guard_flags", 936);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "guard_status", 940);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "acked_count", 944);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "deferred_count", 948);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "suppressed_count", 952);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "coalesced_count", 956);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "dropped_count", 960);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "skipped_count", 964);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, "held_count", 968);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "primary_window_before", 976);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "primary_window_after", 980);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "deferred_window_before", 984);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "deferred_window_after", 988);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "window_floor", 992);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "window_flags", 996);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "window_status", 1000);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "acked_count", 1004);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "deferred_count", 1008);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "suppressed_count", 1012);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "coalesced_count", 1016);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "dropped_count", 1020);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "skipped_count", 1024);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, "held_count", 1028);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary, "policy_flags", 1032);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary, "effective_policy_flags", 1036);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary, "policy_status", 1040);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary, "acked_count", 1044);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary, "deferred_count", 1048);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary, "suppressed_count", 1052);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary, "coalesced_count", 1056);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary, "dropped_count", 1060);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary, "skipped_count", 1064);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary, "held_count", 1068);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "budget_flags", 1072);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "primary_budget_before", 1076);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "primary_budget_after", 1080);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "deferred_budget_before", 1084);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "deferred_budget_after", 1088);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "budget_status", 1092);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "acked_count", 1096);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "deferred_count", 1100);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "suppressed_count", 1104);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "coalesced_count", 1108);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "dropped_count", 1112);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "skipped_count", 1116);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, "held_count", 1120);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, "budget_window_flags", 1128);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, "budget_window_before", 1132);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, "budget_window_after", 1136);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, "budget_window_floor", 1140);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, "budget_window_status", 1144);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, "acked_count", 1148);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, "deferred_count", 1152);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, "suppressed_count", 1156);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, "coalesced_count", 1160);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, "dropped_count", 1164);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, "skipped_count", 1168);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, "held_count", 1172);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "delivery_flags", 1176);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "primary_delivery_budget_before", 1180);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "primary_delivery_budget_after", 1184);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "deferred_delivery_budget_before", 1188);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "deferred_delivery_budget_after", 1192);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "delivery_status", 1196);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "acked_count", 1200);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "deferred_count", 1204);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "suppressed_count", 1208);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "coalesced_count", 1212);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "dropped_count", 1216);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "skipped_count", 1220);
        layout_assert.assertOffset(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary, "held_count", 1224);
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
        layout_assert.assertOffset(abi.ChrdevRetryView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevRetryView, "file_offset", @sizeOf(usize) + 56);
        layout_assert.assertOffset(abi.ChrdevRetryView, "resume_passes", @sizeOf(usize) + 72);
        layout_assert.assertOffset(abi.ChrdevRetryView, "retry_budget", @sizeOf(usize) + 76);
        layout_assert.assertOffset(abi.ChrdevRetryView, "stall_budget", @sizeOf(usize) + 80);
        layout_assert.assertOffset(abi.ChrdevRetryView, "backoff_quanta", @sizeOf(usize) + 84);
        layout_assert.assertOffset(abi.ChrdevRetryView, "reserved", @sizeOf(usize) + 88);
        layout_assert.assertOffset(abi.ChrdevRetrySummary, "start_offset", 32);
        layout_assert.assertOffset(abi.ChrdevRetrySummary, "next_offset", 40);
        layout_assert.assertOffset(abi.ChrdevRetrySummary, "initial_bytes_completed", 48);
        layout_assert.assertOffset(abi.ChrdevRetrySummary, "pass_count", 56);
        layout_assert.assertOffset(abi.ChrdevRetrySummary, "entry_ops", 68);
        layout_assert.assertOffset(abi.ChrdevRetrySummary, "retry_count", 84);
        layout_assert.assertOffset(abi.ChrdevRetrySummary, "stall_count", 88);
        layout_assert.assertOffset(abi.ChrdevRetrySummary, "remaining_retry_budget", 92);
        layout_assert.assertOffset(abi.ChrdevRetrySummary, "backoff_ticks", 96);
        layout_assert.assertOffset(abi.ChrdevRetrySummary, "flags", 100);
        layout_assert.assertOffset(abi.ChrdevRequeueView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevRequeueView, "file_offset", @sizeOf(usize) + 56);
        layout_assert.assertOffset(abi.ChrdevRequeueView, "resume_passes", @sizeOf(usize) + 72);
        layout_assert.assertOffset(abi.ChrdevRequeueView, "retry_budget", @sizeOf(usize) + 76);
        layout_assert.assertOffset(abi.ChrdevRequeueView, "stall_budget", @sizeOf(usize) + 80);
        layout_assert.assertOffset(abi.ChrdevRequeueView, "backoff_quanta", @sizeOf(usize) + 84);
        layout_assert.assertOffset(abi.ChrdevRequeueView, "queue_depth", @sizeOf(usize) + 88);
        layout_assert.assertOffset(abi.ChrdevRequeueView, "queue_capacity", @sizeOf(usize) + 92);
        layout_assert.assertOffset(abi.ChrdevRequeueView, "requeue_budget", @sizeOf(usize) + 96);
        layout_assert.assertOffset(abi.ChrdevRequeueView, "reserved", @sizeOf(usize) + 100);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "start_offset", 32);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "next_offset", 40);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "initial_bytes_completed", 48);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "pass_count", 56);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "projected_remaining_bytes", 68);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "entry_ops", 72);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "retry_count", 88);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "stall_count", 92);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "requeue_count", 96);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "queue_depth_before", 100);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "queue_depth_after", 104);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "remaining_retry_budget", 108);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "remaining_requeue_budget", 112);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "backoff_ticks", 116);
        layout_assert.assertOffset(abi.ChrdevRequeueSummary, "flags", 120);
        layout_assert.assertOffset(abi.ChrdevCompleteView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevCompleteView, "file_offset", @sizeOf(usize) + 56);
        layout_assert.assertOffset(abi.ChrdevCompleteView, "resume_passes", @sizeOf(usize) + 72);
        layout_assert.assertOffset(abi.ChrdevCompleteView, "retry_budget", @sizeOf(usize) + 76);
        layout_assert.assertOffset(abi.ChrdevCompleteView, "stall_budget", @sizeOf(usize) + 80);
        layout_assert.assertOffset(abi.ChrdevCompleteView, "backoff_quanta", @sizeOf(usize) + 84);
        layout_assert.assertOffset(abi.ChrdevCompleteView, "queue_depth", @sizeOf(usize) + 88);
        layout_assert.assertOffset(abi.ChrdevCompleteView, "queue_capacity", @sizeOf(usize) + 92);
        layout_assert.assertOffset(abi.ChrdevCompleteView, "requeue_budget", @sizeOf(usize) + 96);
        layout_assert.assertOffset(abi.ChrdevCompleteView, "completion_cookie", @sizeOf(usize) + 104);
        layout_assert.assertOffset(abi.ChrdevCompleteView, "completion_budget", @sizeOf(usize) + 112);
        layout_assert.assertOffset(abi.ChrdevCompleteView, "reserved", @sizeOf(usize) + 116);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "start_offset", 32);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "next_offset", 40);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "initial_bytes_completed", 48);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "pass_count", 56);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "projected_remaining_bytes", 68);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "entry_ops", 72);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "retry_count", 88);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "stall_count", 92);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "requeue_count", 96);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "queue_depth_before", 100);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "queue_depth_after", 104);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "remaining_retry_budget", 108);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "remaining_requeue_budget", 112);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "backoff_ticks", 116);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "completion_cookie", 120);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "completion_status", 128);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "completion_count", 132);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "deferred_count", 136);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "failure_count", 140);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "remaining_completion_budget", 144);
        layout_assert.assertOffset(abi.ChrdevCompleteSummary, "flags", 148);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "file_offset", @sizeOf(usize) + 56);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "resume_passes", @sizeOf(usize) + 72);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "retry_budget", @sizeOf(usize) + 76);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "stall_budget", @sizeOf(usize) + 80);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "backoff_quanta", @sizeOf(usize) + 84);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "queue_depth", @sizeOf(usize) + 88);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "queue_capacity", @sizeOf(usize) + 92);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "requeue_budget", @sizeOf(usize) + 96);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "completion_cookie", @sizeOf(usize) + 104);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "completion_budget", @sizeOf(usize) + 112);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "notify_mask", @sizeOf(usize) + 116);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "notify_cookie", @sizeOf(usize) + 120);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "notify_budget", @sizeOf(usize) + 128);
        layout_assert.assertOffset(abi.ChrdevNotifyView, "reserved", @sizeOf(usize) + 132);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "start_offset", 32);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "next_offset", 40);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "initial_bytes_completed", 48);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "pass_count", 56);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "projected_remaining_bytes", 68);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "entry_ops", 72);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "retry_count", 88);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "stall_count", 92);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "requeue_count", 96);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "queue_depth_before", 100);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "queue_depth_after", 104);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "remaining_retry_budget", 108);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "remaining_requeue_budget", 112);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "backoff_ticks", 116);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "completion_cookie", 120);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "completion_status", 128);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "completion_count", 132);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "deferred_count", 136);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "failure_count", 140);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "remaining_completion_budget", 144);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "notify_mask", 148);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "matched_notify_mask", 152);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "notify_status", 156);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "notify_count", 160);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "deferred_notify_count", 164);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "dropped_notify_count", 168);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "remaining_notify_budget", 172);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "notify_cookie", 176);
        layout_assert.assertOffset(abi.ChrdevNotifySummary, "flags", 184);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "file_offset", @sizeOf(usize) + 56);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "resume_passes", @sizeOf(usize) + 72);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "retry_budget", @sizeOf(usize) + 76);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "stall_budget", @sizeOf(usize) + 80);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "backoff_quanta", @sizeOf(usize) + 84);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "queue_depth", @sizeOf(usize) + 88);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "queue_capacity", @sizeOf(usize) + 92);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "requeue_budget", @sizeOf(usize) + 96);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "completion_cookie", @sizeOf(usize) + 104);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "completion_budget", @sizeOf(usize) + 112);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "notify_mask", @sizeOf(usize) + 116);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "notify_cookie", @sizeOf(usize) + 120);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "notify_budget", @sizeOf(usize) + 128);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "reserved", @sizeOf(usize) + 132);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "policy_flags", @sizeOf(usize) + 136);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicyView, "policy_reserved", @sizeOf(usize) + 140);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "start_offset", 32);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "next_offset", 40);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "initial_bytes_completed", 48);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "pass_count", 56);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "projected_remaining_bytes", 68);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "entry_ops", 72);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "retry_count", 88);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "stall_count", 92);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "requeue_count", 96);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "queue_depth_before", 100);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "queue_depth_after", 104);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "remaining_retry_budget", 108);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "remaining_requeue_budget", 112);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "backoff_ticks", 116);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "completion_cookie", 120);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "completion_status", 128);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "completion_count", 132);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "deferred_count", 136);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "failure_count", 140);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "remaining_completion_budget", 144);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "notify_mask", 148);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "matched_notify_mask", 152);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "notify_status", 156);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "notify_count", 160);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "deferred_notify_count", 164);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "dropped_notify_count", 168);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "remaining_notify_budget", 172);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "notify_cookie", 176);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "flags", 184);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "policy_flags", 188);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "effective_policy_flags", 192);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "effective_notify_cookie", 200);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "policy_status", 208);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "policy_notify_count", 212);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "policy_deferred_count", 216);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "policy_suppressed_count", 220);
        layout_assert.assertOffset(abi.ChrdevNotifyPolicySummary, "policy_coalesced_count", 224);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "file_offset", @sizeOf(usize) + 56);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "resume_passes", @sizeOf(usize) + 72);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "retry_budget", @sizeOf(usize) + 76);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "stall_budget", @sizeOf(usize) + 80);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "backoff_quanta", @sizeOf(usize) + 84);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "queue_depth", @sizeOf(usize) + 88);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "queue_capacity", @sizeOf(usize) + 92);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "requeue_budget", @sizeOf(usize) + 96);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "completion_cookie", @sizeOf(usize) + 104);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "completion_budget", @sizeOf(usize) + 112);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "notify_mask", @sizeOf(usize) + 116);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "notify_cookie", @sizeOf(usize) + 120);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "notify_budget", @sizeOf(usize) + 128);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "reserved", @sizeOf(usize) + 132);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "policy_flags", @sizeOf(usize) + 136);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "policy_reserved", @sizeOf(usize) + 140);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "delivery_budget", @sizeOf(usize) + 144);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetView, "deferred_budget", @sizeOf(usize) + 148);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "start_offset", 32);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "next_offset", 40);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "initial_bytes_completed", 48);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "pass_count", 56);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "projected_remaining_bytes", 68);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "entry_ops", 72);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "retry_count", 88);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "stall_count", 92);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "requeue_count", 96);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "queue_depth_before", 100);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "queue_depth_after", 104);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "remaining_retry_budget", 108);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "remaining_requeue_budget", 112);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "backoff_ticks", 116);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "completion_cookie", 120);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "completion_status", 128);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "completion_count", 132);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "deferred_count", 136);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "failure_count", 140);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "remaining_completion_budget", 144);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "notify_mask", 148);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "matched_notify_mask", 152);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "notify_status", 156);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "notify_count", 160);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "deferred_notify_count", 164);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "dropped_notify_count", 168);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "remaining_notify_budget", 172);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "notify_cookie", 176);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "flags", 184);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "policy_flags", 188);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "effective_policy_flags", 192);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "effective_notify_cookie", 200);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "policy_status", 208);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "policy_notify_count", 212);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "policy_deferred_count", 216);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "policy_suppressed_count", 220);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "policy_coalesced_count", 224);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "budget_flags", 228);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "delivery_budget_before", 232);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "delivery_budget_after", 236);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "deferred_budget_before", 240);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "deferred_budget_after", 244);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "budget_status", 248);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "budget_notify_count", 252);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "budget_deferred_count", 256);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "budget_dropped_count", 260);
        layout_assert.assertOffset(abi.ChrdevNotifyBudgetSummary, "budget_suppressed_count", 264);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "file_offset", @sizeOf(usize) + 56);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "resume_passes", @sizeOf(usize) + 72);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "retry_budget", @sizeOf(usize) + 76);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "stall_budget", @sizeOf(usize) + 80);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "backoff_quanta", @sizeOf(usize) + 84);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "queue_depth", @sizeOf(usize) + 88);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "queue_capacity", @sizeOf(usize) + 92);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "requeue_budget", @sizeOf(usize) + 96);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "completion_cookie", @sizeOf(usize) + 104);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "completion_budget", @sizeOf(usize) + 112);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "notify_mask", @sizeOf(usize) + 116);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "notify_cookie", @sizeOf(usize) + 120);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "notify_budget", @sizeOf(usize) + 128);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "reserved", @sizeOf(usize) + 132);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "policy_flags", @sizeOf(usize) + 136);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "policy_reserved", @sizeOf(usize) + 140);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "delivery_budget", @sizeOf(usize) + 144);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "deferred_budget", @sizeOf(usize) + 148);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "ack_mask", @sizeOf(usize) + 152);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "ack_window", @sizeOf(usize) + 156);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "ack_cookie", @sizeOf(usize) + 160);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "ack_observed", @sizeOf(usize) + 168);
        layout_assert.assertOffset(abi.ChrdevNotifyAckView, "ack_reserved", @sizeOf(usize) + 172);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "start_offset", 32);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "next_offset", 40);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "initial_bytes_completed", 48);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "pass_count", 56);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "projected_remaining_bytes", 68);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "entry_ops", 72);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "retry_count", 88);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "stall_count", 92);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "requeue_count", 96);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "queue_depth_before", 100);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "queue_depth_after", 104);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "remaining_retry_budget", 108);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "remaining_requeue_budget", 112);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "backoff_ticks", 116);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "completion_cookie", 120);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "completion_status", 128);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "completion_count", 132);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "deferred_count", 136);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "failure_count", 140);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "remaining_completion_budget", 144);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "notify_mask", 148);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "matched_notify_mask", 152);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "notify_status", 156);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "notify_count", 160);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "deferred_notify_count", 164);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "dropped_notify_count", 168);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "remaining_notify_budget", 172);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "notify_cookie", 176);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "flags", 184);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "policy_flags", 188);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "effective_policy_flags", 192);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "effective_notify_cookie", 200);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "policy_status", 208);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "policy_notify_count", 212);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "policy_deferred_count", 216);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "policy_suppressed_count", 220);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "policy_coalesced_count", 224);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "budget_flags", 228);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "delivery_budget_before", 232);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "delivery_budget_after", 236);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "deferred_budget_before", 240);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "deferred_budget_after", 244);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "budget_status", 248);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "budget_notify_count", 252);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "budget_deferred_count", 256);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "budget_dropped_count", 260);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "budget_suppressed_count", 264);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "ack_mask", 268);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "matched_ack_mask", 272);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "ack_status", 276);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "ack_count", 280);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "deferred_ack_count", 284);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "expired_ack_count", 288);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "skipped_ack_count", 292);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "ack_window_before", 296);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "ack_window_after", 300);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "ack_cookie", 304);
        layout_assert.assertOffset(abi.ChrdevNotifyAckSummary, "ack_flags", 312);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicyView, "available_ops", @sizeOf(usize) + 36);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicyView, "file_offset", @sizeOf(usize) + 56);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicyView, "completion_cookie", @sizeOf(usize) + 104);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicyView, "ack_mask", @sizeOf(usize) + 152);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicyView, "ack_cookie", @sizeOf(usize) + 160);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicyView, "ack_policy_flags", @sizeOf(usize) + 176);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicyView, "ack_policy_reserved", @sizeOf(usize) + 180);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicySummary, "start_offset", 32);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicySummary, "completion_cookie", 120);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicySummary, "ack_cookie", 304);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicySummary, "ack_flags", 312);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicySummary, "ack_policy_flags", 316);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicySummary, "effective_ack_policy_flags", 320);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicySummary, "effective_ack_cookie", 328);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicySummary, "ack_policy_status", 336);
        layout_assert.assertOffset(abi.ChrdevNotifyAckPolicySummary, "policy_skipped_ack_count", 360);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetView, "ack_cookie", @sizeOf(usize) + 160);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetView, "ack_policy_flags", @sizeOf(usize) + 176);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetView, "ack_budget", @sizeOf(usize) + 184);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetView, "deferred_ack_budget", @sizeOf(usize) + 188);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetView, "ack_budget_reserved", @sizeOf(usize) + 192);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowView, "ack_budget", @sizeOf(usize) + 184);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowView, "deferred_ack_budget", @sizeOf(usize) + 188);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowView, "ack_budget_reserved", @sizeOf(usize) + 192);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowView, "window_floor", @sizeOf(usize) + 196);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowView, "window_reserved", @sizeOf(usize) + 200);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyView, "window_floor", @sizeOf(usize) + 196);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyView, "window_reserved", @sizeOf(usize) + 200);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyView, "window_policy_flags", @sizeOf(usize) + 204);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyView, "window_policy_reserved", @sizeOf(usize) + 208);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetView, "window_floor", @sizeOf(usize) + 196);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetView, "window_reserved", @sizeOf(usize) + 200);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetView, "window_policy_flags", @sizeOf(usize) + 204);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetView, "window_policy_reserved", @sizeOf(usize) + 208);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetView, "window_policy_budget", @sizeOf(usize) + 212);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetView, "deferred_window_policy_budget", @sizeOf(usize) + 216);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetView, "window_policy_budget_reserved", @sizeOf(usize) + 220);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowView, "window_policy_budget_window", @sizeOf(usize) + 224);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowView, "window_policy_budget_window_floor", @sizeOf(usize) + 228);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowView, "window_policy_budget_window_reserved", @sizeOf(usize) + 232);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryView, "window_policy_budget_window", @sizeOf(usize) + 224);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryView, "window_policy_budget_window_floor", @sizeOf(usize) + 228);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryView, "window_policy_budget_window_reserved", @sizeOf(usize) + 232);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryView, "window_policy_budget_window_delivery_budget", @sizeOf(usize) + 236);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryView, "deferred_window_policy_budget_window_delivery_budget", @sizeOf(usize) + 240);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryView, "window_policy_budget_window_delivery_reserved", @sizeOf(usize) + 244);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "ack_cookie", 304);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "ack_policy_flags", 316);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "ack_budget_flags", 364);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "ack_budget_before", 368);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "ack_budget_after", 372);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "deferred_ack_budget_before", 376);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "deferred_ack_budget_after", 380);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "ack_budget_status", 384);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "budget_acked_count", 388);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "budget_deferred_ack_count", 392);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "budget_dropped_ack_count", 396);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "budget_suppressed_ack_count", 400);
        layout_assert.assertOffset(abi.ChrdevNotifyAckBudgetSummary, "budget_skipped_ack_count", 404);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "ack_budget_flags", 364);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "ack_budget_before", 368);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "ack_budget_after", 372);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "deferred_ack_budget_before", 376);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "deferred_ack_budget_after", 380);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "ack_budget_status", 384);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "budget_acked_count", 388);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "budget_deferred_ack_count", 392);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "budget_dropped_ack_count", 396);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "budget_suppressed_ack_count", 400);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "budget_skipped_ack_count", 404);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "window_flags", 408);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "window_before", 412);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "window_after", 416);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "window_floor", 420);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "window_status", 424);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "window_acked_count", 428);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "window_deferred_count", 432);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "window_dropped_count", 436);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "window_suppressed_count", 440);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowSummary, "window_skipped_count", 444);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "window_flags", 408);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "window_before", 412);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "window_after", 416);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "window_floor", 420);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "window_status", 424);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "window_acked_count", 428);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "window_deferred_count", 432);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "window_dropped_count", 436);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "window_suppressed_count", 440);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "window_skipped_count", 444);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "window_policy_flags", 448);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "effective_window_policy_flags", 452);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "effective_window_cookie", 456);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "window_policy_status", 464);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "policy_window_acked_count", 468);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "policy_window_deferred_count", 472);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "policy_window_suppressed_count", 476);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "policy_window_coalesced_count", 480);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "policy_window_dropped_count", 484);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicySummary, "policy_window_skipped_count", 488);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_flags", 408);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_before", 412);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_after", 416);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_floor", 420);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_status", 424);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_acked_count", 428);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_deferred_count", 432);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_dropped_count", 436);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_suppressed_count", 440);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_skipped_count", 444);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_policy_flags", 448);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "effective_window_policy_flags", 452);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "effective_window_cookie", 456);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_policy_status", 464);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "policy_window_acked_count", 468);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "policy_window_deferred_count", 472);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "policy_window_suppressed_count", 476);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "policy_window_coalesced_count", 480);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "policy_window_dropped_count", 484);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "policy_window_skipped_count", 488);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_policy_budget_flags", 492);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_policy_budget_before", 496);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_policy_budget_after", 500);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "deferred_window_policy_budget_before", 504);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "deferred_window_policy_budget_after", 508);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "window_policy_budget_status", 512);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "budget_window_acked_count", 516);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "budget_window_deferred_count", 520);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "budget_window_suppressed_count", 524);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "budget_window_coalesced_count", 528);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "budget_window_dropped_count", 532);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetSummary, "budget_window_skipped_count", 536);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowSummary, "window_policy_budget_window_flags", 540);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowSummary, "window_policy_budget_window_before", 544);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowSummary, "window_policy_budget_window_after", 548);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowSummary, "window_policy_budget_window_floor", 552);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowSummary, "window_policy_budget_window_status", 556);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowSummary, "window_policy_budget_window_acked_count", 560);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowSummary, "window_policy_budget_window_deferred_count", 564);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowSummary, "window_policy_budget_window_suppressed_count", 568);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowSummary, "window_policy_budget_window_coalesced_count", 572);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowSummary, "window_policy_budget_window_dropped_count", 576);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowSummary, "window_policy_budget_window_skipped_count", 580);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_flags", 540);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_before", 544);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_after", 548);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_floor", 552);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_status", 556);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_acked_count", 560);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_deferred_count", 564);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_suppressed_count", 568);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_coalesced_count", 572);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_dropped_count", 576);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_skipped_count", 580);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_flags", 584);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_before", 588);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_after", 592);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "deferred_window_policy_budget_window_delivery_before", 596);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "deferred_window_policy_budget_window_delivery_after", 600);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_status", 604);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_acked_count", 608);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_deferred_count", 612);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_suppressed_count", 616);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_coalesced_count", 620);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_dropped_count", 624);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_skipped_count", 628);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "window_policy_budget_window", @sizeOf(usize) + 224);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "window_policy_budget_window_floor", @sizeOf(usize) + 228);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "window_policy_budget_window_reserved", @sizeOf(usize) + 232);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "window_policy_budget_window_delivery_budget", @sizeOf(usize) + 236);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "deferred_window_policy_budget_window_delivery_budget", @sizeOf(usize) + 240);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "window_policy_budget_window_delivery_reserved", @sizeOf(usize) + 244);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "window_policy_budget_window_delivery_window", @sizeOf(usize) + 248);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "window_policy_budget_window_delivery_window_floor", @sizeOf(usize) + 252);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "window_policy_budget_window_delivery_window_reserved", @sizeOf(usize) + 256);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window_policy_budget_window_delivery_window", @sizeOf(usize) + 248);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window_policy_budget_window_delivery_window_floor", @sizeOf(usize) + 252);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window_policy_budget_window_delivery_window_reserved", @sizeOf(usize) + 256);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window_policy_budget_window_delivery_window_budget", @sizeOf(usize) + 260);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "deferred_window_policy_budget_window_delivery_window_budget", @sizeOf(usize) + 264);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window_policy_budget_window_delivery_window_budget_reserved", @sizeOf(usize) + 268);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowView, "window_policy_budget_window_delivery_window_budget_window", @sizeOf(usize) + 272);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowView, "window_policy_budget_window_delivery_window_budget_window_floor", @sizeOf(usize) + 276);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowView, "window_policy_budget_window_delivery_window_budget_window_reserved", @sizeOf(usize) + 280);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryView, "window_policy_budget_window_delivery_window_budget_window_delivery_budget", @sizeOf(usize) + 284);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryView, "deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget", @sizeOf(usize) + 288);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryView, "window_policy_budget_window_delivery_window_budget_window_delivery_reserved", @sizeOf(usize) + 292);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowView, "window_policy_budget_window_delivery_window_budget_window_delivery_window", 304);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowView, "window_policy_budget_window_delivery_window_budget_window_delivery_window_floor", 308);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowView, "window_policy_budget_window_delivery_window_budget_window_delivery_window_reserved", 312);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_flags", 540);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_before", 544);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_after", 548);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_floor", 552);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_status", 556);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_acked_count", 560);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_deferred_count", 564);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_suppressed_count", 568);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_coalesced_count", 572);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_dropped_count", 576);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_skipped_count", 580);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_flags", 584);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_before", 588);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_after", 592);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "deferred_window_policy_budget_window_delivery_before", 596);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "deferred_window_policy_budget_window_delivery_after", 600);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_status", 604);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_acked_count", 608);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_deferred_count", 612);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_suppressed_count", 616);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_coalesced_count", 620);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_dropped_count", 624);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_skipped_count", 628);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_flags", 632);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_before", 636);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_after", 640);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_floor", 644);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_status", 648);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_acked_count", 652);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_deferred_count", 656);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_suppressed_count", 660);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_coalesced_count", 664);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_dropped_count", 668);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_skipped_count", 672);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_flags", 676);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_before", 680);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_after", 684);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "deferred_window_policy_budget_window_delivery_window_budget_before", 688);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "deferred_window_policy_budget_window_delivery_window_budget_after", 692);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_status", 696);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_acked_count", 700);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_deferred_count", 704);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_suppressed_count", 708);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_coalesced_count", 712);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_dropped_count", 716);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "window_policy_budget_window_delivery_window_budget_skipped_count", 720);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowSummary, "window_policy_budget_window_delivery_window_budget_window_flags", 724);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowSummary, "window_policy_budget_window_delivery_window_budget_window_before", 728);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowSummary, "window_policy_budget_window_delivery_window_budget_window_after", 732);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowSummary, "window_policy_budget_window_delivery_window_budget_window_floor", 736);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowSummary, "window_policy_budget_window_delivery_window_budget_window_status", 740);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowSummary, "window_policy_budget_window_delivery_window_budget_window_acked_count", 744);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowSummary, "window_policy_budget_window_delivery_window_budget_window_deferred_count", 748);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowSummary, "window_policy_budget_window_delivery_window_budget_window_suppressed_count", 752);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowSummary, "window_policy_budget_window_delivery_window_budget_window_coalesced_count", 756);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowSummary, "window_policy_budget_window_delivery_window_budget_window_dropped_count", 760);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowSummary, "window_policy_budget_window_delivery_window_budget_window_skipped_count", 764);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_window_budget_window_delivery_flags", 768);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_window_budget_window_delivery_before", 772);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_window_budget_window_delivery_after", 776);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, "deferred_window_policy_budget_window_delivery_window_budget_window_delivery_before", 780);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, "deferred_window_policy_budget_window_delivery_window_budget_window_delivery_after", 784);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_window_budget_window_delivery_status", 788);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_window_budget_window_delivery_acked_count", 792);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_window_budget_window_delivery_deferred_count", 796);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_window_budget_window_delivery_suppressed_count", 800);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_window_budget_window_delivery_coalesced_count", 804);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_window_budget_window_delivery_dropped_count", 808);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, "window_policy_budget_window_delivery_window_budget_window_delivery_skipped_count", 812);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_flags", 816);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_before", 820);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_after", 824);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_floor", 828);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_status", 832);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_acked_count", 836);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_deferred_count", 840);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_suppressed_count", 844);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_coalesced_count", 848);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_dropped_count", 852);
        layout_assert.assertOffset(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowSummary, "window_policy_budget_window_delivery_window_budget_window_delivery_window_skipped_count", 856);
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

test "phase3 chrdev retry consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};

    const complete_view = chrdev_retry_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5);
    const complete_summary = chrdev_retry_plan.summarize(complete_view);
    try std.testing.expect(chrdev_retry_plan.isValid(complete_view));
    try std.testing.expectEqual(@as(u32, 0), complete_summary.retry_count);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.stall_count);
    try std.testing.expectEqual(@as(u32, 2), complete_summary.remaining_retry_budget);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.backoff_ticks);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_RETRY_FLAG_COMPLETE_OK) != 0);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRY_PLANNED) == 0);

    const continuable_view = chrdev_retry_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 1, 2, 1, 0);
    const continuable_summary = chrdev_retry_plan.summarize(continuable_view);
    try std.testing.expectEqual(@as(u32, 1), continuable_summary.retry_count);
    try std.testing.expectEqual(@as(u32, 1), continuable_summary.remaining_retry_budget);
    try std.testing.expect((continuable_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRYABLE) != 0);
    try std.testing.expect((continuable_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRY_PLANNED) != 0);
    try std.testing.expect((continuable_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED) == 0);

    const stalled_view = chrdev_retry_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 12, 32, 2048, 4, 2, 3, 2, 1, 5);
    const stalled_summary = chrdev_retry_plan.summarize(stalled_view);
    try std.testing.expectEqual(@as(u32, 1), stalled_summary.retry_count);
    try std.testing.expectEqual(@as(u32, 1), stalled_summary.stall_count);
    try std.testing.expectEqual(@as(u32, 1), stalled_summary.remaining_retry_budget);
    try std.testing.expectEqual(@as(u32, 5), stalled_summary.backoff_ticks);
    try std.testing.expect((stalled_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRYABLE) != 0);
    try std.testing.expect((stalled_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRY_PLANNED) != 0);
    try std.testing.expect((stalled_summary.flags & abi.CHRDEV_RETRY_FLAG_BACKOFF_APPLIED) != 0);

    const denied_view = chrdev_retry_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 12, 8, 512, 0, 2, 2, 2, 1, 5);
    const denied_summary = chrdev_retry_plan.summarize(denied_view);
    try std.testing.expectEqual(@as(u32, 0), denied_summary.retry_count);
    try std.testing.expectEqual(@as(u32, 1), denied_summary.stall_count);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_RETRY_FLAG_DENIED) != 0);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_RETRY_FLAG_FAILS) != 0);

    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};
    const exhausted_view = chrdev_retry_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5);
    const exhausted_summary = chrdev_retry_plan.summarize(exhausted_view);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.retry_count);
    try std.testing.expectEqual(@as(u32, 0), exhausted_summary.remaining_retry_budget);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_RETRY_FLAG_EXHAUSTED) != 0);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED) != 0);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_RETRY_FLAG_FAILS) != 0);
}

test "phase3 chrdev requeue consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const complete_view = chrdev_requeue_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2);
    const complete_summary = chrdev_requeue_plan.summarize(complete_view);
    try std.testing.expect(chrdev_requeue_plan.isValid(complete_view));
    try std.testing.expectEqual(@as(u32, 0), complete_summary.projected_remaining_bytes);
    try std.testing.expectEqual(@as(u32, 0), complete_summary.requeue_count);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_REQUEUE_FLAG_COMPLETE) != 0);

    const planned_view = chrdev_requeue_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0, 1, 4, 2);
    const planned_summary = chrdev_requeue_plan.summarize(planned_view);
    try std.testing.expectEqual(@as(u32, 16), planned_summary.projected_remaining_bytes);
    try std.testing.expectEqual(@as(u32, 1), planned_summary.requeue_count);
    try std.testing.expectEqual(@as(u32, 2), planned_summary.queue_depth_after);
    try std.testing.expect((planned_summary.flags & abi.CHRDEV_REQUEUE_FLAG_REQUEUE_PLANNED) != 0);

    const delayed_view = chrdev_requeue_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 12, 32, 2048, 4, 2, 3, 2, 1, 5, 2, 4, 3);
    const delayed_summary = chrdev_requeue_plan.summarize(delayed_view);
    try std.testing.expectEqual(@as(u32, 8), delayed_summary.projected_remaining_bytes);
    try std.testing.expect((delayed_summary.flags & abi.CHRDEV_REQUEUE_FLAG_DELAYED) != 0);

    const saturated_view = chrdev_requeue_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0, 4, 4, 2);
    const saturated_summary = chrdev_requeue_plan.summarize(saturated_view);
    try std.testing.expectEqual(@as(u32, 0), saturated_summary.requeue_count);
    try std.testing.expect((saturated_summary.flags & abi.CHRDEV_REQUEUE_FLAG_SATURATED) != 0);
    try std.testing.expect((saturated_summary.flags & abi.CHRDEV_REQUEUE_FLAG_DROPPED) != 0);

    const denied_view = chrdev_requeue_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 12, 8, 512, 0, 2, 2, 2, 1, 5, 1, 4, 2);
    const denied_summary = chrdev_requeue_plan.summarize(denied_view);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_REQUEUE_FLAG_DENIED) != 0);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_REQUEUE_FLAG_DROPPED) != 0);

    const exhausted_view = chrdev_requeue_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2);
    const exhausted_summary = chrdev_requeue_plan.summarize(exhausted_view);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_REQUEUE_FLAG_EXHAUSTED) != 0);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_REQUEUE_FLAG_DROPPED) != 0);
}

test "phase3 chrdev complete consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const complete_view = chrdev_complete_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1);
    const complete_summary = chrdev_complete_plan.summarize(complete_view);
    try std.testing.expect(chrdev_complete_plan.isValid(complete_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_COMPLETE_STATUS_OK), complete_summary.completion_status);
    try std.testing.expectEqual(@as(u32, 1), complete_summary.completion_count);
    try std.testing.expectEqual(@as(u64, 0x1111), complete_summary.completion_cookie);
    try std.testing.expect((complete_summary.flags & abi.CHRDEV_COMPLETE_FLAG_COMPLETION_PLANNED) != 0);

    const planned_view = chrdev_complete_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0, 1, 4, 2, 0x3333, 1);
    const planned_summary = chrdev_complete_plan.summarize(planned_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_COMPLETE_STATUS_DEFERRED), planned_summary.completion_status);
    try std.testing.expectEqual(@as(u32, 1), planned_summary.deferred_count);
    try std.testing.expect((planned_summary.flags & abi.CHRDEV_COMPLETE_FLAG_REQUEUE_PLANNED) != 0);
    try std.testing.expect((planned_summary.flags & abi.CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION) != 0);

    const delayed_view = chrdev_complete_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_READ, 12, 32, 2048, 4, 2, 3, 2, 1, 5, 2, 4, 3, 0x4444, 2);
    const delayed_summary = chrdev_complete_plan.summarize(delayed_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_COMPLETE_STATUS_DEFERRED), delayed_summary.completion_status);
    try std.testing.expect((delayed_summary.flags & abi.CHRDEV_COMPLETE_FLAG_DELAYED) != 0);

    const saturated_view = chrdev_complete_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0, 4, 4, 2, 0x5555, 1);
    const saturated_summary = chrdev_complete_plan.summarize(saturated_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_COMPLETE_STATUS_FAILED), saturated_summary.completion_status);
    try std.testing.expectEqual(@as(u32, 1), saturated_summary.failure_count);
    try std.testing.expect((saturated_summary.flags & abi.CHRDEV_COMPLETE_FLAG_FAILURE_COMPLETION) != 0);

    const denied_view = chrdev_complete_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 12, 8, 512, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x6666, 1);
    const denied_summary = chrdev_complete_plan.summarize(denied_view);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_COMPLETE_FLAG_DENIED) != 0);
    try std.testing.expect((denied_summary.flags & abi.CHRDEV_COMPLETE_FLAG_FAILURE_COMPLETION) != 0);

    const exhausted_view = chrdev_complete_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0);
    const exhausted_summary = chrdev_complete_plan.summarize(exhausted_view);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_COMPLETE_FLAG_EXHAUSTED) != 0);
    try std.testing.expect((exhausted_summary.flags & abi.CHRDEV_COMPLETE_FLAG_FAILURE_COMPLETION) != 0);
}

test "phase3 chrdev notify consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const delivered_view = chrdev_notify_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA);
    const delivered_summary = chrdev_notify_plan.summarize(delivered_view);
    try std.testing.expect(chrdev_notify_plan.isValid(delivered_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_STATUS_DELIVERED), delivered_summary.notify_status);
    try std.testing.expectEqual(@as(u32, 1), delivered_summary.notify_count);
    try std.testing.expectEqual(@as(u64, 0xAAAA), delivered_summary.notify_cookie);
    try std.testing.expect((delivered_summary.flags & abi.CHRDEV_NOTIFY_FLAG_MATCHED_NOTIFY) != 0);
    try std.testing.expect((delivered_summary.flags & abi.CHRDEV_NOTIFY_FLAG_NOTIFY_PLANNED) != 0);

    const deferred_view = chrdev_notify_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0, 1, 4, 2, 0x3333, 1, abi.CHRDEV_NOTIFY_MASK_DEFERRED, 0, 0xBBBB);
    const deferred_summary = chrdev_notify_plan.summarize(deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_STATUS_DEFERRED), deferred_summary.notify_status);
    try std.testing.expectEqual(@as(u32, 1), deferred_summary.deferred_notify_count);
    try std.testing.expect((deferred_summary.flags & abi.CHRDEV_NOTIFY_FLAG_MATCHED_NOTIFY) != 0);

    const failed_view = chrdev_notify_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xCCCC);
    const failed_summary = chrdev_notify_plan.summarize(failed_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_STATUS_DELIVERED), failed_summary.notify_status);
    try std.testing.expectEqual(@as(u32, 1), failed_summary.notify_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_MASK_FAILURE), failed_summary.matched_notify_mask);

    const unmatched_view = chrdev_notify_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xDDDD);
    const unmatched_summary = chrdev_notify_plan.summarize(unmatched_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_STATUS_NONE), unmatched_summary.notify_status);
    try std.testing.expectEqual(@as(u32, 0), unmatched_summary.matched_notify_mask);
}

test "phase3 chrdev notify policy consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const delivered_view = chrdev_notify_policy_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0);
    const delivered_summary = chrdev_notify_policy_plan.summarize(delivered_view);
    try std.testing.expect(chrdev_notify_policy_plan.isValid(delivered_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_STATUS_DELIVERED), delivered_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), delivered_summary.policy_notify_count);
    try std.testing.expectEqual(@as(u32, 0), delivered_summary.effective_policy_flags);
    try std.testing.expectEqual(@as(u64, 0xAAAA), delivered_summary.effective_notify_cookie);

    const force_deferred_view = chrdev_notify_policy_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, abi.CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED);
    const force_deferred_summary = chrdev_notify_policy_plan.summarize(force_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_STATUS_DEFERRED), force_deferred_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), force_deferred_summary.policy_deferred_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED), force_deferred_summary.effective_policy_flags);

    const suppress_failure_view = chrdev_notify_policy_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xCCCC, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE);
    const suppress_failure_summary = chrdev_notify_policy_plan.summarize(suppress_failure_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED), suppress_failure_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), suppress_failure_summary.policy_suppressed_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE), suppress_failure_summary.effective_policy_flags);

    const coalesced_view = chrdev_notify_policy_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xDEAD, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDEAD, abi.CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE);
    const coalesced_summary = chrdev_notify_policy_plan.summarize(coalesced_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_STATUS_COALESCED), coalesced_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), coalesced_summary.policy_coalesced_count);
    try std.testing.expectEqual(@as(u64, 0xDEAD), coalesced_summary.effective_notify_cookie);

    const dropped_view = chrdev_notify_policy_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 0, 0xEEEE, 0);
    const dropped_summary = chrdev_notify_policy_plan.summarize(dropped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED), dropped_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), dropped_summary.policy_suppressed_count);
}

test "phase3 chrdev notify budget consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const issued_view = chrdev_notify_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0);
    const issued_summary = chrdev_notify_budget_plan.summarize(issued_view);
    try std.testing.expect(chrdev_notify_budget_plan.isValid(issued_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_BUDGET_STATUS_ISSUED), issued_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 1), issued_summary.budget_notify_count);
    try std.testing.expectEqual(@as(u32, 0), issued_summary.delivery_budget_after);

    const fallback_deferred_view = chrdev_notify_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, 0, 0, 1);
    const fallback_deferred_summary = chrdev_notify_budget_plan.summarize(fallback_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_BUDGET_STATUS_DEFERRED), fallback_deferred_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 1), fallback_deferred_summary.budget_deferred_count);
    try std.testing.expectEqual(@as(u32, 0), fallback_deferred_summary.deferred_budget_after);

    const dropped_view = chrdev_notify_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xCCCC, 0, 0, 0);
    const dropped_summary = chrdev_notify_budget_plan.summarize(dropped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_BUDGET_STATUS_DROPPED), dropped_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 1), dropped_summary.budget_dropped_count);

    const suppressed_view = chrdev_notify_budget_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xDDDD, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4);
    const suppressed_summary = chrdev_notify_budget_plan.summarize(suppressed_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_BUDGET_STATUS_SUPPRESSED), suppressed_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 1), suppressed_summary.budget_suppressed_count);
}

test "phase3 chrdev notify ack consumer stays aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_view = chrdev_notify_ack_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1);
    const acked_summary = chrdev_notify_ack_plan.summarize(acked_view);
    try std.testing.expect(chrdev_notify_ack_plan.isValid(acked_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_STATUS_ACKED), acked_summary.ack_status);
    try std.testing.expectEqual(@as(u32, 1), acked_summary.ack_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED), acked_summary.matched_ack_mask);
    try std.testing.expectEqual(@as(u32, 2), acked_summary.ack_window_after);
    try std.testing.expect((acked_summary.ack_flags & abi.CHRDEV_NOTIFY_ACK_FLAG_ACKED) != 0);

    const deferred_view = chrdev_notify_ack_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, abi.CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED, 0, 1, abi.CHRDEV_NOTIFY_ACK_MASK_DEFERRED, 2, 0xB2B2, 0);
    const deferred_summary = chrdev_notify_ack_plan.summarize(deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_STATUS_DEFERRED), deferred_summary.ack_status);
    try std.testing.expectEqual(@as(u32, 1), deferred_summary.deferred_ack_count);
    try std.testing.expectEqual(@as(u32, 1), deferred_summary.ack_window_after);
    try std.testing.expect((deferred_summary.ack_flags & abi.CHRDEV_NOTIFY_ACK_FLAG_WINDOW_USED) != 0);

    const expired_view = chrdev_notify_ack_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xCCCC, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xC3C3, 0);
    const expired_summary = chrdev_notify_ack_plan.summarize(expired_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_STATUS_EXPIRED), expired_summary.ack_status);
    try std.testing.expectEqual(@as(u32, 1), expired_summary.expired_ack_count);
    try std.testing.expect((expired_summary.ack_flags & abi.CHRDEV_NOTIFY_ACK_FLAG_WINDOW_EXHAUSTED) != 0);

    const skipped_view = chrdev_notify_ack_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xDDDD, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xD4D4, 0);
    const skipped_summary = chrdev_notify_ack_plan.summarize(skipped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_STATUS_SKIPPED), skipped_summary.ack_status);
    try std.testing.expectEqual(@as(u32, 1), skipped_summary.skipped_ack_count);
    try std.testing.expectEqual(@as(u32, 0), skipped_summary.matched_ack_mask);
    try std.testing.expect((skipped_summary.ack_flags & abi.CHRDEV_NOTIFY_ACK_FLAG_SKIPPED) != 0);

    const unmatched_view = chrdev_notify_ack_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xEEEE, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_DEFERRED, 2, 0xE5E5, 0);
    const unmatched_summary = chrdev_notify_ack_plan.summarize(unmatched_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_STATUS_SKIPPED), unmatched_summary.ack_status);
    try std.testing.expectEqual(@as(u32, 0), unmatched_summary.matched_ack_mask);
    try std.testing.expect((unmatched_summary.ack_flags & abi.CHRDEV_NOTIFY_ACK_FLAG_SKIPPED) != 0);

    const empty_view = abi.ChrdevNotifyAckView{
        .bits_addr = 0, .major = 240, .first_minor = 0, .minor_count = 0, .max_scan = 0, .request_count = 2,
        .policy = abi.IDA_POLICY_FIRST_FIT, .target_minor = 0, .requested_mode = abi.CHRDEV_MODE_READ, .supported_mode = abi.CHRDEV_MODE_READ,
        .available_ops = abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, .io_op = abi.CHRDEV_IO_OP_READ,
        .requested_bytes = 8, .max_chunk_bytes = 8, .file_offset = 0, .bytes_completed = 0, .max_segments = 1, .resume_passes = 2,
        .retry_budget = 1, .stall_budget = 1, .backoff_quanta = 5, .queue_depth = 0, .queue_capacity = 2, .requeue_budget = 1,
        .completion_cookie = 0x9999, .completion_budget = 0, .notify_mask = abi.CHRDEV_NOTIFY_MASK_SUCCESS, .notify_cookie = 0xFFFF,
        .notify_budget = 0, .reserved = 0, .policy_flags = 0, .policy_reserved = 0, .delivery_budget = 0, .deferred_budget = 0,
        .ack_mask = abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, .ack_window = 0, .ack_cookie = 0xF6F6, .ack_observed = 0, .ack_reserved = 0,
    };
    const empty_summary = chrdev_notify_ack_plan.summarize(empty_view);
    try std.testing.expect(chrdev_notify_ack_plan.isValid(empty_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_STATUS_NONE), empty_summary.ack_status);
    try std.testing.expectEqual(@as(u32, 0), empty_summary.matched_ack_mask);
    try std.testing.expectEqual(@as(u32, 0), empty_summary.ack_flags);
}

test "phase3 chrdev notify ack budget helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_view = chrdev_notify_ack_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0);
    const acked_summary = chrdev_notify_ack_budget_plan.summarize(acked_view);
    try std.testing.expect(chrdev_notify_ack_budget_plan.isValid(acked_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_BUDGET_STATUS_ACKED), acked_summary.ack_budget_status);
    try std.testing.expectEqual(@as(u32, 1), acked_summary.budget_acked_count);
    try std.testing.expectEqual(@as(u32, 0), acked_summary.ack_budget_after);

    const fallback_deferred_view = chrdev_notify_ack_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xB2B2, 1, 0, 0, 1);
    const fallback_deferred_summary = chrdev_notify_ack_budget_plan.summarize(fallback_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DEFERRED), fallback_deferred_summary.ack_budget_status);
    try std.testing.expectEqual(@as(u32, 1), fallback_deferred_summary.budget_deferred_ack_count);
    try std.testing.expect((fallback_deferred_summary.ack_budget_flags & abi.CHRDEV_NOTIFY_ACK_BUDGET_FLAG_ACK_BUDGET_EXHAUSTED) != 0);

    const policy_deferred_view = chrdev_notify_ack_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xCCCC, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xC3C3, 1, abi.CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED, 1, 1);
    const policy_deferred_summary = chrdev_notify_ack_budget_plan.summarize(policy_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DEFERRED), policy_deferred_summary.ack_budget_status);
    try std.testing.expectEqual(@as(u32, 1), policy_deferred_summary.budget_deferred_ack_count);
    try std.testing.expectEqual(@as(u32, 0), policy_deferred_summary.deferred_ack_budget_after);

    const dropped_view = chrdev_notify_ack_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xD4D4, 1, 0, 0, 0);
    const dropped_summary = chrdev_notify_ack_budget_plan.summarize(dropped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DROPPED), dropped_summary.ack_budget_status);
    try std.testing.expectEqual(@as(u32, 1), dropped_summary.budget_dropped_ack_count);

    const suppressed_view = chrdev_notify_ack_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xE5E5, 0, abi.CHRDEV_NOTIFY_ACK_POLICY_SUPPRESS_EXPIRED, 1, 1);
    const suppressed_summary = chrdev_notify_ack_budget_plan.summarize(suppressed_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_BUDGET_STATUS_SUPPRESSED), suppressed_summary.ack_budget_status);
    try std.testing.expectEqual(@as(u32, 1), suppressed_summary.budget_suppressed_ack_count);
    try std.testing.expectEqual(@as(u32, 1), suppressed_summary.ack_budget_after);

    const skipped_view = chrdev_notify_ack_budget_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1);
    const skipped_summary = chrdev_notify_ack_budget_plan.summarize(skipped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_BUDGET_STATUS_SKIPPED), skipped_summary.ack_budget_status);
    try std.testing.expectEqual(@as(u32, 1), skipped_summary.budget_skipped_ack_count);
}

test "phase3 chrdev notify ack window helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_view = chrdev_notify_ack_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0);
    const acked_summary = chrdev_notify_ack_window_plan.summarize(acked_view);
    try std.testing.expect(chrdev_notify_ack_window_plan.isValid(acked_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_STATUS_ACKED), acked_summary.window_status);
    try std.testing.expectEqual(@as(u32, 1), acked_summary.window_acked_count);
    try std.testing.expectEqual(@as(u32, 1), acked_summary.window_after);

    const floor_held_view = chrdev_notify_ack_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xCCCC, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xC3C3, 1, abi.CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED, 1, 1, 2);
    const floor_held_summary = chrdev_notify_ack_window_plan.summarize(floor_held_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_STATUS_DEFERRED), floor_held_summary.window_status);
    try std.testing.expect((floor_held_summary.window_flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_FLAG_FLOOR_HELD) != 0);
    try std.testing.expectEqual(@as(u32, 2), floor_held_summary.window_after);

    const dropped_view = chrdev_notify_ack_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xD4D4, 1, 0, 1, 0, 0);
    const dropped_summary = chrdev_notify_ack_window_plan.summarize(dropped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_STATUS_DROPPED), dropped_summary.window_status);
    try std.testing.expect((dropped_summary.window_flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_FLAG_WINDOW_EXHAUSTED) != 0);

    const suppressed_view = chrdev_notify_ack_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xE5E5, 0, abi.CHRDEV_NOTIFY_ACK_POLICY_SUPPRESS_EXPIRED, 1, 1, 0);
    const suppressed_summary = chrdev_notify_ack_window_plan.summarize(suppressed_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_STATUS_SUPPRESSED), suppressed_summary.window_status);
    try std.testing.expectEqual(@as(u32, 1), suppressed_summary.window_suppressed_count);

    const skipped_view = chrdev_notify_ack_window_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0);
    const skipped_summary = chrdev_notify_ack_window_plan.summarize(skipped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_STATUS_SKIPPED), skipped_summary.window_status);
    try std.testing.expectEqual(@as(u32, 1), skipped_summary.window_skipped_count);
}

test "phase3 chrdev notify ack window policy helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_view = chrdev_notify_ack_window_policy_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0);
    const acked_summary = chrdev_notify_ack_window_policy_plan.summarize(acked_view);
    try std.testing.expect(chrdev_notify_ack_window_policy_plan.isValid(acked_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_ACKED), acked_summary.window_policy_status);
    try std.testing.expectEqual(@as(u32, 1), acked_summary.policy_window_acked_count);

    const forced_deferred_view = chrdev_notify_ack_window_policy_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xB2B2, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED);
    const forced_deferred_summary = chrdev_notify_ack_window_policy_plan.summarize(forced_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DEFERRED), forced_deferred_summary.window_policy_status);
    try std.testing.expectEqual(@as(u32, 1), forced_deferred_summary.policy_window_deferred_count);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED), forced_deferred_summary.effective_window_policy_flags);

    const dropped_view = chrdev_notify_ack_window_policy_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xD4D4, 1, 0, 1, 0, 0, 0);
    const dropped_summary = chrdev_notify_ack_window_policy_plan.summarize(dropped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DROPPED), dropped_summary.window_policy_status);
    try std.testing.expectEqual(@as(u32, 1), dropped_summary.policy_window_dropped_count);

    const suppressed_dropped_view = chrdev_notify_ack_window_policy_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xE5E5, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED);
    const suppressed_dropped_summary = chrdev_notify_ack_window_policy_plan.summarize(suppressed_dropped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SUPPRESSED), suppressed_dropped_summary.window_policy_status);
    try std.testing.expectEqual(@as(u32, 1), suppressed_dropped_summary.policy_window_suppressed_count);

    const coalesced_view = chrdev_notify_ack_window_policy_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xE5E5, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xE5E5, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE);
    const coalesced_summary = chrdev_notify_ack_window_policy_plan.summarize(coalesced_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_COALESCED), coalesced_summary.window_policy_status);
    try std.testing.expectEqual(@as(u32, 1), coalesced_summary.policy_window_coalesced_count);
    try std.testing.expectEqual(@as(u64, 0xE5E5), coalesced_summary.effective_window_cookie);

    const skipped_view = chrdev_notify_ack_window_policy_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0);
    const skipped_summary = chrdev_notify_ack_window_policy_plan.summarize(skipped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SKIPPED), skipped_summary.window_policy_status);
    try std.testing.expectEqual(@as(u32, 1), skipped_summary.policy_window_skipped_count);
}

test "phase3 chrdev notify ack window policy budget helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0);
    const acked_summary = chrdev_notify_ack_window_policy_budget_plan.summarize(acked_view);
    try std.testing.expect(chrdev_notify_ack_window_policy_budget_plan.isValid(acked_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_ACKED), acked_summary.window_policy_budget_status);
    try std.testing.expectEqual(@as(u32, 1), acked_summary.budget_window_acked_count);
    try std.testing.expectEqual(@as(u32, 0), acked_summary.window_policy_budget_after);

    const fallback_deferred_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xB2B2, 1, 0, 1, 0, 0, 0, 0, 1);
    const fallback_deferred_summary = chrdev_notify_ack_window_policy_budget_plan.summarize(fallback_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DEFERRED), fallback_deferred_summary.window_policy_budget_status);
    try std.testing.expectEqual(@as(u32, 1), fallback_deferred_summary.budget_window_deferred_count);
    try std.testing.expect((fallback_deferred_summary.window_policy_budget_flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_WINDOW_POLICY_BUDGET_EXHAUSTED) != 0);

    const policy_deferred_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xCCCC, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xC3C3, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED, 1, 1);
    const policy_deferred_summary = chrdev_notify_ack_window_policy_budget_plan.summarize(policy_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DEFERRED), policy_deferred_summary.window_policy_budget_status);
    try std.testing.expectEqual(@as(u32, 1), policy_deferred_summary.budget_window_deferred_count);
    try std.testing.expectEqual(@as(u32, 0), policy_deferred_summary.deferred_window_policy_budget_after);

    const coalesced_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xE5E5, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xE5E5, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE, 1, 0);
    const coalesced_summary = chrdev_notify_ack_window_policy_budget_plan.summarize(coalesced_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_COALESCED), coalesced_summary.window_policy_budget_status);
    try std.testing.expectEqual(@as(u32, 1), coalesced_summary.budget_window_coalesced_count);

    const suppressed_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xE5E5, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED, 1, 1);
    const suppressed_summary = chrdev_notify_ack_window_policy_budget_plan.summarize(suppressed_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_SUPPRESSED), suppressed_summary.window_policy_budget_status);
    try std.testing.expectEqual(@as(u32, 1), suppressed_summary.budget_window_suppressed_count);

    const dropped_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xD4D4, 1, 0, 1, 0, 0, 0, 1, 1);
    const dropped_summary = chrdev_notify_ack_window_policy_budget_plan.summarize(dropped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DROPPED), dropped_summary.window_policy_budget_status);
    try std.testing.expectEqual(@as(u32, 1), dropped_summary.budget_window_dropped_count);

    const skipped_view = chrdev_notify_ack_window_policy_budget_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1);
    const skipped_summary = chrdev_notify_ack_window_policy_budget_plan.summarize(skipped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_SKIPPED), skipped_summary.window_policy_budget_status);
    try std.testing.expectEqual(@as(u32, 1), skipped_summary.budget_window_skipped_count);
}

test "phase3 chrdev notify ack window policy budget window helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_view = chrdev_notify_ack_window_policy_budget_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0);
    const acked_summary = chrdev_notify_ack_window_policy_budget_window_plan.summarize(acked_view);
    try std.testing.expect(chrdev_notify_ack_window_policy_budget_window_plan.isValid(acked_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_ACKED), acked_summary.window_policy_budget_window_status);
    try std.testing.expectEqual(@as(u32, 1), acked_summary.window_policy_budget_window_acked_count);
    try std.testing.expect((acked_summary.window_policy_budget_window_flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_USED) != 0);

    const floor_held_view = chrdev_notify_ack_window_policy_budget_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xB2B2, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED, 1, 1, 1, 1);
    const floor_held_summary = chrdev_notify_ack_window_policy_budget_window_plan.summarize(floor_held_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DEFERRED), floor_held_summary.window_policy_budget_window_status);
    try std.testing.expect((floor_held_summary.window_policy_budget_window_flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_FLAG_FLOOR_HELD) != 0);
    try std.testing.expectEqual(@as(u32, 1), floor_held_summary.window_policy_budget_window_deferred_count);

    const policy_deferred_view = chrdev_notify_ack_window_policy_budget_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xCCCC, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xC3C3, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED, 1, 1, 3, 0);
    const policy_deferred_summary = chrdev_notify_ack_window_policy_budget_window_plan.summarize(policy_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DEFERRED), policy_deferred_summary.window_policy_budget_window_status);
    try std.testing.expectEqual(@as(u32, 1), policy_deferred_summary.window_policy_budget_window_deferred_count);

    const coalesced_view = chrdev_notify_ack_window_policy_budget_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xE5E5, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xE5E5, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE, 1, 0, 3, 0);
    const coalesced_summary = chrdev_notify_ack_window_policy_budget_window_plan.summarize(coalesced_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_COALESCED), coalesced_summary.window_policy_budget_window_status);
    try std.testing.expectEqual(@as(u32, 1), coalesced_summary.window_policy_budget_window_coalesced_count);

    const suppressed_view = chrdev_notify_ack_window_policy_budget_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xE5E5, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED, 1, 1, 2, 0);
    const suppressed_summary = chrdev_notify_ack_window_policy_budget_window_plan.summarize(suppressed_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SUPPRESSED), suppressed_summary.window_policy_budget_window_status);
    try std.testing.expectEqual(@as(u32, 1), suppressed_summary.window_policy_budget_window_suppressed_count);

    const dropped_view = chrdev_notify_ack_window_policy_budget_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xD4D4, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0);
    const dropped_summary = chrdev_notify_ack_window_policy_budget_window_plan.summarize(dropped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DROPPED), dropped_summary.window_policy_budget_window_status);
    try std.testing.expectEqual(@as(u32, 1), dropped_summary.window_policy_budget_window_dropped_count);

    const skipped_view = chrdev_notify_ack_window_policy_budget_window_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0);
    const skipped_summary = chrdev_notify_ack_window_policy_budget_window_plan.summarize(skipped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SKIPPED), skipped_summary.window_policy_budget_window_status);
    try std.testing.expectEqual(@as(u32, 1), skipped_summary.window_policy_budget_window_skipped_count);
}

test "phase3 chrdev notify ack window policy budget window delivery helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_view = chrdev_notify_ack_window_policy_budget_window_delivery_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0);
    const acked_summary = chrdev_notify_ack_window_policy_budget_window_delivery_plan.summarize(acked_view);
    try std.testing.expect(chrdev_notify_ack_window_policy_budget_window_delivery_plan.isValid(acked_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_ACKED), acked_summary.window_policy_budget_window_delivery_status);
    try std.testing.expectEqual(@as(u32, 1), acked_summary.window_policy_budget_window_delivery_acked_count);
    try std.testing.expect((acked_summary.window_policy_budget_window_delivery_flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_WINDOW_DELIVERY_BUDGET_USED) != 0);

    const fallback_deferred_view = chrdev_notify_ack_window_policy_budget_window_delivery_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xB2B2, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 1);
    const fallback_deferred_summary = chrdev_notify_ack_window_policy_budget_window_delivery_plan.summarize(fallback_deferred_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED), fallback_deferred_summary.window_policy_budget_window_delivery_status);
    try std.testing.expectEqual(@as(u32, 1), fallback_deferred_summary.window_policy_budget_window_delivery_deferred_count);
    try std.testing.expect((fallback_deferred_summary.window_policy_budget_window_delivery_flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_WINDOW_DELIVERY_BUDGET_EXHAUSTED) != 0);
    try std.testing.expect((fallback_deferred_summary.window_policy_budget_window_delivery_flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_USED) != 0);

    const suppressed_view = chrdev_notify_ack_window_policy_budget_window_delivery_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xE5E5, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED, 1, 1, 2, 0, 1, 1);
    const suppressed_summary = chrdev_notify_ack_window_policy_budget_window_delivery_plan.summarize(suppressed_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_SUPPRESSED), suppressed_summary.window_policy_budget_window_delivery_status);
    try std.testing.expectEqual(@as(u32, 1), suppressed_summary.window_policy_budget_window_delivery_suppressed_count);

    const skipped_view = chrdev_notify_ack_window_policy_budget_window_delivery_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1);
    const skipped_summary = chrdev_notify_ack_window_policy_budget_window_delivery_plan.summarize(skipped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_SKIPPED), skipped_summary.window_policy_budget_window_delivery_status);
    try std.testing.expectEqual(@as(u32, 1), skipped_summary.window_policy_budget_window_delivery_skipped_count);
}

test "phase3 chrdev notify ack window policy budget window delivery window helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_view = chrdev_notify_ack_window_policy_budget_window_delivery_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0);
    const acked_summary = chrdev_notify_ack_window_policy_budget_window_delivery_window_plan.summarize(acked_view);
    try std.testing.expect(chrdev_notify_ack_window_policy_budget_window_delivery_window_plan.isValid(acked_view));
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED), acked_summary.window_policy_budget_window_delivery_window_status);
    try std.testing.expectEqual(@as(u32, 1), acked_summary.window_policy_budget_window_delivery_window_acked_count);
    try std.testing.expect((acked_summary.window_policy_budget_window_delivery_window_flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_USED) != 0);

    const floor_held_view = chrdev_notify_ack_window_policy_budget_window_delivery_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 1, 1);
    const floor_held_summary = chrdev_notify_ack_window_policy_budget_window_delivery_window_plan.summarize(floor_held_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED), floor_held_summary.window_policy_budget_window_delivery_window_status);
    try std.testing.expect((floor_held_summary.window_policy_budget_window_delivery_window_flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_FLOOR_HELD) != 0);
    try std.testing.expect((floor_held_summary.window_policy_budget_window_delivery_window_flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_FLOOR_BLOCKED) != 0);

    const dropped_view = chrdev_notify_ack_window_policy_budget_window_delivery_window_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xD4D4, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0);
    const dropped_summary = chrdev_notify_ack_window_policy_budget_window_delivery_window_plan.summarize(dropped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED), dropped_summary.window_policy_budget_window_delivery_window_status);
    try std.testing.expectEqual(@as(u32, 1), dropped_summary.window_policy_budget_window_delivery_window_dropped_count);

    const skipped_view = chrdev_notify_ack_window_policy_budget_window_delivery_window_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1, 2, 1);
    const skipped_summary = chrdev_notify_ack_window_policy_budget_window_delivery_window_plan.summarize(skipped_view);
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED), skipped_summary.window_policy_budget_window_delivery_window_status);
    try std.testing.expectEqual(@as(u32, 1), skipped_summary.window_policy_budget_window_delivery_window_skipped_count);
}

test "phase3 chrdev notify ack delivery budget guard window helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_parent = chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1),
        1,
        0,
    );
    const acked_summary = chrdev_notify_ack_delivery_budget_guard_window_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(acked_parent, 2, 1, 0),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_ACKED), acked_summary.window_status);
    try std.testing.expect((acked_summary.window_flags & abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PRIMARY_WINDOW_USED) != 0);
    try std.testing.expectEqual(@as(u32, 1), acked_summary.primary_window_after);

    const fallback_summary = chrdev_notify_ack_delivery_budget_guard_window_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(acked_parent, 0, 2, 0),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DEFERRED), fallback_summary.window_status);
    try std.testing.expect((fallback_summary.window_flags & abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_WINDOW_EXHAUSTED) != 0);
    try std.testing.expect((fallback_summary.window_flags & abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_DEFERRED_WINDOW_USED) != 0);

    const skipped_parent = chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 2, 1),
        1,
        1,
    );
    const skipped_summary = chrdev_notify_ack_delivery_budget_guard_window_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(skipped_parent, 2, 2, 1),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_SKIPPED), skipped_summary.window_status);
    try std.testing.expectEqual(@as(u32, 1), skipped_summary.skipped_count);
}

test "phase3 chrdev notify ack delivery budget guard window policy helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_parent = chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(
        chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
            chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1),
            1,
            0,
        ),
        2,
        1,
        0,
    );
    const acked_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(acked_parent, 0),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_ACKED), acked_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), acked_summary.acked_count);

    const forced_deferred_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(acked_parent, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DEFERRED), forced_deferred_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), forced_deferred_summary.deferred_count);

    const coalesced_parent = chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(
        chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
            chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xE5E5, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xE5E5, 1, 0, 1, 0, 0, abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE, 1, 0, 3, 0, 1, 0, 2, 1, 1, 0, 1, 0, 1, 0, 3, 0, 0, 0),
            1,
            0,
        ),
        2,
        1,
        0,
    );
    const coalesced_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(coalesced_parent, 0),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DROPPED), coalesced_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), coalesced_summary.dropped_count);

    const held_parent = chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(
        chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
            chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1),
            1,
            0,
        ),
        1,
        1,
        1,
    );
    const suppressed_held_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(held_parent, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_HELD),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SUPPRESSED), suppressed_held_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), suppressed_held_summary.suppressed_count);

    const skipped_parent = chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(
        chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
            chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 2, 1),
            1,
            1,
        ),
        2,
        2,
        1,
    );
    const skipped_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(skipped_parent, 0),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SKIPPED), skipped_summary.policy_status);
    try std.testing.expectEqual(@as(u32, 1), skipped_summary.skipped_count);
}

test "phase3 chrdev notify ack delivery budget guard window policy budget helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_parent = chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(
        chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(
            chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
                chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1),
                1,
                0,
            ),
            2,
            1,
            0,
        ),
        0,
    );
    const acked_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.viewFromParent(acked_parent, 1, 1),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_ACKED), acked_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 0), acked_summary.primary_budget_after);
    try std.testing.expectEqual(@as(u32, 1), acked_summary.acked_count);

    const fallback_deferred_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.viewFromParent(acked_parent, 0, 1),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DEFERRED), fallback_deferred_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 0), fallback_deferred_summary.deferred_budget_after);
    try std.testing.expectEqual(@as(u32, 1), fallback_deferred_summary.deferred_count);

    const policy_deferred_parent = chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(
        chrdev_notify_ack_delivery_budget_guard_window_policy_plan.asParentView(acked_parent),
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED,
    );
    const policy_deferred_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.viewFromParent(policy_deferred_parent, 1, 1),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DEFERRED), policy_deferred_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 0), policy_deferred_summary.deferred_budget_after);
    try std.testing.expectEqual(@as(u32, 1), policy_deferred_summary.deferred_count);

    const held_parent = chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(
        chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(
            chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
                chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1),
                1,
                0,
            ),
            1,
            1,
            1,
        ),
        0,
    );
    const held_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.viewFromParent(held_parent, 1, 1),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_HELD), held_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 1), held_summary.held_count);

    const suppressed_dropped_parent = chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(
        chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(
            chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
                chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xDDDD, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xD4D4, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0),
                0,
                0,
            ),
            0,
            0,
            0,
        ),
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_DROPPED,
    );
    const suppressed_dropped_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.viewFromParent(suppressed_dropped_parent, 1, 1),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_SUPPRESSED), suppressed_dropped_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 1), suppressed_dropped_summary.suppressed_count);

    const skipped_parent = chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(
        chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(
            chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
                chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 2, 1),
                1,
                1,
            ),
            2,
            2,
            1,
        ),
        0,
    );
    const skipped_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.viewFromParent(skipped_parent, 1, 1),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_SKIPPED), skipped_summary.budget_status);
    try std.testing.expectEqual(@as(u32, 1), skipped_summary.skipped_count);
}

test "phase3 chrdev notify ack delivery budget guard window policy budget window delivery helpers stay aligned with the ABI substrate" {
    const words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 3) | (@as(usize, 1) << 7)};
    const exhausted_words = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 4)};

    const acked_parent_view = chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan.viewFromParent(
        chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.viewFromParent(
            chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(
                chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(
                    chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
                        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1),
                        1,
                        0,
                    ),
                    2,
                    1,
                    0,
                ),
                0,
            ),
            1,
            1,
        ),
        2,
        0,
    );
    const acked_delivery_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan.viewFromParent(
            acked_parent_view,
            1,
            0,
        ),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_ACKED), acked_delivery_summary.delivery_status);
    try std.testing.expectEqual(@as(u32, 0), acked_delivery_summary.primary_delivery_budget_after);
    try std.testing.expectEqual(@as(u32, 1), acked_delivery_summary.acked_count);

    const fallback_deferred_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan.viewFromParent(
            acked_parent_view,
            0,
            1,
        ),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED), fallback_deferred_summary.delivery_status);
    try std.testing.expectEqual(@as(u32, 0), fallback_deferred_summary.deferred_delivery_budget_after);
    try std.testing.expectEqual(@as(u32, 1), fallback_deferred_summary.deferred_count);

    const held_delivery_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan.viewFromParent(
            chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan.viewFromParent(
                chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.viewFromParent(
                    chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(
                        chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(
                            chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
                                chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(words[0..], 240, 32, 8, 8, 2, abi.IDA_POLICY_LAST_FIT, 37, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_MODE_READ | abi.CHRDEV_MODE_WRITE, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_WRITE, abi.CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, abi.CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1),
                                1,
                                0,
                            ),
                            1,
                            1,
                            1,
                        ),
                        0,
                    ),
                    1,
                    1,
                ),
                2,
                0,
            ),
            1,
            1,
        ),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_HELD), held_delivery_summary.delivery_status);
    try std.testing.expectEqual(@as(u32, 1), held_delivery_summary.held_count);

    const skipped_delivery_summary = chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan.summarize(
        chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_plan.viewFromParent(
            chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_plan.viewFromParent(
                chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan.viewFromParent(
                    chrdev_notify_ack_delivery_budget_guard_window_policy_plan.viewFromParent(
                        chrdev_notify_ack_delivery_budget_guard_window_plan.viewFromParent(
                            chrdev_notify_ack_delivery_budget_guard_plan.viewFromParent(
                                chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan.viewFromBits(exhausted_words[0..], 240, 16, 5, 5, 2, abi.IDA_POLICY_FIRST_FIT, 20, abi.CHRDEV_MODE_READ, abi.CHRDEV_MODE_READ, abi.CHRDEV_FOP_OPEN | abi.CHRDEV_FOP_RELEASE | abi.CHRDEV_FOP_READ, abi.CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, abi.CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, abi.CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, abi.CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 2, 1),
                                1,
                                1,
                            ),
                            2,
                            2,
                            1,
                        ),
                        0,
                    ),
                    1,
                    1,
                ),
                2,
                0,
            ),
            1,
            1,
        ),
    );
    try std.testing.expectEqual(@as(u32, abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_SKIPPED), skipped_delivery_summary.delivery_status);
    try std.testing.expectEqual(@as(u32, 1), skipped_delivery_summary.skipped_count);
}
