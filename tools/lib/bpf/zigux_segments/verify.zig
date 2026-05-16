const std = @import("std");

const logging = @import("logging.zig");
const pin_path = @import("pin_path.zig");
const cpu_mask = @import("cpu_mask.zig");
const type_names = @import("type_names.zig");
const file_path_handle_bridge = @import("file_path_handle_bridge.zig");
const perf_buffer_poll = @import("perf_buffer_poll.zig");
const online_cpu_routing = @import("online_cpu_routing.zig");

fn expectHasDecl(comptime Module: type, comptime decl_name: []const u8) !void {
    try std.testing.expect(@hasDecl(Module, decl_name));
}

test "helper-first tools/lib/bpf Zigux segments compile together and keep their focused tests live" {
    std.testing.refAllDecls(logging);
    std.testing.refAllDecls(pin_path);
    std.testing.refAllDecls(cpu_mask);
    std.testing.refAllDecls(type_names);
    std.testing.refAllDecls(file_path_handle_bridge);
    std.testing.refAllDecls(perf_buffer_poll);
    std.testing.refAllDecls(online_cpu_routing);
}

test "helper-first tools/lib/bpf Zigux segments keep the landed bounded entrypoints explicit" {
    try expectHasDecl(logging, "parseLogLevelSetting");
    try expectHasDecl(logging, "libbpfVersionString");
    try expectHasDecl(logging, "formatLibbpfError");
    try expectHasDecl(pin_path, "buildValidatedSanitizedMapPinPath");
    try expectHasDecl(cpu_mask, "parseCpuMaskString");
    try expectHasDecl(cpu_mask, "parseCpuMaskFromReader");
    try expectHasDecl(cpu_mask, "countPossibleCpus");
    try expectHasDecl(type_names, "libbpfBpfAttachTypeStr");
    try expectHasDecl(type_names, "libbpfBpfMapTypeStr");
    try expectHasDecl(file_path_handle_bridge, "buildProcFdinfoPath");
    try expectHasDecl(file_path_handle_bridge, "parseFdinfoLine");
    try expectHasDecl(file_path_handle_bridge, "applyFdinfoMapInfoLine");
    try expectHasDecl(file_path_handle_bridge, "parseFdinfoMapInfo");
    try expectHasDecl(file_path_handle_bridge, "summarizeFdinfoMapInfo");
    try expectHasDecl(file_path_handle_bridge, "mapReuseObservationFromFdinfo");
    try expectHasDecl(file_path_handle_bridge, "resolveReusedMapName");
    try expectHasDecl(file_path_handle_bridge, "normalizeObservedReuseMapFlags");
    try expectHasDecl(file_path_handle_bridge, "summarizeMapReuseCompatibility");
    try expectHasDecl(file_path_handle_bridge, "isMapReuseCompatible");
    try expectHasDecl(file_path_handle_bridge, "resolveReusePinnedMapAttempt");
    try expectHasDecl(file_path_handle_bridge, "planTokenPreparation");
    try expectHasDecl(perf_buffer_poll, "summarizePollExecution");
    try expectHasDecl(perf_buffer_poll, "resolvePollExecutionResultFromWaitResult");
    try expectHasDecl(perf_buffer_poll, "summarizePollExecutionResultFromWaitResult");
    try expectHasDecl(online_cpu_routing, "advanceOnlineCpuCursor");
    try expectHasDecl(online_cpu_routing, "summarizeNextOnlineCpuRoute");
    try expectHasDecl(online_cpu_routing, "summarizeOnlineCpuRouting");
}
