from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from bson import ObjectId
import hashlib
import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# MongoDB connection - 根据设计文档使用指定地址
mongo_host = os.environ.get('MONGO_HOST', '192.168.237.128')
mongo_port = int(os.environ.get('MONGO_PORT', 27017))
mongo_username = os.environ.get('MONGO_USERNAME', 'admin')
mongo_password = os.environ.get('MONGO_PASSWORD', 'admin123')

try:
    client = MongoClient(f'mongodb://{mongo_host}:{mongo_port}/')
    # 确保连接有效
    client.admin.command('ping')
    db = client.bookstore
    print("成功连接到 MongoDB")
except Exception as e:
    print(f"无法连接到 MongoDB: {e}")
    # 如果连接失败，使用模拟数据库
    print("使用模拟数据库...")
    
    # 模拟数据库 - 使用文件存储数据
    import json
    
    class MockDB:
        def __init__(self, filename):
            self.filename = filename
            self.data = self.load_data()
        
        def load_data(self):
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        
        def save_data(self):
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        def find_one(self, collection, query):
            if collection not in self.data:
                return None
            for item in self.data[collection]:
                match = True
                for key, value in query.items():
                    # 处理_id字段的特殊处理
                    if key == '_id':
                        try:
                            if isinstance(value, str) and value.isdigit():
                                value = int(value)
                            elif isinstance(value, ObjectId):
                                value = int(str(value))
                        except:
                            pass
                    if key not in item or item[key] != value:
                        match = False
                        break
                if match:
                    return item
            return None
        
        def find_all(self, collection):
            if collection not in self.data:
                return []
            return self.data[collection]
        
        def insert_one(self, collection, data):
            if collection not in self.data:
                self.data[collection] = []
            # 添加ID
            data['_id'] = len(self.data[collection]) + 1
            self.data[collection].append(data)
            self.save_data()
            return type('obj', (object,), {'inserted_id': data['_id']})()
        
        def update_one(self, collection, query, update):
            if collection not in self.data:
                return
            for item in self.data[collection]:
                match = True
                for key, value in query.items():
                    if key not in item or item[key] != value:
                        match = False
                        break
                if match:
                    # $set 操作
                    if '$set' in update:
                        for k, v in update['$set'].items():
                            item[k] = v
                    self.save_data()
                    break
        
        def delete_one(self, collection, query):
            if collection not in self.data:
                return
            for i, item in enumerate(self.data[collection]):
                match = True
                for key, value in query.items():
                    if key not in item or item[key] != value:
                        match = False
                        break
                if match:
                    del self.data[collection][i]
                    self.save_data()
                    break
        
        def count_documents(self, collection, query=None):
            if collection not in self.data:
                return 0
            if query is None:
                return len(self.data[collection])
            count = 0
            for item in self.data[collection]:
                match = True
                for key, value in query.items():
                    if key not in item or item[key] != value:
                        match = False
                        break
                if match:
                    count += 1
            return count
    
    # 使用模拟数据库
    db = MockDB('mock_data.json')
    users_collection = db
    books_collection = db
    orders_collection = db
    comments_collection = db
    feedback_collection = db
    
    # 初始化一些示例数据
    if not db.find_one('books', {}):
        # 添加一些示例书籍
        sample_books = [
            {
                'title': 'Python编程入门',
                'author': '张三',
                'price': 59.0,
                'description': 'Python编程的入门书籍，适合初学者',
                'stock': 10,
                'created_at': str(datetime.datetime.now())
            },
            {
                'title': 'Flask Web开发',
                'author': '李四',
                'price': 69.0,
                'description': '学习Flask Web框架的实用指南',
                'stock': 5,
                'created_at': str(datetime.datetime.now())
            },
            {
                'title': 'JavaScript高级程序设计',
                'author': '王五',
                'price': 89.0,
                'description': '深入学习JavaScript语言的高级特性',
                'stock': 8,
                'created_at': str(datetime.datetime.now())
            },
            {
                'title': '数据结构与算法',
                'author': '赵六',
                'price': 75.0,
                'description': '计算机科学中的经典算法和数据结构',
                'stock': 12,
                'created_at': str(datetime.datetime.now())
            },
            {
                'title': '机器学习实战',
                'author': '钱七',
                'price': 95.0,
                'description': '使用Python进行机器学习的实践指南',
                'stock': 6,
                'created_at': str(datetime.datetime.now())
            },
            {
                'title': '设计模式之美',
                'author': '孙八',
                'price': 72.0,
                'description': '软件设计中常用的设计模式及其应用',
                'stock': 9,
                'created_at': str(datetime.datetime.now())
            }
        ]
        for book in sample_books:
            db.insert_one('books', book)
    
    # 为模拟数据库设置别名
    class MockCollection:
        def __init__(self, db, collection_name):
            self.db = db
            self.collection_name = collection_name
        
        def find_one(self, query):
            return self.db.find_one(self.collection_name, query)
        
        def find(self, query=None):
            if query is None:
                return self.db.find_all(self.collection_name)
            # 简单的查询实现
            result = []
            for item in self.db.find_all(self.collection_name):
                match = True
                for key, value in query.items():
                    if key not in item or item[key] != value:
                        match = False
                        break
                if match:
                    result.append(item)
            return result
        
        def insert_one(self, data):
            return self.db.insert_one(self.collection_name, data)
        
        def update_one(self, query, update):
            return self.db.update_one(self.collection_name, query, update)
        
        def delete_one(self, query):
            return self.db.delete_one(self.collection_name, query)
        
        def count_documents(self, query=None):
            return self.db.count_documents(self.collection_name, query)
    
    users_collection = MockCollection(db, 'users')
    books_collection = MockCollection(db, 'books')
    orders_collection = MockCollection(db, 'orders')
    comments_collection = MockCollection(db, 'comments')
    feedback_collection = MockCollection(db, 'feedback')
    
