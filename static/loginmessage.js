(function(){
    var form = document.getElementById("login");

    addEvent(form, 'submit', function(e){
        var elements = this.elements;
        var username = elements.username.value;
        alert(`Good to see you again ${username} hope you're enjoying the story`)
    });
}());