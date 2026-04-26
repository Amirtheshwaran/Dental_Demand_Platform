document.addEventListener('DOMContentLoaded', () => {
    // Nav Navigation Logic
    const navBtns = document.querySelectorAll('.nav-btn');
    const views = document.querySelectorAll('.view-section');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active from all
            navBtns.forEach(b => b.classList.remove('active'));
            views.forEach(v => v.classList.remove('active'));

            // Add active to clicked
            btn.classList.add('active');
            const targetView = document.getElementById(`view-${btn.dataset.view}`);
            if(targetView) targetView.classList.add('active');
        });
    });

    // Base data
    const originalPrevalenceData = [
        { label: 'McDowell, WV', value: 41.2 },
        { label: 'Buchanan, VA', value: 38.5 },
        { label: 'Harlan, KY', value: 37.9 },
        { label: 'Owsley, KY', value: 36.4 },
        { label: 'Dickenson, VA', value: 35.8 },
        { label: 'Tazewell, VA', value: 35.1 },
        { label: 'Mingo, WV', value: 34.6 },
        { label: 'Clay, KY', value: 33.9 },
        { label: 'Perry, KY', value: 33.2 },
        { label: 'Wyoming, WV', value: 32.8 }
    ];

    let prevalenceChartInstance = null;

    // Slider logic
    const slider = document.getElementById('prevalenceSlider');
    const prevValue = document.getElementById('prevalenceValue');
    
    slider.addEventListener('input', (e) => {
        const threshold = parseFloat(e.target.value);
        prevValue.textContent = `${threshold}% - 50%+`;
        
        if (prevalenceChartInstance) {
            const filteredData = originalPrevalenceData.filter(item => item.value >= threshold);
            prevalenceChartInstance.data.labels = filteredData.map(item => item.label);
            prevalenceChartInstance.data.datasets[0].data = filteredData.map(item => item.value);
            prevalenceChartInstance.update();
            
            // Optional update highest prevalence value text
            const highestPrevVal = document.getElementById('highestPrevVal');
            const countyCountVal = document.getElementById('countyCountVal');
            if (highestPrevVal && filteredData.length > 0) {
                highestPrevVal.textContent = `${filteredData[0].label} (${filteredData[0].value}%)`;
            } else if (highestPrevVal) {
                highestPrevVal.textContent = "None";
            }
            if (countyCountVal) {
                // Mocking variable county count
                countyCountVal.textContent = Math.max(0, 3142 - Math.floor(threshold * 60)).toLocaleString();
            }
        }
    });

    // Chart.js Default styling
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = '#64748b';

    // Dashboard Bar Chart (Prevalence)
    const ctx1 = document.getElementById('prevalenceBarChart');
    if(ctx1) {
        prevalenceChartInstance = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: originalPrevalenceData.map(item => item.label),
                datasets: [{
                    label: 'Complete Tooth Loss Prevalence (%)',
                    data: originalPrevalenceData.map(item => item.value),
                    backgroundColor: '#0284c7', // Brand blue
                    borderRadius: 4,
                    barPercentage: 0.7,
                }]
            },
            options: {
                indexAxis: 'y', // Horizontal bar chart
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                return ` Prevalence: ${context.parsed.x}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: '#f1f5f9',
                            drawBorder: false
                        },
                        title: {
                            display: true,
                            text: 'Prevalence (%)'
                        }
                    },
                    y: {
                        grid: {
                            display: false,
                            drawBorder: false
                        }
                    }
                }
            }
        });
    }

    // Phase 2 Demand Index Bar Chart
    const ctx2 = document.getElementById('demandIndexChart');
    if(ctx2) {
        new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: [
                    'Marion, FL', 
                    'Collier, FL', 
                    'Maricopa, AZ', 
                    'Cameron, TX', 
                    'Pima, AZ',
                    'Horry, SC',
                    'Ocean, NJ'
                ],
                datasets: [{
                    label: 'Composite Demand Index Score',
                    data: [89.4, 86.2, 85.1, 82.5, 79.8, 77.4, 76.9],
                    backgroundColor: '#0d9488', // Brand teal
                    borderRadius: 4,
                    barPercentage: 0.6,
                }]
            },
            options: {
                indexAxis: 'y', // Horizontal
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                return ` Index Score: ${context.parsed.x}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        min: 50,
                        max: 100,
                        grid: {
                            color: '#f1f5f9'
                        },
                        title: {
                            display: true,
                            text: 'Demand Index (0-100)'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
});
