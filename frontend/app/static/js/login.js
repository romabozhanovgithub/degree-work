document.getElementById('submit').addEventListener('click', async function(e) {
    e.preventDefault();
    let loginForm = document.getElementById('login-form');
    let username = document.getElementById('email').value;
    let password = document.getElementById('password').value;
    let errorElement = document.getElementById('error');
    errorElement.style.display = "none";

    if (!username || !password) {
        errorElement.style.display = "block";
        errorElement.textContent = "Please fill in all fields";
        return;
    } else {
        let formData = new URLSearchParams(new FormData(loginForm));
        await fetch(
            'http://localhost:5000/auth/login',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            }
        ).then(response => response.json())
        .then(data => {
            if (!data.access_token) {
                console.log(data.detail);
                errorElement.style.display = "block";
                errorElement.textContent = data.detail;
                return;
            }
            localStorage.setItem("accessToken", data.access_token);
            window.location.href = indexLink;
        }).catch(
            error => {
                errorElement.style.display = "block";
                errorElement.textContent = error.message;
                return null;
            }
        )
    };
});
