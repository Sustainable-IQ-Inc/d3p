import base64
import os

# Generate a 32-byte (256-bit) random key
encryption_key = base64.b64encode(os.urandom(32)).decode('utf-8')

# Generate a 16-byte (128-bit) random salt
encryption_salt = base64.b64encode(os.urandom(16)).decode('utf-8')

print(f'ENCRYPTION_KEY="{encryption_key}"')
print(f'ENCRYPTION_SALT="{encryption_salt}"')