#!/usr/bin/python3
# From https://stackoverflow.com/questions/20852664/python-pycrypto-encrypt-decrypt-text-files-with-aes
from Crypto import Random
from Crypto.Cipher import AES
import json
from config_parse import enc_key as key

key = key.encode('ascii')

def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

def encrypt(message, key, key_size=256):
    message = pad(message)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(message)

def decrypt(ciphertext, key):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b"\0")

def encrypt_file(file_name, key,out_fd):
    if type(file_name) == str:
        with open(file_name, 'rb') as fo:
            plaintext = fo.read()
    else:
        plaintext = file_name.read()

    enc = encrypt(plaintext, key)

    out_fd.write(enc)

def decrypt_file(file_name, key,out_fd):

    if type(file_name) == str:
        with open(file_name, 'rb') as fo:
            ciphertext = fo.read()
    else:
        ciphertext = file_name.read()
    dec = decrypt(ciphertext, key)

    out_fd.write(dec)

