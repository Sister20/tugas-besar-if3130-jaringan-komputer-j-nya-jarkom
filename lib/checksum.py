def calculate_checksum(data: bytes):
    crc16 = 0xFFFF
    for byte in data:
        byte_to_calc = byte
        for _ in range(8):
            msb_crc = (crc16 & 0x8000) >> 8
            msb_byte = byte_to_calc & 0x80
            msb_is_set = msb_byte ^ msb_crc
            crc16 = (crc16 << 1) & 0xFFFF
            if msb_is_set:
                crc16 = crc16 ^ 0x1021

            byte_to_calc = (byte_to_calc << 1) & 0xFF

    return crc16 & 0xFFFF

