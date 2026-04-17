function chart_dynamic_column_chart_comparative(json, containerId, opciones) {
  containerId = containerId || 'chart-ramas';
  opciones = opciones || {};

  var tituloInicial      = opciones.tituloInicial      || 'Cantidad total';
  var ordenSubcategorias = opciones.ordenSubcategorias || null;
  var backButtonId       = opciones.backButtonId       || null;

  var categorias = Object.keys(json);
  var totales = categorias.map(function(cat) {
    var total = 0;
    Object.values(json[cat]).forEach(function(subcats) {
      total += Object.values(subcats).reduce(function(a, b) { return a + b; }, 0);
    });
    return total;
  });

  // Ordenar de mayor a menor por total
  var indices = categorias.map(function(_, i) { return i; });
  indices.sort(function(a, b) { return totales[b] - totales[a]; });
  categorias = indices.map(function(i) { return categorias[i]; });
  totales    = indices.map(function(i) { return totales[i]; });

  var options = {
    chart: {
      type: 'bar',
      height: 400,
      events: {
        dataPointSelection: function(event, chartContext, config) {
          mostrarDetalle(categorias[config.dataPointIndex]);
        }
      }
    },
    plotOptions: { bar: { horizontal: true } },
    dataLabels: { style: { colors: ['#000000'] } },
    series: [{ name: 'Cantidad total', data: totales }],
    xaxis: { categories: categorias },
    title: { text: tituloInicial }
  };

  var chart = new ApexCharts(document.querySelector('#' + containerId), options);
  chart.render();

  if (backButtonId) {
    var btn = document.getElementById(backButtonId);
    if (btn) {
      btn.style.display = 'none';
      btn.addEventListener('click', function() {
        chart.updateOptions({
          series: [{ name: 'Cantidad total', data: totales }],
          plotOptions: { bar: { horizontal: true } },
          xaxis: { categories: categorias },
          title: { text: tituloInicial }
        });
        btn.style.display = 'none';
      });
    }
  }

  function mostrarDetalle(categoria) {
    var dataCategoria = json[categoria];
    var subcats = new Set();
    var series = [];

    for (var anio in dataCategoria) {
      series.push({ name: anio, data: [] });
      for (var sub in dataCategoria[anio]) {
        subcats.add(sub);
      }
    }

    var xaxisCats;
    if (ordenSubcategorias) {
      xaxisCats = Array.from(subcats).sort(function(a, b) {
        return ordenSubcategorias.indexOf(a) - ordenSubcategorias.indexOf(b);
      });
    } else {
      xaxisCats = Array.from(subcats);
    }

    series.forEach(function(serie) {
      serie.data = xaxisCats.map(function(sub) {
        return dataCategoria[serie.name][sub] || 0;
      });
    });

    chart.updateOptions({
      series: series,
      plotOptions: { bar: { horizontal: false } },
      xaxis: { categories: xaxisCats },
      title: { text: 'Detalle de: ' + categoria }
    });

    if (backButtonId) {
      var btn = document.getElementById(backButtonId);
      if (btn) btn.style.display = 'block';
    }
  }
}

