var processingUnit = 'CPU'; // CPU | GPU
var fps = 0;

// used to record the time when we processed last frame
prev_frame_time = 0
// used to record the time at which we processed current frame
new_frame_time = 0

const video = document.querySelector("#videoInput");

video.width = 640;
video.height = 480;

var socket = io('ws://localhost:5000', { transports: ['websocket'] });

function changeToCPU() {
    processingUnit = 'CPU';
    console.log('Changing to ' + processingUnit);
};

function changeToGPU() {
    processingUnit = 'GPU';
    console.log('Changing to ' + processingUnit);
};

socket.on('connect', function () {
    console.log("Connected...!", socket.connected)
});

if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
            video.play();
        })
        .catch(function (err0r) {
            console.log(err0r)
            console.log("Something went wrong!");
        });
}


let src = new cv.Mat(video.height, video.width, cv.CV_8UC4);
let cap = new cv.VideoCapture(video);

function sendFrame() {
    cap.read(src);
    cv.imshow("canvasOutput", src);

    var type = "image/jpeg";
    var data = document.getElementById("canvasOutput").toDataURL(type, 0.3);
    data = data.replace('data:' + type + ';base64,', ''); 
    
    socket.emit('video-stream', { "processingUnit": processingUnit, "image": data });
};

function sendFirstFrame() {
    console.log('Sending first frame');
    sendFrame();
};

sendFirstFrame();

async function computeFPS() {
    console.log('Total processing time (ms):', new_frame_time - prev_frame_time)
    fps = Math.ceil(1000 / (new_frame_time - prev_frame_time));
    prev_frame_time = new_frame_time;

    document.getElementById("fps-display").innerHTML = `FPS: ${fps}.0`
}

socket.on('response_back', function (image) {
    const image_id = document.getElementById('videOutput');
    image_id.src = image;

    // time when we finish processing for this frame
    // new_frame_time = Date.now();
    // computeFPS();

    sendFrame();
});

socket.on('connect_error', (err) => {
    console.log(`connect_error due to ${err.message}`);
});