# 豆苗プランター - Flaskアプリケーション

"""
Flaskアプリケーションのメインファイル
画面表示ルートのみを定義（APIは src/api/ に分離）
"""

from flask import Flask, render_template
import os
import logging


def create_app():
    """Flaskアプリケーションを作成・設定"""
    
    # テンプレートディレクトリを指定
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'web', 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'web', 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # 設定
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # ========================================
    # テンプレート変数（ナビゲーションデータ）
    # ========================================
    
    @app.context_processor
    def inject_navbar_data():
        """ナビゲーションバーのデータをテンプレートに注入"""
        return {
            'navbar_items': [
                {'name': 'ダッシュボード', 'url': '/', 'icon': 'fas fa-tachometer-alt', 'key': 'dashboard'},
                {'name': 'AI相談チャット', 'url': '/ai-consultation', 'icon': 'fas fa-robot', 'key': 'ai-consultation'},
                {'name': 'カメラ管理', 'url': '/multi-camera', 'icon': 'fas fa-camera', 'key': 'multi-camera'},
                {'name': '給水タンク', 'url': '/water-tank', 'icon': 'fas fa-tint', 'key': 'water-tank'},
                {'name': '成長記録', 'url': '/records', 'icon': 'fas fa-chart-line', 'key': 'records'},
                {'name': 'システムログ', 'url': '/logs', 'icon': 'fas fa-file-alt', 'key': 'logs'},
                {'name': 'システム設定', 'url': '/settings', 'icon': 'fas fa-cog', 'key': 'settings'},
            ]
        }
    
    # ========================================
    # 画面表示ルート（HTMLページ）
    # ========================================
    

    

    
    @app.route('/')
    def dashboard():
        """ダッシュボードページ"""
        return render_template('dashboard.html')
    

    
    @app.route('/settings')
    def settings():
        """設定ページ"""
        return render_template('settings.html')
    
    @app.route('/ai-consultation')
    def ai_consultation():
        """AI相談ページ（豆苗プラン特有）"""
        return render_template('ai_consultation.html')
    
    @app.route('/multi-camera')
    def multi_camera():
        """多層化カメラ管理ページ（豆苗プラン特有）"""
        return render_template('multi_camera.html')
    
    @app.route('/water-tank')
    def water_tank():
        """給水タンク管理ページ（豆苗プラン特有）"""
        return render_template('water_tank.html')
    
    @app.route('/logs')
    def logs():
        """ログページ"""
        return render_template('logs.html')
    
    # ========================================
    # エラーハンドラー
    # ========================================
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app



