var fence_word: u8 = 0;

test "phase3 barrier wrappers compile" {
    acquire();
    release();
    full();
    acquireRelease();
}

pub fn acquire() void {
    _ = @atomicLoad(u8, &fence_word, .acquire);
}

pub fn release() void {
    @atomicStore(u8, &fence_word, 0, .release);
}

pub fn full() void {
    _ = @atomicRmw(u8, &fence_word, .Xchg, 0, .seq_cst);
}

pub fn acquireRelease() void {
    _ = @atomicRmw(u8, &fence_word, .Xchg, 0, .acq_rel);
}
