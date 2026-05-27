const std = @import("std");

const runtime_loader_source = @embedFile("runtime_loader.zig");
const runtime_loader_contract_source = @embedFile("runtime_loader_contract.zig");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectLacks(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(512 * 1024),
    );
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
    try expectContains(runtime_loader_contract_source, "LoadPlan keeps blocked registration-summary surfaces out of the shared request contract");
    try expectContains(runtime_loader_contract_source, "register_api");
    try expectContains(runtime_loader_contract_source, "unregister_api");
    try expectContains(runtime_loader_contract_source, "summary");
    try expectContains(runtime_loader_contract_source, "registration_snapshot");
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
    try expectContains(runtime_loader_source, "PreparedRequest keeps blocked publication and depmod surfaces out of the shared request boundary");
    try expectContains(runtime_loader_source, "\"modinfo\"");
    try expectContains(runtime_loader_source, "\"module_alias\"");
    try expectContains(runtime_loader_source, "\"module_aliases\"");
    try expectContains(runtime_loader_source, "\"modules_alias_path\"");
    try expectContains(runtime_loader_source, "\"module_install_root\"");
    try expectContains(runtime_loader_source, "\"modules_order_path\"");
    try expectContains(runtime_loader_source, "\"modules_builtin_path\"");
    try expectContains(runtime_loader_source, "\"module_symvers_path\"");
    try expectContains(runtime_loader_source, "\"depmod_script\"");
    try expectContains(runtime_loader_source, "\"depmod_manifest\"");
    try expectContains(runtime_loader_source, "\"depmod_aliases\"");
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
        "activation_env:",
        "argv_policy:",
        "command_env:",
        "command_name:",
        "exec_name:",
        "exec_path:",
        "exec_path_env:",
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

test "shared runtime loader surface keeps Phase 8 exec-cmd path controls in their original owner" {
    const exec_cmd_source = try readRepoFile(std.testing.allocator, "tools/lib/subcmd/exec-cmd.zig");
    defer std.testing.allocator.free(exec_cmd_source);

    const exec_cmd_owner_markers = [_][]const u8{
        "pub const Config",
        "exec_name",
        "exec_path",
        "exec_path_env",
        "PERF_EXEC_PATH",
        "setupPathWithPwd",
        "buildDeferredExeclCall",
        "buildDeferredExecvCall",
        "\"PATH\"",
    };
    const loader_absence_markers = [_][]const u8{
        "exec_name:",
        "exec_path:",
        "exec_path_env:",
        "PERF_EXEC_PATH",
        "setupPathWithPwd",
        "buildDeferredExeclCall",
        "buildDeferredExecvCall",
        "\"PATH\"",
    };

    inline for (exec_cmd_owner_markers) |marker| {
        try expectContains(exec_cmd_source, marker);
    }
    inline for (loader_absence_markers) |marker| {
        try expectLacks(runtime_loader_source, marker);
    }
}

test "shared runtime loader surface keeps Phase 8 exec-cmd environment mutation helpers in their original owner" {
    const exec_cmd_source = try readRepoFile(std.testing.allocator, "tools/lib/subcmd/exec-cmd.zig");
    defer std.testing.allocator.free(exec_cmd_source);

    const exec_cmd_owner_markers = [_][]const u8{
        "pub const EnvMap",
        "pub const ExtractArgv0Result",
        "command_name",
        "pub fn execCmdInit",
        "pub fn setArgvExecPath",
        "pub fn setupPath(",
        "pub fn setupPathWithPwd",
        "try env.set(config.exec_path_env, exec_path);",
        "try env.set(\"PATH\", new_path);",
    };
    const loader_absence_markers = [_][]const u8{
        "EnvMap",
        "command_name:",
        "execCmdInit",
        "setArgvExecPath",
        "setupPathWithPwd",
        "try env.set(config.exec_path_env, exec_path);",
        "try env.set(\"PATH\", new_path);",
    };

    inline for (exec_cmd_owner_markers) |marker| {
        try expectContains(exec_cmd_source, marker);
    }
    inline for (loader_absence_markers) |marker| {
        try expectLacks(runtime_loader_source, marker);
        try expectLacks(runtime_loader_contract_source, marker);
    }
}

test "shared runtime loader surface keeps Phase 8 help-display controls in their original owner" {
    const help_source = try readRepoFile(std.testing.allocator, "tools/lib/subcmd/help.zig");
    defer std.testing.allocator.free(help_source);

    const help_owner_markers = [_][]const u8{
        "default_command_prefix",
        "default_terminal_columns",
        "renderPrettyStringList",
        "renderCommandSections",
        "$PATH",
        "terminal_columns",
    };

    inline for (help_owner_markers) |marker| {
        try expectContains(help_source, marker);
        try expectLacks(runtime_loader_source, marker);
        try expectLacks(runtime_loader_contract_source, marker);
    }
}

