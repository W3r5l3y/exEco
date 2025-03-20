
/* ---------
    CSRF Token
--------- */
function getCSRFToken() {
    const cookieValue = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
    return cookieValue || "";
}

document.addEventListener('DOMContentLoaded', function() {

    /* ---------
        Character counter
    --------- */
    const messageTextArea = document.getElementById('message');
    const charCountDisplay = document.getElementById('charCount');

    messageTextArea.addEventListener('input', function() {
        const currentLength = messageTextArea.value.length;
        charCountDisplay.textContent = `${currentLength} / 500`;
    });


    /* ---------
        Form submission
    --------- */
    const form = document.querySelector('form');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const message = document.getElementById('message').value;
        const url = '/submit/';

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Your message has been sent!');
                document.getElementById('message').value = '';
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });
});