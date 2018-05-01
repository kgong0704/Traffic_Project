import subprocess
from math import ceil
from get_model import get_model
import os
import cv2
import numpy as np
import datetime


class VideoAnalysis:

    def __init__(self, _in_path, _out_path, _expec_reso, _ori_reso, _ori_fr, _expec_fr, **kwargs):
        self.in_path = _in_path
        self.out_path = _out_path
        self.expec_reso = _expec_reso
        self.ori_reso = _ori_reso
        self.expec_fr = _expec_fr
        self.ori_fr = _ori_fr
        if "sorted_refPt" in kwargs:
            self.sorted_refPt = kwargs.get('sorted_refPt')
            roi_corners = np.array([self.sorted_refPt], dtype=np.int32)
        else:
            self.sorted_refPt = None

        if "duration" in kwargs:
            self.duration = kwargs.get('duration')
        else:
            self.duration = self.get_duration()

        if "frame_total" in kwargs:
            self.frame_total = kwargs.get('frame_total')
        else:
            self.frame_total = self.get_frame_count()

        if "ori_frame_rate" in kwargs:
            self.ori_frame_rate = kwargs.get('ori_frame_rate')
        else:
            self.ori_frame_rate = ceil(self.frame_total/self.duration)

    def get_duration(self):
        """Get the duration of a video using ffprobe."""
        cmd = 'ffprobe -i {} -show_entries format=duration -v quiet -of csv="p=0"'.format(self.in_path)
        output = subprocess.check_output(
            cmd,
            shell=True, # Let this run in the shell
            stderr=subprocess.STDOUT
        )
        # return round(float(output))  # ugly, but rounds your seconds up or down
        return float(output)

    def get_frame_count(self):
        """Get the duration of a video using ffprobe."""
        cmd = 'ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_frames -of default=nokey=1:noprint_wrappers=1 {}'.format(self.in_path)
        output = subprocess.check_output(
            cmd,
            shell=True, # Let this run in the shell
            stderr=subprocess.STDOUT
        )
        # return round(float(output))  # ugly, but rounds your seconds up or down
        return float(output)

    def get_frame_rate(self):
        cmd = 'ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=r_frame_rate -of default=nokey=1:noprint_wrappers=1 {}'.format(self.in_path)
        output = subprocess.check_output(
            cmd,
            shell=True, # Let this run in the shell
            stderr=subprocess.STDOUT
        )
        # return round(float(output))  # ugly, but rounds your seconds up or down
        return float(output)

    def re_scale_roi(self):
        x_fraction = float(self.ori_reso[0]/self.expec_reso[0])
        y_fraction = float(self.ori_reso[1]/self.expec_reso[1])
        new_roi = []
        for p in self.sorted_refPt:
            x = ceil(p[0]/x_fraction)
            y = ceil(p[1]/y_fraction)
            new_roi.append((x, y))
        return new_roi

    #
    # print(re_scale_roi((1920, 1080), (480, 360), [(368, 464), (544, 168), (973, 514), (978, 313)]))

    # down size(scale and framerate) and mask video if roi information is provided
    # duration/framerate/totalframe are metadata from recording
    # here set them as optional input to make the method more flexible for testing, etc
    def mask_video(self):
        if self.sorted_refPt is None:
            reso = str(self.expec_reso[0]) + 'x' + str(self.expec_reso[1])
            cmd = 'ffmpeg -y -r {0} -i {1} -t {2} -r {3} -vf scale={4} -strict -2 {5}'.format(self.ori_fr, self.in_path, self.duration, self.expec_fr, reso, self.out_path)
            subprocess.call(cmd, shell=True)

        else:
            rescaled_refPt = self.re_scale_roi()
            temp = './temp.mp4'
            reso = str(self.expec_reso[0]) + 'x' + str(self.expec_reso[1])
            cmd = 'ffmpeg -y -r {0} -i {1} -t {2} -r {3} -vf scale={4} -strict -2 {5}'.format(self.ori_fr, self.in_path, self.duration, self.expec_fr, reso, temp)
            subprocess.call(cmd, shell=True)

            cap = cv2.VideoCapture(temp)
            out = cv2.VideoWriter(self.out_path, cv2.VideoWriter_fourcc('M','J','P','G'), float(self.expec_fr), tuple(self.expec_reso))
            # while not cap.isOpened():
            #     cap = cv2.VideoCapture("./out.mp4")
            #     cv2.waitKey(1000)
            #     print('Wait for the header')
            #
            pos_frame = cap.get(1)
            # print(pos_frame)
            while True:
                flag, frame = cap.read()
                if flag:
                    pos_frame = cap.get(1)
                    # The frame is ready and already VideoCaptured
                    mask = np.zeros(frame.shape, dtype=np.uint8)
                    roi_corners = np.array([rescaled_refPt], dtype=np.int32)
                    channel_count = frame.shape[2]  # i.e. 3 or 4 depending on your image
                    ignore_mask_color = (255,)*channel_count
                    cv2.fillPoly(mask, roi_corners, ignore_mask_color)
                    masked_image = cv2.bitwise_and(frame, mask)

                    out.write(masked_image)
                    # pos_frame = cap.get(1)
                    # print(str(int(pos_frame))+" frames")
                else:
                    # The next frame is not ready, so we try to read it again
                    cap.set(1, pos_frame-1)
                    print("frame is not ready")
                    # It is better to wait for a while for the next frame to be ready
                    cv2.waitKey(1000)

                if cv2.waitKey(10) == 27:
                    break
                if cap.get(1) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                    # If the number of captured frames is equal to the total number of frames,
                    # we stop
                    break

            os.remove(temp)

    def mask_rcnn_apply(self):
        ROOT_DIR = os.getcwd()
        COCO_MODEL_PATH = os.path.join(ROOT_DIR + '/model', "mask_rcnn_coco.h5")
        model = get_model(ROOT_DIR, COCO_MODEL_PATH)

        # COCO Class names
        # Index of the class in the list is its ID. For example, to get ID of
        # the teddy bear class, use: class_names.index('teddy bear')
        class_names = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
                     'bus', 'train', 'truck', 'boat', 'traffic light',
                     'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
                     'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
                     'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
                     'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
                     'kite', 'baseball bat', 'baseball glove', 'skateboard',
                     'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
                     'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
                     'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
                     'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
                     'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
                     'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
                     'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
                     'teddy bear', 'hair drier', 'toothbrush']

        frame_num = self.get_frame_count()
        cap = cv2.VideoCapture(self.out_path)
        class_num = len(class_names) - 1
        arr = [[0 for x in range(class_num)] for y in range(int(frame_num))]

        #
        # out = cv2.VideoWriter(o, cv2.VideoWriter_fourcc('M','J','P','G'), 10, (640,400))

        print(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        while not cap.isOpened():
            cap = cv2.VideoCapture("./out.mp4")
            cv2.waitKey(1000)
            print('Wait for the header')

        pos_frame = cap.get(1)
        while True:
            flag, frame = cap.read()
            if flag:
                pos_frame = cap.get(1)
                # The frame is ready and already VideoCapturedend_time
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = model.detect([frame], verbose=1)
                r = results[0]
                for x in r['class_ids']:
                    if x > class_num:
                        pass
                    else:
                        arr[int(pos_frame)-1][x-1]+=1

            else:
                # The next frame is not ready, so we try to read it again
                cap.set(1, pos_frame-1)
                print("frame is not ready")
                # It is better to wait for a while for the next frame to be ready
                cv2.waitKey(1000)

            if cv2.waitKey(10) == 27:
                break
            if cap.get(1) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                # If the number of captured frames is equal to the total number of frames,
                # we stop
                break
        os.remove(self.out_path)
        return arr

    @staticmethod
    def find_interested_frames(detected_list, object_index):
        count = 0
        frames = [[]]
        clips_count = 0
        for index, item in enumerate(detected_list):
            if item[object_index] >= 1 and count < 5:
                if clips_count == 0:
                    frames[clips_count].append(index)
                    count = 0
                else:
                    frames[clips_count].append(index)
                    count = 0
            if item[object_index] >= 1 and count >= 5:
                clips_count += 1
                frames.append([index])
                count = 0
            else:
                count += 1
        frames.pop(0)
        return frames

    def clip_video(self, interested_frames):
        if interested_frames[0]:
            for index, frames in enumerate(interested_frames):
                video_len = str(datetime.timedelta(seconds=(len(frames)/self.expec_fr)))
                start_time = str(datetime.timedelta(seconds=(frames[0])/self.expec_fr))
                end_time = str(datetime.timedelta(seconds=(frames[0] + len(frames))/self.expec_fr))
                clip_name = os.path.abspath(os.path.join(self.in_path, os.pardir)) + '/' + start_time + '_to_' + end_time + '.mp4'
                cmd = 'ffmpeg -y -i {0} -ss {1} -t {2} -async 1 {3}'.format(self.in_path, start_time, video_len, clip_name)
                subprocess.call(cmd, shell=True)
        else:
            print('there is no detection founded')

