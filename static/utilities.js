function addEvent(el, event, callback) {
    if ('addEventListener' in el) {                              // If addEventListener works
        el.addEventListener(event, callback, false);            // Use it
    } else {                                                    // Otherwise
        el['e' + event + callback] = callback;                  // Make callback a method of el
        el[event + callback] = function() {                     // Add second method
            el['e' + event + callback](window.event);           // Use it to call the previous function
        };
        el.attachEvent('on' + event, el[event + callback]);     // Use attachEvent() to call the second fucntion, which then calls the first one
    }
}

// This script adds an event handler and has been designed to be reused.