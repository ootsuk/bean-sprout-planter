# 豆苗プランター - メインアプリケーション

"""
豆苗栽培に特化した自動植物育成システム
メインエントリーポイント
"""

import os
import sys
import logging
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.app.app import create_app
from src.api.api_blueprint import register_api_blueprints
from src.utils.logger import setup_logging


def main():
    """メイン実行関数"""
    
    # ログ設定
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🌱 豆苗プランター起動中...")
        
        # Flaskアプリケーション作成
        app = create_app()
        
        # APIブループリントを登録
        register_api_blueprints(app)
        
        # アプリケーション実行
        app.run(
            host='0.0.0.0',
            port=8080,
            debug=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️ アプリケーション停止")
    except Exception as e:
        logger.error(f"❌ アプリケーションエラー: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()



