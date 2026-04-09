
$.fn.dataTable.ext.errMode = 'none';

new DataTable('#example', {
    info:false,
    language: {
        emptyTable: 'No hay datos disponibles para la fecha seleccionada.'
    },
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
