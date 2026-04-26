const std = @import("std");
const abi = @import("abi_bindings");

pub const abi_version: u16 = abi.ABI_VERSION;

test "phase3 uapi version follows abi version" {
    try std.testing.expectEqual(abi.ABI_VERSION, abi_version);
}
