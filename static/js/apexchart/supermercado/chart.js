function data_graficos_supermercado(){

  chartPrecioCorriente = generar_grafico(data_variacion_corriente, 'Variacion intermensual / interanual precios corriente', 'chart-corriente')
  chartPrecioConstante = generar_grafico(data_variacion_corriente, 'Variacion intermensual / interanual precios constante', 'chart-constante')

}