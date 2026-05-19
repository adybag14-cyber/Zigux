const std = @import("std");

pub const abi_version: u32 = 1;
pub const major_bits: u6 = 12;
pub const minor_bits: u6 = 20;
pub const max_major: u32 = (@as(u32, 1) << major_bits) - 1;
pub const max_minor: u32 = (@as(u32, 1) << minor_bits) - 1;

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

pub fn makeDeviceNumber(major: u32, minor: u32) u32 {
    return (major << minor_bits) | (minor & max_minor);
}

pub fn majorFromDeviceNumber(device_number: u32) u32 {
    return device_number >> minor_bits;
}

pub fn minorFromDeviceNumber(device_number: u32) u32 {
    return device_number & max_minor;
}

pub fn fieldsFromDeviceNumber(device_number: u32) Fields {
    return init(
        majorFromDeviceNumber(device_number),
        minorFromDeviceNumber(device_number),
    );
}

pub fn validate(fields: Fields) bool {
    return fields.major <= max_major and fields.minor <= max_minor;
}

pub fn validateRange(start: Fields, end: Fields) bool {
    if (!validate(start) or !validate(end)) return false;
    return start.major < end.major or
        (start.major == end.major and start.minor <= end.minor);
}

comptime {
    std.debug.assert(fields_size == 8);
    std.debug.assert(fields_align == 4);
    std.debug.assert(major_offset == 0);
    std.debug.assert(minor_offset == 4);
    std.debug.assert(major_bits + minor_bits == 32);
}

test "dev_t validation keeps the starter boundary explicit" {
    const valid = init(max_major, max_minor);
    const invalid_major = init(max_major + 1, 0);
    const invalid_minor = init(0, max_minor + 1);
    const later = init(max_major, max_minor);
    const earlier = init(max_major, max_minor - 1);

    try std.testing.expect(validate(valid));
    try std.testing.expect(!validate(invalid_major));
    try std.testing.expect(!validate(invalid_minor));
    try std.testing.expect(validateRange(valid, later));
    try std.testing.expect(!validateRange(valid, earlier));
    try std.testing.expect(!validateRange(valid, invalid_minor));
}

test "dev_t packing stays aligned with the starter boundary" {
    const fields = init(11, 29);
    const encoded = makeDeviceNumber(fields.major, fields.minor);
    const roundtrip = fieldsFromDeviceNumber(encoded);
    const max_encoded = makeDeviceNumber(max_major, max_minor);

    try std.testing.expectEqual(@as(u32, 11), majorFromDeviceNumber(encoded));
    try std.testing.expectEqual(@as(u32, 29), minorFromDeviceNumber(encoded));
    try std.testing.expectEqual(fields.major, roundtrip.major);
    try std.testing.expectEqual(fields.minor, roundtrip.minor);
    try std.testing.expectEqual(max_major, majorFromDeviceNumber(max_encoded));
    try std.testing.expectEqual(max_minor, minorFromDeviceNumber(max_encoded));
}

test "dev_t equality stays field-wise across direct and packed values" {
    const original = init(11, 29);
    const same = init(11, 29);
    const different_major = init(12, 29);
    const different_minor = init(11, 30);
    const roundtrip = fieldsFromDeviceNumber(makeDeviceNumber(original.major, original.minor));
    const max_roundtrip = fieldsFromDeviceNumber(makeDeviceNumber(max_major, max_minor));

    try std.testing.expect(eql(original, same));
    try std.testing.expect(eql(original, roundtrip));
    try std.testing.expect(!eql(original, different_major));
    try std.testing.expect(!eql(original, different_minor));
    try std.testing.expect(eql(init(max_major, max_minor), max_roundtrip));
}
