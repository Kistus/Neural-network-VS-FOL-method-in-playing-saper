import numpy as np
import tensorflow as tf
from neuralnet.transformer import NUM_OF_CLASSES, NUM_OF_NEIGHBOURS
from neuralnet.datamining import get_possible_inputs_for_game

INPUT_SHAPE = (NUM_OF_CLASSES * NUM_OF_NEIGHBOURS, )


def create_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.InputLayer(INPUT_SHAPE),
        tf.keras.layers.Dense(300, activation='sigmoid'),
        tf.keras.layers.Dense(1, activation='relu')
    ])
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
    return model


def join_datasets(size, mines, max_clicks, num_datasets):
    datasets_x = []
    datasets_y = []
    for _ in range(num_datasets):
        x_vals, y_vals = get_possible_inputs_for_game(size, mines, max_clicks)
        datasets_x.append(x_vals)
        datasets_y.append(y_vals)
    length = sum(map(lambda val: len(val), datasets_y))
    X = np.zeros((length, INPUT_SHAPE[0]))
    Y = np.zeros((length, 1))
    idx = 0
    for x_vals, y_vals in zip(datasets_x, datasets_y):
        for x, y in zip(x_vals, y_vals):
            X[idx] = x
            Y[idx] = y
            idx += 1
    return X, Y


def to_uniform_result_distribution(x_vals, y_vals):
    ones = int(y_vals.sum())
    zeros = len(y_vals) - ones
    selector = np.ones((len(y_vals, )), np.bool8)
    difference = abs(ones-zeros)
    element_to_remove = 1.0 if ones > zeros else 0.0
    i = 0
    j = 0
    while i < difference:
        if y_vals[j] == element_to_remove:
            i += 1
            selector[j] = False
        j += 1
    return x_vals[selector], y_vals[selector]


def shuffle_dataset(x_vals, y_vals):
    indexes = np.array(list(range(len(y_vals))))
    np.random.shuffle(indexes)
    return x_vals[indexes], y_vals[indexes]


def make_model():
    model = create_model()
    x_vals, y_vals = shuffle_dataset(*join_datasets(20, 20, 5, 100))
    x_test, y_test = shuffle_dataset(*join_datasets(20, 20, 5, 10))
    model.fit(x_vals, y_vals, epochs=20)
    model.evaluate(x_test, y_test)
    model.save('mymodel.h5')

if __name__ == '__main__':
    make_model()