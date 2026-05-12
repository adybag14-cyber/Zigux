// SPDX-License-Identifier: GPL-2.0-only
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum base64_variant {
    BASE64_STD = 0,
    BASE64_URLSAFE = 1,
    BASE64_IMAP = 2,
};

static const char base64_tables[][65] = {
    [BASE64_STD] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
    [BASE64_URLSAFE] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_",
    [BASE64_IMAP] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+,",
};

#define INIT_1(v, ch_62, ch_63) \
    [v] = (v) >= 'A' && (v) <= 'Z' ? (v) - 'A' \
        : (v) >= 'a' && (v) <= 'z' ? (v) - 'a' + 26 \
        : (v) >= '0' && (v) <= '9' ? (v) - '0' + 52 \
        : (v) == (ch_62) ? 62 : (v) == (ch_63) ? 63 : -1
#define INIT_2(v, ...) INIT_1(v, __VA_ARGS__), INIT_1((v) + 1, __VA_ARGS__)
#define INIT_4(v, ...) INIT_2(v, __VA_ARGS__), INIT_2((v) + 2, __VA_ARGS__)
#define INIT_8(v, ...) INIT_4(v, __VA_ARGS__), INIT_4((v) + 4, __VA_ARGS__)
#define INIT_16(v, ...) INIT_8(v, __VA_ARGS__), INIT_8((v) + 8, __VA_ARGS__)
#define INIT_32(v, ...) INIT_16(v, __VA_ARGS__), INIT_16((v) + 16, __VA_ARGS__)
#define BASE64_REV_INIT(ch_62, ch_63) { \
    [0 ... 0x1f] = -1, \
    INIT_32(0x20, ch_62, ch_63), \
    INIT_32(0x40, ch_62, ch_63), \
    INIT_32(0x60, ch_62, ch_63), \
    [0x80 ... 0xff] = -1 }

static const int8_t base64_rev_maps[][256] = {
    [BASE64_STD] = BASE64_REV_INIT('+', '/'),
    [BASE64_URLSAFE] = BASE64_REV_INIT('-', '_'),
    [BASE64_IMAP] = BASE64_REV_INIT('+', ','),
};

#undef BASE64_REV_INIT
#undef INIT_32
#undef INIT_16
#undef INIT_8
#undef INIT_4
#undef INIT_2
#undef INIT_1

struct encode_case {
    enum base64_variant variant;
    bool padding;
    const unsigned char *input;
    size_t input_len;
};

struct decode_case {
    enum base64_variant variant;
    bool padding;
    const unsigned char *input;
    size_t input_len;
};

struct invalid_case {
    enum base64_variant variant;
    bool padding;
    const unsigned char *input;
    size_t input_len;
};

#include "phase6_base64_c_generated_cases.inc"

static int base64_encode(const unsigned char *src, int srclen, char *dst, bool padding, enum base64_variant variant)
{
    uint32_t ac = 0;
    char *cp = dst;
    const char *table = base64_tables[variant];

    while (srclen >= 3) {
        ac = ((uint32_t)src[0] << 16) | ((uint32_t)src[1] << 8) | src[2];
        *cp++ = table[ac >> 18];
        *cp++ = table[(ac >> 12) & 0x3f];
        *cp++ = table[(ac >> 6) & 0x3f];
        *cp++ = table[ac & 0x3f];
        src += 3;
        srclen -= 3;
    }

    switch (srclen) {
    case 2:
        ac = ((uint32_t)src[0] << 16) | ((uint32_t)src[1] << 8);
        *cp++ = table[ac >> 18];
        *cp++ = table[(ac >> 12) & 0x3f];
        *cp++ = table[(ac >> 6) & 0x3f];
        if (padding)
            *cp++ = '=';
        break;
    case 1:
        ac = (uint32_t)src[0] << 16;
        *cp++ = table[ac >> 18];
        *cp++ = table[(ac >> 12) & 0x3f];
        if (padding) {
            *cp++ = '=';
            *cp++ = '=';
        }
        break;
    default:
        break;
    }

    return (int)(cp - dst);
}

static int base64_decode(const char *src, int srclen, unsigned char *dst, bool padding, enum base64_variant variant)
{
    unsigned char *bp = dst;
    int8_t input[4];
    int32_t val;
    const unsigned char *s = (const unsigned char *)src;
    const int8_t *rev = base64_rev_maps[variant];

    while (srclen >= 4) {
        input[0] = rev[s[0]];
        input[1] = rev[s[1]];
        input[2] = rev[s[2]];
        input[3] = rev[s[3]];

        val = (input[0] << 18) | (input[1] << 12) | (input[2] << 6) | input[3];

        if (val < 0) {
            if (!padding || srclen != 4 || s[3] != '=')
                return -1;
            padding = false;
            srclen = s[2] == '=' ? 2 : 3;
            break;
        }

        *bp++ = (unsigned char)(val >> 16);
        *bp++ = (unsigned char)(val >> 8);
        *bp++ = (unsigned char)val;

        s += 4;
        srclen -= 4;
    }

    if (!srclen)
        return (int)(bp - dst);
    if (padding || srclen == 1)
        return -1;

    val = (rev[s[0]] << 12) | (rev[s[1]] << 6);
    *bp++ = (unsigned char)(val >> 10);

    if (srclen == 2) {
        if (val & 0x800003ff)
            return -1;
    } else {
        val |= rev[s[2]];
        if (val & 0x80000003)
            return -1;
        *bp++ = (unsigned char)(val >> 2);
    }

    return (int)(bp - dst);
}