// Gráfico combinado: vista inicial solo Formosa, drill-down con ambas regiones
function chart_dynamic_combined(jsonFormosa, jsonNacional, containerId, opciones) {
  containerId = containerId || 'chart-combined';
  opciones = opciones || {};

  var tituloInicial      = opciones.tituloInicial      || 'Cantidad total (Formosa)';
  var ordenSubcategorias = opciones.ordenSubcategorias || null;
  var backButtonId       = opciones.backButtonId       || null;

  // Vista inicial: totales de Formosa por tipo de acceso
  var categorias = Object.keys(jsonFormosa);
  var totales = categorias.map(function(cat) {
    var total = 0;
    Object.values(jsonFormosa[cat]).forEach(function(meses) {
      total += Object.values(meses).reduce(function(a, b) { return a + b; }, 0);
    });
    return total;
  });

  var options = {
    chart: {
      type: 'bar',
      height: 400,
      events: {
        dataPointSelection: function(event, chartContext, config) {
          mostrarDetalle(categorias[config.dataPointIndex]);
        }
      }
    },
    plotOptions: { bar: { horizontal: true } },
    series: [{ name: 'Formosa', data: totales }],
    xaxis: { categories: categorias },
    title: { text: tituloInicial }
  };

  var chart = new ApexCharts(document.querySelector('#' + containerId), options);
  chart.render();

  if (backButtonId) {
    var btn = document.getElementById(backButtonId);
    if (btn) {
      btn.style.display = 'none';
      btn.addEventListener('click', function() {
        chart.updateOptions({
          series: [{ name: 'Formosa', data: totales }],
          plotOptions: { bar: { horizontal: true } },
          xaxis: { categories: categorias },
          yaxis: { show: true, opposite: false, title: undefined, labels: { formatter: undefined } },
          tooltip: { shared: false, y: { formatter: undefined } },
          title: { text: tituloInicial }
        });
        btn.style.display = 'none';
      });
    }
  }

  function mostrarDetalle(categoria) {
    var dataFormosa  = jsonFormosa[categoria]  || {};
    var dataNacional = jsonNacional[categoria] || {};

    // Unir años de ambas regiones
    var aniosSet = new Set(Object.keys(dataFormosa).concat(Object.keys(dataNacional)));
    var anios = Array.from(aniosSet).sort();

    // Unir meses de ambas regiones
    var subcats = new Set();
    anios.forEach(function(anio) {
      if (dataFormosa[anio])  Object.keys(dataFormosa[anio]).forEach(function(m)  { subcats.add(m); });
      if (dataNacional[anio]) Object.keys(dataNacional[anio]).forEach(function(m) { subcats.add(m); });
    });

    var xaxisCats;
    if (ordenSubcategorias) {
      xaxisCats = Array.from(subcats).sort(function(a, b) {
        return ordenSubcategorias.indexOf(a) - ordenSubcategorias.indexOf(b);
      });
    } else {
      xaxisCats = Array.from(subcats);
    }

    // Generar una serie por cada año + región
    var series = [];
    anios.forEach(function(anio) {
      series.push({
        name: anio + ' - Formosa',
        data: xaxisCats.map(function(m) {
          return (dataFormosa[anio] && dataFormosa[anio][m]) || 0;
        })
      });
      series.push({
        name: anio + ' - Nacional',
        data: xaxisCats.map(function(m) {
          return (dataNacional[anio] && dataNacional[anio][m]) || 0;
        })
      });
    });

    function formatearValor(val) {
      if (val >= 1000000) return (val / 1000000).toFixed(1) + 'M';
      if (val >= 1000)    return (val / 1000).toFixed(1) + 'K';
      return Math.round(val);
    }

    // Doble eje Y: Formosa izquierda, Nacional derecha (cada uno con su propia escala)
    var primeraFormosa  = true;
    var primeraNacional = true;
    var yaxisConfig = series.map(function(serie) {
      var esNacional = serie.name.indexOf('Nacional') !== -1;
      var mostrar;
      if (esNacional) {
        mostrar = primeraNacional;
        primeraNacional = false;
      } else {
        mostrar = primeraFormosa;
        primeraFormosa = false;
      }
      return {
        seriesName: serie.name,
        opposite: esNacional,
        show: mostrar,
        title: mostrar ? { text: esNacional ? 'Nacional' : 'Formosa' } : undefined,
        labels: { formatter: function(val) { return formatearValor(val); } }
      };
    });

    chart.updateOptions({
      series: series,
      plotOptions: { bar: { horizontal: false } },
      xaxis: { categories: xaxisCats },
      yaxis: yaxisConfig,
      tooltip: {
        shared: true,
        y: {
          formatter: function(val) {
            return val.toLocaleString('es-AR');
          }
        }
      },
      title: { text: 'Detalle de: ' + categoria }
    });

    if (backButtonId) {
      var btn = document.getElementById(backButtonId);
      if (btn) btn.style.display = 'block';
    }
  }
}
