from __future__ import print_function, division
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

num_epochs = 100
total_series_length = 50000
#truncated_backprop_length = 15
truncated_backprop_length = 129  #3 seconds
state_size = 4
#num_classes = 2
num_classes = 10
echo_step = 3
#batch_size = 5
batch_size = 500
#num_batches = total_series_length//batch_size//truncated_backprop_length
num_batches = 1292//truncated_backprop_length
num_layers = 3

def pad(arr):
    return np.append(arr, [0,1,0])

def loadData(dataPath):
    x_train = pickle.load(open(dataPath + 'x_train_mel.p', 'rb'))
    y_train = pickle.load(open(dataPath + 'y_train_mel.p', 'rb'))
    #x_test = pickle.load(open(dataPath + 'x_test_mel.p', 'rb'))
    #y_test = pickle.load(open(dataPath + 'y_test_mel.p', 'rb')) 
    return (x_train, y_train)

def generateData():
    x = np.array(np.random.choice(2, total_series_length, p=[0.5, 0.5]))
    y = np.roll(x, echo_step)
    y[0:echo_step] = 0

    x = x.reshape((batch_size, -1))  # The first index changing slowest, subseries as rows
    # new lines
    x = np.expand_dims(x, axis = 2)
    x = np.apply_along_axis(pad, 2, x)

    y = y.reshape((batch_size, -1))
    return (x, y)

#batchX_placeholder = tf.placeholder(tf.float32, [batch_size, truncated_backprop_length])
batchX_placeholder = tf.placeholder(tf.float32, [batch_size, truncated_backprop_length, 4])
print(batchX_placeholder.shape)
batchY_placeholder = tf.placeholder(tf.int32, [batch_size, truncated_backprop_length])

init_state = tf.placeholder(tf.float32, [num_layers, 2, batch_size, state_size])

state_per_layer_list = tf.unstack(init_state, axis=0)
rnn_tuple_state = tuple(
    [tf.nn.rnn_cell.LSTMStateTuple(state_per_layer_list[idx][0], state_per_layer_list[idx][1])
     for idx in range(num_layers)]
)

W2 = tf.Variable(np.random.rand(state_size, num_classes),dtype=tf.float32)
b2 = tf.Variable(np.zeros((1,num_classes)), dtype=tf.float32)

# Unpack columns
# inputs_series = tf.split(axis = 1, num_or_size_splits = truncated_backprop_length, value = batchX_placeholder)
inputs_series = tf.unstack(batchX_placeholder, axis=1)
labels_series = tf.unstack(batchY_placeholder, axis=1)


# Forward passes
stacked_rnn = []
for _ in range(num_layers):
    stacked_rnn.append(tf.nn.rnn_cell.LSTMCell(state_size, state_is_tuple=True))

cell = tf.nn.rnn_cell.MultiRNNCell(stacked_rnn, state_is_tuple=True)
states_series, current_state = tf.contrib.rnn.static_rnn(cell, inputs_series, initial_state=rnn_tuple_state)

logits_series = [tf.matmul(state, W2) + b2 for state in states_series] #Broadcasted addition
predictions_series = [tf.nn.softmax(logits) for logits in logits_series]

losses = [tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=labels) for logits, labels in zip(logits_series,labels_series)]
#total_loss = tf.reduce_mean(losses)
total_loss = tf.reduce_mean(losses[-1])

train_step = tf.train.AdagradOptimizer(0.3).minimize(total_loss)

def plot(loss_list, predictions_series, batchX, batchY):
    plt.subplot(2, 3, 1)
    plt.cla()
    plt.plot(loss_list)

    for batch_series_idx in range(5):
        one_hot_output_series = np.array(predictions_series)[:, batch_series_idx, :]
        single_output_series = np.array([(1 if out[0] < 0.5 else 0) for out in one_hot_output_series])

        plt.subplot(2, 3, batch_series_idx + 2)
        plt.cla()
        plt.axis([0, truncated_backprop_length, 0, 2])
        left_offset = range(truncated_backprop_length)
        plt.bar(left_offset, batchX[batch_series_idx, :], width=1, color="blue")
        plt.bar(left_offset, batchY[batch_series_idx, :] * 0.5, width=1, color="red")
        plt.bar(left_offset, single_output_series * 0.3, width=1, color="green")

    plt.draw()
    plt.pause(0.0001)


with tf.Session() as sess:
    sess.run(tf.initialize_all_variables())
    #plt.ion()
    #plt.figure()
    #plt.show()
    loss_list = []

    for epoch_idx in range(num_epochs):
        #x,y = generateData()
	x,y = loadData("/data/hibbslab/jyang/tzanetakis/ver6.0/")

        _current_state = np.zeros((num_layers, 2, batch_size, state_size))

        print("New data, epoch", epoch_idx)

        for batch_idx in range(num_batches):
            start_idx = batch_idx * truncated_backprop_length
            end_idx = start_idx + truncated_backprop_length

            #batchX = x[:,start_idx:end_idx]
            batchX = x[:,start_idx:end_idx, :]
            batchY = y[:,start_idx:end_idx]

            _total_loss, _train_step, _current_state, _predictions_series = sess.run(
                [total_loss, train_step, current_state, predictions_series],
                feed_dict={
                    batchX_placeholder: batchX,
                    batchY_placeholder: batchY,
                    init_state: _current_state
                })


            loss_list.append(_total_loss)

            if batch_idx%100 == 0:
                print("Step",batch_idx, "Batch loss", _total_loss)
                #plot(loss_list, _predictions_series, batchX, batchY)

plt.ioff()
plt.show()
