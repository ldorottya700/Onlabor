#!/usr/bin/env python
# coding: utf-8

import tensorflow as tf

from tensorflow.keras import datasets, layers, models
from tensorflow import keras
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

get_ipython().system('ls /home/dodo/egyetem/6.felev/onlab/dataset/raw')


image_size = (54,96)
batch_size = 32
class_names = ['500', '1000', '2000', '5000', '10000', '20000']

train_dataset = tf.keras.preprocessing.image_dataset_from_directory(
    "/home/dodo/egyetem/6.felev/onlab/dataset/raw/z3_new",
    validation_split = 0.2,
    subset = "training",
    seed = 1337,
    class_names = class_names,
    image_size = image_size,
    batch_size = batch_size,
)

valid_dataset = tf.keras.preprocessing.image_dataset_from_directory(
    "/home/dodo/egyetem/6.felev/onlab/dataset/raw/z3_new",
    validation_split = 0.2,
    subset = "validation",
    seed = 1337,
    class_names = class_names,
    image_size = image_size,
    batch_size = batch_size,
)

layers.Rescaling(1.0 / 255)


plt.figure(figsize=(10, 10))

data_augmentation = keras.Sequential(
    [
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
    ]
)

for images, labels in train_dataset.take(1):
    for i in range(9):
        ax = plt.subplot(3, 3, i + 1)
        plt.imshow(images[i].numpy().astype("uint8"))
        plt.title(int(labels[i]))
        plt.axis("off")


input_shape = image_size + (3,)
num_classes = 6
model = models.Sequential(
    [
        keras.Input(shape=input_shape),
        layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Flatten(),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation="softmax"),
    ]
)
model.summary()


epochs = 4

model.compile(loss = "sparse_categorical_crossentropy", optimizer = "adam", metrics = ["accuracy"])

model.fit(train_dataset, epochs = epochs, validation_data = valid_dataset)


imgpath = "pelda/tst_25.jpg"

flower = mpimg.imread(imgpath)

img = keras.preprocessing.image.load_img(
    imgpath, target_size = image_size
)

plt.imshow(flower)

img_array = keras.preprocessing.image.img_to_array(img)
img_array = tf.expand_dims(img_array, 0)

predictions = model.predict(img_array)
score = predictions[0]
idx = np.where(score == np.amax(score))

print(
    class_names[int(idx[0])] + '\t' + str(np.amax(score))
)
#print(predictions)




