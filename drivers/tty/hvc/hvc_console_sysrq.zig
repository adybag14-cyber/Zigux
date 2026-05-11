const std = @import("std");

pub const SysrqHandoffRequest = struct {
    target_vtermno: ?u32,
    byte: u8,
    toggles_sysrq_mode: bool,
    invokes_sysrq_handler: bool,
    is_kernel_console: bool,
    keeps_live_sysrq_execution_out_of_scope: bool = true,
};

pub const SysrqHandoffSnapshot = struct {
    toggles_sysrq_mode: bool,
    invokes_sysrq_handler: bool,
    falls_back_to_literal: bool,
    keeps_live_sysrq_execution_out_of_scope: bool,
};

pub const keeps_live_sysrq_execution_out_of_scope = true;

pub fn summarizeSysrqHandoff(request: SysrqHandoffRequest) SysrqHandoffSnapshot {
    const literal_fallback = !request.is_kernel_console or request.target_vtermno == null;
    return .{
        .toggles_sysrq_mode = request.toggles_sysrq_mode,
        .invokes_sysrq_handler = request.invokes_sysrq_handler and !literal_fallback,
        .falls_back_to_literal = literal_fallback,
        .keeps_live_sysrq_execution_out_of_scope = request.keeps_live_sysrq_execution_out_of_scope and keeps_live_sysrq_execution_out_of_scope,
    };
}

test "phase11 hvc sysrq handoff keeps live execution out of scope" {
    const snapshot = summarizeSysrqHandoff(.{
        .target_vtermno = 0,
        .byte = 0x0f,
        .toggles_sysrq_mode = true,
        .invokes_sysrq_handler = true,
        .is_kernel_console = true,
    });

    try std.testing.expect(snapshot.toggles_sysrq_mode);
    try std.testing.expect(snapshot.invokes_sysrq_handler);
    try std.testing.expect(snapshot.keeps_live_sysrq_execution_out_of_scope);
}
