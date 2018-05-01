import subprocess
from PIL import Image
import json
import datetime

# from add_camera import check_existance
def take_image(targe_ip, ip_passcode, path, resolution, framerate, time, Mode, file_name=None):
	if Mode == "photo":
		file_name = file_name or "out.jpg"
		subprocess.call(['./ssh_connect.sh', targe_ip, ip_passcode, 'ke@192.168.0.6', 'Gk@135790', file_name, resolution, framerate, '-vframes 1', path])
		im = Image.open(path + '/' + file_name)
		width, height = im.size
		root_path = '/home/ke/TrafficProject/Mask-RCNN/'
		json_file_path = root_path + "/Cameras/" + targe_ip + "/" + targe_ip + "_metadata.json"
		with open(json_file_path, "r") as json_file:
			json_data = json.load(json_file)
			tmp1 = json_data["resolution"]
			json_data["resolution"] = (width,height)
		with open(json_file_path, "w") as json_file:
			json.dump(json_data, json_file)

	else:
		file_name = file_name or "out.mp4"
		subprocess.call(['./ssh_connect.sh', targe_ip, ip_passcode, 'ke@192.168.0.6', 'Gk@135790', file_name, resolution, framerate, '-t '+ time, path])


# take_image('kgong@192.168.0.4', 'tristanwolf3', '/home/ke/test.mp4', '1280x720', '30', '5', 'video', 'out.mp4')
# take_image('kgong@192.168.0.4', 'tristanwolf3', 'Downloads/', '1280x720', '30', '5', 'photo')
# cv_display_instances()
