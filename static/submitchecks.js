function manage(e){
    var submit = document.getElementById('submit');
    var elements = document.getElementsByTagName('input');

    console.log(submit);

    for (i = 0; i < elements.length; i++) {                                              // Loops through the elements recorded in elements

        console.log(elements[i].type);

        if (elements[i].type == ('text' || 'password') && elements[i].value == '') {  // Checks the elements to see if they are text or password
            submit.disabled = true;                                                 // Disables the submit button
            return false;
        }
        else {
            submit.disabled = false;                                                    // Enables the button when all boxes have content
        }

        console.log(submit.disabled);
    }
}

// Adds an event listener to each of the buttons
var eventAddition = document.getElementsByTagName('input');
for (i = 0; i < eventAddition.length; i++) {
    eventAddition[i].addEventListener('blur', manage, false);
}