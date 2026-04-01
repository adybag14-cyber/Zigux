const std = @import("std");
const parent_plan = @import("current_window_plan");

pub const ParentView = parent_plan.View;
pub const ParentSummary = parent_plan.Summary;

pub const FLAG_BUDGET_APPLIED: u32 = 1 << 0;
pub const FLAG_BUDGET_USED: u32 = 1 << 1;
pub const FLAG_DEFERRED_BUDGET_USED: u32 = 1 << 2;
pub const FLAG_BUDGET_EXHAUSTED: u32 = 1 << 3;
pub const FLAG_DEFERRED_BUDGET_EXHAUSTED: u32 = 1 << 4;

pub const STATUS_NONE: u32 = 0;
pub const STATUS_ACKED: u32 = 1;
pub const STATUS_DEFERRED: u32 = 2;
pub const STATUS_SUPPRESSED: u32 = 3;
pub const STATUS_COALESCED: u32 = 4;
pub const STATUS_DROPPED: u32 = 5;
pub const STATUS_SKIPPED: u32 = 6;
pub const STATUS_HELD: u32 = 7;

pub const View = extern struct {
    parent: ParentView,
    delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget: u32,
    deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget: u32,
    reserved: u32,
};

pub const Summary = extern struct {
    parent: ParentSummary,
    delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flags: u32,
    delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_before: u32,
    delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after: u32,
    deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_before: u32,
    deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after: u32,
    delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status: u32,
    acked_count: u32,
    deferred_count: u32,
    suppressed_count: u32,
    coalesced_count: u32,
    dropped_count: u32,
    skipped_count: u32,
    held_count: u32,
};

fn emptySummary() Summary {
    return std.mem.zeroInit(Summary, .{});
}

pub fn viewFromParent(parent: ParentView, delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget: u32, deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget: u32) View {
    return .{
        .parent = parent,
        .delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget = delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget,
        .deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget = deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget,
        .reserved = 0,
    };
}

pub fn asParentView(view: View) ParentView {
    return view.parent;
}

pub fn isValid(view: View) bool {
    if (view.reserved != 0) return false;
    return parent_plan.isValid(view.parent);
}

pub fn summarize(view: View) Summary {
    if (!isValid(view)) return emptySummary();

    const parent_summary = parent_plan.summarize(view.parent);
    var summary = emptySummary();
    summary.parent = parent_summary;
    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flags = 0;
    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_before = view.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget;
    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after = view.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget;
    summary.deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_before = view.deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget;
    summary.deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after = view.deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget;
    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status = STATUS_NONE;

    switch (parent_summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status) {
        parent_plan.STATUS_NONE => {},
        parent_plan.STATUS_SUPPRESSED => {
            summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status = STATUS_SUPPRESSED;
            summary.suppressed_count = 1;
        },
        parent_plan.STATUS_SKIPPED => {
            summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status = STATUS_SKIPPED;
            summary.skipped_count = 1;
        },
        parent_plan.STATUS_DROPPED => {
            summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status = STATUS_DROPPED;
            summary.dropped_count = 1;
        },
        parent_plan.STATUS_HELD => {
            summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status = STATUS_HELD;
            summary.held_count = 1;
        },
        parent_plan.STATUS_DEFERRED => {
            summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= FLAG_BUDGET_APPLIED;
            if (summary.deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after > 0) {
                summary.deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after -= 1;
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= FLAG_DEFERRED_BUDGET_USED;
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status = STATUS_DEFERRED;
                summary.deferred_count = 1;
            } else {
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= FLAG_DEFERRED_BUDGET_EXHAUSTED;
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status = STATUS_DROPPED;
                summary.dropped_count = 1;
            }
        },
        parent_plan.STATUS_ACKED,
        parent_plan.STATUS_COALESCED,
        => {
            summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= FLAG_BUDGET_APPLIED;
            if (summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after > 0) {
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after -= 1;
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= FLAG_BUDGET_USED;
                switch (parent_summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status) {
                    parent_plan.STATUS_ACKED => {
                        summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status = STATUS_ACKED;
                        summary.acked_count = 1;
                    },
                    parent_plan.STATUS_COALESCED => {
                        summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status = STATUS_COALESCED;
                        summary.coalesced_count = 1;
                    },
                    else => {
                        summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status = STATUS_DEFERRED;
                        summary.deferred_count = 1;
                    },
                }
            } else {
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= FLAG_BUDGET_EXHAUSTED;
                if (summary.deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after > 0) {
                    summary.deferred_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_after -= 1;
                    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= FLAG_DEFERRED_BUDGET_USED;
                    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status = STATUS_DEFERRED;
                    summary.deferred_count = 1;
                } else {
                    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= FLAG_DEFERRED_BUDGET_EXHAUSTED;
                    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_status = STATUS_DROPPED;
                    summary.dropped_count = 1;
                }
            }
        },
        else => {},
    }

    return summary;
}
