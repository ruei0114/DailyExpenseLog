import sqlite3 as lite
import copy
from flask import Flask, request, render_template, jsonify
from functools import wraps

# Composition 結構：FinanceApp 擁有 DataProcessor
class DataProcessor:
    def sort_by_amount(self, data: list[dict]) -> list[dict]:
        return sorted(data, key=lambda x: x['amount'])

class BaseApp:
    def __init__(self):
        self.app = Flask(__name__)

    def run(self):
        self.app.debug = True
        self.app.run()

class FinanceApp(BaseApp):
    def __init__(self):
        super().__init__()
        self.processor = DataProcessor()  # Composition 結構
        self._register_routes()
        self.run()

    def _register_routes(self):
        self.app.route('/')(self.DailyExpenseLog)
        self.app.route('/save_data', methods=['POST'])(self.save_data)
        self.app.route('/apply_filter', methods=['POST'])(self.apply_filter)

    def DailyExpenseLog(self):
        return render_template('finance.html')
    
    @staticmethod
    def validate_form(func):
        @wraps(func)
        def wrapper(self):
            data = request.form
            required_fields = ['item', 'date', 'in_out', 'category', 'amount']
            for field in required_fields:
                if field not in data or data[field] == '':
                    return jsonify({'status': 'error', 'message': f'Missing or empty field: {field}'})
            # 驗證 amount
            try:
                amount = float(data['amount'])
                if amount < 0:
                    return jsonify({'status': 'error', 'message': 'Amount must be non-negative'})
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Invalid amount'})
            return func(self)
        return wrapper
    
    @staticmethod
    def get_form_data():
        return {
            'item': request.form.get('item'),
            'date': request.form.get('date'),
            'inOut': request.form.get('in_out'),
            'category': request.form.get('category'),
            'amount': request.form.get('amount')
        }
    
    @staticmethod
    def save_to_database(item, date, inOut, category, amount):
    # 將資料儲存到資料庫，檢查重複並處理異常
        try:
            con = lite.connect('midDB.db')
            cur = con.cursor()
            if not FinanceApp.check_duplicate(cur, item, date, inOut, category, amount):
                return {'status': 'error', 'message': 'Duplicate data'}
            cur.execute("INSERT INTO Finance (item, date, inOut, category, amount) VALUES (?, ?, ?, ?, ?)",
                        (item, date, inOut, category, amount))
            con.commit()
            return {'status': 'success'}
        except lite.Error as e:
            return {'status': 'error', 'message': f'Database error: {e}'}
        finally:
            con.close()

    @staticmethod
    def check_duplicate(cur, item, date, inOut, category, amount):
        cur.execute('''SELECT * FROM Finance WHERE item = ? AND date = ? AND inOut = ? AND category = ? AND amount = ?''',
                    (item, date, inOut, category, amount))
        return cur.fetchone() is None
    
    @staticmethod
    def make_response(status, message=None):
        # 生成標準化的 JSON 訊息。
        response = {'status': status}
        if message:
            response['message'] = message
        return jsonify(response)

    @validate_form
    def save_data(self):
        # 取得表單資料
        form_data = self.get_form_data()
        item, date, inOut, category, amount = (
            form_data['item'],
            form_data['date'],
            form_data['inOut'],
            form_data['category'],
            form_data['amount']
        )

        # 儲存到資料庫
        db_result = self.save_to_database(item, date, inOut, category, amount)
        if db_result['status'] == 'error':
            return self.make_response('error', db_result['message'])

        # 回傳訊息
        return self.make_response('success')

    def apply_filter(self):
        date_filter = request.json.get('dateFilter')
        print(date_filter)

        try:
            con = lite.connect('midDB.db')
            cur = con.cursor()
            cur.execute('''SELECT item, date, inOut, category, amount FROM Finance WHERE date = ?''', (date_filter,))
            rows = cur.fetchall()
            columns = ['item', 'date', 'inOut', 'category', 'amount']
            data = [dict(zip(columns, row)) for row in rows]
            data = copy.deepcopy(data)
        except lite.Error as e:
            return jsonify({'status': 'error', 'message': f'Database error: {e}'})
        finally:
            con.close()

        # 使用 lambda 依金額排序，並透過 composition 類別執行
        data = self.processor.sort_by_amount(data)

        return jsonify(data)

if __name__ == '__main__':
    finance_app = FinanceApp()
