document.getElementById('signupForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting normally

    // Simulate a successful signup process
    alert('Signup successful!');

    // Optionally, redirect to another page after the alert
    window.location.href = 'userlogin.html';
});