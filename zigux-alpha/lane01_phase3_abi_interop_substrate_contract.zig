const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const linux_anchor_markers = [_][]const u8{
    "- `rust/exports.c`",
    "- `lib/bitmap.c`",
    "- `lib/rbtree.c`",
    "- `lib/cpumask.c`",
};

const required_feature_markers = [_][]const u8{
    "- explicit export shims",
    "- generated or curated bindings",
    "- layout assertions",
    "- explicit panic policy",
    "- explicit allocator policy",
    "- approved atomic, barrier, and MMIO wrappers",
    "- narrow unsafe surface",
};

const destination_markers = [_][]const u8{
    "- `zigux/kernel/`",
    "- `zigux/helpers/`",
    "- `zigux/bindings/`",
    "- `zigux/uapi/`",
    "- `zigux/unsafe/`",
    "- `include/linux/zigux.h`",
    "- `include/zigux/abi.h`",
};

test "phase 3 roadmap packet keeps permanent C Zigux boundary goal" {
    try expectContains("## Phase 3: ABI and Interop Substrate");
    try expectContains("Primary product goal:");
    try expectContains("- define the permanent C/Zigux boundary");
}

test "phase 3 roadmap packet keeps ABI anchors and substrate features" {
    try expectContains("Primary Linux anchors:");
    for (linux_anchor_markers) |marker| {
        try expectContains(marker);
    }

    try expectContains("Required Zigux features:");
    for (required_feature_markers) |marker| {
        try expectContains(marker);
    }
}

test "phase 3 roadmap packet keeps small support root destinations and ZAR boundary" {
    try expectContains("Recommended Zigux destinations:");
    for (destination_markers) |marker| {
        try expectContains(marker);
    }

    try expectContains("exported runtime state, ABI gating, and explicit failure-code discipline");
    try expectContains("the actual Zigux substrate must be Linux-kernel-specific");
}

test "phase 3 roadmap packet stays between toolchain and differential validation phases" {
    try expectOrder("## Phase 2: Toolchain and Kbuild Enablement", "## Phase 3: ABI and Interop Substrate");
    try expectOrder("## Phase 3: ABI and Interop Substrate", "## Phase 4: Differential Validation and Rollback");
    try expectOrder("- `zigux/Makefile`", "- define the permanent C/Zigux boundary");
    try expectOrder("- `include/zigux/abi.h`", "## Phase 4: Differential Validation and Rollback");
}

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, roadmap, 1, needle));
}

fn expectOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}
