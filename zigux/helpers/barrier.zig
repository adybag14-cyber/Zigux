fn fenceProbe() *u8 {
    var word: u8 = 0;
    return &word;
}

pub fn acquire() void {
    _ = @atomicLoad(u8, fenceProbe(), .acquire);
}

pub fn release() void {
    @atomicStore(u8, fenceProbe(), 0, .release);
}

pub fn full() void {
    _ = @atomicRmw(u8, fenceProbe(), .Xchg, 0, .seq_cst);
}

pub fn acquireRelease() void {
    _ = @atomicLoad(u8, fenceProbe(), .acquire);
    @atomicStore(u8, fenceProbe(), 0, .release);
}

test "phase3 barrier wrappers compile" {
    acquire();
    release();
    full();
    acquireRelease();
}
