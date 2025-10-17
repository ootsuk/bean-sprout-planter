// 豆苗プランター - AI相談専用JavaScript

/**
 * AI相談機能
 */

// マークダウンレンダラー
class MarkdownRenderer {
    constructor() {
        // marked.jsの設定
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (lang && typeof hljs !== 'undefined' && hljs.getLanguage(lang)) {
                        return hljs.highlight(code, {language: lang}).value;
                    }
                    if (typeof hljs !== 'undefined') {
                        return hljs.highlightAuto(code).value;
                    }
                    return code;
                },
                breaks: true,
                gfm: true
            });
        }
    }
    
    render(markdownText) {
        if (typeof marked !== 'undefined') {
            return marked.parse(markdownText);
        }
        // marked.jsが読み込まれていない場合はプレーンテキストを返す
        return markdownText.replace(/\n/g, '<br>');
    }
}

// グローバルインスタンス
const markdownRenderer = new MarkdownRenderer();

// 画像添付機能
class ImageAttachment {
    constructor() {
        this.attachedImage = null;
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const imageAttachBtn = document.getElementById('image-attach-btn');
        const imageInput = document.getElementById('image-input');
        const removeImageBtn = document.getElementById('remove-image-btn');
        
        if (imageAttachBtn) {
            imageAttachBtn.addEventListener('click', () => {
                imageInput.click();
            });
        }
        
        if (imageInput) {
            imageInput.addEventListener('change', (e) => {
                this.handleImageSelect(e);
            });
        }
        
        if (removeImageBtn) {
            removeImageBtn.addEventListener('click', () => {
                this.removeImage();
            });
        }
    }
    
    handleImageSelect(event) {
        const file = event.target.files[0];
        if (file) {
            // ファイルサイズチェック（5MB以下）
            if (file.size > 5 * 1024 * 1024) {
                showNotification('画像サイズは5MB以下にしてください', 'warning');
                return;
            }
            
            // ファイル形式チェック
            if (!file.type.startsWith('image/')) {
                showNotification('画像ファイルを選択してください', 'warning');
                return;
            }
            
            this.attachedImage = file;
            this.showPreview(file);
        }
    }
    
    showPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('image-preview');
            const previewImage = document.getElementById('preview-image');
            
            if (preview && previewImage) {
                previewImage.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(file);
    }
    
    removeImage() {
        this.attachedImage = null;
        const preview = document.getElementById('image-preview');
        const imageInput = document.getElementById('image-input');
        
        if (preview) {
            preview.style.display = 'none';
        }
        if (imageInput) {
            imageInput.value = '';
        }
    }
    
    getAttachedImage() {
        return this.attachedImage;
    }
}

// グローバルインスタンス
const imageAttachment = new ImageAttachment();

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
        const attachedImage = imageAttachment.getAttachedImage();
        
        if (!question && !attachedImage) {
            showNotification('質問を入力するか画像を添付してください', 'warning');
            return;
        }

        // ユーザーメッセージを表示
        this.addMessageToChat('user', question, false, attachedImage);
        questionInput.value = '';

        // ローディング表示
        this.addMessageToChat('ai', '考え中...', true);

        try {
            const formData = new FormData();
            formData.append('question', question);
            formData.append('tag', this.selectedTag);
            
            if (attachedImage) {
                formData.append('image', attachedImage);
            }

            const response = await fetch('/api/ai/consultation', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

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
            
            // 画像をクリア
            imageAttachment.removeImage();
            
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
        
        let messageContent = message;
        
        // AIメッセージの場合はマークダウンをレンダリング
        if (type === 'ai' && !isLoading) {
            messageContent = markdownRenderer.render(message);
        }

        messageDiv.className = `message-container ${messageClass}`;
        messageDiv.innerHTML = `
            <div class="message-bubble ${bubbleClass} ${variantClass}">
                ${isLoading ? '<div class="spinner-border spinner-border-sm me-2"></div>' : `<i class="${icon} me-2"></i>`}
                <div class="${type === 'ai' && !isLoading ? 'markdown-content' : ''}">
                    ${messageContent}
                </div>
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
