import numpy as np
import pathlib


def get_data(npzfile):
    with np.load(f"{pathlib.Path(__file__).parent.absolute()}/"+str(npzfile)) as f:
        images, labels = f["img"], f["lbl"]
    images = images.astype("float32") / 255
    images = np.reshape(images, (images.shape[0], images.shape[1] * images.shape[2]))
    labels = np.eye(4)[labels]  ###Change int value to the number of unique cases
    return images, labels