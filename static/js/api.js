function picker(id) {
    return datePicker = flatpickr("#datePicker", {
            mode: "range",
            dateFormat: "Y-m-d",
            onChange: function(selectedDates, dateStr) {
                if (selectedDates.length === 2) {
                    const startDate = flatpickr.formatDate(selectedDates[0], "Y-m-d");
                    const endDate = flatpickr.formatDate(selectedDates[1], "Y-m-d");

                    document.getElementById('dateRangeText').textContent = `${flatpickr.formatDate(selectedDates[0], "d/m/Y")} - ${flatpickr.formatDate(selectedDates[1], "d/m/Y")}`;

                    document.querySelectorAll('.predefined-btn').forEach(btn => btn.classList.remove('active'));

                    applyFilter(startDate, endDate);
                }
            }
        });

        
}

