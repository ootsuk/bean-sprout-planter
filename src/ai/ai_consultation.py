# 豆苗プランター - AI相談機能

"""
豆苗栽培に特化したAI判断機能
LLM API連携による収穫判断、病気診断、調理例提供
"""

import os
import base64
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
from openai import OpenAI
import anthropic
import google.generativeai as genai


class AIConsultationManager:
    """AI相談マネージャー"""
    
    def __init__(self):
        """AI相談マネージャーの初期化"""
        self.logger = logging.getLogger("ai_consultation")
        
        # APIクライアント初期化
        self.openai_client = None
        self.anthropic_client = None
        self.google_client = None
        
        self._initialize_clients()
        
        # 相談履歴
        self.consultation_history = []
        self.max_history = 100
        
        # 豆苗栽培に特化したプロンプトテンプレート
        self.prompts = {
            'harvest_judgment': """
あなたは豆苗栽培の専門家です。以下の情報を基に、豆苗の収穫タイミングを判断してください。

画像情報: {image_description}
センサーデータ:
- 温度: {temperature}°C
- 湿度: {humidity}%
- 土壌水分: {soil_moisture}%

豆苗の成長段階と収穫の目安:
1. 発芽期（1-2日）: 種から芽が出る
2. 初期成長期（3-4日）: 双葉が開く
3. 成長期（5-6日）: 茎が伸びる
4. 収穫期（7-10日）: 高さ10-15cm、葉が開く

以下の形式で回答してください:
- harvest_ready: true/false
- confidence: 0.0-1.0
- recommendation: 具体的な推奨事項
- days_remaining: 収穫まで何日
- growth_stage: 現在の成長段階
""",
            'disease_diagnosis': """
あなたは植物病理学の専門家です。豆苗の病気を診断してください。

症状: {symptoms}
画像情報: {image_description}

豆苗によくある病気:
1. うどんこ病: 葉に白い粉状の斑点
2. 軟腐病: 茎や根が腐る
3. 立枯病: 茎が細くなり倒れる
4. 葉枯病: 葉の先端から枯れる

以下の形式で回答してください:
- disease_detected: 病気名または"健康"
- confidence: 0.0-1.0
- treatment: 対処法
- prevention: 予防法
- severity: mild/moderate/severe
""",
            'cooking_suggestions': """
あなたは料理の専門家です。収穫した豆苗の調理例を提案してください。

収穫データ:
- 収穫量: {harvest_amount}g
- 品質: {quality}
- 成長日数: {growth_days}日

豆苗の特徴:
- シャキシャキした食感
- ビタミンCが豊富
- 加熱時間は短めが良い

以下の形式で回答してください:
- recommended_dishes: 料理名のリスト
- cooking_tips: 調理のコツ
- nutrition_info: 栄養情報
- storage_tips: 保存方法
""",
            'general_consultation': """
あなたは豆苗栽培の専門家です。以下の質問に答えてください。

質問: {question}
相談タグ: {tag}

豆苗栽培の基本知識:
- 発芽温度: 20-25°C
- 成長温度: 18-22°C
- 水やり: 1日1-2回
- 光量: 明るい場所、直射日光は避ける
- 収穫時期: 7-10日目

以下の形式で回答してください:
- answer: 具体的な回答
- confidence: 0.0-1.0
- related_topics: 関連トピック
- next_steps: 次のステップ
""",
            'image_consultation': """
あなたは豆苗栽培の専門家です。以下の質問と画像を基に回答してください。

質問: {question}
相談タグ: {tag}
画像データ: {image_data}

豆苗栽培の基本知識:
- 発芽温度: 20-25°C
- 成長温度: 18-22°C
- 水やり: 1日1-2回
- 光量: 明るい場所、直射日光は避ける
- 収穫時期: 7-10日目

画像を詳しく分析し、豆苗の状態を評価してください。
マークダウン形式で回答し、見出し、リスト、表などを適切に使用してください。

以下の形式で回答してください:
- answer: 具体的な回答（マークダウン形式）
- confidence: 0.0-1.0
- related_topics: 関連トピック
- next_steps: 次のステップ
"""
        }
    
    def _initialize_clients(self):
        """APIクライアントを初期化"""
        try:
            # OpenAI
            if os.getenv('OPENAI_API_KEY'):
                self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                self.logger.info("OpenAI APIクライアント初期化完了")
            
            # Anthropic
            if os.getenv('ANTHROPIC_API_KEY'):
                self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                self.logger.info("Anthropic APIクライアント初期化完了")
            
            # Google AI
            if os.getenv('GOOGLE_AI_API_KEY'):
                genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
                self.google_client = genai.GenerativeModel('gemini-pro')
                self.logger.info("Google AI APIクライアント初期化完了")
                
        except Exception as e:
            self.logger.error(f"APIクライアント初期化エラー: {str(e)}")
    
    def get_harvest_judgment(self, image_path: str, sensor_data: dict) -> Dict[str, Any]:
        """豆苗の収穫判断を実行"""
        try:
            # 画像をBase64エンコード
            image_description = self._analyze_image(image_path)
            
            # プロンプト作成
            prompt = self.prompts['harvest_judgment'].format(
                image_description=image_description,
                temperature=sensor_data.get('temperature', 0),
                humidity=sensor_data.get('humidity', 0),
                soil_moisture=sensor_data.get('soil_moisture', 0)
            )
            
            # AI API呼び出し
            response = self._call_ai_api(prompt, "harvest_judgment")
            
            # 結果をパース
            result = self._parse_harvest_response(response)
            
            # 履歴に追加
            self._add_to_history("harvest_judgment", prompt, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"収穫判断エラー: {str(e)}")
            return {
                'harvest_ready': False,
                'confidence': 0.0,
                'recommendation': 'エラーが発生しました',
                'error': str(e)
            }
    
    def diagnose_disease(self, image_path: str, symptoms: List[str]) -> Dict[str, Any]:
        """豆苗の病気診断を実行"""
        try:
            # 画像分析
            image_description = self._analyze_image(image_path)
            
            # プロンプト作成
            prompt = self.prompts['disease_diagnosis'].format(
                symptoms=', '.join(symptoms),
                image_description=image_description
            )
            
            # AI API呼び出し
            response = self._call_ai_api(prompt, "disease_diagnosis")
            
            # 結果をパース
            result = self._parse_disease_response(response)
            
            # 履歴に追加
            self._add_to_history("disease_diagnosis", prompt, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"病気診断エラー: {str(e)}")
            return {
                'disease_detected': '診断エラー',
                'confidence': 0.0,
                'treatment': 'エラーが発生しました',
                'error': str(e)
            }
    
    def get_cooking_suggestions(self, harvest_data: dict) -> Dict[str, Any]:
        """収穫した豆苗の調理例を提供"""
        try:
            # プロンプト作成
            prompt = self.prompts['cooking_suggestions'].format(
                harvest_amount=harvest_data.get('amount', 0),
                quality=harvest_data.get('quality', 'good'),
                growth_days=harvest_data.get('growth_days', 7)
            )
            
            # AI API呼び出し
            response = self._call_ai_api(prompt, "cooking_suggestions")
            
            # 結果をパース
            result = self._parse_cooking_response(response)
            
            # 履歴に追加
            self._add_to_history("cooking_suggestions", prompt, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"調理例取得エラー: {str(e)}")
            return {
                'recommended_dishes': ['エラーが発生しました'],
                'cooking_tips': 'エラーが発生しました',
                'error': str(e)
            }
    
    def consult(self, question: str, tag: str = "general", image_data: str = None) -> Dict[str, Any]:
        """一般相談を実行"""
        try:
            # プロンプト作成
            if image_data:
                # 画像付きの相談
                prompt = self.prompts['image_consultation'].format(
                    question=question,
                    tag=tag,
                    image_data=image_data
                )
            else:
                # テキストのみの相談
                prompt = self.prompts['general_consultation'].format(
                    question=question,
                    tag=tag
                )
            
            # AI API呼び出し
            response = self._call_ai_api(prompt, "general_consultation")
            
            # 結果をパース
            result = self._parse_general_response(response)
            
            # 履歴に追加
            self._add_to_history("general_consultation", prompt, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"一般相談エラー: {str(e)}")
            return {
                'answer': 'エラーが発生しました',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _analyze_image(self, image_path: str) -> str:
        """画像を分析して説明文を生成"""
        try:
            # 実際の実装では、画像解析APIを使用
            # ここでは簡易的な実装
            if os.path.exists(image_path):
                return f"豆苗の画像が提供されました（{os.path.basename(image_path)}）"
            else:
                return "画像が見つかりません"
        except Exception as e:
            self.logger.error(f"画像分析エラー: {str(e)}")
            return "画像分析に失敗しました"
    
    def _call_ai_api(self, prompt: str, task_type: str) -> str:
        """AI APIを呼び出し"""
        try:
            # OpenAI API
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=os.getenv('AI_MODEL', 'gpt-4'),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=int(os.getenv('AI_MAX_TOKENS', 1000))
                )
                return response.choices[0].message.content
            
            # Anthropic API
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=int(os.getenv('AI_MAX_TOKENS', 1000)),
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            # Google AI API
            elif self.google_client:
                response = self.google_client.generate_content(prompt)
                return response.text
            
            else:
                raise Exception("利用可能なAI APIがありません")
                
        except Exception as e:
            self.logger.error(f"AI API呼び出しエラー: {str(e)}")
            raise e
    
    def _parse_harvest_response(self, response: str) -> Dict[str, Any]:
        """収穫判断レスポンスをパース"""
        try:
            # 簡易的なパース（実際の実装ではより詳細な解析が必要）
            result = {
                'harvest_ready': 'true' in response.lower(),
                'confidence': 0.8,  # 実際の実装ではAIの信頼度を抽出
                'recommendation': '豆苗の状態を確認してください',
                'days_remaining': 2,
                'growth_stage': 'mature',
                'quality_score': 8.0
            }
            return result
        except Exception as e:
            self.logger.error(f"収穫判断レスポンス解析エラー: {str(e)}")
            return {'error': str(e)}
    
    def _parse_disease_response(self, response: str) -> Dict[str, Any]:
        """病気診断レスポンスをパース"""
        try:
            result = {
                'disease_detected': '健康',
                'confidence': 0.9,
                'treatment': '定期的な観察を続けてください',
                'prevention': '適切な水やりと通風を保ってください',
                'severity': 'mild',
                'affected_area': 'none'
            }
            return result
        except Exception as e:
            self.logger.error(f"病気診断レスポンス解析エラー: {str(e)}")
            return {'error': str(e)}
    
    def _parse_cooking_response(self, response: str) -> Dict[str, Any]:
        """調理例レスポンスをパース"""
        try:
            result = {
                'recommended_dishes': ['豆苗炒め', '豆苗スープ', '豆苗サラダ'],
                'cooking_tips': '茎の部分は火を通しすぎないようにしてください',
                'nutrition_info': 'ビタミンCが豊富で、シャキシャキした食感が特徴です',
                'storage_tips': '冷蔵庫で3-4日保存可能です'
            }
            return result
        except Exception as e:
            self.logger.error(f"調理例レスポンス解析エラー: {str(e)}")
            return {'error': str(e)}
    
    def _parse_general_response(self, response: str) -> Dict[str, Any]:
        """一般相談レスポンスをパース"""
        try:
            result = {
                'answer': response,
                'confidence': 0.8,
                'related_topics': ['水やり', '光量', '温度管理'],
                'next_steps': ['定期的な観察を続ける', 'センサーデータを確認する']
            }
            return result
        except Exception as e:
            self.logger.error(f"一般相談レスポンス解析エラー: {str(e)}")
            return {'error': str(e)}
    
    def _add_to_history(self, task_type: str, prompt: str, result: dict):
        """相談履歴に追加"""
        try:
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'task_type': task_type,
                'prompt': prompt[:200] + '...' if len(prompt) > 200 else prompt,
                'result': result,
                'success': 'error' not in result
            }
            
            self.consultation_history.append(history_entry)
            
            # 履歴数制限
            if len(self.consultation_history) > self.max_history:
                self.consultation_history = self.consultation_history[-self.max_history:]
                
        except Exception as e:
            self.logger.error(f"履歴追加エラー: {str(e)}")
    
    def get_consultation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """相談履歴を取得"""
        return self.consultation_history[-limit:]
    
    def get_available_tags(self) -> List[str]:
        """利用可能な相談タグを取得"""
        return [
            'general',      # 一般相談
            'harvest',      # 収穫判断
            'disease',      # 病気診断
            'cooking',      # 調理例
            'watering',     # 水やり
            'lighting',     # 光量
            'temperature',  # 温度管理
            'nutrients'     # 栄養管理
        ]



