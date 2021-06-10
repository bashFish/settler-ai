import tensorflow as tf
import numpy as np
import copy
from tensorflow.keras.optimizers import Adam

from building.sawmill import Sawmill
from building.woodcutter import Woodcutter


def extract_state(environment):
    #TODO: do i need to convert that to binary masks? guess so :/
    return ([copy.deepcopy(x) for x in (environment.landscape_occupation,
             environment.landscape_resource_amount,
             environment.owned_terrain)],
            copy.deepcopy(environment.state_dict),
            sum([1 for b in environment.buildings if b.finished is False]),
            sum([1 for b in environment.buildings if b.finished is True and b == Sawmill]),
            sum([1 for b in environment.buildings if b.finished is True and b == Woodcutter]),
            sum([1 for b in environment.buildings if b.finished is False and b == Sawmill]),
            sum([1 for b in environment.buildings if b.finished is False and b == Woodcutter]),
            )

def model_action(learning_rate):
    map_input = tf.keras.Input(shape=(3,50,50), name='map_state')
    x = tf.keras.layers.Conv2D(32, 2, padding="same", activation='relu')(map_input)
    x = tf.keras.layers.MaxPool2D(3)(x)
    x = tf.keras.layers.Conv2D(32, 2, padding="same", activation='relu')(map_input)
    x = tf.keras.layers.MaxPool2D(3)(x)

    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(150, activation='relu')(x)
    x = tf.keras.layers.Dense(50, activation='relu')(x)
    x = tf.keras.Model(inputs=map_input, outputs=x)

    statistic_input = tf.keras.Input(shape=(5+5), name='statistic_state')
    y = tf.keras.layers.Dense(50, activation='relu')(statistic_input)
    y = tf.keras.Model(inputs=statistic_input, outputs=y)

    model = tf.keras.layers.Concatenate()([x.output, y.output])
    model = tf.keras.layers.Dense(150, activation='relu')(model)
    model = tf.keras.layers.Dense(50, activation='relu')(model)

    #TODO: remove should be handled somewhat different
    model = tf.keras.layers.Dense(5, activation='linear', #TODO: not linear - what did i have before?
        kernel_regularizer=tf.keras.regularizers.l1_l2(l1=1e-5, l2=1e-4),
        bias_regularizer=tf.keras.regularizers.l2(1e-4),
        activity_regularizer=tf.keras.regularizers.l1(1e-3))(model)

    model = tf.keras.Model(inputs=[x.input, y.input], outputs=model)
    #TODO: loss should be should be RSM rather? but i also train somewhat different here
    model.compile(loss="mse", optimizer=Adam(lr=learning_rate), metrics=['accuracy'])
    return model


#TODO: could also insert map in multiple layers (wood/ woodcutter/ ...) = embedding
#TODO: use deconvolutional -> generate heat map here?
def model_coordinates():
    map = tf.keras.models.Sequential()
    map.add(tf.keras.Input(shape=(3,50,50)))
    map.add(tf.keras.layers.Conv2D(32, (3, 3), padding="same", activation='relu'))
    map.add(tf.keras.layers.Conv2D(32, (3, 3), padding="same", activation='relu'))
    map.add(tf.keras.layers.Dropout(.1))
    map.add(tf.keras.layers.Dense(50, activation='relu'))
    map.add(tf.keras.layers.Dense(50, activation='relu'))
    map.add(tf.keras.layers.Dense(2)) # < must be in 0,50

    return map


def prediction_to_coords(preds):
    coords = preds*10
    cell = (int(min(abs(coords[0]), 49)), int(min(abs(coords[1]) , 49)))
    return cell