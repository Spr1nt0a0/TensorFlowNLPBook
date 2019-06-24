# encoding: utf-8
"""
@author: Spr1nt
@file: TextCNN.py
@time: 2019/6/24 9:20
"""

import tensorflow as tf
import numpy as np

tf.reset_default_graph()

embedding_size = 2
sequence_length = 3
num_classes = 2
filter_sizes = [2,2,2]
num_filters = 3

sentences = ["i love you","he loves me", "she likes baseball", "i hate you","sorry for that", "this is awful"]
labels = [1,1,1,0,0,0]

word_list = " ".join(sentences).split()
word_list = list(set(word_list))
word_dict = {w: i for i,w in enumerate(word_list)}
vocab_size = len(word_dict)

inputs = []
for sen in sentences:
    inputs.append(np.asarray([word_dict[n] for n in sen.split()]))

outputs = []
for out in labels:
    outputs.append(np.eye(num_classes)[out])

X = tf.placeholder(tf.int32, [None,sequence_length])
Y = tf.placeholder(tf.int32, [None,num_classes])

W = tf.Variable(tf.random_uniform([vocab_size,embedding_size], -1.0,1.0))
embedded_char = tf.nn.embedding_lookup(W,X)
embedded_char = tf.expand_dims(embedded_char,-1)

pooled_outputs = []
for i, filter_size in enumerate(filter_sizes):
    filter_shape = [filter_size,embedding_size,1,num_filters]
    W = tf.Variable(tf.truncated_normal(filter_shape,stddev=0.1))
    b = tf.Variable(tf.constant(0.1, shape=[num_filters]))

    conv = tf.nn.conv2d(embedded_char,W,strides=[1,1,1,1],padding='VALID')
    h = tf.nn.relu(tf.nn.bias_add(conv,b))
    pooled = tf.nn.max_pool(h,ksize=[1,sequence_length-filter_size+1,1,1],strides=[1,1,1,1],padding='VALID')
    pooled_outputs.append(pooled)

num_filters_total = num_filters*len(filter_sizes)
h_pool = tf.concat(pooled_outputs,num_filters)
h_pool_flat = tf.reshape(h_pool, [-1,num_filters_total])

Weight = tf.get_variable('W', shape=[num_filters_total,num_classes],
                         initializer=tf.contrib.layers.xavier_initializer())
Bias = tf.Variable(tf.constant(0.1, shape=[num_classes]))
model = tf.nn.xw_plus_b(h_pool_flat,Weight,Bias)
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=model,labels=Y))
optimizer = tf.train.AdamOptimizer(0.001).minimize(cost)

hypothesis = tf.nn.softmax(model)
predictions = tf.arg_max(hypothesis,1)

init = tf.global_variables_initializer()
sess = tf.Session()
sess.run(init)

for epoch in range(5000):
    _, loss = sess.run([optimizer, cost], feed_dict= {X:inputs, Y: outputs})
    if (epoch+1)%100 == 0:
        print('Epoch:','%04d' % (epoch+1), 'cost=', '%.6f' % (loss))

test_text = 'sorry hate you '
tests = []
tests.append(np.asarray([word_dict[n] for n in test_text.split()]))

predict = sess.run([predictions], feed_dict={X:tests})
result = predict[0][0]
if result == 0:
    print(test_text,"is bad mean.")
else:
    print(test_text,"is good mean.")







