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
            } catch (error) {
                console.error('Error:', error);
                addMessageToChat('Sorry, there was an error processing your request.', 'bot');
            } finally {
                sendButton.disabled = false;
            }
        }
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

    // Call this function when the page loads
    updateQuickInsights();
});