const std = @import("std");
const testing = std.testing;

const closure_note_path = "Documentation/zigux/phase1-closure.md";
const validator_path = "scripts/zigux/validate-phase1-closure.py";
const makefile_path = "zigux/Makefile";

const required_makefile_routes = [_][]const u8{
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase3-validate:",
    "phase3:",
    "phase4-validate:",
    "phase6-validate:",
    "phase8-validate:",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "phase14-validate:",
};

const forbidden_phase1_makefile_routes = [_][]const u8{
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContainsOnce(haystack: []const u8, needle: []const u8) !void {
    const count = std.mem.count(u8, haystack, needle);
    if (count != 1) {
        std.debug.print("expected marker once, saw {d}: {s}\n", .{ count, needle });
        return error.MarkerCountMismatch;
    }
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    const count = std.mem.count(u8, haystack, needle);
    if (count != 0) {
        std.debug.print("forbidden marker present {d} time(s): {s}\n", .{ count, needle });
        return error.ForbiddenMarkerPresent;
    }
}

test "closure note parks old Phase 1 Makefile wrappers while naming active closure guards" {
    const closure_note = try readRepoFile(testing.allocator, closure_note_path);
    defer testing.allocator.free(closure_note);

    try requireContainsOnce(
        closure_note,
        "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    );
    try requireContainsOnce(
        closure_note,
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    );
    try requireContainsOnce(
        closure_note,
        "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.",
    );
}

test "closure validator requires later-lane Makefile routes and forbids old Phase 1 routes" {
    const validator_source = try readRepoFile(testing.allocator, validator_path);
    defer testing.allocator.free(validator_source);

    try requireContainsOnce(validator_source, "EXPECTED_MAKEFILE_MARKERS = (");
    try requireContainsOnce(validator_source, "FORBIDDEN_MAKEFILE_MARKERS = (");

    for (required_makefile_routes) |route| {
        var marker_buf: [128]u8 = undefined;
        const marker = try std.fmt.bufPrint(&marker_buf, "\"{s}\"", .{route});
        try requireContainsOnce(validator_source, marker);
    }

    for (forbidden_phase1_makefile_routes) |route| {
        var marker_buf: [128]u8 = undefined;
        const marker = try std.fmt.bufPrint(&marker_buf, "\"{s}\"", .{route});
        try requireContainsOnce(validator_source, marker);
    }

    try requireContainsOnce(
        validator_source,
        "(\"forbidden_phase1_makefile_route\", lambda root: write_text(root / ZIGUX_MAKEFILE_REL, load_text(root, ZIGUX_MAKEFILE_REL) + \"phase1-validate:\\\\n\")),",
    );
}

test "live Makefile exposes only the current closure-validation route posture" {
    const makefile = try readRepoFile(testing.allocator, makefile_path);
    defer testing.allocator.free(makefile);

    for (required_makefile_routes) |route| {
        try requireContainsOnce(makefile, route);
    }

    for (forbidden_phase1_makefile_routes) |route| {
        try requireAbsent(makefile, route);
    }
}
