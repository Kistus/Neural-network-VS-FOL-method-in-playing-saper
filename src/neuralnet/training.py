from neuralnet.datagenerator import generate_for_params
from itertools import cycle
import numpy as np
import tensorflow as tf


def get_shuffle_positions(selected0, selected1):
    total = selected0 + selected1
    positions = np.array(range(total))
    shuffled_positions = np.copy(positions)
    np.random.shuffle(shuffled_positions)
    in_class0 = positions < selected0
    return shuffled_positions[in_class0], shuffled_positions[~in_class0]


def get_data(training_samples, test_samples):
    samples = training_samples + test_samples
    x_vals, y_vals = generate_for_params(
        cycle([(9, 12), (9, 11), (9, 10), (9, 9), (9, 8), (9, 9), (9, 15), (9, 21), (9, 5), (9, 3), (9, 2)]), samples)
    training_positions, test_positions = get_shuffle_positions(training_samples, test_samples)
    training_data = x_vals[training_positions], y_vals[training_positions]
    test_data = x_vals[test_positions], y_vals[test_positions]
    return training_data, test_data

# Sequential model is obvious, but parameters for hidden layers are not obvious


# model = tf.keras.Sequential([
#     tf.keras.layers.InputLayer(input_shape=(162,)),
#     tf.keras.layers.Dense(81*9, activation='sigmoid'),
#     tf.keras.layers.Dense(81*9, activation='sigmoid'),
#     tf.keras.layers.Dropout(0.2),
#     tf.keras.layers.Dense(81, activation='relu')
# ])
#
#
# # Loss function probably should be corrected
# model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
#
#
# print('Generating data samples')
# # The more data samples, the longer it takes to generate and train, but it is generally better
# # (but over fitting may occur)
# (x_train, y_train), (x_test, y_test) = get_data(10, 20)
# print('Training neural network')
# model.fit(x_train, y_train, epochs=25)
# print('Evaluating neural network')
# model.evaluate(x_test, y_test)
# model.save('model2.h5')

n = 100000
x_vals, y_vals = generate_for_params(
    cycle([(9, 12), (9, 11), (9, 10), (9, 9), (9, 8), (9, 9), (9, 15), (9, 21), (9, 5), (9, 3), (9, 2)]), n)
shuffle_positions, _ = get_shuffle_positions(n, 0)
x_vals = x_vals[shuffle_positions]# 1000, 162
y_vals = y_vals[shuffle_positions]# 1000, 81
np.save('X.npy', x_vals)
np.save('Y.npy', y_vals)