else:
    # 使用真实的 MongoDB 连接
    users_collection = db.user
    books_collection = db.book
    orders_collection = db.order
    comments_collection = db.comment
    feedback_collection = db.feedback

# 用户端路由
@app.route('/')
def index():
    return render_template('user_dashboard.html')

@app.route('/books')
def view_books():
    # 获取搜索参数
    search_query = request.args.get('q', '')
    
    if search_query:
        # 如果有搜索参数，搜索书籍
        all_books = list(books_collection.find({}))
        books = []
        for book in all_books:
            if search_query.lower() in book['title'].lower() or \
               search_query.lower() in book['author'].lower():
                books.append(book)
    else:
        # 否则显示所有书籍
        books = list(books_collection.find({}))
    
    return render_template('dashboard.html', books=books)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = hashlib.md5(request.form['password'].encode()).hexdigest()
    
    user = users_collection.find_one({'username': username, 'password': password})
    if user:
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        
        # 检查是否有重定向到之前请求的页面
        next_url = session.pop('next_url', None)
        if next_url:
            return redirect(next_url)
        else:
            return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error='用户名或密码错误')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def do_register():
    username = request.form['username']
    password = hashlib.md5(request.form['password'].encode()).hexdigest()
    email = request.form['email']
    
    # 检查用户名是否已存在
    if users_collection.find_one({'username': username}):
        return render_template('register.html', error='用户名已存在')
    
    # 创建新用户
    user_data = {
        'username': username,
        'password': password,
        'email': email,
        'created_at': datetime.datetime.now()
    }
    users_collection.insert_one(user_data)
    
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    books = list(books_collection.find({}))
    return render_template('dashboard.html', books=books)

