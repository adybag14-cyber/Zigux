const std = @import("std");
const build_options = @import("build_options");

const workflow_path = build_options.workflow_path;

const WorkflowError = error{
    DuplicateMarker,
    MissingMarker,
};

const Marker = struct {
    name: []const u8,
    needle: []const u8,
};

const phase2_core_steps = [_]Marker{
    .{ .name = "fixdep gate self-test", .needle = "- name: Self-test current Phase 2 fixdep gate checker" },
    .{ .name = "fixdep gate packet", .needle = "- name: Check current Phase 2 fixdep gate packet" },
    .{ .name = "fixdep parity self-test", .needle = "- name: Self-test current fixdep parity checker" },
    .{ .name = "fixdep parity packet", .needle = "- name: Check current fixdep parity packet" },
    .{ .name = "fixdep unit tests", .needle = "- name: Run current Phase 2 fixdep unit tests" },
    .{ .name = "bootstrap validator self-test", .needle = "- name: Self-test current bootstrap validator" },
    .{ .name = "bootstrap packet validation", .needle = "- name: Validate current bootstrap packet" },
    .{ .name = "kconfig bridge self-test", .needle = "- name: Self-test current kconfig bridge checker" },
    .{ .name = "kconfig bridge packet", .needle = "- name: Check current kconfig bridge packet" },
    .{ .name = "conf bridge unit tests", .needle = "- name: Run current Phase 2 conf bridge unit tests" },
    .{ .name = "confdata bridge unit tests", .needle = "- name: Run current Phase 2 confdata bridge unit tests" },
    .{ .name = "kconfig alignment self-test", .needle = "- name: Self-test current Phase 2 kconfig bridge checker" },
    .{ .name = "kconfig alignment packet", .needle = "- name: Check current Phase 2 kconfig bridge packet" },
    .{ .name = "allconfig helper self-test", .needle = "- name: Self-test current Phase 2 kconfig allconfig helper checker" },
    .{ .name = "allconfig helper packet", .needle = "- name: Check current Phase 2 kconfig allconfig helper packet" },
    .{ .name = "kbuild routes self-test", .needle = "- name: Self-test current Phase 2 kbuild routes checker" },
    .{ .name = "kbuild routes packet", .needle = "- name: Check current Phase 2 kbuild packet" },
    .{ .name = "tests README self-test", .needle = "- name: Self-test current Phase 2 tests README checker" },
    .{ .name = "tests README packet", .needle = "- name: Check current Phase 2 tests README packet" },
    .{ .name = "cross checker self-test", .needle = "- name: Self-test current Phase 2 cross checker" },
    .{ .name = "cross checker packet", .needle = "- name: Check current Phase 2 direct cross-route packet" },
    .{ .name = "cross alignment self-test", .needle = "- name: Self-test current Phase 2 cross selftest alignment checker" },
    .{ .name = "cross alignment packet", .needle = "- name: Check current Phase 2 cross alignment packet" },
    .{ .name = "toolchain pinning self-test", .needle = "- name: Self-test current Phase 2 toolchain pinning checker" },
    .{ .name = "toolchain pinning packet", .needle = "- name: Check current Phase 2 toolchain pinning packet" },
    .{ .name = "toolchain pin-scope self-test", .needle = "- name: Self-test current Phase 2 toolchain pin-scope checker" },
    .{ .name = "toolchain pin-scope packet", .needle = "- name: Check current Phase 2 toolchain pin-scope packet" },
    .{ .name = "bootstrap workflow routes self-test", .needle = "- name: Self-test current Phase 2 bootstrap workflow routes checker" },
    .{ .name = "bootstrap workflow routes packet", .needle = "- name: Check current Phase 2 bootstrap workflow routes packet" },
    .{ .name = "toolchain make route", .needle = "- name: Run current Phase 2 toolchain make route" },
    .{ .name = "tools make route", .needle = "- name: Run current Phase 2 tools make route" },
    .{ .name = "kconfig make route", .needle = "- name: Run current Phase 2 kconfig make route" },
    .{ .name = "fixdep make route", .needle = "- name: Run current Phase 2 fixdep make route" },
    .{ .name = "cross make route", .needle = "- name: Run current Phase 2 cross make route" },
    .{ .name = "required make routes self-test", .needle = "- name: Self-test current Phase 2 required-make-routes checker" },
    .{ .name = "required make routes packet", .needle = "- name: Check current Phase 2 required-make-routes packet" },
    .{ .name = "shared reminder self-test", .needle = "- name: Self-test current Phase 2 shared reminder checker" },
    .{ .name = "shared reminder packet", .needle = "- name: Check current Phase 2 shared reminder packet" },
    .{ .name = "tool manifest self-test", .needle = "- name: Self-test current Phase 2 tool manifest checker" },
    .{ .name = "tool manifest packet", .needle = "- name: Check current Phase 2 tool manifest packet" },
    .{ .name = "artifact tool manifest self-test", .needle = "- name: Self-test current Phase 2 artifact tools manifest checker" },
    .{ .name = "artifact tool manifest packet", .needle = "- name: Check current Phase 2 artifact tools manifest packet" },
    .{ .name = "genksyms bridge self-test", .needle = "- name: Self-test current Phase 2 genksyms bridge checker" },
    .{ .name = "genksyms bridge packet", .needle = "- name: Check current Phase 2 genksyms bridge packet" },
    .{ .name = "genksyms unit replay", .needle = "- name: Run current Phase 2 genksyms unit replay" },
    .{ .name = "genksyms alignment self-test", .needle = "- name: Self-test current Phase 2 genksyms alignment checker" },
    .{ .name = "genksyms alignment packet", .needle = "- name: Check current Phase 2 genksyms alignment packet" },
    .{ .name = "genksyms survey self-test", .needle = "- name: Self-test current Phase 2 genksyms survey guard" },
    .{ .name = "genksyms survey packet", .needle = "- name: Check current Phase 2 genksyms survey packet" },
    .{ .name = "genksyms make route", .needle = "- name: Run current Phase 2 genksyms make route" },
    .{ .name = "validate make route", .needle = "- name: Run current Phase 2 validate make route" },
    .{ .name = "aggregate make route", .needle = "- name: Run current Phase 2 aggregate make route" },
    .{ .name = "tool packet validation", .needle = "- name: Validate current Phase 2 tool packet" },
    .{ .name = "closure validator self-test", .needle = "- name: Self-test current Phase 2 closure validator" },
    .{ .name = "closure packet", .needle = "- name: Check current Phase 2 closure packet" },
    .{ .name = "phase1 direct-owner self-test", .needle = "- name: Self-test current Phase 1 direct-owner checker" },
};

