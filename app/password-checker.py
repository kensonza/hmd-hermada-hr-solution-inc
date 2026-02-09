from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

hashed = "scrypt:32768:8:1$erZRdvMDhwyqzIN1$5068f67a1879025f1aed893ed689eaccb6896af0b41d0d8e02d67f4307eb56d85a02e1c5b59bdd2fa1ab216af0ef00028c306d9cbc34a5e1f2c3598f10fa2f20"
print(check_password_hash(hashed, "K3np@ch123"))
#print(generate_password_hash("K3np@ch123"))