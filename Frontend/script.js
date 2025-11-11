// Data storage (simulating a database)
let dogRecords = [];
let dietRecords = [];
let editingDogId = null;
let editingDietId = null;

// DOM Elements
const dogForm = document.getElementById('dogForm');
const dietForm = document.getElementById('dietForm');
const searchBtn = document.getElementById('searchBtn');
const searchUserId = document.getElementById('searchUserId');
const searchResults = document.getElementById('searchResults');
const showAllBtn = document.getElementById('showAllBtn');
const clearAllBtn = document.getElementById('clearAllBtn');
const allRecords = document.getElementById('allRecords');

// Form buttons
const updateDogBtn = document.getElementById('updateDogBtn');
const deleteDogBtn = document.getElementById('deleteDogBtn');
const clearDogForm = document.getElementById('clearDogForm');
const updateDietBtn = document.getElementById('updateDietBtn');
const deleteDietBtn = document.getElementById('deleteDietBtn');
const clearDietForm = document.getElementById('clearDietForm');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadStoredData();
    setupEventListeners();
    displayAllRecords();
});

// Load data from localStorage
function loadStoredData() {
    const storedDogRecords = localStorage.getItem('dogRecords');
    const storedDietRecords = localStorage.getItem('dietRecords');
    
    if (storedDogRecords) {
        dogRecords = JSON.parse(storedDogRecords);
    }
    
    if (storedDietRecords) {
        dietRecords = JSON.parse(storedDietRecords);
    }
}

// Save data to localStorage
function saveData() {
    localStorage.setItem('dogRecords', JSON.stringify(dogRecords));
    localStorage.setItem('dietRecords', JSON.stringify(dietRecords));
}

// Setup event listeners
function setupEventListeners() {
    // Dog form submission
    dogForm.addEventListener('submit', handleDogFormSubmit);
    
    // Diet form submission
    dietForm.addEventListener('submit', handleDietFormSubmit);
    
    // Search functionality
    searchBtn.addEventListener('click', handleSearch);
    searchUserId.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    
    // Update buttons
    updateDogBtn.addEventListener('click', handleDogUpdate);
    updateDietBtn.addEventListener('click', handleDietUpdate);
    
    // Delete buttons
    deleteDogBtn.addEventListener('click', handleDogDelete);
    deleteDietBtn.addEventListener('click', handleDietDelete);
    
    // Clear form buttons
    clearDogForm.addEventListener('click', () => clearForm('dog'));
    clearDietForm.addEventListener('click', () => clearForm('diet'));
    
    // Show all records
    showAllBtn.addEventListener('click', displayAllRecords);
    
    // Clear all data
    clearAllBtn.addEventListener('click', handleClearAllData);
    
    // Breed selection handler for "Other" option
    const breedSelect = document.getElementById('dogBreed');
    breedSelect.addEventListener('change', handleBreedSelection);
}

// Handle breed selection to show/hide "Other" text field
function handleBreedSelection() {
    const breedSelect = document.getElementById('dogBreed');
    const otherBreedsGroup = document.getElementById('otherBreedsGroup');
    const selectedValues = Array.from(breedSelect.selectedOptions).map(option => option.value);
    
    if (selectedValues.includes('other')) {
        otherBreedsGroup.style.display = 'block';
        otherBreedsGroup.classList.add('show');
    } else {
        otherBreedsGroup.style.display = 'none';
        otherBreedsGroup.classList.remove('show');
        // Clear the other breeds field when not needed
        document.getElementById('otherBreeds').value = '';
    }
}

// Handle dog form submission
function handleDogFormSubmit(e) {
    e.preventDefault();
    
    if (!validateDogForm()) {
        return;
    }
    
    const formData = new FormData(dogForm);
    const breedSelect = document.getElementById('dogBreed');
    const selectedBreeds = Array.from(breedSelect.selectedOptions).map(option => option.value);
    const otherBreeds = document.getElementById('otherBreeds').value.trim();
    
    const dogData = {
        id: editingDogId || generateId(),
        userId: formData.get('userId').trim(),
        name: formData.get('dogName').trim(),
        age: parseInt(formData.get('dogAge')),
        breeds: selectedBreeds,
        otherBreeds: otherBreeds,
        weight: parseFloat(formData.get('dogWeight')),
        createdAt: editingDogId ? dogRecords.find(d => d.id === editingDogId).createdAt : new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };
    
    if (editingDogId) {
        // Update existing record
        const index = dogRecords.findIndex(d => d.id === editingDogId);
        dogRecords[index] = dogData;
        showMessage('Dog information updated successfully!', 'success');
        resetDogEditMode();
    } else {
        // Create new record
        dogRecords.push(dogData);
        showMessage('Dog information saved successfully!', 'success');
    }
    
    saveData();
    clearForm('dog');
    displayAllRecords();
}

