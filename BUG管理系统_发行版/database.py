import sqlite3
from datetime import datetime
import threading
import hashlib
import secrets

# 全局标志，确保表只创建一次
_table_created = False
_table_lock = threading.Lock()

def get_connection():
    """获取当前线程的数据库连接"""
    if not hasattr(threading.current_thread(), 'conn'):
        setattr(threading.current_thread(), 'conn', sqlite3.connect('bugs.db', check_same_thread=False))
    
    # 确保表结构只初始化一次
    global _table_created
    with _table_lock:
        if not _table_created:
            initialize_database(getattr(threading.current_thread(), 'conn'))
            _table_created = True
    
    return getattr(threading.current_thread(), 'conn')

# 初始化数据库（迁移式表结构更新）
def initialize_database(conn):
    cursor = conn.cursor()
    
    # 创建/更新bugs表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bugs'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        # 表不存在，创建新表
        print("创建新的bugs表...")
        cursor.execute('''
            CREATE TABLE bugs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                version TEXT NOT NULL,
                region TEXT NOT NULL,
                submitter TEXT NOT NULL,
                assignee_id INTEGER,
                status TEXT DEFAULT '待处理',
                screenshot TEXT,
                log_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        ''')
        print("bugs表创建成功")
    else:
        # 表存在，检查并添加缺失字段
        print("检查bugs表结构...")
        required_columns = ['id', 'title', 'description', 'version', 'region', 'submitter', 'assignee_id', 'status', 'screenshot', 'log_file', 'created_at', 'resolved_at']
        
        cursor.execute("PRAGMA table_info(bugs)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        for required_col in required_columns:
            if required_col not in existing_columns:
                if required_col == 'assignee_id':
                    cursor.execute("ALTER TABLE bugs ADD COLUMN assignee_id INTEGER")
                    print(f"添加assignee_id字段")
                elif required_col == 'status':
                    cursor.execute("ALTER TABLE bugs ADD COLUMN status TEXT DEFAULT '待处理'")
                    print(f"添加status字段")
                elif required_col == 'resolved_at':
                    cursor.execute("ALTER TABLE bugs ADD COLUMN resolved_at TIMESTAMP")
                    print(f"添加resolved_at字段")
                elif required_col == 'screenshot':
                    cursor.execute("ALTER TABLE bugs ADD COLUMN screenshot TEXT")
                    print(f"添加screenshot字段")
                elif required_col == 'log_file':
                    cursor.execute("ALTER TABLE bugs ADD COLUMN log_file TEXT")
                    print(f"添加log_file字段")
    
    # 创建/更新users表（用户认证）
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    users_table_exists = cursor.fetchone()
    
    if not users_table_exists:
        print("创建新的users表...")
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'tester',
                email TEXT UNIQUE,
                real_name TEXT,
                status TEXT DEFAULT 'active',
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("users表创建成功")
        
        # 创建默认管理员账户
        admin_salt = secrets.token_hex(16)
        admin_password = "admin123"  # 默认密码
        admin_hash = hashlib.sha256((admin_password + admin_salt).encode()).hexdigest()
        
        default_users = [
            ('admin', admin_hash, admin_salt, 'admin', 'admin@company.com', '系统管理员', 'active'),
            ('pm', hashlib.sha256(("pm123" + admin_salt).encode()).hexdigest(), admin_salt, 'pm', 'pm@company.com', '项目经理', 'active'),
            ('tester', hashlib.sha256(("test123" + admin_salt).encode()).hexdigest(), admin_salt, 'tester', 'tester@company.com', '测试人员', 'active')
        ]
        
        cursor.executemany('''
            INSERT INTO users (username, password_hash, salt, role, email, real_name, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', default_users)
        print("添加默认用户账户")
    
    # 创建/更新developers表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='developers'")
    dev_table_exists = cursor.fetchone()
    
    if not dev_table_exists:
        print("创建新的developers表...")
        cursor.execute('''
            CREATE TABLE developers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                email TEXT UNIQUE,
                role TEXT DEFAULT '开发工程师',
                status TEXT DEFAULT '活跃',
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("developers表创建成功")
        # 添加一些默认研发人员
        default_developers = [
            ('张三', 'zhangsan@company.com', '高级工程师', '活跃', None),
            ('李四', 'lisi@company.com', '开发工程师', '活跃', None),
            ('王五', 'wangwu@company.com', '测试工程师', '活跃', None),
            ('赵六', 'zhaoliu@company.com', '架构师', '活跃', None)
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO developers (name, email, role, status, user_id) 
            VALUES (?, ?, ?, ?, ?)
        ''', default_developers)
        print("添加默认研发人员")
    else:
        print("检查developers表结构...")
        dev_required_columns = ['id', 'name', 'email', 'role', 'status', 'user_id', 'created_at']
        
        cursor.execute("PRAGMA table_info(developers)")
        dev_existing_columns = [column[1] for column in cursor.fetchall()]
        
        for required_col in dev_required_columns:
            if required_col not in dev_existing_columns:
                if required_col == 'email':
                    cursor.execute("ALTER TABLE developers ADD COLUMN email TEXT UNIQUE")
                    print(f"添加email字段")
                elif required_col == 'role':
                    cursor.execute("ALTER TABLE developers ADD COLUMN role TEXT DEFAULT '开发工程师'")
                    print(f"添加role字段")
                elif required_col == 'status':
                    cursor.execute("ALTER TABLE developers ADD COLUMN status TEXT DEFAULT '活跃'")
                    print(f"添加status字段")
                elif required_col == 'user_id':
                    cursor.execute("ALTER TABLE developers ADD COLUMN user_id INTEGER")
                    print(f"添加user_id字段")
                elif required_col == 'created_at':
                    cursor.execute("ALTER TABLE developers ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    print(f"添加created_at字段")
    
    # 验证最终表结构
    print("=== bugs表结构 ===")
    cursor.execute("PRAGMA table_info(bugs)")
    for col in cursor.fetchall():
        print(f"  - {col[1]} ({col[2]})")
    
    print("=== developers表结构 ===")
    cursor.execute("PRAGMA table_info(developers)")
    for col in cursor.fetchall():
        print(f"  - {col[1]} ({col[2]})")
    
    conn.commit()
    print("数据库初始化完成")

# 研发人员管理函数
def create_developer(name, email=None, role='开发工程师', status='活跃'):
    """创建新研发人员"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO developers (name, email, role, status) 
            VALUES (?, ?, ?, ?)
        ''', (name, email, role, status))
        dev_id = cursor.lastrowid
        conn.commit()
        print(f"创建研发人员成功: {name}, ID: {dev_id}")
        return dev_id
    except sqlite3.IntegrityError as e:
        print(f"创建研发人员失败: {e}")
        return None

def get_developers(search=None, role=None, status=None, page=1, page_size=10):
    """获取研发人员列表，支持搜索、分页、过滤"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 基础查询
    query = '''
        SELECT id, name, email, role, status, created_at 
        FROM developers 
        WHERE 1=1
    '''
    params = []
    
    # 搜索条件
    if search:
        query += " AND name LIKE ?"
        params.append(f"%{search}%")
    
    if role and role != "所有":
        query += " AND role = ?"
        params.append(role)
    
    if status and status != "所有":
        query += " AND status = ?"
        params.append(status)
    
    # 分页
    offset = (page - 1) * page_size
    query += " ORDER BY name ASC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    
    cursor.execute(query, params)
    developers = cursor.fetchall()
    
    # 获取总记录数（移除LIMIT和OFFSET）
    count_query = '''
        SELECT COUNT(*) FROM developers 
        WHERE 1=1
    '''
    count_params = []
    if search:
        count_query += " AND name LIKE ?"
        count_params.append(f"%{search}%")
    if role and role != "所有":
        count_query += " AND role = ?"
        count_params.append(role)
    if status and status != "所有":
        count_query += " AND status = ?"
        count_params.append(status)
    
    cursor.execute(count_query, count_params)
    total_count = cursor.fetchone()[0]
    
    result = []
    for dev in developers:
        result.append({
            'id': dev[0],
            'name': dev[1],
            'email': dev[2],
            'role': dev[3],
            'status': dev[4],
            'created_at': dev[5]
        })
    
    print(f"查询到 {len(result)} / {total_count} 条研发人员记录")
    return result, total_count

def get_developer_by_id(dev_id):
    """根据ID获取单个研发人员"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, email, role, status, created_at 
        FROM developers WHERE id = ?
    ''', (dev_id,))
    row = cursor.fetchone()
    if row:
        return {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'role': row[3],
            'status': row[4],
            'created_at': row[5]
        }
    return None

def update_developer(dev_id, name=None, email=None, role=None, status=None):
    """更新研发人员信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if email is not None:
        updates.append("email = ?")
        params.append(email)
    if role is not None:
        updates.append("role = ?")
        params.append(role)
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    
    if updates:
        params.append(dev_id)
        query = f"UPDATE developers SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        affected = cursor.rowcount
        conn.commit()
        print(f"更新研发人员 {dev_id} 成功，影响行数: {affected}")
        return affected > 0
    return False

def delete_developer(dev_id):
    """删除研发人员（级联检查）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查是否有BUG分配给该研发人员
    cursor.execute('SELECT COUNT(*) FROM bugs WHERE assignee_id = ?', (dev_id,))
    bug_count = cursor.fetchone()[0]
    
    if bug_count > 0:
        print(f"无法删除研发人员 {dev_id}，还有 {bug_count} 个BUG分配给该人员")
        return False
    
    # 删除研发人员
    cursor.execute('DELETE FROM developers WHERE id = ?', (dev_id,))
    affected = cursor.rowcount
    conn.commit()
    print(f"删除研发人员 {dev_id} 成功，影响行数: {affected}")
    return affected > 0

# 用户认证和权限管理函数
def create_user(username, password, role='tester', email=None, real_name=None):
    """创建新用户"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 生成盐值和密码哈希
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, salt, role, email, real_name) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, salt, role, email, real_name))
        
        user_id = cursor.lastrowid
        conn.commit()
        print(f"创建用户成功: {username}, ID: {user_id}")
        return user_id
    except sqlite3.IntegrityError as e:
        print(f"创建用户失败: {e}")
        return None

def authenticate_user(username, password):
    """用户认证"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, password_hash, salt, role, email, real_name, status 
        FROM users WHERE username = ? AND status = 'active'
    ''', (username,))
    
    user = cursor.fetchone()
    if user:
        user_id, username, stored_hash, salt, role, email, real_name, status = user
        # 验证密码
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        if password_hash == stored_hash:
            # 更新最后登录时间
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
            conn.commit()
            
            print(f"用户 {username} 登录成功")
            return {
                'id': user_id,
                'username': username,
                'role': role,
                'email': email,
                'real_name': real_name
            }
    
    print(f"用户 {username} 认证失败")
    return None

def get_user_by_id(user_id):
    """根据ID获取用户信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, role, email, real_name, status, created_at, last_login 
        FROM users WHERE id = ?
    ''', (user_id,))
    
    row = cursor.fetchone()
    if row:
        return {
            'id': row[0],
            'username': row[1],
            'role': row[2],
            'email': row[3],
            'real_name': row[4],
            'status': row[5],
            'created_at': row[6],
            'last_login': row[7]
        }
    return None

def check_permission(user_role, action):
    """检查用户权限"""
    permissions = {
        'admin': ['all'],  # 管理员拥有所有权限
        'pm': ['view_bugs', 'create_bug', 'edit_bug', 'delete_bug', 'manage_developers', 'view_stats', 'export_data'],
        'developer': ['view_bugs', 'create_bug', 'edit_own_bug', 'view_stats'],
        'tester': ['view_bugs', 'create_bug', 'edit_own_bug', 'view_stats'],
        'guest': ['view_bugs', 'view_stats']
    }
    
    user_permissions = permissions.get(user_role, [])
    return 'all' in user_permissions or action in user_permissions

def get_all_users(search=None, role=None, page=1, page_size=10):
    """获取用户列表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT id, username, role, email, real_name, status, created_at, last_login 
        FROM users WHERE 1=1
    '''
    params = []
    
    if search:
        query += " AND (username LIKE ? OR real_name LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    if role and role != "所有":
        query += " AND role = ?"
        params.append(role)
    
    # 分页
    offset = (page - 1) * page_size
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    
    cursor.execute(query, params)
    users = cursor.fetchall()
    
    # 获取总数
    count_query = "SELECT COUNT(*) FROM users WHERE 1=1"
    count_params = []
    if search:
        count_query += " AND (username LIKE ? OR real_name LIKE ?)"
        count_params.extend([f"%{search}%", f"%{search}%"])
    if role and role != "所有":
        count_query += " AND role = ?"
        count_params.append(role)
    
    cursor.execute(count_query, count_params)
    total_count = cursor.fetchone()[0]
    
    result = []
    for user in users:
        result.append({
            'id': user[0],
            'username': user[1],
            'role': user[2],
            'email': user[3],
            'real_name': user[4],
            'status': user[5],
            'created_at': user[6],
            'last_login': user[7]
        })
    
    return result, total_count

def update_user(user_id, username=None, role=None, email=None, real_name=None, status=None):
    """更新用户信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if username is not None:
        updates.append("username = ?")
        params.append(username)
    if role is not None:
        updates.append("role = ?")
        params.append(role)
    if email is not None:
        updates.append("email = ?")
        params.append(email)
    if real_name is not None:
        updates.append("real_name = ?")
        params.append(real_name)
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    
    if updates:
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        affected = cursor.rowcount
        conn.commit()
        print(f"更新用户 {user_id} 成功，影响行数: {affected}")
        return affected > 0
    return False

def change_user_password(user_id, new_password):
    """修改用户密码"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 生成新的盐值和密码哈希
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((new_password + salt).encode()).hexdigest()
    
    cursor.execute('''
        UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
    ''', (password_hash, salt, user_id))
    
    affected = cursor.rowcount
    conn.commit()
    print(f"修改用户 {user_id} 密码成功")
    return affected > 0

def delete_user(user_id):
    """删除用户（软删除）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查是否为最后一个管理员
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin" AND status = "active"')
    admin_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
    user_role = cursor.fetchone()
    
    if user_role and user_role[0] == 'admin' and admin_count <= 1:
        print(f"无法删除用户 {user_id}，至少需要保留一个管理员账户")
        return False
    
    # 软删除（设置状态为inactive）
    cursor.execute('UPDATE users SET status = "inactive" WHERE id = ?', (user_id,))
    affected = cursor.rowcount
    conn.commit()
    print(f"删除用户 {user_id} 成功（软删除）")
    return affected > 0

# BUG相关函数（新增编辑和删除功能）
def create_bug(title, description, version, region, submitter, assignee_name=None, status='待处理', screenshot=None, log_file=None):
    """创建BUG，支持研发人员名称分配"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 如果分配了研发人员，获取其ID
    assignee_id = None
    if assignee_name and assignee_name != "未分配":
        cursor.execute('SELECT id FROM developers WHERE name = ?', (assignee_name,))
        result = cursor.fetchone()
        if result:
            assignee_id = result[0]
        else:
            print(f"警告: 研发人员 {assignee_name} 不存在，使用未分配")
    
    print(f"正在插入BUG: {title} by {submitter}, 分配: {assignee_name or '未分配'}")
    cursor.execute('''
        INSERT INTO bugs (title, description, version, region, submitter, assignee_id, status, screenshot, log_file) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, version, region, submitter, assignee_id, status, screenshot, log_file))
    
    bug_id = cursor.lastrowid
    print(f"插入成功，BUG ID: {bug_id}")
    
    conn.commit()
    print(f"事务已提交，影响行数: {cursor.rowcount}")
    return bug_id

