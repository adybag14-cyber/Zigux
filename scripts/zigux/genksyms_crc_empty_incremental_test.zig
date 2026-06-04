const std = @import("std");
const crc = @import("genksyms_crc.zig");

test "partialCrc32 treats empty chunks as state-preserving boundaries" {
    const seed: u32 = 0xffff_ffff;
    const prefix = "VMLINUX_SYMBOL_STR(";
    const symbol = "empty_chunk_symbol";
    const suffix = ")";

    const direct_state = crc.partialCrc32(prefix ++ symbol ++ suffix, seed);
    const split_state = crc.partialCrc32(
        suffix,
        crc.partialCrc32(
            "",
            crc.partialCrc32(
                symbol,
                crc.partialCrc32(
                    "",
                    crc.partialCrc32(prefix, seed),
                ),
            ),
        ),
    );

    try std.testing.expectEqual(seed, crc.partialCrc32("", seed));
    try std.testing.expectEqual(direct_state, split_state);
    try std.testing.expectEqual(crc.crc32(prefix ++ symbol ++ suffix), split_state ^ 0xffff_ffff);
}

test "partialCrc32One resumes identically after empty chunk boundaries" {
    const packet = "struct module_version_attribute";
    var state = crc.partialCrc32(packet[0..6], 0xffff_ffff);
    state = crc.partialCrc32("", state);
    state = crc.partialCrc32(packet[6..14], state);
    state = crc.partialCrc32("", state);
    for (packet[14..]) |byte| {
        state = crc.partialCrc32One(byte, state);
        state = crc.partialCrc32("", state);
    }

    try std.testing.expectEqual(crc.crc32(packet), state ^ 0xffff_ffff);
}
