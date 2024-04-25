from MLDataRead import get_data
import numpy as np
from numpy import load
import cv2


"""
w = weights, b = bias, i = input, h = hidden, o = output, l = label
e.g. w_i_h = weights from input layer to hidden layer
"""
images, labels = get_data()
w_i_h = np.random.uniform(-0.5, 0.5, (100, 84000))
w_h_o = np.random.uniform(-0.5, 0.5, (4, 100))
b_i_h = np.zeros((100, 1))
b_h_o = np.zeros((4, 1))

learn_rate = 0.01
nr_correct = 0
epochs = 5
p = 0
for epoch in range(epochs):
    for img, l in zip(images, labels):
        img.shape += (1,)
        l.shape += (1,)
        # Forward propagation input -> hidden
        h_pre = b_i_h + w_i_h @ img
        h = 1 / (1 + np.exp(-h_pre))
        # Forward propagation hidden -> output
        o_pre = b_h_o + w_h_o @ h
        o = 1 / (1 + np.exp(-o_pre))

        # Cost / Error calculation
        e = 1 / len(o) * np.sum((o - l) ** 2, axis=0)
        nr_correct += int(np.argmax(o) == np.argmax(l))

        # Backpropagation output -> hidden (cost function derivative)
        delta_o = o - l
        w_h_o += -learn_rate * delta_o @ np.transpose(h)
        b_h_o += -learn_rate * delta_o
        # Backpropagation hidden -> input (activation function derivative)
        delta_h = np.transpose(w_h_o) @ delta_o * (h * (1 - h))
        w_i_h += -learn_rate * delta_h @ np.transpose(img)
        b_i_h += -learn_rate * delta_h

    # Show accuracy for this epoch
    print(f"Num Correct: {nr_correct}")
    print(f"Acc: {round((nr_correct / images.shape[0]) * 100, 2)}%")
    nr_correct = 0

np.savez_compressed('MLWeights', W_I_H=w_i_h, W_H_O=w_h_o, B_I_H=b_i_h, B_H_O=b_h_o)

i = 1
# Show results
while i < 1448:
    img = load('MLFrames/frame'+str(i)+'.npy')
    cv2.imshow('frame', img)
    cv2.waitKey(100)

    img = img.astype("float32") / 255
    img = np.reshape(img, (1, 84000))
    img.shape += (1,)
    # Forward propagation input -> hidden
    h_pre = b_i_h + w_i_h @ img
    h = 1 / (1 + np.exp(-h_pre))
    # Forward propagation hidden -> output
    o_pre = b_h_o + w_h_o @ h
    o = 1 / (1 + np.exp(-o_pre))

    # print(o)
    print(o.argmax())
    i += 1