def update_bug(bug_id, title=None, description=None, version=None, region=None, 
               status=None, assignee_name=None, screenshot=None, log_file=None):
    """更新BUG信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if version is not None:
        updates.append("version = ?")
        params.append(version)
    if region is not None:
        updates.append("region = ?")
        params.append(region)
    if status is not None:
        updates.append("status = ?")
        params.append(status)
        if status == "已解决":
            updates.append("resolved_at = CURRENT_TIMESTAMP")
    if screenshot is not None:
        updates.append("screenshot = ?")
        params.append(screenshot)
    if log_file is not None:
        updates.append("log_file = ?")
        params.append(log_file)
    
    # 处理研发人员分配
    if assignee_name is not None:
        assignee_id = None
        if assignee_name and assignee_name != "未分配":
            cursor.execute('SELECT id FROM developers WHERE name = ?', (assignee_name,))
            result = cursor.fetchone()
            if result:
                assignee_id = result[0]
        
        updates.append("assignee_id = ?")
        params.append(assignee_id)
    
    if updates:
        params.append(bug_id)
        query = f"UPDATE bugs SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        affected = cursor.rowcount
        conn.commit()
        print(f"更新BUG {bug_id} 成功，影响行数: {affected}")
        return affected > 0
    return False

def delete_bug(bug_id):
    """删除BUG"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 获取BUG信息用于日志
    cursor.execute('SELECT title, submitter FROM bugs WHERE id = ?', (bug_id,))
    bug_info = cursor.fetchone()
    
    if bug_info:
        cursor.execute('DELETE FROM bugs WHERE id = ?', (bug_id,))
        affected = cursor.rowcount
        conn.commit()
        print(f"删除BUG {bug_id} ({bug_info[0]}) 成功，影响行数: {affected}")
        return affected > 0
    else:
        print(f"BUG {bug_id} 不存在")
        return False

