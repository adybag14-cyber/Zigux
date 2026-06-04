const std = @import("std");
const genksyms_crc = @import("genksyms_crc.zig");

test "partialCrc32 composes across every split with an explicit seed" {
    const payload = "VMLINUX_SYMBOL_STR(sample_symbol)\x00\x1f\x7f\x80\xff\r\nquoted\\name";
    const seed: u32 = 0x1357_9bdf;
    const whole = genksyms_crc.partialCrc32(payload, seed);

    var split: usize = 0;
    while (split <= payload.len) : (split += 1) {
        const prefix_state = genksyms_crc.partialCrc32(payload[0..split], seed);
        const split_state = genksyms_crc.partialCrc32(payload[split..], prefix_state);
        try std.testing.expectEqual(whole, split_state);
    }
}

test "partialCrc32One matches slice replay for every byte under a non-default seed" {
    const payload = "crc-seed-replay:\x00\x08\x0c\x1f\x7f\x80\xff";
    const seed: u32 = 0x2468_ace0;
    var rolling = seed;

    for (payload, 0..) |byte, index| {
        rolling = genksyms_crc.partialCrc32One(byte, rolling);
        try std.testing.expectEqual(
            genksyms_crc.partialCrc32(payload[0 .. index + 1], seed),
            rolling,
        );
    }

    try std.testing.expectEqual(genksyms_crc.partialCrc32(payload, seed), rolling);
}
