from get_model import get_model
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
#model path

def cv_display_instances(image, boxes, masks, class_ids, class_names,
                    scores=None, title="",
                    figsize=(16, 16)):
  # Number of instances
  N = boxes.shape[0]
  print(N)
  if not N:
      print("\n*** No instances to display *** \n")
  else:
      assert boxes.shape[0] == masks.shape[-1] == class_ids.shape[0]

  # Generate random colors
  colors = visualize.random_colors(N)

  height, width = image.shape[:2]

  masked_image = image.copy()#.astype(np.uint32).copy()
  for i in range(N):
      color = colors[i]

      # Bounding box
      if not np.any(boxes[i]):
          continue
      y1, x1, y2, x2 = boxes[i]
      cv_color = (color[0] * 255, color[1] * 255, color[2] * 255)
      cv2.rectangle(masked_image, (x1, y1), (x2, y2), cv_color , 1)

      # Label
      class_id = class_ids[i]
      score = scores[i] if scores is not None else None
      label = class_names[class_id]
      print(label)
      x = random.randint(x1, (x1 + x2) // 2)
      caption = "{} {:.3f}".format(label, score) if score else label

      font = cv2.FONT_HERSHEY_PLAIN
      cv2.putText(masked_image,caption,(x1, y1),font, 1, cv_color)

      # Mask
      mask = masks[:, :, i]
      masked_image = visualize.apply_mask(masked_image, mask, color)


  masked_image.astype(np.uint8)
  return masked_image
