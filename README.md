# Ransomware analysis and decryptor

This repo holds the work from a university malware analysis assignment (MSc Cyber Security, University of Birmingham). A friend's files had been locked by a ransomware sample, and the job was to reverse engineer the sample, find out how it locks files, recover the key, and write a tool that gets the files back. It was done as a group assignment, and the sample was only ever read in a disassembler and never run.

The short version of what we found is that the ransomware uses a strong cipher but keeps its secrets in the wrong place. It encrypts with AES-128 in CBC mode, yet the key and the IV sit in plain view inside the program file, so anyone who opens the sample can read the key and decrypt every locked file without paying anything.

## What is in this repo

- `decrypt.py`, the decryption tool
- `docs/analysis-notes.md`, the step by step method and findings
- `docs/report.pdf`, the group report, rebuilt for this repo (see the note below)

The malware sample, the encrypted backup, and the decrypted media files are not in this repo, on purpose. The sample is dangerous to handle, and the media files are large and add nothing.

## A note on the report

The report that was handed in for the assignment carried the wrong title, which was copied from another piece of coursework (an IoT camera penetration test), and it printed the IV with one digit out of place. The editable Word file of that report could not be found afterwards, so the corrected version in `docs/report.pdf` was rebuilt from the original text and not edited from the original file. The title and the typos are fixed, and the IV in it matches the bytes in the sample. The rebuilt copy is shorter and plainer than the one that was submitted, but the findings are the same.

## The key facts

| Item | Value |
| --- | --- |
| Cipher | AES-128, CBC mode |
| Key | `8D02E65E508308DD743F0DD4D31E484D` |
| IV | `0A0B0C0D0E0FA0B0C0D0E0F0AABBCCDD` |
| Location in the sample | key at file offset `0x84e00`, IV straight after it at `0x84e10` |
| Block layout | 1028 bytes per chunk: 16 byte IV, 4 byte length, 1008 bytes of ciphertext |

## How the locked files are laid out

The ransomware does not encrypt a file in one go. It cuts the file into pieces of 1008 bytes and encrypts each piece on its own, writing out a 16 byte IV, a 4 byte little endian length, and then the 1008 bytes of ciphertext for every piece. The last piece is usually shorter than 1008 bytes and gets padded, and the stored length is what tells the decryptor how much of it is real data. The decryptor reads a chunk, decrypts it with the key and the stored IV, keeps only the number of bytes the length field asks for, and moves on to the next chunk.

## How to run it

You need Python 3 and the PyCryptodome package.

```
pip install pycryptodome
python decrypt.py <encrypted_file> <output_file>
```

For example, `python decrypt.py locked/report.pdf restored/report.pdf`. The tool was tested against all 13 files of the backup that came with the assignment, and every one decrypted without errors into a file of the expected type. Eleven of them were compared byte for byte with the earlier decrypted copies from the original submission and matched exactly.

## Safety

Do not run the ransomware sample on any computer you care about. Reverse engineering does not need it to run, and every step in the notes was done by reading the code in a disassembler.

## Credits

This was group coursework. The analysis was done in Ghidra, with IDA used to confirm the findings.
