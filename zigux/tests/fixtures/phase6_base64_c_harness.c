// SPDX-License-Identifier: GPL-2.0-only
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

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
    static const unsigned char empty_input[] = "";
    static const unsigned char one_byte[] = "f";
    static const unsigned char two_bytes[] = "fo";
    static const unsigned char foobar[] = "foobar";
    static const unsigned char hello_world[] = "Hello, world!";
    static const unsigned char variant_sample[] = { 0x00, 0xfb, 0xff, 0x7f, 0x80 };
    static const unsigned char invalid_with_nul[] = { 'Z', 'g', 0, '=' };

    static const struct encode_case encode_cases[] = {
        { BASE64_STD, true, empty_input, 0 },
        { BASE64_STD, true, one_byte, 1 },
        { BASE64_STD, true, two_bytes, 2 },
        { BASE64_STD, false, foobar, 6 },
        { BASE64_STD, true, hello_world, 13 },
        { BASE64_URLSAFE, false, variant_sample, sizeof(variant_sample) },
        { BASE64_URLSAFE, true, variant_sample, sizeof(variant_sample) },
        { BASE64_IMAP, false, variant_sample, sizeof(variant_sample) },
        { BASE64_IMAP, true, variant_sample, sizeof(variant_sample) },
    };
    static const struct decode_case decode_cases[] = {
        { BASE64_STD, true, (const unsigned char *)"", 0 },
        { BASE64_STD, true, (const unsigned char *)"Zg==", 4 },
        { BASE64_STD, true, (const unsigned char *)"Zm8=", 4 },
        { BASE64_STD, false, (const unsigned char *)"Zm9vYmFy", 8 },
        { BASE64_STD, true, (const unsigned char *)"SGVsbG8sIHdvcmxkIQ==", 20 },
        { BASE64_URLSAFE, false, (const unsigned char *)"APv_f4A", 7 },
        { BASE64_URLSAFE, true, (const unsigned char *)"APv_f4A=", 8 },
        { BASE64_IMAP, false, (const unsigned char *)"APv,f4A", 7 },
        { BASE64_IMAP, true, (const unsigned char *)"APv,f4A=", 8 },
    };
    static const struct invalid_case invalid_cases[] = {
        { BASE64_STD, true, (const unsigned char *)"Zg=!", 4 },
        { BASE64_STD, true, (const unsigned char *)"Z===", 4 },
        { BASE64_STD, false, (const unsigned char *)"Zm9v====", 8 },
        { BASE64_STD, true, invalid_with_nul, sizeof(invalid_with_nul) },
        { BASE64_URLSAFE, false, (const unsigned char *)"Zg==", 4 },
        { BASE64_IMAP, false, (const unsigned char *)"Zg==", 4 },
    };

    char encoded[128];
    unsigned char decoded[128];
    size_t i;

    for (i = 0; i < sizeof(encode_cases) / sizeof(encode_cases[0]); i++) {
        const struct encode_case *c = &encode_cases[i];
        const int written = base64_encode(c->input, (int)c->input_len, encoded, c->padding, c->variant);
        printf("enc\t%s\t%d\t", variant_name(c->variant), c->padding ? 1 : 0);
        print_hex(c->input, c->input_len);
        putchar('\t');
        print_hex((const unsigned char *)encoded, (size_t)written);
        putchar('\n');
    }

    for (i = 0; i < sizeof(decode_cases) / sizeof(decode_cases[0]); i++) {
        const struct decode_case *c = &decode_cases[i];
        const int written = base64_decode((const char *)c->input, (int)c->input_len, decoded, c->padding, c->variant);
        printf("dec\t%s\t%d\t", variant_name(c->variant), c->padding ? 1 : 0);
        print_hex(c->input, c->input_len);
        putchar('\t');
        print_hex(decoded, written < 0 ? 0U : (size_t)written);
        putchar('\n');
    }

    for (i = 0; i < sizeof(invalid_cases) / sizeof(invalid_cases[0]); i++) {
        const struct invalid_case *c = &invalid_cases[i];
        const int bytes_result = base64_decode((const char *)c->input, (int)c->input_len, decoded, c->padding, c->variant);
        const int decode_result = base64_decode((const char *)c->input, (int)c->input_len, decoded, c->padding, c->variant);
        printf("inv\t%s\t%d\t", variant_name(c->variant), c->padding ? 1 : 0);
        print_hex(c->input, c->input_len);
        printf("\t%s\t%s\n", bytes_result < 0 ? "InvalidInput" : "ok", decode_result < 0 ? "InvalidInput" : "ok");
    }

    return 0;
}
