import numpy as np
import zlib
import matplotlib.pyplot as plt

def decode_png(png_bytes):
    # PNG signature check
    if png_bytes[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError("Invalid PNG signature")

    i = 8
    width = 0
    height = 0
    bit_depth = 0
    color_type = 0
    data = b''

    while i < len(png_bytes):
        chunk_len = int.from_bytes(png_bytes[i:i+4], 'big')
        chunk_type = png_bytes[i+4:i+8].decode('ascii')
        chunk_data = png_bytes[i+8:i+8+chunk_len]
        i += 8 + chunk_len + 4

        if chunk_type == 'IHDR':
            width = int.from_bytes(chunk_data[:4], 'big')
            height = int.from_bytes(chunk_data[4:8], 'big')
            bit_depth = chunk_data[8]
            color_type = chunk_data[9]

        elif chunk_type == 'IDAT':
            data += chunk_data

    decompressed_data = zlib.decompress(data)

    # Unfiltering
    bytes_per_pixel = 1 if color_type < 4 else (4 if color_type == 6 else 3)
    scanline_length = (width * bit_depth // 8) * bytes_per_pixel
    unfiltered_data = bytearray()
    i = 0

    for y in range(height):
        filter_type = decompressed_data[i]
        i += 1
        scanline = decompressed_data[i:i + scanline_length]
        i += scanline_length

        if filter_type == 0:  # None
            unfiltered_data.extend(scanline)
        elif filter_type == 1:  # Sub
            for x in range(scanline_length):
                if x < bytes_per_pixel:
                    unfiltered_data.append(scanline[x])
                else:
                    unfiltered_data.append((scanline[x] + unfiltered_data[-bytes_per_pixel]) % 256)
        elif filter_type == 2:  # Up
            for x in range(scanline_length):
                if y == 0:
                    unfiltered_data.append(scanline[x])
                else:
                    unfiltered_data.append((scanline[x] + unfiltered_data[x - scanline_length]) % 256)
        else:
            raise ValueError(f"Unsupported filter type: {filter_type}")

    # Reshape
    image_data = np.frombuffer(unfiltered_data, dtype=np.uint8).reshape(height, width, bytes_per_pixel)

    return image_data


hex_bytes = open("./images/sample-input.png", "rb").read()
# hex_bytes = open("./images/slack-icon.png", "rb").read()

image = decode_png(hex_bytes)
# show image with matplotlib
plt.imshow(image)
plt.show()
# save image to file
plt.imsave("output.png", image)
print("Image saved to output.png")
