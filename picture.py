from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, Aer, transpile, assemble
import PIL.Image as Image #NOTE: Pillow imported instead of PIL
import io
from numpy.random import randint
import numpy as np

def create_bell_pair(qc, a, b):
    """Creates a bell pair in the quantum image circuit using qubits a & b in quantum circuit qc.
    This is done by moving one qubit into the X basis with an H gate, and then applying a CNOT
    gate to the other qubit, using the first qubit as a control"""
    qc.h(a)  # Put qubit a into state |+> using the hadmard gate
    qc.cx(a, b)  # CNOT with the a qubit as the control and b qubit as the target

def alice_gates(qc, b, a):
    """Alice applies the CNOT gate to one qubit, which is contrlled by
    the qubit she wants to send to bob. The control qubit is also
    put through a hadamard gate."""
    qc.cx(b, a)  # CNOT gate is applied to qubit a, controlled by qubit b
    qc.h(b)  # hadamard gate is applied to qubit b

def measure_and_send(qc, a, b, crz, crx):
    """Alice measures qubits a and b, puts the results into the classical registers crz and crx.
    These classical results are trasnmitted to Bob through a classical channel."""
    qc.barrier()
    # crz and crx are the associated classical registers for each teleportation/bell pair qubit.
    qc.measure(a, crz)
    qc.measure(b, crx)

def bob_gates(qc, qubit, crz, crx):
    """Bob applies gates to the qubit which will receive the teleported qubit's state, based on the
    classical bits he recieved from alice. The options are:
    00: nothing
    01: X Gate
    10: Z Gate
    11: ZX Gate
    """
    # c_if is used to control the gates with a bit, not a qubit
    qc.x(qubit).c_if(crx, 1)  # Only apply gates when the classical registers are in the state '1'
    qc.z(qubit).c_if(crz, 1)

