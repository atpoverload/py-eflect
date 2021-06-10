import tensorflow as tf

mnist = tf.keras.datasets.mnist

(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = tf.keras.models.Sequential([
  tf.keras.layers.Flatten(input_shape=(28, 28)),
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(10)
])

predictions = model(x_train[:1]).numpy()

array([[-0.28274903,  0.19788507, -0.18761218,  0.80738944, -0.25398862,
        -1.2106801 ,  0.08712098,  0.24884817,  0.48026958, -0.63544625]],
        dtype=float32)

array([[0.07085732, 0.11458333, 0.07792953, 0.21077827, 0.07292479,
        0.02801492, 0.10256924, 0.12057421, 0.15197057, 0.04979781]],
        dtype=float32)

loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)

loss_fn(y_train[:1], predictions).numpy()

model.compile(optimizer='adam',
              loss=loss_fn,
              metrics=['accuracy'])

model.fit(x_train, y_train, epochs=5)
model.evaluate(x_test,  y_test, verbose=2)
