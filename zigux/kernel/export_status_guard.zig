const std = @import("std");
const abi = @import("abi_bindings");

pub const ExportStatus = abi.ExportStatus;
pub const Facility = abi.Facility;

pub const KNOWN_STATUS_FLAGS: u16 = abi.STATUS_FLAG_ERROR;

pub const StatusAdmissionError = error{
    UnknownFacility,
    UnknownFlags,
    FlagMismatch,
};

pub const StatusClass = enum(u8) {
    ok,
    error_status,
    unknown_facility,
    unknown_flags,
    flag_mismatch,
};

pub fn statusHasOnlyKnownFlags(status: ExportStatus) bool {
    return (status.flags & ~KNOWN_STATUS_FLAGS) == 0;
}

pub fn statusErrorFlagMatchesCode(status: ExportStatus) bool {
    const flagged_error = (status.flags & abi.STATUS_FLAG_ERROR) != 0;
    return flagged_error == (status.code < 0);
}

pub fn classifyStatus(status: ExportStatus) StatusClass {
    if (!abi.statusHasKnownFacility(status)) return .unknown_facility;
    if (!statusHasOnlyKnownFlags(status)) return .unknown_flags;
    if (!statusErrorFlagMatchesCode(status)) return .flag_mismatch;
    return if (status.code < 0) .error_status else .ok;
}

pub fn statusIsAdmissible(status: ExportStatus) bool {
    return switch (classifyStatus(status)) {
        .ok, .error_status => true,
        .unknown_facility, .unknown_flags, .flag_mismatch => false,
    };
}

pub fn requireAdmissibleStatus(status: ExportStatus) StatusAdmissionError!void {
    return switch (classifyStatus(status)) {
        .ok, .error_status => {},
        .unknown_facility => error.UnknownFacility,
        .unknown_flags => error.UnknownFlags,
        .flag_mismatch => error.FlagMismatch,
    };
}

pub fn canonicalizeStatus(status: ExportStatus) ?ExportStatus {
    const facility = abi.facilityFromInt(status.facility) orelse return null;
    return abi.makeStatus(status.code, facility);
}

test "export status guard classifies admissible and malformed packets" {
    const ok = abi.okStatus(.helpers);
    const negative = abi.makeStatus(-22, .kernel);
    const positive = abi.makeStatus(7, .drivers);
    const unknown_facility = ExportStatus{
        .code = 0,
        .facility = 9,
        .flags = 0,
    };
    const unknown_flags = ExportStatus{
        .code = 0,
        .facility = @intFromEnum(Facility.helpers),
        .flags = 0x8000,
    };
    const flagged_positive = ExportStatus{
        .code = 7,
        .facility = @intFromEnum(Facility.drivers),
        .flags = abi.STATUS_FLAG_ERROR,
    };
    const unflagged_negative = ExportStatus{
        .code = -5,
        .facility = @intFromEnum(Facility.kernel),
        .flags = 0,
    };

    try std.testing.expectEqual(StatusClass.ok, classifyStatus(ok));
    try std.testing.expectEqual(StatusClass.error_status, classifyStatus(negative));
    try std.testing.expectEqual(StatusClass.ok, classifyStatus(positive));
    try std.testing.expectEqual(StatusClass.unknown_facility, classifyStatus(unknown_facility));
    try std.testing.expectEqual(StatusClass.unknown_flags, classifyStatus(unknown_flags));
    try std.testing.expectEqual(StatusClass.flag_mismatch, classifyStatus(flagged_positive));
    try std.testing.expectEqual(StatusClass.flag_mismatch, classifyStatus(unflagged_negative));

    try std.testing.expect(statusIsAdmissible(ok));
    try std.testing.expect(statusIsAdmissible(negative));
    try std.testing.expect(statusIsAdmissible(positive));
    try std.testing.expect(!statusIsAdmissible(unknown_facility));
    try std.testing.expect(!statusIsAdmissible(unknown_flags));
    try std.testing.expect(!statusIsAdmissible(flagged_positive));
    try std.testing.expect(!statusIsAdmissible(unflagged_negative));
}

test "export status guard exposes explicit admission errors" {
    try requireAdmissibleStatus(abi.okStatus(.helpers));
    try requireAdmissibleStatus(abi.makeStatus(-12, .kernel));

    try std.testing.expectError(error.UnknownFacility, requireAdmissibleStatus(.{
        .code = 0,
        .facility = 9,
        .flags = 0,
    }));
    try std.testing.expectError(error.UnknownFlags, requireAdmissibleStatus(.{
        .code = 0,
        .facility = @intFromEnum(Facility.helpers),
        .flags = 0x0004,
    }));
    try std.testing.expectError(error.FlagMismatch, requireAdmissibleStatus(.{
        .code = 0,
        .facility = @intFromEnum(Facility.kernel),
        .flags = abi.STATUS_FLAG_ERROR,
    }));
    try std.testing.expectError(error.FlagMismatch, requireAdmissibleStatus(.{
        .code = -1,
        .facility = @intFromEnum(Facility.kernel),
        .flags = 0,
    }));
}

test "export status guard canonicalizes flags from code and known facility" {
    const flagged_positive = ExportStatus{
        .code = 7,
        .facility = @intFromEnum(Facility.drivers),
        .flags = abi.STATUS_FLAG_ERROR,
    };
    const unflagged_negative = ExportStatus{
        .code = -19,
        .facility = @intFromEnum(Facility.kernel),
        .flags = 0,
    };
    const unknown_flags = ExportStatus{
        .code = 0,
        .facility = @intFromEnum(Facility.helpers),
        .flags = 0x4000,
    };
    const unknown_facility = ExportStatus{
        .code = 0,
        .facility = 99,
        .flags = 0,
    };

    const canonical_positive = canonicalizeStatus(flagged_positive) orelse return error.TestUnexpectedResult;
    const canonical_negative = canonicalizeStatus(unflagged_negative) orelse return error.TestUnexpectedResult;
    const canonical_unknown_flags = canonicalizeStatus(unknown_flags) orelse return error.TestUnexpectedResult;

    try std.testing.expectEqual(StatusClass.flag_mismatch, classifyStatus(flagged_positive));
    try std.testing.expectEqual(StatusClass.ok, classifyStatus(canonical_positive));
    try std.testing.expectEqual(@as(u16, 0), canonical_positive.flags);

    try std.testing.expectEqual(StatusClass.flag_mismatch, classifyStatus(unflagged_negative));
    try std.testing.expectEqual(StatusClass.error_status, classifyStatus(canonical_negative));
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), canonical_negative.flags);

    try std.testing.expectEqual(StatusClass.unknown_flags, classifyStatus(unknown_flags));
    try std.testing.expectEqual(StatusClass.ok, classifyStatus(canonical_unknown_flags));
    try std.testing.expectEqual(@as(u16, 0), canonical_unknown_flags.flags);

    try std.testing.expectEqual(@as(?ExportStatus, null), canonicalizeStatus(unknown_facility));
}
