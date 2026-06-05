const std = @import("std");
const contract_options = @import("contract_options");

const max_workflow_bytes = 1024 * 1024;

fn readWorkflow(allocator: std.mem.Allocator) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        contract_options.workflow_path,
        allocator,
        .limited(max_workflow_bytes),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |found| {
        count += 1;
        offset = found + needle.len;
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn requireOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOfPos(u8, haystack, cursor, needle) orelse {
            std.debug.print("missing or out-of-order workflow marker: {s}\n", .{needle});
            return error.MissingWorkflowMarker;
        };
        cursor = found + needle.len;
    }
}

test "phase1 closure flows into expanded phase3 export handoff before shared smoke" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const ordered = [_][]const u8{
        "name: Check current Phase 1 closure packet",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "name: Self-test current Phase 3 interop packet",
        "run: python3 scripts/zigux/validate_phase3_selftest.py",
        "name: Check current Phase 3 interop packet",
        "run: python3 scripts/zigux/run-phase3-checks.py",
        "name: Run current Phase 3 export/UAPI C header smoke",
        "run: python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
        "name: Run current Phase 3 export/UAPI layout replay",
        "run: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
        "name: Run current Phase 3 export shim replay",
        "run: zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
        "name: Run current Phase 3 shared tests-root packet",
        "run: zig build phase3-test --build-file zigux/tests/build.zig",
        "name: Run current Phase 3 ABI dump replay",
        "run: zig build phase3-dump --build-file zigux/tests/build.zig",
        "name: Run current Phase 1 shared tests-root smoke",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    };

    try requireOrdered(workflow, &ordered);
}

test "phase3 policy and low-level wrappers remain inside the handoff window" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const ordered = [_][]const u8{
        "name: Run current Phase 3 export shim replay",
        "name: Run current Phase 3 policy starter-packet replay",
        "run: make -C zigux phase3-policy-starter-packet-test",
        "name: Run current Phase 3 policy unsafe replay",
        "run: zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
        "name: Run current Phase 3 policy unsafe make route",
        "run: make -C zigux phase3-policy-unsafe-test",
        "name: Run current Phase 3 policy dump replay",
        "run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
        "name: Run current Phase 3 policy dump make wrapper",
        "run: make -C zigux phase3-policy-dump",
        "name: Self-test current Phase 3 low-level wrapper survey validator",
        "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
        "name: Check current Phase 3 low-level wrapper survey packet",
        "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "name: Run current Phase 3 low-level wrapper replay",
        "run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
        "name: Run current Phase 3 low-level wrapper make route",
        "run: make -C zigux phase3-low-level-wrappers",
        "name: Run current Phase 3 focused low-level wrapper make route",
        "run: make -C zigux phase3-low-level-wrappers-test",
        "name: Run current Phase 3 shared tests-root packet",
    };

    try requireOrdered(workflow, &ordered);
}

test "handoff commands are unique for review-sensitive routes" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const unique_markers = [_][]const u8{
        "name: Run current Phase 3 export/UAPI C header smoke",
        "run: python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
        "name: Run current Phase 3 export/UAPI layout replay",
        "run: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
        "name: Run current Phase 3 export shim replay",
        "run: zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
        "name: Run current Phase 3 shared tests-root packet",
        "run: zig build phase3-test --build-file zigux/tests/build.zig",
        "name: Run current Phase 3 ABI dump replay",
        "run: zig build phase3-dump --build-file zigux/tests/build.zig",
        "name: Run current Phase 1 shared tests-root smoke",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    };

    for (unique_markers) |marker| {
        try requireOnce(workflow, marker);
    }
}

test "stale phase3 handoff shortcuts stay out of the bootstrap workflow" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const stale_markers = [_][]const u8{
        "zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
        "zig build phase3-export-shim --build-file zigux/tests/build.zig",
        "zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
        "make -C zigux phase3-test",
        "make -C zigux phase1-host-tools-smoke",
    };

    for (stale_markers) |marker| {
        try requireNotContains(workflow, marker);
    }
}

test "phase1 closure and phase3 handoff scripts stay referenced explicitly" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const explicit_files = [_][]const u8{
        "scripts/zigux/validate-phase1-closure.py",
        "scripts/zigux/validate_phase3_selftest.py",
        "scripts/zigux/run-phase3-checks.py",
        "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
        "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "zigux/tests/phase3_export_uapi_layout_build.zig",
        "zigux/tests/phase3_export_shim_build.zig",
        "zigux/tests/phase3_policy_unsafe_build.zig",
        "zigux/tests/phase3_policy_dump_build.zig",
        "zigux/tests/phase3_low_level_wrappers_build.zig",
        "zigux/tests/build.zig",
    };

    for (explicit_files) |marker| {
        try requireContains(workflow, marker);
    }
}
