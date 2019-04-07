function checkPassword(e) {
    var elMsg = document.getElementById('feedback');
    if (this.value.length < 5) {
        elMsg.textContent = 'Password must be at least 5 characters or more!';
    }   else if (this.value.length > 20) {
        elMsg.textContent = 'Password must be less than least 20 characters!';
    }   else if (this.value.search(/\d/) == -1) {
        elMsg.textContent = 'Password must contain at least one number!';
    }   else {
        elMsg.textContent = '';
    }
}

var elUsername = document.getElementById('password');
elUsername.addEventListener('blur', checkPassword, false)