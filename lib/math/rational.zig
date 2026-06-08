// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub const Rational = struct {
    numerator: usize,
    denominator: usize,
};

pub fn rationalBestApproximation(
    given_numerator: usize,
    given_denominator: usize,
    max_numerator: usize,
    max_denominator: usize,
) Rational {
    var n = given_numerator;
    var d = given_denominator;
    var n0: usize = 0;
    var d0: usize = 1;
    var n1: usize = 1;
    var d1: usize = 0;

    while (true) {
        if (d == 0) break;

        const dp = d;
        const a = n / d;
        d = n % d;
        n = dp;

        const n2 = n0 +% (a *% n1);
        const d2 = d0 +% (a *% d1);

        if (n2 > max_numerator or d2 > max_denominator) {
            var t: usize = std.math.maxInt(usize);

            if (d1 != 0) t = (max_denominator -% d0) / d1;
            if (n1 != 0) t = @min(t, (max_numerator -% n0) / n1);

            const twice_t = t *% 2;
            if (d1 == 0 or twice_t > a or (twice_t == a and (d0 *% dp) > (d1 *% d))) {
                n1 = n0 +% (t *% n1);
                d1 = d0 +% (t *% d1);
            }
            break;
        }

        n0 = n1;
        n1 = n2;
        d0 = d1;
        d1 = d2;
    }

    return .{ .numerator = n1, .denominator = d1 };
}

pub fn rational_best_approximation(
    given_numerator: usize,
    given_denominator: usize,
    max_numerator: usize,
    max_denominator: usize,
    best_numerator: *usize,
    best_denominator: *usize,
) void {
    const best = rationalBestApproximation(given_numerator, given_denominator, max_numerator, max_denominator);
    best_numerator.* = best.numerator;
    best_denominator.* = best.denominator;
}

fn expectRational(want_num: usize, want_den: usize, got: Rational) !void {
    try std.testing.expectEqual(want_num, got.numerator);
    try std.testing.expectEqual(want_den, got.denominator);
}

test "rational Linux KUnit vectors" {
    const cases = [_]struct {
        num: usize,
        den: usize,
        max_num: usize,
        max_den: usize,
        want_num: usize,
        want_den: usize,
    }{
        .{ .num = 1230, .den = 10, .max_num = 100, .max_den = 20, .want_num = 100, .want_den = 1 },
        .{ .num = 34567, .den = 100, .max_num = 120, .max_den = 20, .want_num = 120, .want_den = 1 },
        .{ .num = 1, .den = 30, .max_num = 100, .max_den = 10, .want_num = 0, .want_den = 1 },
        .{ .num = 1, .den = 19, .max_num = 100, .max_den = 10, .want_num = 1, .want_den = 10 },
        .{ .num = 27, .den = 32, .max_num = 16, .max_den = 16, .want_num = 11, .want_den = 13 },
        .{ .num = 1155, .den = 7735, .max_num = 255, .max_den = 255, .want_num = 33, .want_den = 221 },
        .{ .num = 87, .den = 32, .max_num = 70, .max_den = 32, .want_num = 68, .want_den = 25 },
        .{ .num = 14533, .den = 4626, .max_num = 15000, .max_den = 2400, .want_num = 7433, .want_den = 2366 },
    };

    for (cases) |tc| {
        try expectRational(
            tc.want_num,
            tc.want_den,
            rationalBestApproximation(tc.num, tc.den, tc.max_num, tc.max_den),
        );
    }
}

test "rational documented pll-style example" {
    try expectRational(22, 7, rationalBestApproximation(31415, 10000, 255, 31));
}

test "rational C-style out parameters" {
    var n: usize = 0;
    var d: usize = 0;
    rational_best_approximation(1155, 7735, 255, 255, &n, &d);
    try std.testing.expectEqual(@as(usize, 33), n);
    try std.testing.expectEqual(@as(usize, 221), d);
}
