
$.fn.dataTable.ext.errMode = 'none';

new DataTable('#example', {
    info:false,
    language: {
        emptyTable: 'No hay datos disponibles para la fecha seleccionada.',
        search: 'Buscar:'
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
    language: {
        search: 'Buscar:'
    },
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
