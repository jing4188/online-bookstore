from pymongo import MongoClient
from datetime import datetime
import hashlib

# 连接到MongoDB
print("正在连接到MongoDB...")
client = MongoClient('mongodb://192.168.237.128:27017/')
db = client.bookstore

# 创建示例数据
print("正在初始化数据库...")

# 清空现有数据
db.book.delete_many({})
db.user.delete_many({})
db.order.delete_many({})
db.comment.delete_many({})
db.feedback.delete_many({})
db.admin.delete_many({})

# 插入管理员数据
admin_data = {
    'username': 'admin',
    'password': hashlib.md5('admin123'.encode()).hexdigest(),  # admin123加密后
    'created_at': datetime.now()
}
db.admin.insert_one(admin_data)
print("已添加管理员账户: admin / admin123")

# 插入示例书籍数据
sample_books = [
    {
        'title': 'Python编程入门',
        'author': '张三',
        'price': 59.0,
        'description': 'Python编程的入门书籍，适合初学者',
        'stock': 10,
        'created_at': datetime.now()
    },
    {
        'title': 'Flask Web开发',
        'author': '李四',
        'price': 69.0,
        'description': '学习Flask Web框架的实用指南',
        'stock': 5,
        'created_at': datetime.now()
    },
    {
        'title': 'JavaScript高级程序设计',
        'author': '王五',
        'price': 89.0,
        'description': '深入学习JavaScript语言的高级特性',
        'stock': 8,
        'created_at': datetime.now()
    },
    {
        'title': '数据结构与算法',
        'author': '赵六',
        'price': 75.0,
        'description': '计算机科学中的经典算法和数据结构',
        'stock': 12,
        'created_at': datetime.now()
    },
    {
        'title': '机器学习实战',
        'author': '钱七',
        'price': 95.0,
        'description': '使用Python进行机器学习的实践指南',
        'stock': 6,
        'created_at': datetime.now()
    },
    {
        'title': '设计模式之美',
        'author': '孙八',
        'price': 72.0,
        'description': '软件设计中常用的设计模式及其应用',
        'stock': 9,
        'created_at': datetime.now()
    }
]

db.book.insert_many(sample_books)
print(f"已添加 {len(sample_books)} 本示例书籍")

# 插入示例用户数据
sample_users = [
    {
        'username': 'testuser',
        'password': hashlib.md5('123456'.encode()).hexdigest(),  # 123456加密后
        'email': 'test@example.com',
        'created_at': datetime.now()
    },
    {
        'username': 'demo',
        'password': hashlib.md5('demo123'.encode()).hexdigest(),  # demo123加密后
        'email': 'demo@example.com',
        'created_at': datetime.now()
    }
]

db.user.insert_many(sample_users)
print(f"已添加 {len(sample_users)} 个示例用户")

# 插入示例订单数据
sample_orders = [
    {
        'user_id': db.user.find_one({'username': 'testuser'})['_id'],
        'books': [
            {'book_id': db.book.find_one({'title': 'Python编程入门'})['_id'], 'quantity': 1}
        ],
        'total_price': 59.0,
        'status': 'completed',
        'created_at': datetime.now()
    }
]

for order in sample_orders:
    db.order.insert_one(order)
print(f"已添加 {len(sample_orders)} 个示例订单")

# 插入示例评价数据
first_order = db.order.find_one()
first_book = db.book.find_one({'title': 'Python编程入门'})
first_user = db.user.find_one({'username': 'testuser'})

if first_order and first_book and first_user:
    sample_comments = [
        {
            'user_id': first_user['_id'],
            'order_id': first_order['_id'],
            'content': '这本书非常好，讲解清晰易懂，对初学者很友好。',
            'rating': 5,
            'created_at': datetime.now()
        }
    ]
    
    for comment in sample_comments:
        db.comment.insert_one(comment)
    print(f"已添加 {len(sample_comments)} 个示例评价")

# 插入示例反馈数据
first_user = db.user.find_one({'username': 'demo'})
if first_user:
    sample_feedback = [
        {
            'user_id': first_user['_id'],
            'title': '网站建议',
            'content': '希望能增加更多的筛选功能，比如按价格区间筛选。',
            'created_at': datetime.now()
        }
    ]
    
    for feedback in sample_feedback:
        db.feedback.insert_one(feedback)
    print(f"已添加 {len(sample_feedback)} 条示例反馈")

print("数据库初始化完成！")
print(f"数据库名称: bookstore")
print(f"书籍数量: {db.book.count_documents({})}")
print(f"用户数量: {db.user.count_documents({})}")
print(f"订单数量: {db.order.count_documents({})}")
print(f"评价数量: {db.comment.count_documents({})}")
print(f"反馈数量: {db.feedback.count_documents({})}")
print(f"管理员数量: {db.admin.count_documents({})}")

client.close()
print("数据库连接已关闭")