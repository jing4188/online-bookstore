from pymongo import MongoClient
from datetime import datetime
import random

# 连接到MongoDB
print("正在连接到MongoDB...")
client = MongoClient('mongodb://192.168.237.128:27017/')
db = client.bookstore

print("正在添加50本书籍到数据库...")

# 更多书籍数据
more_books = [
    {
        'title': '深入理解计算机系统',
        'author': 'Randal E. Bryant',
        'price': 128.0,
        'description': '从程序员的角度深入剖析计算机系统的经典教材',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '算法导论',
        'author': 'Thomas H. Cormen',
        'price': 139.0,
        'description': '算法领域的权威教材，涵盖广泛的算法知识',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '设计模式',
        'author': 'Erich Gamma',
        'price': 45.0,
        'description': '面向对象软件设计的经典著作',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '重构：改善既有代码的设计',
        'author': 'Martin Fowler',
        'price': 79.0,
        'description': '改善代码质量的经典之作',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '代码整洁之道',
        'author': 'Robert C. Martin',
        'price': 59.0,
        'description': '教你编写更整洁、更易维护的代码',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '人月神话',
        'author': 'Frederick P. Brooks Jr.',
        'price': 35.0,
        'description': '软件工程领域的经典著作',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'C程序设计语言',
        'author': 'Brian W. Kernighan',
        'price': 30.0,
        'description': 'C语言的经典教材',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Java核心技术',
        'author': 'Cay S. Horstmann',
        'price': 149.0,
        'description': 'Java编程的权威参考书',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Effective Java',
        'author': 'Joshua Bloch',
        'price': 78.0,
        'description': 'Java编程的最佳实践指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Java并发编程实战',
        'author': 'Brian Goetz',
        'price': 69.0,
        'description': '深入理解Java并发编程',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Spring实战',
        'author': 'Craig Walls',
        'price': 89.0,
        'description': 'Spring框架的实战指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Head First设计模式',
        'author': 'Eric Freeman',
        'price': 98.0,
        'description': '以生动有趣的方式学习设计模式',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '高性能MySQL',
        'author': 'Baron Schwartz',
        'price': 108.0,
        'description': 'MySQL性能优化的权威指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Redis设计与实现',
        'author': '黄健宏',
        'price': 65.0,
        'description': '深入理解Redis内部实现原理',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '深入浅出Node.js',
        'author': '朴灵',
        'price': 58.0,
        'description': 'Node.js开发的优秀指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '你不知道的JavaScript',
        'author': 'Kyle Simpson',
        'price': 88.0,
        'description': '深入探索JavaScript语言的核心概念',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'ES6标准入门',
        'author': '阮一峰',
        'price': 68.0,
        'description': '学习ECMAScript 6的优秀教程',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Vue.js实战',
        'author': '梁灏',
        'price': 72.0,
        'description': 'Vue.js框架的实战指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'React进阶之路',
        'author': '徐超',
        'price': 66.0,
        'description': 'React开发的进阶指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Angular权威教程',
        'author': 'Adam Freeman',
        'price': 75.0,
        'description': 'Angular框架的权威指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Linux命令行与shell脚本编程大全',
        'author': 'Richard Blum',
        'price': 119.0,
        'description': 'Linux命令行和shell脚本编程的全面指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '鸟哥的Linux私房菜',
        'author': '鸟哥',
        'price': 108.0,
        'description': '学习Linux的经典教材',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Docker技术入门与实战',
        'author': '杨保华',
        'price': 52.0,
        'description': 'Docker容器技术的入门实战指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Kubernetes权威指南',
        'author': '龚正',
        'price': 128.0,
        'description': 'Kubernetes容器编排的权威指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '微服务架构与实践',
        'author': '王磊',
        'price': 69.0,
        'description': '微服务架构的设计与实践指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '大数据技术原理与应用',
        'author': '林子雨',
        'price': 49.0,
        'description': '大数据技术的原理与应用实践',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Spark大数据处理',
        'author': '陈欢',
        'price': 55.0,
        'description': 'Apache Spark大数据处理指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Hadoop权威指南',
        'author': 'Tom White',
        'price': 98.0,
        'description': 'Hadoop生态系统权威指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '人工智能：一种现代方法',
        'author': 'Stuart Russell',
        'price': 158.0,
        'description': '人工智能领域的权威教材',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '机器学习',
        'author': '周志华',
        'price': 78.0,
        'description': '机器学习领域的中文经典教材',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '深度学习',
        'author': 'Ian Goodfellow',
        'price': 168.0,
        'description': '深度学习领域的权威著作',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Python机器学习',
        'author': 'Sebastian Raschka',
        'price': 89.0,
        'description': '使用Python进行机器学习的实践指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '统计学习方法',
        'author': '李航',
        'price': 56.0,
        'description': '统计学习方法的经典教材',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '数据挖掘：概念与技术',
        'author': 'Jiawei Han',
        'price': 95.0,
        'description': '数据挖掘领域的权威教材',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '推荐系统实践',
        'author': '项亮',
        'price': 42.0,
        'description': '推荐系统的设计与实现指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'Web性能权威指南',
        'author': 'Ilya Grigorik',
        'price': 95.0,
        'description': 'Web性能优化的权威指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '图解HTTP',
        'author': '上野宣',
        'price': 49.0,
        'description': 'HTTP协议的图解指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'TCP/IP详解 卷1',
        'author': 'Kevin R. Fall',
        'price': 128.0,
        'description': 'TCP/IP协议的权威详解',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '网络安全技术',
        'author': 'William Stallings',
        'price': 88.0,
        'description': '网络安全技术的全面指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '操作系统概念',
        'author': 'Abraham Silberschatz',
        'price': 119.0,
        'description': '操作系统概念的经典教材',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '计算机网络',
        'author': '谢希仁',
        'price': 45.0,
        'description': '计算机网络的经典教材',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '编译原理',
        'author': 'Alfred V. Aho',
        'price': 78.0,
        'description': '编译原理的经典教材',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '软件工程导论',
        'author': '张海藩',
        'price': 32.0,
        'description': '软件工程的经典教材',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'UML和模式应用',
        'author': 'Craig Larman',
        'price': 68.0,
        'description': 'UML建模和设计模式应用指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '敏捷软件开发',
        'author': 'Robert C. Martin',
        'price': 59.0,
        'description': '敏捷软件开发原则、模式与实践',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '持续集成与交付',
        'author': 'Jez Humble',
        'price': 75.0,
        'description': '持续集成与交付的实践指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': 'DevOps实践指南',
        'author': 'Gene Kim',
        'price': 85.0,
        'description': 'DevOps实施的实践指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '领域驱动设计',
        'author': 'Eric Evans',
        'price': 95.0,
        'description': '复杂软件设计的建模与架构指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    },
    {
        'title': '微服务设计',
        'author': 'Sam Newman',
        'price': 62.0,
        'description': '微服务架构的设计指南',
        'stock': random.randint(5, 20),
        'created_at': datetime.now()
    }
]

# 添加所有书籍到数据库
result = db.book.insert_many(more_books)
print(f"成功添加 {len(result.inserted_ids)} 本书籍到数据库")

# 统计总数
total_books = db.book.count_documents({})
print(f"现在数据库中共有 {total_books} 本书籍")

client.close()
print("数据库连接已关闭")