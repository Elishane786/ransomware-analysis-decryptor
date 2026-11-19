# Analysis notes

These notes describe how the ransomware sample was analysed and how the key was recovered. The sample is a 64 bit Windows program (a PE32+ GUI executable, 580,096 bytes). It was only read with static analysis tools and never executed. Function names such as `FUN_140008240` are the default names Ghidra gives to code it has not been told the name of, and the number is the address inside the program.

## 1. Setup

The work was done inside a Parrot OS virtual machine with no internet connection, so that nothing could run by accident and nothing could reach an outside server. The tools were Ghidra for the main reverse engineering, IDA to confirm what Ghidra showed, and Python for the decryption tool. The first step was the `file` command, which confirmed the sample is a Windows 64 bit executable.

## 2. Finding the real code

The entry point in Ghidra is a runtime start up routine that the compiler adds. It sets up the environment, prepares global variables and the program arguments, and then hands control to another function, and it has nothing harmful in it. That other function is `FUN_140008240`, and it is where the actual behaviour begins, so it was treated as the main controller.

## 3. The main controller

`FUN_140008240` does not encrypt anything itself. It calls out to smaller functions that find the files and then lock them, and splitting the work this way makes the program harder to follow, since no single function shows the whole story. Following its calls leads to the two functions that matter.

## 4. Finding the files

`FUN_140007590` is the file discovery routine. It uses the Windows functions `FindFirstFileW` and `FindNextFileW` to walk through folders and into the folders inside them, it skips files that are already locked, and it passes every other file on to the encryption routine. This is standard ransomware behaviour. One limit worth noting is that the exact list of folders and file types it targets was not fully pinned down in our notes, so check that part against the sample before relying on it.

## 5. The encryption routine

`FUN_140007080` does the locking. It encrypts with AES-128 in CBC mode, and it does so in pieces of 1008 bytes, with each piece written out as a 16 byte IV, a 4 byte length, and the ciphertext. Because the cipher starts fresh for every piece, no piece depends on the one before it, and that is not how AES is normally used on a whole file.

## 6. Where the key is

Inside `FUN_140007080` the address of a fixed block of data is passed into the AES code, which means the key and the IV are stored in the program and not made fresh for each victim. In the data view the 16 key bytes are at file offset `0x84e00` and the 16 IV bytes follow directly after at `0x84e10`.

```
0x84e00  8d 02 e6 5e 50 83 08 dd 74 3f 0d d4 d3 1e 48 4d   <- key
0x84e10  0a 0b 0c 0d 0e 0f a0 b0 c0 d0 e0 f0 aa bb cc dd   <- IV
```

The key is `8D02E65E508308DD743F0DD4D31E484D` and the IV is `0A0B0C0D0E0FA0B0C0D0E0F0AABBCCDD`. Note that the group report printed the IV with one digit out of place (`...E0FAABBCCDD0`), and the bytes above, read straight from the sample, are the correct ones.

## 7. Checking the layout on the real backup

The backup files were opened and measured to confirm the layout. Every file is an exact multiple of 1028 bytes, and in the three files checked in detail, every chunk starts with the same IV, `0a0b0c0d0e0fa0b0c0d0e0f0aabbccdd`, which is the IV found in the sample. Every chunk but the last has a length field of 1008, and the last chunk holds a smaller number, for example 924 for a 21,588 byte PDF, so the original size is easy to recover.

## 8. The decryption tool

`decrypt.py` reverses this directly. For each 1028 byte record it reads the IV, reads the length, decrypts the 1008 bytes with the key, and writes out only as many bytes as the length says. All 13 files of the assignment backup decrypted without errors into valid files, and 11 of them matched the decrypted copies from the original submission exactly (the other two had no copy to compare against).

## 9. Why this ransomware is weak

The cipher is fine and the way it is used is not. The key and IV are fixed in the program, so the defender gets the secret by opening the sample and the attacker is not needed at all. The same IV is used for every chunk of every file, which means two chunks with identical contents become identical ciphertext, and that leaks patterns, which is exactly what CBC with a fresh IV is meant to prevent. Nothing for the attacker to protect their key with exists anywhere in the design.

## 10. Other behaviour reported

The group noted that the sample includes a function that deletes its own executable after running, which removes evidence and slows down an investigation. This was reported from the Ghidra analysis and was not rechecked when these notes were written.

## What was not verified here

Two things from the original analysis were not independently confirmed while preparing this repo. The first is the full list of target folders, and the second is the self deletion feature. Everything about the key, the IV, the chunk layout and the decryption was checked directly against the sample and the backup files.