static int base64_decoded_length(const char *src, int srclen, bool padding, enum base64_variant variant)
{
    int out_len = 0;
    const unsigned char *s = (const unsigned char *)src;
    const int8_t *rev = base64_rev_maps[variant];

    while (srclen >= 4) {
        const int8_t a = rev[s[0]];
        const int8_t b = rev[s[1]];
        const int8_t c = rev[s[2]];
        const int8_t d = rev[s[3]];

        if (a < 0 || b < 0)
            return -1;

        if (c < 0 || d < 0) {
            if (!padding || srclen != 4 || s[3] != '=')
                return -1;
            padding = false;
            srclen = s[2] == '=' ? 2 : 3;
            break;
        }

        out_len += 3;
        s += 4;
        srclen -= 4;
    }

    if (!srclen)
        return out_len;
    if (padding || srclen == 1)
        return -1;

    {
        int32_t val;

        if (rev[s[0]] < 0 || rev[s[1]] < 0)
            return -1;

        val = (rev[s[0]] << 12) | (rev[s[1]] << 6);
        out_len += 1;

        if (srclen == 2) {
            if (val & 0x800003ff)
                return -1;
            return out_len;
        }

        if (rev[s[2]] < 0)
            return -1;

        val |= rev[s[2]];
        if (val & 0x80000003)
            return -1;
        return out_len + 1;
    }
}

static size_t base64_encoded_length(size_t input_len, bool padding)
{
    const size_t whole_groups = input_len / 3;
    const size_t remainder = input_len % 3;
    size_t out_len = whole_groups * 4;

    if (remainder == 0)
        return out_len;

    return out_len + (padding ? 4 : remainder + 1);
}

static int validate_encode_case_capacity(const struct encode_case *c, size_t case_index, size_t capacity)
{
    const size_t required = base64_encoded_length(c->input_len, c->padding);

    if (required > capacity) {
        fprintf(
            stderr,
            "phase6-base64-c-parity: encode case %zu exceeds fixed harness buffer (%zu > %zu)\n",
            case_index,
            required,
            capacity
        );
        return -1;
    }

    return 0;
}

static int validate_decode_case_capacity(int decoded_length, size_t case_index, size_t capacity)
{
    if (decoded_length < 0) {
        fprintf(
            stderr,
            "phase6-base64-c-parity: decode case %zu failed decoded-length preflight\n",
            case_index
        );
        return -1;
    }

    if ((size_t)decoded_length > capacity) {
        fprintf(
            stderr,
            "phase6-base64-c-parity: decode case %zu exceeds fixed harness buffer (%d > %zu)\n",
            case_index,
            decoded_length,
            capacity
        );
        return -1;
    }

    return 0;
}

static void print_hex(const unsigned char *buf, size_t len)
{
    static const char *hex = "0123456789abcdef";
    size_t i;

    for (i = 0; i < len; i++) {
        putchar(hex[buf[i] >> 4]);
        putchar(hex[buf[i] & 0x0f]);
    }
}

static const char *variant_name(enum base64_variant variant)
{
    switch (variant) {
    case BASE64_STD:
        return "std";
    case BASE64_URLSAFE:
        return "urlsafe";
    case BASE64_IMAP:
        return "imap";
    }
    return "unknown";
}

int main(void)
{
    char encoded[128];
    unsigned char decoded[128];
    size_t i;

    for (i = 0; i < sizeof(encode_cases) / sizeof(encode_cases[0]); i++) {
        const struct encode_case *c = &encode_cases[i];
        const size_t expected_len = base64_encoded_length(c->input_len, c->padding);
        int written;

        if (validate_encode_case_capacity(c, i, sizeof(encoded)) != 0)
            return 1;

        written = base64_encode(c->input, (int)c->input_len, encoded, c->padding, c->variant);
        if ((size_t)written != expected_len) {
            fprintf(
                stderr,
                "phase6-base64-c-parity: encode case %zu length drifted (%d != %zu)\n",
                i,
                written,
                expected_len
            );
            return 1;
        }

        printf("enc\t%s\t%d\t", variant_name(c->variant), c->padding ? 1 : 0);
        print_hex(c->input, c->input_len);
        putchar('\t');
        print_hex((const unsigned char *)encoded, (size_t)written);
        putchar('\n');
    }

    for (i = 0; i < sizeof(decode_cases) / sizeof(decode_cases[0]); i++) {
        const struct decode_case *c = &decode_cases[i];
        const int bytes_result = base64_decoded_length((const char *)c->input, (int)c->input_len, c->padding, c->variant);
        int written;

        if (validate_decode_case_capacity(bytes_result, i, sizeof(decoded)) != 0)
            return 1;

        written = base64_decode((const char *)c->input, (int)c->input_len, decoded, c->padding, c->variant);
        if (written != bytes_result) {
            fprintf(
                stderr,
                "phase6-base64-c-parity: decode case %zu length drifted (%d != %d)\n",
                i,
                written,
                bytes_result
            );
            return 1;
        }

        printf("dec\t%s\t%d\t%d\t", variant_name(c->variant), c->padding ? 1 : 0, bytes_result);
        print_hex(c->input, c->input_len);
        putchar('\t');
        print_hex(decoded, (size_t)written);
        putchar('\n');
    }

    for (i = 0; i < sizeof(invalid_cases) / sizeof(invalid_cases[0]); i++) {
        const struct invalid_case *c = &invalid_cases[i];
        const int bytes_result = base64_decoded_length((const char *)c->input, (int)c->input_len, c->padding, c->variant);
        const int decode_result = base64_decode((const char *)c->input, (int)c->input_len, decoded, c->padding, c->variant);
        printf(
            "inv\t%s\t%d\t",
            variant_name(c->variant),
            c->padding ? 1 : 0
        );
        print_hex(c->input, c->input_len);
        printf("\t%s\t%s\n", bytes_result < 0 ? "InvalidInput" : "ok", decode_result < 0 ? "InvalidInput" : "ok");
    }

    return 0;
}
