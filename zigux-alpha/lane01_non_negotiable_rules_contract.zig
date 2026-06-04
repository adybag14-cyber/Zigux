const std = @import("std");
const testing = std.testing;

const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const Section = struct {
    start: usize,
    end: usize,

    fn text(self: Section) []const u8 {
        return roadmap[self.start..self.end];
    }
};

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], needle) orelse {
            return error.MissingOrOutOfOrderMarker;
        };
        cursor += relative + needle.len;
    }
}

fn nonNegotiableRulesSection() !Section {
    const start_marker = "## Non-Negotiable Product Rules";
    const end_marker = "## How ZAR Should Feed Zigux";

    const start = std.mem.indexOf(u8, roadmap, start_marker) orelse return error.MissingRulesSection;
    const end_relative = std.mem.indexOf(u8, roadmap[start..], end_marker) orelse return error.MissingNextSection;
    return .{
        .start = start,
        .end = start + end_relative,
    };
}

test "non-negotiable product rules keep their ordered roadmap packet" {
    const section = (try nonNegotiableRulesSection()).text();

    try requireOrdered(section, &.{
        "1. No flag-day rewrite.",
        "2. No mirror-tree sprawl.",
        "3. Co-locate product code with Linux ownership.",
        "4. Keep the Zigux support root small.",
        "5. Port leaf helpers before shared runtime helpers.",
        "6. Validation is mandatory before expansion.",
        "7. Wrapper-first or dual-implementation is the default where semantics are risky.",
        "8. Deep-core freeze is real.",
        "9. Human review remains mandatory.",
    });
}

test "folder-charter boundaries stay explicit in product rules" {
    const section = (try nonNegotiableRulesSection()).text();

    try requireContains(section, "Zigux grows through mixed-language coexistence.");
    try requireContains(section, "`zigux-alpha/` is a bootstrap workspace, not the final home for subsystem ports.");
    try requireContains(section, "Do not build a fake parallel kernel under a generic Zigux namespace.");
    try requireContains(section, "Host-side helper ports belong beside current files such as `tools/lib/*.zig`.");
    try requireContains(section, "The support root exists for boundary code, not for duplicating Linux subsystems.");
}

test "validation wrapper and freeze rules remain named" {
    const section = (try nonNegotiableRulesSection()).text();

    try requireContains(section, "Every approved target needs parity tests.");
    try requireContains(section, "Every sensitive path needs a perf threshold.");
    try requireContains(section, "Every migration needs a rollback owner.");
    try requireContains(section, "ABI/export surfaces");
    try requireContains(section, "virtio rings");
    try requireContains(section, "`kernel/sched/core.c`");
    try requireContains(section, "`mm/page_alloc.c`");
    try requireContains(section, "`kernel/rcu/tree.c`");
    try requireContains(section, "`net/core/skbuff.c`");
}

test "human review boundary remains stronger than automation" {
    const section = (try nonNegotiableRulesSection()).text();

    try requireContains(section, "Follow Linux process expectations.");
    try requireContains(section, "Use AI-assisted work only as a human-reviewed aid, not as an autonomous authority.");
}
