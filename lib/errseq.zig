// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub const ErrSeq = u32;
pub const MAX_ERRNO: ErrSeq = 4095;
pub const ERRSEQ_SHIFT: u5 = 12;
pub const ERRSEQ_SEEN: ErrSeq = 1 << ERRSEQ_SHIFT;
pub const ERRNO_MASK: ErrSeq = ERRSEQ_SEEN - 1;
pub const ERRSEQ_CTR_INC: ErrSeq = 1 << (ERRSEQ_SHIFT + 1);

pub fn errseq_set(eseq: *ErrSeq, err: i32) ErrSeq {
    const old = eseq.*;
    const errno = errnoMagnitude(err) orelse return old;

    var new = (old & ~(ERRNO_MASK | ERRSEQ_SEEN)) | errno;
    if ((old & ERRSEQ_SEEN) != 0) new +%= ERRSEQ_CTR_INC;
    if (new != old) eseq.* = new;
    return old;
}

pub fn errseq_sample(eseq: *const ErrSeq) ErrSeq {
    const old = eseq.*;
    return if ((old & ERRSEQ_SEEN) == 0) 0 else old;
}

pub fn errseq_check(eseq: *const ErrSeq, since: ErrSeq) i32 {
    const cur = eseq.*;
    if (cur == since) return 0;
    return -@as(i32, @intCast(cur & ERRNO_MASK));
}

pub fn errseq_check_and_advance(eseq: *ErrSeq, since: *ErrSeq) i32 {
    const old = eseq.*;
    if (old == since.*) return 0;

    const new = old | ERRSEQ_SEEN;
    if (new != old) eseq.* = new;
    since.* = new;
    return -@as(i32, @intCast(new & ERRNO_MASK));
}

fn errnoMagnitude(err: i32) ?ErrSeq {
    if (err >= 0) return null;
    const magnitude = -@as(i64, err);
    if (magnitude > MAX_ERRNO) return null;
    return @intCast(magnitude);
}

test "errseq set records unseen errors and sample hides unseen state" {
    var seq: ErrSeq = 0;

    try std.testing.expectEqual(@as(ErrSeq, 0), errseq_set(&seq, -5));
    try std.testing.expectEqual(@as(ErrSeq, 5), seq);
    try std.testing.expectEqual(@as(ErrSeq, 0), errseq_sample(&seq));
    try std.testing.expectEqual(@as(i32, -5), errseq_check(&seq, 0));
}

test "errseq check and advance marks errors as seen" {
    var seq: ErrSeq = 0;
    _ = errseq_set(&seq, -5);
    var since = errseq_sample(&seq);

    try std.testing.expectEqual(@as(ErrSeq, 0), since);
    try std.testing.expectEqual(@as(i32, -5), errseq_check_and_advance(&seq, &since));
    try std.testing.expectEqual(ERRSEQ_SEEN | 5, seq);
    try std.testing.expectEqual(ERRSEQ_SEEN | 5, since);
    try std.testing.expectEqual(@as(i32, 0), errseq_check_and_advance(&seq, &since));
}

test "errseq set bumps counter after seen and rejects invalid errors" {
    var seq: ErrSeq = ERRSEQ_SEEN | 5;

    try std.testing.expectEqual(ERRSEQ_SEEN | 5, errseq_set(&seq, -6));
    try std.testing.expectEqual(ERRSEQ_CTR_INC | 6, seq);
    try std.testing.expectEqual(@as(i32, -6), errseq_check(&seq, ERRSEQ_SEEN | 5));

    try std.testing.expectEqual(ERRSEQ_CTR_INC | 6, errseq_set(&seq, 0));
    try std.testing.expectEqual(ERRSEQ_CTR_INC | 6, errseq_set(&seq, -5000));
    try std.testing.expectEqual(ERRSEQ_CTR_INC | 6, seq);
}

test "errseq sample returns current value once seen" {
    var seq: ErrSeq = 0;
    var since: ErrSeq = 0;

    _ = errseq_set(&seq, -12);
    _ = errseq_check_and_advance(&seq, &since);

    try std.testing.expectEqual(seq, errseq_sample(&seq));
}
