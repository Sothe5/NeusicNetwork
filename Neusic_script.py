import librosa as lb
import tensorflow as tf
import numpy as np
from IPython.display import clear_output
from random import randint
import pickle
import sys

#Initialize random biases
def create_biases(number_of_neurons, n_classes):
    biases = []
    #Hidden layers
    for i in range(len(number_of_neurons)):
        biases.append(tf.Variable(tf.random_normal([number_of_neurons[i]])))
    #Output Layer
    biases.append(tf.Variable(tf.random_normal([n_classes])))
    return biases

#Initialize random weights
def create_weights(number_of_neurons, n_inputs, n_classes):
    weights = []
    #First layer (nºinputs x nºneurons)
    weights.append(tf.Variable(tf.random_normal([n_inputs,number_of_neurons[0]])))

    #Hidden layers
    for i in range(1,len(number_of_neurons)):
        weights.append(tf.Variable(tf.random_normal([number_of_neurons[i-1],number_of_neurons[i]])))
    #Output layer (nºneuros x nºoutputs)
    weights.append(tf.Variable(tf.random_normal([number_of_neurons[len(number_of_neurons)-1],
                                                                                  n_classes])))
    return weights

def multilayer_perceptron(x, weights, biases):
    progression = []
    activation = []
    progression.append(tf.add(tf.matmul(x, weights[0]), biases[0]))
    activation.append(tf.nn.tanh(progression[0]))
    for i in range(1, len(number_of_neurons)+1):
        progression.append(tf.add(tf.matmul(activation[i-1], weights[i]), biases[i]))
        activation.append(tf.nn.tanh(progression[i]))

    return activation[len(number_of_neurons)]

def getDataFrom(path):
    data = []
    with open(path, 'rb') as f:
        content = f.read()
        data = pickle.loads(content)
    return data

def taking_batches(input_x, expected_y, batch_size, offset):
    return input_x[offset:offset+batch_size],expected_y[offset:offset+batch_size]

#Main code

if (len(sys.argv) < 2):
    raise Exception("You must provide the path to the data.\npython " + sys.argv[0] + " path_to_data")

path = sys.argv[1]

data = getDataFrom(path + '/inputs')
data = np.reshape(data, (29*1000, 13*5))

labels = getDataFrom(path +'/labels')
labels = np.array(labels)

#Input and correct output
x = tf.constant(data, dtype='float')
y = tf.constant(labels, dtype='float')

learning_rate = 0.003
training_epochs = 600
n_samples = 29*1000 # Number of samples we have
n_inputs = 13*5    #We get a matrix (13 x 5) when calculating the MFCC
n_classes = 10     #Rock, blues, jazz...
batch_size = n_samples

#Create our Neural Network
number_of_neurons = [256, 256]
biases = create_biases(number_of_neurons, n_classes)
weights = create_weights(number_of_neurons, n_inputs, n_classes)
#Get predictions
pred = multilayer_perceptron(x, weights, biases)
#Set cost and optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

#Inizialize variables for TensorFlow
init = tf.global_variables_initializer()
#Start session
sess = tf.InteractiveSession()
sess.run(init)

in_x, in_y = x, y

for epoch in range(training_epochs):
    avg_cost = 0.0
    total_batches = int(n_samples/batch_size)
    for i in range(total_batches):
        batch_x,batch_y = taking_batches(in_x,in_y,batch_size,i)


        _,c = sess.run([optimizer,cost], feed_dict={x:batch_x.eval(session=sess),y:batch_y.eval(session=sess)})
        avg_cost += c/total_batches;
    clear_output()
    print("Epoch: {} cost= {:.4f}".format(epoch+1,avg_cost))

print("Finished with {} epochs with cost {}".format(training_epochs,avg_cost))

# Test error
correct_predictions = tf.equal(tf.argmax(pred,1), tf.argmax(y,1))
correct_predictions = tf.cast(correct_predictions, "float")
accuracy = tf.reduce_mean(correct_predictions)
print("Accuracy: {}".format(accuracy.eval({x:batch_x.eval(session=sess),y:batch_y.eval(session=sess)})))
