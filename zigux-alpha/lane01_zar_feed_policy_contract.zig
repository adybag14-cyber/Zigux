const std = @import("std");

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const Error = error{
    MissingMarker,
    MarkerOutOfOrder,
};

fn requireContains(haystack: []const u8, needle: []const u8) Error!void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        return Error.MissingMarker;
    }
}

fn requireInOrder(haystack: []const u8, needles: []const []const u8) Error!void {
    var offset: usize = 0;

    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[offset..], needle) orelse return Error.MissingMarker;
        const next = offset + found + needle.len;
        if (next < offset) {
            return Error.MarkerOutOfOrder;
        }
        offset = next;
    }
}

fn sectionBetween(
    haystack: []const u8,
    start_marker: []const u8,
    end_marker: []const u8,
) Error![]const u8 {
    const start = std.mem.indexOf(u8, haystack, start_marker) orelse return Error.MissingMarker;
    const body_start = start + start_marker.len;
    const relative_end = std.mem.indexOf(u8, haystack[body_start..], end_marker) orelse return Error.MissingMarker;
    return haystack[body_start .. body_start + relative_end];
}

test "ZAR feed policy keeps research and product repos separate" {
    const section = try sectionBetween(
        roadmap,
        "## How ZAR Should Feed Zigux",
        "## zigux-alpha Scope",
    );

    try requireInOrder(section, &.{
        "ZAR should not try to become Zigux.",
        "ZAR should instead feed Zigux in these ways:",
        "| ZAR capability or work type | Use for Zigux | How to transfer it | Zigux phase impact |",
        "The rule is simple:",
        "- If a ZAR slice reduces Zigux product risk, keep it.",
        "- If it only expands ZAR",
        "do not let it consume Zigux product bandwidth.",
    });
}

test "ZAR transfer table preserves the approved reuse lanes" {
    const section = try sectionBetween(
        roadmap,
        "## How ZAR Should Feed Zigux",
        "## zigux-alpha Scope",
    );

    try requireInOrder(section, &.{
        "| parity gates and drift checks | High | Rebuild as Linux-facing differential gates inside `zigux/tests/` and `scripts/zigux/` | 2-4 |",
        "| build reproducibility discipline | High | Transfer the release-gate mindset, not the exact scripts | 2-4 |",
        "| ABI/export/wrapper discipline | High | Convert to Linux-kernel-specific `zigux/` substrate rules | 3 |",
        "| bare-metal i386 platform and SMP research | Medium | Use as concurrency-validation research input only | 4, 9, 14 |",
        "| virtio, E1000, RTL8139 proof methodology | Medium | Reuse the validation mindset and probe culture, not the current ZAR code shape | 9-12 |",
        "| storage and filesystem probe methodology | Medium | Reuse for `fs/libfs`, `lib/devres`, and driver validation scaffolding | 4, 13 |",
        "| shell, TTY, tool-service runtime | Low | Product value is indirect; use only where it informs repo-hosted tooling or validation UX | 4-8 |",
        "| workspace/package/trust runtime | Low | Mostly ZAR-specific; keep out of near-term Zigux product scope | research only |",
        "| VFS overlay experiments | Medium | Use only as design lessons for bounded helper layers, not as a direct port target | 13-15 |",
        "| driver lifecycle proofs | High | Use to shape lab matrices, teardown checks, and failure-mode expectations | 10-12 |",
    });
}

test "ZAR feed policy keeps validation transfer Linux-facing" {
    const section = try sectionBetween(
        roadmap,
        "## How ZAR Should Feed Zigux",
        "## zigux-alpha Scope",
    );

    try requireContains(section, "Rebuild as Linux-facing differential gates inside `zigux/tests/` and `scripts/zigux/`");
    try requireContains(section, "Convert to Linux-kernel-specific `zigux/` substrate rules");
    try requireContains(section, "Use as concurrency-validation research input only");
    try requireContains(section, "Reuse for `fs/libfs`, `lib/devres`, and driver validation scaffolding");
    try requireContains(section, "Use to shape lab matrices, teardown checks, and failure-mode expectations");
    try requireContains(section, "research only");
}
