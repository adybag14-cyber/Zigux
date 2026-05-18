const std = @import("std");

const logging = @import("logging.zig");
const perf_buffer_poll = @import("perf_buffer_poll.zig");
const pin_path = @import("pin_path.zig");
const type_names = @import("type_names.zig");

fn expectHasDecl(comptime Module: type, comptime decl_name: []const u8) !void {
    try std.testing.expect(@hasDecl(Module, decl_name));
}

test "materialized tools/lib/bpf Zigux segments compile together and keep their focused tests live" {
    std.testing.refAllDecls(logging);
    std.testing.refAllDecls(perf_buffer_poll);
    std.testing.refAllDecls(pin_path);
    std.testing.refAllDecls(type_names);
}

test "materialized tools/lib/bpf Zigux segments keep their landed bounded entrypoints explicit" {
    try expectHasDecl(logging, "parseLogLevelSetting");
    try expectHasDecl(logging, "shouldLog");
    try expectHasDecl(logging, "shouldLogWithEnv");
    try expectHasDecl(logging, "formatUnrecognizedLogLevel");
    try expectHasDecl(logging, "libbpfMajorVersion");
    try expectHasDecl(logging, "libbpfMinorVersion");
    try expectHasDecl(logging, "libbpfVersionString");
    try expectHasDecl(logging, "libbpfErrorMessage");
    try expectHasDecl(logging, "formatLibbpfError");
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferAttemptIndex");
    try expectHasDecl(perf_buffer_poll, "summarizeReadyBufferAttemptLookup");
    try expectHasDecl(perf_buffer_poll, "resolveReadyBufferAttemptLookup");
    try expectHasDecl(perf_buffer_poll, "summarizePollExecutionResultFromWaitResult");
    try expectHasDecl(perf_buffer_poll, "resolvePollExecutionResultFromWaitResult");
    try expectHasDecl(perf_buffer_poll, "summarizeBufferFdLookup");
    try expectHasDecl(perf_buffer_poll, "resolveBufferFd");
    try expectHasDecl(perf_buffer_poll, "resolveBufferFdLookupReturn");
    try expectHasDecl(perf_buffer_poll, "summarizeBufferWindowLookup");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowMappedSize");
    try expectHasDecl(perf_buffer_poll, "resolveBufferWindowLookupReturn");
    try expectHasDecl(pin_path, "pathnameConcat");
    try expectHasDecl(pin_path, "sanitizePinPath");
    try expectHasDecl(pin_path, "validatePinName");
    try expectHasDecl(pin_path, "validatePinRootPath");
    try expectHasDecl(pin_path, "buildMapPinPath");
    try expectHasDecl(pin_path, "buildValidatedMapPinPath");
    try expectHasDecl(pin_path, "buildSanitizedMapPinPath");
    try expectHasDecl(pin_path, "buildValidatedSanitizedMapPinPath");
    try expectHasDecl(type_names, "libbpfBpfAttachTypeStr");
    try expectHasDecl(type_names, "libbpfBpfMapTypeStr");
    try expectHasDecl(type_names, "libbpfBpfLinkTypeStr");
    try expectHasDecl(type_names, "libbpfBpfProgTypeStr");
    try expectHasDecl(type_names, "formatLibbpfBpfAttachType");
    try expectHasDecl(type_names, "formatLibbpfBpfMapType");
    try expectHasDecl(type_names, "formatLibbpfBpfLinkType");
    try expectHasDecl(type_names, "formatLibbpfBpfProgType");
}
