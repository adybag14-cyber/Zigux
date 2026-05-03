/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <ctype.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static const unsigned char data_b[] = {
	0xbe, 0x32, 0xdb, 0x7b, 0x0a, 0x18, 0x93, 0xb2,
	0x70, 0xba, 0xc4, 0x24, 0x7d, 0x83, 0x34, 0x9b,
	0xa6, 0x9c, 0x31, 0xad, 0x9c, 0x0f, 0xac, 0xe9,
	0x4c, 0xd1, 0x19, 0x99, 0x43, 0xb1, 0xaf, 0x0c,
};

static const char data_a[] = ".2.{....p..$}.4...1.....L...C...";
static const char hex_asc[] = "0123456789abcdef";
static const char hex_asc_upper[] = "0123456789ABCDEF";

static unsigned char hex_asc_hi(unsigned char byte)
{
	return (unsigned char)hex_asc[(byte >> 4) & 0x0f];
}

static unsigned char hex_asc_lo(unsigned char byte)
{
	return (unsigned char)hex_asc[byte & 0x0f];
}

static unsigned char hex_asc_upper_hi(unsigned char byte)
{
	return (unsigned char)hex_asc_upper[(byte >> 4) & 0x0f];
}

static unsigned char hex_asc_upper_lo(unsigned char byte)
{
	return (unsigned char)hex_asc_upper[byte & 0x0f];
}

static int hex_to_bin(unsigned char ch)
{
	if (ch >= '0' && ch <= '9')
		return (int)(ch - '0');
	if (ch >= 'a' && ch <= 'f')
		return (int)(ch - 'a') + 10;
	if (ch >= 'A' && ch <= 'F')
		return (int)(ch - 'A') + 10;
	return -1;
}

static size_t normalized_rowsize(size_t rowsize_input)
{
	return (rowsize_input == 16 || rowsize_input == 32) ? rowsize_input : 16;
}

static size_t normalized_groupsize(size_t len, size_t groupsize_input)
{
	size_t groupsize = groupsize_input;

	if (groupsize == 0 || groupsize > 8 ||
	    (groupsize & (groupsize - 1)) != 0)
		groupsize = 1;
	if (len % groupsize != 0)
		groupsize = 1;
	return groupsize;
}

static size_t hex_dump_line_length(size_t len_input, size_t rowsize_input,
				     size_t groupsize_input, bool ascii)
{
	size_t rowsize = normalized_rowsize(rowsize_input);
	size_t len = len_input < rowsize ? len_input : rowsize;
	size_t groupsize = normalized_groupsize(len, groupsize_input);
	size_t ngroups = groupsize == 0 ? 0 : len / groupsize;

	if (ascii)
		return rowsize * 2 + rowsize / groupsize + 1 + len;
	return ngroups == 0 ? 0 : (groupsize * 2 + 1) * ngroups - 1;
}

static void write_hex_byte(char *linebuf, size_t *pos, unsigned char byte)
{
	linebuf[*pos] = (char)hex_asc_hi(byte);
	linebuf[*pos + 1] = (char)hex_asc_lo(byte);
	*pos += 2;
}

static bool is_little_endian(void)
{
	const uint16_t value = 1;

	return *(const unsigned char *)&value == 1;
}

static void write_group_hex(char *linebuf, size_t *pos,
			      const unsigned char *bytes, size_t len)
{
	size_t index;

	if (is_little_endian() && len > 1) {
		for (index = len; index > 0; index--)
			write_hex_byte(linebuf, pos, bytes[index - 1]);
		return;
	}

	for (index = 0; index < len; index++)
		write_hex_byte(linebuf, pos, bytes[index]);
}

static size_t hex_dump_to_buffer(const unsigned char *buf, size_t len_input,
				   size_t rowsize_input, size_t groupsize_input,
				   char *linebuf, size_t linebuf_len, bool ascii)
{
	size_t rowsize = normalized_rowsize(rowsize_input);
	size_t len = len_input < rowsize ? len_input : rowsize;
	size_t groupsize = normalized_groupsize(len, groupsize_input);
	size_t required = hex_dump_line_length(len_input, rowsize_input, groupsize_input, ascii);
	size_t pos = 0;
	size_t index;
	size_t ascii_column = rowsize * 2 + rowsize / groupsize + 1;

	if (linebuf_len == 0)
		return required;

	if (len == 0) {
		linebuf[0] = '\0';
		return 0;
	}

	for (index = 0; index < len; index += groupsize) {
		if (index != 0 && pos + 1 < linebuf_len)
			linebuf[pos] = ' ';
		if (index != 0)
			pos++;
		if (pos >= linebuf_len)
			continue;
		write_group_hex(linebuf, &pos, buf + index, groupsize);
	}

	if (ascii) {
		while (pos < ascii_column) {
			if (pos + 1 < linebuf_len)
				linebuf[pos] = ' ';
			pos++;
		}
		for (index = 0; index < len; index++) {
			unsigned char byte = buf[index];
			if (pos + 1 < linebuf_len)
				linebuf[pos] = (char)((byte < 0x80 && isprint(byte)) ? byte : '.');
			pos++;
		}
	}

	if (linebuf_len > 0) {
		size_t terminator = required < (linebuf_len - 1) ? required : (linebuf_len - 1);
		linebuf[terminator] = '\0';
	}
	return required;
}

static void bin2hex_lower(const unsigned char *src, size_t len, char *dst)
{
	size_t index;

	for (index = 0; index < len; index++) {
		dst[index * 2] = (char)hex_asc_hi(src[index]);
		dst[index * 2 + 1] = (char)hex_asc_lo(src[index]);
	}
	dst[len * 2] = '\0';
}

