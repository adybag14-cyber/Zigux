const std = @import("std");

const runtime_loader_source = @embedFile("runtime_loader.zig");
const runtime_loader_contract_source = @embedFile("runtime_loader_contract.zig");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectLacks(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "shared runtime loader surface keeps the bounded request contract explicit" {
    try expectContains(runtime_loader_contract_source, "pub const LoadPlan = struct");
    try expectContains(runtime_loader_contract_source, "module_name");
    try expectContains(runtime_loader_contract_source, "anchor");
    try expectContains(runtime_loader_contract_source, "entry_symbol");
    try expectContains(runtime_loader_contract_source, "exit_symbol");
    try expectContains(runtime_loader_contract_source, "requires_runtime_substrate");
    try expectContains(runtime_loader_contract_source, "provides_selftest_hook");
    try expectContains(runtime_loader_contract_source, "allocator_handoff");
    try expectContains(runtime_loader_contract_source, "init_flow");
    try expectContains(runtime_loader_contract_source, "pub const RequestState");

    try expectContains(runtime_loader_source, "pub const PreparedRequest");
    try expectContains(runtime_loader_source, "pub fn prepareRequest");
    try expectContains(runtime_loader_source, "pub fn releaseWithoutSubstrate");
    try expectContains(runtime_loader_source, "waiting_on_runtime_substrate");
    try expectContains(runtime_loader_source, "released_without_substrate");
}

test "shared runtime loader surface rejects argv and environment control bleed-through" {
    const forbidden_markers = [_][]const u8{
        "argv_policy",
        "activation_env",
        "command_env",
        "command_name",
        "exec_name",
        "exec_path",
        "exec_path_env",
        "PERF_EXEC_PATH",
        "setupPathWithPwd",
        "planDeferredExeclCallWithPwd",
        "planDeferredExecvCallWithPwd",
        "\"PATH\"",
        "\"LINES\"",
        "\"COLUMNS\"",
    };

    inline for (forbidden_markers) |marker| {
        try expectLacks(runtime_loader_contract_source, marker);
        try expectLacks(runtime_loader_source, marker);
    }
}
