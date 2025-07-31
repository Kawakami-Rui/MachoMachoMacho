document.addEventListener("DOMContentLoaded", function () {
    const rawData = document.getElementById("category-pie-data").textContent;
    const categoryTotals = JSON.parse(rawData);
    const categories = ['胸', '肩', '腕', '背中', '腹筋', '脚', 'その他'];
    const data = categories.map(cat => categoryTotals[cat] || 0);

    const backgroundColors = {
        '胸': '#ff6b6b',
        '肩': '#feca57',
        '腕': '#1dd1a1',
        '背中': '#54a0ff',
        '腹筋': '#a29bfe',
        '脚': '#ff9f43',
        'その他': '#dfe6e9'
    };

    Chart.register(ChartDataLabels);

    new Chart(document.getElementById('categoryPieChart').getContext('2d'), {
        type: 'pie',
        data: {
            labels: categories,
            datasets: [{
                data: data,
                backgroundColor: categories.map(cat => backgroundColors[cat] || '#cccccc')
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'カテゴリ毎の割合'
                },
                legend: {
                    display: false
                },
                datalabels: {
                    // 値が0の場合はラベルを非表示にする
                    formatter: (value, ctx) => {
                        const total = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return percentage > 0 ? `${percentage}%` : '';
                    },
                    // ラベルのテキスト色
                    color: '#000',
                    // ラベルのフォント設定
                    font: {
                        family: 'Arial',     // 使用するフォント
                        size: 17,            // フォントサイズ
                        weight: 'bold'       // フォントの太さ
                    },
                    // ラベルの表示位置設定
                    anchor: 'end',
                    align: 'start',
                    offset: 10
                }
            }
        },
        plugins: [ChartDataLabels]
    });
});