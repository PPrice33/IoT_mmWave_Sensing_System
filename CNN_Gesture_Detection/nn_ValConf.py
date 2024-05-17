# FOR GENERATING CONFUSION MATRIX, FROM VALIDATION DATA

from MLDataRead import get_data
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

images, labels = get_data("ValMLData.npz")
actual = []
predicted = []

# Validation / Confusion Matrix
WEIGHTS = np.load('MLWeights.npz')
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