function checkUserName(e) {
    var elMsg = document.getElementById('feedback');
    if (this.value.length < 5) {
        elMsg.textContent = 'Username must be at least 5 characters or more!';
    }   else {
        elMsg.textContent = '';
    }
}

var elUsername = document.getElementById('username');
elUsername.addEventListener('blur', checkUserName, false)