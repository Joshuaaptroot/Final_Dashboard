let myChart = null;

function renderChangeableChart() {
    const xSelect = document.getElementById('x-axis-dropdown'); 
    const ySelect = document.getElementById('y-axis-dropdown'); 
    const typeSelect = document.getElementById('type-dropdown');
    const chartCanvas = document.getElementById('changeableChartCanvas'); 

    const selectedXAxis = xSelect.value;
    const selectedYAxis = ySelect.value;
    const ChartType = typeSelect.value;

    const box = document.querySelector('#box');

    var x , y , h , w;

    function ts(e){
        x = e.touches[0].clientX;
        y = e.touches[0].clientY;

        h = box.clientHeight;
        w= box.clientWidth;
    }

    function tm(e){
        mx = e.touches[0].clientX;
        my = e.touches[0].clientY;

        cx = mx - x;
        cy = my - y;

        box.computedStyleMap.width=cx+w;
        box.computedStyleMap.height=cy+h
    }


    fetch(`http://localhost:5000/api/ChartData/${selectedXAxis}/${selectedYAxis}`)
    .then(response => response.json())
    .then(data => {
        console.log('Data received:', data);

        // Fetch AI completion separately
        fetch(`http://localhost:5000/ai/${selectedXAxis}/${selectedYAxis}`)
            .then(aiResponse => aiResponse.json())
            .then(aiData => {
                console.log('AI Data received:', aiData);

                // Access the 'result' key in the AI data
                const aiResult = aiData.result;

                // Update your HTML with the AI completion data
                document.querySelector('.ai-output').innerText = aiResult;

                // Continue with your code for handling the chart data
                const xData = data.map(item => item[selectedXAxis]);
                const yData = data.map(item => item[selectedYAxis]);

                if (myChart) {
                    myChart.destroy();
                }

                const ctxChangeableChart = chartCanvas.getContext('2d');
                myChart = new Chart(ctxChangeableChart, {
                    type: ChartType,
                    data: {
                        labels: xData,
                        datasets: [{
                            label: selectedYAxis,
                            data: yData,
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1 
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            },
                            x: {
                                display: true
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('AI Data fetch error:', error);
            });
    })
    .catch(error => {
        console.error('Data fetch error:', error);
    });
}
