function apiGetCountedOrigins() {
    return fetch(`/origins/`, {
        method: 'get',
    }).then((r) => { return r.json() });
}

function apiRequestDataOnDate(origin, date) {
    return fetch(`/stats/${origin}/${date}`, {
        method: 'get',
    }).then((r) => { return r.json() });
}

function apiRequestData(origin, start_date, end_date) {
    return fetch(`/stats/${origin}/`, {
        method: 'post',
        headers: { 'content-type': 'application/json'},
        body: JSON.stringify({
            start_date: start_date,
            end_date: end_date,
        })
    }).then((r) => { return r.json() });
}

Date.prototype.addDays = function(days) {
    var date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
}

function getOrigins(){
    apiGetCountedOrigins().then((origins)=>{
        origins.forEach((origin)=>{
        $('#queryOrigin').append($(`<option value="${origin}">${origin}</option>`));
        });
    });
}

async function getDataAndBuildGraphics(){
    let form = $('#param_form').get()[0]
    if (form.origin.value == 'None' || form.start_date.value.length == 0 || form.end_date.value == 0 ) {
        console.log("Incorrect data");
        return;
    }
    console.log(form.origin.value, form.start_date.value, form.end_date.value);
    let start_date = new Date(form.start_date.value);
    let end_date = new Date(form.end_date.value);
    let origin = form.origin.value;
    if (start_date > end_date)
    {
       console.log("Incorrect data");
       return;
    }
    let dates = [];
    let total_clients_series = [];
    let total_visits_series = [];
    while (start_date <= end_date){
        let data = await apiRequestDataOnDate(origin, start_date.toISOString().split('T')[0])
        console.log(data)
        dates.push(start_date.toISOString().split('T')[0])
        total_clients_series.push(data.total_clients)
        total_visits_series.push(data.total_visits)
        start_date =  start_date.addDays(1);
    }
    buildGraphic(dates, total_visits_series);
    // apiRequestData(form.origin.value, form.start_date.value, form.end_date.value)
}

function buildGraphic(dates, series){
var data = {
  // A labels array that can contain any sort of values
  labels: dates,
  // Our series array that contains series objects or in this case series data arrays
  series: [
    series
  ]
};

// Create a new line chart object where as first parameter we pass in a selector
// that is resolving to our chart container element. The Second parameter
// is the actual data object.
new Chartist.Line('.ct-chart', data);
}

document.addEventListener("DOMContentLoaded", getOrigins);