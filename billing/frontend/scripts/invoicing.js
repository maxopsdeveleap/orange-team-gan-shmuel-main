document.addEventListener('DOMContentLoaded', function () {
    const generateInvoiceForm = document.getElementById('generate-invoice-form');
    const invoiceResult = document.getElementById('invoice-result');
    const invoiceHistoryForm = document.getElementById('invoice-history-form');
    const invoiceHistoryList = document.getElementById('invoice-history-list');

    // Generate Invoice
    generateInvoiceForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const provider_id = document.getElementById('provider-id-invoice').value;
        const fromDate = document.getElementById('from-date').value;
        const toDate = document.getElementById('to-date').value;

        fetch(`http://localhost:5000/bill/${provider_id}?from=${fromDate}&to=${toDate}`)
            .then(response => response.json())
            .then(data => {
                invoiceResult.innerHTML = `
                    <div class="p-2 bg-gray-50 rounded-md">
                        <p><strong>Provider:</strong> ${data.name}</p>
                        <p><strong>From:</strong> ${data.from}</p>
                        <p><strong>To:</strong> ${data.to}</p>
                        <p><strong>Total:</strong> ${data.total}</p>
                        <p><strong>Products:</strong></p>
                        <ul class="list-disc pl-5">
                            ${data.products.map(product => `
                                <li>${product.product}: ${product.amount} units, Pay: ${product.pay}</li>
                            `).join('')}
                        </ul>
                    </div>
                `;
            })
            .catch(error => {
                console.error('Error generating invoice:', error);
                invoiceResult.innerHTML = '<div class="text-red-500">Error generating invoice.</div>';
            });
    });

    // Fetch Invoice History
    invoiceHistoryForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const provider_id = document.getElementById('provider-id-history').value;

        fetch(`http://localhost:5000/bill/history/${provider_id}`)
            .then(response => response.json())
            .then(data => {
                invoiceHistoryList.innerHTML = ''; // Clear existing list
                data.forEach(invoice => {
                    const invoiceItem = document.createElement('div');
                    invoiceItem.className = 'p-2 bg-gray-50 rounded-md';
                    invoiceItem.textContent = `Invoice ID: ${invoice.id}, Total: ${invoice.total}`;
                    invoiceHistoryList.appendChild(invoiceItem);
                });
            })
            .catch(error => {
                console.error('Error fetching invoice history:', error);
                invoiceHistoryList.innerHTML = '<div class="text-red-500">Error loading invoice history.</div>';
            });
    });
});
