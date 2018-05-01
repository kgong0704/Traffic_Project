import os
import json
import time
import subprocess
import shlex
from region_select import region_select
from shutil import copyfile
import cv2
import glob

#name format: optional short discription followed by ip address
def check_existance(ip):
	root_path = '/home/ke/TrafficProject/Mask-RCNN/'
	os.chdir(root_path + "/Cameras")
	if any(x.startswith(ip) for x in os.listdir('./')):
		return True
	else:
		subprocess.call(['mkdir',ip])
		return False
		#update camera information to UI check list

def create_CameraInfo_file(ip, password):
	root_path = '/home/ke/TrafficProject/Mask-RCNN/'
	json_file_path = root_path + "/Cameras/"+ ip + "/" + ip + "_metadata.json"
	copyfile(root_path + "camera_info_example.json", json_file_path)
	current_time = time.localtime(time.time())
	#password
	with open(json_file_path, "r") as json_file:
		json_data = json.load(json_file)
		tmp1 = json_data["ip_address"]
		tmp2 = json_data["password"]
		tmp3 = json_data["create_time"]
		json_data["ip_address"] = ip
		json_data["create_time"] = str(current_time[0]) + str(current_time[1])
		json_data["password"] = password

	with open(json_file_path, "w") as json_file:
		json.dump(json_data, json_file)


def create_default_roi(ip):
	roi, encoded = region_select(ip)
	cv2.imshow("image_masked", encoded)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	return roi
#write roi into the infofile

def save_roi_info(ip):
	root_path = '/home/ke/TrafficProject/Mask-RCNN/'

	with open(root_path + "/Cameras/" + ip + "/" + ip + "_metadata.json", 'r') as json_file:
    # read a list of lines into data
		json_data = json.load(json_file)
		for key, roi_data in json_data["rois"].items():
			if roi_data == "":
				tmp = json_data["rois"][key]
				json_data["rois"][key] = create_default_roi(ip)
				break
			else:
				json_data["rois"]["roi1"] = create_default_roi(ip)

	with open(root_path + "/Cameras/" + ip + "/" + ip + "_metadata.json", "w") as json_file:
	    json.dump(json_data, json_file)


def return_camera_list():
	Camera_List = os.listdir('/home/ke/TrafficProject/Mask-RCNN/Cameras')
	return Camera_List
# ip='kgong@192.168.0.4'
# save_roi_info(ip)
# # def add_default(ip):
# # 	def check_

def read_camera_info_file(ip):
	camera_info_list = []
	root_path = '/home/ke/TrafficProject/Mask-RCNN/'
	with open(root_path + "/Cameras/"+ ip+ "/" + ip + "_metadata.json", 'r') as json_file:
		json_data = json.load(json_file)
	return json_data

def check_roi_image_existance(ip):
	Camera_path = '/home/ke/TrafficProject/Mask-RCNN/' + 'Cameras/' + ip
	print(Camera_path)
	checker = []
	for File in os.listdir(Camera_path):
		# print(File)
	    if File.endswith('.jpg'):
	    	checker.append(File)
	return len(checker)
