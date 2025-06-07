// document.addEventListener("DOMContentLoaded", function() {
//     const donateButton = document.getElementById("donateButton");
    
//     donateButton.addEventListener("click", function() {
//         window.location.href = "login.html"; // Replace with your login page URL
//     });

//     const hamburger = document.querySelector(".hamburger");
//     hamburger.onclick = function() {
//         const navBar = document.querySelector(".nav-bar");
//         navBar.classList.toggle("active");
//     };
// });
// Handle Donate Food Button Click
document.addEventListener('DOMContentLoaded', function () {
    const donateButton = document.getElementById('donateButton');
    if (donateButton) {
        donateButton.addEventListener('click', function () {
            // Redirect to the donation page
            window.location.href = 'userlogin.html';
        });
    }
});

// Handle Form Submission on Sign Up Page
document.addEventListener('DOMContentLoaded', function () {
    const signupForm = document.querySelector('form[action="SignupServlet"]');
    if (signupForm) {
        signupForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent default form submission

            // Get form data
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // Perform validation or other operations
            if (email && password) {
                // For example, you can send the form data via fetch to your server
                fetch('SignupServlet', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({
                        email: email,
                        password: password
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Sign Up Successful!');
                        window.location.href = 'login.html'; // Redirect to login page
                    } else {
                        alert('Sign Up Failed: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            } else {
                alert('Please fill in all fields.');
            }
        });
    }
});
