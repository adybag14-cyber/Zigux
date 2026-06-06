const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const phase10_heading = "## Phase 10: Virtio and Lab Drivers";
const phase11_heading = "## Phase 11: Simple Production Drivers";
const phase12_heading = "## Phase 12: Complex Production Drivers and Heavy Helper Consumers";

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, roadmap, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, roadmap, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

fn phase11Body() []const u8 {
    const phase11 = std.mem.indexOf(u8, roadmap, phase11_heading) orelse
        @panic("missing Phase 11 roadmap heading");
    const phase12 = std.mem.indexOf(u8, roadmap, phase12_heading) orelse
        @panic("missing Phase 12 roadmap heading");
    std.debug.assert(phase11 < phase12);
    return roadmap[phase11..phase12];
}

test "phase11 simple production driver goal stays lifecycle bounded" {
    const phase11 = phase11Body();

    try requireContains(phase11, phase11_heading);
    try requireContains(phase11, "Primary product goal:");
    try requireContains(phase11, "- move from lab drivers to bounded real hardware drivers with straightforward lifecycles");
}

test "phase11 keeps watchdog and hvc anchor roster explicit" {
    const phase11 = phase11Body();

    try requireContains(phase11, "Primary Linux anchors:");
    try requireContains(phase11, "- `drivers/watchdog/gpio_wdt.c`");
    try requireContains(phase11, "- `drivers/watchdog/bcm2835_wdt.c`");
    try requireContains(phase11, "- `drivers/watchdog/dw_wdt.c`");
    try requireContains(phase11, "- `drivers/tty/hvc/hvc_console.c`");
}

test "phase11 keeps driver template and validation features explicit" {
    const phase11 = phase11Body();

    try requireContains(phase11, "Required Zigux features:");
    try requireContains(phase11, "- direct-port or dual-impl driver templates");
    try requireContains(phase11, "- hardware validation matrix");
    try requireContains(phase11, "- teardown and failure-mode parity");
}

test "phase11 destinations and neighboring order stay bounded" {
    const phase11 = phase11Body();

    try requireContains(phase11, "Recommended Zigux destinations:");
    try requireContains(phase11, "- `drivers/watchdog/*.zig`");
    try requireContains(phase11, "- `drivers/tty/hvc/*.zig`");

    try requireOrdered(phase10_heading, phase11_heading);
    try requireOrdered(phase11_heading, phase12_heading);
}
