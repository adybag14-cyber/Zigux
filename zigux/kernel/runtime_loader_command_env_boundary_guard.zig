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
    try expectContains(runtime_loader_contract_source, "LoadPlan keeps Phase 8 command and environment control fields out of the shared request contract");
    try expectContains(runtime_loader_contract_source, "argv_policy");
    try expectContains(runtime_loader_contract_source, "activation_env");
    try expectContains(runtime_loader_contract_source, "command_env");
    try expectContains(runtime_loader_contract_source, "command_name");
    try expectContains(runtime_loader_contract_source, "exec_name");
    try expectContains(runtime_loader_contract_source, "exec_path");
    try expectContains(runtime_loader_contract_source, "exec_path_env");
    try expectContains(runtime_loader_contract_source, "LoadPlan keeps blocked publication and depmod surfaces out of the shared request contract");
    try expectContains(runtime_loader_contract_source, "modinfo");
    try expectContains(runtime_loader_contract_source, "module_alias");
    try expectContains(runtime_loader_contract_source, "module_aliases");
    try expectContains(runtime_loader_contract_source, "modules_alias_path");
    try expectContains(runtime_loader_contract_source, "module_install_root");
    try expectContains(runtime_loader_contract_source, "modules_order_path");
    try expectContains(runtime_loader_contract_source, "modules_builtin_path");
    try expectContains(runtime_loader_contract_source, "module_symvers_path");
    try expectContains(runtime_loader_contract_source, "depmod_script");
    try expectContains(runtime_loader_contract_source, "depmod_manifest");
    try expectContains(runtime_loader_contract_source, "depmod_aliases");

    try expectContains(runtime_loader_source, "pub const PreparedRequest");
    try expectContains(runtime_loader_source, "pub fn prepareRequest");
    try expectContains(runtime_loader_source, "pub fn releaseWithoutSubstrate");
    try expectContains(runtime_loader_source, "waiting_on_runtime_substrate");
    try expectContains(runtime_loader_source, "released_without_substrate");
}

test "shared runtime loader surface rejects argv and environment control bleed-through" {
    const contract_forbidden_markers = [_][]const u8{
        "PERF_EXEC_PATH",
        "setupPathWithPwd",
        "planDeferredExeclCallWithPwd",
        "planDeferredExecvCallWithPwd",
        "\"PATH\"",
        "\"LINES\"",
        "\"COLUMNS\"",
    };
    const loader_forbidden_markers = [_][]const u8{
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

    inline for (contract_forbidden_markers) |marker| {
        try expectLacks(runtime_loader_contract_source, marker);
    }
    inline for (loader_forbidden_markers) |marker| {
        try expectLacks(runtime_loader_source, marker);
    }
}

test "shared runtime loader surface rejects publication and depmod bleed-through" {
    const loader_forbidden_markers = [_][]const u8{
        "modinfo",
        "module_alias",
        "module_aliases",
        "modules_alias_path",
        "module_install_root",
        "modules_order_path",
        "modules_builtin_path",
        "module_symvers_path",
        "depmod_script",
        "depmod_manifest",
        "depmod_aliases",
    };

    inline for (loader_forbidden_markers) |marker| {
        try expectLacks(runtime_loader_source, marker);
    }
}
