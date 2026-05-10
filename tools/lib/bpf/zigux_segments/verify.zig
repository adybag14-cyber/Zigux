const std = @import("std");

const logging = @import("logging.zig");
const pin_path = @import("pin_path.zig");
const cpu_mask = @import("cpu_mask.zig");
const type_names = @import("type_names.zig");
const file_path_handle_bridge = @import("file_path_handle_bridge.zig");
const perf_buffer_poll = @import("perf_buffer_poll.zig");

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
}

test "helper-first tools/lib/bpf Zigux segments keep the landed bounded entrypoints explicit" {
    try expectHasDecl(logging, "resolveMinPrintLevel");
    try expectHasDecl(logging, "libbpfVersionString");
    try expectHasDecl(logging, "formatErrorString");

    try expectHasDecl(pin_path, "buildValidatedSanitizedMapPinPath");

    try expectHasDecl(cpu_mask, "parseCpuMaskString");
    try expectHasDecl(cpu_mask, "parseCpuMaskFromReader");
    try expectHasDecl(cpu_mask, "countPossibleCpus");

    try expectHasDecl(type_names, "libbpfBpfAttachTypeStr");
    try expectHasDecl(type_names, "libbpfBpfLinkTypeStr");
    try expectHasDecl(type_names, "libbpfBpfMapTypeStr");
    try expectHasDecl(type_names, "libbpfBpfProgTypeStr");

    try expectHasDecl(file_path_handle_bridge, "buildProcFdinfoPath");
    try expectHasDecl(file_path_handle_bridge, "buildProcFdPath");
    try expectHasDecl(file_path_handle_bridge, "parseFdinfoMapInfo");
    try expectHasDecl(file_path_handle_bridge, "summarizeFdinfoMapInfo");
    try expectHasDecl(file_path_handle_bridge, "mapReuseObservationFromFdinfo");
    try expectHasDecl(file_path_handle_bridge, "summarizeMapReuseCompatibility");
    try expectHasDecl(file_path_handle_bridge, "resolveReusePinnedMapAttempt");
    try expectHasDecl(file_path_handle_bridge, "planTokenPreparation");

    try expectHasDecl(perf_buffer_poll, "lookupBufferFd");
    try expectHasDecl(perf_buffer_poll, "resolveBufferFdResultFromSlots");
    try expectHasDecl(perf_buffer_poll, "lookupBufferWindow");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowResultFromSlots");
    try expectHasDecl(perf_buffer_poll, "lookupSignaledBufferIndex");
    try expectHasDecl(perf_buffer_poll, "resolveSignaledBufferIndexResultFromSlots");
    try expectHasDecl(perf_buffer_poll, "lookupReadyBufferIndex");
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferIndexResultFromSlots");
    try expectHasDecl(perf_buffer_poll, "summarizePollExecution");
    try expectHasDecl(perf_buffer_poll, "resolvePollExecutionResult");
    try expectHasDecl(perf_buffer_poll, "summarizePollExecutionResultFromWaitResult");
}
