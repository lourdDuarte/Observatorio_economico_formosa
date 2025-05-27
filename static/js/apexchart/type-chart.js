

function area_chart(id, intermensual_data, interanual_data,meses, titulo_chart, max_chart, min_chart)
{
   
 var options = {
  series: [
    {
      name: "Intermensual",
      data: intermensual_data
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
  colors: ['#003764', '#859222'], // Tus colores actuales

  dataLabels: {
    enabled: false, // Deshabilitado como lo pediste
  },
  stroke: {
    curve: 'smooth', // Hace que la línea sea suave, como en la imagen
    width: 2,
  },
  title: {
    text: titulo_chart,
    align: 'left'
  },
  grid: {
    show: true,
    borderColor: '#e7e7e7', // Color de borde para la rejilla
    strokeDashArray: 0, // No usar líneas punteadas para la rejilla
    position: 'back', // La rejilla detrás de las líneas del gráfico
    row: {
      colors: ['#f3f3f3', 'transparent'], // Toma un array que se repetirá en las filas
      opacity: 0.5
    },
    xaxis: {
      lines: {
        show: false // Ocultar las líneas verticales de la rejilla
      }
    },
    yaxis: {
        lines: {
            show: true,
            colors: ['#e7e7e7'] // Color muy claro para las líneas horizontales
        }
    }
  },
  markers: {
    size: 5,        // Tamaño de los círculos en los puntos de datos (estos son los "puntos" que quieres ver)
    colors: ['#007D9D', '#859222'], // Colores que coinciden con tus series
    strokeColors: '#fff', // Color del borde de los marcadores (blanco para que resalten)
    strokeWidth: 2,       // Ancho del borde de los marcadores
    hover: {
      sizeOffset: 2 // Los marcadores pueden crecer un poco al pasar el ratón
    }
  },
  xaxis: {
    categories: meses, // Tus categorías de meses
    title: {
      text: 'Meses'
    },
    tooltip: {
      enabled: true, // Habilita el tooltip en el eje X
      formatter: function (val, { series, seriesIndex, dataPointIndex, w }) {
        // Asegúrate de que el valor sea el nombre del mes de tus categorías
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
      borderColor: '#000000', // Color de la línea
      strokeDashArray: 0, // Línea sólida (0 para no punteada)
    }]
  },
  tooltip: {
    enabled: true, // Habilitar el tooltip en general
    x: {
      show: true,
      formatter: function(val, { series, seriesIndex, dataPointIndex, w }) {
        // Muestra el nombre del mes de las categorías en la parte superior del tooltip
        return w.globals.categoryLabels[dataPointIndex];
      }
    },
    y: {
      formatter: function (val) {
        // Muestra el valor como un porcentaje en el tooltip
        if (typeof val === 'number') {
            return val.toFixed(1) + '%'; // Formatea a un decimal y añade '%'
        }
        return val;
      },
      title: {
          formatter: function (seriesName) {
              return seriesName; // Muestra el nombre de la serie (ej. "Intermensual")
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