test "shared runtime loader surface rejects registration-summary bleed-through" {
    const contract_forbidden_field_decls = [_][]const u8{
        "register_api:",
        "unregister_api:",
        "summary:",
        "registration_snapshot:",
    };
    const loader_forbidden_field_decls = [_][]const u8{
        "register_api:",
        "unregister_api:",
        "summary:",
        "registration_snapshot:",
    };

    inline for (contract_forbidden_field_decls) |marker| {
        try expectLacks(runtime_loader_contract_source, marker);
    }
    inline for (loader_forbidden_field_decls) |marker| {
        try expectLacks(runtime_loader_source, marker);
    }
}

test "shared runtime loader surface rejects initcall metadata bleed-through" {
    const contract_forbidden_field_decls = [_][]const u8{
        "module_init:",
        "module_exit:",
        "initcall:",
        "exitcall:",
    };
    const loader_forbidden_field_decls = [_][]const u8{
        "module_init:",
        "module_exit:",
        "initcall:",
        "exitcall:",
    };

    inline for (contract_forbidden_field_decls) |marker| {
        try expectLacks(runtime_loader_contract_source, marker);
    }
    inline for (loader_forbidden_field_decls) |marker| {
        try expectLacks(runtime_loader_source, marker);
    }
}

test "shared runtime loader surface rejects live initcall and runtime registration bleed-through" {
    const contract_forbidden_markers = [_][]const u8{
        "module_init(",
        "module_exit(",
        "register_kretprobe(",
        "unregister_kretprobe(",
        "register_trace_",
        "unregister_trace_",
        "tracepoint_probe_register(",
        "tracepoint_probe_unregister(",
    };
    const loader_forbidden_markers = [_][]const u8{
        "module_init(",
        "module_exit(",
        "register_kretprobe(",
        "unregister_kretprobe(",
        "register_trace_",
        "unregister_trace_",
        "tracepoint_probe_register(",
        "tracepoint_probe_unregister(",
    };

    inline for (contract_forbidden_markers) |marker| {
        try expectLacks(runtime_loader_contract_source, marker);
    }
    inline for (loader_forbidden_markers) |marker| {
        try expectLacks(runtime_loader_source, marker);
    }
}

test "shared runtime loader surface rejects publication and depmod bleed-through" {
    const contract_forbidden_field_decls = [_][]const u8{
        "modinfo:",
        "module_alias:",
        "module_aliases:",
        "modules_alias_path:",
        "module_install_root:",
        "modules_order_path:",
        "modules_builtin_path:",
        "module_symvers_path:",
        "depmod_script:",
        "depmod_manifest:",
        "depmod_aliases:",
    };
    const loader_forbidden_field_decls = [_][]const u8{
        "modinfo:",
        "module_alias:",
        "module_aliases:",
        "modules_alias_path:",
        "module_install_root:",
        "modules_order_path:",
        "modules_builtin_path:",
        "module_symvers_path:",
        "depmod_script:",
        "depmod_manifest:",
        "depmod_aliases:",
    };

    inline for (contract_forbidden_field_decls) |marker| {
        try expectLacks(runtime_loader_contract_source, marker);
    }
    inline for (loader_forbidden_field_decls) |marker| {
        try expectLacks(runtime_loader_source, marker);
    }
}

test "shared runtime loader surface keeps Phase 8 poll ownership in the perf-buffer helper" {
    const perf_buffer_poll_source = try readRepoFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    );
    defer std.testing.allocator.free(perf_buffer_poll_source);

    const phase8_poll_owner_markers = [_][]const u8{
        "pub const WaitClass",
        "pub const PollOutcome",
        "pub const PollExecutionResult",
        "pub fn classifyObservedWaitResult",
        "pub fn classifyWaitClass",
        "pub fn summarizePollExecutionResultFromWaitResult",
    };
    const loader_absence_markers = [_][]const u8{
        "WaitClass",
        "PollOutcome",
        "PollExecutionResult",
        "classifyObservedWaitResult",
        "classifyWaitClass",
        "summarizePollExecutionResultFromWaitResult",
    };

    inline for (phase8_poll_owner_markers) |marker| {
        try expectContains(perf_buffer_poll_source, marker);
    }
    inline for (loader_absence_markers) |marker| {
        try expectLacks(runtime_loader_source, marker);
        try expectLacks(runtime_loader_contract_source, marker);
    }
}

test "shared runtime loader surface rejects task, poll, and event-loop field bleed-through" {
    const forbidden_field_decls = [_][]const u8{
        "task_queue:",
        "task_state:",
        "wait_class:",
        "poll_timeout_ms:",
        "poll_outcome:",
        "poll_summary:",
        "poll_execution:",
        "ready_events:",
        "event_loop:",
        "scheduler_state:",
    };

    inline for (forbidden_field_decls) |marker| {
        try expectLacks(runtime_loader_source, marker);
        try expectLacks(runtime_loader_contract_source, marker);
    }
}

test "shared runtime loader surface rejects scheduler and event-loop substrate markers" {
    const forbidden_markers = [_][]const u8{
        "task_struct",
        "wait_queue",
        "event loop",
        "event_loop",
        "epoll",
        "io_uring",
        "schedule_timeout",
        "wake_up_process",
        "task_work",
        "runqueue",
    };

    inline for (forbidden_markers) |marker| {
        try expectLacks(runtime_loader_source, marker);
        try expectLacks(runtime_loader_contract_source, marker);
    }
}
