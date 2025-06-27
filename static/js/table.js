

new DataTable('#example', {
    layout: {
        topStart: {
            buttons: [
                {
                    extend: 'excelHtml5',
                    autoFilter: true,
                    sheetName: 'Exported data'
                },
                {
                    extend: 'colvis',
                    text: 'Mostrar/Ocultar columnas'
                }
            ]
        }
    }
});