const phase2_core_commands = [_]Marker{
    .{ .name = "fixdep gate self-test", .needle = "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test" },
    .{ .name = "fixdep gate packet", .needle = "run: python3 scripts/zigux/check-phase2-fixdep-gate.py" },
    .{ .name = "fixdep parity self-test", .needle = "run: python3 scripts/zigux/check-fixdep-diff.py --self-test" },
    .{ .name = "fixdep parity packet", .needle = "run: python3 scripts/zigux/check-fixdep-diff.py" },
    .{ .name = "fixdep unit tests", .needle = "run: zig test scripts/zigux/fixdep.zig" },
    .{ .name = "bootstrap self-test", .needle = "run: python3 scripts/zigux/validate-bootstrap.py --self-test" },
    .{ .name = "bootstrap packet", .needle = "run: python3 scripts/zigux/validate-bootstrap.py" },
    .{ .name = "kconfig bridge self-test", .needle = "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test" },
    .{ .name = "kconfig bridge packet", .needle = "run: python3 scripts/zigux/check-kconfig-bridge.py" },
    .{ .name = "conf bridge unit tests", .needle = "run: zig test scripts/zigux/kconfig/conf_bridge.zig" },
    .{ .name = "confdata bridge unit tests", .needle = "run: zig test scripts/zigux/kconfig/confdata_bridge.zig" },
    .{ .name = "phase2 kconfig self-test", .needle = "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test" },
    .{ .name = "phase2 kconfig packet", .needle = "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py" },
    .{ .name = "allconfig self-test", .needle = "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test" },
    .{ .name = "allconfig packet", .needle = "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py" },
    .{ .name = "kbuild self-test", .needle = "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test" },
    .{ .name = "kbuild packet", .needle = "run: python3 scripts/zigux/check-phase2-kbuild-routes.py" },
    .{ .name = "cross packet", .needle = "run: python3 scripts/zigux/check-phase2-cross.py" },
    .{ .name = "toolchain pinning packet", .needle = "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py" },
    .{ .name = "bootstrap workflow routes packet", .needle = "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py" },
    .{ .name = "toolchain make route", .needle = "run: make -C zigux phase2-toolchain" },
    .{ .name = "tools make route", .needle = "run: make -C zigux phase2-tools" },
    .{ .name = "kconfig make route", .needle = "run: make -C zigux phase2-kconfig" },
    .{ .name = "fixdep make route", .needle = "run: make -C zigux phase2-fixdep" },
    .{ .name = "cross make route", .needle = "run: make -C zigux phase2-cross" },
    .{ .name = "required make routes packet", .needle = "run: python3 scripts/zigux/check-phase2-required-make-routes.py" },
    .{ .name = "tool manifest packet", .needle = "run: python3 scripts/zigux/check-phase2-tool-manifest.py" },
    .{ .name = "artifact tools packet", .needle = "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py" },
    .{ .name = "genksyms bridge packet", .needle = "run: python3 scripts/zigux/check-genksyms-bridge.py" },
    .{ .name = "genksyms unit replay", .needle = "run: zig test scripts/zigux/genksyms.zig" },
    .{ .name = "genksyms make route", .needle = "run: make -C zigux phase2-genksyms" },
    .{ .name = "validate make route", .needle = "run: make -C zigux phase2-validate" },
    .{ .name = "aggregate make route", .needle = "run: make -C zigux phase2" },
    .{ .name = "tool packet validation", .needle = "run: python3 scripts/zigux/validate-phase2.py" },
    .{ .name = "closure self-test", .needle = "run: python3 scripts/zigux/validate-phase2-closure.py --self-test" },
    .{ .name = "closure packet", .needle = "run: python3 scripts/zigux/validate-phase2-closure.py" },
    .{ .name = "phase1 direct-owner self-test", .needle = "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test" },
};

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(2 * 1024 * 1024),
    );
}