@app.route('/book/<book_id>')
def book_detail(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 尝试将book_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        book_id_int = int(book_id)
        book = books_collection.find_one({'_id': book_id_int})
    except ValueError:
        book = books_collection.find_one({'_id': ObjectId(book_id)})
    
    return render_template('book_detail.html', book=book)

@app.route('/cart')
def cart():
    # 允许未登录用户查看购物车
    # if 'user_id' not in session:
    #     return redirect(url_for('login'))
    
    # 获取购物车内容
    cart_items = session.get('cart', [])
    books = []
    total_price = 0
    
    for item in cart_items:
        # 尝试将book_id转换为整数（模拟数据库）或ObjectId（真实数据库）
        try:
            book_id = int(item['book_id'])
            book = books_collection.find_one({'_id': book_id})
        except ValueError:
            book = books_collection.find_one({'_id': ObjectId(item['book_id'])})
        
        if book:
            book['quantity'] = item['quantity']
            book['subtotal'] = book['price'] * item['quantity']
            total_price += book['subtotal']
            books.append(book)
    
    return render_template('cart.html', books=books, total_price=total_price)

@app.route('/add_to_cart/<book_id>', methods=['GET', 'POST'])
def add_to_cart(book_id):
    # 调试信息：打印请求方法和会话状态
    print(f"[DEBUG] 请求方法: {request.method}")
    print(f"[DEBUG] 会话内容: {session}")
    
    # 允许未登录用户添加到临时购物车
    # if 'user_id' not in session:
    #     print("[DEBUG] 用户未登录，重定向到登录页面")
    #     return redirect(url_for('login'))
    
    # 同时支持GET参数和POST表单数据
    if request.method == 'POST':
        quantity = int(request.form.get('quantity', 1))
        action = request.form.get('action', 'add')
        print(f"[DEBUG] POST请求 - 数量: {quantity}, 动作: {action}")
    else:
        quantity = int(request.args.get('quantity', 1))
        action = 'add'
        print(f"[DEBUG] GET请求 - 数量: {quantity}, 动作: {action}")
    
    if 'cart' not in session:
        session['cart'] = []
    
    # 检查是否已经添加过此书
    found = False
    for item in session['cart']:
        if item['book_id'] == book_id:
            if action == 'increase':
                item['quantity'] += 1  # 增加数量
            elif action == 'decrease':
                item['quantity'] = max(1, item['quantity'] - 1)  # 减少数量，但不能少于1
            else:
                item['quantity'] += quantity  # 添加到购物车
            found = True
            break
    
    # 如果没有添加过，且不是减少操作，则新增
    if not found and action != 'decrease':
        session['cart'].append({
            'book_id': book_id,
            'quantity': quantity
        })
    
    session.modified = True
    
    # 如果用户已登录，正常重定向到购物车
    if 'user_id' in session:
        return redirect(url_for('cart'))
    else:
        # 如果用户未登录，提示需要登录才能结账，并返回到图书列表页
        books = list(books_collection.find({}))
        return render_template('dashboard.html', books=books, 
                               message='商品已添加到购物车！登录后可查看购物车并结账。', cart_updated=True)

@app.route('/remove_from_cart/<book_id>')
def remove_from_cart(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['book_id'] != book_id]
        session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        # 如果用户未登录，重定向到登录页面，并在登录后返回到购物车
        session['next_url'] = url_for('checkout')
        return redirect(url_for('login'))
    
    # 获取购物车内容
    cart_items = session.get('cart', [])
    if not cart_items:
        return redirect(url_for('cart'))
    
    books = []
    total_price = 0
    
    for item in cart_items:
        # 尝试将book_id转换为整数（模拟数据库）或ObjectId（真实数据库）
        try:
            book_id = int(item['book_id'])
            book = books_collection.find_one({'_id': book_id})
        except ValueError:
            book = books_collection.find_one({'_id': ObjectId(item['book_id'])})
        
        if book:
            book['quantity'] = item['quantity']
            book['subtotal'] = book['price'] * item['quantity']
            total_price += book['subtotal']
            books.append(book)
    
    # 创建订单
    order_data = {
        'user_id': session['user_id'],
        'books': cart_items,
        'total_price': total_price,
        'status': 'pending',
        'created_at': datetime.datetime.now()
    }
    
    result = orders_collection.insert_one(order_data)
    order_id = str(result.inserted_id)
    
    # 清空购物车
    session['cart'] = []
    session.modified = True
    
    return redirect(url_for('order_detail', order_id=order_id))

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_orders = list(orders_collection.find({'user_id': session['user_id']}))
    return render_template('orders.html', orders=user_orders)

@app.route('/order/<order_id>')
def order_detail(order_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 尝试将order_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        order_id_int = int(order_id)
        order = orders_collection.find_one({'_id': order_id_int, 'user_id': session['user_id']})
    except ValueError:
        order = orders_collection.find_one({'_id': ObjectId(order_id), 'user_id': session['user_id']})
    
    if not order:
        return "订单不存在"
    
    books = []
    for item in order['books']:
        # 尝试将book_id转换为整数（模拟数据库）或ObjectId（真实数据库）
        try:
            book_id = int(item['book_id'])
            book = books_collection.find_one({'_id': book_id})
        except ValueError:
            book = books_collection.find_one({'_id': ObjectId(item['book_id'])})
        
        if book:
            book['quantity'] = item['quantity']
            books.append(book)
    
    return render_template('order_detail.html', order=order, books=books)

@app.route('/order/<order_id>/comment', methods=['POST'])
def add_comment(order_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 尝试将order_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        order_id_int = int(order_id)
        order = orders_collection.find_one({'_id': order_id_int, 'user_id': session['user_id']})
    except ValueError:
        order = orders_collection.find_one({'_id': ObjectId(order_id), 'user_id': session['user_id']})
    
    if not order:
        return "订单不存在"
    
    content = request.form['content']
    rating = int(request.form['rating'])
    
    comment_data = {
        'user_id': session['user_id'],
        'order_id': order_id,
        'content': content,
        'rating': rating,
        'created_at': datetime.datetime.now()
    }
    
    comments_collection.insert_one(comment_data)
    
    # 更新订单状态
    try:
        order_id_int = int(order_id)
        orders_collection.update_one(
            {'_id': order_id_int},
            {'$set': {'status': 'commented'}}
        )
    except ValueError:
        orders_collection.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'status': 'commented'}}
        )
    
    return redirect(url_for('order_detail', order_id=order_id))

