# CPU/GPU object detection in video streaming

Demo developed to visually show the difference in data processing speed between a
CPU and a GPU. The demo raises a webapp in ```localhost:5000``` that captures the webcam and processes the frames
with a deep learning model (YOLO v5) to detect the objects present in the image, allowing the user
choose if this model runs on the CPU or on the GPU.


## Install
### Create and activate virtual environment:

```
python3 -m venv venv; source venv/bin/activate
```


### Install dependencies:

```
pip install -r requirements.txt
```

### install app

```
cd webapp; python setup.py install
```


### Init app

```
cd ..; sh dev-tmux.sh
```
