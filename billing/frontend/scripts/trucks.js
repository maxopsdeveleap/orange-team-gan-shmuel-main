document.addEventListener('DOMContentLoaded', function () {
    const trucksList = document.getElementById('trucks-list');
    const addTruckForm = document.getElementById('add-truck-form');

    function fetchTrucks() {
        fetch('http://localhost:5000/truck', {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            trucksList.innerHTML = '';
            data.forEach(truck => {
                const item = document.createElement('li');
                item.textContent = `Truck ${truck.id} - Provider: ${truck.provider_id}`;
                trucksList.appendChild(item);
            });
        })
        .catch(error => console.error("Fetch error:", error));
    }

    function fetchTruckById(truckId) {
        fetch(`http://localhost:5000/truck/${truckId}`, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error("Error fetching truck:", error));
    }

    fetchTrucks();
});
