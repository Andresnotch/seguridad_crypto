# Caesar Cipher - www.101computing.net/caesar-cipher

cipher = "N qtaj uwtlwfrrnsl zxnsl Udymts"


# Complete the code below to decode this cipher using a 5-character right shift

def decypher(code, shift):
	letters = 'abcdefghijklmnopqrstuvwxyz'
	return ' '.join(
		(''.join([letters[(letters.find(l) + shift) % len(letters)] for l in w]) for w in code.lower().split(' ')))


print(decypher(cipher, -5))