// Handle diet form submission
function handleDietFormSubmit(e) {
    e.preventDefault();
    
    if (!validateDietForm()) {
        return;
    }
    
    const formData = new FormData(dietForm);
    
    const dietData = {
        id: editingDietId || generateId(),
        userId: formData.get('dietUserId').trim(),
        foodType: formData.get('foodType'),
        brand: formData.get('brand').trim(),
        amount: formData.get('amount').trim(),
        feedingTimes: parseInt(formData.get('feedingTimes')),
        createdAt: editingDietId ? dietRecords.find(d => d.id === editingDietId).createdAt : new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };
    
    if (editingDietId) {
        // Update existing record
        const index = dietRecords.findIndex(d => d.id === editingDietId);
        dietRecords[index] = dietData;
        showMessage('Diet information updated successfully!', 'success');
        resetDietEditMode();
    } else {
        // Create new record
        dietRecords.push(dietData);
        showMessage('Diet information saved successfully!', 'success');
    }
    
    saveData();
    clearForm('diet');
    displayAllRecords();
}

// Form validation
function validateDogForm() {
    const userId = document.getElementById('userId').value.trim();
    const dogName = document.getElementById('dogName').value.trim();
    const dogAge = document.getElementById('dogAge').value;
    const dogWeight = document.getElementById('dogWeight').value;
    const breedSelect = document.getElementById('dogBreed');
    
    let isValid = true;
    
    if (!userId) {
        showFieldError('userId', 'User ID is required');
        isValid = false;
    } else {
        clearFieldError('userId');
    }
    
    if (!dogName) {
        showFieldError('dogName', 'Dog name is required');
        isValid = false;
    } else {
        clearFieldError('dogName');
    }
    
    if (!dogAge || dogAge < 0 || dogAge > 30) {
        showFieldError('dogAge', 'Please enter a valid age (0-30 years)');
        isValid = false;
    } else {
        clearFieldError('dogAge');
    }
    
    if (!dogWeight || dogWeight < 1 || dogWeight > 200) {
        showFieldError('dogWeight', 'Please enter a valid weight (1-200 lbs)');
        isValid = false;
    } else {
        clearFieldError('dogWeight');
    }
    
    if (breedSelect.selectedOptions.length === 0) {
        showFieldError('dogBreed', 'Please select at least one breed');
        isValid = false;
    } else {
        clearFieldError('dogBreed');
    }
    
    return isValid;
}

function validateDietForm() {
    const userId = document.getElementById('dietUserId').value.trim();
    const foodType = document.querySelector('input[name="foodType"]:checked');
    const brand = document.getElementById('brand').value.trim();
    const amount = document.getElementById('amount').value.trim();
    const feedingTimes = document.getElementById('feedingTimes').value;
    
    let isValid = true;
    
    if (!userId) {
        showFieldError('dietUserId', 'User ID is required');
        isValid = false;
    } else {
        clearFieldError('dietUserId');
    }
    
    if (!foodType) {
        showMessage('Please select a food type', 'error');
        isValid = false;
    }
    
    if (!brand) {
        showFieldError('brand', 'Brand is required');
        isValid = false;
    } else {
        clearFieldError('brand');
    }
    
    if (!amount) {
        showFieldError('amount', 'Amount is required');
        isValid = false;
    } else {
        clearFieldError('amount');
    }
    
    if (!feedingTimes || feedingTimes < 1 || feedingTimes > 6) {
        showFieldError('feedingTimes', 'Please enter valid feeding times (1-6 per day)');
        isValid = false;
    } else {
        clearFieldError('feedingTimes');
    }
    
    return isValid;
}

// Show field error
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    field.classList.add('error');
    field.classList.remove('success');
}

// Clear field error
function clearFieldError(fieldId) {
    const field = document.getElementById(fieldId);
    field.classList.remove('error');
    field.classList.add('success');
}

// Handle search
function handleSearch() {
    const userId = searchUserId.value.trim();
    
    if (!userId) {
        showMessage('Please enter a User ID to search', 'error');
        return;
    }
    
    const dogRecord = dogRecords.find(d => d.userId === userId);
    const dietRecord = dietRecords.find(d => d.userId === userId);
    
    if (!dogRecord && !dietRecord) {
        searchResults.innerHTML = '<div class="no-records">No records found for this User ID</div>';
        return;
    }
    
    let resultsHTML = '<h3>Search Results</h3>';
    
    if (dogRecord) {
        resultsHTML += generateDogRecordHTML(dogRecord);
    }
    
    if (dietRecord) {
        resultsHTML += generateDietRecordHTML(dietRecord);
    }
    
    searchResults.innerHTML = resultsHTML;
}

