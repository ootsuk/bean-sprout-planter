# 豆苗プランター - AI相談API

"""
AI相談機能のRESTful API
収穫判断、病気診断、調理例、一般相談を提供
"""

from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
from src.ai.ai_consultation import AIConsultationManager
import logging
import base64
from PIL import Image
import io

# ブループリント作成
ai_bp = Blueprint('ai', __name__)
api = Api(ai_bp)

# AI相談マネージャーのインスタンス
ai_manager = AIConsultationManager()


class AIConsultationResource(Resource):
    """AI相談API"""
    
    def post(self):
        """AI相談を実行"""
        try:
            # フォームデータまたはJSONデータを処理
            if request.content_type and 'multipart/form-data' in request.content_type:
                # 画像付きのリクエスト
                question = request.form.get('question', '')
                tag = request.form.get('tag', 'general')
                image_file = request.files.get('image')
                
                if not question and not image_file:
                    return {'error': '質問または画像が必要です'}, 400
                
                # 画像がある場合はBase64エンコード
                image_data = None
                if image_file:
                    try:
                        image = Image.open(image_file)
                        # 画像をリサイズ（最大1024px）
                        image.thumbnail((1024, 1024))
                        
                        buffer = io.BytesIO()
                        image.save(buffer, format='JPEG', quality=85)
                        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    except Exception as img_error:
                        logging.error(f"画像処理エラー: {str(img_error)}")
                        return {'error': '画像の処理に失敗しました'}, 400
                
                # AI相談を実行（画像付き）
                result = ai_manager.consult(question, tag, image_data)
                
            else:
                # JSONリクエスト
                data = request.get_json()
                if not data:
                    return {'error': 'リクエストボディが必要です'}, 400
                
                question = data.get('question')
                tag = data.get('tag', 'general')
                
                if not question:
                    return {'error': '質問内容が必要です'}, 400
                
                # AI相談を実行
                result = ai_manager.consult(question, tag)
            
            return {
                'status': 'success',
                'answer': result.get('answer', '回答を生成できませんでした'),
                'confidence': result.get('confidence', 0.0),
                'tag': tag,
                'related_topics': result.get('related_topics', []),
                'next_steps': result.get('next_steps', [])
            }
            
        except Exception as e:
            logging.error(f"AI相談エラー: {str(e)}")
            return {'error': f'AI相談エラー: {str(e)}'}, 500


class HarvestJudgmentResource(Resource):
    """収穫判断API"""
    
    def post(self):
        """収穫判断を実行"""
        try:
            # 最新の画像とセンサーデータを取得（モック）
            image_path = "plant_images/latest.jpg"  # 実際の実装では最新画像を取得
            sensor_data = {
                'temperature': 22.5,
                'humidity': 65.0,
                'soil_moisture': 45.0
            }
            
            # AI判断を実行
            judgment = ai_manager.get_harvest_judgment(image_path, sensor_data)
            
            return {
                'status': 'success',
                'harvest_ready': judgment.get('harvest_ready', False),
                'confidence': judgment.get('confidence', 0.0),
                'recommendation': judgment.get('recommendation', ''),
                'days_remaining': judgment.get('days_remaining', 0),
                'growth_stage': judgment.get('growth_stage', 'unknown'),
                'quality_score': judgment.get('quality_score', 0.0)
            }
            
        except Exception as e:
            logging.error(f"収穫判断エラー: {str(e)}")
            return {'error': f'収穫判断エラー: {str(e)}'}, 500


class DiseaseCheckResource(Resource):
    """病気診断API"""
    
    def post(self):
        """病気診断を実行"""
        try:
            data = request.get_json()
            if not data:
                return {'error': 'リクエストボディが必要です'}, 400
            
            symptoms = data.get('symptoms', [])
            image_path = "plant_images/latest.jpg"  # 実際の実装では最新画像を取得
            
            # 病気診断を実行
            diagnosis = ai_manager.diagnose_disease(image_path, symptoms)
            
            return {
                'status': 'success',
                'disease_detected': diagnosis.get('disease_detected', '健康'),
                'confidence': diagnosis.get('confidence', 0.0),
                'treatment': diagnosis.get('treatment', ''),
                'prevention': diagnosis.get('prevention', ''),
                'severity': diagnosis.get('severity', 'mild'),
                'affected_area': diagnosis.get('affected_area', 'none')
            }
            
        except Exception as e:
            logging.error(f"病気診断エラー: {str(e)}")
            return {'error': f'病気診断エラー: {str(e)}'}, 500


class CookingTipsResource(Resource):
    """調理例API"""
    
    def post(self):
        """調理例を提供"""
        try:
            data = request.get_json()
            if not data:
                return {'error': 'リクエストボディが必要です'}, 400
            
            harvest_data = {
                'amount': data.get('harvest_amount', 200),
                'quality': data.get('harvest_quality', 'good'),
                'growth_days': data.get('growth_days', 7)
            }
            
            # 調理例を取得
            cooking_suggestions = ai_manager.get_cooking_suggestions(harvest_data)
            
            return {
                'status': 'success',
                'recommended_dishes': cooking_suggestions.get('recommended_dishes', []),
                'cooking_tips': cooking_suggestions.get('cooking_tips', ''),
                'nutrition_info': cooking_suggestions.get('nutrition_info', ''),
                'storage_tips': cooking_suggestions.get('storage_tips', '')
            }
            
        except Exception as e:
            logging.error(f"調理例取得エラー: {str(e)}")
            return {'error': f'調理例取得エラー: {str(e)}'}, 500


class AITagsResource(Resource):
    """AI相談タグ一覧API"""
    
    def get(self):
        """利用可能な相談タグを取得"""
        try:
            tags = ai_manager.get_available_tags()
            return {
                'status': 'success',
                'tags': tags,
                'descriptions': {
                    'general': '一般相談',
                    'harvest': '収穫判断',
                    'disease': '病気診断',
                    'cooking': '調理例',
                    'watering': '水やり',
                    'lighting': '光量',
                    'temperature': '温度管理',
                    'nutrients': '栄養管理'
                }
            }
            
        except Exception as e:
            logging.error(f"タグ取得エラー: {str(e)}")
            return {'error': f'タグ取得エラー: {str(e)}'}, 500


class AIConsultationHistoryResource(Resource):
    """AI相談履歴API"""
    
    def get(self):
        """相談履歴を取得"""
        try:
            limit = request.args.get('limit', 10, type=int)
            history = ai_manager.get_consultation_history(limit)
            
            return {
                'status': 'success',
                'history': history,
                'count': len(history)
            }
            
        except Exception as e:
            logging.error(f"履歴取得エラー: {str(e)}")
            return {'error': f'履歴取得エラー: {str(e)}'}, 500


# APIエンドポイントを登録
api.add_resource(AIConsultationResource, '/consultation')
api.add_resource(HarvestJudgmentResource, '/harvest-judgment')
api.add_resource(DiseaseCheckResource, '/disease-check')
api.add_resource(CookingTipsResource, '/cooking-tips')
api.add_resource(AITagsResource, '/tags')
api.add_resource(AIConsultationHistoryResource, '/history')
