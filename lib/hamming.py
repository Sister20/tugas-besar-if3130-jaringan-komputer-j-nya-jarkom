import logging

class Hamming:
    # implement hamming(8,4) code
    def __init__(self):
        self.error = False
        self.error_bit = 0

    def bytes_to_bits(self, data: bytes) -> str:
        bits = [bin(byte)[2:].zfill(8) for byte in data]
    
        bit_string = ''.join(bits)
    
        return bit_string
    
    def bits_to_bytes(self, bit_string: str) -> bytes:
        chunks = [bit_string[i:i+8] for i in range(0, len(bit_string), 8)]
    
        byte_data = bytes([int(chunk, 2) for chunk in chunks])
    
        return byte_data
    
    def encode(self, data: bytes) -> bytes:
        bit_string = self.bytes_to_bits(data)
        encoded_bit_string = self.encode_bits(bit_string)
        encoded_data = self.bits_to_bytes(encoded_bit_string)
        return encoded_data
    
    def encode_bits(self, bit_string: str) -> str:
        # print(f"sisa dari lennya {int(len(bit_string) / 4)}")
        chunks = [bit_string[i:i+4] for i in range(0, len(bit_string), 4)]
    
        encoded_chunks = [self.encode_chunk(chunk) for chunk in chunks]
    
        encoded_bit_string = ''.join(encoded_chunks)
    
        return encoded_bit_string
    
    def encode_chunk(self, chunk: str) -> str:
        p1 = self.parity(chunk, [0, 1, 3])
        p2 = self.parity(chunk, [0, 2, 3])
        p3 = self.parity(chunk, [1, 2, 3])

        # print(f"encode chunk {p1 + p2 + chunk[0] + p3 + chunk[1:] + '0'}")
    
        return p1 + p2 + chunk[0] + p3 + chunk[1:] + '0'
    
    def parity(self, bit_string: str, indices: list) -> str:
        parity_bit = str(sum([int(bit_string[i]) for i in indices]) % 2)
    
        return parity_bit
    
    def decode(self, data: bytes) -> bytes:
        bit_string = self.bytes_to_bits(data)
        decoded_bit_string = self.decode_bits(bit_string)
        decoded_data = self.bits_to_bytes(decoded_bit_string)
        return decoded_data
    
    def decode_bits(self, bit_string: str) -> str:
        chunks = [bit_string[i:i+8] for i in range(0, len(bit_string), 8)]
    
        decoded_chunks = [self.decode_chunk(chunk) for chunk in chunks]
    
        decoded_bit_string = ''.join(decoded_chunks)
    
        return decoded_bit_string
    
    def decode_chunk(self, chunk: str) -> str:
        chunk = chunk[:-1]
        # if len(chunk) != 7:
        #     chunk = chunk.zfill(7)

        # print(f"decode chunk {chunk}")
        s1 = self.parity(chunk, [0, 2, 4, 6])
        s2 = self.parity(chunk, [1, 2, 5, 6])
        s3 = self.parity(chunk, [3, 4, 5, 6])
        # print(f"s1 {s1} s2 {s2} s3 {s3}")
    
        syndrome = int(s3 + s2 + s1, 2)
        # print(f"syndrome {syndrome}")
        if syndrome != 0:
            self.error = True
            self.error_bit_index = syndrome - 1
            chunk = chunk[:self.error_bit_index] + str(1 - int(chunk[self.error_bit_index])) + chunk[self.error_bit_index+1:]

            # print(f"error detected, trying to correct bit")
            # print(f"result corrected {chunk}")
            # logging.info(f"Error detected, trying to correct bit")
    
        return chunk[2] + chunk[4] + chunk[5] + chunk[6]
    

# def main():
#     hamming = Hamming()
#     data = b"11"
#     print(f"length {len(data)}")
#     print(f"original data {data}")
#     encoded = hamming.encode(data)
#     print(f"len encoded {len(encoded)}")
#     byte = encoded[0]
#     # code to change bit
#     byte = bytes([byte ^ (1 << 2)])
#     encoded = byte + encoded[1:]
#     print(f"encoded data {encoded}")
#     decoded = hamming.decode(encoded)
#     print(f"decoded data {decoded}")

# if __name__ == "__main__":
#     main()