const std = @import("std");
const testing = std.testing;

pub const abi_version: u32 = 1;

pub const Fields = extern struct {
    major: u32,
    minor: u32,
};

pub const fields_size: usize = @sizeOf(Fields);
pub const fields_align: usize = @alignOf(Fields);
pub const major_offset: usize = @offsetOf(Fields, "major");
pub const minor_offset: usize = @offsetOf(Fields, "minor");

pub fn init(major: u32, minor: u32) Fields {
    return .{
        .major = major,
        .minor = minor,
    };
}

pub fn eql(left: Fields, right: Fields) bool {
    return left.major == right.major and left.minor == right.minor;
}

comptime {
    std.debug.assert(fields_size == 8);
    std.debug.assert(fields_align == 4);
    std.debug.assert(major_offset == 0);
    std.debug.assert(minor_offset == 4);
}

test "dev_t uapi init keeps the current field layout explicit" {
    const fields = init(11, 29);

    try testing.expectEqual(@as(u32, 1), abi_version);
    try testing.expectEqual(@as(usize, 8), fields_size);
    try testing.expectEqual(@as(usize, 4), fields_align);
    try testing.expectEqual(@as(usize, 0), major_offset);
    try testing.expectEqual(@as(usize, 4), minor_offset);
    try testing.expectEqual(@as(u32, 11), fields.major);
    try testing.expectEqual(@as(u32, 29), fields.minor);
}

test "dev_t uapi equality stays field based" {
    const left = init(7, 3);
    const same = init(7, 3);
    const different_major = init(8, 3);
    const different_minor = init(7, 4);

    try testing.expect(eql(left, same));
    try testing.expect(!eql(left, different_major));
    try testing.expect(!eql(left, different_minor));
}
