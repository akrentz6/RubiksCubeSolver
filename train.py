import keras
from keras.layers import LSTM, Dense, Input, Dropout, MultiHeadAttention, LayerNormalization, Conv1D, GlobalAveragePooling1D
from tensorflow.keras.optimizers import Adam
import numpy as np

# https://github.com/keras-team/keras/issues/1753
# https://keras.io/examples/vision/image_classification_with_vision_transformer/
# https://keras.io/examples/structured_data/movielens_recommendations_transformers/

src = "datasets"

def load_train_data(source, files):

    for i in range(files):

        print(f"Loading train{i} data")
        yield load(source + "/train" + str(i) + ".npz")

def load(file):

    with open(file, "rb") as f:
        
        b = np.load(f)
        cubes, sols = b["cubes"], b["sols"]
    
    return cubes, sols
    
def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):

    # Attention and Normalization
    x = MultiHeadAttention(
        key_dim=head_size, num_heads=num_heads, dropout=dropout
    )(inputs, inputs)
    x = Dropout(dropout)(x)
    x = LayerNormalization(epsilon=1e-6)(x)
    res = x + inputs

    # Feed Forward Part
    x = Conv1D(filters=ff_dim, kernel_size=1, activation="relu")(res)
    x = Dropout(dropout)(x)
    x = Conv1D(filters=inputs.shape[-1], kernel_size=1)(x)
    x = LayerNormalization(epsilon=1e-6)(x) 

    return x + res

def build_model(input_shape, head_size, num_heads, ff_dim, num_transformer_blocks, mlp_units, dropout = 0, mlp_dropout = 0):

    inputs = Input(shape=input_shape)
    temp_inputs = inputs

    for _ in range(num_transformer_blocks):
        temp_inputs = transformer_encoder(temp_inputs, head_size, num_heads, ff_dim, dropout)

    temp_inputs = GlobalAveragePooling1D(data_format="channels_first")(temp_inputs)

    for dim in mlp_units:

        temp_inputs = Dense(dim, activation="relu")(temp_inputs)
        temp_inputs = Dropout(mlp_dropout)(temp_inputs)
    
    outputs = Dense(18, activation="softmax")(temp_inputs)

    return keras.Model(inputs, outputs)

if __name__ == "__main__":

    print("Building model")

    # model = build_model(
    #     (1, 288),
    #     head_size=256,
    #     num_heads=4,
    #     ff_dim=4,
    #     num_transformer_blocks=4,
    #     mlp_units=[128],
    #     mlp_dropout=0.4,
    #     dropout=0.25,
    # )
    
    model = keras.Sequential()

    model.add(LSTM(256, input_shape = (48, 6), activation = "relu", return_sequences = True))
    model.add(Dropout(0.2))
    
    model.add(LSTM(256, activation = "relu", return_sequences = True))
    model.add(Dropout(0.2))

    model.add(LSTM(256, activation = "relu", return_sequences = True))
    model.add(Dropout(0.2))

    model.add(LSTM(256, activation = "relu", return_sequences = True))
    model.add(Dropout(0.2))

    model.add(LSTM(256, activation = "relu"))
    model.add(Dropout(0.2))

    model.add(Dense(18, activation = "softmax"))
    
    model.compile(loss = "categorical_crossentropy", optimizer = Adam(learning_rate = 1e-4), metrics = ["accuracy"])
    
    print("Loading valid data")
    (X_valid, Y_valid) = load(src + "/valid0.npz")
    
    print("Loading test data")
    (X_test, Y_test) = load(src + "/test0.npz")

    for _ in range(1):

        for (X_train, Y_train) in load_train_data(src, 20):

            print(f"X_train: {X_train.shape}")
            print(f"Y_train: {Y_train.shape}")

            model.fit(X_train, Y_train, epochs = 1, validation_data = (X_valid, Y_valid))

    test_loss, test_acc = model.evaluate(X_test, Y_test)
    print(f"Loss: {test_loss} | Accuracy: {test_acc}")
    
    model.save("model")

    input()
