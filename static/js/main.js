async function getChartData(modelName, anioId, valorId, additionalKwargs = {}) {
    // Construir los query parameters
    const queryParams = new URLSearchParams(additionalKwargs).toString();
    const url = `/api/chart/${modelName}/${anioId}/${valorId}/` + (queryParams ? `?${queryParams}` : '');

    try {
        const response = await fetch(url);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        const chartOptions = await response.json();
        return chartOptions;
    } catch (error) {
        console.error("Error al obtener los datos del gráfico:", error);
        // Aquí podrías mostrar un mensaje de error al usuario
        return null;
    }
}

