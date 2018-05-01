from video_analysis import VideoAnalysis
import cv2
from region_select import region_select
from tkinter import filedialog
import json

camera_ip = 'kgong@192.168.0.4'
root_path = '/home/ke/TrafficProject/Mask-RCNN/'
in_path = filedialog.askopenfilename(initialdir=root_path + "/Cameras/" + camera_ip + "/Videos")
out_path = '/home/ke/TrafficProject/Mask-RCNN/' + "/Cameras/" + camera_ip + "/Videos" + '/out_temp.mp4'
json_file_path = root_path + "/Cameras/" + camera_ip + "/" + camera_ip + "_metadata.json"
# password
with open(json_file_path, "r") as json_file:
    json_data = json.load(json_file)

cap = cv2.VideoCapture(in_path)
flag, frame = cap.read()
cv2.imwrite('./Cameras/haha/haha.jpg', frame)
ori_reso = (frame.shape[1], frame.shape[0])
x, _ = region_select('haha')
# A = VideoAnalysis('/home/ke/Downloads/test2.mp4', '/home/ke/Downloads/13.mp4', (640, 400), ori_reso, 30, 1)
VA = VideoAnalysis(in_path, out_path, json_data['resolution'], ori_reso, 30, json_data['frame_rate'], sorted_refPt=x)
VA.mask_video()
arr = VA.mask_rcnn_apply()
interested_frame = VA.find_interested_frames(arr, 2)
VA.clip_video(interested_frame)