def get_user_submitted_bugs(submitter_name):
    """获取用户提交的BUG列表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT b.id, b.title, b.version, b.region, b.submitter, b.status, b.created_at,
               d.name as assignee_name
        FROM bugs b 
        LEFT JOIN developers d ON b.assignee_id = d.id 
        WHERE b.submitter = ?
        ORDER BY b.created_at DESC
    ''', (submitter_name,))
    
    rows = cursor.fetchall()
    result = [
        {
            'id': row[0],
            'title': row[1],
            'version': row[2],
            'region': row[3],
            'submitter': row[4],
            'status': row[5],
            'created_at': row[6],
            'assignee': row[7] or '未分配'
        } for row in rows
    ]
    
    print(f"查询到用户 {submitter_name} 提交的 {len(result)} 条BUG记录")
    return result

def get_developer_assigned_bugs(developer_name):
    """获取分配给指定研发人员的BUG列表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT b.id, b.title, b.version, b.region, b.submitter, b.status, b.created_at,
               d.name as assignee_name
        FROM bugs b 
        JOIN developers d ON b.assignee_id = d.id 
        WHERE d.name = ?
        ORDER BY b.created_at DESC
    ''', (developer_name,))
    
    rows = cursor.fetchall()
    result = [
        {
            'id': row[0],
            'title': row[1],
            'version': row[2],
            'region': row[3],
            'submitter': row[4],
            'status': row[5],
            'created_at': row[6],
            'assignee': row[7]
        } for row in rows
    ]
    
    print(f"查询到分配给 {developer_name} 的 {len(result)} 条BUG记录")
    return result
    """创建新BUG，支持研发人员名称分配"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 如果分配了研发人员，获取其ID
    assignee_id = None
    if assignee_name and assignee_name != "未分配":
        cursor.execute('SELECT id FROM developers WHERE name = ?', (assignee_name,))
        result = cursor.fetchone()
        if result:
            assignee_id = result[0]
        else:
            print(f"警告: 研发人员 {assignee_name} 不存在，使用未分配")
    
    print(f"正在插入BUG: {title} by {submitter}, 分配: {assignee_name or '未分配'}")
    cursor.execute('''
        INSERT INTO bugs (title, description, version, region, submitter, assignee_id, status, screenshot, log_file) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, version, region, submitter, assignee_id, status, screenshot, log_file))
    
    bug_id = cursor.lastrowid
    print(f"插入成功，BUG ID: {bug_id}")
    
    conn.commit()
    print(f"事务已提交，影响行数: {cursor.rowcount}")
    return bug_id