// Display all records
function displayAllRecords() {
    let html = '<h3>All Records</h3>';
    
    if (dogRecords.length === 0 && dietRecords.length === 0) {
        html += '<div class="no-records">No records found. Add some dog and diet information to get started!</div>';
    } else {
        // Group records by userId
        const userIds = [...new Set([...dogRecords.map(d => d.userId), ...dietRecords.map(d => d.userId)])];
        
        userIds.forEach(userId => {
            const dogRecord = dogRecords.find(d => d.userId === userId);
            const dietRecord = dietRecords.find(d => d.userId === userId);
            
            html += `<div class="user-records">`;
            html += `<h4>User ID: ${userId}</h4>`;
            
            if (dogRecord) {
                html += generateDogRecordHTML(dogRecord);
            }
            
            if (dietRecord) {
                html += generateDietRecordHTML(dietRecord);
            }
            
            html += '</div>';
        });
    }
    
    allRecords.innerHTML = html;
}

// Generate dog record HTML
function generateDogRecordHTML(dogRecord) {
    const breedsDisplay = dogRecord.breeds.map(breed => 
        breed.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    ).join(', ');
    
    let otherBreedsHTML = '';
    if (dogRecord.otherBreeds && dogRecord.otherBreeds.trim() !== '') {
        otherBreedsHTML = `<p><strong>Other Breeds:</strong> ${dogRecord.otherBreeds}</p>`;
    }
    
    return `
        <div class="record-card">
            <h3>🐕 Dog Information</h3>
            <div class="record-info">
                <p><strong>Name:</strong> ${dogRecord.name}</p>
                <p><strong>Age:</strong> ${dogRecord.age} years</p>
                <p><strong>Breed(s):</strong> ${breedsDisplay}</p>
                ${otherBreedsHTML}
                <p><strong>Weight:</strong> ${dogRecord.weight} lbs</p>
                <p><strong>Created:</strong> ${formatDate(dogRecord.createdAt)}</p>
                <p><strong>Updated:</strong> ${formatDate(dogRecord.updatedAt)}</p>
            </div>
            <div class="record-actions">
                <button class="btn btn-secondary" onclick="editDogRecord('${dogRecord.id}')">Edit</button>
                <button class="btn btn-danger" onclick="deleteDogRecord('${dogRecord.id}')">Delete</button>
            </div>
        </div>
    `;
}

// Generate diet record HTML
function generateDietRecordHTML(dietRecord) {
    const foodTypeDisplay = dietRecord.foodType.charAt(0).toUpperCase() + dietRecord.foodType.slice(1);
    
    return `
        <div class="record-card">
            <h3>🍽️ Diet Information</h3>
            <div class="record-info">
                <p><strong>Food Type:</strong> ${foodTypeDisplay}</p>
                <p><strong>Brand:</strong> ${dietRecord.brand}</p>
                <p><strong>Amount:</strong> ${dietRecord.amount}</p>
                <p><strong>Feeding Times:</strong> ${dietRecord.feedingTimes} times per day</p>
                <p><strong>Created:</strong> ${formatDate(dietRecord.createdAt)}</p>
                <p><strong>Updated:</strong> ${formatDate(dietRecord.updatedAt)}</p>
            </div>
            <div class="record-actions">
                <button class="btn btn-secondary" onclick="editDietRecord('${dietRecord.id}')">Edit</button>
                <button class="btn btn-danger" onclick="deleteDietRecord('${dietRecord.id}')">Delete</button>
            </div>
        </div>
    `;
}

// Edit dog record
function editDogRecord(id) {
    const dogRecord = dogRecords.find(d => d.id === id);
    if (!dogRecord) return;
    
    // Populate form with existing data
    document.getElementById('userId').value = dogRecord.userId;
    document.getElementById('dogName').value = dogRecord.name;
    document.getElementById('dogAge').value = dogRecord.age;
    document.getElementById('dogWeight').value = dogRecord.weight;
    
    // Set selected breeds
    const breedSelect = document.getElementById('dogBreed');
    Array.from(breedSelect.options).forEach(option => {
        option.selected = dogRecord.breeds.includes(option.value);
    });
    
    // Handle other breeds field
    const otherBreedsField = document.getElementById('otherBreeds');
    if (dogRecord.otherBreeds) {
        otherBreedsField.value = dogRecord.otherBreeds;
    }
    
    // Trigger breed selection handler to show/hide other breeds field
    handleBreedSelection();
    
    // Enter edit mode
    editingDogId = id;
    updateDogBtn.style.display = 'inline-block';
    deleteDogBtn.style.display = 'inline-block';
    dogForm.querySelector('button[type="submit"]').style.display = 'none';
    
    // Scroll to form
    dogForm.scrollIntoView({ behavior: 'smooth' });
    showMessage('Editing dog record. Make your changes and click Update.', 'info');
}

