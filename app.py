from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt
import os
from PIL import Image
import numpy as np
import base64
from segment_anything import sam_model_registry, SamPredictor
import torch
import cv2
import time

app = Flask(__name__)
CORS(app)

# Load the pre-trained classification model
model = load_model('models/segmented/ResNet50.h5')

# Load the segmentation model
CHECKPOINT_PATH = "sam_vit_h_4b8939.pth"
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
MODEL_TYPE = "vit_h"
sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECKPOINT_PATH).to(device=DEVICE)
mask_predictor = SamPredictor(sam)

def get_class_name(predicted_class):
    class_names = [ 
        'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
        'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
        'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot',
        'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
        'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
        'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight',
        'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy',
        'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
        'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold',
        'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot',
        'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
    ]

    # Ensure the predicted class index is within the valid range
    if 0 <= predicted_class < len(class_names):
        return class_names[predicted_class]
    else:
        return f'Unknown Class (Index: {predicted_class})'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}) 

        seg_start_time = time.time()

        # Get the image file from the POST request
        image_data = request.files['image']
        print(image_data)
        nparr = np.fromstring(image_data.read(), np.uint8)
        image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Get the bounding box coordinates from the request (you need to adjust this part based on your frontend implementation)
        x, y, width, height = map(float, request.form.get('bbox').split(','))

        default_box = {'x': x, 'y': y, 'width': width, 'height': height, 'label': ''}
        box = default_box
        box = np.array([
            box['x'],
            box['y'],
            box['x'] + box['width'],
            box['y'] + box['height']
        ])
        # Perform segmentation
        mask_predictor.set_image(image_bgr)
        masks, scores, logits = mask_predictor.predict(
            box=box,
            multimask_output=True
        )

        # Apply segmentation mask to the original image
        roi = image_bgr.copy()
        largest_mask_index = np.argmax([np.sum(mask) for mask in masks])
        print(largest_mask_index)
        largest_mask = masks[largest_mask_index]
        roi[~largest_mask.astype(bool)] = 0

        # Save the segmented image roi
        segmented_image_path = 'segmented_roi.jpg'
        cv2.imwrite(segmented_image_path, roi)

        # Convert segmented image to base64 string
        _, encoded_image = cv2.imencode('.jpg', roi)       
        segmented_image_base64 = base64.b64encode(encoded_image).decode('utf-8')

        seg_end_time = time.time()
        print('Segmentation Time: ', (seg_end_time-seg_start_time))

        # Perform classification on the segmented image
        classification_result = classify_segmented_image(roi)
        
        class_end_time = time.time()
        print('Classification Time: ', (class_end_time-seg_end_time))

        result = {'success': True, 'segmented_image': segmented_image_base64, 'classification_result': classification_result}

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def classify_segmented_image(segmented_image):
    try:
        # Resize segmented image to match the expected input shape of the model
        resized_image = cv2.resize(segmented_image, (224, 224))

        # Convert resized image to numpy array for classification
        segmented_img_array = np.expand_dims(resized_image, axis=0)

        # Perform classification on the segmented image
        prediction = model.predict(segmented_img_array)
        predicted_class = np.argmax(prediction)

        class_name = get_class_name(predicted_class)

        return {'success': True, 'predictedClass': int(predicted_class), 'className': class_name}

    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    app.run(debug=True)