def run_circuits(values):
    """Initialize an NEQR quantum circuit to represent the 2x2 image
    this function receives in the form of intensity bytes for each pixel.

    Then, reuse 2 qubits to form bell-pairs to teleport each of the 10 NEQR qubits from
    alice to bob, one by one.

    Simulate this quantum circuit with the Aer simulator, and recover the measurement outcomes
    for the 8-bit intensity for each pixel position, encoded in 2 bits.
    :param: 4 8-bit intensity values for each pixel 00/01/10/11 in this image subset
    :return: the now-teleported 2x2 image in the form of a length 4 array of bytes"""

    # Initialize the quantum circuit representation for 4 pixels of the image.

    # This process is split into groups of 4 pixels to simulate fewer qubits at a time,
    # in order to conserve computing resources and to provide the user of progress
    # updates on the teleportation. Only 2 qubits are needed for position this way.

    # Pixel position qubits (4 positions represented as 00, 01, 10, and 11)
    idx = QuantumRegister(2, 'idx')

    # pixel intensity qubits (grayscale, requires 8 bits for 1 to 255)
    intensity = QuantumRegister(8,'intensity')

    # bell pair qubits for teleporting each of the 10 NEQR qubits above
    teleport = QuantumRegister(2,'teleport')

    # classical registers for measurements to be recorded in during simulation of quantum circuit
    cr = ClassicalRegister(10, 'cr') # -> for 10 NEQR qubits
    crz = ClassicalRegister(1, name="crz") # -> for 1 teleportation qubit
    crx = ClassicalRegister(1, name="crx") # -> for 1 more teleportation qubit

    # create the quantum circuit of the 4 pixel image. 3 quantum registers, 3 classical.
    qc_image = QuantumCircuit(intensity, idx, teleport, cr, crx, crz)

    # get the total number of qubits in this circuit
    num_qubits = qc_image.num_qubits

    # Use hadamard gate on pixel position qubits to induce superposition, which will allow us
    # to take advantage of every position in the 2x2 image (subset) at once.
    qc_image.h(8)
    qc_image.h(9)

    # barriers are used to delineate sections of the quantum circuit
    qc_image.barrier()

    # The 1st pixel, 00, is encoded into the image circuit.
    # Make the forthcoming CNOT gate(s) trigger for 00 pixel by wrapping with X gates on pixel qubits.
    # This X gate wrapping is undertaken for each pixel, except for position 11 (functioning as a default)
    qc_image.x(qc_image.num_qubits-3)
    qc_image.x(qc_image.num_qubits-4)

    # Add CNOT gate to each targeted intensity qubit in the byte with qubit controls on pixel qubits (2).
    # Bit values are reversed so that the measurements are in the order one expects.
    for idx, px_value in enumerate((values[0])[::-1]):
        if (px_value == '1'):
            qc_image.ccx(num_qubits-3, num_qubits-4, idx)

    # end of the X gate wrapping for pixel 00, resetting the first 2
    qc_image.x(qc_image.num_qubits-3)
    qc_image.x(qc_image.num_qubits-4)

    qc_image.barrier()

    # The 2nd pixel, 01, is encoded into the image circuit.
    # For this pixel, the control must be a combination of 0 and 1 to trigger the CNOT gate, hence the X gates.
    qc_image.x(qc_image.num_qubits-3)

    # Add CNOT gate to each targeted intensity qubit in the byte with qubit controls on pixel qubits (2)
    for idx, px_value in enumerate((values[1])[::-1]):
        if(px_value=='1'):
            qc_image.ccx(num_qubits-3, num_qubits-4, idx)

    # Finish X gate wrap of pixel 01, resetting the first one
    qc_image.x(num_qubits-3)

    qc_image.barrier()

    # The 3rd pixel, 10, is encoded into the image circuit
    # As with pixel 2, we want the CNOT gate to trigger when control is a combination of 1 and 0.
    qc_image.x(num_qubits-4)

    # Add CNOT gate to each targeted intensity qubit in the byte with qubit controls on pixel qubits (2)
    for idx, px_value in enumerate((values[2])[::-1]):
        if(px_value=='1'):
            qc_image.ccx(num_qubits-3, num_qubits-4, idx)

    # Finish X gate wrap of pixel 10, resetting the first one
    qc_image.x(num_qubits-4)

    qc_image.barrier()

    # The 4th pixel, 11, is encoded into the image circuit. No X gate wrapping needed for 11.
    # Add CNOT gate to each targeted intensity qubit in the byte with qubit controls on pixel qubits (2)
    for idx, px_value in enumerate((values[3])[::-1]):
        if(px_value=='1'):
            qc_image.ccx(num_qubits-3,num_qubits-4, idx)

    qc_image.barrier()

    #########################################################################################
    # At this stage, the NEQR circuit representation for the 2x2 image subset has been built.
    #########################################################################################

    # Next, we utilize the 2 teleportation qubits to teleport each NEQR qubit from alice to bob.
    # This process is repeated for each of the 10 NEQR qubits (8 intensity, 2 pixel position)
    # with the teleportation qubits resetting each time in order to be reused.
    for i in range(0,num_qubits-2):

        # First, a bell pair is created by a third party (let's call them Eve!).
        # One of each of these entangled qubits is given to alice and bob.
        create_bell_pair(qc_image, 10, 11)

        qc_image.barrier()

        # Alice applies a CNOT gate to her bell pair qubit, controlled by the
        # qubit state we want to teleport to bob. H gate is applied to the latter qubit as well.
        alice_gates(qc_image, i, 10)

        # Alice measures the teleportation qubit (bell-pair half) that she owns, and the qubit
        # state she wants to send to Bob. These results are stored in classical bits and sent to Bob.
        measure_and_send(qc_image, i, 10, crz, crx)

        qc_image.barrier()

        # Lastly, Bob chooses which gates to apply to his bell-pair half (teleportation qubit) based on
        # the classical bits he receives from Alice.
        bob_gates(qc_image, 11, crz, crx)

        # Measure bob's qubit (which has successfully taken on the state of alice's intended qubit to send).
        # In this case, it will contain information about the 8-bit intensity of each of 4 pixels (2 bits).
        qc_image.measure(11, cr[i])

        # Reset the bell-pair qubits created by Eve so they can be reused to continue teleporting
        # the entire NEQR represented image susbet (2x2). 10 qubits in total will be teleported.
        qc_image.reset(qc_image.qubits[10:12])

        qc_image.barrier()

    #########################################################################################
    # The full NEQR and teleportation circuit has been built. Time to simulate it:
    #########################################################################################

    # Run the NEQR image representation and subsequent teleportation and measurements with the Aer simulator
    # 20 shots failed often. 30 failed rarely. 40 should be safe, and not too time-consuming.
    shot_count = 40
    aer_sim = Aer.get_backend('aer_simulator')
    t_qc_image = transpile(qc_image, aer_sim)
    qobj = assemble(t_qc_image, shots=shot_count)
    job_neqr = aer_sim.run(qobj)
    result_neqr = job_neqr.result()

    # dictionary with all measurement results for the total 12 classical register bits
    counts_neqr = result_neqr.get_counts()

    # measurement counts for each intensity, each likely mapping onto 1 of 4 pixel coordinates: [00, 01, 10, 11]
    counts=[0,0,0,0]

    # Check dictionary keys for the 4 unique measurement outcomes (excluding the crz/crx classical registers).
    # These 4 unique measurement outcomes, roughly equal in their prevalence, assign pixel location with the
    # first 2 bits, and intensity with the following 8 bits. The first 2 bits in these measurements may be
    # excluded from our analysis, as they are a relic of the teleportation qubit measurements.
    for key in counts_neqr.keys():

        if (key[4:]=='00'+values[0]):
            counts[0]=counts[0]+counts_neqr[key]

        elif (key[4:]=='01'+values[1]):
            counts[1]=counts[1]+counts_neqr[key]

        elif (key[4:] == '10'+values[2]):
            counts[2] = counts[2] + counts_neqr[key]

        elif (key[4:]=='11'+values[3]):
            counts[3]=counts[3]+counts_neqr[key]

    # 4 encoded then teleported bytes, to be returned, which are to be deduced from counts of measurement
    # simulations of the quantum circuit representation of the 2x2 image.
    processed = []

    # In this idealized simulation, we expect to have enough shots and low noise such that there are only
    # 4 unique measurement outcomes, corresponding to the 8-bit intensity of each of 2-bit pixel positions.
    if(sum(counts) != shot_count):
        # Counts for the 4 unique/expected measurement outcomes must equal the overall simulation shot count.
        # Otherwise, we have not accounted for every possible measurement of the simulated quantum circuit.
        # This is only true in this idealized simulation.
        print("ERROR: some measurement possibilities not accounted for in the count. Please check counts_neqr.")
        print("EXITING...")
        exit()
    elif (counts[0]<=0 or counts[1]<=0 or counts[2]<=0 or counts[3]<=0):
        # If insufficient shots are used during the Aer simulation, one may not measure at least one
        print("ERROR: insufficient shots in circuit simulation to check all expected pixel intensities from measurements.")
        print("Please try again with higher shot count. 100 shots is vanishingly unlikely to fail.")
        print("EXITING...")
        exit()
    else:
        # We have 4 unique measurement outcomes for the 10 NEQR qubits, which indicates statistical significance.
        # In the absence of noise (and even noise/eavesdropping during the QKD phase), if there is only 1 unique
        # intensity measurement outcome for each pixel position, we can assume the initial byte values have been
        # 100% accurately encoded into the quantum circuit, teleported, and ultimately measured. In the presence of
        # noise, this process would need to employ tolerances on the measurement counts, and more statistical analysis
        # to determine the best intensity value for each pixel.
        processed = [values[0],values[1],values[2],values[3]]

    return processed

