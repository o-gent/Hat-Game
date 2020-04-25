var reload = setInterval(runMe, 3000);

/* 
* Reloads the page if there as been an update
*/
function runMe()
{
    URL = "/refresh";

    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() { 
        // if 1, reload page
        if (xhr.responseText == "1")
        {
            location.reload()
        }
    }
    xhr.open('GET', URL);
    xhr.send( null );
}