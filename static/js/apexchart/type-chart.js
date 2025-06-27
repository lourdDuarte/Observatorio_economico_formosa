function area_chart(id, intermensual_data, interanual_data, meses, titulo_chart, max_chart, min_chart, serie_puntos_data = null, nombre_puntos = "Tercera Serie") {
  
  let series = [
    {
      name: "Intermensual",
      data: intermensual_data
    },
    {
      name: "Interanual",
      data: interanual_data
    }
  ];

  let colors = ['#003764', '#859222'];
  let widths = [2, 2];
  let marker_sizes = [5, 5];
  let dashArray = [0, 0]; // 0 = línea sólida

  if (serie_puntos_data && Array.isArray(serie_puntos_data) && serie_puntos_data.length > 0) {
    series.push({
      name: nombre_puntos,
      data: serie_puntos_data
    });
    colors.push('#F5B041');        // color para la serie punteada
    widths.push(2);                // grosor de línea
    marker_sizes.push(6);          // tamaño de puntos
    dashArray.push(8);             // 8 = línea punteada
  }

  var options = {
    series: series,
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
      zoom: { enabled: true },
      toolbar: { show: true }
    },
    colors: colors,
    dataLabels: { enabled: false },
    stroke: {
      curve: 'straight',
      width: widths,
      dashArray: dashArray
    },
    markers: {
      size: marker_sizes,
      colors: colors,
      strokeColors: '#fff',
      strokeWidth: 2,
      hover: { sizeOffset: 2 }
    },
    title: {
      text: titulo_chart,
      align: 'left'
    },
    grid: {
      show: true,
      borderColor: '#e7e7e7',
      strokeDashArray: 0,
      position: 'back',
      row: {
        colors: ['#f3f3f3', 'transparent'],
        opacity: 0.5
      },
      xaxis: { lines: { show: false } },
      yaxis: { lines: { show: true, colors: ['#e7e7e7'] } }
    },
    xaxis: {
      categories: meses,
      title: { text: 'Meses' },
      tooltip: {
        enabled: true,
        formatter: function (val, { series, seriesIndex, dataPointIndex, w }) {
          return w.globals.categoryLabels[dataPointIndex];
        }
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
        borderColor: '#000000',
        strokeDashArray: 0
      }]
    },
    tooltip: {
      enabled: true,
      x: {
        show: true,
        formatter: function(val, { series, seriesIndex, dataPointIndex, w }) {
          return w.globals.categoryLabels[dataPointIndex];
        }
      },
      y: {
        formatter: function (val) {
          return typeof val === 'number' ? val.toFixed(1) + '%' : val;
        },
        title: {
          formatter: function (seriesName) {
            return seriesName;
          }
        }
      }
    }
  };

  var chart = new ApexCharts(document.querySelector('#' + id), options);
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
    colors: ['#003764'],
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

