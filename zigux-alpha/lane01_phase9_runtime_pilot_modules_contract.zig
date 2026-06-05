const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const phase8_heading = "## Phase 8: Userspace-Adjacent Tooling Expansion";
const phase9_heading = "## Phase 9: Runtime Pilot Modules";
const phase10_heading = "## Phase 10: Virtio and Lab Drivers";

test "phase9 roadmap packet keeps runtime-pilot goal out of production pressure" {
    const section = phase9Section();

    try expectContains(section, "Primary product goal:");
    try expectContains(section, "enter runtime kernels through tests and samples, not production pressure");
    try expectContains(section, "Runtime Pilot Modules");
    try expectNotContains(section, "prove the driver model on VM-friendly transports");
    try expectNotContains(section, "bounded real hardware drivers");
}

test "phase9 roadmap packet keeps exact test and sample anchor roster" {
    const section = phase9Section();

    const anchors = [_][]const u8{
        "`lib/atomic64_test.c`",
        "`lib/test_bitmap.c`",
        "`samples/trace_events/trace-events-sample.c`",
        "`samples/kprobes/kretprobe_example.c`",
    };

    for (anchors) |anchor| {
        try expectContains(section, anchor);
    }

    try expectMarkerOrder(section, &anchors);
    try expectNotContains(section, "`drivers/virtio/virtio.c`");
    try expectNotContains(section, "`drivers/watchdog/gpio_wdt.c`");
}

test "phase9 roadmap packet keeps loadable-module feature and destination boundaries" {
    const section = phase9Section();

    const required_features = [_][]const u8{
        "first loadable Zigux runtime modules",
        "selftest hooks",
        "runtime module lifecycle parity",
    };
    const destinations = [_][]const u8{
        "`zigux/tests/runtime_*`",
        "`samples/zigux/runtime_*`",
    };

    for (required_features) |feature| {
        try expectContains(section, feature);
    }
    for (destinations) |destination| {
        try expectContains(section, destination);
    }

    try expectMarkerOrder(section, &required_features);
    try expectMarkerOrder(section, &destinations);
    try expectNotContains(section, "`drivers/virtio/*.zig`");
    try expectNotContains(section, "`drivers/watchdog/*.zig`");
}

test "phase9 roadmap packet stays ordered between tooling and virtio phases" {
    try expectMarkerOrder(roadmap, &[_][]const u8{
        phase8_heading,
        phase9_heading,
        phase10_heading,
    });

    const section = phase9Section();
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

fn phase9Section() []const u8 {
    const start = std.mem.indexOf(u8, roadmap, phase9_heading) orelse
        @panic("missing Phase 9 heading");
    const end_relative = std.mem.indexOf(u8, roadmap[start..], phase10_heading) orelse
        @panic("missing Phase 10 heading after Phase 9");
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
