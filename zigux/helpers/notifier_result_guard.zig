const std = @import("std");
const abi = @import("abi_bindings");

pub const NotifierResult = abi.NotifierResult;

pub const NotifierResultAdmissionKind = enum(u8) {
    done,
    ok,
    stop,
    unknown,
};

pub const NotifierResultAdmissionError = error{
    UnknownNotifierResult,
};

pub const NotifierResultAdmission = struct {
    raw: u32,
    result: ?NotifierResult,
    kind: NotifierResultAdmissionKind,

    pub fn isKnown(self: NotifierResultAdmission) bool {
        return self.result != null;
    }

    pub fn stopsChain(self: NotifierResultAdmission) bool {
        const result = self.result orelse return false;
        return abi.notifierResultStopsChain(result);
    }

    pub fn requireKnown(self: NotifierResultAdmission) NotifierResultAdmissionError!NotifierResult {
        return self.result orelse error.UnknownNotifierResult;
    }
};

pub fn classifyNotifierResult(raw: u32) NotifierResultAdmissionKind {
    return switch (abi.notifierResultFromInt(raw) orelse return .unknown) {
        .done => .done,
        .ok => .ok,
        .stop => .stop,
    };
}

pub fn inspectNotifierResult(raw: u32) NotifierResultAdmission {
    return .{
        .raw = raw,
        .result = abi.notifierResultFromInt(raw),
        .kind = classifyNotifierResult(raw),
    };
}

pub fn notifierResultIsKnown(raw: u32) bool {
    return inspectNotifierResult(raw).isKnown();
}

pub fn notifierResultStopsChainRaw(raw: u32) bool {
    return inspectNotifierResult(raw).stopsChain();
}

pub fn requireKnownNotifierResult(raw: u32) NotifierResultAdmissionError!NotifierResult {
    return inspectNotifierResult(raw).requireKnown();
}

pub fn canonicalizeNotifierResult(raw: u32) NotifierResultAdmissionError!u32 {
    return @intFromEnum(try requireKnownNotifierResult(raw));
}

test "notifier result guard classifies known result values" {
    const done = inspectNotifierResult(@intFromEnum(NotifierResult.done));
    try std.testing.expect(done.isKnown());
    try std.testing.expectEqual(NotifierResultAdmissionKind.done, done.kind);
    try std.testing.expectEqual(NotifierResult.done, try done.requireKnown());
    try std.testing.expect(!done.stopsChain());

    const ok = inspectNotifierResult(@intFromEnum(NotifierResult.ok));
    try std.testing.expect(ok.isKnown());
    try std.testing.expectEqual(NotifierResultAdmissionKind.ok, ok.kind);
    try std.testing.expectEqual(NotifierResult.ok, try ok.requireKnown());
    try std.testing.expect(!ok.stopsChain());

    const stop = inspectNotifierResult(@intFromEnum(NotifierResult.stop));
    try std.testing.expect(stop.isKnown());
    try std.testing.expectEqual(NotifierResultAdmissionKind.stop, stop.kind);
    try std.testing.expectEqual(NotifierResult.stop, try stop.requireKnown());
    try std.testing.expect(stop.stopsChain());
}

test "notifier result guard rejects unknown raw result values" {
    const unknown = inspectNotifierResult(99);

    try std.testing.expect(!unknown.isKnown());
    try std.testing.expectEqual(NotifierResultAdmissionKind.unknown, unknown.kind);
    try std.testing.expect(!unknown.stopsChain());
    try std.testing.expectError(error.UnknownNotifierResult, unknown.requireKnown());
    try std.testing.expectError(error.UnknownNotifierResult, requireKnownNotifierResult(99));
    try std.testing.expectError(error.UnknownNotifierResult, canonicalizeNotifierResult(99));
}

test "notifier result guard exposes raw predicates and canonical values" {
    try std.testing.expect(notifierResultIsKnown(@intFromEnum(NotifierResult.done)));
    try std.testing.expect(notifierResultIsKnown(@intFromEnum(NotifierResult.ok)));
    try std.testing.expect(notifierResultIsKnown(@intFromEnum(NotifierResult.stop)));
    try std.testing.expect(!notifierResultIsKnown(3));

    try std.testing.expect(!notifierResultStopsChainRaw(@intFromEnum(NotifierResult.done)));
    try std.testing.expect(!notifierResultStopsChainRaw(@intFromEnum(NotifierResult.ok)));
    try std.testing.expect(notifierResultStopsChainRaw(@intFromEnum(NotifierResult.stop)));
    try std.testing.expect(!notifierResultStopsChainRaw(3));

    try std.testing.expectEqual(@as(u32, 0), try canonicalizeNotifierResult(0));
    try std.testing.expectEqual(@as(u32, 1), try canonicalizeNotifierResult(1));
    try std.testing.expectEqual(@as(u32, 2), try canonicalizeNotifierResult(2));
}
