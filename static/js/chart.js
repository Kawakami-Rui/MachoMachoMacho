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
                    position: 'top',
                    reverse: true,
                    labels: {
                        generateLabels: function(chart) {
                            const categories = {
                                '胸': '#ff6b6b',
                                '肩': '#feca57',
                                '腕': '#1dd1a1',
                                '背中': '#54a0ff',
                                '腹筋': '#a29bfe',
                                '脚': '#ff9f43',
                                'その他': '#dfe6e9'
                            };
                            return Object.keys(categories).reverse().map(category => ({
                                text: category,
                                fillStyle: categories[category],
                                strokeStyle: categories[category],
                                lineWidth: 1,
                                hidden: false,
                                datasetIndex: null
                            }));
                        }
                    }
                }
            },
            scales: {
                x: { stacked: true },
                y: { stacked: true, beginAtZero: true }
            }
        }
    });
});