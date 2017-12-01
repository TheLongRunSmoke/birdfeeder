document.addEventListener('DOMContentLoaded', function() {
   fitToContainer(document.querySelector('canvas'))
   requestData();
}, false);

function fitToContainer(canvas){
  canvas.style.width ='100%';
  canvas.style.height='400px';
  canvas.width  = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
}

function requestData() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "http://192.168.1.120:5000/api/v1.0/temp?seconds=43200", true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.setRequestHeader("Authorization", "Basic d2ViOjVdQDI7NVptRD85ZjcxbTouWCx1N3ozQkphZ3Y+YA==");
    xhttp.onreadystatechange = function () {
    if (xhttp.readyState == 4) {
      if (xhttp.status == 200) {
          drawChart(JSON.parse(xhttp.responseText));
      }
    }
  };
  xhttp.send();
}

function drawChart(data){
    var ctx = document.getElementById("chart");
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data[0].map(function(d){
                return new Date(d*1000).format('d M H:i');
            }),
            datasets: [
            {
                label: 'Воздуха',
                data: data[1].map(function(d){
                    return Number(parseFloat(d).toFixed(2));
                }),
                backgroundColor: 'rgb(54, 162, 235)',
                borderColor: 'rgb(54, 162, 235)',
                fill: false
            },
            {
                label: 'Внутри корпуса',
                data: data[2].map(function(d){
                    return Number(parseFloat(d).toFixed(2));
                }),
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                fill: false
            },
            {
                label: 'Процессор',
                data: data[3].map(function(d){
                    return Number(parseFloat(d).toFixed(2));
                }),
                backgroundColor: 'rgb(75, 192, 192)',
                borderColor: 'rgb(75, 192, 192)',
                fill: false
            },
            ]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero:false
                    }
                }]
            }
        }
    });
}
