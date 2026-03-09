from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from bson import ObjectId
import hashlib
import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-admin-secret-key'

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
    
    # 初始化管理员账户（如果不存在）
    if not db.find_one('admins', {}):
        default_admin = {
            'username': 'admin',
            'password': hashlib.md5('admin123'.encode()).hexdigest(),  # admin123 as default password
            'created_at': str(datetime.datetime.now())
        }
        db.insert_one('admins', default_admin)
        print("Default admin account created:")
        print("Username: admin")
        print("Password: admin123")
        print("Please change the password after first login!")
    
    # 初始化一些示例书籍数据（如果不存在）
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
        print("Sample books data created")
    
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
    
    admins_collection = MockCollection(db, 'admins')
    users_collection = MockCollection(db, 'users')
    books_collection = MockCollection(db, 'books')
    orders_collection = MockCollection(db, 'orders')
    comments_collection = MockCollection(db, 'comments')
    feedback_collection = MockCollection(db, 'feedback')
    
else:
    # 使用真实的 MongoDB 连接
    admins_collection = db.admin
    users_collection = db.user
    books_collection = db.book
    orders_collection = db.order
    comments_collection = db.comment
    feedback_collection = db.feedback

# 管理员端路由
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = hashlib.md5(request.form['password'].encode()).hexdigest()
    
    admin = admins_collection.find_one({'username': username, 'password': password})
    if admin:
        session['admin_id'] = str(admin['_id'])
        session['admin_username'] = admin['username']
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error='用户名或密码错误')

@app.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # 统计数据
    user_count = users_collection.count_documents({})
    book_count = books_collection.count_documents({})
    order_count = orders_collection.count_documents({})
    comment_count = comments_collection.count_documents({})
    feedback_count = feedback_collection.count_documents({})
    
    return render_template('dashboard.html', 
                          user_count=user_count,
                          book_count=book_count,
                          order_count=order_count,
                          comment_count=comment_count,
                          feedback_count=feedback_count)

@app.route('/users')
def users():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    all_users = list(users_collection.find({}))
    return render_template('users.html', users=all_users)

@app.route('/books')
def books():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    all_books = list(books_collection.find({}))
    return render_template('books.html', books=all_books)

@app.route('/books/add')
def add_book():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('add_book.html')

@app.route('/books/add', methods=['POST'])
def do_add_book():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    book_data = {
        'title': request.form['title'],
        'author': request.form['author'],
        'price': float(request.form['price']),
        'description': request.form['description'],
        'stock': int(request.form['stock']),
        'created_at': datetime.datetime.now()
    }
    
    books_collection.insert_one(book_data)
    return redirect(url_for('books'))

