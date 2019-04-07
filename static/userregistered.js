// A basic on event function edited to use an ajax request to check if the username is already taken

function userRegistered(){
    console.log('is this thing on?');
    // A new AJAX object
    const ajax = new XMLHttpRequest();
    // The target of the event listener passed in to the function as e
    const username = document.querySelector('#username').value;
    console.log(username);

    // Sends the ajax POST request to the server to run the function at /votecheck
    ajax.open('POST', '/regcheck', true);

    // When the request is complete, and ajax returns, run this function
    ajax.onload = function () {
        console.log('returned ajax')
        // Pasrses the JSON file and extracts the text from the response
        const registered = JSON.parse(ajax.responseText);
        console.log(registered);
        // If the user has not voted
        if (registered.success == false) {
            alert(`Unfortunately this username is already taken`);
            return false;
        }
    }

    const data = new FormData();
    data.append('username', username)

    ajax.send(data);
    console.log('ajax sent?');
    return false;
}

var elUsername = document.getElementById('username');
elUsername.addEventListener('blur', userRegistered, false)
