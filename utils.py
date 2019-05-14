#!/usr/bin/python3

from Crypto import Random
from Crypto.Cipher import AES
import json

# read file with key
with open('config.json','r') as f:
    data=json.load(f)
    key=data['key'].encode('ascii')

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

if __name__ == '__main__':
    print(key)
    with open("out33.enc", 'wb') as fo:
        encrypt_file('/home/aferral/Escritorio/p_m/05. Where You End.mp3', key,fo)

    with open('out2.mp3', 'wb') as fo:
        decrypt_file('a.enc', key,fo)
