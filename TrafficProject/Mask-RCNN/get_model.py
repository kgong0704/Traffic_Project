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

def get_model(root_path, model_file_path):

  # Directory to save logs and trained model
  MODEL_DIR = os.path.join(root_path, "logs")

  # Directory of images to run detection on
  IMAGE_DIR = os.path.join(root_path, "images")

  config = InferenceConfig()
  config.print()

  # Create model object in inference mode.
  model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)
  print(model)
  # Load weights trained on MS-COCO
  model.load_weights(model_file_path, by_name=True)
  print(model)

  return model
