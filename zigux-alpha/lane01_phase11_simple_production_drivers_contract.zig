const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "phase11 simple production driver goal stays lifecycle bounded" {
    try requireContains(roadmap, "## Phase 11: Simple Production Drivers");
    try requireContains(roadmap, "Primary product goal:");
    try requireContains(roadmap, "- move from lab drivers to bounded real hardware drivers with straightforward lifecycles");
}

test "phase11 keeps watchdog and hvc anchor roster explicit" {
    try requireContains(roadmap, "Primary Linux anchors:");
    try requireContains(roadmap, "- `drivers/watchdog/gpio_wdt.c`");
    try requireContains(roadmap, "- `drivers/watchdog/bcm2835_wdt.c`");
    try requireContains(roadmap, "- `drivers/watchdog/dw_wdt.c`");
    try requireContains(roadmap, "- `drivers/tty/hvc/hvc_console.c`");
}

test "phase11 keeps driver template and validation features explicit" {
    try requireContains(roadmap, "Required Zigux features:");
    try requireContains(roadmap, "- direct-port or dual-impl driver templates");
    try requireContains(roadmap, "- hardware validation matrix");
    try requireContains(roadmap, "- teardown and failure-mode parity");
}

test "phase11 destinations and neighboring order stay bounded" {
    try requireContains(roadmap, "Recommended Zigux destinations:");
    try requireContains(roadmap, "- `drivers/watchdog/*.zig`");
    try requireContains(roadmap, "- `drivers/tty/hvc/*.zig`");

    try requireOrdered("## Phase 10: Virtio and Lab Drivers", "## Phase 11: Simple Production Drivers");
    try requireOrdered("## Phase 11: Simple Production Drivers", "## Phase 12: Complex Production Drivers and Heavy Helper Consumers");
}
