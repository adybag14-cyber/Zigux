const std = @import("std");
const data = @import("phase1_closure_makefile_boundary_data");

const ContractError = error{ MissingMarker, UnexpectedPhase1Route };

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) return ContractError.MissingMarker;
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) != null) return ContractError.UnexpectedPhase1Route;
}

fn expectTargetAbsent(makefile: []const u8, target: []const u8) !void {
    var target_with_colon = [_]u8{0} ** 64;
    if (target.len + 1 > target_with_colon.len) @panic("target literal too long");
    @memcpy(target_with_colon[0..target.len], target);
    target_with_colon[target.len] = ':';
    const target_line = target_with_colon[0 .. target.len + 1];

    if (std.mem.startsWith(u8, makefile, target_line)) return ContractError.UnexpectedPhase1Route;

    var newline_prefixed = [_]u8{0} ** 65;
    newline_prefixed[0] = '\n';
    @memcpy(newline_prefixed[1 .. target.len + 1], target);
    newline_prefixed[target.len + 1] = ':';
    if (std.mem.indexOf(u8, makefile, newline_prefixed[0 .. target.len + 2]) != null) {
        return ContractError.UnexpectedPhase1Route;
    }
}

test "closure note keeps Phase 1 parked behind route summary guard" {
    try expectContains(data.closure_note, "`PHASE1_STATUS=parked`");
    try expectContains(data.closure_note, "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`");
    try expectContains(data.closure_note, "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`");
    try expectContains(data.closure_note, "route-summary checker stays an adjacent workflow and Makefile guard");
}

test "closure validator documents the Makefile boundary" {
    try expectContains(data.closure_validator, "ROUTE_SUMMARY_CHECKER_REL = Path(\"scripts/zigux/check-phase1-route-summary-counts.py\")");
    try expectContains(data.closure_validator, "ZIGUX_MAKEFILE_REL = Path(\"zigux/Makefile\")");
    try expectContains(data.closure_validator, "EXPECTED_MAKEFILE_MARKERS = (");
    try expectContains(data.closure_validator, "FORBIDDEN_MAKEFILE_MARKERS = (");
    try expectContains(data.closure_validator, "\"phase1-validate:\"");
    try expectContains(data.closure_validator, "\"phase1-test:\"");
    try expectContains(data.closure_validator, "\"phase1-bench:\"");
    try expectContains(data.closure_validator, "\"phase1:\"");
    try expectContains(data.closure_validator, "\"phase2-toolchain:\"");
    try expectContains(data.closure_validator, "\"phase3-validate:\"");
    try expectContains(data.closure_validator, "\"phase14-validate:\"");
}

test "Makefile exposes only the narrow Phase 1 route summary target" {
    try expectContains(data.makefile, ".PHONY: phase1-route-summary");
    try expectContains(data.makefile, "phase1-route-summary:\n");
    try expectContains(data.makefile, "scripts/zigux/check-phase1-route-summary-counts.py --self-test");
    try expectContains(data.makefile, "scripts/zigux/check-phase1-route-summary-counts.py\n");

    try expectTargetAbsent(data.makefile, "phase1-validate");
    try expectTargetAbsent(data.makefile, "phase1-test");
    try expectTargetAbsent(data.makefile, "phase1-bench");
    try expectTargetAbsent(data.makefile, "phase1");
    try expectNotContains(data.makefile, " phase1-validate ");
    try expectNotContains(data.makefile, " phase1-test ");
    try expectNotContains(data.makefile, " phase1-bench ");
}
