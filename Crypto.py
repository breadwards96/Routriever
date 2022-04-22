from cryptography.fernet import Fernet


def get_key():
    key = Fernet.generate_key()

    return key


def encrypt(string, key):

    f = Fernet(key)

    token = f.encrypt(string)

    return token


def decrypt(string, key):

    f = Fernet(key)

    token = f.decrypt(string)

    return token


# UGH FIX ME


"""mode = input("Select mode\n 1: provide key\n 2: generate key\n#")
if int(mode) == 1:
    seskey = bytes(input("Paste Key Here\n>"), 'utf-8')
else:
    seskey = get_key()

print("Session Key: " + str(seskey))

Ustr = input("Enter text to encrypt\n>")

Estr = encrypt(Ustr.encode(), seskey)

print("Encrypted String: " + str(Estr))"""
