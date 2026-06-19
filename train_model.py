import pandas as pd
import tensorflow as tf

data = pd.read_csv(
"dataset.csv"
)

X = data[
["course",
"skill",
"hours",
"quiz"]
]

y = data[
"output"
]

model = tf.keras.Sequential([

tf.keras.layers.Dense(
16,
activation="relu"
),

tf.keras.layers.Dense(
12,
activation="relu"
),

tf.keras.layers.Dense(
12,
activation="softmax"
)

])

model.compile(

optimizer="adam",

loss="sparse_categorical_crossentropy",

metrics=["accuracy"]

)

model.fit(

X,
y,

epochs=50

)

model.save(
"models/path_model.keras"
)

print(
"Training Completed"
)