def update_bug_status(bug_id, status, assignee_name=None):
    """更新BUG状态和分配"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 获取新分配研发人员的ID
    assignee_id = None
    if assignee_name and assignee_name != "未分配":
        cursor.execute('SELECT id FROM developers WHERE name = ?', (assignee_name,))
        result = cursor.fetchone()
        if result:
            assignee_id = result[0]
    
    print(f"正在更新BUG {bug_id} 状态为: {status}, 分配: {assignee_name or '未分配'}")
    
    if assignee_id:
        cursor.execute('''
            UPDATE bugs SET status = ?, assignee_id = ?, resolved_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (status, assignee_id, bug_id))
    else:
        cursor.execute('''
            UPDATE bugs SET status = ?, resolved_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (status, bug_id))
    
    affected = cursor.rowcount
    conn.commit()
    print(f"更新成功，影响行数: {affected}")
    return affected > 0

def get_user_bugs():
    """获取BUG列表（包含研发人员名称）"""
    conn = get_connection()
    cursor = conn.cursor()
    print("正在查询BUG列表...")
    cursor.execute('''
        SELECT b.id, b.title, b.version, b.region, b.submitter, b.status, b.created_at,
               d.name as assignee_name
        FROM bugs b 
        LEFT JOIN developers d ON b.assignee_id = d.id 
        ORDER BY b.created_at DESC
    ''')
    rows = cursor.fetchall()
    print(f"查询到 {len(rows)} 条记录")
    
    result = [
        {
            'id': row[0],
            'title': row[1],
            'version': row[2],
            'region': row[3],
            'submitter': row[4],
            'status': row[5],
            'created_at': row[6],
            'assignee': row[7] or '未分配'
        } for row in rows
    ]
    return result

def get_bug_details(bug_id):
    """获取单个BUG详情（包含研发人员名称）"""
    conn = get_connection()
    cursor = conn.cursor()
    print(f"正在查询BUG详情 ID: {bug_id}")
    cursor.execute('''
        SELECT b.title, b.description, b.version, b.region, b.submitter, b.status, 
               b.screenshot, b.log_file, b.created_at, b.resolved_at,
               d.name as assignee_name
        FROM bugs b 
        LEFT JOIN developers d ON b.assignee_id = d.id 
        WHERE b.id = ?
    ''', (bug_id,))
    row = cursor.fetchone()
    if row:
        print(f"找到BUG详情: {row[0]} by {row[4]}, Status: {row[5]}")
        return {
            'id': bug_id,
            'title': row[0],
            'description': row[1],
            'version': row[2],
            'region': row[3],
            'submitter': row[4],
            'status': row[5],
            'screenshot': row[6],
            'log_file': row[7],
            'created_at': row[8],
            'resolved_at': row[9],
            'assignee': row[10] or '未分配'
        }
    else:
        print(f"未找到BUG ID: {bug_id}")
    return None

def get_bug_stats():
    """获取BUG统计信息（增强版）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 基本统计
    cursor.execute('SELECT COUNT(*) FROM bugs')
    total = cursor.fetchone()[0]
    
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('SELECT COUNT(*) FROM bugs WHERE strftime("%Y-%m", created_at) = ?', (current_month,))
    monthly = cursor.fetchone()[0]
    
    # 已解决BUG统计
    cursor.execute('SELECT COUNT(*) FROM bugs WHERE status = "已解决"')
    resolved = cursor.fetchone()[0]
    
    # 按提交人统计
    cursor.execute('SELECT submitter, COUNT(*) FROM bugs GROUP BY submitter')
    submitter_stats = dict(cursor.fetchall())
    
    # 按状态统计
    cursor.execute('SELECT status, COUNT(*) FROM bugs GROUP BY status')
    status_stats = dict(cursor.fetchall())
    
    # 按研发人员统计（已分配的BUG）
    cursor.execute('''
        SELECT d.name, COUNT(*) 
        FROM bugs b 
        LEFT JOIN developers d ON b.assignee_id = d.id 
        WHERE b.assignee_id IS NOT NULL 
        GROUP BY d.id, d.name
    ''')
    assignee_stats = dict(cursor.fetchall())
    
    # 按月统计（最近12个月）
    cursor.execute('''
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) 
        FROM bugs 
        GROUP BY month 
        ORDER BY month DESC 
        LIMIT 12
    ''')
    monthly_trend = cursor.fetchall()
    
    print(f"统计信息 - 总计: {total}, 本月: {monthly}, 已解决: {resolved}")
    print(f"提交人统计: {submitter_stats}")
    print(f"状态统计: {status_stats}")
    print(f"研发人员统计: {assignee_stats}")
    
    return {
        'total': total,
        'monthly': monthly,
        'resolved': resolved,
        'submitter_stats': submitter_stats,
        'status_stats': status_stats,
        'assignee_stats': assignee_stats,
        'monthly_trend': monthly_trend
    }

# 关闭所有连接（用于清理）
def close_connections():
    if hasattr(threading.current_thread(), 'conn'):
        getattr(threading.current_thread(), 'conn').close()