document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/symptom-frequency")
        .then(response => response.json())
        .then(data => renderSymptomFrequencyChart(data));

    fetch("/api/symptom-map")
        .then(response => response.json())
        .then(data => renderSymptomGraph(data));

    fetch("/api/symptom-heatmap")
        .then(response => response.json())
        .then(data => renderSymptomHeatmap(data));
});

function renderSymptomFrequencyChart(data) {
    const ctx = document.getElementById("symptomFrequencyChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: data.labels,
            datasets: [{
                label: "Symptom Frequency",
                data: data.values,
                backgroundColor: "rgba(75, 192, 192, 0.6)"
            }]
        },
    });
}

function renderSymptomGraph(data) {
    const ctx = document.getElementById("symptomGraph").getContext("2d");
    new Chart(ctx, {
        type: "network",
        data: data,
        options: {}
    });
}

function renderSymptomHeatmap(data) {
    const ctx = document.getElementById("symptomHeatmap").getContext("2d");
    new Chart(ctx, {
        type: "heatmap",
        data: data,
        options: {}
    });
}
