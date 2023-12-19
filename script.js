function uploadImage() {
    const input = document.getElementById('imageInput');
    const file = input.files[0];

    const formData = new FormData();
    formData.append('image', file);

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
}
