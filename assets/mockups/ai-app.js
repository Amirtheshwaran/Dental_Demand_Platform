document.addEventListener('DOMContentLoaded', () => {
    
    // Sliders Logic
    const sliders = [
        { id: 'slider-prevalence', valId: 'val-prevalence', suffix: '%' },
        { id: 'slider-pop', valId: 'val-pop', suffix: '', map: (v) => v < 33 ? 'Low' : v < 66 ? 'Med' : 'High' },
        { id: 'slider-income', valId: 'val-income', suffix: 'k', prefix: '$' },
        { id: 'slider-urban', valId: 'val-urban', suffix: '', map: (v) => v < 33 ? 'Rural' : v < 66 ? 'Suburban' : 'Urban' }
    ];

    sliders.forEach(config => {
        const slider = document.getElementById(config.id);
        const display = document.getElementById(config.valId);
        
        if(slider && display) {
            slider.addEventListener('input', (e) => {
                let val = e.target.value;
                if(config.map) {
                    display.textContent = config.map(val);
                } else {
                    let pre = config.prefix || '';
                    let suf = config.suffix || '';
                    display.textContent = `${pre}${val}${suf}`;
                }
            });
        }
    });

    // Run Analysis Animation Logic
    const btn = document.getElementById('btn-run-analysis');
    const nodes = {
        data: document.getElementById('node-data'),
        model: document.getElementById('node-model'),
        predict: document.getElementById('node-predict')
    };
    const connections = document.querySelectorAll('.pipeline-connection');
    const modelProgress = document.getElementById('model-progress');
    const loadingOverlay = document.getElementById('output-loader');
    const resultsContainer = document.getElementById('results-container');

    if(btn) {
        btn.addEventListener('click', () => {
            // Disable button during execution
            btn.disabled = true;
            btn.style.opacity = '0.5';
            
            // Hide previous results
            resultsContainer.style.opacity = '0';
            loadingOverlay.classList.add('active');

            // Reset pipeline
            Object.values(nodes).forEach(n => n.classList.remove('active'));
            connections.forEach(c => c.classList.remove('flowing'));
            modelProgress.style.width = '0%';

            // Step 1: Data Ingestion
            setTimeout(() => {
                nodes.data.classList.add('active');
                connections[0].classList.add('flowing');
            }, 500);

            // Step 2: Model Execution
            setTimeout(() => {
                nodes.data.classList.remove('active');
                nodes.model.classList.add('active');
                connections[0].classList.remove('flowing');
                
                // Simulate progress bar
                let progress = 0;
                let interval = setInterval(() => {
                    progress += 5;
                    modelProgress.style.width = `${progress}%`;
                    if(progress >= 100) {
                        clearInterval(interval);
                    }
                }, 100);

            }, 2000);

            // Step 3: Predictions & Output
            setTimeout(() => {
                nodes.model.classList.remove('active');
                nodes.predict.classList.add('active');
                connections[1].classList.add('flowing');
            }, 4500);
            
            // Finish
            setTimeout(() => {
                connections[1].classList.remove('flowing');
                loadingOverlay.classList.remove('active');
                resultsContainer.style.opacity = '1';
                resultsContainer.style.animation = 'fadeIn 0.5s ease-out forwards';
                
                // Re-enable button
                btn.disabled = false;
                btn.style.opacity = '1';
            }, 6000);
        });
    }

});
