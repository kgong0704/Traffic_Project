#!/bin/sh
# s1 for host_ip, s2 for host_password
sshpass -p $2 ssh -T -o StrictHostKeyChecking=no $1 << EOF
ls
# ffmpeg -i out.mp4 -t 05.00 -r 1 -y -vf scale=640:360 output.mp4
# ffmpeg -i out.mp4 -vf scale=640:360 video_640.mp4
ffmpeg -f avfoundation -pix_fmt uyvy422 -video_size $6 -framerate $7 -i "default:none" $8 /Users/kgong/$5
sshpass -p $4 scp /Users/kgong/$5 $3:$9
rm $5
EOF