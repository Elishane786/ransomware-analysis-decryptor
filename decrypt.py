from Crypto.Cipher import AES
from pathlib import Path
import sys

KEY = bytes.fromhex("8d02e65e508308dd743f0dd4d31e484d")
DEFAULT_IV = bytes.fromhex("0a0b0c0d0e0fa0b0c0d0e0f0aabbccdd")

CHUNK_PLAINTEXT_SIZE = 0x3F0   # 1008
IV_SIZE = 16
LEN_SIZE = 4

def decrypt_file(src_path: str, dst_path: str) -> None:
    with open(src_path, "rb") as f, open(dst_path, "wb") as out:
        while True:
            iv = f.read(IV_SIZE)
            if not iv:
                break
            if len(iv) != IV_SIZE:
                raise ValueError("Truncated file while reading IV")

            length_bytes = f.read(LEN_SIZE)
            if len(length_bytes) != LEN_SIZE:
                raise ValueError("Truncated file while reading chunk length")

            chunk_len = int.from_bytes(length_bytes, "little")

            ciphertext = f.read(CHUNK_PLAINTEXT_SIZE)
            if len(ciphertext) != CHUNK_PLAINTEXT_SIZE:
                raise ValueError("Truncated file while reading ciphertext block")

            cipher = AES.new(KEY, AES.MODE_CBC, iv)
            plaintext = cipher.decrypt(ciphertext)

            out.write(plaintext[:chunk_len])

def main():
    if len(sys.argv) != 3:
        print(f"Usage: python {Path(sys.argv[0]).name} <encrypted_file> <output_file>")
        sys.exit(1)

    decrypt_file(sys.argv[1], sys.argv[2])
    print("Done.")

if __name__ == "__main__":
    main()
