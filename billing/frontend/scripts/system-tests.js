document.addEventListener('DOMContentLoaded', function () {
    const healthCheckButton = document.getElementById('health-check-button');
    const healthCheckResult = document.getElementById('health-check-result');
    const uploadTestsForm = document.getElementById('upload-tests-form');
    const testPasswordInput = document.getElementById('test-password');

    healthCheckButton.addEventListener('click', function () {
        fetch('http://localhost:5000/health', {
            method: 'GET'
        })
        .then(response => {
            if (!response.ok) throw new Error(`Error: ${response.status}`);
            return response.text();
        })
        .then(data => {
            healthCheckResult.textContent = data;
        })
        .catch(error => console.error("Error fetching health status:", error));
    });

    uploadTestsForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const fileInput = document.getElementById('test-file');
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('password', testPasswordInput.value);

        fetch('http://localhost:5000/upload-tests', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => console.log("Test upload successful:", data))
        .catch(error => console.error("Error uploading test:", error));
    });
});
