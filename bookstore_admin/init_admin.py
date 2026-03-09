from pymongo import MongoClient
import hashlib
import os

# MongoDB connection - 根据环境变量决定连接地址
mongo_host = os.environ.get('MONGO_HOST', 'localhost')
mongo_port = int(os.environ.get('MONGO_PORT', 27017))
mongo_username = os.environ.get('MONGO_USERNAME', 'admin')
mongo_password = os.environ.get('MONGO_PASSWORD', 'admin123')

try:
    if mongo_username and mongo_password:
        client = MongoClient(f'mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/bookstore')
    else:
        client = MongoClient(f'mongodb://{mongo_host}:{mongo_port}/')
    # 确保连接有效
    client.admin.command('ping')
    db = client.bookstore
    print("成功连接到 MongoDB")
except Exception as e:
    print(f"无法连接到 MongoDB: {e}")
    exit(1)

admins_collection = db.admin

# Check if admin already exists
admin_exists = admins_collection.count_documents({})

if not admin_exists:
    # Create default admin account
    default_admin = {
        'username': 'admin',
        'password': hashlib.md5('admin123'.encode()).hexdigest(),  # admin123 as default password
        'created_at': __import__('datetime').datetime.now()
    }
    
    admins_collection.insert_one(default_admin)
    print("Default admin account created:")
    print("Username: admin")
    print("Password: admin123")
    print("Please change the password after first login!")
else:
    print("Admin account already exists, skipping creation.")