@app.route('/comments')
def comments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 显示当前用户的评论
    user_comments = list(comments_collection.find({'user_id': session['user_id']}))
    # 补充用户和订单信息
    for comment in user_comments:
        # 处理用户ID
        user_id = comment.get('user_id')
        if isinstance(user_id, str):
            try:
                # 如果是字符串，尝试转换为整数
                user_id_int = int(user_id)
                user = users_collection.find_one({'_id': user_id_int})
            except ValueError:
                # 如果转换失败，尝试作为ObjectId查询
                try:
                    user = users_collection.find_one({'_id': ObjectId(user_id)})
                except:
                    user = None
        elif isinstance(user_id, ObjectId):
            # 如果已经是ObjectId，直接查询
            user = users_collection.find_one({'_id': user_id})
        else:
            # 其他情况，尝试转换为整数
            try:
                user_id_int = int(user_id)
                user = users_collection.find_one({'_id': user_id_int})
            except:
                user = None
        comment['user'] = user
        
        # 处理订单ID
        order_id = comment.get('order_id')
        if isinstance(order_id, str):
            try:
                # 如果是字符串，尝试转换为整数
                order_id_int = int(order_id)
                order = orders_collection.find_one({'_id': order_id_int})
            except ValueError:
                # 如果转换失败，尝试作为ObjectId查询
                try:
                    order = orders_collection.find_one({'_id': ObjectId(order_id)})
                except:
                    order = None
        elif isinstance(order_id, ObjectId):
            # 如果已经是ObjectId，直接查询
            order = orders_collection.find_one({'_id': order_id})
        else:
            # 其他情况，尝试转换为整数
            try:
                order_id_int = int(order_id)
                order = orders_collection.find_one({'_id': order_id_int})
            except:
                order = None
        comment['order'] = order
    
    return render_template('comments.html', comments=user_comments)

