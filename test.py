import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

password = "shruti"  # Replace with your desired password
hashed = hash_password(password)
print("Hashed password:", hashed)
