pub const minor_bits: u5 = 20;
pub const minor_mask: u32 = (@as(u32, 1) << minor_bits) - 1;
pub const max_major: u32 = ~@as(u32, 0) >> minor_bits;

pub const EncodeError = error{
    MajorOutOfRange,
    MinorOutOfRange,
    RangeExhausted,
};

pub fn majorValid(major_id: u32) bool {
    return major_id <= max_major;
}

pub fn minorValid(minor_id: u32) bool {
    return minor_id <= minor_mask;
}

pub fn packMasked(major_id: u32, minor_id: u32) u32 {
    return @as(u32, @truncate((@as(u64, major_id) << minor_bits) | (@as(u64, minor_id) & minor_mask)));
}

pub fn encode(major_id: u32, minor_id: u32) EncodeError!u32 {
    if (!majorValid(major_id)) return error.MajorOutOfRange;
    if (!minorValid(minor_id)) return error.MinorOutOfRange;
    return packMasked(major_id, minor_id);
}

pub fn major(dev: u32) u32 {
    return dev >> minor_bits;
}

pub fn minor(dev: u32) u32 {
    return dev & minor_mask;
}

pub fn rangeFits(first_minor: u32, count: u32) bool {
    if (count == 0) return true;
    if (!minorValid(first_minor)) return false;
    const last = first_minor + count - 1;
    return last <= minor_mask and last >= first_minor;
}

pub fn lastInRange(major_id: u32, first_minor: u32, count: u32) EncodeError!u32 {
    if (!majorValid(major_id)) return error.MajorOutOfRange;
    if (count == 0) return encode(major_id, first_minor);
    if (!rangeFits(first_minor, count)) return error.RangeExhausted;
    return encode(major_id, first_minor + count - 1);
}
