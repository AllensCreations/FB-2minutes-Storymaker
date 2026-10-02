"""
Zero-dependency Pure-Python QR Code Terminal Generator
Encodes URLs and text into ISO/IEC 18004 QR Codes and renders them
in the terminal using Unicode half-block characters (▀, ▄, █, space).
"""

import shutil
from typing import List, Optional, Tuple

# Galois Field GF(256) tables with primitive polynomial 0x11d
_GF_EXP = [0] * 512
_GF_LOG = [0] * 256
_x = 1
for _i in range(255):
    _GF_EXP[_i] = _x
    _GF_EXP[_i + 255] = _x
    _GF_LOG[_x] = _i
    _x <<= 1
    if _x & 256:
        _x ^= 0x11D


def _gf_mul(x: int, y: int) -> int:
    return 0 if x == 0 or y == 0 else _GF_EXP[(_GF_LOG[x] + _GF_LOG[y]) % 255]


def _rs_generator_poly(nsym: int) -> List[int]:
    g = [1]
    for i in range(nsym):
        new_g = [0] * (len(g) + 1)
        for j in range(len(g)):
            new_g[j] ^= _gf_mul(g[j], _GF_EXP[i])
            new_g[j + 1] ^= g[j]
        g = new_g
    return g


def _rs_encode(data: List[int], nsym: int) -> List[int]:
    gen = _rs_generator_poly(nsym)
    res = list(data) + [0] * nsym
    for i in range(len(data)):
        coef = res[i]
        if coef != 0:
            for j in range(len(gen)):
                res[i + j] ^= _gf_mul(gen[j], coef)
    return res[len(data):]


# Capacity specifications for QR Versions 1 to 4 with ECC Level L
# Format: (size, total_codewords, data_codewords, ec_codewords, alignment_coord)
_VERSION_SPECS = {
    1: (21, 26, 19, 7, None),
    2: (25, 44, 34, 10, 18),
    3: (29, 70, 55, 15, 22),
    4: (33, 100, 80, 20, 26),
}

# Precomputed BCH(15, 5) format info for ECC Level L (01) and mask patterns 0..7
_FORMAT_INFO_L = {
    0: 0x77C4, 1: 0x72F3, 2: 0x7DAA, 3: 0x789D,
    4: 0x662F, 5: 0x6318, 6: 0x6C41, 7: 0x6976,
}


def _select_version(data_len: int) -> Optional[int]:
    """Select the smallest suitable QR version for 8-bit byte mode."""
    # 4 bits (mode) + 8 bits (char count) + data_len * 8 bits
    required_bits = 12 + data_len * 8
    required_codewords = (required_bits + 7) // 8
    for version, (_, _, data_cap, _, _) in _VERSION_SPECS.items():
        if required_codewords <= data_cap:
            return version
    return None


