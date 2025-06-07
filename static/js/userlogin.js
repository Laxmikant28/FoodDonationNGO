document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting normally

    // Simulate a successful login process
    alert('Login successful!');

    // Optionally, redirect to another page after the alert
    // window.location.href = 'dashboard.html'; // Uncomment and set your target page
});
