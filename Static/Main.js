// Initialize a variable to hold the Chart object
let myChart = null;

// Function to render a changeable chart based on user input
function renderChangeableChart() {
    // Get references to HTML elements and canvas
    const xSelect = document.getElementById('x-axis-dropdown'); 
    const ySelect = document.getElementById('y-axis-dropdown'); 
    const typeSelect = document.getElementById('type-dropdown');
    const chartCanvas = document.getElementById('changeableChartCanvas'); 

    // Get selected values from dropdowns to later be used in the URL routes in python.
    const selectedXAxis = xSelect.value;
    const selectedYAxis = ySelect.value;
    const chartType = typeSelect.value;

    /*these events were implemented as part of a resize chart function, however, due to a lack of techncial CSS skills, 
    whilst the resize function worked, it did not present well with elements inside the resizeable div, however it has been kept in,
    as it was possible I would return to the function in a later sprint. further logic around this function exists in the resize.js file.
    //Variables for touch events
    var x , y , h , w;

    // Touch start event listener
    function ts(e){
        x = e.touches[0].clientX;
        y = e.touches[0].clientY;

        h = box.clientHeight;
        w= box.clientWidth;
    }

    // Touch move event listener
    function tm(e){
        mx = e.touches[0].clientX;
        my = e.touches[0].clientY;

        cx = mx - x;
        cy = my - y;

        // Update box dimensions
        box.computedStyleMap.width=cx+w;
        box.computedStyleMap.height=cy+h;
    } */

    // Fetch chart data from the server based on user selection, using the variable names pulled from the HTML
    fetch(`http://localhost:5000/api/ChartData/${selectedXAxis}/${selectedYAxis}`)
    .then(response => response.json())
    .then(data => {
        console.log('Data received:', data);

        // Fetch AI completion data separately, establishing a second route to use in the app.py, 
        fetch(`http://localhost:5000/ai/${selectedXAxis}/${selectedYAxis}`)
            .then(aiResponse => aiResponse.json())
            .then(aiData => {
                console.log('AI Data received:', aiData);

                // Access the 'result' key in the AI data, where the content needed for the completion is stored
                const aiResult = aiData.result;

                // Updates the HTML with the AI completion data, shifiting the completion into the modifie.HTML
                document.querySelector('.ai-output').innerText = aiResult;

                // Extract x and y data from the fetched data, this data is used for the actual chart
                const xData = data.map(item => item[selectedXAxis]);
                const yData = data.map(item => item[selectedYAxis]);

                /* Destroy existing chart if it exists, necessary for the variable content of the chart. when a user changes the axis, this destroys the existing chart
                    to make way for a new one */
                if (myChart) {
                    myChart.destroy();
                }

                // This function then creates a chart using ther x & y data saved to xData and yData
                const ctxChangeableChart = chartCanvas.getContext('2d');
                myChart = new Chart(ctxChangeableChart, {
                    type: chartType,
                    data: {
                        // sets display of chart
                        labels: xData,
                        datasets: [{
                            label: selectedYAxis,
                            data: yData,
                            backgroundColor: '#BE0071',
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
            // logs erro to console to be viewed in devtools and logs.
            .catch(error => {
                console.error('AI Data fetch error:', error);
            });
    })
    .catch(error => {
        console.error('Data fetch error:', error);
    });
}
