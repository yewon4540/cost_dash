// Chart.js로 그래프 생성
const ctx = document.getElementById("myChart").getContext("2d");
new Chart(ctx, {
    type: "bar",
    data: {
        labels: labels, // X축: 날짜
        datasets: datasets // Y축: 제품별 데이터
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: true,
                position: "top"
            },
            title: {
                display: true,
                text: "AWS 제품별 일별 비용 ($)"
            }
        },
        scales: {
            x: {
                ticks: {
                    color: "#666"
                }
            },
            y: {
                ticks: {
                    color: "#666",
                    callback: function(value) {
                        return `$${value}`;
                    }
                }
            }
        }
    }
});

