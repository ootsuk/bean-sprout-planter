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
    }

    // 初期化
    initialize() {
        this.updateSystemStatus();
        this.startAutoUpdate();
        this.setupEventListeners();
    }

    // イベントリスナーの設定
    setupEventListeners() {
        // AI相談フォーム
        const aiForm = document.getElementById('ai-question');
        if (aiForm) {
            aiForm.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.askAI();
                }
            });
        }

        // 収穫判断ボタン
        const harvestBtn = document.getElementById('harvest-check-btn');
        if (harvestBtn) {
            harvestBtn.addEventListener('click', () => {
                this.checkHarvest();
            });
        }
    }

    // システム状態の更新
    async updateSystemStatus() {
        if (this.isUpdating) return;
        
        this.isUpdating = true;
        
        try {
            const data = await apiCall('/api/status');
            this.updateSystemStatusDisplay(data);
        } catch (error) {
            console.error('システム状態取得エラー:', error);
            showNotification('システム状態の取得に失敗しました', 'warning');
        } finally {
            this.isUpdating = false;
        }
    }

    // システム状態表示の更新
    updateSystemStatusDisplay(data) {
        // コンポーネント状態の更新
        const components = data.components || {};
        
        // 各コンポーネントの状態を表示
        Object.keys(components).forEach(component => {
            const element = document.getElementById(`${component}-status`);
            if (element) {
                const status = components[component];
                element.textContent = status === 'available' ? '利用可能' : 
                                    status === 'not_implemented' ? '未実装' : 'エラー';
                element.className = `badge ${status === 'available' ? 'bg-success' : 
                                   status === 'not_implemented' ? 'bg-warning' : 'bg-danger'}`;
            }
        });
    }

    // AI相談
    async askAI() {
        const questionInput = document.getElementById('ai-question');
        const question = questionInput.value.trim();
        
        if (!question) {
            showNotification('質問を入力してください', 'warning');
            return;
        }

        const chatDiv = document.getElementById('ai-chat');
        const originalContent = showLoading(chatDiv);
        
        try {
            // ユーザーの質問を表示
            chatDiv.innerHTML = `
                <div class="message-container message-user">
                    <div class="message-bubble user">
                        ${question}
                    </div>
                    <div class="message-time">${formatDate(new Date())}</div>
                </div>
            `;

            // AI回答を取得
            const data = await apiCall('/api/ai/consultation', {
                method: 'POST',
                body: JSON.stringify({
                    question: question,
                    tag: 'general'
                })
            });

            if (data.status === 'success') {
                chatDiv.innerHTML += `
                    <div class="message-container message-ai">
                        <div class="message-bubble ai">
                            <i class="fas fa-robot"></i> ${data.answer}
                        </div>
                        <div class="message-time">${formatDate(new Date())}</div>
                    </div>
                `;
                showNotification('AI相談が完了しました', 'success');
            } else {
                chatDiv.innerHTML += `
                    <div class="message-container message-ai">
                        <div class="message-bubble ai">
                            <i class="fas fa-exclamation-triangle text-danger"></i> 
                            エラー: ${data.error}
                        </div>
                    </div>
                `;
                showNotification('AI相談でエラーが発生しました', 'danger');
            }
            
            chatDiv.scrollTop = chatDiv.scrollHeight;
            questionInput.value = '';
            
        } catch (error) {
            chatDiv.innerHTML = originalContent;
            chatDiv.innerHTML += `
                <div class="message-container message-ai">
                    <div class="message-bubble ai">
                        <i class="fas fa-exclamation-triangle text-danger"></i> 
                        エラー: ${error.message}
                    </div>
                </div>
            `;
            showNotification('AI相談でエラーが発生しました', 'danger');
        }
    }

    // 収穫判断
    async checkHarvest() {
        const statusDiv = document.getElementById('harvest-status');
        const originalContent = showLoading(statusDiv);
        
        try {
            const data = await apiCall('/api/ai/harvest-judgment', {
                method: 'POST'
            });

            if (data.status === 'success') {
                const icon = data.harvest_ready ? 
                    'fas fa-check-circle text-success' : 
                    'fas fa-clock text-warning';
                const message = data.harvest_ready ? '収穫可能です！' : 'まだ収穫時期ではありません';
                
                statusDiv.innerHTML = `
                    <div class="harvest-status-card fade-in">
                        <i class="${icon} harvest-icon"></i>
                        <h4>${message}</h4>
                        <div class="mt-3">
                            <p><strong>信頼度:</strong> ${formatNumber(data.confidence * 100)}%</p>
                            <p><strong>推奨事項:</strong> ${data.recommendation}</p>
                            <p><strong>残り日数:</strong> ${data.days_remaining}日</p>
                        </div>
                    </div>
                `;
                showNotification('収穫判断が完了しました', 'success');
            } else {
                statusDiv.innerHTML = `
                    <div class="text-center">
                        <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                        <h4>エラーが発生しました</h4>
                        <p>${data.error}</p>
                    </div>
                `;
                showNotification('収穫判断でエラーが発生しました', 'danger');
            }
        } catch (error) {
            statusDiv.innerHTML = originalContent;
            statusDiv.innerHTML += `
                <div class="text-center">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <h4>エラーが発生しました</h4>
                    <p>${error.message}</p>
                </div>
            `;
            showNotification('収穫判断でエラーが発生しました', 'danger');
        }
    }

    // 自動更新の開始
    startAutoUpdate() {
        this.updateTimer = setInterval(() => {
            this.updateSystemStatus();
        }, this.updateInterval);
    }

    // 自動更新の停止
    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    // クリーンアップ
    cleanup() {
        this.stopAutoUpdate();
    }
}

// ダッシュボードマネージャーのインスタンス
const dashboardManager = new DashboardManager();

// ページ読み込み完了時の初期化
document.addEventListener('DOMContentLoaded', function() {
    dashboardManager.initialize();
});

// ページ離脱時のクリーンアップ
window.addEventListener('beforeunload', function() {
    dashboardManager.cleanup();
});
