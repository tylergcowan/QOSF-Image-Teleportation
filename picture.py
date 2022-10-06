import numpy as np
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, Aer, transpile, assemble
from qiskit.quantum_info import partial_trace, Statevector
import PIL.Image as Image
import io

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

    def create_bell_pair(qc, a, b):
        """Creates a bell pair in qc using qubits a & b"""
        qc.h(a) # Put qubit a into state |+>
        qc.cx(a,b) # CNOT with a as control and b as target

    def alice_gates(qc, psi, a):
        qc.cx(psi, a) # CNOT gate applied to q1, controlled by psi (q0)
        qc.h(psi) # psi is q0 in our our quantum circuit

    def measure_and_send(qc, a, b):
        """Measures qubits a & b and 'sends' the results to Bob"""
        qc.barrier()
        qc.measure(a,crz)
        qc.measure(b,crx)

    def bob_gates(qc, qubit, crz, crx):
        # Here we use c_if to control our gates with a classical
        # bit instead of a qubit
        qc.x(qubit).c_if(crx, 1) # Apply gates if the registers
        qc.z(qubit).c_if(crz, 1) # are in the state '1'

    # build teleportation pairs
    for i in range(0,num_qubits-2):
        create_bell_pair(qc_image, 10, 11)
        qc_image.barrier()
        alice_gates(qc_image, i, 10)
        measure_and_send(qc_image, i, 10)
        qc_image.barrier()
        bob_gates(qc_image, 11, crz, crx)
        qc_image.measure(11, cr[i])
        qc_image.reset(qc_image.qubits[10:12])
        qc_image.barrier()

    #print(qc_image)

    shot_count=30 #20 failed.
    aer_sim = Aer.get_backend('aer_simulator')
    t_qc_image = transpile(qc_image, aer_sim)
    qobj = assemble(t_qc_image, shots=shot_count)
    job_neqr = aer_sim.run(qobj)
    result_neqr = job_neqr.result()
    counts_neqr = result_neqr.get_counts()
    #print(counts_neqr)

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

with open("trythis - Copy.jpg", "rb") as image:
    f = image.read()
    b = bytearray(f)
    print(len(b))

bi=[]
i=0
for xx in b:
    bi.append(format(b[i],'08b'))  # GOAL OF THIS IS TO CONVERT FROM SAY, 216, TO LIKE 10010110
    i+=1

# BI IS READY TO BE SPLIT UP AND SENT INTO RUN_CIRCUITS


# this is how you'll do it. use this to convert at the end
#print(bi[1:5])
#print(type(bi[1]))
c1=[]
for x in bi:
    c1.append(int(x,2))
c1=bytearray(c1)

print(c1==b)

#print(c)
# use this
#image2 = Image.open(io.BytesIO(c))
#image2.save("new.jpg")
#exit()


c=[]
# split this into groups of 4, then send the array of 4 bytes to process
i=0
process=[]
for val in bi:
    process.append(val)
    i+=1
    if i==4:# send it pieces of 4 bytes
        i=0
        # INSERT CALLS TO PROCESS THE ARRAY OF 4
        #print(process)
        add_2_final_arr=run_circuits(process)
        #print(add_2_final_arr)

        for x in add_2_final_arr:
            c.append(int(x,2))
            print(int(x,2))

        process=[]

c.append(int('11011001',2)) # hardcoding this last one because real file isn't multiple of 4 pixels
c=bytearray(c)


image2 = Image.open(io.BytesIO(c))
Image.LOAD_TRUNCATED_IMAGES = True
image2.save("didthiswork.jpg")



