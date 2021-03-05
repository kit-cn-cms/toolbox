import sys
import os
try:
    import tensorflow as tf
except:
    exit("could not load keras for .dnn_loader.py")

def load_model(model_path):
    ''' load an already trained model '''
    checkpoint_path = model_path+"/checkpoints/trained_model.h5py"
    if not os.path.exists(checkpoint_path):
        checkpoint_path = model_path+"/trained_model.h5py"
    if not os.path.exists(checkpoint_path):
        sys.exit("no valid model path: {}".format(model_path))

    # get the keras model
    model = tf.keras.models.load_model(checkpoint_path)
    model.summary()

    return model






input_models = sys.argv[1:]
print("input model paths:")
print("\n".join(input_models))

models = []
for m in input_models:
    models.append( load_model(m) )
m = models[0]
print("access models via 'models' list")
print("access first model via 'm'")


print("call 'help()' to show features")
def help():
    print("no help function implemented yet")



