function apiReportVisit(counter_host, origin, pathname, referer, client_id) {
    return fetch(`${counter_host}/api/counter`, {
        method: 'post',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
            origin: origin,
            referer: referer,
            path: pathname,
            client_id: client_id,
        })
    }).then((r) => { return r.json() });
}



function collectStatistic(){
    console.log("Starting collect statics")
    let counter_host = new URL(document.getElementById('counter_scripts').src);
    let client_id = 0x10000000000 + Math.floor(Math.random() * 0xF0000000000);
    if (localStorage.client_id)
        client_id = localStorage.client_id;
    else
        localStorage.client_id = client_id;
    apiReportVisit(counter_host.origin, window.location.host, window.location.pathname, document.referrer, client_id);
}

document.addEventListener("DOMContentLoaded", collectStatistic);