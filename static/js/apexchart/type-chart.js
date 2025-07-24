

function column_chart_comparative(id,series, titulo){
  var options = {
    series: Object.keys(series).map(key => ({
      name: key,
      data: series[key]
    })),
    chart: {
    type: 'bar',
    height: 350,
    
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
      text: titulo
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




function area_chart_variation(id, diccionario_variacion, titulo_chart,  serie_puntos_data = null, nombre_puntos = "Tercera Serie") {

  const meses = diccionario_variacion['meses'];

  let series = [];
  let colors = ['#003764', '#859222', '#0fa89cff', '#f57404ff'];
  let widths = [];
  let marker_sizes = [];
  let dashArray = [];

  let todos_los_valores = [];

  for (const [clave, valores] of Object.entries(diccionario_variacion)) {
    if (clave === 'meses') continue;

    const valores_numericos = valores.map(parseFloat);
    series.push({
      name: clave,
      data: valores_numericos,
      hidden: clave.includes("Nacional") // <-- Oculta series que contienen "Nacional"
    });

    todos_los_valores = todos_los_valores.concat(valores_numericos);
    widths.push(2);
    marker_sizes.push(5);
    dashArray.push(0);
  }

  // Serie opcional punteada
  if (serie_puntos_data && Array.isArray(serie_puntos_data) && serie_puntos_data.length > 0) {
    const valores_numericos = serie_puntos_data.map(parseFloat);
    series.push({
      name: nombre_puntos,
      data: valores_numericos,
    });
    colors.push('#F5B041');
    widths.push(2);
    marker_sizes.push(6);
    dashArray.push(8);
    todos_los_valores = todos_los_valores.concat(valores_numericos);
  }

  
    const min = Math.min(...todos_los_valores);
    const max = Math.max(...todos_los_valores);
    const margen = (max - min) * 0.1;
    min_chart = Math.floor(min - margen);
    max_chart = Math.ceil(max + margen);
  

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

