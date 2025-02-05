# gemini advanced generated this for me

import numpy as np
import zlib
from skimage import io

def decode_png(file_binary):
    """Decodes a simplified PNG binary into a NumPy array and displays it."""

    # 1. Signature check (simplified)
    if file_binary[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError("Invalid PNG signature")

    # 2. IHDR chunk (simplified)
    ihdr_length = int.from_bytes(file_binary[8:12], 'big')  # Assuming big-endian
    ihdr_data = file_binary[12+4:12+4+ihdr_length]
    width = int.from_bytes(ihdr_data[:4], 'big')
    height = int.from_bytes(ihdr_data[4:8], 'big')
    color_type = ihdr_data[9]  # Simplified color type

    # 3. IDAT chunk (handling multiple IDATs)
    idat_data = b''
    idat_start = 0
    while True:
        idat_start = file_binary.find(b'IDAT', idat_start)
        if idat_start == -1:
            break
        idat_length = int.from_bytes(file_binary[idat_start-4:idat_start], 'big')
        idat_data += file_binary[idat_start+4:idat_start+4+idat_length]
        idat_start += 4 + 4 + idat_length  # Move past current IDAT

    # 4. Decompress IDAT data
    decoded_data = zlib.decompress(idat_data)

    # 5. Reconstruct image data (handling filtering)
    bytes_per_pixel = 4 if color_type == 6 else 1  # RGBA or Grayscale
    row_bytes = width * bytes_per_pixel
    image_array = np.zeros((height, width, bytes_per_pixel), dtype=np.uint8)

    recon_data = bytearray() # Use bytearray directly to accumulate
    i = 0
    for y in range(height):
        filter_type = decoded_data[i]
        i += 1
        row_data = decoded_data[i:i + row_bytes]
        i += row_bytes
        recon_row = bytearray(row_data)

        # Handle filtering
        if filter_type == 0:  # None
            pass  # No filtering needed
        elif filter_type == 1:  # Sub
            for x in range(bytes_per_pixel, row_bytes):
                recon_row[x] = (recon_row[x] + recon_row[x - bytes_per_pixel]) & 0xFF  # Modulo 256
        else:
            raise ValueError(f"Unsupported filter type: {filter_type}")

        recon_data.extend(recon_row)

    image_array = np.frombuffer(recon_data, dtype=np.uint8).reshape((height, width, bytes_per_pixel))
    return image_array

# Example usage (assuming you have the binary data in 'file_binary'):
file_binary = bytes([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x02, 0x08, 0x06, 0x00, 0x00, 0x00, 0x9d, 0x74, 0x66, 0x1a, 0x00, 0x00, 0x00, 0x09, 0x70, 0x48, 0x59, 0x73, 0x00, 0x00, 0x2e, 0x23, 0x00, 0x00, 0x2e, 0x23, 0x01, 0x78, 0xa5, 0x3f, 0x76, 0x00, 0x00, 0x00, 0x1e, 0x49, 0x44, 0x41, 0x54, 0x08, 0x99, 0x05, 0xc1, 0x01, 0x01, 0x00, 0x20, 0x00, 0xc3, 0x20, 0x66, 0xff, 0x2c, 0x56, 0x32, 0xca, 0x85, 0xb6, 0x0d, 0x94, 0x93, 0xbc, 0x9b, 0xf0, 0x01, 0x69, 0xe9, 0x05, 0x93, 0x21, 0x64, 0xb5, 0x26, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82])

image = decode_png(file_binary)
io.imshow(image)
io.show()
