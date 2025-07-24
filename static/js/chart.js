document.addEventListener("DOMContentLoaded", function () {
    const rawData = document.getElementById("chart-data").textContent;
    const parsed = JSON.parse(rawData);

    const ctx = document.getElementById('stackedChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: parsed.labels,
            datasets: parsed.datasets
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '日別カテゴリごとの合計重量（kg）'
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: { stacked: true },
                y: { stacked: true, beginAtZero: true }
            }
        }
    });
});