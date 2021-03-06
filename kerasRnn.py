import keras.layers as L
import keras.models as M
import keras

import pickle
import numpy as np

batch_size = 32
num_classes = 10
epochs = 200

# The inputs to the model.
# We will create two data points, just for the example.
data_x = np.array([
    # Datapoint 1
    [
        # Input features at timestep 1
        [1, 2, 3],
        # Input features at timestep 2
        [4, 5, 6]
    ],
    # Datapoint 2
    [
        # Features at timestep 1
        [7, 8, 9],
        # Features at timestep 2
        [10, 11, 12]
    ]
])

# The desired model outputs.
# We will create two data points, just for the example.
data_y = np.array([
    # Datapoint 1
    # Target features at timestep 2
    [105, 106, 107, 108],
    # Datapoint 2
    # Target features at timestep 2
    [205, 206, 207, 208]
])
# Each input data point has 2 timesteps, each with 3 features.
# So the input shape (excluding batch_size) is (2, 3), which
# matches the shape of each data point in data_x above.
model_input = L.Input(shape=(1292,128))

# This RNN will return timesteps with 4 features each.
# Because return_sequences=True, it will output 2 timesteps, each
# with 4 features. So the output shape (excluding batch size) is
# (2, 4), which matches the shape of each data point in data_y above.
model_output = L.LSTM(num_classes, return_sequences=False)(model_input)

# Create the model.
model = M.Model(input=model_input, output=model_output)

# You need to pick appropriate loss/optimizers for your problem.
# I'm just using these to make the example compile.
opt = keras.optimizers.rmsprop(lr=0.0001)
model.compile(optimizer=opt, loss="mean_squared_error", metrics=['accuracy'])

dataPath = '/data/hibbslab/jyang/tzanetakis/ver6.0/'
x_train = pickle.load(open(dataPath + 'x_train_mel.p', 'rb'))
y_train = pickle.load(open(dataPath + 'y_train_mel.p', 'rb'))
x_test = pickle.load(open(dataPath + 'x_test_mel.p', 'rb'))
y_test = pickle.load(open(dataPath + 'y_test_mel.p', 'rb'))


# Train
model.fit(x_train, y_train, batch_size=batch_size, epochs = epochs, validation_data=(x_test, y_test), shuffle=True)