fn findRunLineAfter(haystack: []const u8, cursor: usize, needle: []const u8) ?usize {
    var offset = cursor;
    while (offset <= haystack.len) {
        const next_newline = std.mem.indexOfScalarPos(u8, haystack, offset, '\n') orelse haystack.len;
        const line = std.mem.trim(u8, haystack[offset..next_newline], " ");
        if (std.mem.eql(u8, line, needle)) {
            return offset;
        }
        if (next_newline == haystack.len) {
            return null;
        }
        offset = next_newline + 1;
    }
    return null;
}

fn findMarkerAfter(haystack: []const u8, cursor: usize, needle: []const u8) ?usize {
    if (std.mem.startsWith(u8, needle, "run: ")) {
        return findRunLineAfter(haystack, cursor, needle);
    }
    const relative_index = std.mem.indexOf(u8, haystack[cursor..], needle) orelse return null;
    return cursor + relative_index;
}

fn requireOrderedUnique(haystack: []const u8, markers: []const Marker) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const absolute_index = findMarkerAfter(haystack, cursor, marker.needle) orelse {
            _ = marker.name;
            return WorkflowError.MissingMarker;
        };
        if (findMarkerAfter(haystack, absolute_index + marker.needle.len, marker.needle) != null) {
            _ = marker.name;
            return WorkflowError.DuplicateMarker;
        }
        cursor = absolute_index + marker.needle.len;
    }
}

fn requirePhase2CoreLadder(workflow: []const u8) !void {
    try requireOrderedUnique(workflow, phase2_core_steps[0..]);
    try requireOrderedUnique(workflow, phase2_core_commands[0..]);
}

test "workflow keeps Phase 2 core steps ordered through closure before Phase 1 resumes" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    try requireOrderedUnique(workflow, phase2_core_steps[0..]);
}

test "workflow keeps Phase 2 core run commands exact and ordered" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    try requireOrderedUnique(workflow, phase2_core_commands[0..]);
}

test "missing closure packet fails closed before Phase 1 direct-owner starts" {
    const workflow =
        \\- name: Run current Phase 2 aggregate make route
        \\  run: make -C zigux phase2
        \\- name: Validate current Phase 2 tool packet
        \\  run: python3 scripts/zigux/validate-phase2.py
        \\- name: Self-test current Phase 2 closure validator
        \\  run: python3 scripts/zigux/validate-phase2-closure.py --self-test
        \\- name: Self-test current Phase 1 direct-owner checker
        \\  run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
    ;
    const closure_handoff = [_]Marker{
        .{ .name = "aggregate make route", .needle = "- name: Run current Phase 2 aggregate make route" },
        .{ .name = "tool packet validation", .needle = "- name: Validate current Phase 2 tool packet" },
        .{ .name = "closure validator self-test", .needle = "- name: Self-test current Phase 2 closure validator" },
        .{ .name = "closure packet", .needle = "- name: Check current Phase 2 closure packet" },
        .{ .name = "phase1 direct-owner self-test", .needle = "- name: Self-test current Phase 1 direct-owner checker" },
    };

    try std.testing.expectError(WorkflowError.MissingMarker, requireOrderedUnique(workflow, closure_handoff[0..]));
}

test "duplicate aggregate route is rejected" {
    const workflow =
        \\- name: Run current Phase 2 aggregate make route
        \\  run: make -C zigux phase2
        \\- name: Run current Phase 2 aggregate make route
        \\  run: make -C zigux phase2
        \\- name: Validate current Phase 2 tool packet
        \\  run: python3 scripts/zigux/validate-phase2.py
        \\- name: Self-test current Phase 2 closure validator
        \\  run: python3 scripts/zigux/validate-phase2-closure.py --self-test
        \\- name: Check current Phase 2 closure packet
        \\  run: python3 scripts/zigux/validate-phase2-closure.py
        \\- name: Self-test current Phase 1 direct-owner checker
        \\  run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
    ;
    const aggregate_route = [_]Marker{
        .{ .name = "aggregate make route", .needle = "- name: Run current Phase 2 aggregate make route" },
    };

    try std.testing.expectError(WorkflowError.DuplicateMarker, requireOrderedUnique(workflow, aggregate_route[0..]));
}
