// 豆苗プランター - ダッシュボード専用JavaScript

/**
 * ダッシュボード機能
 */

// ダッシュボード管理クラス
class DashboardManager {
    constructor() {
        this.updateInterval = 30000; // 30秒
        this.updateTimer = null;
        this.isUpdating = false;
        this.isInitialized = false;
        this.temperatureChart = null;
        this.historyLoaded = false;
    }

    // 初期化
    initialize() {
        if (this.isInitialized) {
            console.warn('DashboardManager already initialized');
            return;
        }
        
        this.isInitialized = true;
        console.log('Initializing DashboardManager...');
        
        this.initializeChart();
        this.updateSystemStatus();
        this.updateHarvestStatus();
        this.updateLatestImage();
        this.startAutoUpdate();
    }

    // Chart.jsの初期化
    initializeChart() {
        const ctx = document.getElementById('temperature-chart');
        if (!ctx) {
            console.warn('Temperature chart element not found');
            return;
        }

        this.temperatureChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '温度 (°C)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: '温度 (°C)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '時間'
                        }
                    }
                }
            }
        });

        // 初期データの読み込み
        this.loadTemperatureHistory();
    }

    // 温度履歴データの読み込み
    async loadTemperatureHistory() {
        if (this.historyLoaded) {
            return;
        }
        
        try {
            const data = await apiCall('/api/sensors/history?type=temperature');
            if (data.status === 'success' && data.history) {
                this.updateChartData(data.history);
                this.historyLoaded = true;
                console.log('Temperature history loaded successfully');
            } else {
                this.loadSampleData();
                this.historyLoaded = true;
                console.log('Using sample temperature data');
            }
        } catch (error) {
            console.error('温度履歴取得エラー:', error);
            this.loadSampleData();
            this.historyLoaded = true;
            console.log('Using sample temperature data due to error');
        }
    }

    // サンプルデータの読み込み
    loadSampleData() {
        const now = new Date();
        const sampleData = [];

        for (let i = 23; i >= 0; i--) {
            const time = new Date(now.getTime() - (i * 60 * 60 * 1000));
            const temperature = 20 + Math.sin(i * 0.5) * 5 + Math.random() * 2;
            
            sampleData.push({
                timestamp: time.toISOString(),
                temperature: parseFloat(temperature.toFixed(1)),
                value: parseFloat(temperature.toFixed(1)) // APIの構造に合わせて追加
            });
        }

        this.updateChartData(sampleData);
    }

    // チャートデータの更新
    updateChartData(history) {
        if (!this.temperatureChart || !history || history.length === 0) return;

        const labels = [];
        const temperatures = [];

        history.forEach(item => {
            const date = new Date(item.timestamp);
            labels.push(date.toLocaleTimeString('ja-JP', { 
                hour: '2-digit', 
                minute: '2-digit' 
            }));
            // APIが返すデータ構造に応じて値を取得
            const tempValue = item.temperature !== undefined ? item.temperature : item.value;
            temperatures.push(tempValue);
        });

        this.temperatureChart.data.labels = labels;
        this.temperatureChart.data.datasets[0].data = temperatures;
        this.temperatureChart.update('none');
    }

    // チャートにライブデータを追加
    addDatapointToChart(timestamp, temperature) {
        if (!this.temperatureChart) return;

        const chart = this.temperatureChart;
        const label = new Date(timestamp).toLocaleTimeString('ja-JP', {
            hour: '2-digit',
            minute: '2-digit'
        });

        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(temperature);

        // グラフのデータポイント数を制限（例：24件）
        if (chart.data.labels.length > 24) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update();
    }

    // システム状態の更新
    async updateSystemStatus() {
        if (this.isUpdating) return;
        
        this.isUpdating = true;
        
        try {
            const data = await apiCall('/api/sensors/data');
            if (data.status === 'success' && data.data) {
                this.updateSensorDisplay(data.data);

                // 履歴読み込み後にライブデータをチャートに追加
                if (this.historyLoaded && data.data.temperature !== undefined) {
                    const timestamp = data.data.timestamp || new Date().toISOString();
                    this.addDatapointToChart(timestamp, data.data.temperature);
                }
            }
        } catch (error) {
            console.error('センサーデータ取得エラー:', error);
            // エラー時はサンプルデータを表示
            this.updateSensorDisplay({
                temperature: (20 + Math.random() * 10).toFixed(1),
                humidity: (50 + Math.random() * 30).toFixed(1),
                tank_level: (60 + Math.random() * 40).toFixed(1)
            });
        } finally {
            this.isUpdating = false;
        }
    }

    // センサー表示の更新
    updateSensorDisplay(data) {
        const tempElement = document.getElementById('temperature');
        if (tempElement && data.temperature !== undefined) {
            tempElement.textContent = `${data.temperature}°C`;
        }

        const humidityElement = document.getElementById('humidity');
        if (humidityElement && data.humidity !== undefined) {
            humidityElement.textContent = `${data.humidity}%`;
        }

        const tankElement = document.getElementById('tank-level');
        if (tankElement && data.tank_level !== undefined) {
            tankElement.textContent = `${data.tank_level}%`;
        }

        this.updateCardColors(data);
    }

    // カードの色をデータに応じて更新
    updateCardColors(data) {
        const tempCard = document.querySelector('#temperature')?.closest('.card');
        if (tempCard) {
            const temp = parseFloat(data.temperature);
            if (temp < 15) {
                tempCard.className = 'card status-card bg-info text-white';
            } else if (temp > 25) {
                tempCard.className = 'card status-card bg-warning text-white';
            } else {
                tempCard.className = 'card status-card bg-primary text-white';
            }
        }

        const tankCard = document.querySelector('#tank-level')?.closest('.card');
        if (tankCard) {
            const level = parseFloat(data.tank_level);
            if (level < 20) {
                tankCard.className = 'card status-card bg-danger text-white';
            } else if (level < 50) {
                tankCard.className = 'card status-card bg-warning text-white';
            } else {
                tankCard.className = 'card status-card bg-success text-white';
            }
        }
    }

    // 収穫判断結果の更新
    async updateHarvestStatus() {
        try {
            const data = await apiCall('/api/ai/harvest-judgment', {
                method: 'POST'
            });
            if (data.status === 'success') {
                this.displayHarvestResult(data);
            } else {
                this.displayHarvestError(data.error);
            }
        } catch (error) {
            console.error('収穫判断取得エラー:', error);
            this.displayHarvestError('収穫判断データの取得に失敗しました');
        }
    }

    // 収穫判断結果の表示
    displayHarvestResult(data) {
        const statusDiv = document.getElementById('harvest-status');
        const resultDiv = document.getElementById('harvest-result');
        
        if (statusDiv && resultDiv) {
            statusDiv.style.display = 'none';
            resultDiv.style.display = 'block';
            
            const readyElement = document.getElementById('harvest-ready');
            const confidenceElement = document.getElementById('harvest-confidence');
            const recommendationElement = document.getElementById('harvest-recommendation');
            const updatedElement = document.getElementById('harvest-updated');
            
            if (readyElement) {
                readyElement.textContent = data.harvest_ready ? 'はい' : 'いいえ';
                readyElement.className = `badge ${data.harvest_ready ? 'bg-success' : 'bg-warning'} fs-6`;
            }
            
            if (confidenceElement) {
                const confidence = Math.round(data.confidence * 100);
                confidenceElement.textContent = `${confidence}%`;
                confidenceElement.className = `badge ${confidence > 70 ? 'bg-success' : confidence > 50 ? 'bg-warning' : 'bg-danger'} fs-6`;
            }
            
            if (recommendationElement) {
                recommendationElement.textContent = data.recommendation || '特にありません';
            }
            
            if (updatedElement) {
                updatedElement.textContent = formatDate(new Date());
            }
        }
    }

    // 収穫判断エラーの表示
    displayHarvestError(errorMessage) {
        const statusDiv = document.getElementById('harvest-status');
        
        if (statusDiv) {
            statusDiv.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <p class="text-danger">${errorMessage}</p>
                </div>
            `;
        }
    }

    // 最新画像の更新
    async updateLatestImage() {
        try {
            const data = await apiCall('/api/camera/latest');
            if (data.status === 'success' && data.image_url) {
                const imgElement = document.getElementById('latest-image');
                if (imgElement) {
                    imgElement.src = data.image_url;
                    imgElement.alt = '最新の豆苗画像';
                }
            }
        } catch (error) {
            console.error('最新画像取得エラー:', error);
        }
    }

    // 自動更新の開始
    startAutoUpdate() {
        this.stopAutoUpdate();
        
        this.updateTimer = setInterval(() => {
            if (!this.isUpdating) {
                this.updateSystemStatus();
                // 収穫判断は長い間隔で更新
                if (Math.random() < 0.1) {
                    this.updateHarvestStatus();
                }
            }
        }, this.updateInterval);
        
        console.log(`Auto-update started with interval: ${this.updateInterval}ms`);
    }

    // 自動更新の停止
    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    // チャートの破棄
    destroyChart() {
        if (this.temperatureChart) {
            this.temperatureChart.destroy();
            this.temperatureChart = null;
        }
    }

    // クリーンアップ
    cleanup() {
        this.stopAutoUpdate();
        this.destroyChart();
        this.isInitialized = false;
        this.historyLoaded = false;
    }
}

// ダッシュボードマネージャーのインスタンス
let dashboardManager = null;

// ページ読み込み完了時の初期化
document.addEventListener('DOMContentLoaded', function() {
    if (dashboardManager) {
        dashboardManager.cleanup();
    }
    
    dashboardManager = new DashboardManager();
    dashboardManager.initialize();
});

// ページ離脱時のクリーンアップ
window.addEventListener('beforeunload', function() {
    if (dashboardManager) {
        dashboardManager.cleanup();
        dashboardManager = null;
    }
});

// ウィンドウリサイズ時のチャート調整
let resizeTimeout = null;
window.addEventListener('resize', function() {
    if (resizeTimeout) {
        clearTimeout(resizeTimeout);
    }
    
    resizeTimeout = setTimeout(function() {
        if (dashboardManager && dashboardManager.temperatureChart) {
            dashboardManager.temperatureChart.resize();
        }
    }, 250);
});