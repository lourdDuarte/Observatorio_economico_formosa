
function max_min_chart(intermensual,interanual){
    
    const indicadores = intermensual.concat(interanual);
    
    maximo = (Math.max(...indicadores));
    minimo = (Math.min(...indicadores));

   

    return [maximo,minimo]
}


function generar_grafico(funcion, titulo, id_grafico){

    let [data_intermensual, data_interanual, meses,anio, valor] = funcion();
   

    let[maximo,minimo] = max_min_chart(data_intermensual, data_interanual)

    // if (tipo === '$'){
    //     return draw_line_chart(intermensual ,interanual, titulo + ' ' + anio +' ' + valor, meses,maximo,minimo,'$', id_grafico)
    // }else{
    return area_chart(
        id_grafico,
        data_intermensual,
        data_interanual, 
        meses,
        titulo + 
        ' ' + 
        anio +' ' 
        + valor, 
        maximo,
        minimo,
        
        )

}
    
    

