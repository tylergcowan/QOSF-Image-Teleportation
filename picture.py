from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, Aer, transpile, assemble
import PIL.Image as Image #NOTE: Pillow imported instead of PIL
import io
from numpy.random import randint
import numpy as np

def create_bell_pair(qc, a, b):
    """Creates a bell pair in qc using qubits a & b"""
    qc.h(a)  # Put qubit a into state |+>
    qc.cx(a, b)  # CNOT with a as control and b as target

def alice_gates(qc, psi, a):
    qc.cx(psi, a)  # CNOT gate applied to q1, controlled by psi (q0)
    qc.h(psi)  # psi is q0 in our our quantum circuit

def measure_and_send(qc, a, b, crz, crx):
    """Measures qubits a & b and 'sends' the results to Bob"""
    qc.barrier()
    qc.measure(a, crz)
    qc.measure(b, crx)

def bob_gates(qc, qubit, crz, crx):
    # Here we use c_if to control our gates with a classical
    # bit instead of a qubit
    qc.x(qubit).c_if(crx, 1)  # Apply gates if the registers
    qc.z(qubit).c_if(crz, 1)  # are in the state '1'

def run_circuits(values):

    # Initialize the quantum circuit for the image
    # Pixel position
    idx = QuantumRegister(2, 'idx')
    # grayscale pixel intensity value
    intensity = QuantumRegister(8,'intensity')
    #teeleportation qubits (bellpair)
    teleport = QuantumRegister(2,'teleport')
    # classical register
    cr = ClassicalRegister(10, 'cr')
    crz = ClassicalRegister(1, name="crz") # and 2 classical bits
    crx = ClassicalRegister(1, name="crx") # in 2 different registers
    # create the quantum circuit for the image
    qc_image = QuantumCircuit(intensity, idx, teleport ,cr, crx, crz)

    # set the total number of qubits
    num_qubits = qc_image.num_qubits

    # Optional: Add Identity gates to the intensity values
    for idx in range(intensity.size):
        qc_image.i(idx)

    # Add Hadamard gates to the pixel positions
    qc_image.h(8)
    qc_image.h(9)
    qc_image.barrier()

    # Encode the first pixel, 00
    if (values[0]=='00000000'):
        pass
    else:
        qc_image.x(qc_image.num_qubits - 1 - 2)
        qc_image.x(qc_image.num_qubits - 2 - 2)
        for idx, px_value in enumerate((values[0])[::-1]):
            if (px_value == '1'):
                qc_image.ccx(num_qubits - 1 - 2, num_qubits - 2 - 2, idx)
        qc_image.x(qc_image.num_qubits - 1 - 2)
        qc_image.x(qc_image.num_qubits - 2 - 2)
        #qc_image.x(qc_image.num_qubits - 1 - 2)
    qc_image.barrier()
    qc_image.draw()

    # Encode the second pixel
    # Add the NOT gate to set the position at 01:
    qc_image.x(qc_image.num_qubits-1-2)
    for idx, px_value in enumerate((values[1])[::-1]):
        if(px_value=='1'):
            qc_image.ccx(num_qubits-1-2, num_qubits-2-2, idx)

    qc_image.x(num_qubits-1-2)
    qc_image.barrier()



    # Encode the third pixel
    # Add the 0CNOT gates, where 0 is on X pixel:
    qc_image.x(num_qubits-2-2)
    for idx, px_value in enumerate((values[2])[::-1]):
        if(px_value=='1'):
            qc_image.ccx(num_qubits-1-2, num_qubits-2-2, idx)

    qc_image.x(num_qubits-2-2)
    qc_image.barrier()


    # Encode the 4th pixel
    # Add the CCNOT gates:
    for idx, px_value in enumerate((values[3])[::-1]):
        if(px_value=='1'):
            qc_image.ccx(num_qubits-1-2,num_qubits-2-2, idx)
    qc_image.barrier()

    # build teleportation pairs
    for i in range(0,num_qubits-2):
        create_bell_pair(qc_image, 10, 11)
        qc_image.barrier()
        alice_gates(qc_image, i, 10)
        measure_and_send(qc_image, i, 10, crz, crx)
        qc_image.barrier()
        bob_gates(qc_image, 11, crz, crx)
        qc_image.measure(11, cr[i])
        qc_image.reset(qc_image.qubits[10:12])
        qc_image.barrier()


    shot_count = 40 #20 failed often. 30 failed rarely. 40 should be safe, and not too slow.
    aer_sim = Aer.get_backend('aer_simulator')
    t_qc_image = transpile(qc_image, aer_sim)
    qobj = assemble(t_qc_image, shots=shot_count)
    job_neqr = aer_sim.run(qobj)
    result_neqr = job_neqr.result()
    counts_neqr = result_neqr.get_counts()

    # 4 pixel coordinates: [00, 01, 10, 11]
    # 16 maximum expected measurement possibilities (ignoring 2 classical registers used for teleportation)
    counts=[0,0,0,0]

    for key in counts_neqr.keys():
        if (key[4:]=='00'+values[0]):
            counts[0]=counts[0]+counts_neqr[key]
        elif (key[4:]=='01'+values[1]):
            counts[1]=counts[1]+counts_neqr[key]
        elif (key[4:] == '10'+values[2]):
            counts[2] = counts[2] + counts_neqr[key]
        elif (key[4:]=='11'+values[3]):
            counts[3]=counts[3]+counts_neqr[key]

    # the array we will return from the def that does this entire thing:
    process=[]

    # Used to verify this assumption: we have enough shots and low enough noise such that
    # we expect with very high probability to only have 4 unique measurement outcomes,
    # that is: one intensity (encoded in 8 bits) for each of 4 pixel coordinates.
    #print(sum(counts), " vs ", shot_count)
    #print("-")
    #print(counts[0],counts[1],counts[2],counts[3])
    if( (counts[0]+counts[1]+counts[2]+counts[3])!=shot_count):
        print("ERROR: some intensity measurement possibilities not accounted for, examine.")
        exit()
    elif (counts[0]<=0 or counts[1]<=0 or counts[2]<=0 or counts[3]<=0):
        print("ERROR: insufficient shots in circuit simulation to check all expected pixel intensities from measurements.")
        exit()
    else:
        # we have 4 unique measurement outcomes, which indicates statistical significance
        process=[values[0],values[1],values[2],values[3]]
        pass

    #print(process)
    #print(sum(counts))
    return process

    # when this is all inside a function, return process[], which will then be converted to bytes again
    # and appended to the appropriate final recreated image array.

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

