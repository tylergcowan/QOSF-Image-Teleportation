import numpy as np
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, Aer, transpile, assemble
from qiskit.quantum_info import partial_trace, Statevector

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

# Initialize the quantum circuit
# Optional: Add Identity gates to the intensity values
for idx in range(intensity.size):
    qc_image.i(idx)

# Add Hadamard gates to the pixel positions
qc_image.h(8)
qc_image.h(9)

# Separate with barrier so it is easy to read later.
qc_image.barrier()
#print(qc_image)

values=[]
values.append('00000000')
values.append('01100100')
values.append('11001000')
values.append('11111111')

# Encode the first pixel, since its value is 0, we will apply ID gates here:

for idx in range(num_qubits-2):
    qc_image.i(idx)

qc_image.barrier()
qc_image.draw()


# Encode the second pixel whose value is (01100100):

# Add the NOT gate to set the position at 01:
qc_image.x(qc_image.num_qubits-1-2)

# We'll reverse order the value so it is in the same order when measured.
for idx, px_value in enumerate((values[1])[::-1]):
    if(px_value=='1'):
        qc_image.ccx(num_qubits-1-2, num_qubits-2-2, idx)

# Reset the NOT gate
qc_image.x(num_qubits-1-2)

qc_image.barrier()
#print(qc_image)


# Encode the third pixel whose value is (11001000):

# Add the 0CNOT gates, where 0 is on X pixel:
qc_image.x(num_qubits-2-2)
for idx, px_value in enumerate((values[2])[::-1]):
    if(px_value=='1'):
        qc_image.ccx(num_qubits-1-2, num_qubits-2-2, idx)
qc_image.x(num_qubits-2-2)


qc_image.barrier()
#print(qc_image)

# Encode the third pixel whose value is (10101010):


# Add the CCNOT gates:
for idx, px_value in enumerate(values[3]):
    if(px_value=='1'):
        qc_image.ccx(num_qubits-1-2,num_qubits-2-2, idx)

qc_image.barrier()

################### do the first and second example manually, then automate it with a loop! ##########

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


print(qc_image)

print('Circuit dimensions')
print('Circuit depth: ', qc_image.decompose().depth())
print('Circuit size: ', qc_image.decompose().size())

aer_sim = Aer.get_backend('aer_simulator')
t_qc_image = transpile(qc_image, aer_sim)
qobj = assemble(t_qc_image, shots=600) #set high but not too high thatit takes forever
job_neqr = aer_sim.run(qobj)
result_neqr = job_neqr.result()
counts_neqr = result_neqr.get_counts()
print('Encoded: 00 = 0')
print('Encoded: 01 = 01100100')
print('Encoded: 10 = 11001000')
print('Encoded: 11 = 1')
print(counts_neqr)


print(counts_neqr['0 1 1111111111'])







exit()




