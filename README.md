# send_file // Task 4

######################## Introduction ########################

This program serves as Tyler Cowan's application for the QOSF Mentorship Program. 
Thank you for your consideration, and please don't hesitate to 
reach out if you have any questions, at tylergcowan@gmail.com. 

send_file is executed from picture.py, and accomplishes the following:

1. 2 identical encryption keys are generated using the BB84 protocol. Function: get_bb84_keys()
2. From mentor folder (origin), the image is imported as a bytearray.
3. The image data is then encrypted using XOR on each byte, which represents intensity values for each pixel in the grayscale image
4. The byte data is then segmented into groups of 4 and converted into a quantum circuit in run_circuits() using the Novel Enhanced Quantum Representation for image processing.
5. This circuit is then teleported by reusing a bell-pair, qubit by qubit, to the destination location
6. The measurement outcomes are tallied and analyzed for statistical significance, checking for the influence of noise and eavesdropping at any point in the process, including the BB84 protocol
7. Once it is confirmed that the intensity bytes have been teleported without alteration for each pixel, the full image data is decrypted using the second (but identical) key generated in step 1.
8. Finally, the teleported and decrypted image is reassembled in the destination mentor folder without any changes.
9. A boolean is returned upon completion of the program to inform the user of its success in sending the image file.

As a photographer and physicist, I think this method of encryption, teleportation, and quantum circuit image representation is very fascinating. I look forward to seeing it used in the coming years for more secure encryption, and NEQR opens up many unique image transformations, which is a growing area of study.


######################## Getting Started ########################

The following packages will need to be installed in order to run this program:

- qiskit
- Pillow (imported instead of PIL)
- numpy

It can be executed by running: 

- python picture.py

Example inputs to send_file:
* mentee_path = r".\mentee\\"
* file_name = "qosf.jpg"
* mentor_path = r".\mentor\\"

Which is executed as follows: send_file(mentee_path, file_name, mentor_path).

If mentor_path does not exist it will be created. 

########################### Analysis ############################

In the absence of noise and eavesdropping on the quantum channel, this process is able to perfectly send the image in the mentee folder to the mentor folder. Noise or eavesdropping on the quantum channel could result in keys that are not identical after using the BB84 protocol, making perfect decryption impossible. This is because eavesdropping can occur in between step 1 and 2, before bob (or the recipient) measures the qubits prepared by alice (the sender). This eavesdropping can be detected during the sampling stage, which is undertaken trivially in this program. This is a prime benefit of the BB84 protocol for encryption using XOR one-time pad - eavesdropping can be detected, which prevents the secrecy of the encrypted message from being tainted.

NEQR was chosen over FRQI to represent the encrypted image as a quantum circuit because it is quadratically faster, and the image can be retrieved via measurement accurately (assuming low noise, no eavesdropping, and sufficient simulator shots) as opposed to probabilistically. Representing a digital image as a quantum circuit opens up the possibility of using entanglement, superposition, and interference to create faster versions of classical algorithms. However, noise, decoherence can result in the encrypted image being transmitted imperfectly. Given the generalizable nature of NEQR, it is a benefit that an encrypted or unencrypted message alike can be sent. Breaking this protocol into pixel groups of 4 also means you can use a quantum computer with fewer qubits to execute this circuit. Any changes to the image may only be present in a small section of it, rather than the entire image this way as well. 

In order to reduce the runtime of this program, the qosf logo was made smaller, meaning fewer pixels had to be encoded in the quantum circuit. Additionally, the image has been converted to grayscale, resulting in only 8 intensity qubits being needed, rather than 24, which would be needed to represent the full RGB intensities. Lastly, within send_file the image data is segmented into groups of 4 bytes (intensity of each pixel) in order to reduce the number of qubits needed in each quantum circuit. My computer struggled to quickly simulate a quantum circuit of this size, with enough shots to be statistically significant. 

Despite using 40 shots for each circuit Aer simulation, the program technically has a nonzero chance to fail, at which point it should be re-run, or the number of shots should be increased. This would make the program slower but more reliable. The failure could be due to one of the four unique measurement outcomes (of 10 qubits) not being present in the final dictionary. Each has a roughly 25% chance of being measured (corresponding to the 8-bit intensity of each pixel, which is represented with a grid of 00 10 01 and 11), so 4 shots minimum are needed for each pixel. This is very risky, and so 40 are used. I did not experience any program failures using 40 shots, but I did ocassionally using 30. 

Overall, I think this method is slow but idealized when simulated on my laptop. On a real quantum computer and channel, noise and eavesdropping could result in the image being compromised, but this interference could be detected at multiple points. This is a massive security benefit. Ultimately, representing an image with a quantum circuit enables us to take advantage of the unique properties of quantum states, and significantly speed up algorithms like edge detection. I think this simulation serves as an effective proof of concept, and it should be explored further. The complexity will increase significantly but not overwhelmingly as larger and color images are encrypted, encoded, and teleported. 






########################### Citations ###########################

- BB84 Protocol: https://qiskit.org/textbook/ch-algorithms/quantum-key-distribution.html

- Quantum Teleportation: https://qiskit.org/textbook/ch-algorithms/teleportation.html

- Quantum Image Processing: https://qiskit.org/textbook/ch-applications/image-processing-frqi-neqr.html

Thank you to the contributors to these sources, I could not have accomplished
this task without you!
