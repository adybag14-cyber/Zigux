/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <stdint.h>
#include <stdio.h>

static uint32_t csum_add(uint32_t sum, uint32_t addend)
{
	uint32_t result = sum + addend;

	return result + (result < addend);
}

static uint32_t csum_sub(uint32_t sum, uint32_t addend)
{
	return csum_add(sum, ~addend);
}

static uint32_t csum_shift(uint32_t sum, int offset)
{
	if (offset & 1)
		return (sum >> 8) | (sum << 24);
	return sum;
}

static uint32_t csum_block_add(uint32_t sum, uint32_t other, int offset)
{
	return csum_add(sum, csum_shift(other, offset));
}

static uint32_t csum_negate(uint32_t sum)
{
	return 0U - sum;
}

static uint16_t csum_from32to16(uint32_t sum)
{
	sum += (sum >> 16) | (sum << 16);
	return (uint16_t)(sum >> 16);
}

static uint16_t csum_fold(uint32_t sum)
{
	return (uint16_t)~csum_from32to16(sum);
}

static uint32_t csum_from64to32(uint64_t sum)
{
	sum = (sum & 0xffffffffULL) + (sum >> 32);
	sum = (sum & 0xffffffffULL) + (sum >> 32);
	return (uint32_t)sum;
}

static uint32_t csum_unfold(uint16_t sum)
{
	return sum;
}

static uint16_t csum16_add(uint16_t sum, uint16_t addend)
{
	uint16_t result = (uint16_t)(sum + addend);

	return (uint16_t)(result + (result < addend));
}

static uint16_t csum16_sub(uint16_t sum, uint16_t addend)
{
	return csum16_add(sum, (uint16_t)~addend);
}

static void csum_replace_by_diff(uint16_t *sum, uint32_t diff)
{
	*sum = csum_fold(csum_add(diff, ~csum_unfold(*sum)));
}

static void csum_replace4(uint16_t *sum, uint32_t from, uint32_t to)
{
	uint32_t tmp = csum_sub(~csum_unfold(*sum), from);

	*sum = csum_fold(csum_add(tmp, to));
}

static void csum_replace2(uint16_t *sum, uint16_t old, uint16_t new_value)
{
	*sum = (uint16_t)~csum16_add(csum16_sub((uint16_t)~(*sum), old), new_value);
}

static void csum_replace(uint32_t *sum, uint32_t old, uint32_t new_value)
{
	*sum = csum_add(csum_sub(*sum, old), new_value);
}

static uint32_t partial_bytes(const unsigned char *bytes, size_t len, uint32_t seed)
{
	uint64_t acc = seed;
	size_t index = 0;

	while (index + 1 < len) {
		acc += ((uint64_t)bytes[index] << 8) | bytes[index + 1];
		index += 2;
	}

	if (index < len)
		acc += (uint64_t)bytes[index] << 8;

	while ((acc >> 16) != 0)
		acc = (acc & 0xffff) + (acc >> 16);

	return (uint32_t)acc;
}

static uint16_t compute_bytes(const unsigned char *bytes, size_t len)
{
	return (uint16_t)~partial_bytes(bytes, len, 0);
}

static uint32_t csum_tcpudp_nofold(uint32_t saddr, uint32_t daddr,
				   uint32_t len, uint8_t proto, uint32_t sum)
{
	uint32_t acc = partial_bytes((const unsigned char *)"", 0, sum);

	acc = csum_add(acc, saddr >> 16);
	acc = csum_add(acc, saddr & 0xffffU);
	acc = csum_add(acc, daddr >> 16);
	acc = csum_add(acc, daddr & 0xffffU);
	acc = csum_add(acc, proto);
	acc = csum_add(acc, len);
	return partial_bytes((const unsigned char *)"", 0, acc);
}

static void print_u16_case(const char *kind, const char *name, uint16_t value)
{
	printf("%s\t%s\t0x%04x\n", kind, name, value);
}

static void print_u32_case(const char *kind, const char *name, uint32_t value)
{
	printf("%s\t%s\t0x%08x\n", kind, name, value);
}

