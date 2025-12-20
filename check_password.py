import hashlib

password = 'DACOS!Charaun#687'
salt_hex = 'b9931be6d900f4a3e9514c1baa780d523b5d87f06cd556c19c59489358b21f48'
stored_hash = '89ce070ce98e2f8650f26ad88cb262a5a2150fb67ebfc008fd5a7df6787f8cc2'

salt = bytes.fromhex(salt_hex)
key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
computed_hash = salt.hex() + key.hex()

print('Stored hash:', stored_hash)
print('Computed hash:', computed_hash)
print('Match:', stored_hash == computed_hash)