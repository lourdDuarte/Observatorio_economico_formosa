function chart_dynamic_column_chart_comparative(json){
    

  // Inicial: ramas totales
  const ramas = Object.keys(json);
  const totales = ramas.map(rama => {
    let total = 0;
    Object.values(chartData[rama]).forEach(trimestres => {
      total += Object.values(trimestres).reduce((a, b) => a + b, 0);
    });
    return total;
  });

  const options = {
    chart: {
      type: 'bar',
      height: 400,
      events: {
        dataPointSelection: function(event, chartContext, config) {
          const selectedRama = ramas[config.dataPointIndex];
          showRamaDetalle(selectedRama);
        }
      }
    },
    plotOptions: {
        bar: {
            horizontal: true,
            
        }
    },
    series: [{
      name: 'Cantidad total',
      data: totales
    }],
    xaxis: {
      categories: ramas
    },
    title: {
      text: 'Cantidad total por rama'
    }
  };

  const chart = new ApexCharts(document.querySelector("#chart-ramas"), options);
  chart.render();

  function showRamaDetalle(rama) {
    const dataRama = chartData[rama];
    const trimestres = new Set();
    const series = [];

    for (const anio in dataRama) {
      const trimestreData = dataRama[anio];
      series.push({
        name: anio,
        data: []
      });

      for (const trimestre in trimestreData) {
        trimestres.add(trimestre);
      }
    }

    const ordenTrimestres = ['Primer trimestre', 'Segundo trimestre', 'Tercer trimestre', 'Cuarto trimestre'];
    const xaxisCats = Array.from(trimestres).sort(
      (a, b) => ordenTrimestres.indexOf(a) - ordenTrimestres.indexOf(b)
    );

    series.forEach(serie => {
      const anio = serie.name;
      serie.data = xaxisCats.map(tri => dataRama[anio][tri] || 0);
    });

    chart.updateOptions({
      series: series,
      plotOptions: {
        bar: {
            horizontal: false
        }
    },
      xaxis: {
        categories: xaxisCats
      },
      title: {
        text: `Detalle por trimestre de: ${rama}`
      }
    });
    // Mostrar el botón de volver
    document.getElementById('backButton').style.display = 'block';

  }
}