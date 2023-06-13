window.addEventListener('load', async function () {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const token = urlParams.get('token');
    const errorElement = document.getElementById('message');

    try {
        let response = await fetch(
            `http://localhost:5000/auth/verify-email?token=${token}`,
            {
                method: 'GET',
            }
        );

        let data = await response.json();

        if (!response.ok) {
            showError(errorElement, data.detail);
            return;
        }

        // Display a success message
        errorElement.textContent = "Your email has been successfully verified! You can now log in.";
        errorElement.style.color = "#00FF00";
    } catch (err) {
        showError(errorElement, err.message);
    }
});

function showError(errorElement, message) {
    errorElement.textContent = message;
    errorElement.style.color = "#FF0000";
}

