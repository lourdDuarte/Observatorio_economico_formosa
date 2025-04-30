

function area_chart(id, intermensual_data, interanual_data,meses, titulo_chart, max_chart, min_chart)
{
   
  var options = {
    series: [
    {
      name: "Intermensual",
      data:  intermensual_data
    },
    {
      name: "Interanual",
      data: interanual_data
    }
  ],
    chart: {
    height: 350,
    type: 'line',
    dropShadow: {
      enabled: true,
      color: '#000',
      top: 18,
      left: 7,
      blur: 10,
      opacity: 0.5
    },
    zoom: {
      enabled: true
    },
    toolbar: {
      show: true
    }
  },
  colors: ['#007D9D', '#859222'],

  dataLabels: {
    enabled: true,
  },
  stroke: {
    curve: 'smooth'
  },
  title: {
    text: titulo_chart,
    align: 'left'
  },
  grid: {
    borderColor: '#e7e7e7',
    row: {
      colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
      opacity: 0.5
    },
  },
  markers: {
    size: 1
  },
  xaxis: {
    categories: meses,
    title: {
      text: 'Meses'
    }
  },
  yaxis: {
    
    min: min_chart,
    max: max_chart
  },
  legend: {
    position: 'top',
    horizontalAlign: 'right',
    floating: true,
    offsetY: -25,
    offsetX: -5
  },
  annotations: {
    yaxis: [{
      y: 0,
      borderColor: '#000000',  // Color de la línea
      strokeDashArray: 0,       // Línea punteada
      
    }]
  }
  };

  var chart = new ApexCharts(document.querySelector('#'+id), options);
  chart.render();
}

