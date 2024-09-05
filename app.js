//import { generateAndDownloadPDF } from 'pdfGenerator.js';

document.addEventListener('DOMContentLoaded', function() {
    const toggleInsightsButton = document.getElementById('toggleInsights');
    const quickInsightsPanel = document.getElementById('quickInsights');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const chatHistory = document.getElementById('chatHistory');

    toggleInsightsButton.addEventListener('click', function() {
        quickInsightsPanel.classList.toggle('hidden');
        this.textContent = quickInsightsPanel.classList.contains('hidden')
            ? 'Show Quick Insights'
            : 'Hide Quick Insights';
    });

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    async function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessageToChat(message, 'user');
            userInput.value = '';
            sendButton.disabled = true;
            addMessageToChat('Thinking...', 'bot');

            try {
                const response = await fetch('http://localhost:5000/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: message }),
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                chatHistory.removeChild(chatHistory.lastChild);
                addMessageToChat(data.response, 'bot');

                if (data.graph_data) {
                    addGraphToChat(data.graph_data);
                }


            } catch (error) {
                console.error('Error:', error);
                addMessageToChat('Sorry, there was an error processing your request.', 'bot');
            } finally {
                sendButton.disabled = false;
            }
        }
    }

    function addGraphToChat(graphData) {
        const graphContainer = document.createElement('div');
        graphContainer.classList.add('message', 'bot', 'graph-container');
        chatHistory.appendChild(graphContainer);

        const canvas = document.createElement('canvas');
        graphContainer.appendChild(canvas);

        const ctx = canvas.getContext('2d');

        // Default colors for datasets
        const defaultColors = [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(199, 199, 199, 0.8)',
            'rgba(83, 102, 255, 0.8)',
            'rgba(40, 159, 64, 0.8)',
            'rgba(210, 105, 30, 0.8)'
        ];

        // Prepare datasets based on the graph type
        let datasets = [];
        if (Array.isArray(graphData.data.datasets)) {
            datasets = graphData.data.datasets.map((dataset, index) => ({
                ...dataset,
                backgroundColor: dataset.backgroundColor || defaultColors[index % defaultColors.length],
                borderColor: dataset.borderColor || defaultColors[index % defaultColors.length],
            }));
        } else if (Array.isArray(graphData.data.values)) {
            datasets = [{
                data: graphData.data.values,
                backgroundColor: defaultColors.slice(0, graphData.data.values.length),
                borderColor: defaultColors.slice(0, graphData.data.values.length),
            }];
        }

        new Chart(ctx, {
            type: graphData.type,
            data: {
                labels: graphData.data.labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: graphData.type !== 'bar' && graphData.type !== 'line',
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: graphData.title || 'Chart'
                    }
                },
                scales: {
                    x: {
                        display: graphData.type === 'bar' || graphData.type === 'line',
                    },
                    y: {
                        display: graphData.type === 'bar' || graphData.type === 'line',
                        beginAtZero: true
                    }
                }
            }
        });

        chatHistory.scrollTop = chatHistory.scrollHeight;
    }


    function addMessageToChat(message, sender) {
        const messageElement = document.createElement('pre');
        messageElement.classList.add('message', sender);
        messageElement.textContent = message;
        messageElement.style.whiteSpace = 'pre-wrap';
        chatHistory.appendChild(messageElement);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    async function updateQuickInsights() {
        try {
            const response = await fetch('http://localhost:5000/quick-insights');
            const data = await response.json();
            document.getElementById('shelfLifeScore').textContent = data.shelfLifeScore.toFixed(2);
            document.getElementById('viabilityScore').textContent = data.viabilityScore.toFixed(2);
            const formatter = new Intl.NumberFormat('en-IN');
            document.getElementById('currentRevenue').textContent = `₹${formatter.format(data.currentRevenue.toFixed(2))}`;
            document.getElementById('predictedRevenue').textContent = `₹${formatter.format(data.predictedRevenue.toFixed(2))}`;
        } catch (error) {
            console.error('Error fetching quick insights:', error);
        }
    }

    const generateReportButton = document.getElementById('generateReport');
    generateReportButton.addEventListener('click', async function() {
        try {
            generateReportButton.disabled = true;
            generateReportButton.textContent = 'Generating...';

            const response = await fetch('http://localhost:5000/generate-report');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            console.log('Data received for PDF:', data);  // For debugging
            if (data && typeof data === 'object') {
                await window.generateAndDownloadPDF(data);
            } else {
                console.error('Invalid data structure received');
                alert('Error: Invalid data received for report generation');
            }
        } catch (error) {
            console.error('Error generating report:', error);
            alert('Error generating report');
        } finally {
            generateReportButton.disabled = false;
            generateReportButton.textContent = 'Generate Insights Report';
        }
    });

    addMessageToChat('Hello, I\'m Kai! \nI am your personal business intelligence agent. I give insights and suggestions specific to your business. \n \nHow can I help you today?', 'bot');
    // Call this function when the page loads
    updateQuickInsights();
});