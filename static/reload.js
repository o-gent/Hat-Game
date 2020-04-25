var reload = setInterval(runMe, 3000);

/* 
* Reloads the page if there as been an update
*/
export function runMe()
{
    URL = "/refresh";
    content = {
        id:'room_id..'
    };

    const xhr = new XMLHttpRequest();
    xhr.open('POST', URL);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(content));
    xhr.onload()
    {
        console.log(xhr.responseText)
        // if 1, reload page
        if (xhr.responseText == 1)
        {
            location.reload()
        }
    }
}