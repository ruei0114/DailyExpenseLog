import sqlite3 as lite
from flask import Flask, request, render_template, jsonify
app = Flask(__name__) 

@app.route('/')
def health():
    
    return render_template('finance.html')

@app.route('/save_data', methods=['POST'])
def save_data():
    item = request.form.get('item')
    date = request.form.get('date')
    inOut = request.form.get('in_out')
    category = request.form.get('category')
    amount = request.form.get('amount')

    con = lite.connect('midDB.db')
    cur = con.cursor()

    #Check for blank
    if item=='' or date=='' or inOut=='' or category=='' or amount=='':
        return jsonify({'status': 'error', 'message': 'Cannot insert NULL'})

    # Check for duplicate data
    cur.execute('''
        SELECT * FROM Finance
        WHERE item = ? AND date = ? AND inOut = ? AND category = ? AND amount = ?
    ''', (item, date, inOut, category, amount))
    duplicate_data = cur.fetchone()

    if duplicate_data:
        return jsonify({'status': 'error', 'message': 'Duplicate data'})

    # Insert data into the database
    cur.execute("INSERT INTO Finance (item, date, inOut, category, amount)VALUES (?, ?, ?, ?, ?)", (item, date, inOut, category, amount))
    con.commit()
    con.close()

    # Perform any necessary processing or save to a database
    # For now, let's just print the data
    print(f"Received data: Item={item}, Date={date}, income/cose={inOut}, category={category}, Amount={float(amount)}")

    # You can send a response back to the client if needed
    return jsonify({'status': 'success'})

@app.route('/apply_filter', methods=['POST'])
def apply_filter():
    # 獲取日期選擇器的值
    date_filter = request.json.get('dateFilter')
    print(date_filter)

    con = lite.connect('midDB.db')
    cur = con.cursor()

    # 這裡假設你的Finance表中有一個名為date的欄位
    cur.execute('''
        SELECT * FROM Finance
        WHERE date = ?
    ''', (date_filter,))
    
    data = cur.fetchall()
    con.close()

    #return data
    # 返回過濾後的數據
    return jsonify(data)

if __name__ == '__main__':
    app.debug = True
    app.run()  
