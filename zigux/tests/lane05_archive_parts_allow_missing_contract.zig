const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap-archive-parts-packet.yml";
const packet_self_test_step = "- name: Self-test current Lane 05 archive parts packet checker";
const packet_check_step = "- name: Check current Lane 05 archive parts packet";
const allow_missing_command = "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing";
const strict_packet_command = "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py";

const PacketStatus = enum {
    verified,
    missing_allowed,
    rejected,

    fn passesBootstrap(self: PacketStatus) bool {
        return switch (self) {
            .verified, .missing_allowed => true,
            .rejected => false,
        };
    }

    fn requiresPayload(self: PacketStatus) bool {
        return self == .verified;
    }
};

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, workflow_path, allocator, .limited(128 * 1024));
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "archive parts workflow keeps allow-missing scoped to packet check" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "--allow-missing"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, allow_missing_command));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow, strict_packet_command ++ "\n"));
}

test "archive parts workflow keeps checker self-test before temporary packet check" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    const self_test_index = std.mem.indexOf(u8, workflow, packet_self_test_step) orelse return error.MissingPacketSelfTestStep;
    const check_index = std.mem.indexOf(u8, workflow, packet_check_step) orelse return error.MissingPacketCheckStep;
    const allow_missing_index = std.mem.indexOf(u8, workflow, allow_missing_command) orelse return error.MissingAllowMissingCommand;

    try std.testing.expect(self_test_index < check_index);
    try std.testing.expect(check_index < allow_missing_index);
}

test "allow-missing status is the only non-payload bootstrap pass state" {
    try std.testing.expect(PacketStatus.verified.passesBootstrap());
    try std.testing.expect(PacketStatus.missing_allowed.passesBootstrap());
    try std.testing.expect(!PacketStatus.rejected.passesBootstrap());

    try std.testing.expect(PacketStatus.verified.requiresPayload());
    try std.testing.expect(!PacketStatus.missing_allowed.requiresPayload());
    try std.testing.expect(!PacketStatus.rejected.requiresPayload());
}
