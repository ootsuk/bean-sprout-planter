# 豆苗プランター - スケジューラー管理モジュール

"""
APSchedulerを使用したジョブスケジューリング管理
- センサー収集
- 給水チェック
- カメラ撮影
- 設定変更時の動的再スケジュール
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import atexit
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SchedulerManager:
    """スケジューラー管理クラス"""
    
    def __init__(self):
        self.scheduler = None
        self.data_manager = None
        self.sensor_manager = None
        self.watering_manager = None
        self.camera_manager = None
        self._initialized = False
        
    def initialize(self, data_manager, sensor_manager=None, watering_manager=None, camera_manager=None):
        """スケジューラーを初期化"""
        try:
            self.data_manager = data_manager
            self.sensor_manager = sensor_manager
            self.watering_manager = watering_manager
            self.camera_manager = camera_manager
            
            # ジョブストア設定（SQLite）
            jobstores = {
                'default': SQLAlchemyJobStore(url='sqlite:///data/scheduler.db')
            }
            
            # エグゼキューター設定
            executors = {
                'default': ThreadPoolExecutor(max_workers=10)
            }
            
            # スケジューラー設定
            job_defaults = {
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 30
            }
            
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='Asia/Tokyo'
            )
            
            # イベントリスナー追加
            self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
            
            # スケジューラー開始
            self.scheduler.start()
            
            # 既存の設定からジョブを登録
            self.schedule_all()
            
            # 終了時のクリーンアップ
            atexit.register(self.shutdown)
            
            self._initialized = True
            logger.info("スケジューラー初期化完了")
            
        except Exception as e:
            logger.error(f"スケジューラー初期化エラー: {e}")
            raise
    
    def schedule_all(self):
        """設定に基づいて全ジョブをスケジュール"""
        try:
            if not self._initialized:
                logger.warning("スケジューラーが初期化されていません")
                return
            
            # 既存のジョブを削除
            self.scheduler.remove_all_jobs()
            
            # 設定を取得
            settings = self.data_manager.get_settings()
            
            # センサー収集ジョブ
            self._schedule_sensor_jobs(settings.get('sensors', {}))
            
            # 給水チェックジョブ
            self._schedule_watering_jobs(settings.get('watering', {}))
            
            # カメラ撮影ジョブ
            self._schedule_camera_jobs(settings.get('camera', {}))
            
            logger.info("全ジョブのスケジュール完了")
            
        except Exception as e:
            logger.error(f"ジョブスケジュールエラー: {e}")
    
    def reschedule_all(self):
        """設定変更時に全ジョブを再スケジュール"""
        logger.info("設定変更を検出、ジョブを再スケジュールします")
        self.schedule_all()
    
    def _schedule_sensor_jobs(self, sensor_config: Dict[str, Any]):
        """センサー収集ジョブをスケジュール"""
        if not self.sensor_manager:
            logger.warning("センサーマネージャーが設定されていません")
            return
        
        # 全センサー収集ジョブ
        check_interval = sensor_config.get('check_interval', 60)
        self.scheduler.add_job(
            func=self._sensor_collection_job,
            trigger=IntervalTrigger(seconds=check_interval),
            id='sensor_collection',
            name='センサー収集',
            replace_existing=True
        )
        
        # 個別センサー収集（必要に応じて）
        temp_humidity_interval = sensor_config.get('temperature_humidity_interval', 1800)
        if temp_humidity_interval != check_interval:
            self.scheduler.add_job(
                func=self._temperature_humidity_job,
                trigger=IntervalTrigger(seconds=temp_humidity_interval),
                id='temperature_humidity',
                name='温湿度センサー',
                replace_existing=True
            )
        
        soil_moisture_interval = sensor_config.get('water_pressure_interval', 300)
        if soil_moisture_interval != check_interval:
            self.scheduler.add_job(
                func=self._water_pressure_job,
                trigger=IntervalTrigger(seconds=soil_moisture_interval),
                id='water_pressure',
                name='水圧センサー',
                replace_existing=True
            )
    
    def _schedule_watering_jobs(self, watering_config: Dict[str, Any]):
        """給水チェックジョブをスケジュール"""
        if not self.watering_manager:
            logger.warning("給水マネージャーが設定されていません")
            return
        
        watering_interval_hours = watering_config.get('watering_interval_hours', 12)
        self.scheduler.add_job(
            func=self._watering_check_job,
            trigger=IntervalTrigger(hours=watering_interval_hours),
            id='watering_check',
            name='給水チェック',
            replace_existing=True
        )
    
    def _schedule_camera_jobs(self, camera_config: Dict[str, Any]):
        """カメラ撮影ジョブをスケジュール"""
        if not self.camera_manager:
            logger.warning("カメラマネージャーが設定されていません")
            return
        
        auto_capture_time = camera_config.get('auto_capture_time', '06:00')
        hour, minute = map(int, auto_capture_time.split(':'))
        
        self.scheduler.add_job(
            func=self._camera_capture_job,
            trigger=CronTrigger(hour=hour, minute=minute),
            id='camera_capture',
            name='カメラ自動撮影',
            replace_existing=True
        )
    
    def _sensor_collection_job(self):
        """センサー収集ジョブ実行"""
        try:
            logger.info("センサー収集ジョブ実行")
            if self.sensor_manager:
                self.sensor_manager.read_all_sensors_once()
        except Exception as e:
            logger.error(f"センサー収集ジョブエラー: {e}")
    
    def _temperature_humidity_job(self):
        """温湿度センサージョブ実行"""
        try:
            logger.info("温湿度センサージョブ実行")
            if self.sensor_manager:
                self.sensor_manager.read_temperature_humidity_once()
        except Exception as e:
            logger.error(f"温湿度センサージョブエラー: {e}")
    
    def _water_pressure_job(self):
        """水圧センサージョブ実行"""
        try:
            logger.info("水圧センサージョブ実行")
            if self.sensor_manager:
                # TODO: 水圧センサーの読み取りメソッドを実装
                logger.warning("水圧センサーの読み取りメソッドは未実装です")
        except Exception as e:
            logger.error(f"水圧センサージョブエラー: {e}")
    
    def _watering_check_job(self):
        """給水チェックジョブ実行"""
        try:
            logger.info("給水チェックジョブ実行")
            if self.watering_manager:
                self.watering_manager.evaluate_and_water_once()
        except Exception as e:
            logger.error(f"給水チェックジョブエラー: {e}")
    
    def _camera_capture_job(self):
        """カメラ撮影ジョブ実行"""
        try:
            logger.info("カメラ撮影ジョブ実行")
            if self.camera_manager:
                self.camera_manager.capture_once()
        except Exception as e:
            logger.error(f"カメラ撮影ジョブエラー: {e}")
    
    def _job_listener(self, event):
        """ジョブ実行イベントリスナー"""
        if event.exception:
            logger.error(f"ジョブ実行エラー: {event.job_id} - {event.exception}")
        else:
            logger.debug(f"ジョブ実行完了: {event.job_id}")
    
    def get_job_status(self) -> Dict[str, Any]:
        """ジョブの状態を取得"""
        if not self._initialized:
            return {"error": "スケジューラーが初期化されていません"}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "scheduler_running": self.scheduler.running,
            "jobs": jobs
        }
    
    def shutdown(self):
        """スケジューラーを停止"""
        if self.scheduler and self.scheduler.running:
            logger.info("スケジューラーを停止します")
            self.scheduler.shutdown(wait=True)
            logger.info("スケジューラー停止完了")


# グローバルインスタンス
scheduler_manager = SchedulerManager()

