new DataTable('#example', {
    
    fixedColumns: {
        start: 0
    },
    layout: {
      topStart: {
        buttons: [
            {
                extend: 'colvis',
                text: 'Esconder columna',
               
            }
        ]
         
    }
    },
    order: [],
    paging: true,
   

});