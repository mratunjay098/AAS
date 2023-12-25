const canvas = document.getElementById('imageCanvas');
const ctx = canvas.getContext('2d');
const croppedCanvas = document.getElementById('croppedCanvas');
const croppedCtx = croppedCanvas.getContext('2d');
let drawing = false;
let bbox = {};

// Event listeners for drawing bounding box
canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);

function startDrawing(e) {
    drawing = true;
    const rect = canvas.getBoundingClientRect();
    bbox = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
        width: 0,
        height: 0
    };
    
    // Draw the selected image on the canvas
    drawImageOnCanvas();
}

function draw(e) {
    if (!drawing) return;
    const rect = canvas.getBoundingClientRect();
    bbox.width = e.clientX - rect.left - bbox.x;
    bbox.height = e.clientY - rect.top - bbox.y;
    
    // Clear canvas and draw bounding box
    clearCanvas();
    drawBoundingBox();
    
    // Draw the selected image on the canvas
    drawImageOnCanvas();
}

function drawCroppedImage() {
    const input = document.getElementById('imageInput');
    const file = input.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = new Image();
            img.onload = function () {
                // Draw the cropped region on the second canvas
                croppedCtx.fillStyle = '#FFFFFF'; // Set fill color to white
                croppedCtx.fillRect(0, 0, croppedCanvas.width, croppedCanvas.height); // Fill the canvas with white
                croppedCtx.drawImage(img, bbox.x, bbox.y, bbox.width, bbox.height, 0, 0, croppedCanvas.width, croppedCanvas.height);
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

function stopDrawing() {
    drawing = false;
    // Update the hidden input field with the bounding box coordinates
    document.getElementById('bbox').value = `${bbox.x},${bbox.y},${bbox.width},${bbox.height}`;
    
    // Draw the cropped region on the second canvas
    drawCroppedImage();
}

function drawImageOnCanvas() {
    const input = document.getElementById('imageInput');
    const file = input.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = new Image();
            img.onload = function () {
                // Draw the original image on the canvas
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                // Draw the bounding box
                drawBoundingBox();
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

function clearCanvas() {
    // Clear only the bounding box region
    ctx.clearRect(bbox.x, bbox.y, bbox.width, bbox.height);
}

function drawBoundingBox() {
    ctx.strokeStyle = '#FF0000';
    ctx.lineWidth = 2;
    ctx.strokeRect(bbox.x, bbox.y, bbox.width, bbox.height);
}

function uploadImage() {
    const input = document.getElementById('imageInput');
    const file = input.files[0];

    const formData = new FormData();
    formData.append('image', file);
    formData.append('bbox', document.getElementById('bbox').value);

    const resultElement = document.getElementById('result');

    // Clear previous result
    resultElement.innerHTML = '';
    resultElement.classList.remove('result-visible');

    // Update the URL to point to your local Flask server
    fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const classResult = document.createElement('div');

        // Display predicted class index
        classResult.innerHTML = `Predicted Class Index: ${data.predictedClass}`;

        // Display predicted class name
        if (data.className) {
            const classNameResult = document.createElement('div');
            classNameResult.innerHTML = `Predicted Class Name: ${data.className}`;
            resultElement.appendChild(classNameResult);
        }

        resultElement.appendChild(classResult);
        resultElement.classList.add('result-visible');
    })
    .catch(error => console.error('Error:', error));

    // Draw the original image on the canvas immediately after uploading
    drawImageOnCanvas();
}