// Edit diet record
function editDietRecord(id) {
    const dietRecord = dietRecords.find(d => d.id === id);
    if (!dietRecord) return;
    
    // Populate form with existing data
    document.getElementById('dietUserId').value = dietRecord.userId;
    document.getElementById('brand').value = dietRecord.brand;
    document.getElementById('amount').value = dietRecord.amount;
    document.getElementById('feedingTimes').value = dietRecord.feedingTimes;
    
    // Set selected food type
    document.querySelector(`input[name="foodType"][value="${dietRecord.foodType}"]`).checked = true;
    
    // Enter edit mode
    editingDietId = id;
    updateDietBtn.style.display = 'inline-block';
    deleteDietBtn.style.display = 'inline-block';
    dietForm.querySelector('button[type="submit"]').style.display = 'none';
    
    // Scroll to form
    dietForm.scrollIntoView({ behavior: 'smooth' });
    showMessage('Editing diet record. Make your changes and click Update.', 'info');
}

// Handle dog update
function handleDogUpdate() {
    if (validateDogForm()) {
        handleDogFormSubmit(new Event('submit'));
    }
}

// Handle diet update
function handleDietUpdate() {
    if (validateDietForm()) {
        handleDietFormSubmit(new Event('submit'));
    }
}

// Handle dog delete
function handleDogDelete() {
    if (confirm('Are you sure you want to delete this dog record?')) {
        dogRecords = dogRecords.filter(d => d.id !== editingDogId);
        saveData();
        resetDogEditMode();
        clearForm('dog');
        displayAllRecords();
        showMessage('Dog record deleted successfully!', 'success');
    }
}

// Handle diet delete
function handleDietDelete() {
    if (confirm('Are you sure you want to delete this diet record?')) {
        dietRecords = dietRecords.filter(d => d.id !== editingDietId);
        saveData();
        resetDietEditMode();
        clearForm('diet');
        displayAllRecords();
        showMessage('Diet record deleted successfully!', 'success');
    }
}

// Delete dog record (called from record display)
function deleteDogRecord(id) {
    if (confirm('Are you sure you want to delete this dog record?')) {
        dogRecords = dogRecords.filter(d => d.id !== id);
        saveData();
        displayAllRecords();
        showMessage('Dog record deleted successfully!', 'success');
    }
}

// Delete diet record (called from record display)
function deleteDietRecord(id) {
    if (confirm('Are you sure you want to delete this diet record?')) {
        dietRecords = dietRecords.filter(d => d.id !== id);
        saveData();
        displayAllRecords();
        showMessage('Diet record deleted successfully!', 'success');
    }
}

// Reset dog edit mode
function resetDogEditMode() {
    editingDogId = null;
    updateDogBtn.style.display = 'none';
    deleteDogBtn.style.display = 'none';
    dogForm.querySelector('button[type="submit"]').style.display = 'inline-block';
}

// Reset diet edit mode
function resetDietEditMode() {
    editingDietId = null;
    updateDietBtn.style.display = 'none';
    deleteDietBtn.style.display = 'none';
    dietForm.querySelector('button[type="submit"]').style.display = 'inline-block';
}

// Clear form
function clearForm(formType) {
    if (formType === 'dog') {
        dogForm.reset();
        resetDogEditMode();
        clearAllFieldErrors('dog');
    } else if (formType === 'diet') {
        dietForm.reset();
        resetDietEditMode();
        clearAllFieldErrors('diet');
    }
}

// Clear all field errors
function clearAllFieldErrors(formType) {
    const form = formType === 'dog' ? dogForm : dietForm;
    const fields = form.querySelectorAll('input, select');
    fields.forEach(field => {
        field.classList.remove('error', 'success');
    });
}

// Handle clear all data
function handleClearAllData() {
    if (confirm('Are you sure you want to delete ALL data? This cannot be undone!')) {
        dogRecords = [];
        dietRecords = [];
        saveData();
        clearForm('dog');
        clearForm('diet');
        searchResults.innerHTML = '';
        displayAllRecords();
        showMessage('All data has been cleared!', 'info');
    }
}

// Generate unique ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString() + ' ' + 
           new Date(dateString).toLocaleTimeString();
}

// Show message
function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    // Insert at the top of container
    const container = document.querySelector('.container');
    container.insertBefore(messageDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Export data (bonus feature)
function exportData() {
    const data = {
        dogRecords,
        dietRecords,
        exportDate: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = 'dog_management_data.json';
    link.click();
}