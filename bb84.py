from qiskit import QuantumCircuit, Aer, assemble
from numpy.random import randint
import numpy as np


a = "11001100"
b = "1100010100"
y = int(a, 2)^int(b,2)
print(bin(y)[2:].zfill(len(a)))

exit()


# https://qiskit.org/textbook/ch-algorithms/quantum-key-distribution.html
def encode_message(bits, bases):
    message = []
    for i in range(n):
        qc = QuantumCircuit(1,1)
        if bases[i] == 0: # Prepare qubit in Z-basis
            if bits[i] == 0:
                pass
            else:
                qc.x(0)
        else: # Prepare qubit in X-basis
            if bits[i] == 0:
                qc.h(0)
            else:
                qc.x(0)
                qc.h(0)
        qc.barrier()
        message.append(qc)
    return message

def measure_message(message, bases):
    backend = Aer.get_backend('aer_simulator')
    measurements = []
    for q in range(n):
        if bases[q] == 0: # measuring in Z-basis
            message[q].measure(0,0)
        if bases[q] == 1: # measuring in X-basis
            message[q].h(0)
            message[q].measure(0,0)
        aer_sim = Aer.get_backend('aer_simulator')
        qobj = assemble(message[q], shots=1, memory=True)
        result = aer_sim.run(qobj).result()
        measured_bit = int(result.get_memory()[0])
        measurements.append(measured_bit)
    return measurements

# https://github.com/VoxelPixel/CiphersInPython/blob/master/XOR%20Cipher.py
def cipher_encryption(msg,key):
    print(msg)
    encrypt_hex = ""
    key_itr = 0
    for i in range(len(msg)):
        temp = ord(msg[i]) ^ ord(key[key_itr])
        # zfill will pad a single letter hex with 0, to make it two letter pair
        encrypt_hex += hex(temp)[2:].zfill(2)
        key_itr += 1
        if key_itr >= len(key):
            # once all of the key's letters are used, repeat the key
            key_itr = 0

    print("Encrypted Text: {}".format(encrypt_hex))
    return format(encrypt_hex)

def cipher_decryption(msg,key):

    hex_to_uni = ""
    for i in range(0, len(msg), 2):
        hex_to_uni += bytes.fromhex(msg[i:i+2]).decode('utf-8')

    decryp_text = ""
    key_itr = 0
    for i in range(len(hex_to_uni)):
        temp = ord(hex_to_uni[i]) ^ ord(key[key_itr])
        # zfill will pad a single letter hex with 0, to make it two letter pair
        decryp_text += chr(temp)
        key_itr += 1
        if key_itr >= len(key):
            # once all of the key's letters are used, repeat the key
            key_itr = 0

    print("Decrypted Text: {}".format(decryp_text))
    return format(decryp_text)

def remove_garbage(a_bases, b_bases, bits):
    good_bits = []
    for q in range(n):
        if a_bases[q] == b_bases[q]:
            # If both used the same basis, add
            # this to the list of 'good' bits
            good_bits.append(bits[q])
    return good_bits

def sample_bits(bits, selection):
    sample = []
    for i in selection:
        # use np.mod to make sure the
        # bit we sample is always in
        # the list range
        i = np.mod(i, len(bits))
        # pop(i) removes the element of the
        # list at index 'i'
        sample.append(bits.pop(i))
    return sample

n = 1000
# Step 1
alice_bits = randint(2, size=n)
alice_bases = randint(2, size=n)

# Step 2
message = encode_message(alice_bits, alice_bases)

# Step 3
bob_bases = randint(2, size=n)
bob_results = measure_message(message, bob_bases)

# Step 4
bob_key = remove_garbage(alice_bases, bob_bases, bob_results)
alice_key = remove_garbage(alice_bases, bob_bases, alice_bits)

# Step 5
sample_size = 100
bit_selection = randint(n, size=sample_size)
bob_sample = sample_bits(bob_key, bit_selection)
alice_sample = sample_bits(alice_key, bit_selection)

if (bob_sample != alice_sample):
    print("WARNING: Key samples do not match. Noise or eavesdropper on the quantum channel is  present")
    exit()

print(len(bob_key))

string_ints = [str(int) for int in alice_key]
str_of_ints = ",".join(string_ints)
a_key=str_of_ints

string_ints = [str(int) for int in bob_key]
str_of_ints = ",".join(string_ints)
b_key = str_of_ints

to_encrypt = '1001100'

a= cipher_encryption(to_encrypt,a_key)
c=cipher_decryption(a,b_key)


