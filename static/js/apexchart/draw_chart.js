
function max_min_chart(intermensual,interanual){
    
    const indicadores = intermensual.concat(interanual);
    
    maximo = (Math.max(...indicadores));
    minimo = (Math.min(...indicadores));

   

    return [maximo,minimo]
}


function generar_grafico(funcion, titulo, id_grafico)
{

    let [data_intermensual, data_interanual, meses,anio, valor, type, data_chart, data_total] = funcion();
    let data_params = [15,12.8,25.8]
    
    let[maximo,minimo] = max_min_chart(data_intermensual, data_interanual)

    if (type === 1){
        column_chart_comparative('chart-comparative',data_chart)
    }
    if (type === 0){
        column_chart_basic('chart-basic',data_total,meses)
       

    }

    return area_chart(
        id_grafico,
        data_intermensual,
        data_interanual, 
        meses,
        titulo + 
        ' ' 
        + valor, 
        maximo,
        minimo,
        
    )

}
    
    

