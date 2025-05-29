function data_graficos_vehiculo(){

  chartPatentamientoAuto = generar_grafico(data_variacion_patentamiento, 'Variacion intermensual / interanual patentamiento', 'chart-patentamiento')
  chartTransferenciaAuto = generar_grafico(data_variacion_patentamiento, 'Variacion intermensual / interanual transferencia', 'chart-transferencia')

}