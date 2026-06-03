const std = @import("std");

const roadmap_path = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md";

const required_phase3_lines = [_][]const u8{
    "## Phase 3: ABI and Interop Substrate",
    "Primary product goal:",
    "- define the permanent C/Zigux boundary",
    "Primary Linux anchors:",
    "- `rust/exports.c`",
    "- `lib/bitmap.c`",
    "- `lib/rbtree.c`",
    "- `lib/cpumask.c`",
    "Required Zigux features:",
    "- explicit export shims",
    "- generated or curated bindings",
    "- layout assertions",
    "- explicit panic policy",
    "- explicit allocator policy",
    "- approved atomic, barrier, and MMIO wrappers",
    "- narrow unsafe surface",
    "Recommended Zigux destinations:",
    "- `zigux/kernel/`",
    "- `zigux/helpers/`",
    "- `zigux/bindings/`",
    "- `zigux/uapi/`",
    "- `zigux/unsafe/`",
    "- `include/linux/zigux.h`",
    "- `include/zigux/abi.h`",
    "Why ZAR matters here:",
};

const zar_methodology_fragments = [_][]const u8{
    "exported runtime state, ABI gating, and explicit failure-code discipline",
    "directly useful as a product engineering habit",
    "actual Zigux substrate must be Linux-kernel-specific",
};

const phase3_order = [_][]const u8{
    "## Phase 3: ABI and Interop Substrate",
    "Primary product goal:",
    "Primary Linux anchors:",
    "Required Zigux features:",
    "Recommended Zigux destinations:",
    "Why ZAR matters here:",
    "## Phase 4: Differential Validation and Rollback",
};

test "phase3 roadmap packet keeps permanent C Zigux boundary contract" {
    const roadmap = try readRoadmap(std.testing.allocator);
    defer std.testing.allocator.free(roadmap);

    const packet = try sectionBetween(
        roadmap,
        "## Phase 3: ABI and Interop Substrate",
        "## Phase 4: Differential Validation and Rollback",
    );

    for (required_phase3_lines) |line| {
        try std.testing.expect(std.mem.indexOf(u8, packet, line) != null);
    }
    for (zar_methodology_fragments) |fragment| {
        try std.testing.expect(std.mem.indexOf(u8, packet, fragment) != null);
    }

    try std.testing.expect(countOccurrences(packet, "- `") == 11);
}

test "phase3 roadmap packet preserves ABI destination boundary before phase4" {
    const roadmap = try readRoadmap(std.testing.allocator);
    defer std.testing.allocator.free(roadmap);

    try expectOrdered(roadmap, &phase3_order);

    const packet = try sectionBetween(
        roadmap,
        "## Phase 3: ABI and Interop Substrate",
        "## Phase 4: Differential Validation and Rollback",
    );

    try std.testing.expect(std.mem.indexOf(u8, packet, "- `drivers/") == null);
    try std.testing.expect(std.mem.indexOf(u8, packet, "- `samples/") == null);
    try std.testing.expect(std.mem.indexOf(u8, packet, "- `tools/lib/") == null);
}

test "phase3 roadmap packet remains scoped between phase2 tooling and phase4 validation" {
    const roadmap = try readRoadmap(std.testing.allocator);
    defer std.testing.allocator.free(roadmap);

    try expectOrdered(roadmap, &[_][]const u8{
        "## Phase 2: Toolchain and Kbuild Enablement",
        "## Phase 3: ABI and Interop Substrate",
        "## Phase 4: Differential Validation and Rollback",
    });
}

fn readRoadmap(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        roadmap_path,
        allocator,
        .limited(256 * 1024),
    );
}

fn sectionBetween(text: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, text, start) orelse return error.MissingStartSection;
    const end_index = std.mem.indexOfPos(u8, text, start_index + start.len, end) orelse return error.MissingEndSection;
    return text[start_index..end_index];
}

fn expectOrdered(text: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const relative_index = std.mem.indexOfPos(u8, text, cursor, marker) orelse return error.MissingOrderedMarker;
        cursor = relative_index + marker.len;
    }
}

fn countOccurrences(text: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, text, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}
