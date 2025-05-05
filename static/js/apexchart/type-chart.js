

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


function column_chart_comparative(id,series){
  var options = {
    series: Object.keys(series).map(key => ({
      name: key,
      data: series[key]
    })),
    chart: {
    type: 'bar',
    height: 350
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '55%',
      borderRadius: 5,
      borderRadiusApplication: 'end'
    },
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    show: true,
    width: 2,
    colors: ['transparent']
  },
  xaxis: {
    categories: ['En','Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct','Nov','Dic'],
  },
  yaxis: {
    title: {
      text: 'Ventas totales'
    }
  },
  fill: {
    opacity: 1
  },
  tooltip: {
    y: {
      formatter: function (val) {
        return  val 
      }
    }
  }
  };

  var chart = new ApexCharts(document.querySelector('#'+id), options);
  chart.render();

}


function column_chart_basic(id, data, meses) {
  // Filtrar los datos válidos (que no sean NaN ni null)
  const validData = data
    .map((value, index) => ({ value, mes: meses[index] }))
    .filter(item => !isNaN(item.value) && item.value !== null);

  const filteredValues = validData.map(item => item.value);
  const filteredMeses = validData.map(item => item.mes);

  var options = {
    series: [{
      name: 'Total',
      data: filteredValues
    }],
    chart: {
      height: 350,
      type: 'bar',
    },
    colors: ['#007D9D'],
    plotOptions: {
      bar: {
        borderRadius: 10,
        dataLabels: {
          position: 'top',
        },
      }
    },
    dataLabels: {
      enabled: true,
      offsetY: -20,
      style: {
        fontSize: '12px',
        colors: ["#859222"]
      }
    },
    xaxis: {
      categories: filteredMeses,
      position: 'bottom',
      offsetY: -8,
      axisBorder: {
        show: false
      },
      axisTicks: {
        show: false
      },
      crosshairs: {
        fill: {
          type: 'gradient',
          gradient: {
            colorFrom: '#D8E3F0',
            colorTo: '#BED1E6',
            stops: [0, 100],
            opacityFrom: 0.4,
            opacityTo: 0.5,
          }
        }
      },
      tooltip: {
        enabled: true,
      }
    },
    yaxis: {
      axisBorder: {
        show: false
      },
      axisTicks: {
        show: false,
      },
      labels: {
        show: false,
        formatter: function (val) {
          return val + "%";
        }
      }
    },
  };

  var chart = new ApexCharts(document.querySelector("#" + id), options);
  chart.render();
}

