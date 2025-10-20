// 成長記録ページ用JavaScript

document.addEventListener('DOMContentLoaded', function() {
    let currentDate = new Date();
    let selectedDate = null;
    
    // カレンダー初期化
    initCalendar();
    
    // イベントリスナー
    document.getElementById('prevMonth').addEventListener('click', function() {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });
    
    document.getElementById('nextMonth').addEventListener('click', function() {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });
    
    function initCalendar() {
        renderCalendar();
    }
    
    function renderCalendar() {
        const calendarGrid = document.getElementById('calendarGrid');
        const calendarTitle = document.getElementById('calendarTitle');
        
        // タイトル更新
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth() + 1;
        calendarTitle.textContent = `${year}年${month}月`;
        
        // カレンダーグリッドをクリア
        calendarGrid.innerHTML = '';
        
        // 曜日ヘッダー
        const dayHeaders = ['日', '月', '火', '水', '木', '金', '土'];
        dayHeaders.forEach(day => {
            const dayHeader = document.createElement('div');
            dayHeader.className = 'calendar-day-header';
            dayHeader.textContent = day;
            calendarGrid.appendChild(dayHeader);
        });
        
        // 月の最初の日
        const firstDay = new Date(year, month - 1, 1);
        const lastDay = new Date(year, month, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());
        
        // 6週間分の日付を生成
        for (let i = 0; i < 42; i++) {
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + i);
            
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            dayElement.textContent = date.getDate();
            
            // 現在の月以外の日付
            if (date.getMonth() !== month - 1) {
                dayElement.classList.add('other-month');
            }
            
            // データがある日付（サンプル）
            if (hasDataForDate(date)) {
                dayElement.classList.add('has-data');
            }
            
            // クリックイベント
            dayElement.addEventListener('click', function() {
                if (date.getMonth() === month - 1) {
                    selectDate(date);
                }
            });
            
            calendarGrid.appendChild(dayElement);
        }
    }
    
    function hasDataForDate(date) {
        // サンプルデータ：10月の15日、20日、25日にデータがある
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return month === 10 && (day === 15 || day === 20 || day === 25);
    }
    
    function selectDate(date) {
        selectedDate = date;
        
        // カレンダーの選択状態を更新
        document.querySelectorAll('.calendar-day').forEach(day => {
            day.classList.remove('selected');
        });
        
        event.target.classList.add('selected');
        
        // 詳細表示を更新
        showDateDetails(date);
    }
    
    function showDateDetails(date) {
        const selectedDateElement = document.getElementById('selectedDate');
        const dateDetailsElement = document.getElementById('dateDetails');
        
        // 日付表示
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const dayOfWeek = ['日', '月', '火', '水', '木', '金', '土'][date.getDay()];
        
        selectedDateElement.textContent = `${year}年${month}月${day}日 (${dayOfWeek})`;
        
        // 詳細データを表示
        const template = document.getElementById('dateDetailTemplate');
        const clone = template.content.cloneNode(true);
        
        // サンプルデータを設定
        updateSampleData(clone, date);
        
        dateDetailsElement.innerHTML = '';
        dateDetailsElement.appendChild(clone);
        
        // 気温チャートを描画
        drawTemperatureChart();
    }
    
    function updateSampleData(element, date) {
        // サンプルデータの更新
        const day = date.getDate();
        
        // 気温データ
        element.querySelector('#maxTemp').textContent = `${20 + (day % 10)}°C`;
        element.querySelector('#minTemp').textContent = `${15 + (day % 8)}°C`;
        element.querySelector('#avgTemp').textContent = `${17.5 + (day % 6)}°C`;
    }
    
    function drawTemperatureChart() {
        const canvas = document.getElementById('temperatureChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // サンプルデータ
        const hours = [0, 6, 12, 18, 24];
        const temperatures = [18, 16, 25, 22, 20];
        
        // チャート描画（簡易版）
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // グリッド線
        ctx.strokeStyle = '#e9ecef';
        ctx.lineWidth = 1;
        
        for (let i = 0; i <= 4; i++) {
            const y = (canvas.height / 4) * i;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        }
        
        // 温度線
        ctx.strokeStyle = '#dc3545';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        temperatures.forEach((temp, index) => {
            const x = (canvas.width / (temperatures.length - 1)) * index;
            const y = canvas.height - ((temp - 15) / 10) * canvas.height;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
        
        // データポイント
        ctx.fillStyle = '#dc3545';
        temperatures.forEach((temp, index) => {
            const x = (canvas.width / (temperatures.length - 1)) * index;
            const y = canvas.height - ((temp - 15) / 10) * canvas.height;
            
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fill();
        });
    }
});
