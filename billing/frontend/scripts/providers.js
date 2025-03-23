document.addEventListener('DOMContentLoaded', function () {
    const providersList = document.getElementById('providers-list');
    const addProviderForm = document.getElementById('add-provider-form');

    function fetchProviders() {
        fetch('http://localhost:5000/provider', {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            providersList.innerHTML = '';
            data.forEach(provider => {
                const item = document.createElement('li');
                item.textContent = provider.name;
                providersList.appendChild(item);
            });
        })
        .catch(error => console.error("Fetch error:", error));
    }

    addProviderForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const formData = { name: document.getElementById('provider-name').value };

        fetch('http://localhost:5000/provider', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(() => fetchProviders()) // Refresh list
        .catch(error => console.error("Error adding provider:", error));
    });

    fetchProviders();
});
