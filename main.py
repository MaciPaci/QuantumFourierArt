import numpy as np
import cv2
import argparse
from decouple import config
from qiskit import QuantumCircuit, Aer, execute
from qiskit_ibm_provider import IBMProvider
import matplotlib.pyplot as plt
from QFT import qft, inverse_qft

number_of_qubits = 8


def get_parser():
    arg_parser = argparse.ArgumentParser(description='Description of your script')
    arg_parser.add_argument('image_path', help='The path to the image', metavar="path", type=str)
    arg_parser.add_argument('resolution', help='Output resolution of the image', metavar="resolution", type=int)
    return arg_parser


def get_backends():
    IBMProvider.save_account(api_token, overwrite=True)
    sim = Aer.get_backend("qasm_simulator")
    real = IBMProvider().get_backend("ibm_brisbane")
    return sim, real


def prepare_vector(image_path, resolution):
    image = cv2.imread(image_path)
    new_image = cv2.resize(image, (resolution, resolution))
    gray = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
    vector = gray.flatten()
    return vector


def calculate_qft():
    pixel_list = []
    for i, element in enumerate(vector):
        qc = QuantumCircuit(number_of_qubits)
        binary_string = format(element, '08b')
        for j, bit in enumerate(binary_string):
            if bit == '1':
                qc.x(j)
        qft(qc, number_of_qubits)
        inverse_qft(qc, number_of_qubits)

        qc.measure_all()

        job = execute(qc, real, shots=1)
        result = job.result()
        counts = result.get_counts(qc)

        pixel_value = int(list(counts.keys())[0], 2)
        print(i, " ", pixel_value)
        pixel_list.append(pixel_value)
    return pixel_list


def save_image(pixel_list, resolution):
    arr = np.array(pixel_list).reshape(resolution, resolution)
    plt.imshow(arr, cmap='gray')
    plt.savefig('./output_img/' + image_path.split('/')[-1].split('.')[0] + str(resolution) + '.jpg')


if __name__ == '__main__':
    args = get_parser().parse_args()
    image_path = args.image_path
    resolution = args.resolution
    api_token = config('API_TOKEN')
    sim, real = get_backends()

    vector = prepare_vector(image_path, resolution)

    pixel_list = calculate_qft()

    save_image(pixel_list, resolution)