static void bin2hex_upper(const unsigned char *src, size_t len, char *dst)
{
	size_t index;

	for (index = 0; index < len; index++) {
		dst[index * 2] = (char)hex_asc_upper_hi(src[index]);
		dst[index * 2 + 1] = (char)hex_asc_upper_lo(src[index]);
	}
	dst[len * 2] = '\0';
}

static void hex2bin(unsigned char *dst, const char *src, size_t len)
{
	size_t index;

	for (index = 0; index < len; index++) {
		int hi = hex_to_bin((unsigned char)src[index * 2]);
		int lo = hex_to_bin((unsigned char)src[index * 2 + 1]);
		dst[index] = (unsigned char)((hi << 4) | lo);
	}
}

int main(void)
{
	char linebuf[160];
	char textbuf[16];
	unsigned char decoded[4];

	printf("hexToBin\t0\t%d\n", hex_to_bin('0'));
	printf("hexToBin\t9\t%d\n", hex_to_bin('9'));
	printf("hexToBin\tA\t%d\n", hex_to_bin('A'));
	printf("hexToBin\tF\t%d\n", hex_to_bin('F'));
	printf("hexToBin\ta\t%d\n", hex_to_bin('a'));
	printf("hexToBin\tf\t%d\n", hex_to_bin('f'));
	printf("hexToBin\tg\t%d\n", hex_to_bin('g'));

	hex2bin(decoded, "Be32dB7b", 4);
	bin2hex_lower(decoded, 4, textbuf);
	printf("hex2bin\tmixed-case\t%s\n", textbuf);

	bin2hex_lower(data_b, 4, textbuf);
	printf("bin2hex\tlower\t%s\n", textbuf);
	bin2hex_upper(data_b, 4, textbuf);
	printf("bin2hex\tupper\t%s\n", textbuf);
	bin2hex_lower(data_b, 2, textbuf);
	bin2hex_upper(data_b + 2, 2, textbuf + 4);
	printf("bin2hex\tappend-mixed\t%s\n", textbuf);

	printf("length\tascii rowsize-16 group-1\t%zu\n",
	       hex_dump_line_length(16, 16, 1, true));
	printf("length\tascii rowsize-16 group-4\t%zu\n",
	       hex_dump_line_length(16, 16, 4, true));
	printf("length\tnormalized rowsize and groupsize fallback\t%zu\n",
	       hex_dump_line_length(16, 7, 3, true));
	printf("length\tplain rowsize-16 group-8\t%zu\n",
	       hex_dump_line_length(16, 16, 8, false));

	hex_dump_to_buffer(data_b, 16, 16, 1, linebuf, sizeof(linebuf), false);
	printf("dump\tplain rowsize-16 group-1\t47\t%s\n", linebuf);
	hex_dump_to_buffer(data_b, 16, 16, 1, linebuf, sizeof(linebuf), true);
	printf("dump\tascii rowsize-16 group-1\t65\t%s\n", linebuf);
	hex_dump_to_buffer(data_b, 16, 16, 2, linebuf, sizeof(linebuf), false);
	printf("dump\tplain rowsize-16 group-2\t39\t%s\n", linebuf);
	hex_dump_to_buffer(data_b, 16, 16, 2, linebuf, sizeof(linebuf), true);
	printf("dump\tascii rowsize-16 group-2\t57\t%s\n", linebuf);
	hex_dump_to_buffer(data_b, 16, 16, 4, linebuf, sizeof(linebuf), false);
	printf("dump\tplain rowsize-16 group-4\t35\t%s\n", linebuf);
	hex_dump_to_buffer(data_b, 16, 16, 4, linebuf, sizeof(linebuf), true);
	printf("dump\tascii rowsize-16 group-4\t53\t%s\n", linebuf);
	hex_dump_to_buffer(data_b, 16, 16, 8, linebuf, sizeof(linebuf), false);
	printf("dump\tplain rowsize-16 group-8\t33\t%s\n", linebuf);
	hex_dump_to_buffer(data_b, 16, 16, 8, linebuf, sizeof(linebuf), true);
	printf("dump\tascii rowsize-16 group-8\t51\t%s\n", linebuf);
	hex_dump_to_buffer(data_b, 32, 32, 2, linebuf, sizeof(linebuf), true);
	printf("dump\tascii rowsize-32 group-2\t113\t%s\n", linebuf);
	hex_dump_to_buffer(data_b, 12, 99, 3, linebuf, sizeof(linebuf), true);
	printf("dump\tnormalized rowsize and groupsize fallback\t61\t%s\n", linebuf);

	memset(linebuf, '#', sizeof(linebuf));
	printf("overflow\tzero-sized caller buffer reports required ascii length\t%zu\t\n",
	       hex_dump_to_buffer(data_b, 16, 7, 3, linebuf, 0, true));
	memset(linebuf, '#', sizeof(linebuf));
	hex_dump_to_buffer(data_b, 4, 16, 1, linebuf, 8, true);
	printf("overflow\tshort ascii buffer truncates but stays NUL terminated\t53\t%s\n", linebuf);
	memset(linebuf, '#', sizeof(linebuf));
	hex_dump_to_buffer(data_b, 16, 16, 2, linebuf, 20, false);
	printf("overflow\tgrouped plain buffer truncates deterministically\t39\t%s\n", linebuf);
	memset(linebuf, '#', sizeof(linebuf));
	hex_dump_to_buffer(data_b, 15, 16, 8, linebuf, 12, true);
	printf("overflow\tnormalized ascii buffer truncates after fallback formatting\t64\t%s\n", linebuf);

	return 0;
}
