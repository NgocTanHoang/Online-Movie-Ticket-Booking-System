
// Constants
const ROWS = 10; // Number of rows
const COLS = 10; // Number of columns
const TICKET_PRICE = 110; // Price per ticket in Rs.
const MAX_SEATS = 10; // Maximum seats a user can select

// Map row numbers to letters (1 → A, 2 → B, ..., 26 → Z)
const rowLabels = Array.from({ length: 26 }, (_, i) => String.fromCharCode(65 + i)); // A-Z

// DOM Elements
const seatGrid = document.getElementById('seat-grid');
const selectedSeatsContainer = document.getElementById('selected-seats');
const ticketCountElement = document.getElementById('ticket-count');
const totalCostElement = document.getElementById('total-cost');
const confirmBtn = document.getElementById('confirm-btn');

// State
let selectedSeats = [
    { row: 5, col: 1 }, // Row 5 is 'E' (E1)
    { row: 5, col: 2 }  // Row 5 is 'E' (E2)
];

// Function to convert row number to letter
function rowNumberToLetter(row) {
    return rowLabels[row - 1]; // 1 → A, 2 → B, etc.
}

// Function to generate the seat grid dynamically
function generateSeatGrid() {
    // Clear the grid
    seatGrid.innerHTML = '';

    // Generate seats for each row (no top row of labels)
    for (let row = 1; row <= ROWS; row++) {
        // Add row label for the row (first column)
        const rowLabel = document.createElement('div');
        rowLabel.classList.add('seat-row-label');
        rowLabel.textContent = rowNumberToLetter(row); // A, B, C, ...
        seatGrid.appendChild(rowLabel);

        // Add seats for the row
        for (let col = 1; col <= COLS; col++) {
            const seat = document.createElement('div');
            seat.classList.add('seat');
            seat.dataset.row = row;
            seat.dataset.col = col;
            seat.textContent = `${rowNumberToLetter(row)}${col}`; // e.g., A1, B2, etc.

            // Set initial state of the seat
            if (row === 1 && (col === 2)) { // A2
                seat.classList.add('sold');
            } else if (row === 4 && (col === 4 || col === 5)) { // D4, D5
                seat.classList.add('sold');
            } else if (row === 6 && (col === 6 || col === 7)) { // F6, F7
                seat.classList.add('sold');
            } else if (row === 8 && (col === 5 || col === 6 || col === 7 || col === 8)) { // H5, H6, H7, H8
                seat.classList.add('sold');
            } else if (row === 10 && (col === 1 || col === 2)) { // J1, J2
                seat.classList.add('sold');
            } else if (selectedSeats.some(s => s.row === row && s.col === col)) {
                seat.classList.add('selected'); // Pre-selected seats
            } else {
                seat.classList.add('available');
            }

            // Add click event listener for seat selection
            seat.addEventListener('click', () => toggleSeat(seat));
            seatGrid.appendChild(seat);
        }
    }
}

// Function to update the summary
function updateSummary() {
    // Update selected seats display
    selectedSeatsContainer.innerHTML = selectedSeats.map(seat =>
        `<span>${rowNumberToLetter(seat.row)}${seat.col}</span>`
    ).join('');

    // Update ticket count
    const ticketCount = selectedSeats.length;
    ticketCountElement.textContent = `Tickets: ${ticketCount}`;

    // Update total cost
    const totalCost = ticketCount * TICKET_PRICE;
    totalCostElement.textContent = `Total: Rs.${totalCost}`;

    // Enable/disable confirm button
    confirmBtn.disabled = ticketCount === 0;
}

// Function to toggle seat selection
function toggleSeat(seat) {
    const row = parseInt(seat.dataset.row);
    const col = parseInt(seat.dataset.col);

    // If seat is sold, do nothing
    if (seat.classList.contains('sold')) {
        return;
    }

    // Check if seat is already selected
    const seatIndex = selectedSeats.findIndex(s => s.row === row && s.col === col);

    if (seatIndex !== -1) {
        // Deselect the seat
        selectedSeats.splice(seatIndex, 1);
        seat.classList.remove('selected');
        seat.classList.add('available');
    } else {
        // Check if maximum seats limit is reached
        if (selectedSeats.length >= MAX_SEATS) {
            alert(`You can only select up to ${MAX_SEATS} seats.`);
            return;
        }

        // Select the seat
        selectedSeats.push({ row, col });
        seat.classList.remove('available');
        seat.classList.add('selected');
    }

    updateSummary();
}

// Function to confirm booking (mark selected seats as sold)
function confirmBooking() {
    if (selectedSeats.length === 0) {
        alert('Please select at least one seat to confirm your booking.');
        return;
    }

    // Mark all selected seats as sold
    const seats = document.querySelectorAll('.seat');
    seats.forEach(seat => {
        const row = parseInt(seat.dataset.row);
        const col = parseInt(seat.dataset.col);

        if (selectedSeats.some(s => s.row === row && s.col === col)) {
            seat.classList.remove('selected');
            seat.classList.add('sold');
        }
    });

    // Clear selected seats
    selectedSeats = [];
    updateSummary();

    alert('Booking confirmed! Your seats are now reserved.');
}

// Add click event listener to confirm button
confirmBtn.addEventListener('click', confirmBooking);

// Generate the seat grid and update summary on page load
document.addEventListener('DOMContentLoaded', () => {
    generateSeatGrid();
    updateSummary();
});
