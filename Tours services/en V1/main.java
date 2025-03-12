// Add event listeners to buttons
document.getElementById('homeBtn').addEventListener('click', function() {
    alert('Welcome to the Home Page!');
});

document.getElementById('shuttlesBtn').addEventListener('click', function() {
    alert('Shuttle Services Selected!');
});

document.getElementById('toursBtn').addEventListener('click', function() {
    alert('Tours Selected!');
});

// Optional: Add click functionality to service bubbles
document.querySelectorAll('.service-bubble').forEach(bubble => {
    bubble.addEventListener('click', function() {
        const service = this.getAttribute('data-service');
        alert(`You clicked on ${service} service.`);
    });
});