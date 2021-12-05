from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import torch
import os
import base64
import cv2
import numpy as np
import time

app = Flask(__name__)
socketio = SocketIO(app, logger=False, engineio_logger=False, cors_allowed_origins='*')

MODEL = 'yolov5'
VERSION = 'm'
MODELS_PATH = './webapp/static/models'

# Model runing over GPU
model_gpu = torch.hub.load('ultralytics/{}'.format(MODEL), '{}{}'.format(MODEL, VERSION), pretrained=True)

if not os.path.isfile(MODELS_PATH + '/{}{}.pt'.format(MODEL, VERSION)):
    torch.save(torch.hub.load('ultralytics/{}'.format(MODEL), '{}{}'.format(MODEL, VERSION), pretrained=True), MODELS_PATH + '/{}{}.pt'.format(MODEL, VERSION))

# Model runing over CPU
model_cpu = torch.load(MODELS_PATH + '/{}{}.pt'.format(MODEL, VERSION), map_location=torch.device('cpu'))

models = {'CPU': model_cpu, 'GPU': model_gpu}

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

# --- SOCKETS ---
@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('video-stream')
def video_stream(data):
    times = []
    t_start = time.time()
    
    processing_unit = data['processingUnit']
    data_image = data['image']
    # print('PROCESSING UNIT:', processing_unit)

    # Decode image
    im_bytes = base64.b64decode(data_image)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
    frame = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)

    times.append((time.time() - t_start) * 1000)
    print('Decoding time (ms):', times[-1])
    t_start = time.time()

    # Process the image frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = models[processing_unit](frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Plot results into the frame
    for obj in results.pandas().xyxy[0].iterrows():
        obj = obj[1]
        # Print bounding box
        cv2.rectangle(frame, (int(obj['xmin']), int(obj['ymin'])), (int(obj['xmax']), int(obj['ymax'])), (255,202,83), 2)
        # Print object name and accuracy
        cv2.rectangle(frame, (int(obj['xmin']), int(obj['ymin'])), (int(obj['xmax']), int(obj['ymin']) + 13), (255,202,83), -1)
        cv2.putText(frame, obj['name'], (int(obj['xmin']), int(obj['ymin']) + 11), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        # cv2.putText(frame,'{} {:.2f}'.format(obj['name'], obj['confidence']), (int(obj['xmin']), int(obj['ymin']) + 11), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

    times.append((time.time() - t_start) * 1000)
    print('Processing time (ms):', times[-1])
    t_start = time.time()

    # Encode image
    imgencode = cv2.imencode('.jpg', frame)[1]
    stringData = base64.b64encode(imgencode).decode('utf-8')
    b64_src = 'data:image/jpg;base64,'
    stringData = b64_src + stringData

    times.append((time.time() - t_start) * 1000)
    print('Encoding time (ms):', times[-1])
    print('Total time (ms):', sum(times))
    # Emit the frame back
    emit('response_back', stringData)

if __name__ == '__main__':
    socketio.run(app)
