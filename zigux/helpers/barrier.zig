var fence_word: u8 = 0;

test "phase3 barrier wrappers compile" {
    acquire();
    release();
    full();
}

pub fn acquire() void {
    _ = @atomicLoad(u8, &fence_word, .acquire);
}

pub fn release() void {
    @atomicStore(u8, &fence_word, fence_word, .release);
}

pub fn full() void {
    _ = @atomicRmw(u8, &fence_word, .Xchg, fence_word, .seq_cst);
}
