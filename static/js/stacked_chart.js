document.addEventListener("DOMContentLoaded", function () {
    const rawData = document.getElementById("chart-data").textContent;
    const parsed = JSON.parse(rawData);
    const categoryMap = parsed.category_map;

    const ctx = document.getElementById('stackedChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: parsed.labels.map(dateStr => {
                const date = new Date(dateStr);
                return ['日', '月', '火', '水', '木', '金', '土'][date.getDay()];
            }),
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
                            const allCategories = ['胸', '肩', '腕', '背中', '腹筋', '脚', 'その他'];
                            const datasets = chart.data.datasets;

                            return allCategories.reverse().map(cat => {
                                const matchingIndexes = datasets.map((ds, i) => categoryMap[ds.label] === cat ? i : null).filter(i => i !== null);
                                const hidden = matchingIndexes.every(i => chart.getDatasetMeta(i).hidden);
                                return {
                                    text: cat,
                                    fillStyle: categories[cat] || '#ccc',
                                    strokeStyle: categories[cat] || '#ccc',
                                    lineWidth: 1,
                                    hidden: hidden,
                                    category: cat
                                };
                            });
                        }
                    },
                    onClick: function(e, legendItem, legend) {
                        const chart = legend.chart;
                        const category = legendItem.text;
                        chart.data.datasets.forEach((ds, i) => {
                            if (categoryMap[ds.label] === category) {
                                const meta = chart.getDatasetMeta(i);
                                meta.hidden = meta.hidden === null ? true : null;
                            }
                        });
                        chart.update();
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            const datasetIndex = tooltipItems[0].datasetIndex;
                            const label = tooltipItems[0].chart.data.datasets[datasetIndex].label;
                            const category = categoryMap[label];
                            return category || label;
                        },
                        label: function(tooltipItem) {
                            const dataset = tooltipItem.dataset;
                            const value = tooltipItem.formattedValue;
                            return `${dataset.label}: ${value}`;
                        }
                    }
                },
                datalabels: {
                    display: false // データラベルは非表示
                }
            },
            scales: {
                x: { stacked: true },
                y: { stacked: true,
                     beginAtZero: true
                    }
            }
        }
    });
});


