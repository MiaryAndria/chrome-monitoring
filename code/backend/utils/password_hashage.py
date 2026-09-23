from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hasher_password(password):
    return password_hash.hash(password)

def verifier_password(password_clair, password_hache):
    return password_hash.verify(password_clair, password_hache)