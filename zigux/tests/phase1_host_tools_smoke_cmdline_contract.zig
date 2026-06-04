const std = @import("std");
const contract_options = @import("contract_options");

const smoke_text = contract_options.smoke_text;
const build_text = contract_options.build_text;

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    const index = std.mem.indexOf(u8, haystack, needle) orelse return error.MarkerMissing;
    try std.testing.expectEqual(index, std.mem.lastIndexOf(u8, haystack, needle).?);
}

test "smoke harness keeps cmdline imported through the shared build root" {
    try requireOnce(smoke_text, "const cmdline = @import(\"cmdline\");");
    try requireOnce(build_text, "const cmdline_module = b.createModule(.{");
    try requireOnce(build_text, ".root_source_file = b.path(\"../../tools/lib/cmdline.zig\"),");
    try requireOnce(build_text, "root_module.addImport(\"cmdline\", cmdline_module);");
    try requireOnce(build_text, "string_module.addImport(\"cmdline\", cmdline_module);");
    try requireOnce(build_text, ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\"),");
    try requireOnce(build_text, ".name = \"phase1-host-tools-smoke\",");
}

test "smoke harness keeps memparse base, suffix, sign, and overflow anchors" {
    try requireContains(smoke_text, "try std.testing.expect(@hasDecl(cmdline, \"memparse\"));");
    try requireContains(smoke_text, "const parsed = cmdline.memparse(\"64K tail\");");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u64, 64 << 10), parsed.value);");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\" tail\", parsed.rest);");
    try requireContains(smoke_text, "const signed = cmdline.memparse(\"-2K tail\");");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), signed.value);");
    try requireContains(smoke_text, "const saturated = cmdline.memparse(\"+9223372036854775808\");");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u64, @intCast(std.math.maxInt(i64))), saturated.value);");
    try requireContains(smoke_text, "const hexadecimal = cmdline.memparse(\"0x20M\");");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u64, 0x20 << 20), hexadecimal.value);");
    try requireContains(smoke_text, "const octal = cmdline.memparse(\"010K\");");
    try requireContains(smoke_text, "try std.testing.expectEqual(@as(u64, 8 << 10), octal.value);");
    try requireContains(smoke_text, "const invalid = cmdline.memparse(\"xyz\");");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\"xyz\", invalid.rest);");
}

test "smoke harness keeps option-token and next-arg quote anchors" {
    try requireContains(smoke_text, "try std.testing.expect(cmdline.parseOptionStr(\"rootwait,quiet\", \"quiet\"));");
    try requireContains(smoke_text, "try std.testing.expect(cmdline.parseOptionStr(\",quiet\", \"\"));");
    try requireContains(smoke_text, "try std.testing.expect(cmdline.parseOptionStr(\"rootwait,,quiet\", \"\"));");
    try requireContains(smoke_text, "try std.testing.expect(!cmdline.parseOptionStr(\"quiet,\", \"\"));");
    try requireContains(smoke_text, "try std.testing.expect(!cmdline.parseOptionStr(\"rootwait,quiet\", \"debug\"));");
    try requireContains(smoke_text, "const keyed = cmdline.nextArg(\"console=ttyS0,115200 root=\\\"/dev/sda1 quiet\\\" panic=-1\")");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\"console\", keyed.param);");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\"root=\\\"/dev/sda1 quiet\\\" panic=-1\", keyed.remaining);");
    try requireContains(smoke_text, "const quoted_pair = cmdline.nextArg(keyed.remaining)");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\"/dev/sda1 quiet\", quoted_pair.value.?);");
    try requireContains(smoke_text, "const quoted = cmdline.nextArg(\"\\\"mode=fast path\\\" tail\")");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\"fast path\", quoted.value.?);");
    try requireContains(smoke_text, "const unterminated = cmdline.nextArg(\"mode=\\\"fast boot\")");
    try requireContains(smoke_text, "try std.testing.expectEqualStrings(\"fast boot\", unterminated.value.?);");
}

test "cmdline smoke contract does not accept stale route or module spellings" {
    try requireMissing(build_text, "root_module.addImport(\"cmd_line\", cmdline_module);");
    try requireMissing(build_text, ".root_source_file = b.path(\"../../scripts/zigux/cmdline.zig\"),");
    try requireMissing(smoke_text, "cmdline.memparse(\"64K\")");
    try requireMissing(smoke_text, "cmdline.nextArg(\"console=ttyS0 panic=-1\")");
}
