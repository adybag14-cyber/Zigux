const std = @import("std");
const testing = std.testing;

const tests_readme_root_markers = [_][]const u8{
    "# zigux/tests",
    "This directory is the home of reusable Zigux parity and differential validation harnesses.",
    "hold shared harness logic before subsystem-specific tests spread through the tree",
    "keep product-facing validation code separate from ad hoc experiments",
    "provide the checks for helper parity, ABI assertions, and rollback readiness",
};

const tests_readme_review_packet_markers = [_][]const u8{
    "## Phase 1 host-tools review packet",
    "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`",
    "## Phase 2 review packet",
    "current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`",
    "## Phase 3 shared substrate packet",
    "current shared Phase 3 route: `make -C zigux phase3-validate`",
    "current shared Phase 3 aggregate route: `make -C zigux phase3`",
};

const tests_build_route_markers = [_][]const u8{
    "phase1-host-tools-smoke",
    "phase3-dev-t-starter-packet",
    "phase3-errptr-xarray-starter-packet",
    "phase3-xarray-slot-starter-packet",
    "phase3-bitmap-cpumask-starter-packet",
    "phase3-list-hlist-starter-packet",
    "phase3-test",
    "smoke",
    "test",
};

const tests_build_route_ladder = [_][]const u8{
    "const smoke_step = b.step(",
    "smoke_step.dependOn(&phase1_host_tools_smoke.step);",
    "smoke_step.dependOn(phase3_test_step);",
    "const test_step = b.step(",
    "test_step.dependOn(&phase1_host_tools_smoke.step);",
    "test_step.dependOn(phase3_test_step);",
};

fn expectContainsAll(haystack: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.indexOf(u8, haystack, marker) == null) {
            return error.MissingMarker;
        }
    }
}

fn expectOrdered(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], marker) orelse {
            return error.MarkerOutOfOrder;
        };
        cursor += relative + marker.len;
    }
}

test "Lane 04 root charter keeps differential harness purpose explicit" {
    const current_readme_excerpt =
        \\# zigux/tests
        \\
        \\This directory is the home of reusable Zigux parity and differential validation harnesses.
        \\
        \\Purpose
        \\
        \\  * hold shared harness logic before subsystem-specific tests spread through the tree
        \\  * keep product-facing validation code separate from ad hoc experiments
        \\  * provide the checks for helper parity, ABI assertions, and rollback readiness
    ;

    try expectContainsAll(current_readme_excerpt, &tests_readme_root_markers);
    try expectOrdered(current_readme_excerpt, &tests_readme_root_markers);
}

test "Lane 04 tests README keeps early review packets tied to root routes" {
    const current_readme_route_excerpt =
        \\## Phase 1 host-tools review packet
        \\  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
        \\  * current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`
        \\
        \\## Phase 2 review packet
        \\  * current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`
        \\
        \\## Phase 3 shared substrate packet
        \\  * current shared Phase 3 route: `make -C zigux phase3-validate`
        \\  * current shared Phase 3 aggregate route: `make -C zigux phase3`
    ;

    try expectContainsAll(current_readme_route_excerpt, &tests_readme_review_packet_markers);
    try expectOrdered(current_readme_route_excerpt, &tests_readme_review_packet_markers);
}

test "Lane 04 shared build root keeps smoke and test routes on the harness ladder" {
    const current_build_excerpt =
        \\const phase1_step = b.step(
        \\    "phase1-host-tools-smoke",
        \\    "Run the shared Phase 1 host-tools smoke anchor from zigux/tests",
        \\);
        \\
        \\const phase3_step = b.step(
        \\    "phase3-dev-t-starter-packet",
        \\    "Run the shared Phase 3 dev_t starter packet from zigux/tests",
        \\);
        \\const phase3_errptr_xarray_step = b.step(
        \\    "phase3-errptr-xarray-starter-packet",
        \\    "Run the shared Phase 3 err_ptr/xarray starter packet from zigux/tests",
        \\);
        \\const phase3_xarray_slot_step = b.step(
        \\    "phase3-xarray-slot-starter-packet",
        \\    "Run the shared Phase 3 xarray-slot starter packet from zigux/tests",
        \\);
        \\const phase3_bitmap_cpumask_step = b.step(
        \\    "phase3-bitmap-cpumask-starter-packet",
        \\    "Run the shared Phase 3 bitmap/cpumask starter packet from zigux/tests",
        \\);
        \\const phase3_list_hlist_step = b.step(
        \\    "phase3-list-hlist-starter-packet",
        \\    "Run the shared Phase 3 list/hlist starter packet from zigux/tests",
        \\);
        \\const phase3_test_step = b.step(
        \\    "phase3-test",
        \\    "Run the current shared Phase 3 starter packet bundle from zigux/tests",
        \\);
        \\const smoke_step = b.step(
        \\    "smoke",
        \\    "Run the currently live shared survey anchors from zigux/tests",
        \\);
        \\smoke_step.dependOn(&phase1_host_tools_smoke.step);
        \\smoke_step.dependOn(phase3_test_step);
        \\const test_step = b.step(
        \\    "test",
        \\    "Run the shared Zigux tests-root survey smoke",
        \\);
        \\test_step.dependOn(&phase1_host_tools_smoke.step);
        \\test_step.dependOn(phase3_test_step);
    ;

    try expectContainsAll(current_build_excerpt, &tests_build_route_markers);
    try expectOrdered(current_build_excerpt, &tests_build_route_ladder);
}
