import sqlite3 as lite
import copy
from flask import Flask, request, render_template, jsonify
from functools import wraps

def validate_form(func):
    """自定義裝飾器，檢查表單數據"""
    @wraps(func)
    def wrapper(self):
        data = request.form
        assert all([value != '' for value in data.values()]), "Cannot insert NULL"
        return func(self)
    return wrapper

class BaseApp:
    """父類，提供基礎應用功能"""
    def __init__(self):
        self.app = Flask(__name__)

    def run(self):
        self.app.debug = True
        self.app.run()

class FinanceApp(BaseApp):
    def __init__(self):
        super().__init__()
        self.init_database()
        self.register_routes()
        self.run()

    def register_routes(self):
        """註冊路由"""
        self.app.route('/')(self.health)
        self.app.route('/save_data', methods=['POST'])(self.save_data)
        self.app.route('/apply_filter', methods=['POST'])(self.apply_filter)

    @classmethod
    def init_database(cls):
        """初始化數據庫"""
        try:
            con = lite.connect('midDB.db')
            cur = con.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS Finance
                          (item TEXT, date TEXT, inOut TEXT, category TEXT, amount REAL)''')
            con.commit()
        except lite.Error as e:
            print(f"Database error: {e}")
        finally:
            con.close()

    @staticmethod
    def validate_input(item, date, inOut, category, amount):
        """驗證輸入"""
        return not any(v == '' for v in [item, date, inOut, category, amount])

    @staticmethod
    def check_duplicate(cur, item, date, inOut, category, amount):
        """檢查重複數據"""
        cur.execute('''SELECT * FROM Finance WHERE item = ? AND date = ? AND inOut = ? AND category = ? AND amount = ?''',
                    (item, date, inOut, category, amount))
        return cur.fetchone() is None

    def health(self):
        """顯示首頁"""
        return render_template('finance.html')

    @validate_form
    def save_data(self):
        """處理數據保存"""
        item = request.form.get('item')
        date = request.form.get('date')
        inOut = request.form.get('in_out')
        category = request.form.get('category')
        amount = request.form.get('amount')

        try:
            amount = float(amount)
            assert amount >= 0, "Amount must be non-negative"
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid amount'})

        try:
            con = lite.connect('midDB.db')
            cur = con.cursor()
            if not FinanceApp.check_duplicate(cur, item, date, inOut, category, amount):
                return jsonify({'status': 'error', 'message': 'Duplicate data'})
            cur.execute("INSERT INTO Finance (item, date, inOut, category, amount) VALUES (?, ?, ?, ?, ?)",
                        (item, date, inOut, category, amount))
            con.commit()
        except lite.Error as e:
            return jsonify({'status': 'error', 'message': f'Database error: {e}'})
        finally:
            con.close()

        print(f"Received data: Item={item}, Date={date}, income/cose={inOut}, category={category}, Amount={amount}")
        return jsonify({'status': 'success'})

    def apply_filter(self):
        """處理數據過濾"""
        date_filter = request.json.get('dateFilter')
        print(date_filter)

        try:
            con = lite.connect('midDB.db')
            cur = con.cursor()
            cur.execute('''SELECT * FROM Finance WHERE date = ?''', (date_filter,))
            columns = ['item', 'date', 'inOut', 'category', 'amount']
            data = [dict(zip(columns, row)) for row in cur.fetchall()]
            data = copy.deepcopy(data)  # 確保返回獨立副本
        except lite.Error as e:
            return jsonify({'status': 'error', 'message': f'Database error: {e}'})
        finally:
            con.close()

        return jsonify(data)

if __name__ == '__main__':
    finance_app = FinanceApp()