def sample_bits(bits, selection):
    """
    Alice and bob randomly compare a chosen number of bits in their keys in order to
    detect the presence of an eavesdropper, or the influence of noise in the quantum channel. 
    :return: alice or bob's choice of bits which were sampled/compared, then discarded.
    """
    sample = []
    for i in selection:
        # np.mod ensures we stay in bits range
        i = np.mod(i, len(bits))
        # pop out index 'i' element
        sample.append(bits.pop(i))
    return sample

def encode_message(bits, bases):
    """
    Alice encodes each bit onto a qubit using the basis X or Z inputted (randomly).
    0 maps to Z basis and 1 maps to X basis.
    :return: list of quantum circuits, which represent alice's messsage to bob.
    """
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
    """
    Bob measures each qubit sent to him by Alice in a randomly chosen
    basis (X or Z), then stores this classical information.
    :return: list of measurements that bob performed
    """
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
    """
    Sift alice and bob's keys by matching the random basis choices
    each of them chose. Throw away bits that were not randomly measured/encoded
    with the same basis.
    :return: list of bits that were measured/chosen by alice/bob
    with the same basis (X or Z).
    """
    good_bits = []
    for q in range(len(bits)):
        if a_bases[q] == b_bases[q]:
            # If both used the same basis, add
            # this to the list of 'good' bits
            good_bits.append(bits[q])
    return good_bits

def get_bb84_keys():
    """
    BB84 is a quantum key distribution protocol used to distribute identical (ideally)
    keys to alice and bob, using a quantum channel and a classical information channel.
    :return: alice and bob's completed bit keys to be used for encryption/decryption.
    """

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
    """
    Encrypt (or decrypt) a message using the key using XOR (the bitwise operator is: ^).
    :return: 8-bit encrypted or decrypted string
    """
    encrypted = int(msg, 2)^int(key,2)
    return bin(encrypted)[2:].zfill(len(msg))


# First, use BB84 to create and distribute binary keys to alice and bob
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
        # 4 bytes obtained via teleportation of encrypted NEQR circuit
        tp=run_circuits(to_teleport)

        # decrypt format each teleported byte
        for x in tp:

            # decrypt using bob's key and add to list:
            x = xor_encrypt(x,b_key)
            c.append(int(x,2))

            # % completion tracker for user's awareness
            print("Image teleportation "+str(100*float(j)/float(len(bi)))[0:4]+" % completed")
            j+=1

        # reset array of 4 bytes each time it is teleported
        to_teleport = []

print("Teleportation and decryption of image complete.")

# hardcoding this last pixel because the file isn't a multiple of 4 pixels
c.append(int('11011001',2))

# convert teleported/decrypted array of bytes to bytearray type
c = bytearray(c)

# Create new image using teleported and decrypted bytearray
image2 = Image.open(io.BytesIO(c))
Image.LOAD_TRUNCATED_IMAGES = True

# save image in destination folder (Bob's folder)
image2.save("final2.jpg")

print("Image has been saved in destination folder.")