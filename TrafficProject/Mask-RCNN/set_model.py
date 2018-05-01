import os
import sys
import random
import math
import numpy as np
import scipy.misc
import matplotlib
import matplotlib.pyplot as plt

from coco_config import InferenceConfig
import utils
import model as modellib
import cv2

import matplotlib.patches as patches
from matplotlib.patches import Polygon
import random
import visualize
import time

def get_model():
  # %matplotlib inline 

  # Root directory of the project
  ROOT_DIR = os.getcwd()

  # Directory to save logs and trained model
  MODEL_DIR = os.path.join(ROOT_DIR, "logs")

  # Path to trained weights file
  # Download this file and place in the root of your 
  # project (See README file for details)
  COCO_MODEL_PATH = os.path.join(ROOT_DIR + '/model', "mask_rcnn_coco.h5")

  # Directory of images to run detection on
  IMAGE_DIR = os.path.join(ROOT_DIR, "images")

  config = InferenceConfig()
  config.print()

  # Create model object in inference mode.
  model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)
  print(model)
  # Load weights trained on MS-COCO
  model.load_weights(COCO_MODEL_PATH, by_name=True)
  print(model)

  return model
