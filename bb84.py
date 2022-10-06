from qiskit import QuantumCircuit, Aer, assemble
from numpy.random import randint
import numpy as np

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

n = 100
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
sample_size = 10 # more is safer against eavesdropping and noise
bit_selection = randint(n, size=sample_size)
bob_sample = sample_bits(bob_key, bit_selection)
alice_sample = sample_bits(alice_key, bit_selection)

if (bob_sample != alice_sample):
    print("WARNING: Key samples do not match. Noise or eavesdropper on the quantum channel is  present")
    exit()
elif (bob_key!=alice_key):
    print("WARNING: Keys do not match. Abort quantum key distribution protocol")
    exit()


string_ints = [str(int) for int in alice_key]
str_of_ints = "".join(string_ints)
a_key=str_of_ints

string_ints = [str(int) for int in bob_key]
str_of_ints = "".join(string_ints)
b_key = str_of_ints

a_key=a_key[0:8]
b_key=b_key[0:8]
to_encrypt = '10011000'

# returns encrypted byte
def xor_encrypt(msg, key):
    encrypted = int(msg, 2)^int(key,2)
    return bin(encrypted)[2:].zfill(len(a))

def xor_decrypt(msg, key):
    decrypted=int(msg, 2)^int(key,2)
    return bin(decrypted)[2:].zfill(len(msg))

a = "11011111"
b = "11001011"

encrypted_text=xor_encrypt(to_encrypt,a_key)
decrypted_text=xor_decrypt(encrypted_text,b_key)
print(to_encrypt, encrypted_text, decrypted_text)



