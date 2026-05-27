/* SPDX-License-Identifier: GPL-2.0-only */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static const char hex_asc[] = "0123456789abcdef";
static const char hex_asc_upper[] = "0123456789ABCDEF";

static const unsigned char data[] = {
	0xbe, 0x32, 0xdb, 0x7b, 0x0a, 0x18, 0x93, 0xb2,
	0x70, 0xba, 0xc4, 0x24, 0x7d, 0x83, 0x34, 0x9b,
	0xa6, 0x9c, 0x31, 0xad, 0x9c, 0x0f, 0xac, 0xe9,
	0x4c, 0xd1, 0x19, 0x99, 0x43, 0xb1, 0xaf, 0x0c,
};

static int is_power_of_two(unsigned int value)
{
	return value && ((value & (value - 1U)) == 0U);
}

static int decode_range(unsigned char ch, unsigned char first, unsigned char last, int bias)
{
	int ch_i = ch;
	int first_i = first;
	int last_i = last;
	unsigned int mask = (unsigned int)((ch_i - last_i - 1) & (first_i - 1 - ch_i)) >> 8;
	return (ch_i - first_i + bias) & (int)mask;
}

static int hex_to_bin(unsigned char ch)
{
	unsigned char cu = ch & 0xdfU;
	return -1 +
	       decode_range(ch, '0', '9', 1) +
	       decode_range(cu, 'A', 'F', 11);
}

static int hex2bin(unsigned char *dst, const char *src, size_t count)
{
	while (count--) {
		int hi = hex_to_bin((unsigned char)*src++);
		int lo;

		if (hi < 0)
			return -1;
		lo = hex_to_bin((unsigned char)*src++);
		if (lo < 0)
			return -1;
		*dst++ = (unsigned char)((hi << 4) | lo);
	}
	return 0;
}

static char *bin2hex(char *dst, const unsigned char *src, size_t count, const char *table)
{
	while (count--) {
		unsigned char byte = *src++;
		*dst++ = table[(byte >> 4) & 0x0fU];
		*dst++ = table[byte & 0x0fU];
	}
	return dst;
}

static uint16_t read_native_u16(const unsigned char *bytes)
{
	uint16_t value;

	memcpy(&value, bytes, sizeof(value));
	return value;
}

static uint32_t read_native_u32(const unsigned char *bytes)
{
	uint32_t value;

	memcpy(&value, bytes, sizeof(value));
	return value;
}

static uint64_t read_native_u64(const unsigned char *bytes)
{
	uint64_t value;

	memcpy(&value, bytes, sizeof(value));
	return value;
}

static size_t hex_dump_to_buffer(const void *buf, size_t len, int rowsize, int groupsize,
				       char *linebuf, size_t linebuflen, bool ascii)
{
	const unsigned char *ptr = buf;
	int ngroups;
	unsigned char ch;
	int j;
	size_t lx = 0;
	int ascii_column;
	int ret;

	if (rowsize != 16 && rowsize != 32)
		rowsize = 16;
	if (len > (size_t)rowsize)
		len = (size_t)rowsize;
	if (!is_power_of_two((unsigned int)groupsize) || groupsize > 8 || groupsize == 0)
		groupsize = 1;
	if ((len % (size_t)groupsize) != 0)
		groupsize = 1;
	ngroups = (int)(len / (size_t)groupsize);
	ascii_column = rowsize * 2 + rowsize / groupsize + 1;

	if (!linebuflen)
		goto overflow1;
	if (!len)
		goto nil;

	if (groupsize == 8) {
		for (j = 0; j < ngroups; j++) {
			ret = snprintf(linebuf + lx, linebuflen - lx, "%s%16.16llx",
				       j ? " " : "",
				       (unsigned long long)read_native_u64(ptr + j * 8));
			if ((size_t)ret >= linebuflen - lx)
				goto overflow1;
			lx += (size_t)ret;
		}
	} else if (groupsize == 4) {
		for (j = 0; j < ngroups; j++) {
			ret = snprintf(linebuf + lx, linebuflen - lx, "%s%8.8x",
				       j ? " " : "",
				       read_native_u32(ptr + j * 4));
			if ((size_t)ret >= linebuflen - lx)
				goto overflow1;
			lx += (size_t)ret;
		}
	} else if (groupsize == 2) {
		for (j = 0; j < ngroups; j++) {
			ret = snprintf(linebuf + lx, linebuflen - lx, "%s%4.4x",
				       j ? " " : "",
				       read_native_u16(ptr + j * 2));
			if ((size_t)ret >= linebuflen - lx)
				goto overflow1;
			lx += (size_t)ret;
		}
	} else {
		for (j = 0; j < (int)len; j++) {
			if (linebuflen < lx + 2)
				goto overflow2;
			ch = ptr[j];
			linebuf[lx++] = hex_asc[(ch >> 4) & 0x0fU];
			if (linebuflen < lx + 2)
				goto overflow2;
			linebuf[lx++] = hex_asc[ch & 0x0fU];
			if (linebuflen < lx + 2)
				goto overflow2;
			linebuf[lx++] = ' ';
		}
		if (j)
			lx--;
	}

	if (!ascii)
		goto nil;

	while ((int)lx < ascii_column) {
		if (linebuflen < lx + 2)
			goto overflow2;
		linebuf[lx++] = ' ';
	}

	for (j = 0; j < (int)len; j++) {
		if (linebuflen < lx + 2)
			goto overflow2;
		ch = ptr[j];
		linebuf[lx++] = (ch < 0x80 && ch >= 0x20 && ch <= 0x7e) ? (char)ch : '.';
	}

nil:
	linebuf[lx] = '\0';
	return lx;

overflow2:
	linebuf[lx++] = '\0';
overflow1:
	return ascii ? (size_t)ascii_column + len : ((size_t)groupsize * 2U + 1U) * (size_t)ngroups - 1U;
}

