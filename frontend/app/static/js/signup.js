document.getElementById('submit').addEventListener('click', async function(e) {
    e.preventDefault();
    // Here you would add your signup logic
    let firstName = document.getElementById('firstName').value;
    let lastName = document.getElementById('lastName').value;
    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;
    let confirmPassword = document.getElementById('confirm-password').value;
    let errorElement = document.getElementById('error');

    if (password !== confirmPassword) {
        errorElement.style.display = "block";
        errorElement.textContent = "Passwords do not match";
        return;
    } else if (!firstName || !lastName || !email || !password || !confirmPassword) {
        errorElement.style.display = "block";
        errorElement.textContent = "Please fill in all fields";
        return;
    } else {
        error.textContent = "";
        errorElement.style.display = "none";
        await fetch(
            'http://localhost:5000/auth/sign-up',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    firstName,
                    lastName,
                    email,
                    password
                })
            }
        ).then(response => response.json()).then(
            data => {
                if (!data.isActive) {
                    errorElement.style.display = "block";
                    errorElement.textContent = data.detail;
                    console.log(data.detail);
                    return;
                }
                window.location.href = signupSuccessLink;
            }
        ).catch(
            error => {
                errorElement.style.display = "block";
                errorElement.textContent = error.message;
                return;
            }
        );
    }
});
