const std = @import("std");

const readme_text = @embedFile("README.md");
const build_text = @embedFile("build.zig");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBefore;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfter;
    try std.testing.expect(before_index < after_index);
}

test "tests root documents differential harness ownership" {
    try requireContains(
        readme_text,
        "This directory is the home of reusable Zigux parity and differential validation harnesses.",
    );
    try requireContains(readme_text, "hold shared harness logic");
    try requireContains(readme_text, "keep product-facing validation code separate from ad hoc experiments");
    try requireContains(readme_text, "provide the checks for helper parity, ABI assertions, and rollback readiness");
    try requireContains(readme_text, "## Phase 1 host-tools review packet");
    try requireContains(readme_text, "## Phase 2 review packet");
    try requireContains(readme_text, "## Phase 3 shared substrate packet");
    try requireContains(readme_text, "## Phase 4 rollback-ownership and lab-matrix packet");
}

test "shared build root keeps reusable harness constructors and aggregate routes" {
    try requireContains(build_text, "fn addSurveyTest(");
    try requireContains(build_text, "fn addPhase1HostToolsSmoke(");
    try requireContains(build_text, "pub fn build(b: *std.Build) void");
    try requireContains(build_text, "const smoke_step = b.step(");
    try requireContains(build_text, "const test_step = b.step(");
    try requireContains(build_text, "Run the currently live shared survey anchors from zigux/tests");
    try requireContains(build_text, "Run the shared Zigux tests-root survey smoke");
    try requireAbsent(build_text, "ad hoc experiments");
}

test "shared build root keeps cross-phase route vocabulary ordered" {
    try requireContains(build_text, "\"phase1-host-tools-smoke\"");
    try requireContains(build_text, "\"phase3-test\"");
    try requireContains(build_text, "\"phase3-dump\"");
    try requireContains(build_text, "\"phase3-export-uapi-layout\"");
    try requireContains(build_text, "\"phase4-runtime-atomic64-diff-survey\"");
    try requireContains(build_text, "\"phase7-argv-split-survey\"");
    try requireContains(build_text, "\"phase8-host-tools-alpha\"");
    try requireContains(build_text, "\"phase10-virtio-core-survey\"");
    try requireContains(build_text, "\"phase12-virtio-net-throughput-parity\"");

    try requireOrdered(build_text, "const phase1_step = b.step(", "const phase3_test_step = b.step(");
    try requireOrdered(build_text, "const phase3_test_step = b.step(", "const phase4_step = b.step(");
    try requireOrdered(build_text, "const phase4_step = b.step(", "const phase7_step = b.step(");
    try requireOrdered(build_text, "const phase7_step = b.step(", "const phase8_host_tools_alpha_step = b.step(");
    try requireOrdered(build_text, "const phase8_host_tools_alpha_step = b.step(", "const phase10_step = b.step(");
    try requireOrdered(build_text, "const phase10_step = b.step(", "const phase12_throughput_step = b.step(");
}
