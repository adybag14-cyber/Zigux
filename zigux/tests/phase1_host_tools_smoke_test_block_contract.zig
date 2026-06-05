const std = @import("std");
const contract_options = @import("contract_options");

const smoke_source = @embedFile(contract_options.smoke_path);
const tests_build_source = @embedFile(contract_options.tests_build_path);

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingRequiredMarker;
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) != null) return error.StaleMarkerPresent;
}

fn requireExactlyOnce(haystack: []const u8, needle: []const u8) !usize {
    const first = try requireContains(haystack, needle);
    const after_first = first + needle.len;
    if (std.mem.indexOf(u8, haystack[after_first..], needle) != null) {
        return error.DuplicateMarker;
    }
    return first;
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = try requireContains(haystack, earlier);
    const later_index = try requireContains(haystack, later);
    if (earlier_index >= later_index) return error.MarkerOutOfOrder;
}

test "phase1 smoke harness keeps the closed current test block roster" {
    _ = try requireExactlyOnce(
        smoke_source,
        "test \"phase1 host-tools smoke imports the live helper modules\"",
    );
    _ = try requireExactlyOnce(
        smoke_source,
        "test \"phase1 host-tools smoke exercises live helper behavior\"",
    );
    _ = try requireExactlyOnce(
        smoke_source,
        "test \"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\"",
    );
    _ = try requireExactlyOnce(
        smoke_source,
        "test \"phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned\"",
    );

    try requireBefore(
        smoke_source,
        "test \"phase1 host-tools smoke imports the live helper modules\"",
        "test \"phase1 host-tools smoke exercises live helper behavior\"",
    );
    try requireBefore(
        smoke_source,
        "test \"phase1 host-tools smoke exercises live helper behavior\"",
        "test \"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\"",
    );
    try requireBefore(
        smoke_source,
        "test \"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\"",
        "test \"phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned\"",
    );
}

test "phase1 smoke source keeps helper family anchors in their owning blocks" {
    try requireBefore(
        smoke_source,
        "try std.testing.expect(@hasDecl(argv_split, \"argvSplit\"));",
        "var split = try argv_split.argv_split",
    );
    try requireBefore(
        smoke_source,
        "try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(0xf0));",
        "slab.kmalloc_nr_allocated = 0;",
    );
    try requireBefore(
        smoke_source,
        "list_sort.listSort(null, &bool_head, bool_cmp);",
        "const word_bits = find_bit.bits_per_long;",
    );
    try requireBefore(
        smoke_source,
        "const sysfs = [_][]const u8{ \"disabled\", \"auto\\n\", \"manual\" };",
        "var tree_entries = [_]RbtreeSmokeEntry{",
    );
    try requireBefore(
        smoke_source,
        "try std.testing.expect(rbtree.emptyNode(&cached_replacement.node));",
        "test \"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\"",
    );
}

test "phase1 tests build root keeps shared smoke on the default gates" {
    _ = try requireExactlyOnce(tests_build_source, "fn addPhase1HostToolsSmoke(");
    _ = try requireExactlyOnce(tests_build_source, "const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);");
    _ = try requireExactlyOnce(tests_build_source, "const phase1_step = b.step(\n        \"phase1-host-tools-smoke\",");

    try requireBefore(
        tests_build_source,
        "const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);",
        "const phase1_step = b.step(\n        \"phase1-host-tools-smoke\",",
    );
    try requireBefore(
        tests_build_source,
        "phase1_step.dependOn(&phase1_host_tools_smoke.step);",
        "const phase1_string_direct_anchor_step = b.step(",
    );
    _ = try requireContains(
        tests_build_source,
        "smoke_step.dependOn(&phase1_host_tools_smoke.step);",
    );
    _ = try requireContains(
        tests_build_source,
        "test_step.dependOn(&phase1_host_tools_smoke.step);",
    );
}

test "phase1 smoke contract rejects stale detached harness spellings" {
    try requireAbsent(smoke_source, "phase1_host_tools_smoke_runtime_alloc_contract");
    try requireAbsent(smoke_source, "phase1-host-tools-smoke-runtime-alloc-contract");
    try requireAbsent(tests_build_source, "build.phase1_host_tools_smoke");
    try requireAbsent(tests_build_source, "phase1-host-tools-smoke-fixture-only");
}
