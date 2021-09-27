function apiReportVisit(counter_host, origin, pathname, referer) {
    return fetch(`${counter_host}/api/counter`, {
        method: 'post',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
            origin: origin,
            referer: referer,
            pathname: pathname
        })
    }).then((r) => { return r.json() });
}

function collectStatistic(){
    console.log("Starting collect statics")
    let counter_host = new URL(document.getElementById('counter_scripts').src);
    apiReportVisit(counter_host.origin, window.location.host, window.location.pathname,document.referrer);
}

document.addEventListener("DOMContentLoaded", collectStatistic);