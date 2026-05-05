pub fn acquire() void {
    var word: u8 = 0;
    _ = @atomicLoad(u8, &word, .acquire);
}

pub fn release() void {
    var word: u8 = 0;
    @atomicStore(u8, &word, 0, .release);
}

pub fn full() void {
    var word: u8 = 0;
    _ = @atomicRmw(u8, &word, .Xchg, 0, .seq_cst);
}

pub fn acquireRelease() void {
    var word: u8 = 0;
    _ = @atomicLoad(u8, &word, .acquire);
    @atomicStore(u8, &word, 0, .release);
}

test "phase3 barrier wrappers compile" {
    acquire();
    release();
    full();
    acquireRelease();
}