def generate_qr_matrix(text: str) -> Optional[List[List[int]]]:
    """Encodes a string into a QR code 2D binary matrix (1 for dark, 0 for light)."""
    raw_data = text.encode("utf-8")
    version = _select_version(len(raw_data))
    if version is None:
        return None

    size, total_cw, data_cw, ec_cw, align_pos = _VERSION_SPECS[version]

    # Step 1: Bitstream encoding in 8-bit Byte mode
    bitstream: List[int] = []

    def append_bits(val: int, length: int):
        for k in range(length - 1, -1, -1):
            bitstream.append((val >> k) & 1)

    append_bits(0b0100, 4)           # Byte mode indicator
    append_bits(len(raw_data), 8)     # Character count
    for byte in raw_data:
        append_bits(byte, 8)

    # Terminator (up to 4 zeros)
    max_data_bits = data_cw * 8
    terminator_len = min(4, max_data_bits - len(bitstream))
    bitstream.extend([0] * terminator_len)

    # Pad to byte boundary
    if len(bitstream) % 8 != 0:
        bitstream.extend([0] * (8 - (len(bitstream) % 8)))

    # Convert bitstream to bytes
    data_bytes: List[int] = []
    for i in range(0, len(bitstream), 8):
        byte_val = 0
        for bit in bitstream[i:i + 8]:
            byte_val = (byte_val << 1) | bit
        data_bytes.append(byte_val)

    # Pad codewords with 0xEC and 0x11
    pad_bytes = [0xEC, 0x11]
    pad_idx = 0
    while len(data_bytes) < data_cw:
        data_bytes.append(pad_bytes[pad_idx % 2])
        pad_idx += 1

    # Step 2: Error Correction (Reed-Solomon)
    ec_bytes = _rs_encode(data_bytes, ec_cw)
    all_codewords = data_bytes + ec_bytes

    # Convert all codewords to bit array
    all_bits: List[int] = []
    for cw in all_codewords:
        for k in range(7, -1, -1):
            all_bits.append((cw >> k) & 1)

    # Step 3: Matrix Setup
    matrix = [[0] * size for _ in range(size)]
    reserved = [[False] * size for _ in range(size)]

    def mark_reserved(r, c, val):
        matrix[r][c] = val
        reserved[r][c] = True

    # Finder patterns (7x7) + Separators
    for r0, c0 in [(0, 0), (0, size - 7), (size - 7, 0)]:
        for dr in range(-1, 8):
            for dc in range(-1, 8):
                r, c = r0 + dr, c0 + dc
                if 0 <= r < size and 0 <= c < size:
                    is_black = (
                        0 <= dr <= 6 and 0 <= dc <= 6
                        and (dr in (0, 6) or dc in (0, 6) or (2 <= dr <= 4 and 2 <= dc <= 4))
                    )
                    mark_reserved(r, c, 1 if is_black else 0)

    # Timing patterns
    for i in range(8, size - 8):
        mark_reserved(6, i, 1 if i % 2 == 0 else 0)
        mark_reserved(i, 6, 1 if i % 2 == 0 else 0)

    # Dark module
    mark_reserved(size - 8, 8, 1)

    # Alignment pattern
    if align_pos is not None:
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                r, c = align_pos + dr, align_pos + dc
                if not reserved[r][c]:
                    is_black = (abs(dr) == 2 or abs(dc) == 2 or (dr == 0 and dc == 0))
                    mark_reserved(r, c, 1 if is_black else 0)

    # Reserve format info areas
    for i in range(9):
        if not reserved[8][i]:
            reserved[8][i] = True
        if not reserved[i][8]:
            reserved[i][8] = True
    for i in range(8):
        if not reserved[8][size - 1 - i]:
            reserved[8][size - 1 - i] = True
        if not reserved[size - 1 - i][8]:
            reserved[size - 1 - i][8] = True

    # Step 4: Place Data Bits (Zigzag right to left)
    bit_idx = 0
    right = size - 1
    upwards = True
    while right > 0:
        if right == 6:  # Skip vertical timing pattern
            right -= 1
        row_range = range(size - 1, -1, -1) if upwards else range(size)
        for r in row_range:
            for c in (right, right - 1):
                if not reserved[r][c]:
                    if bit_idx < len(all_bits):
                        matrix[r][c] = all_bits[bit_idx]
                        bit_idx += 1
                    else:
                        matrix[r][c] = 0
        right -= 2
        upwards = not upwards

    # Step 5: Masking & Penalty Selection
    def mask_func(mask_num, r, c):
        if mask_num == 0:
            return (r + c) % 2 == 0
        elif mask_num == 1:
            return r % 2 == 0
        elif mask_num == 2:
            return c % 3 == 0
        elif mask_num == 3:
            return (r + c) % 3 == 0
        elif mask_num == 4:
            return ((r // 2) + (c // 3)) % 2 == 0
        elif mask_num == 5:
            return ((r * c) % 2) + ((r * c) % 3) == 0
        elif mask_num == 6:
            return (((r * c) % 2) + ((r * c) % 3)) % 2 == 0
        else:
            return (((r + c) % 2) + ((r * c) % 3)) % 2 == 0

    best_mask = 0
    best_penalty = float("inf")
    best_matrix = None

    for m in range(8):
        # Create candidate with mask
        candidate = [row[:] for row in matrix]
        for r in range(size):
            for c in range(size):
                if not reserved[r][c] and mask_func(m, r, c):
                    candidate[r][c] ^= 1

        # Place format info
        format_val = _FORMAT_INFO_L[m]
        # Top-left format info
        fmt_bits = [(format_val >> (14 - i)) & 1 for i in range(15)]
        coords1 = [
            (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 7), (8, 8),
            (7, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8),
        ]
        coords2 = [
            (size - 1, 8), (size - 2, 8), (size - 3, 8), (size - 4, 8),
            (size - 5, 8), (size - 6, 8), (size - 7, 8),
            (8, size - 8), (8, size - 7), (8, size - 6), (8, size - 5),
            (8, size - 4), (8, size - 3), (8, size - 2), (8, size - 1),
        ]
        for (r, c), bit in zip(coords1, fmt_bits):
            candidate[r][c] = bit
        for (r, c), bit in zip(coords2, fmt_bits):
            candidate[r][c] = bit

        # Calculate penalty score
        penalty = 0
        # N1: Horizontal & vertical runs
        for r in range(size):
            run = 1
            for c in range(1, size):
                if candidate[r][c] == candidate[r][c - 1]:
                    run += 1
                else:
                    if run >= 5:
                        penalty += 3 + (run - 5)
                    run = 1
            if run >= 5:
                penalty += 3 + (run - 5)

        for c in range(size):
            run = 1
            for r in range(1, size):
                if candidate[r][c] == candidate[r - 1][c]:
                    run += 1
                else:
                    if run >= 5:
                        penalty += 3 + (run - 5)
                    run = 1
            if run >= 5:
                penalty += 3 + (run - 5)

        # N2: 2x2 blocks
        for r in range(size - 1):
            for c in range(size - 1):
                if candidate[r][c] == candidate[r + 1][c] == candidate[r][c + 1] == candidate[r + 1][c + 1]:
                    penalty += 3

        if penalty < best_penalty:
            best_penalty = penalty
            best_mask = m
            best_matrix = candidate

    return best_matrix


def render_qr_ansi(matrix: List[List[int]], border: int = 1) -> str:
    """
    Renders QR matrix to ANSI text using half-block characters:
    ▀ (upper half), ▄ (lower half), █ (both), space (neither).
    Uses standard white background (\033[47;30m) for maximum camera compatibility.
    """
    if not matrix:
        return ""

    size = len(matrix)
    padded_size = size + border * 2

    # Build padded grid: 1 = dark, 0 = light
    grid = [[0] * padded_size for _ in range(padded_size)]
    for r in range(size):
        for c in range(size):
            grid[r + border][c + border] = matrix[r][c]

    lines = []
    # Process 2 rows at a time
    for y in range(0, padded_size, 2):
        row_chars = []
        for x in range(padded_size):
            top = grid[y][x]
            bot = grid[y + 1][x] if y + 1 < padded_size else 0

            # With \033[47;30m (white bg, black fg):
            # top=1, bot=1 -> '█' (full black)
            # top=1, bot=0 -> '▀' (top black, bottom white)
            # top=0, bot=1 -> '▄' (top white, bottom black)
            # top=0, bot=0 -> ' ' (full white)
            if top and bot:
                row_chars.append("█")
            elif top and not bot:
                row_chars.append("▀")
            elif not top and bot:
                row_chars.append("▄")
            else:
                row_chars.append(" ")
        lines.append(f"\033[47;30m{''.join(row_chars)}\033[0m")

    return "\n".join(lines)


def get_qr_terminal_display(text: str, max_columns: Optional[int] = None) -> str:
    """
    Generates a compact ANSI QR code for display in terminal.
    Returns empty string if terminal is too narrow or text is invalid.
    """
    if not text:
        return ""

    if max_columns is None:
        max_columns = shutil.get_terminal_size((80, 24)).columns

    try:
        matrix = generate_qr_matrix(text)
        if not matrix:
            return ""
        # Check if padded width fits in terminal
        padded_width = len(matrix) + 2
        if max_columns < padded_width:
            return ""
        return render_qr_ansi(matrix, border=1)
    except Exception:
        return ""
