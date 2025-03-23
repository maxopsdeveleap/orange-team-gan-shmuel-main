document.addEventListener('DOMContentLoaded', function () {
    const ratesList = document.getElementById('rates-list');
    const uploadRatesForm = document.getElementById('upload-rates-form');

    function fetchRates() {
        fetch('http://localhost:5000/rates', {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            ratesList.innerHTML = ''; // Clear list
            data.forEach(rate => {
                const rateItem = document.createElement('li');
                rateItem.textContent = `Product: ${rate.product}, Rate: ${rate.rate} agorot`;
                ratesList.appendChild(rateItem);
            });
        })
        .catch(error => console.error("Error fetching rates:", error));
    }

    uploadRatesForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const fileInput = document.getElementById('rates-file');
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        fetch('http://localhost:5000/rates', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(() => fetchRates()) // Refresh rates list
        .catch(error => console.error("Error uploading rates:", error));
    });

    fetchRates();
});