@app.route('/all_comments')
def all_comments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 显示所有评论
    all_comments = list(comments_collection.find({}))
    # 补充用户和订单信息
    for comment in all_comments:
        # 处理用户ID
        user_id = comment.get('user_id')
        if isinstance(user_id, str):
            try:
                # 如果是字符串，尝试转换为整数
                user_id_int = int(user_id)
                user = users_collection.find_one({'_id': user_id_int})
            except ValueError:
                # 如果转换失败，尝试作为ObjectId查询
                try:
                    user = users_collection.find_one({'_id': ObjectId(user_id)})
                except:
                    user = None
        elif isinstance(user_id, ObjectId):
            # 如果已经是ObjectId，直接查询
            user = users_collection.find_one({'_id': user_id})
        else:
            # 其他情况，尝试转换为整数
            try:
                user_id_int = int(user_id)
                user = users_collection.find_one({'_id': user_id_int})
            except:
                user = None
        comment['user'] = user
        
        # 处理订单ID
        order_id = comment.get('order_id')
        if isinstance(order_id, str):
            try:
                # 如果是字符串，尝试转换为整数
                order_id_int = int(order_id)
                order = orders_collection.find_one({'_id': order_id_int})
            except ValueError:
                # 如果转换失败，尝试作为ObjectId查询
                try:
                    order = orders_collection.find_one({'_id': ObjectId(order_id)})
                except:
                    order = None
        elif isinstance(order_id, ObjectId):
            # 如果已经是ObjectId，直接查询
            order = orders_collection.find_one({'_id': order_id})
        else:
            # 其他情况，尝试转换为整数
            try:
                order_id_int = int(order_id)
                order = orders_collection.find_one({'_id': order_id_int})
            except:
                order = None
        comment['order'] = order
    
    return render_template('all_comments.html', comments=all_comments)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # 尝试将user_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        user_id = int(session['user_id'])
        user = users_collection.find_one({'_id': user_id})
    except ValueError:
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
    
    return render_template('profile.html', user=user)

@app.route('/profile/edit', methods=['POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    email = request.form['email']
    # 尝试将user_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        user_id = int(session['user_id'])
        users_collection.update_one(
            {'_id': user_id},
            {'$set': {'email': email}}
        )
    except ValueError:
        users_collection.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {'email': email}}
        )
    
    return redirect(url_for('profile'))

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    old_password = hashlib.md5(request.form['old_password'].encode()).hexdigest()
    new_password = hashlib.md5(request.form['new_password'].encode()).hexdigest()
    
    # 尝试将user_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        user_id = int(session['user_id'])
        user = users_collection.find_one({'_id': user_id})
    except ValueError:
        user = users_collection.find_one({'_id': ObjectId(session['user_id'])})
    
    if user and user['password'] == old_password:
        # 尝试将user_id转换为整数（模拟数据库）或ObjectId（真实数据库）
        try:
            user_id = int(session['user_id'])
            users_collection.update_one(
                {'_id': user_id},
                {'$set': {'password': new_password}}
            )
        except ValueError:
            users_collection.update_one(
                {'_id': ObjectId(session['user_id'])},
                {'$set': {'password': new_password}}
            )
        return redirect(url_for('profile', success='密码修改成功'))
    else:
        return redirect(url_for('profile', error='原密码错误'))

@app.route('/feedback')
def feedback():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('feedback.html')

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    title = request.form.get('title', '')
    content = request.form['content']
    
    feedback_data = {
        'user_id': session['user_id'],
        'title': title,
        'content': content,
        'created_at': datetime.datetime.now()
    }
    
    feedback_collection.insert_one(feedback_data)
    
    return redirect(url_for('dashboard', success='反馈提交成功'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=3000)