@app.route('/books/edit/<book_id>')
def edit_book(book_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # 尝试将book_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        book_id_int = int(book_id)
        book = books_collection.find_one({'_id': book_id_int})
    except ValueError:
        book = books_collection.find_one({'_id': ObjectId(book_id)})
    
    return render_template('edit_book.html', book=book)

@app.route('/books/edit/<book_id>', methods=['POST'])
def do_edit_book(book_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    book_data = {
        'title': request.form['title'],
        'author': request.form['author'],
        'price': float(request.form['price']),
        'description': request.form['description'],
        'stock': int(request.form['stock'])
    }
    
    # 尝试将book_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        book_id_int = int(book_id)
        books_collection.update_one(
            {'_id': book_id_int},
            {'$set': book_data}
        )
    except ValueError:
        books_collection.update_one(
            {'_id': ObjectId(book_id)},
            {'$set': book_data}
        )
    
    return redirect(url_for('books'))

@app.route('/books/delete/<book_id>')
def delete_book(book_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # 尝试将book_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        book_id_int = int(book_id)
        books_collection.delete_one({'_id': book_id_int})
    except ValueError:
        books_collection.delete_one({'_id': ObjectId(book_id)})
    
    return redirect(url_for('books'))

@app.route('/orders')
def orders():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
        
    all_orders = list(orders_collection.find({}))
    # 补充用户信息
    for order in all_orders:
        # 处理user_id，支持ObjectId和字符串/整数格式
        user_id = order.get('user_id')
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
        order['user'] = user
        
    return render_template('orders.html', orders=all_orders)

@app.route('/orders/delete/<order_id>')
def delete_order(order_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # 尝试将order_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        order_id_int = int(order_id)
        orders_collection.delete_one({'_id': order_id_int})
    except ValueError:
        orders_collection.delete_one({'_id': ObjectId(order_id)})
    
    return redirect(url_for('orders'))

@app.route('/comments')
def comments():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
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
    
    return render_template('comments.html', comments=all_comments)

@app.route('/comments/delete/<comment_id>')
def delete_comment(comment_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # 尝试将comment_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        comment_id_int = int(comment_id)
        comments_collection.delete_one({'_id': comment_id_int})
    except ValueError:
        comments_collection.delete_one({'_id': ObjectId(comment_id)})
    
    return redirect(url_for('comments'))

@app.route('/feedback')
def feedback():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    all_feedback = list(feedback_collection.find({}))
    # 补充用户信息
    for fb in all_feedback:
        if 'user_id' in fb:
            # 处理user_id，支持ObjectId和字符串/整数格式
            user_id = fb.get('user_id')
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
            fb['user'] = user
    
    return render_template('feedback.html', feedback=all_feedback)

@app.route('/feedback/<feedback_id>')
def feedback_detail(feedback_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # 尝试将feedback_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        feedback_id_int = int(feedback_id)
        fb = feedback_collection.find_one({'_id': feedback_id_int})
    except ValueError:
        fb = feedback_collection.find_one({'_id': ObjectId(feedback_id)})
    
    if fb and 'user_id' in fb:
        # 尝试将user_id转换为整数（模拟数据库）或ObjectId（真实数据库）
        try:
            user_id = int(fb['user_id'])
            user = users_collection.find_one({'_id': user_id})
        except ValueError:
            user = users_collection.find_one({'_id': ObjectId(fb['user_id'])})
        fb['user'] = user
    
    return render_template('feedback_detail.html', feedback=fb)

@app.route('/feedback/delete/<feedback_id>')
def delete_feedback(feedback_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # 尝试将feedback_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        feedback_id_int = int(feedback_id)
        feedback_collection.delete_one({'_id': feedback_id_int})
    except ValueError:
        feedback_collection.delete_one({'_id': ObjectId(feedback_id)})
    
    return redirect(url_for('feedback'))

@app.route('/users/delete/<user_id>')
def delete_user(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # 尝试将user_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        user_id_int = int(user_id)
        users_collection.delete_one({'_id': user_id_int})
    except ValueError:
        users_collection.delete_one({'_id': ObjectId(user_id)})
    
    return redirect(url_for('users'))

@app.route('/users/edit/<user_id>')
def edit_user(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # 尝试将user_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        user_id_int = int(user_id)
        user = users_collection.find_one({'_id': user_id_int})
    except ValueError:
        user = users_collection.find_one({'_id': ObjectId(user_id)})
    
    return render_template('edit_user.html', user=user)

@app.route('/users/edit/<user_id>', methods=['POST'])
def do_edit_user(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    user_data = {
        'username': request.form['username'],
        'email': request.form['email']
    }
    
    # 尝试将user_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        user_id_int = int(user_id)
        users_collection.update_one(
            {'_id': user_id_int},
            {'$set': user_data}
        )
    except ValueError:
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': user_data}
        )
    
    return redirect(url_for('users'))

@app.route('/change_password')
def show_change_password():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('change_password.html')

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    new_password = hashlib.md5(request.form['new_password'].encode()).hexdigest()
    
    # 尝试将admin_id转换为整数（模拟数据库）或ObjectId（真实数据库）
    try:
        admin_id = int(session['admin_id'])
        admins_collection.update_one(
            {'_id': admin_id},
            {'$set': {'password': new_password}}
        )
    except ValueError:
        admins_collection.update_one(
            {'_id': ObjectId(session['admin_id'])},
            {'$set': {'password': new_password}}
        )
    
    return redirect(url_for('dashboard', success='密码修改成功'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)