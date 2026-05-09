/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum base64_variant {
	BASE64_STD,
	BASE64_URLSAFE,
	BASE64_IMAP,
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
	[BASE64_IMAP] = BASE64_REV_INIT('+', ',')
};

static int base64_encode(const uint8_t *src, int srclen, char *dst, bool padding, enum base64_variant variant)
{
	uint32_t ac = 0;
	char *cp = dst;
	const char *base64_table = base64_tables[variant];

	while (srclen >= 3) {
		ac = src[0] << 16 | src[1] << 8 | src[2];
		*cp++ = base64_table[ac >> 18];
		*cp++ = base64_table[(ac >> 12) & 0x3f];
		*cp++ = base64_table[(ac >> 6) & 0x3f];
		*cp++ = base64_table[ac & 0x3f];
		src += 3;
		srclen -= 3;
	}

	switch (srclen) {
	case 2:
		ac = src[0] << 16 | src[1] << 8;
		*cp++ = base64_table[ac >> 18];
		*cp++ = base64_table[(ac >> 12) & 0x3f];
		*cp++ = base64_table[(ac >> 6) & 0x3f];
		if (padding)
			*cp++ = '=';
		break;
	case 1:
		ac = src[0] << 16;
		*cp++ = base64_table[ac >> 18];
		*cp++ = base64_table[(ac >> 12) & 0x3f];
		if (padding) {
			*cp++ = '=';
			*cp++ = '=';
		}
		break;
	}
	return (int)(cp - dst);
}

static int base64_decode(const char *src, int srclen, uint8_t *dst, bool padding, enum base64_variant variant)
{
	uint8_t *bp = dst;
	int8_t input[4];
	int32_t val;
	const uint8_t *s = (const uint8_t *)src;
	const int8_t *base64_rev_tables = base64_rev_maps[variant];

	while (srclen >= 4) {
		input[0] = base64_rev_tables[s[0]];
		input[1] = base64_rev_tables[s[1]];
		input[2] = base64_rev_tables[s[2]];
		input[3] = base64_rev_tables[s[3]];
		val = input[0] << 18 | input[1] << 12 | input[2] << 6 | input[3];
		if (val < 0) {
			if (!padding || srclen != 4 || s[3] != '=')
				return -1;
			padding = 0;
			srclen = s[2] == '=' ? 2 : 3;
			break;
		}
		*bp++ = val >> 16;
		*bp++ = val >> 8;
		*bp++ = val;
		s += 4;
		srclen -= 4;
	}

	if (!srclen)
		return (int)(bp - dst);
	if (padding || srclen == 1)
		return -1;

	val = (base64_rev_tables[s[0]] << 12) | (base64_rev_tables[s[1]] << 6);
	*bp++ = val >> 10;
	if (srclen == 2) {
		if (val & 0x800003ff)
			return -1;
	} else {
		val |= base64_rev_tables[s[2]];
		if (val & 0x80000003)
			return -1;
		*bp++ = val >> 2;
	}
	return (int)(bp - dst);
}

static void print_encode(const char *label, const uint8_t *input, int len, bool padding, enum base64_variant variant)
{
	char out[128];
	int written = base64_encode(input, len, out, padding, variant);
	out[written] = '\0';
	printf("encode\t%s\t%s\n", label, out);
}

static void print_chars(const char *label, const uint8_t *input, int len, bool padding, enum base64_variant variant)
{
	char out[128];
	int written = base64_encode(input, len, out, padding, variant);
	printf("chars\t%s\t%d\n", label, written);
}

static void print_decode_hex(const char *label, const char *input, bool padding, enum base64_variant variant)
{
	uint8_t out[64];
	int written = base64_decode(input, (int)strlen(input), out, padding, variant);
	int i;

	printf("decode\t%s\t", label);
	for (i = 0; i < written; ++i)
		printf("%02x", out[i]);
	putchar('\n');
}

static void print_bytes(const char *label, const char *input, bool padding, enum base64_variant variant)
{
	uint8_t out[64];
	int written = base64_decode(input, (int)strlen(input), out, padding, variant);
	printf("bytes\t%s\t%d\n", label, written);
}

static void print_invalid(const char *label, const char *input, int len, bool padding, enum base64_variant variant)
{
	uint8_t out[16];
	int written = base64_decode(input, len, out, padding, variant);

	if (written != -1) {
		fprintf(stderr, "expected reject for %s\n", label);
		return;
	}
	printf("invalid\t%s\treject\n", label);
}

int main(void)
{
	static const uint8_t variant_sample[] = { 0x00, 0xfb, 0xff, 0x7f, 0x80 };

	print_encode("std-pad-f", (const uint8_t *)"f", 1, true, BASE64_STD);
	print_encode("std-no-pad-fo", (const uint8_t *)"fo", 2, false, BASE64_STD);
	print_encode("std-pad-hello", (const uint8_t *)"Hello, world!", 13, true, BASE64_STD);
	print_encode("urlsafe-pad-variant", variant_sample, 5, true, BASE64_URLSAFE);
	print_encode("imap-no-pad-variant", variant_sample, 5, false, BASE64_IMAP);

	print_chars("std-pad-f", (const uint8_t *)"f", 1, true, BASE64_STD);
	print_chars("std-no-pad-fo", (const uint8_t *)"fo", 2, false, BASE64_STD);
	print_chars("std-pad-hello", (const uint8_t *)"Hello, world!", 13, true, BASE64_STD);
	print_chars("urlsafe-pad-variant", variant_sample, 5, true, BASE64_URLSAFE);
	print_chars("imap-no-pad-variant", variant_sample, 5, false, BASE64_IMAP);

	print_decode_hex("std-pad-foobar", "Zm9vYmFy", true, BASE64_STD);
	print_decode_hex("std-no-pad-hello", "SGVsbG8sIHdvcmxkIQ", false, BASE64_STD);
	print_decode_hex("urlsafe-pad-variant", "APv_f4A=", true, BASE64_URLSAFE);
	print_decode_hex("imap-no-pad-variant", "APv,f4A", false, BASE64_IMAP);

	print_bytes("std-pad-foobar", "Zm9vYmFy", true, BASE64_STD);
	print_bytes("std-no-pad-hello", "SGVsbG8sIHdvcmxkIQ", false, BASE64_STD);
	print_bytes("urlsafe-pad-variant", "APv_f4A=", true, BASE64_URLSAFE);
	print_bytes("imap-no-pad-variant", "APv,f4A", false, BASE64_IMAP);

	print_invalid("std-pad-noncanonical-pair", "Zh==", 4, true, BASE64_STD);
	print_invalid("urlsafe-pad-noncanonical-pair", "Zh==", 4, true, BASE64_URLSAFE);
	print_invalid("imap-pad-noncanonical-triple", "Zm9=", 4, true, BASE64_IMAP);
	print_invalid("std-no-pad-noncanonical-pair", "Zh", 2, false, BASE64_STD);
	print_invalid("std-no-pad-noncanonical-triple", "Zm9", 3, false, BASE64_STD);
	print_invalid("imap-no-pad-padding-reject", "Zg==", 4, false, BASE64_IMAP);
	return 0;
}
