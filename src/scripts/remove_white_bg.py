import struct
import zlib
from pathlib import Path


def read_png(path: Path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Arquivo não é PNG")

    i = 8
    ihdr = None
    idat_parts = []

    while i < len(data):
        length = int.from_bytes(data[i:i + 4], "big")
        chunk_type = data[i + 4:i + 8]
        chunk_data = data[i + 8:i + 8 + length]
        i += 12 + length

        if chunk_type == b"IHDR":
            ihdr = chunk_data
        elif chunk_type == b"IDAT":
            idat_parts.append(chunk_data)
        elif chunk_type == b"IEND":
            break

    if ihdr is None:
        raise ValueError("PNG sem IHDR")

    width = int.from_bytes(ihdr[0:4], "big")
    height = int.from_bytes(ihdr[4:8], "big")
    bit_depth = ihdr[8]
    color_type = ihdr[9]
    interlace = ihdr[12]

    if bit_depth != 8:
        raise ValueError("Somente PNG 8-bit é suportado")
    if interlace != 0:
        raise ValueError("Somente PNG não-interlaçado é suportado")
    if color_type not in (2, 6):
        raise ValueError("Somente PNG RGB/RGBA é suportado")

    raw = zlib.decompress(b"".join(idat_parts))
    return width, height, color_type, raw


def paeth(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def unfilter_scanlines(raw: bytes, width: int, height: int, bpp: int):
    stride = width * bpp
    out = bytearray(height * stride)
    src = 0

    for y in range(height):
        f = raw[src]
        src += 1
        row_start = y * stride

        for x in range(stride):
            val = raw[src]
            src += 1

            left = out[row_start + x - bpp] if x >= bpp else 0
            up = out[row_start + x - stride] if y > 0 else 0
            up_left = out[row_start + x - stride - bpp] if (y > 0 and x >= bpp) else 0

            if f == 0:
                recon = val
            elif f == 1:
                recon = (val + left) & 0xFF
            elif f == 2:
                recon = (val + up) & 0xFF
            elif f == 3:
                recon = (val + ((left + up) // 2)) & 0xFF
            elif f == 4:
                recon = (val + paeth(left, up, up_left)) & 0xFF
            else:
                raise ValueError(f"Filtro PNG não suportado: {f}")

            out[row_start + x] = recon

    return bytes(out)


def to_rgba(pixels: bytes, color_type: int):
    out = bytearray()

    if color_type == 2:  # RGB
        for i in range(0, len(pixels), 3):
            r, g, b = pixels[i], pixels[i + 1], pixels[i + 2]
            a = 255

            v = min(r, g, b)
            if v >= 245:
                a = 0
            elif v >= 225:
                a = int((245 - v) / 20 * 255)

            out.extend((r, g, b, a))
    else:  # RGBA
        for i in range(0, len(pixels), 4):
            r, g, b, a = pixels[i], pixels[i + 1], pixels[i + 2], pixels[i + 3]

            v = min(r, g, b)
            if v >= 245:
                a = 0
            elif v >= 225:
                a = min(a, int((245 - v) / 20 * 255))

            out.extend((r, g, b, a))

    return bytes(out)


def png_chunk(chunk_type: bytes, chunk_data: bytes):
    crc = zlib.crc32(chunk_type)
    crc = zlib.crc32(chunk_data, crc) & 0xFFFFFFFF
    return (
        len(chunk_data).to_bytes(4, "big")
        + chunk_type
        + chunk_data
        + crc.to_bytes(4, "big")
    )


def write_rgba_png(path: Path, width: int, height: int, rgba: bytes):
    stride = width * 4
    filtered = bytearray()
    for y in range(height):
        filtered.append(0)  # filtro None
        start = y * stride
        filtered.extend(rgba[start:start + stride])

    compressed = zlib.compress(bytes(filtered), level=9)

    ihdr = (
        width.to_bytes(4, "big")
        + height.to_bytes(4, "big")
        + bytes([8, 6, 0, 0, 0])
    )

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(png_chunk(b"IHDR", ihdr))
    png.extend(png_chunk(b"IDAT", compressed))
    png.extend(png_chunk(b"IEND", b""))

    path.write_bytes(bytes(png))


def main():
    src = Path("src/images/bolodecorado.png")
    dst = Path("src/images/bolo-home-transparent.png")

    width, height, color_type, raw = read_png(src)
    bpp = 3 if color_type == 2 else 4
    pixels = unfilter_scanlines(raw, width, height, bpp)
    rgba = to_rgba(pixels, color_type)
    write_rgba_png(dst, width, height, rgba)


if __name__ == "__main__":
    main()