def encode_message(bits, bases):
    message = []
    for i in range(len(bits)):
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
    measurements = []
    for q in range(len(bases)):
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
    for q in range(len(bits)):
        if a_bases[q] == b_bases[q]:
            # If both used the same basis, add
            # this to the list of 'good' bits
            good_bits.append(bits[q])
    return good_bits

def get_bb84_keys():

    # Number of bits to begin BB84 protocol with
    n = 100

    # Step 1 - alice creates n random (classical) bits and bases (X/Z)
    alice_bits = randint(2, size=n)
    alice_bases = randint(2, size=n)

    # Step 2 - alice encodes the bit values into qubits for each random basis chosen
    message = encode_message(alice_bits, alice_bases)

    # Step 3 - bob picks n random bases (X/Z), bob measures the qubits that alice generated in step 2
    bob_bases = randint(2, size=n)
    bob_results = measure_message(message, bob_bases)

    # Step 4 - alice and bob sift their keys with the information made publicly available:
    # their random basis choices.
    bob_key = remove_garbage(alice_bases, bob_bases, bob_results)
    alice_key = remove_garbage(alice_bases, bob_bases, alice_bits)

    # Step 5 - random pairs of bits in their keys are checked against each other and then removed from the keys
    # as they are no longer secret. This is used to detect the influence of potential eavesdroppers and noise.
    # A larger sample_size is safer, but results in smaller keys.
    sample_size = 20
    bit_selection = randint(n, size=sample_size)
    bob_sample = sample_bits(bob_key, bit_selection)
    alice_sample = sample_bits(alice_key, bit_selection)

    # error handling to detect eavesdroppers, noise, and any other issues in the protocol thus far
    if (bob_sample != alice_sample):
        print("WARNING: Key samples do not match. Noise or eavesdropper on the quantum channel is  present")
        exit()
    elif (bob_key!=alice_key):
        print("WARNING: Keys do not match. Abort quantum key distribution protocol")
        exit()

    # converting int key to strings
    string_ints = [str(int) for int in alice_key]
    str_of_ints = "".join(string_ints)

    # alice's finalized key
    a_key = str_of_ints

    # converting int key to strings
    string_ints = [str(int) for int in bob_key]
    str_of_ints = "".join(string_ints)

    # bob's finalized key
    b_key = str_of_ints

    # only need key of 8 bits, as we are encrypting/decrypting 1 byte with them
    a_key = a_key[0:8]
    b_key = b_key[0:8]

    return a_key, b_key

def xor_encrypt(msg, key):
    encrypted = int(msg, 2)^int(key,2)
    return bin(encrypted)[2:].zfill(len(msg))


# First, use BB84 to create and distribute keys to alice and bob
keys = get_bb84_keys()
a_key = keys[0]
b_key = keys[1]

# open image in the first folder (alice's folder), read its contents into a bytearray
with open("trythis - Copy.jpg", "rb") as image:
    f = image.read()
    b = bytearray(f)

bi = []
i = 0
# convert from int to string of 8 bits, and encrypt using alice's key
for xx in b:
    bi.append(format(b[i],'08b'))
    bi[i] = xor_encrypt(bi[i],a_key)
    i+=1

i = 0
j = 0

# group of bytes to be teleported, 4 at a time
to_teleport = []
c = []

# split this into groups of 4, then send the array of 4 bytes to process
for val in bi:
    to_teleport.append(val)
    i+=1

    # Teleporting 4 bytes at a time
    if i==4:
        i=0
        # 4 bytes obtained via teleportation
        tp=run_circuits(to_teleport)

        # decrypt format each teleported byte
        for x in tp:

            # decrypt using bob's key and add to list:
            x = xor_encrypt(x,b_key)
            c.append(int(x,2))

            # % completion tracker for user's awareness
            print(str(100*float(j)/float(len(bi)))[0:4]+" % completed")
            j+=1

        # reset array of 4 bytes each time it is teleported
        to_teleport = []


print("Teleportation and decryption of image complete.")

# hardcoding this last one because real file isn't multiple of 4 pixels
c.append(int('11011001',2))

# convert teleported/decrypted array of bytes to bytearray type
c = bytearray(c)

# Create new image using teleported and decrypted bytearray
image2 = Image.open(io.BytesIO(c))
Image.LOAD_TRUNCATED_IMAGES = True

# save image in destination folder (Bob's folder)
image2.save("final2.jpg")

# make this more explicit, name of the folders, and the image file
print("Image has been saved in destination folder.")