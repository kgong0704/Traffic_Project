from tkinter import *
from tkinter import messagebox as tkMessageBox, filedialog
from take_image import take_image
from add_camera import check_existance, create_CameraInfo_file, return_camera_list, read_camera_info_file, check_roi_image_existance, save_roi_info
from video_analysis import VideoAnalysis
from region_select import region_select
import os
import json
import cv2

Mode = "video"; roi_image_checker = 0


def add_camera():
	value1 = addr.get()
	value2 = passw.get()
	if check_existance(value1) == True:
		tkMessageBox.showinfo("existed", "The camera already existed.")
	else:
		tkMessageBox.askquestion("Delete", "Doulbe check your camera information!!", icon='warning')
		if 'yes':
			create_CameraInfo_file(value1, value2)
			print("new camera added!")
		else:
			print("I'm Not Deleted Yet")
	
def create_cameralist_window():
	window = Toplevel(secondFrame)
	camera_list = return_camera_list()

	for idx, camera_ip in enumerate(camera_list):
		b = Button(window, text=camera_ip, command= lambda camera_ip = camera_ip: create_taking_window(camera_ip))
		b.grid(row=idx, column=0)


	def create_taking_window(camera_ip):
		global roi_image_checker
		#video_default_setting
		path = os.getcwd() + '/Cameras/' + camera_ip
		camera_info = read_camera_info_file(camera_ip)
		def check_roi_image_existance(ip):
			Camera_path = os.getcwd() + '/Cameras/' + ip
			checker = []
			for File in os.listdir(Camera_path):
				# print(File)
			    if File.endswith('.jpg'):
			    	checker.append(File)
			return len(checker)
		roi_image_checker = check_roi_image_existance(camera_ip)


		def mode_swtich_toggle():
			global Mode
			if t_btn.config('text')[-1] == 'video':
			    t_btn.config(text='photo')
			    Mode = "photo"
			else:
			    t_btn.config(text='video')
			    Mode = "video"


		def update_video_duration():
			new_time = [0,0,0]
			h = time1.get()
			m = time2.get()
			s = time3.get()

			if Mode == 'photo':
				time = 'N/A'
			else:
				if not h:
					new_time[0] = '00'
				if h:
					new_time[0] = str(h).zfill(2)
				if not h:
					new_time[1] = '00'
				if m:
					new_time[1] = str(m).zfill(2)
				if not s:
					new_time[2] = '00'
				if s:
					new_time[2] = str(s).zfill(2)

			json_file_path = "./Cameras/" + camera_ip + "/" + camera_ip + "_metadata.json"
			# password
			with open(json_file_path, "r") as json_file:
				json_data = json.load(json_file)
				tmp = json_data["video_length"]
				json_data["video_length"] = new_time

			with open(json_file_path, "w") as json_file:
				json.dump(json_data, json_file)


		def get_video_image_taking():
			json_file_path = "./Cameras/" + camera_ip + "/" + camera_ip + "_metadata.json"
			# password
			with open(json_file_path, "r") as json_file:
				json_data = json.load(json_file)
				duration = json_data["video_length"]

			take_image(camera_ip, camera_info["password"], os.getcwd() + '/Cameras/' + camera_ip, '1280x720', '30',
					   duration[0] + ':' + duration[1] + ':' + duration[2], Mode)

		camera_info_window = Toplevel(window)

		t_btn = Button(camera_info_window, text="video", width=12, command=mode_swtich_toggle)
		t_btn.grid(row=3, column=0)


		image_taking = Button(camera_info_window, text='taking', width=12, command=get_video_image_taking)
		image_taking.grid(row=5, column=0)

		def create_analysis_window():
			ana_window = Toplevel(camera_info_window)

			def update_resolution():
				value = resolution_options[choice.get()]
				label_reso.config(text=(str(value[0]) + ' x ' + str(value[1])))
				json_file_path =  "./Cameras/" + camera_ip + "/" + camera_ip + "_metadata.json"
				# password
				with open(json_file_path, "r") as json_file:
					json_data = json.load(json_file)
					tmp = json_data["resolution"]
					json_data["resolution"] = value

				with open(json_file_path, "w") as json_file:
					json.dump(json_data, json_file)

			def update_frame_rate():
				value = fr_options[choice_fr.get()]
				label_fr.config(text=(value))
				json_file_path =  "./Cameras/" + camera_ip + "/" + camera_ip + "_metadata.json"
				# password
				with open(json_file_path, "r") as json_file:
					json_data = json.load(json_file)
					tmp = json_data["frame_rate"]
					json_data["frame_rate"] = value

				with open(json_file_path, "w") as json_file:
					json.dump(json_data, json_file)

			def anay_video():
				in_path = filedialog.askopenfilename(initialdir= "./Cameras/" + camera_ip + "/Videos")
				out_path = "./Cameras/" + camera_ip + "/Videos" + '/out_temp.mp4'
				json_file_path = "./Cameras/" + camera_ip + "/" + camera_ip + "_metadata.json"
				# password
				with open(json_file_path, "r") as json_file:
					json_data = json.load(json_file)

				cap = cv2.VideoCapture(in_path)
				flag, frame = cap.read()
				cv2.imwrite('./Cameras/' + camera_ip + '/temp.jpg', frame)
				ori_reso = (frame.shape[1], frame.shape[0])
				x, _ = region_select(camera_ip)
				os.remove('./Cameras/' + camera_ip + '/temp.jpg')

				VA = VideoAnalysis(in_path, out_path, json_data['resolution'], ori_reso, 30, json_data['frame_rate'],
								   sorted_refPt=x)
				VA.mask_video()
				arr = VA.mask_rcnn_apply()
				interested_frame = VA.find_interested_frames(arr, 2)
				VA.clip_video(interested_frame)

			# resolution option menu
			resolution_options = {'high': (1280,720),  'median': (800,600), 'low': (640,400)}
			choice = StringVar()
			choice.set("high")  # default value, to use value: choice.get()
			Label(ana_window, text='resolution').grid(row=1)
			popupChoice = OptionMenu(ana_window, choice, *resolution_options, command=lambda x:update_resolution())
			popupChoice.grid(row=1, column=1)
			label_reso = Label(ana_window, text=str(resolution_options[choice.get()][0])+' x '+str(resolution_options[choice.get()][1]))
			label_reso.grid(row=1, column=2)

			fr_options = {'5': 5,  '2': 2, '1': 1}
			choice_fr = StringVar()
			choice_fr.set("1")  # default value, to use value: choice.get()
			Label(ana_window, text='framerate').grid(row=2)
			popupChoice = OptionMenu(ana_window, choice_fr, *fr_options, command=lambda x:update_frame_rate())
			popupChoice.grid(row=2, column=1)
			label_fr = Label(ana_window, text=fr_options[choice_fr.get()])
			label_fr.grid(row=2, column=2)

			ana_butt = Button(ana_window, text='process video', command=anay_video)
			ana_butt.grid(row=3, column=0)


		time_label = Label(camera_info_window, text='video time').grid(row=0)
		t1 = StringVar()
		time1 = Entry(camera_info_window, textvariable=t1,width=5)
		time1.grid(row=0, column=1) # grid is more useful for more customization
		label1 = Label(camera_info_window, text=':').grid(row=0, column=2)
		if roi_image_checker > 0:
			time1.config(state = NORMAL)
		else:
			time1.config(state = DISABLED)

		t2 = StringVar()
		time2 = Entry(camera_info_window, textvariable=t2,width=5)
		time2.grid(row=0, column=3) # grid is more useful for more customization
		label2 = Label(camera_info_window, text=':').grid(row=0, column=4)
		if roi_image_checker > 0:
			time2.config(state = NORMAL)
		else:
			time2.config(state = DISABLED)

		t3 = StringVar()
		time3 = Entry(camera_info_window, textvariable=t3, width=5)
		time3.grid(row=0, column=5) # grid is more useful for more customization
		if roi_image_checker > 0:
			time3.config(state = NORMAL)
		else:
			time3.config(state = DISABLED)

		add_ip_info = Button(camera_info_window, command=update_video_duration, text='update_time')
		add_ip_info.grid(row=0, column=6)

		roi_taking = Button(camera_info_window, text='roi_taking', command=lambda:save_roi_info(camera_ip))
		roi_taking.grid(row=4, column=0)
		if roi_image_checker > 0:
			roi_taking.config(state = NORMAL)
		else:
			roi_taking.config(state = DISABLED)

		ana_butt = Button(camera_info_window, text='analysis video', command=create_analysis_window)
		ana_butt.grid(row=4, column=1)



secondFrame = Tk()
# entry for value
addr = StringVar()
ip_address = Entry(secondFrame, textvariable=addr).grid(row=0, column=1) # grid is more useful for more customization
ip_label = Label(secondFrame, text='ip').grid(row=0)

passw = StringVar()
ip_password = Entry(secondFrame, textvariable=passw).grid(row=1, column=1) # grid is more useful for more customization
passw_label = Label(secondFrame, text='password').grid(row=1)


add_ip_info = Button(secondFrame, command=add_camera, text='add').grid(row=0, column=2)

# label showing result or other text


b = Button(secondFrame, text="check existed cameras", command=create_cameralist_window).grid(row=1, column=2)



secondFrame.mainloop()