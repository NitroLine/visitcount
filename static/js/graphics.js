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
        showErrorAt("Fill all form field")
        return;
    }
    console.log(form.origin.value, form.start_date.value, form.end_date.value);
    let start_date = new Date(form.start_date.value);
    let end_date = new Date(form.end_date.value);
    let origin = form.origin.value;
    if (start_date > end_date)
    {
       showErrorAt("End date must be greater then end date")
       return;
    }
    let dates = [];
    let language_stats = {};
    let platform_stats = {};
    let total_clients_series = [];
    let total_visits_series = [];
    $("#loader").removeClass("is-hidden");
    while (start_date <= end_date){
        let data = await apiRequestDataOnDate(origin, start_date.toISOString().split('T')[0])
        console.log(data)
        dates.push(start_date.toISOString().split('T')[0])
        total_clients_series.push(data.total_clients)
        total_visits_series.push(data.total_visits)
        for (let lang in data.language_stats){
            if (!language_stats[lang])
                language_stats[lang] = 0;
            language_stats[lang] +=1;
        }
        for (let platform in data.platform_stats){
            if (!platform_stats[platform])
                platform_stats[platform] = 0;
            platform_stats[platform] +=1;
        }
        start_date =  start_date.addDays(1);
    }
    console.log(platform_stats)
    console.log(language_stats)
    $("#loader").addClass("is-hidden");
    buildGraphic('#visits_chart',dates, total_visits_series);
    buildGraphic('#visitors_chart',dates, total_clients_series);
    buildCircleGraphic('#platforms_chart', platform_stats);
    buildCircleGraphic('#language_chart', language_stats);
    // apiRequestData(form.origin.value, form.start_date.value, form.end_date.value)
}

let errorPlace = $('#error_place');
function showErrorAt(error, obj=errorPlace){
    console.error(error);
    obj.find('.error').remove();
    obj.append($(`<p class="error has-text-danger has-background-danger-light">Error: ${error}</p>`));
}

function buildGraphic(id, dates, series){
    var data = {
      labels: dates,
      lineSmooth: false,
      axisY: {
        type: Chartist.FixedScaleAxis,
        onlyInteger: true
      },
      series: [
        series
      ],
      fullWidth: true,
    };
    new Chartist.Line(id, data);
}

function buildCircleGraphic(id, data_obj){
    let labels = [];
    let series = [];
    for (key in data_obj) {
      labels.push(key);
      series.push(data_obj[key]);
    }
    var data = {
      labels: labels,
      series: series
    };
    new Chartist.Pie(id, data, {
      donut: true,
      donutWidth: 60,
      donutSolid: true,
      startAngle: 270,
      showLabel: true
    });
}

document.addEventListener("DOMContentLoaded", getOrigins);