

new DataTable('#example', {
    info:false,
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


new DataTable('#example2', {
    info: false,
    layout: {
        topStart: {
            buttons: [
                {
                    extend: 'excelHtml5',
                    autoFilter: true,
                    sheetName: 'Exported data'
                },
            ]
        }
    }
});
