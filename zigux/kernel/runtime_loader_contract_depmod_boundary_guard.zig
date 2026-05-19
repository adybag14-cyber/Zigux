const std = @import("std");

const contract = @embedFile("runtime_loader_contract.zig");

fn contains(marker: []const u8) bool {
    return std.mem.indexOf(u8, contract, marker) != null;
}

test "phase 9 runtime loader contract keeps depmod boundary proof explicit" {
    try std.testing.expect(contains(
        \\test "shared runtime loader contract keeps registration-summary, publication, and depmod surfaces outside the request contract" {
    ));
    try std.testing.expect(contains(
        \\try std.testing.expect(keepsDepmodBoundaryExplicit());
    ));
    try std.testing.expect(contains(
        \\try std.testing.expect(!typeDeclaresAnyField(LoadPlan, &blocked_depmod_fields));
    ));
    try std.testing.expect(contains(
        \\try std.testing.expect(!typeDeclaresAnyField(PreparedRequest, &blocked_depmod_fields));
    ));
    try std.testing.expect(contains(
        \\try std.testing.expectEqual(@as(usize, 3), blocked_depmod_fields.len);
    ));
    try std.testing.expect(contains(
        \\try std.testing.expect(std.mem.eql(u8, blocked_depmod_fields[2], "depmod_aliases"));
    ));
}

test "phase 9 runtime loader contract keeps source-local depmod review proof explicit" {
    try std.testing.expect(contains(
        \\test "shared runtime loader contract can prove source-local publication and depmod metadata stay outside shared requests" {
    ));
    try std.testing.expect(contains(
        \\pub fn keepsSourceLocalDepmodBoundaryExplicit(comptime SourcePlan: type) bool {
    ));
    try std.testing.expect(contains(
        \\return keepsSourceLocalFieldFamilyOutsideSharedRequest(SourcePlan, &blocked_depmod_fields);
    ));
}
