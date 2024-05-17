# MAIN SCRIPT FOR TRAINING ON DATA, VALIDATES AT END

from MLDataRead import get_data
import numpy as np
from numpy import load
import cv2
import pandas as pd
import matplotlib.pyplot as plt

"""
w = weights, b = bias, i = input, h = hidden, o = output, l = label
e.g. w_i_h = weights from input layer to hidden layer
"""
images, labels = get_data("TrainMLData.npz")      ##### EDIT
    
w_i_h = np.random.uniform(-0.5, 0.5, (20, 84000))
w_h_o = np.random.uniform(-0.5, 0.5, (4, 20))           ##### EDIT
b_i_h = np.zeros((20, 1))
b_h_o = np.zeros((4, 1))           ##### EDIT

learn_rate = 0.01
nr_correct = 0
actual = []
predicted = []
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

np.savez_compressed('MLWeights', W_I_H=w_i_h, W_H_O=w_h_o, B_I_H=b_i_h, B_H_O=b_h_o)           ##### EDIT

images, labels = get_data("ValMLData.npz")           ##### EDIT

# Validation / Confusion Matrix
WEIGHTS = np.load('MLWeights.npz')           ##### EDIT
for img, l in zip(images, labels):
    img.shape += (1,)
    l.shape += (1,)
    # Forward propagation input -> hidden
    h_pre = WEIGHTS['B_I_H'] + WEIGHTS['W_I_H'] @ img
    h = 1 / (1 + np.exp(-h_pre))
    # Forward propagation hidden -> output
    o_pre = WEIGHTS['B_H_O'] + WEIGHTS['W_H_O'] @ h
    o = 1 / (1 + np.exp(-o_pre))

    # Create List for Confusion Matrix
    actual.append(int(np.argmax(l)))
    predicted.append(int(np.argmax(o)))

y_actu = pd.Series(actual, name='Actual')
y_pred = pd.Series(predicted, name='Predicted')
df_confusion = pd.crosstab(y_actu, y_pred)    
df_conf_norm = df_confusion.div(df_confusion.sum(axis=1), axis="index")

def plot_confusion_matrix(df_confusion, title='Confusion matrix', cmap=plt.cm.gray_r):
    plt.matshow(df_confusion, cmap=cmap) # imshow
    #plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(df_confusion.columns))
    plt.xticks(tick_marks, df_confusion.columns, rotation=45)
    plt.yticks(tick_marks, df_confusion.index)
    #plt.tight_layout()
    plt.ylabel(df_confusion.index.name)
    plt.xlabel(df_confusion.columns.name)

print(df_conf_norm)
plot_confusion_matrix(df_conf_norm)
plt.show()