from flask import Flask, render_template, request, redirect, session
from database import (
    init_db, add_user, get_user, get_user_by_id,
    get_all_habits, add_habit, delete_habit, get_habit_by_id,
    complete_habit, get_completion_count, is_completed_today,
    get_last_7_days_logs, search_habits
)

app = Flask(__name__)
app.secret_key = 'секретный_ключ_для_трекера_12345'

init_db()

@app.route('/')
def index():
    if not session.get('user_id'):
        return redirect('/login')
    
    habits = get_all_habits(session['user_id'])
    user = get_user_by_id(session['user_id'])
    
    habits_with_stats = []
    for habit in habits:
        habits_with_stats.append({
            'id': habit['id'],
            'name': habit['name'],
            'description': habit['description'],
            'target_count': habit['target_count'],
            'completion_count': get_completion_count(habit['id'], session['user_id']),
            'completed_today': is_completed_today(habit['id'], session['user_id'])
        })
    
    return render_template('index.html', habits=habits_with_stats, username=user['username'])

@app.route('/add', methods=['POST'])
def add():
    if not session.get('user_id'):
        return redirect('/login')
    
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    target_count = request.form.get('target_count', 1)
    
    if name:
        add_habit(session['user_id'], name, description, target_count)
    return redirect('/')

@app.route('/complete/<int:habit_id>')
def complete(habit_id):
    if not session.get('user_id'):
        return redirect('/login')
    complete_habit(habit_id, session['user_id'])
    return redirect('/')

@app.route('/delete/<int:habit_id>')
def delete(habit_id):
    if not session.get('user_id'):
        return redirect('/login')
    delete_habit(habit_id, session['user_id'])
    return redirect('/')

@app.route('/history/<int:habit_id>')
def history(habit_id):
    if not session.get('user_id'):
        return redirect('/login')
    
    habit = get_habit_by_id(habit_id, session['user_id'])
    if not habit:
        return redirect('/')
    
    logs = get_last_7_days_logs(habit_id, session['user_id'])
    return render_template('history.html', habit=habit, logs=logs)

@app.route('/search')
def search():
    if not session.get('user_id'):
        return redirect('/login')
    
    query = request.args.get('q', '').strip()
    if query:
        habits = search_habits(session['user_id'], query)
    else:
        habits = get_all_habits(session['user_id'])
    
    habits_with_stats = []
    for habit in habits:
        habits_with_stats.append({
            'id': habit['id'],
            'name': habit['name'],
            'description': habit['description'],
            'target_count': habit['target_count'],
            'completion_count': get_completion_count(habit['id'], session['user_id']),
            'completed_today': is_completed_today(habit['id'], session['user_id'])
        })
    
    user = get_user_by_id(session['user_id'])
    return render_template('index.html', habits=habits_with_stats, username=user['username'], search_query=query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = get_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/')
        else:
            return render_template('login.html', error='Неверный логин или пароль')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('register.html', error='Заполните все поля')
        
        if add_user(username, password):
            return redirect('/login')
        else:
            return render_template('register.html', error='Пользователь уже существует')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)