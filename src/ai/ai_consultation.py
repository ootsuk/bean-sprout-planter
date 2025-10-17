# 豆苗プランター - AI相談機能

"""
豆苗栽培に特化したAI判断機能
LLM API連携による収穫判断、病気診断、調理例提供
"""

import os
import os
import base64
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from PIL import Image
import io

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
        self.vision_model = None
        
        self._initialize_clients()
        
        # 相談履歴
        self.consultation_history = []
        self.max_history = 100
        
        # 豆苗栽培に特化したプロンプトテンプレート
        self.prompts = {
            'harvest_judgment': """
あなたは豆苗栽培の専門家です。提供された画像とセンサーデータを基に、豆苗の収穫タイミングを判断してください。

センサーデータ:
- 温度: {temperature}°C
- 湿度: {humidity}%
- 土壌水分: {soil_moisture}%

豆苗の成長段階と収穫の目安:
1. 発芽期（1-2日）: 種から芽が出る
2. 初期成長期（3-4日）: 双葉が開く
3. 成長期（5-6日）: 茎が伸びる
4. 収穫期（7-10日）: 高さ10-15cm、葉が開く

以下のキーを持つJSONオブジェクトとして、マークダウン形式で回答してください:
- harvest_ready: boolean (収穫可能か)
- confidence: float (0.0-1.0の信頼度)
- recommendation: string (具体的な推奨事項)
- days_remaining: integer (収穫までの予測日数)
- growth_stage: string (現在の成長段階)
- quality_score: float (1-10の品質スコア)
""",
            'disease_diagnosis': """
あなたは植物病理学の専門家です。提供された画像と症状の情報を基に、豆苗の病気を診断してください。

症状: {symptoms}

豆苗によくある病気:
1. うどんこ病: 葉に白い粉状の斑点
2. 軟腐病: 茎や根が腐る
3. 立枯病: 茎が細くなり倒れる
4. 葉枯病: 葉の先端から枯れる

以下のキーを持つJSONオブジェクトとして、マークダウン形式で回答してください:
- disease_detected: string (病気名または"健康")
- confidence: float (0.0-1.0の信頼度)
- treatment: string (対処法)
- prevention: string (予防法)
- severity: string (mild/moderate/severe)
- affected_area: string (影響範囲)
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

以下のキーを持つJSONオブジェクトとして、マークダウン形式で回答してください:
- recommended_dishes: array of strings (料理名のリスト)
- cooking_tips: string (調理のコツ)
- nutrition_info: string (栄養情報)
- storage_tips: string (保存方法)
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

以下のキーを持つJSONオブジェクトとして、マークダウン形式で回答してください:
- answer: string (具体的な回答)
- confidence: float (0.0-1.0の信頼度)
- related_topics: array of strings (関連トピック)
- next_steps: array of strings (次のステップ)
""",
            'image_consultation': """
あなたは豆苗栽培の専門家です。以下の質問と画像を基に回答してください。

質問: {question}
相談タグ: {tag}

豆苗栽培の基本知識:
- 発芽温度: 20-25°C
- 成長温度: 18-22°C
- 水やり: 1日1-2回
- 光量: 明るい場所、直射日光は避ける
- 収穫時期: 7-10日目

画像を詳しく分析し、豆苗の状態を評価してください。
マークダウン形式で回答し、見出し、リスト、表などを適切に使用してください。

以下のキーを持つJSONオブジェクトとして、マークダウン形式で回答してください:
- answer: string (具体的な回答、マークダウン形式)
- confidence: float (0.0-1.0の信頼度)
- related_topics: array of strings (関連トピック)
- next_steps: array of strings (次のステップ)
"""
        }

    def _initialize_clients(self):
        """APIクライアントを初期化"""
        try:
            # OpenAI
            if os.getenv('OPENAI_API_KEY'):
                self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                self.vision_model = os.getenv('AI_VISION_MODEL', 'gpt-4o')
                self.logger.info(f"OpenAI APIクライアント初期化完了 (Vision: {self.vision_model})")
            
            # Anthropic
            elif os.getenv('ANTHROPIC_API_KEY'):
                self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                self.vision_model = "claude-3-sonnet-20240229"
                self.logger.info(f"Anthropic APIクライアント初期化完了 (Vision: {self.vision_model})")
            
            # Google AI
            elif os.getenv('GOOGLE_AI_API_KEY'):
                genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
                self.google_client = genai.GenerativeModel('gemini-1.5-pro-latest')
                self.vision_model = 'gemini-1.5-pro-latest'
                self.logger.info(f"Google AI APIクライアント初期化完了 (Vision: {self.vision_model})")
                
        except Exception as e:
            self.logger.error(f"APIクライアント初期化エラー: {str(e)}")

    def get_harvest_judgment(self, image_path: str, sensor_data: dict) -> Dict[str, Any]:
        """豆苗の収穫判断を実行"""
        try:
            image_data = self._encode_image(image_path)
            prompt = self.prompts['harvest_judgment'].format(
                temperature=sensor_data.get('temperature', 0),
                humidity=sensor_data.get('humidity', 0),
                soil_moisture=sensor_data.get('soil_moisture', 0)
            )
            response = self._call_ai_api(prompt, "harvest_judgment", image_data=image_data)
            result = self._parse_json_response(response)
            self._add_to_history("harvest_judgment", prompt, result)
            return result
        except Exception as e:
            self.logger.error(f"収穫判断エラー: {str(e)}")
            return {'error': str(e)}

    def diagnose_disease(self, image_path: str, symptoms: List[str]) -> Dict[str, Any]:
        """豆苗の病気診断を実行"""
        try:
            image_data = self._encode_image(image_path)
            prompt = self.prompts['disease_diagnosis'].format(symptoms=', '.join(symptoms))
            response = self._call_ai_api(prompt, "disease_diagnosis", image_data=image_data)
            result = self._parse_json_response(response)
            self._add_to_history("disease_diagnosis", prompt, result)
            return result
        except Exception as e:
            self.logger.error(f"病気診断エラー: {str(e)}")
            return {'error': str(e)}

    def get_cooking_suggestions(self, harvest_data: dict) -> Dict[str, Any]:
        """収穫した豆苗の調理例を提供"""
        try:
            prompt = self.prompts['cooking_suggestions'].format(
                harvest_amount=harvest_data.get('amount', 0),
                quality=harvest_data.get('quality', 'good'),
                growth_days=harvest_data.get('growth_days', 7)
            )
            response = self._call_ai_api(prompt, "cooking_suggestions")
            result = self._parse_json_response(response)
            self._add_to_history("cooking_suggestions", prompt, result)
            return result
        except Exception as e:
            self.logger.error(f"調理例取得エラー: {str(e)}")
            return {'error': str(e)}

    def consult(self, question: str, tag: str = "general", image_data: str = None) -> Dict[str, Any]:
        """一般相談を実行"""
        try:
            if image_data:
                prompt = self.prompts['image_consultation'].format(question=question, tag=tag)
            else:
                prompt = self.prompts['general_consultation'].format(question=question, tag=tag)

            response = self._call_ai_api(prompt, "general_consultation", image_data=image_data)
            result = self._parse_json_response(response, is_markdown=True if image_data else False)
            self._add_to_history("general_consultation", prompt, result)
            return result
        except Exception as e:
            self.logger.error(f"一般相談エラー: {str(e)}")
            return {'error': str(e)}
    
    def _encode_image(self, image_path: str) -> Optional[str]:
        """画像をBase64エンコード"""
        try:
            if not os.path.exists(image_path):
                self.logger.warning(f"画像ファイルが見つかりません: {image_path}")
                return None

            with Image.open(image_path) as image:
                image.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=85)
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            self.logger.error(f"画像エンコードエラー: {str(e)}")
            return None

    def _call_ai_api(self, prompt: str, task_type: str, image_data: Optional[str] = None) -> str:
        """AI APIを呼び出し（マルチモーダル対応）"""
        try:
            max_tokens = int(os.getenv('AI_MAX_TOKENS', 1500))

            if self.openai_client:
                messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
                if image_data:
                    messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})

                response = self.openai_client.chat.completions.create(
                    model=self.vision_model,
                    messages=messages,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content
            
            elif self.anthropic_client:
                messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
                if image_data:
                    messages[0]["content"].insert(0, {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}})

                response = self.anthropic_client.messages.create(
                    model=self.vision_model,
                    max_tokens=max_tokens,
                    messages=messages
                )
                return response.content[0].text

            elif self.google_client:
                content = [prompt]
                if image_data:
                    image_part = {"mime_type": "image/jpeg", "data": base64.b64decode(image_data)}
                    content.insert(0, image_part)

                response = self.google_client.generate_content(content)
                return response.text
            
            else:
                raise Exception("利用可能なAI APIがありません")
                
        except Exception as e:
            self.logger.error(f"AI API呼び出しエラー: {str(e)}")
            raise e

    def _parse_json_response(self, response: str, is_markdown: bool = False) -> Dict[str, Any]:
        """AIからのJSONレスポンスをパース"""
        try:
            # マークダウンのコードブロックを削除
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()

            if is_markdown:
                # マークダウン形式の回答をそのまま返す
                return json.loads(response)

            return json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSONパースエラー: {e}. レスポンス: {response}")
            return {'error': 'AIの応答を解析できませんでした', 'raw_response': response}
        except Exception as e:
            self.logger.error(f"レスポンス解析エラー: {str(e)}")
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



