# then navigate to: http://<kindbot_IP>:8080/stream_simple.html
mkdir /tmp/stream/
raspistill --nopreview -w 1280 -h 720 -q 5 -o /tmp/stream/pic.jpg -tl 100 -t 0 -th 0:0:0 &
export LD_LIBRARY_PATH=/home/pi/mjgp-streamer/mjpg-streamer-experimental/ 
cd /home/pi/mjpg-streamer/mjpg-streamer-experimental/
/home/pi/mjpg-streamer/mjpg-streamer-experimental/mjpg_streamer -i "input_file.so -f /tmp/stream -n pic.jpg" -o "output_http.so -w ./www"

