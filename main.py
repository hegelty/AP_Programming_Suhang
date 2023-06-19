import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

if __name__ == "__main__":
    data = []
    with open("user_infos.pkl", "rb") as f:
        users = pickle.load(f)
        for u in users:
            if "atcoder_rating" in u and "cf_rating" in u:
                data.append([u["rating"], u["atcoder_rating"], u["cf_rating"]])
    data = np.array(data)
    print(data.shape)
    x = data[:, 0]
    y = data[:, 1:]
    print(x,y)

    W = tf.Variable(tf.random.normal((2, 1)))
    b = tf.Variable(tf.random.normal((1,)))

    optimizer = tf.keras.optimizers.SGD(learning_rate=0.00001)

    n_epochs = 1000
    for i in range(n_epochs):
        with tf.GradientTape() as tape:
            hypothesis = tf.matmul(x, W) + b
            cost = tf.reduce_mean(tf.square(hypothesis - y))
        grads = tape.gradient(cost, [W, b])
        optimizer.apply_gradients(zip(grads, [W, b]))
        if i % 100 == 0:
            print(f"Epoch {i} | Cost: {cost.numpy()}")