static void write_hex2bin_case(const char *label, const char *src)
{
	unsigned char decoded[4];
	char encoded[9];

	memset(decoded, 0, sizeof(decoded));
	memset(encoded, 0, sizeof(encoded));

	if (strlen(src) != sizeof(decoded) * 2U) {
		printf("hex2bin\t%s\tInvalidSourceLength\n", label);
		return;
	}
	if (hex2bin(decoded, src, sizeof(decoded)) != 0) {
		printf("hex2bin\t%s\tInvalidHexDigit\n", label);
		return;
	}
	*bin2hex(encoded, decoded, sizeof(decoded), hex_asc) = '\0';
	printf("hex2bin\t%s\t%s\n", label, encoded);
}

static void write_dump_case(const char *label, size_t len, int rowsize, int groupsize, bool ascii)
{
	char line[131];
	size_t required;

	memset(line, 0, sizeof(line));
	required = hex_dump_to_buffer(data, len, rowsize, groupsize, line, sizeof(line), ascii);
	printf("dump\t%s\t%zu\t%s\n", label, required, line);
}

static void write_truncated_dump_case(const char *label, size_t len, int rowsize, int groupsize,
					 bool ascii, size_t buflen)
{
	char line[131];
	size_t required;

	memset(line, 0xaa, sizeof(line));
	required = hex_dump_to_buffer(data, len, rowsize, groupsize, line, buflen, ascii);
	if (!buflen)
		printf("dump-trunc\t%s\t%zu\t\n", label, required);
	else
		printf("dump-trunc\t%s\t%zu\t%s\n", label, required, line);
}

int main(void)
{
	char lower[9];
	char upper[9];

	memset(lower, 0, sizeof(lower));
	memset(upper, 0, sizeof(upper));

	printf("hex-to-bin\tzero\t%d\n", hex_to_bin('0'));
	printf("hex-to-bin\tlower-f\t%d\n", hex_to_bin('f'));
	printf("hex-to-bin\tupper-B\t%d\n", hex_to_bin('B'));
	printf("hex-to-bin\tinvalid-x\t%d\n", hex_to_bin('x'));

	write_hex2bin_case("lower", "be32db7b");
	write_hex2bin_case("mixed", "bE32Db7B");
	write_hex2bin_case("invalid-length", "be32db");
	write_hex2bin_case("invalid-digit", "be32dz7b");

	*bin2hex(lower, data, 4, hex_asc) = '\0';
	printf("bin2hex\tlower\t%s\n", lower);
	*bin2hex(upper, data, 4, hex_asc_upper) = '\0';
	printf("bin2hex-upper\tupper\t%s\n", upper);

	write_dump_case("plain-16-g1", 16, 16, 1, false);
	write_dump_case("ascii-16-g4", 16, 16, 4, true);
	write_dump_case("ascii-32-g2", 32, 32, 2, true);
	write_dump_case("normalized-fallback", 12, 99, 3, true);
	write_dump_case("uneven-group-fallback", 9, 32, 4, false);

	write_truncated_dump_case("ascii-32-g2-buf8", 32, 32, 2, true, 8);
	write_truncated_dump_case("ascii-32-g2-buf113", 32, 32, 2, true, 113);
	write_truncated_dump_case("ascii-16-g4-buf0", 16, 16, 4, true, 0);

	printf("required\tascii-32-g2\t%zu\n",
	       hex_dump_to_buffer(data, 32, 32, 2, NULL, 0, true));
	printf("required\tnormalized-fallback\t%zu\n",
	       hex_dump_to_buffer(data, 12, 99, 3, NULL, 0, true));
	return 0;
}
