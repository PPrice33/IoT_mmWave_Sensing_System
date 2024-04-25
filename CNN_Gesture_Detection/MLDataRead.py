import numpy as np
import pathlib


def get_data():
    with np.load(f"{pathlib.Path(__file__).parent.absolute()}/MLData.npz") as f:
        images, labels = f["img"], f["lbl"]
    images = images.astype("float32") / 255
    images = np.reshape(images, (images.shape[0], images.shape[1] * images.shape[2]))
    labels = np.eye(4)[labels]
    return images, labels