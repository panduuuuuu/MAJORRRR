document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/symptom-frequency")
        .then(response => response.json())
        .then(data => {
            const symptoms = Object.keys(data);
            const frequencies = Object.values(data);

            const ctx = document.getElementById("symptomFrequencyChart").getContext("2d");
            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: symptoms,
                    datasets: [{
                        label: "Symptom Frequency",
                        data: frequencies,
                        backgroundColor: "rgba(75, 192, 192, 0.6)",
                        borderColor: "rgba(75, 192, 192, 1)",
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { ticks: { autoSkip: false } },
                        y: { beginAtZero: true }
                    }
                }
            });
        })
        .catch(error => console.error("Error fetching symptom frequency data:", error));
});
