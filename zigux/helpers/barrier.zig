const std = @import("std");

fn orderedProbe(comptime order: std.builtin.AtomicOrder) void {
    var fence_word = std.atomic.Value(u8).init(0);
    switch (order) {
        .acquire => _ = fence_word.load(.acquire),
        .release => fence_word.store(0, .release),
        .acq_rel => _ = fence_word.swap(0, .acq_rel),
        .seq_cst => _ = fence_word.swap(0, .seq_cst),
        else => @compileError("barrier probes only model acquire, release, acq_rel, and seq_cst ordering"),
    }
}

pub fn acquire() void {
    orderedProbe(.acquire);
}

pub fn release() void {
    orderedProbe(.release);
}

pub fn acquireRelease() void {
    orderedProbe(.acq_rel);
}

pub fn full() void {
    orderedProbe(.seq_cst);
}

test "phase3 barrier wrappers stay local to each barrier probe" {
    acquire();
    release();
    acquireRelease();
    full();
    try std.testing.expect(true);
}
