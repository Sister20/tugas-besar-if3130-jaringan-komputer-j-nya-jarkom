import logging
from random import Random
from functools import reduce

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
        chunks = [bit_string[i:i+4] for i in range(0, len(bit_string), 4)]
    
        encoded_chunks = [self.encode_chunk(chunk) for chunk in chunks]
    
        encoded_bit_string = ''.join(encoded_chunks)
        return encoded_bit_string
    
    def encode_chunk_alternative(self, chunk: str) -> str:
        p1 = self.parity(chunk, [0, 1, 3])
        p2 = self.parity(chunk, [0, 2, 3])
        p3 = self.parity(chunk, [1, 2, 3])
    
        return "0" + p1 + p2 + chunk[0] + p3 + chunk[1:]
    
    def encode_chunk(self, chunk: str) -> str:
        eight_bit = self.get_eight_bit(chunk)
        if eight_bit == "00000000":
            return eight_bit
        parity_bit = reduce(lambda x, y: x^y, [i for i, bin in enumerate(eight_bit) if bin == '1'])

        for i in range(0, 3):
            if parity_bit & (1 << i):
                eight_bit = eight_bit[:1<<i] + '1' + eight_bit[(1<<i)+1:]
            else:
                eight_bit = eight_bit[:1<<i] + '0' + eight_bit[(1<<i)+1:]

        return eight_bit
    
    def get_eight_bit(self, bit_string: str) -> str:
        return "000" + bit_string[0] + "0" + bit_string[1] + bit_string[2] + bit_string[3]
    
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
    
    def decode_chunk_alternative(self, chunk: str) -> str:
        chunk = chunk[1:]
        print(f"decode chunk {chunk}")
        s1 = self.parity(chunk, [0, 2, 4, 6])
        s2 = self.parity(chunk, [1, 2, 5, 6])
        s3 = self.parity(chunk, [3, 4, 5, 6])
        syndrome = int(s3 + s2 + s1, 2)
        print(f"syndrome {syndrome}")
        if syndrome != 0:
            self.error = True
            self.error_bit_index = syndrome - 1
            chunk = chunk[:self.error_bit_index] + str(1 - int(chunk[self.error_bit_index])) + chunk[self.error_bit_index+1:]
    
        return chunk[2] + chunk[4] + chunk[5] + chunk[6]
    
    def decode_chunk(self, chunk: str) -> str:
        if chunk == "00000000":
            return "0000"
        parity_bit = reduce(lambda x, y: x^y, [i for i, bin in enumerate(chunk) if bin == '1'])

        if parity_bit != 0:
            self.error = True
            chunk = chunk[:parity_bit] + str(1 - int(chunk[parity_bit])) + chunk[parity_bit+1:]
            # logging.info(f"Error detected, trying to correct bit")

        return chunk[3] + chunk[5] + chunk[6] + chunk[7]


        
    

# def main():
#     hamming = Hamming()
#     data = b"123456789"
#     # print(f"length {len(data)}")
#     print(f"original data {data}")
#     encoded = hamming.encode(data)
#     # print(f"len encoded {len(encoded)}")
#     encoded = switch_random_bit(encoded)
#     # print(f"encoded data {encoded}")
#     decoded = hamming.decode(encoded)
#     print(f"decoded data {decoded}")
#     # print(1 << 7)

# def switch_random_bit(data: bytes) -> bytes:
#     new_data = b""
#     for byte in data:
#         # print(f"byte before{byte}")
#         # code to change bit
#         random = Random()
#         byte = bytes([byte ^ (1 << random.randint(1, 7))])
#         # print(f"byte after {byte}")
#         new_data = new_data + byte

#     return new_data


# if __name__ == "__main__":
#     main()