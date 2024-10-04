// main.js

// Document ready function
document.addEventListener("DOMContentLoaded", function () {
    // Initialize tooltips
    const tooltipElements = document.querySelectorAll('.tooltip');
    tooltipElements.forEach(elem => {
        elem.addEventListener('mouseover', function () {
            // Show tooltip
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip-box';
            tooltip.innerHTML = tooltipText;
            document.body.appendChild(tooltip);
            tooltip.style.left = `${this.getBoundingClientRect().left}px`;
            tooltip.style.top = `${this.getBoundingClientRect().top - tooltip.offsetHeight}px`;
        });

        elem.addEventListener('mouseout', function () {
            // Remove tooltip
            const tooltipBox = document.querySelector('.tooltip-box');
            if (tooltipBox) {
                tooltipBox.remove();
            }
        });
    });

    // Event listener for county change
    const countySelect = document.getElementById('countySelect');
    countySelect.addEventListener('change', function () {
        const countyId = this.value;
        if (countyId) {
            // Fetch sub-counties based on selected county
            fetchData(`/api/subcounties/${countyId}`, populateSubcounties);
        } else {
            clearSubcounties();
            clearTowns();
        }
    });

    // Event listener for sub-county change
    const subcountySelect = document.getElementById('subcountySelect');
    subcountySelect.addEventListener('change', function () {
        const subcountyId = this.value;
        if (subcountyId) {
            // Fetch towns based on selected sub-county
            fetchData(`/api/towns/${subcountyId}`, populateTowns);
        } else {
            clearTowns();
        }
    });

    // Form validation example
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (event) {
            // Prevent form submission if validation fails
            if (!validateForm(form)) {
                event.preventDefault();
                alert('Please fill out all required fields correctly.');
            }
        });
    });
});

// Function to validate form fields
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('invalid');
        } else {
            field.classList.remove('invalid');
        }
    });

    return isValid;
}

// Fetch data from the server
function fetchData(url, callback) {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            callback(data);
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });
}

// Populate subcounties dropdown
function populateSubcounties(subcounties) {
    const subcountySelect = document.getElementById('subcountySelect');
    subcountySelect.innerHTML = '<option value="">Select Sub-County</option>'; // Reset options
    subcounties.forEach(subcounty => {
        const option = document.createElement('option');
        option.value = subcounty.id; // Assuming each subcounty object has an 'id' property
        option.textContent = subcounty.name; // Assuming each subcounty object has a 'name' property
        subcountySelect.appendChild(option);
    });
}

// Clear subcounties dropdown
function clearSubcounties() {
    const subcountySelect = document.getElementById('subcountySelect');
    subcountySelect.innerHTML = '<option value="">Select Sub-County</option>'; // Reset options
    clearTowns();
}

// Populate towns dropdown
function populateTowns(towns) {
    const townSelect = document.getElementById('townSelect');
    townSelect.innerHTML = '<option value="">Select Town/Ward</option>'; // Reset options
    towns.forEach(town => {
        const option = document.createElement('option');
        option.value = town.id; // Assuming each town object has an 'id' property
        option.textContent = town.name; // Assuming each town object has a 'name' property
        townSelect.appendChild(option);
    });
}

// Clear towns dropdown
function clearTowns() {
    const townSelect = document.getElementById('townSelect');
    townSelect.innerHTML = '<option value="">Select Town/Ward</option>'; // Reset options
}

// Example function to show a success message
function showSuccessMessage(message) {
    const messageBox = document.createElement('div');
    messageBox.className = 'success-message';
    messageBox.textContent = message;
    document.body.appendChild(messageBox);
    setTimeout(() => {
        messageBox.remove();
    }, 3000); // Remove after 3 seconds
}

// Example event listener for a button (e.g., for placing an order)
document.getElementById('orderButton').addEventListener('click', function () {
    const productId = this.getAttribute('data-product-id');
    // Place order logic here, such as making an AJAX request
    showSuccessMessage('Order placed successfully!');
});
