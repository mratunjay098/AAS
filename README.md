# Agricultural Assistance System (AAS)

Agricultural Assistance System (AAS) is a Disease Detection System designed to assist farmers in identifying diseases affecting their crops. This system utilizes computer vision techniques to analyze images of plants and detect any signs of diseases.

## Features

- **Image Upload**: Users can upload images of plants affected by diseases.
- **Bounding Box Selection**: Users can draw bounding boxes around the region of interest in the uploaded images.
- **Segmentation**: The system performs segmentation on the selected region to isolate the diseased areas.
- **Classification**: The segmented region are then classified to identify the type of disease present.
- **Real-time Feedback**: In future, The system will provide real-time feedback on the predicted disease type.

## Installation

To set up the Agricultural Assistance System locally, follow these steps:

1. Clone the repository: `git clone https://github.com/mratunjay098/AAS.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the Flask application: `python app.py`
4. Access the system through your web browser at `http://localhost:5000`

## Usage

1. Open the web application in your browser.
2. Upload an image of a plant affected by a disease.
3. Draw a bounding box around the diseased area.
4. Click on the "Detect Disease" button to initiate the disease detection process.
5. View the classification result and segmented image on the interface.

## Inference

![Agricultural Assistance System]('images/p_final.png')

## Contributors

- [Mratunjay Singh](https://github.com/mratunjay098)

## License

This project is licensed under the [MIT License](LICENSE).
