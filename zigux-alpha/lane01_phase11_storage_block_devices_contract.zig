const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const phase10_heading = "## Phase 10: Virtio and Lab Drivers";
const phase11_heading = "## Phase 11: Simple Production Drivers";
const phase12_heading = "## Phase 12: Complex Production Drivers and Heavy Helper Consumers";

test "phase11 roadmap packet keeps bounded production-driver goal" {
    const section = phase11Section();

    try expectContains(section, "Primary product goal:");
    try expectContains(
        section,
        "move from lab drivers to bounded real hardware drivers with straightforward lifecycles",
    );
    try expectContains(section, "Simple Production Drivers");
    try expectNotContains(section, "high-value, high-risk drivers only after earlier proof");
}

test "phase11 roadmap packet keeps exact Linux anchor roster" {
    const section = phase11Section();

    const anchors = [_][]const u8{
        "`drivers/watchdog/gpio_wdt.c`",
        "`drivers/watchdog/bcm2835_wdt.c`",
        "`drivers/watchdog/dw_wdt.c`",
        "`drivers/tty/hvc/hvc_console.c`",
    };

    for (anchors) |anchor| {
        try expectContains(section, anchor);
    }

    try expectMarkerOrder(section, &anchors);
    try expectNotContains(section, "`drivers/net/virtio_net.c`");
    try expectNotContains(section, "`drivers/nvme/host/pci.c`");
}

test "phase11 roadmap packet keeps validation and destination boundaries" {
    const section = phase11Section();

    const required_features = [_][]const u8{
        "direct-port or dual-impl driver templates",
        "hardware validation matrix",
        "teardown and failure-mode parity",
    };
    const destinations = [_][]const u8{
        "`drivers/watchdog/*.zig`",
        "`drivers/tty/hvc/*.zig`",
    };

    for (required_features) |feature| {
        try expectContains(section, feature);
    }
    for (destinations) |destination| {
        try expectContains(section, destination);
    }

    try expectMarkerOrder(section, &required_features);
    try expectMarkerOrder(section, &destinations);
    try expectNotContains(section, "`drivers/net/virtio_net.zig`");
    try expectNotContains(section, "`tools/lib/bpf/zigux_segments/`");
}

test "phase11 roadmap packet stays ordered between lab and complex-driver phases" {
    try expectMarkerOrder(roadmap, &[_][]const u8{
        phase10_heading,
        phase11_heading,
        phase12_heading,
    });

    const section = phase11Section();
    try expectContains(section, "Primary Linux anchors:");
    try expectContains(section, "Required Zigux features:");
    try expectContains(section, "Recommended Zigux destinations:");
    try expectMarkerOrder(section, &[_][]const u8{
        "Primary product goal:",
        "Primary Linux anchors:",
        "Required Zigux features:",
        "Recommended Zigux destinations:",
    });
}

fn phase11Section() []const u8 {
    const start = std.mem.indexOf(u8, roadmap, phase11_heading) orelse
        @panic("missing Phase 11 heading");
    const end_relative = std.mem.indexOf(u8, roadmap[start..], phase12_heading) orelse
        @panic("missing Phase 12 heading after Phase 11");
    return roadmap[start .. start + end_relative];
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectMarkerOrder(haystack: []const u8, markers: []const []const u8) !void {
    var search_start: usize = 0;
    for (markers) |marker| {
        const relative_index = std.mem.indexOf(u8, haystack[search_start..], marker) orelse
            return error.MissingMarker;
        search_start += relative_index + marker.len;
    }
}
