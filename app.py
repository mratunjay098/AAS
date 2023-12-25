import tensorflow as tf 
from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np

app = Flask(__name__)
CORS(app)

# Load the pre-trained model (adjust the path accordingly)
model = load_model('models/nonSegmented/ResNet50.h5')

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

@app.route('/api/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'})

    # Get the bounding box coordinates from the request (you need to adjust this part based on your frontend implementation)
    x, y, width, height = map(float, request.form.get('bbox').split(','))

    image = request.files['image']
    img = Image.open(image).resize((224, 224))  # Adjust size according to your model

    # Apply segmentation using the bounding box
    segmented_image = img.crop((x, y, x + width, y + height)).resize((224, 224))

    # Convert segmented image to numpy array for classification
    segmented_img_array = np.expand_dims(np.array(segmented_image), axis=0)

    # Perform classification on the cropped image
    prediction = model.predict(segmented_img_array)
    predicted_class = np.argmax(prediction)

    class_name = get_class_name(predicted_class)

    return jsonify({'predictedClass': str(predicted_class), 'className': class_name})

if __name__ == '__main__':
    app.run(debug=True)