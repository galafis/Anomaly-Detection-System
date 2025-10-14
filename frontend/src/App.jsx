import React, { useState, useEffect, useRef, useCallback } from 'react';
import Chart from 'chart.js/auto';
import './App.css';

function App() {
    const [totalDetections, setTotalDetections] = useState(0);
    const [anomaliesFound, setAnomaliesFound] = useState(0);
    const [isMonitoring, setIsMonitoring] = useState(false);
    const [algorithm, setAlgorithm] = useState('ensemble');
    const [alerts, setAlerts] = useState([]);
    const [detections, setDetections] = useState([]);
    const [modelStats, setModelStats] = useState([]);

    const timelineChartRef = useRef(null);
    const performanceChartRef = useRef(null);
    const monitoringIntervalRef = useRef(null);

    const timelineChartInstance = useRef(null);
    const performanceChartInstance = useRef(null);

    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

    useEffect(() => {
        // Initialize charts
        const timelineCtx = timelineChartRef.current.getContext('2d');
        timelineChartInstance.current = new Chart(timelineCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Anomaly Score',
                    data: [],
                    borderColor: '#f44336',
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: 'white' },
                        grid: { color: 'rgba(255, 255, 255, 0.2)' }
                    },
                    y: {
                        ticks: { color: 'white' },
                        grid: { color: 'rgba(255, 255, 255, 0.2)' }
                    }
                }
            }
        });

        const performanceCtx = performanceChartRef.current.getContext('2d');
        performanceChartInstance.current = new Chart(performanceCtx, {
            type: 'radar',
            data: {
                labels: ['Precision', 'Recall', 'F1-Score', 'Accuracy', 'Speed'],
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                },
                scales: {
                    r: {
                        ticks: { color: 'white' },
                        grid: { color: 'rgba(255, 255, 255, 0.2)' },
                        pointLabels: { color: 'white' }
                    }
                }
            }
        });

        fetchModelStats();
        fetchHistory();

        return () => {
            if (timelineChartInstance.current) {
                timelineChartInstance.current.destroy();
            }
            if (performanceChartInstance.current) {
                performanceChartInstance.current.destroy();
            }
            clearInterval(monitoringIntervalRef.current);
        };
    }, [fetchModelStats, fetchHistory]);

    useEffect(() => {
        if (isMonitoring) {
            monitoringIntervalRef.current = setInterval(() => {
                generateSampleData();
            }, 2000);
        } else {
            clearInterval(monitoringIntervalRef.current);
        }
        return () => clearInterval(monitoringIntervalRef.current);
    }, [isMonitoring, generateSampleData]);

    const addAlert = useCallback((message, type) => {
        const newAlert = { id: Date.now(), message, type };
        setAlerts(prevAlerts => [newAlert, ...prevAlerts.slice(0, 4)]);
        setTimeout(() => {
            setAlerts(prevAlerts => prevAlerts.filter(alert => alert.id !== newAlert.id));
        }, 5000);
    }, []);

    const fetchModelStats = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/metrics`);
            const data = await response.json();
            if (response.ok) {
                setModelStats(data);
                updatePerformanceChart(data);
            } else {
                addAlert(`Failed to fetch model metrics: ${data.error}`, 'danger');
            }
        } catch (error) {
            console.error('Error fetching model metrics:', error);
            addAlert(`Error fetching model metrics: ${error.message}`, 'danger');
        }
    }, [API_BASE_URL, updatePerformanceChart, addAlert]);

    const fetchHistory = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/history`);
            const data = await response.json();
            if (response.ok) {
                setDetections(data.history.slice(0, 10));
                setTotalDetections(data.total);
                setAnomaliesFound(data.history.filter(d => d.is_anomaly).length);
                updateTimelineChart(data.history);
            } else {
                addAlert(`Failed to fetch history: ${data.error}`, 'danger');
            }
        } catch (error) {
            console.error('Error fetching history:', error);
            addAlert(`Error fetching history: ${error.message}`, 'danger');
        }
    }, [API_BASE_URL, updateTimelineChart, addAlert]);

    const updateTimelineChart = useCallback((history) => {
        if (timelineChartInstance.current) {
            const labels = history.map(d => new Date(d.timestamp).toLocaleTimeString()).reverse();
            const scores = history.map(d => d.anomaly_score).reverse();
            timelineChartInstance.current.data.labels = labels.slice(-20);
            timelineChartInstance.current.data.datasets[0].data = scores.slice(-20);
            timelineChartInstance.current.update();
        }
    }, []);

    const updatePerformanceChart = useCallback((metrics) => {
        if (performanceChartInstance.current) {
            const datasets = metrics.map((metric, index) => ({
                label: metric.algorithm,
                data: [
                    (metric.precision || 0.0) * 100,
                    (metric.recall || 0.0) * 100,
                    (metric.f1_score || 0.0) * 100,
                    (metric.accuracy || 0.0) * 100,
                    (1 / (metric.prediction_time || 1)) * 100 // Inverse for speed
                ],
                borderColor: `hsl(${index * 60}, 70%, 60%)`,
                backgroundColor: `hsla(${index * 60}, 70%, 60%, 0.2)`,
            }));
            performanceChartInstance.current.data.datasets = datasets;
            performanceChartInstance.current.update();
        }
    }, []);

    const startRealTimeMonitoring = () => {
        setIsMonitoring(true);
        addAlert('Real-time monitoring started', 'success');
    };

    const stopRealTimeMonitoring = () => {
        setIsMonitoring(false);
        addAlert('Real-time monitoring stopped', 'warning');
    };

    const generateSampleData = useCallback(async () => {
        // Generate random features (assuming 1000 features as per backend)
        const features = Array.from({ length: 1000 }, () => Math.random() * 2 - 1);

        try {
            const response = await fetch(`${API_BASE_URL}/api/detect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    features: features,
                    algorithm: algorithm
                })
            });
            const result = await response.json();
            if (response.ok) {
                setTotalDetections(prev => prev + 1);
                if (result.is_anomaly) {
                    setAnomaliesFound(prev => prev + 1);
                }
                setDetections(prev => [result, ...prev.slice(0, 9)]);
                updateTimelineChart([result, ...detections]);

                if (result.is_anomaly) {
                    const alertClass = result.alert_level === 'critical' ? 'danger' :
                        result.alert_level === 'high' ? 'warning' : 'success';
                    addAlert(`Anomaly detected by ${result.algorithm} (${(result.confidence * 100).toFixed(1)}% confidence)`, alertClass);
                }
            } else {
                addAlert(`Detection error: ${result.error}`, 'danger');
            }
        } catch (error) {
            console.error('Error during detection:', error);
            addAlert(`Detection error: ${error.message}`, 'danger');
        }
    }, [API_BASE_URL, algorithm, detections, updateTimelineChart, addAlert]);

    const exportReport = async () => {
        addAlert('Generating report...', 'success');
        try {
            const response = await fetch(`${API_BASE_URL}/api/export-report`, {
                method: 'POST'
            });
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `anomaly_detection_report_${new Date().toISOString().slice(0, 10)}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                addAlert('Report exported successfully', 'success');
            } else {
                const errorData = await response.json();
                addAlert(`Export failed: ${errorData.error}`, 'danger');
            }
        } catch (error) {
            console.error('Error exporting report:', error);
            addAlert(`Export failed: ${error.message}`, 'danger');
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-700 text-white font-sans">
            <header className="bg-black bg-opacity-20 p-6 text-center backdrop-blur-md">
                <h1 className="text-4xl font-bold mb-2">🔍 Advanced Anomaly Detection System</h1>
                <p className="text-lg">Real-time monitoring with multiple algorithms and intelligent alerts</p>
            </header>

            <main className="container mx-auto p-6">
                {/* Control Panel */}
                <section className="bg-white bg-opacity-10 rounded-xl p-6 mb-6 shadow-lg backdrop-blur-md border border-white border-opacity-20">
                    <h2 className="text-2xl font-semibold mb-4 border-b border-white border-opacity-30 pb-3">🎛️ Control Panel</h2>
                    <div className="flex flex-wrap gap-4 mb-4">
                        <button className="btn bg-green-600 hover:bg-green-700" onClick={startRealTimeMonitoring} disabled={isMonitoring}>Start Monitoring</button>
                        <button className="btn bg-blue-600 hover:bg-blue-700" onClick={stopRealTimeMonitoring} disabled={!isMonitoring}>Stop Monitoring</button>
                        <button className="btn bg-gray-600 hover:bg-gray-700" onClick={generateSampleData}>Generate Sample Data</button>
                        <button className="btn bg-red-600 hover:bg-red-700" onClick={exportReport}>Export Report</button>
                    </div>

                    <div className="mb-4">
                        <label htmlFor="algorithmSelect" className="block text-lg font-medium mb-2">Detection Algorithm:</label>
                        <select
                            id="algorithmSelect"
                            className="w-full p-3 rounded-md bg-white bg-opacity-10 border border-white border-opacity-20 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            value={algorithm}
                            onChange={(e) => setAlgorithm(e.target.value)}
                        >
                            <option value="ensemble">Ensemble (All Algorithms)</option>
                            <option value="isolation_forest">Isolation Forest</option>
                            <option value="one_class_svm">One-Class SVM</option>
                            <option value="statistical">Statistical Method</option>
                        </select>
                    </div>
                </section>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Real-time Metrics */}
                    <div className="card">
                        <h3 className="text-xl font-semibold mb-3 border-b border-white border-opacity-30 pb-2">📊 Real-time Metrics</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="metric-card">
                                <div className="text-4xl font-bold text-green-400">{totalDetections}</div>
                                <div className="text-sm opacity-80">Total Detections</div>
                            </div>
                            <div className="metric-card">
                                <div className="text-4xl font-bold text-red-400">{anomaliesFound}</div>
                                <div className="text-sm opacity-80">Anomalies Found</div>
                            </div>
                            <div className="metric-card">
                                <div className="text-4xl font-bold text-blue-400">N/A</div> {/* Placeholder for accuracyRate */}
                                <div className="text-sm opacity-80">Accuracy Rate</div>
                            </div>
                            <div className="metric-card">
                                <div className="text-4xl font-bold text-yellow-400">N/A</div> {/* Placeholder for avgResponseTime */}
                                <div className="text-sm opacity-80">Avg Response Time</div>
                            </div>
                        </div>
                    </div>

                    {/* Recent Alerts */}
                    <div className="card">
                        <h3 className="text-xl font-semibold mb-3 border-b border-white border-opacity-30 pb-2">🚨 Recent Alerts</h3>
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                            {alerts.length === 0 && (
                                <div className="alert alert-success">
                                    <span className="status-indicator bg-green-500"></span>
                                    System initialized successfully
                                </div>
                            )}
                            {alerts.map(alert => (
                                <div key={alert.id} className={`alert ${alert.type === 'success' ? 'alert-success' : alert.type === 'warning' ? 'alert-warning' : 'alert-danger'}`}>
                                    <span className={`status-indicator ${alert.type === 'success' ? 'bg-green-500' : alert.type === 'warning' ? 'bg-yellow-500' : 'bg-red-500'}`}></span>
                                    {alert.message}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Anomaly Timeline */}
                    <div className="card lg:col-span-2">
                        <h3 className="text-xl font-semibold mb-3 border-b border-white border-opacity-30 pb-2">📈 Anomaly Timeline</h3>
                        <div className="chart-container h-64">
                            <canvas ref={timelineChartRef}></canvas>
                        </div>
                    </div>

                    {/* Algorithm Performance */}
                    <div className="card">
                        <h3 className="text-xl font-semibold mb-3 border-b border-white border-opacity-30 pb-2">⚡ Algorithm Performance</h3>
                        <div className="chart-container h-64">
                            <canvas ref={performanceChartRef}></canvas>
                        </div>
                    </div>

                    {/* Recent Detections */}
                    <div className="card lg:col-span-2">
                        <h3 className="text-xl font-semibold mb-3 border-b border-white border-opacity-30 pb-2">🔍 Recent Detections</h3>
                        <div className="max-h-64 overflow-y-auto">
                            <table className="w-full text-left table-auto">
                                <thead>
                                    <tr className="bg-white bg-opacity-10">
                                        <th className="p-3">Time</th>
                                        <th className="p-3">Algorithm</th>
                                        <th className="p-3">Status</th>
                                        <th className="p-3">Confidence</th>
                                        <th className="p-3">Alert Level</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {detections.map((detection, index) => (
                                        <tr key={index} className="border-b border-white border-opacity-10 last:border-b-0">
                                            <td className="p-3">{new Date(detection.timestamp).toLocaleTimeString()}</td>
                                            <td className="p-3">{detection.algorithm}</td>
                                            <td className="p-3">
                                                <span className={`status-indicator ${detection.is_anomaly ? 'bg-red-500' : 'bg-green-500'}`}></span>
                                                {detection.is_anomaly ? 'Anomaly' : 'Normal'}
                                            </td>
                                            <td className="p-3">{(detection.confidence * 100).toFixed(1)}%</td>
                                            <td className="p-3">{detection.alert_level}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Model Statistics */}
                    <div className="card lg:col-span-3">
                        <h3 className="text-xl font-semibold mb-3 border-b border-white border-opacity-30 pb-2">📋 Model Statistics</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {modelStats.map((metric, index) => (
                                <div key={index} className="metric-card bg-white bg-opacity-10 p-4 rounded-lg">
                                    <h4 className="text-lg font-semibold mb-2">{metric.algorithm}</h4>
                                    <p><strong>Precision:</strong> {(metric.precision * 100).toFixed(1)}%</p>
                                    <p><strong>Recall:</strong> {(metric.recall * 100).toFixed(1)}%</p>
                                    <p><strong>F1-Score:</strong> {(metric.f1_score * 100).toFixed(1)}%</p>
                                    <p><strong>Training Time:</strong> {metric.training_time.toFixed(2)}s</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;