int main(void)
{
	static const unsigned char empty[] = "";
	static const unsigned char two_byte_word[] = { 0x00, 0x01 };
	static const unsigned char ipv4_header[] = {
		0x45, 0x00, 0x00, 0x3c,
		0x1c, 0x46, 0x40, 0x00,
		0x40, 0x06, 0x00, 0x00,
		0xc0, 0xa8, 0x00, 0x01,
		0xc0, 0xa8, 0x00, 0xc7,
	};
	static const unsigned char odd_payload[] = "abcde";
	static const unsigned char carry_payload[] = { 0xff, 0xff, 0xff, 0xff, 0x7f };
	static const unsigned char carry_phrase[] = "checksum fragments keep their carry";
	static const unsigned char udp_payload[] = "zigux checksum";
	unsigned char payload[] = { 0x70, 0x68, 0x61, 0x73, 0x65, 0x36 };
	unsigned char mutable_ipv4_header[] = {
		0x45, 0x00, 0x00, 0x3c,
		0x1c, 0x46, 0x40, 0x00,
		0x40, 0x06, 0x00, 0x00,
		0xc0, 0xa8, 0x00, 0x01,
		0xc0, 0xa8, 0x00, 0xc7,
	};

	const uint32_t udp_saddr = 0xc0a80001U;
	const uint32_t udp_daddr = 0xc0a800c7U;
	const uint8_t udp_proto = 17;

	uint32_t old_partial;
	uint32_t old_word;
	uint32_t new_word;
	uint16_t old_checksum;
	uint16_t old_total_length;
	uint16_t new_total_length;
	uint32_t diff;
	uint16_t replaced_by_diff;
	uint16_t replaced2;
	uint16_t checksum_before_addr_change;
	uint16_t replaced4;

	print_u16_case("compute", "empty", compute_bytes(empty, 0));
	print_u16_case("compute", "two-byte word", compute_bytes(two_byte_word, sizeof(two_byte_word)));
	print_u16_case("compute", "ipv4 header", compute_bytes(ipv4_header, sizeof(ipv4_header)));
	print_u16_case("compute", "odd payload", compute_bytes(odd_payload, 5));
	print_u16_case("compute", "carry-heavy payload", compute_bytes(carry_payload, sizeof(carry_payload)));

	print_u32_case("partial", "odd payload with saturated seed", partial_bytes(odd_payload, 5, 0xffffU));
	print_u32_case("partial", "carry-heavy payload with unfolded seed", partial_bytes(carry_payload, sizeof(carry_payload), 0x1fffeU));
	print_u32_case("partial", "ipv4 fragment with arbitrary seed", partial_bytes(ipv4_header, 7, 0xabcdU));

	print_u32_case("compose", "even split",
		       partial_bytes(empty, 0,
				     csum_block_add(
					     partial_bytes(carry_phrase, 20, 0),
					     partial_bytes(carry_phrase + 20, sizeof(carry_phrase) - 1 - 20, 0),
					     20)));
	print_u32_case("compose", "odd split",
		       partial_bytes(empty, 0,
				     csum_block_add(
					     partial_bytes(carry_phrase, 21, 0),
					     partial_bytes(carry_phrase + 21, sizeof(carry_phrase) - 1 - 21, 0),
					     21)));

	print_u32_case("tcpudp-nofold", "udp pseudo header",
		       csum_tcpudp_nofold(udp_saddr, udp_daddr, sizeof(udp_payload) - 1, udp_proto,
					  partial_bytes(udp_payload, sizeof(udp_payload) - 1, 0)));

	print_u32_case("negate", "zero", csum_negate(0x00000000U));
	print_u32_case("negate", "unit", csum_negate(0x00000001U));
	print_u32_case("negate", "saturated", csum_negate(0xffffffffU));
	print_u32_case("negate", "carry-heavy", csum_negate(0xdeadbef0U));

	print_u32_case("from64to32", "zero", csum_from64to32(0x0000000000000000ULL));
	print_u32_case("from64to32", "single carry", csum_from64to32(0x0000000100000000ULL));
	print_u32_case("from64to32", "saturated plus one", csum_from64to32(0xffffffff00000001ULL));
	print_u32_case("from64to32", "mixed words", csum_from64to32(0x123456789abcdef0ULL));

	old_partial = partial_bytes(payload, sizeof(payload), 0);
	old_word = ((uint32_t)payload[0] << 8) | payload[1];
	payload[0] = 0x12;
	payload[1] = 0x34;
	new_word = ((uint32_t)payload[0] << 8) | payload[1];
	csum_replace(&old_partial, old_word, new_word);
	print_u32_case("replace", "payload-word", old_partial);

	old_checksum = compute_bytes(mutable_ipv4_header, sizeof(mutable_ipv4_header));
	old_total_length = (uint16_t)(((uint16_t)mutable_ipv4_header[2] << 8) | mutable_ipv4_header[3]);
	mutable_ipv4_header[2] = 0x00;
	mutable_ipv4_header[3] = 0x40;
	new_total_length = (uint16_t)(((uint16_t)mutable_ipv4_header[2] << 8) | mutable_ipv4_header[3]);
	diff = csum_sub(new_total_length, old_total_length);
	replaced_by_diff = old_checksum;
	csum_replace_by_diff(&replaced_by_diff, diff);
	print_u16_case("replace-by-diff", "ipv4-total-length", replaced_by_diff);

	replaced2 = old_checksum;
	csum_replace2(&replaced2, old_total_length, new_total_length);
	print_u16_case("replace2", "ipv4-total-length", replaced2);

	mutable_ipv4_header[10] = 0;
	mutable_ipv4_header[11] = 0;
	checksum_before_addr_change = compute_bytes(mutable_ipv4_header, sizeof(mutable_ipv4_header));
	replaced4 = checksum_before_addr_change;
	csum_replace4(&replaced4, 0xc0a80001U, 0xc0a80002U);
	print_u16_case("replace4", "ipv4-saddr", replaced4);

	return 0;
}
