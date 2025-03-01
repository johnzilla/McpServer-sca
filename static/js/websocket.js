document.addEventListener('DOMContentLoaded', function() {
    const baseUrl = window.location.origin;

    const socket = io({
        path: '/dashboard/socket.io',
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
    });

    const analysisResults = document.getElementById('analysisResults');
    const recentAnalyses = document.getElementById('recentAnalyses');
    const analyzeForm = document.getElementById('analyzeForm');
    const analysisTime = document.getElementById('analysisTime');
    let analysisStartTime;

    const sessionsChart = new Chart(
        document.getElementById('sessionsChart'),
        {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Active Sessions',
                    data: [],
                    borderColor: '#0d6efd',
                    tension: 0.1
                }]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#ffffff'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#404040'
                        },
                        ticks: {
                            color: '#ffffff'
                        }
                    },
                    x: {
                        grid: {
                            color: '#404040'
                        },
                        ticks: {
                            color: '#ffffff'
                        }
                    }
                }
            }
        }
    );

    analyzeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const code = document.getElementById('codeInput').value;
        const sessionId = 'session_' + Date.now();

        analysisStartTime = performance.now();
        analysisTime.textContent = 'Analysis in progress...';

        analysisResults.innerHTML = '<div class="text-center"><div class="spinner-border text-light" role="status"></div><p class="mt-2">Analyzing code...</p></div>';

        fetch(`${baseUrl}/v1/sca/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            },
            body: JSON.stringify({
                code: code,
                session_id: sessionId,
                file_path: 'analysis_' + sessionId + '.py'
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Analysis received:', data);
            displayAnalysisResults(data);
            const elapsedTime = (performance.now() - analysisStartTime) / 1000;
            analysisTime.textContent = `Analysis completed in ${elapsedTime.toFixed(2)} seconds`;
        })
        .catch(error => {
            console.error('Error:', error);
            analysisResults.textContent = 'Error performing analysis: ' + error.message;
            analysisTime.textContent = 'Analysis failed';
        });
    });

    function displayAnalysisResults(data) {
        if (data.output) {
            const formattedJSON = JSON.stringify(data.output, null, 2);
            analysisResults.innerHTML = `<pre class="text-light">${formattedJSON}</pre>`;
        } else {
            analysisResults.textContent = 'Error performing analysis';
        }
    }

    function updateRecentAnalyses(analyses) {
        const fragment = document.createDocumentFragment();
        analyses.forEach(analysis => {
            const analysisItem = document.createElement('div');
            analysisItem.className = 'analysis-item';
            analysisItem.innerHTML = `
                <strong>File:</strong> ${analysis.session_id}<br>
                <small>${analysis.timestamp}</small>
                <span class="badge ${analysis.status === 'completed' ? 'bg-success' : 'bg-warning'} float-end">
                    ${analysis.status}
                </span>
            `;
            fragment.appendChild(analysisItem);
        });
        recentAnalyses.innerHTML = '';
        recentAnalyses.appendChild(fragment);
    }

    socket.on('connect', () => {
        console.log('Connected to WebSocket');
    });

    socket.on('initial_data', (data) => {
        console.log('Received initial data:', data);
        if (data.recent_analyses) {
            updateRecentAnalyses(data.recent_analyses);
        }

        if (data.active_sessions !== undefined) {
            const now = new Date().toLocaleTimeString();
            sessionsChart.data.labels = [now];
            sessionsChart.data.datasets[0].data = [data.active_sessions];
            sessionsChart.update();
        }
    });

    socket.on('analysis_complete', (data) => {
        console.log('Analysis complete:', data);
        if (data.session_id) {
            const analysisItem = document.createElement('div');
            analysisItem.className = 'analysis-item';
            analysisItem.innerHTML = `
                <strong>File:</strong> ${data.session_id}<br>
                <small>${new Date().toLocaleTimeString()}</small>
                <span class="badge bg-success float-end">completed</span>
            `;
            recentAnalyses.insertBefore(analysisItem, recentAnalyses.firstChild);

            while (recentAnalyses.children.length > 5) {
                recentAnalyses.removeChild(recentAnalyses.lastChild);
            }
        }

        const now = new Date().toLocaleTimeString();
        sessionsChart.data.labels.push(now);
        sessionsChart.data.datasets[0].data.push(1);

        if (sessionsChart.data.labels.length > 10) {
            sessionsChart.data.labels.shift();
            sessionsChart.data.datasets[0].data.shift();
        }

        sessionsChart.update('none');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from WebSocket');
    });

    socket.on('connect_error', (error) => {
        console.log('Connection error:', error);
    });
});