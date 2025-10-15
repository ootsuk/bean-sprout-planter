// 豆苗プランター - AI相談専用JavaScript

/**
 * AI相談機能
 */

// AI相談管理クラス
class AIConsultationManager {
    constructor() {
        this.selectedTag = 'general';
        this.chatHistory = [];
        this.maxHistoryLength = 50;
    }

    // 初期化
    initialize() {
        this.setupEventListeners();
        this.loadConsultationHistory();
        this.loadAvailableTags();
        this.selectDefaultTag();
    }

    // イベントリスナーの設定
    setupEventListeners() {
        // 質問送信ボタン
        const sendBtn = document.getElementById('send-question-btn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                this.sendQuestion();
            });
        }

        // 質問入力フィールド
        const questionInput = document.getElementById('question-input');
        if (questionInput) {
            questionInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.sendQuestion();
                }
            });
        }

        // タグ選択
        const tagElements = document.querySelectorAll('.tag-item');
        tagElements.forEach(tag => {
            tag.addEventListener('click', (e) => {
                this.selectTag(e.target.dataset.tag);
            });
        });

        // クイックアクション
        const quickActions = document.querySelectorAll('.quick-action-btn');
        quickActions.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.executeQuickAction(e.target.dataset.action);
            });
        });
    }

    // タグ選択
    selectTag(tag) {
        this.selectedTag = tag;
        
        // UI更新
        document.querySelectorAll('.tag-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const selectedElement = document.querySelector(`[data-tag="${tag}"]`);
        if (selectedElement) {
            selectedElement.classList.add('active');
        }
    }

    // デフォルトタグの選択
    selectDefaultTag() {
        this.selectTag('general');
    }

    // 質問送信
    async sendQuestion() {
        const questionInput = document.getElementById('question-input');
        const question = questionInput.value.trim();
        
        if (!question) {
            showNotification('質問を入力してください', 'warning');
            return;
        }

        // ユーザーメッセージを表示
        this.addMessageToChat('user', question);
        questionInput.value = '';

        // ローディング表示
        this.addMessageToChat('ai', '考え中...', true);

        try {
            const data = await apiCall('/api/ai/consultation', {
                method: 'POST',
                body: JSON.stringify({
                    question: question,
                    tag: this.selectedTag
                })
            });

            // ローディングメッセージを削除
            this.removeLastMessage();

            if (data.status === 'success') {
                this.addMessageToChat('ai', data.answer);
                this.addToHistory(question, data.answer, this.selectedTag);
                showNotification('AI相談が完了しました', 'success');
            } else {
                this.addMessageToChat('ai', `エラー: ${data.error}`, false, 'danger');
                showNotification('AI相談でエラーが発生しました', 'danger');
            }
        } catch (error) {
            this.removeLastMessage();
            this.addMessageToChat('ai', `エラー: ${error.message}`, false, 'danger');
            showNotification('AI相談でエラーが発生しました', 'danger');
        }
    }

    // チャットにメッセージを追加
    addMessageToChat(type, message, isLoading = false, variant = 'default') {
        const chatContainer = document.getElementById('chat-container');
        const messageDiv = document.createElement('div');
        
        const messageClass = type === 'user' ? 'message-user' : 'message-ai';
        const bubbleClass = type === 'user' ? 'user' : 'ai';
        const icon = type === 'user' ? 'fas fa-user' : 'fas fa-robot';
        
        let variantClass = '';
        if (variant === 'danger') {
            variantClass = 'text-danger';
        }

        messageDiv.className = `message-container ${messageClass}`;
        messageDiv.innerHTML = `
            <div class="message-bubble ${bubbleClass} ${variantClass}">
                ${isLoading ? '<div class="spinner-border spinner-border-sm me-2"></div>' : `<i class="${icon} me-2"></i>`}
                ${message}
            </div>
            <div class="message-time">${formatDate(new Date())}</div>
        `;
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // 最後のメッセージを削除
    removeLastMessage() {
        const chatContainer = document.getElementById('chat-container');
        const lastMessage = chatContainer.lastElementChild;
        if (lastMessage) {
            lastMessage.remove();
        }
    }

    // 履歴に追加
    addToHistory(question, answer, tag) {
        const historyItem = {
            timestamp: new Date().toISOString(),
            question: question,
            answer: answer,
            tag: tag
        };
        
        this.chatHistory.unshift(historyItem);
        
        // 履歴数制限
        if (this.chatHistory.length > this.maxHistoryLength) {
            this.chatHistory = this.chatHistory.slice(0, this.maxHistoryLength);
        }
        
        // ローカルストレージに保存
        storage.set('ai_consultation_history', this.chatHistory);
    }

    // 相談履歴の読み込み
    loadConsultationHistory() {
        this.chatHistory = storage.get('ai_consultation_history', []);
        this.updateHistoryDisplay();
    }

    // 履歴表示の更新
    updateHistoryDisplay() {
        const historyContainer = document.getElementById('history-container');
        if (!historyContainer) return;

        if (this.chatHistory.length === 0) {
            historyContainer.innerHTML = '<p class="text-muted small">相談履歴がありません</p>';
            return;
        }

        const recentHistory = this.chatHistory.slice(0, 5);
        historyContainer.innerHTML = recentHistory.map(item => `
            <div class="history-item">
                <div class="d-flex justify-content-between">
                    <strong>${item.tag}</strong>
                    <small class="text-muted">${formatDate(item.timestamp)}</small>
                </div>
                <div class="small text-truncate">${item.question}</div>
            </div>
        `).join('');
    }

    // 利用可能なタグの読み込み
    async loadAvailableTags() {
        try {
            const data = await apiCall('/api/ai/tags');
            if (data.status === 'success') {
                this.updateTagsDisplay(data.tags, data.descriptions);
            }
        } catch (error) {
            console.error('タグ取得エラー:', error);
        }
    }

    // タグ表示の更新
    updateTagsDisplay(tags, descriptions) {
        const tagsContainer = document.getElementById('tags-container');
        if (!tagsContainer) return;

        tagsContainer.innerHTML = tags.map(tag => `
            <span class="tag-item" data-tag="${tag}">
                ${descriptions[tag] || tag}
            </span>
        `).join('');

        // イベントリスナーを再設定
        const tagElements = document.querySelectorAll('.tag-item');
        tagElements.forEach(tag => {
            tag.addEventListener('click', (e) => {
                this.selectTag(e.target.dataset.tag);
            });
        });
    }

    // クイックアクションの実行
    executeQuickAction(action) {
        let question = '';
        
        switch(action) {
            case 'harvest':
                question = '現在の豆苗の収穫タイミングを判断してください';
                break;
            case 'disease':
                question = '豆苗の病気を診断してください';
                break;
            case 'cooking':
                question = '収穫した豆苗の調理例を教えてください';
                break;
            default:
                return;
        }

        // 質問を入力フィールドに設定
        const questionInput = document.getElementById('question-input');
        if (questionInput) {
            questionInput.value = question;
        }

        // 対応するタグを選択
        this.selectTag(action);
        
        // 質問を送信
        this.sendQuestion();
    }

    // 履歴のクリア
    clearHistory() {
        this.chatHistory = [];
        storage.remove('ai_consultation_history');
        this.updateHistoryDisplay();
        showNotification('相談履歴をクリアしました', 'info');
    }
}

// AI相談マネージャーのインスタンス
const aiConsultationManager = new AIConsultationManager();

// ページ読み込み完了時の初期化
document.addEventListener('DOMContentLoaded', function() {
    aiConsultationManager.initialize();
});
