from lib.checksum import calculate_checksum
import binascii

def test_calculate_checksum():
    data = b"hello world"
    
    # checksum function
    calculated_checksum = calculate_checksum(data)
    
    # binascii library calculation
    expected_checksum = binascii.crc_hqx(data, 0xFFFF)
    
    assert calculated_checksum == expected_checksum
    print(f"Checksum: {hex(calculated_checksum)}, binascii: {hex(expected_checksum)}")

if __name__ == "__main__":
    test_calculate_checksum()
