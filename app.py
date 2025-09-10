import streamlit as st
from database import (create_bug, get_user_bugs, get_bug_details, get_bug_stats, update_bug_status, 
                     get_connection, create_developer, get_developers, get_developer_by_id, 
                     update_developer, delete_developer, update_bug, delete_bug,
                     authenticate_user, check_permission, get_user_by_id, create_user,
                     get_all_users, update_user, change_user_password, delete_user)
import os
import time
import pandas as pd
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 页面配置
st.set_page_config(
    page_title="个人BUG管理系统",
    page_icon="🐛",
    layout="wide"
)

# 初始化会话状态
if 'current_page' not in st.session_state:
    st.session_state.current_page = "submit"
if 'user' not in st.session_state:
    st.session_state.user = None
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False

# 登录页面
def show_login_page():
    st.title("🔐 用户登录")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("### 👋 欢迎使用BUG管理系统")
            username = st.text_input("👤 用户名", placeholder="请输入用户名")
            password = st.text_input("🔑 密码", type="password", placeholder="请输入密码")
            
            submitted = st.form_submit_button("🚀 登录", use_container_width=True)
            
            if submitted:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.is_authenticated = True
                        st.success(f"✅ 欢迎，{user['real_name'] or user['username']}! 正在跳转...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ 用户名或密码错误")
                else:
                    st.error("❌ 请填写用户名和密码")
        
        # 默认账户提示
        st.markdown("---")
        st.info("📝 **默认测试账户**\n\n"
                "👑 管理员: admin / admin123\n\n"
                "📋 项目经理: pm / pm123\n\n"
                "👨‍🗺 测试人员: tester / test123")

# 注销功能
def logout():
    st.session_state.user = None
    st.session_state.is_authenticated = False
    st.session_state.current_page = "submit"
    st.rerun()

# 检查是否登录
if not st.session_state.is_authenticated:
    show_login_page()
    st.stop()

# 已登录用户的主界面
current_user = st.session_state.user
user_role = current_user['role']

# 侧边栏图标导航
st.sidebar.title("🐛 BUG管理系统")

# 用户信息显示
st.sidebar.markdown("---")
with st.sidebar:
    col1, col2 = st.columns([1, 3])
    with col1:
        # 根据角色显示不同图标
        role_icons = {
            'admin': '👑',
            'pm': '📋', 
            'developer': '👨‍🗺',
            'tester': '👨‍🔬',
            'guest': '👥'
        }
        st.markdown(f"### {role_icons.get(user_role, '👤')}")
    with col2:
        st.markdown(f"**{current_user['real_name'] or current_user['username']}**")
        
        role_names = {
            'admin': '管理员',
            'pm': '项目经理',
            'developer': '研发人员',
            'tester': '测试人员',
            'guest': '访客'
        }
        st.caption(f"{role_names.get(user_role, user_role)}")

# 注销按钮
if st.sidebar.button("😪 退出登录", use_container_width=True):
    logout()

st.sidebar.markdown("---")

# 导航按钮配置（根据权限过滤）
nav_config = []

# 所有用户都可以查看统计
if check_permission(user_role, 'view_stats'):
    nav_config.append({"key": "stats", "label": "📊 统计", "icon": "📊"})

# 所有用户都可以查看列表
if check_permission(user_role, 'view_bugs'):
    nav_config.append({"key": "list", "label": "📋 BUG列表", "icon": "📋"})

# 只有有创建BUG权限的用户才能提交
if check_permission(user_role, 'create_bug'):
    nav_config.append({"key": "submit", "label": "📝 提交BUG", "icon": "📝"})

# 只有管理员和项目经理才能管理研发人员
if check_permission(user_role, 'manage_developers'):
    nav_config.append({"key": "developers", "label": "👨‍💻 研发管理", "icon": "👨‍💻"})

# 只有管理员才能管理用户
if user_role == 'admin':
    nav_config.append({"key": "users", "label": "👥 用户管理", "icon": "👥"})

# 当前选中状态
selected_page = st.session_state.current_page

# 创建导航按钮
for item in nav_config:
    if st.sidebar.button(item["label"], key=item["key"], use_container_width=True, 
                        help=f"点击进入{item['label']}页面"):
        st.session_state.current_page = item["key"]
        st.rerun()

# 添加分隔线和说明
st.sidebar.markdown("---")
st.sidebar.caption("点击左侧按钮切换功能")

# 创建文件存储目录
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# 根据页面和权限显示内容
if selected_page == "submit" and check_permission(user_role, 'create_bug'):
    st.title("📝 提交新的BUG")
    
    # 提交表单
    with st.form("bug_form"):
        col1, col2 = st.columns(2)
        with col1:
            # 使用当前用户信息作为默认提交人
            default_submitter = current_user['real_name'] or current_user['username']
            submitter = st.text_input("👤 提交人姓名", 
                                    value=default_submitter, 
                                    help="请填写您的姓名", 
                                    placeholder="例如：张三")
        with col2:
            version = st.text_input("🔢 版本信息", placeholder="例如：v1.0.0", help="软件或系统的版本号")
        
        col1, col2 = st.columns(2)
        with col1:
            bug_title = st.text_input("📌 BUG标题", help="请填写BUG的简短标题")
        with col2:
            region = st.text_input("🌍 供货地区", placeholder="例如：中国/北美", help="产品供货地区")
        
        bug_description = st.text_area("📄 BUG描述", help="详细描述问题现象", height=150)
        
        # 动态加载研发人员列表
        developers, _ = get_developers()
        developer_names = ["未分配"] + [dev['name'] for dev in developers]
        
        col1, col2 = st.columns(2)
        with col1:
            status = st.selectbox("🏷️ 初始状态", ["待处理", "紧急", "一般", "低优先级"], index=0)
        with col2:
            assignee = st.selectbox("👨‍💻 分配研发人员", developer_names, index=0)
        
        col1, col2 = st.columns(2)
        with col1:
            screenshot = st.file_uploader("📸 上传问题截图", type=["png", "jpg", "jpeg"], help="上传问题截图（可选）")
        with col2:
            log_file = st.file_uploader("📋 上传日志文件", type=["txt", "log"], help="上传相关日志文件（可选）")
        
        submitted = st.form_submit_button("🚀 提交BUG", use_container_width=True)
    
    # 提交成功后的处理（表单外部）
    if submitted:
        # 验证必填字段
        if not submitter or not bug_title or not bug_description or not version or not region:
            st.error("❌ 请填写所有必填字段（提交人姓名、标题、描述、版本信息、供货地区）")
        else:
            # 保存文件
            screenshot_path = None
            log_file_path = None
            timestamp = int(time.time())
            
            if screenshot:
                safe_filename = "".join(c for c in screenshot.name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                screenshot_path = os.path.join('uploads', f"screenshot_{timestamp}_{safe_filename}")
                with open(screenshot_path, 'wb') as f:
                    f.write(screenshot.getbuffer())
                st.success("✅ 截图已保存")
            
            if log_file:
                safe_filename = "".join(c for c in log_file.name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                log_file_path = os.path.join('uploads', f"log_{timestamp}_{safe_filename}")
                with open(log_file_path, 'wb') as f:
                    f.write(log_file.getbuffer())
                st.success("✅ 日志文件已保存")

            # 插入BUG记录（使用动态研发人员列表）
            bug_id = create_bug(bug_title, bug_description, version, region, submitter, 
                              assignee if assignee != "未分配" else None, status, 
                              screenshot_path, log_file_path)
            
            # 成功提示 - 模态对话框效果
            st.balloons()
            st.success(f"🎉 BUG提交成功！ID: #{bug_id} (状态: {status}, 分配: {assignee})")
            
            # 模态确认对话框（表单外部）
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("👀 查看我的BUG列表", use_container_width=True, type="primary"):
                    st.session_state.current_page = "list"
                    st.rerun()
            st.markdown("---")
            
            # 提示用户可以继续提交或查看列表
            st.info("💡 您可以继续提交新的BUG，或者点击左侧导航按钮查看已提交的BUG列表")

elif selected_page == "developers" and check_permission(user_role, 'manage_developers'):
    st.title("👨‍💻 研发人员管理")
    
    # 研发人员管理选项卡
    tab1, tab2, tab3 = st.tabs(["📋 人员列表", "➕ 新增人员", "🔧 编辑人员"])
    
    with tab1:
        st.subheader("📋 研发人员列表")
        
        # 搜索和过滤
        col1, col2, col3 = st.columns(3)
        with col1:
            search_name = st.text_input("🔍 搜索姓名", placeholder="输入姓名搜索")
        with col2:
            filter_role = st.selectbox("🎭 筛选角色", ["所有", "开发工程师", "高级工程师", "测试工程师", "架构师"], index=0)
        with col3:
            filter_status = st.selectbox("📊 筛选状态", ["所有", "活跃", "离职"], index=0)
        
        # 分页
        page_size = st.selectbox("每页显示", [5, 10, 20, 50], index=1)
        page = st.number_input("页码", min_value=1, value=1, step=1)
        
        # 获取研发人员列表
        developers, total_count = get_developers(search_name if search_name else None, 
                                               filter_role if filter_role != "所有" else None, 
                                               filter_status if filter_status != "所有" else None, 
                                               page, page_size)
        
        # 显示统计信息
        total_pages = (total_count + page_size - 1) // page_size
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 总人数", total_count)
        with col2:
            st.metric("📊 当前页", f"{len(developers)}/{page_size}")
        with col3:
            st.metric("📄 总页数", total_pages)
        
        # 研发人员表格
        if developers:
            dev_data = []
            for dev in developers:
                dev_data.append({
                    'ID': dev['id'],
                    '姓名': dev['name'],
                    '邮箱': dev['email'] or '未设置',
                    '角色': dev['role'],
                    '状态': dev['status'],
                    '创建时间': dev['created_at'][:10]
                })
            
            df = pd.DataFrame(dev_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # 分页导航
            if total_pages > 1:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("⬅️ 上一页"):
                        if page > 1:
                            st.session_state.current_page = "developers"
                            # 这里需要实现分页跳转逻辑
                with col2:
                    st.write(f"第 {page}/{total_pages} 页")
                with col3:
                    if st.button("➡️ 下一页"):
                        if page < total_pages:
                            st.session_state.current_page = "developers"
        else:
            st.info("📭 暂无研发人员记录")
            st.caption("💡 请点击'新增人员'标签添加第一个研发人员")
    
    with tab2:
        st.subheader("➕ 新增研发人员")
        
        with st.form("add_developer_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("👤 姓名", help="请输入研发人员姓名")
            with col2:
                email = st.text_input("📧 邮箱", help="请输入邮箱地址（可选）")
            
            col1, col2 = st.columns(2)
            with col1:
                role = st.selectbox("🎭 角色", ["开发工程师", "高级工程师", "测试工程师", "架构师", "产品经理"])
            with col2:
                status = st.selectbox("📊 状态", ["活跃", "离职", "试用期"])
            
            submitted = st.form_submit_button("💾 保存", use_container_width=True)
            
            if submitted:
                if not name:
                    st.error("❌ 姓名不能为空")
                else:
                    dev_id = create_developer(name, email if email else None, role, status)
                    if dev_id:
                        st.success(f"✅ 研发人员 {name} 添加成功！ID: #{dev_id}")
                        st.rerun()
                    else:
                        st.error("❌ 添加失败，请检查姓名是否已存在")
    
    with tab3:
        st.subheader("🔧 编辑研发人员")
        
        # 获取所有研发人员用于选择
        all_developers, _ = get_developers()
        
        if all_developers:
            selected_id = st.selectbox("选择要编辑的人员", 
                                     [f"ID: {dev['id']} - {dev['name']} ({dev['role']})" for dev in all_developers])
            
            if selected_id:
                dev_id = int(selected_id.split(" - ")[0].replace("ID: ", ""))
                dev = get_developer_by_id(dev_id)
                
                if dev:
                    with st.form("edit_developer_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input("👤 姓名", value=dev['name'], help="修改姓名")
                        with col2:
                            new_email = st.text_input("📧 邮箱", value=dev['email'] or "", help="修改邮箱地址")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            new_role = st.selectbox("🎭 角色", 
                                                  ["开发工程师", "高级工程师", "测试工程师", "架构师", "产品经理"], 
                                                  index=["开发工程师", "高级工程师", "测试工程师", "架构师", "产品经理"].index(dev['role']))
                        with col2:
                            new_status = st.selectbox("📊 状态", 
                                                    ["活跃", "离职", "试用期"], 
                                                    index=["活跃", "离职", "试用期"].index(dev['status']))
                        
                        submitted = st.form_submit_button("💾 更新", use_container_width=True)
                        
                        if submitted:
                            if new_name != dev['name'] or new_email != (dev['email'] or "") or new_role != dev['role'] or new_status != dev['status']:
                                success = update_developer(dev_id, new_name, new_email if new_email else None, new_role, new_status)
                                if success:
                                    st.success(f"✅ 研发人员 {new_name} 更新成功")
                                    st.rerun()
                                else:
                                    st.error("❌ 更新失败")
                            else:
                                st.info("ℹ️ 没有修改内容")
                    
                    # 删除按钮（表单外部）
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("🗑️ 删除此人员", type="secondary", key=f"delete_{dev_id}"):
                            if delete_developer(dev_id):
                                st.success(f"✅ 研发人员 {dev['name']} 删除成功")
                                st.rerun()
                            else:
                                st.error("❌ 删除失败，该人员可能有BUG分配")
                    st.markdown("---")
                else:
                    st.error("❌ 未找到该研发人员")
        else:
            st.info("📭 暂无研发人员")
            st.caption("💡 请先添加研发人员")

elif selected_page == "stats" and check_permission(user_role, 'view_stats'):
    st.subheader("📊 BUG数据分析与可视化")
    
    # 获取增强统计数据
    stats = get_bug_stats()
    
    # 布局：左侧指标，右侧图表
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("📈 总BUG数", stats['total'])
        st.metric("📅 本月新增", stats['monthly'])
        st.metric("✅ 已解决数", stats['resolved'])
        st.metric("⏳ 解决率", f"{stats['resolved']/max(stats['total'],1)*100:.1f}%")
    
    with col2:
        # 按提交人统计图表
        if stats['submitter_stats']:
            submitter_df = pd.DataFrame(list(stats['submitter_stats'].items()), 
                                      columns=['提交人', 'BUG数量'])
            fig1 = px.bar(submitter_df, x='提交人', y='BUG数量', 
                         title='👤 各提交人BUG提交统计',
                         color='BUG数量', color_continuous_scale='viridis')
            fig1.update_layout(height=300)
            st.plotly_chart(fig1, use_container_width=True)
        
        # 按状态统计饼图
        if stats['status_stats']:
            status_df = pd.DataFrame(list(stats['status_stats'].items()), 
                                   columns=['状态', '数量'])
            fig2 = px.pie(status_df, values='数量', names='状态', 
                         title='🏷️ BUG状态分布')
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)
    
    # 详细统计表格
    st.subheader("📋 详细统计报表")
    
    # 按提交人详细统计
    st.markdown("### 👥 按提交人统计")
    if stats['submitter_stats']:
        submitter_data = []
        for submitter, count in stats['submitter_stats'].items():
            # 计算每个提交人的解决率
            cursor = get_connection().cursor()
            cursor.execute('SELECT COUNT(*) FROM bugs WHERE submitter = ? AND status = "已解决"', (submitter,))
            resolved_count = cursor.fetchone()[0]
            resolve_rate = resolved_count / count * 100 if count > 0 else 0
            
            submitter_data.append({
                '提交人': submitter,
                '总提交数': count,
                '已解决数': resolved_count,
                '解决率': f"{resolve_rate:.1f}%",
                '未解决数': count - resolved_count
            })
        
        submitter_df = pd.DataFrame(submitter_data)
        st.dataframe(submitter_df, use_container_width=True)
    
    # 按月趋势图
    st.markdown("### 📅 按月提交趋势")
    if stats['monthly_trend']:
        trend_df = pd.DataFrame(stats['monthly_trend'], columns=['月份', '数量'])
        trend_df['月份'] = pd.to_datetime(trend_df['月份'] + '-01')
        fig_trend = px.line(trend_df, x='月份', y='数量', 
                           title='📈 每月BUG提交趋势',
                           markers=True)
        fig_trend.update_layout(height=400)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # 按研发人员统计
    st.markdown("### 👨‍💻 按研发人员分配统计")
    if stats['assignee_stats']:
        assignee_df = pd.DataFrame(list(stats['assignee_stats'].items()), 
                                 columns=['研发人员', '分配BUG数'])
        fig_assignee = px.bar(assignee_df, x='研发人员', y='分配BUG数', 
                            title='👨‍💻 各研发人员分配BUG统计',
                            color='分配BUG数', color_continuous_scale='plasma')
        fig_assignee.update_layout(height=300)
        st.plotly_chart(fig_assignee, use_container_width=True)
    
    # 考核指标
    st.markdown("### 🎯 团队考核指标")
    col1, col2, col3 = st.columns(3)
    with col1:
        # 团队平均解决率
        total_resolved = stats['resolved']
        avg_resolve_rate = total_resolved / max(stats['total'], 1) * 100
        st.metric("团队平均解决率", f"{avg_resolve_rate:.1f}%")
    
    with col2:
        # 紧急BUG数量
        cursor = get_connection().cursor()
        cursor.execute('SELECT COUNT(*) FROM bugs WHERE status = "紧急"')
        urgent_bugs = cursor.fetchone()[0]
        st.metric("紧急BUG数量", urgent_bugs)
    
    with col3:
        # 超期未解决
        cursor = get_connection().cursor()
        cursor.execute('SELECT COUNT(*) FROM bugs WHERE status != "已解决" AND created_at < datetime("now", "-7 days")')
        overdue_bugs = cursor.fetchone()[0]
        st.metric("超期未解决", overdue_bugs)

elif selected_page == "list" and check_permission(user_role, 'view_bugs'):
    st.subheader("📋 BUG列表")
    bugs = get_user_bugs()
    
    if not bugs:
        st.info("📭 暂无BUG记录")
        st.caption("💡 快去提交第一个BUG吧！")
    else:
        # 显示BUG统计信息和导出功能
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"📊 总计 {len(bugs)} 个BUG记录")
        with col2:
            # Excel导出功能
            if st.button("📊 导出Excel", key="export_excel", use_container_width=True):
                # 获取所有BUG详细数据
                export_data = []
                for bug in bugs:
                    details = get_bug_details(bug['id'])
                    if details:
                        export_data.append({
                            'ID': details['id'],
                            '标题': details['title'],
                            '提交人': details['submitter'],
                            '分配研发': details['assignee'],
                            '版本': details['version'],
                            '地区': details['region'],
                            '状态': details['status'],
                            '描述': details['description'][:100] + '...' if len(details['description']) > 100 else details['description'],
                            '截图路径': details['screenshot'] or '',
                            '日志路径': details['log_file'] or '',
                            '创建时间': details['created_at'],
                            '解决时间': details['resolved_at'] or ''
                        })
                
                if export_data:
                    # 创建DataFrame
                    df = pd.DataFrame(export_data)
                    
                    # 生成Excel文件
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='BUG记录', index=False)
                        worksheet = writer.sheets['BUG记录']
                        # 设置列宽
                        for column in worksheet.columns:
                            max_length = 0
                            column_letter = column[0].column_letter
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = min(max_length + 2, 50)
                            worksheet.column_dimensions[column_letter].width = adjusted_width
                    
                    # 设置Excel文件名
                    timestamp = int(time.time())
                    filename = f"BUG管理系统_{timestamp}.xlsx"
                    
                    # 提供下载
                    st.download_button(
                        label="💾 下载Excel文件",
                        data=output.getvalue(),
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    st.success(f"✅ Excel文件已准备好下载！包含 {len(export_data)} 条BUG记录")
                else:
                    st.warning("⚠️ 暂无数据可导出")
        
        # 创建卡片式布局
        for bug in bugs:
            with st.expander(f"🔍 {bug['title']} - v{bug['version']} ({bug['region']}) [{bug['status']}]", expanded=False):
                # 基本信息 - 卡片布局
                info_container = st.container()
                with info_container:
                    col1, col2, col3, col4, col5 = st.columns([1.2, 1, 1, 1, 1])
                    with col1:
                        st.write(f"👤 **提交人:** {bug['submitter']}")
                    with col2:
                        st.write(f"🔢 **版本:** {bug['version']}")
                    with col3:
                        st.write(f"🌍 **地区:** {bug['region']}")
                    with col4:
                        st.write(f"🏷️ **状态:** {bug['status']}")
                    with col5:
                        st.write(f"📅 **时间:** {bug['created_at'][:10]}")
                
                # 获取详细报告
                details = get_bug_details(bug['id'])
                if details:
                    st.write("**📄 问题描述:**")
                    st.write(details['description'])
                    
                    # 分配信息
                    if details['assignee'] != '未分配':
                        st.write(f"👨‍💻 **分配研发人员:** {details['assignee']}")
                    else:
                        st.warning("⚠️ 该BUG尚未分配研发人员")
                    
                    # 显示附件
                    if details['screenshot']:
                        st.image(details['screenshot'], caption="📸 问题截图", use_container_width=True)
                    
                    if details['log_file']:
                        try:
                            with open(details['log_file'], 'r', encoding='utf-8') as f:
                                log_content = f.read()
                                with st.expander("📋 查看日志内容", expanded=False):
                                    st.code(log_content, language='text')
                            st.download_button(
                                label="💾 下载日志文件",
                                data=open(details['log_file'], 'rb').read(),
                                file_name=os.path.basename(details['log_file']),
                                mime="text/plain"
                            )
                        except Exception as e:
                            st.error(f"❌ 无法读取日志文件: {e}")
                    
                    # 初始化会话状态
                    if f"reassign_mode_{bug['id']}" not in st.session_state:
                        st.session_state[f"reassign_mode_{bug['id']}"] = False
                    if f"edit_mode_{bug['id']}" not in st.session_state:
                        st.session_state[f"edit_mode_{bug['id']}"] = False
                    
                    # 检查编辑权限（只有管理员、项目经理和提交人可以编辑）
                    can_edit = (
                        user_role == 'admin' or 
                        user_role == 'pm' or 
                        check_permission(user_role, 'edit_bug') or
                        (check_permission(user_role, 'edit_own_bug') and details['submitter'] == (current_user.get('real_name') or current_user.get('username', '')))
                    )
                    
                    # 检查删除权限（只有管理员和项目经理可以删除）
                    can_delete = user_role == 'admin' or user_role == 'pm' or check_permission(user_role, 'delete_bug')
                    
                    # 编辑模式
                    if st.session_state[f"edit_mode_{bug['id']}"]:
                        st.markdown("### 📝 编辑BUG")
                        with st.form(f"edit_bug_form_{bug['id']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                edit_title = st.text_input("📌 标题", value=details['title'])
                            with col2:
                                edit_version = st.text_input("🔢 版本", value=details['version'])
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                edit_region = st.text_input("🌍 地区", value=details['region'])
                            with col2:
                                edit_status = st.selectbox("🏷️ 状态", 
                                                          ["待处理", "紧急", "一般", "低优先级", "已解决"],
                                                          index=["待处理", "紧急", "一般", "低优先级", "已解决"].index(details['status']) if details['status'] in ["待处理", "紧急", "一般", "低优先级", "已解决"] else 0)
                            
                            edit_description = st.text_area("📄 描述", value=details['description'], height=100)
                            
                            # 研发人员分配
                            developers, _ = get_developers()
                            developer_names = ["未分配"] + [dev['name'] for dev in developers]
                            current_assignee = details.get('assignee', '未分配')
                            assignee_index = developer_names.index(current_assignee) if current_assignee in developer_names else 0
                            edit_assignee = st.selectbox("👨‍🗺 分配研发人员", developer_names, index=assignee_index)
                            
                            # 表单按钮
                            col1, col2 = st.columns(2)
                            with col1:
                                update_submitted = st.form_submit_button("💾 保存更新", use_container_width=True, type="primary")
                            with col2:
                                cancel_edit = st.form_submit_button("❌ 取消编辑", use_container_width=True)
                            
                            if update_submitted:
                                # 更新BUG
                                success = update_bug(
                                    bug['id'],
                                    title=edit_title,
                                    description=edit_description,
                                    version=edit_version,
                                    region=edit_region,
                                    status=edit_status,
                                    assignee_name=edit_assignee if edit_assignee != "未分配" else None
                                )
                                
                                if success:
                                    st.success(f"✅ BUG #{bug['id']} 更新成功！")
                                    st.session_state[f"edit_mode_{bug['id']}"] = False
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ 更新BUG #{bug['id']} 失败")
                            
                            if cancel_edit:
                                st.session_state[f"edit_mode_{bug['id']}"] = False
                                st.rerun()
                    
                    else:
                        # 正常显示模式 - 状态操作按钮
                        button_cols = []
                        
                        # 标记为已解决按钮
                        if details['status'] != '已解决':
                            button_cols.append('resolve')
                        
                        # 重新分配按钮
                        if check_permission(user_role, 'edit_bug') or user_role in ['admin', 'pm']:
                            button_cols.append('reassign')
                        
                        # 编辑按钮
                        if can_edit:
                            button_cols.append('edit')
                        
                        # 删除按钮
                        if can_delete:
                            button_cols.append('delete')
                        
                        # 创建按钮布局
                        if button_cols:
                            cols = st.columns(len(button_cols))
                            
                            col_idx = 0
                            
                            # 标记为已解决
                            if 'resolve' in button_cols:
                                with cols[col_idx]:
                                    if st.button(f"✅ 标记为已解决 #{bug['id']}", key=f"resolve_{bug['id']}", use_container_width=True):
                                        if update_bug_status(bug['id'], "已解决", details.get('assignee', '未分配')):
                                            st.success(f"🎉 BUG #{bug['id']} 已标记为已解决")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ 标记BUG #{bug['id']} 失败")
                                col_idx += 1
                            
                            # 重新分配
                            if 'reassign' in button_cols:
                                with cols[col_idx]:
                                    if not st.session_state[f"reassign_mode_{bug['id']}"]:
                                        if st.button(f"🔄 重新分配 #{bug['id']}", key=f"reassign_{bug['id']}", use_container_width=True):
                                            st.session_state[f"reassign_mode_{bug['id']}"] = True
                                            st.rerun()
                                col_idx += 1
                            
                            # 编辑按钮
                            if 'edit' in button_cols:
                                with cols[col_idx]:
                                    if st.button(f"📝 编辑 #{bug['id']}", key=f"edit_{bug['id']}", use_container_width=True):
                                        st.session_state[f"edit_mode_{bug['id']}"] = True
                                        st.rerun()
                                col_idx += 1
                            
                            # 删除按钮
                            if 'delete' in button_cols:
                                with cols[col_idx]:
                                    if st.button(f"🗑️ 删除 #{bug['id']}", key=f"delete_{bug['id']}", use_container_width=True, type="secondary"):
                                        # 删除确认
                                        if f"confirm_delete_{bug['id']}" not in st.session_state:
                                            st.session_state[f"confirm_delete_{bug['id']}"] = True
                                            st.warning(f"⚠️ 确认删除BUG #{bug['id']}: {bug['title']}?")
                                            st.rerun()
                        
                        # 删除确认对话框
                        if st.session_state.get(f"confirm_delete_{bug['id']}", False):
                            st.markdown("---")
                            st.warning(f"🚨 **确认删除** BUG #{bug['id']}: {bug['title']}")
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                if st.button("✅ 确认删除", key=f"confirm_delete_yes_{bug['id']}", use_container_width=True, type="primary"):
                                    if delete_bug(bug['id']):
                                        st.success(f"🗑️ BUG #{bug['id']} 已成功删除")
                                        del st.session_state[f"confirm_delete_{bug['id']}"]
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(f"❌ 删除BUG #{bug['id']} 失败")
                            with col2:
                                if st.button("❌ 取消", key=f"confirm_delete_no_{bug['id']}", use_container_width=True):
                                    del st.session_state[f"confirm_delete_{bug['id']}"]
                                    st.rerun()
                        
                        # 重新分配模式
                        if st.session_state[f"reassign_mode_{bug['id']}"]:
                            st.markdown("---")
                            st.markdown("### 🔄 重新分配")
                            # 动态加载研发人员列表
                            developers, _ = get_developers()
                            developer_names = ["未分配"] + [dev['name'] for dev in developers]
                            # 设置默认值为当前分配人员
                            current_assignee = details.get('assignee', '未分配')
                            default_index = developer_names.index(current_assignee) if current_assignee in developer_names else 0
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                new_assignee = st.selectbox(
                                    f"分配给:",
                                    developer_names,
                                    index=default_index,
                                    key=f"assignee_select_{bug['id']}"
                                )
                            with col2:
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.button("💾 确认", key=f"confirm_assign_{bug['id']}", use_container_width=True):
                                        if update_bug_status(bug['id'], details['status'], new_assignee):
                                            st.success(f"✅ BUG #{bug['id']} 已分配给 {new_assignee}")
                                            st.session_state[f"reassign_mode_{bug['id']}"] = False
                                            st.rerun()
                                        else:
                                            st.error(f"❌ 分配失败")
                                
                                with col_b:
                                    if st.button("❌ 取消", key=f"cancel_assign_{bug['id']}", use_container_width=True):
                                        st.session_state[f"reassign_mode_{bug['id']}"] = False
                                        st.rerun()

elif selected_page == "users" and user_role == 'admin':
    st.title("👥 用户管理")
    
    # 用户管理选项卡
    tab1, tab2, tab3 = st.tabs(["📋 用户列表", "➕ 新增用户", "🔧 编辑用户"])
    
    with tab1:
        st.subheader("📋 用户列表")
        
        # 搜索和过滤
        col1, col2, col3 = st.columns(3)
        with col1:
            search_user = st.text_input("🔍 搜索用户", placeholder="输入用户名或姓名")
        with col2:
            filter_user_role = st.selectbox("🎭 筛选角色", ["所有", "admin", "pm", "developer", "tester", "guest"], index=0)
        with col3:
            filter_user_status = st.selectbox("📊 筛选状态", ["所有", "active", "inactive"], index=0)
        
        # 分页
        user_page_size = st.selectbox("每页显示", [5, 10, 20, 50], index=1, key="user_page_size")
        user_page = st.number_input("页码", min_value=1, value=1, step=1, key="user_page")
        
        # 获取用户列表
        users, user_total_count = get_all_users(
            search_user if search_user else None,
            filter_user_role if filter_user_role != "所有" else None,
            user_page, user_page_size
        )
        
        # 显示统计信息
        user_total_pages = (user_total_count + user_page_size - 1) // user_page_size
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 总用户数", user_total_count)
        with col2:
            st.metric("📊 当前页", f"{len(users)}/{user_page_size}")
        with col3:
            st.metric("📄 总页数", user_total_pages)
        
        # 用户表格
        if users:
            user_data = []
            for user in users:
                role_names = {
                    'admin': '👑 管理员',
                    'pm': '📋 项目经理',
                    'developer': '👨‍🗺 研发人员',
                    'tester': '👨‍🔬 测试人员',
                    'guest': '👥 访客'
                }
                
                user_data.append({
                    'ID': user['id'],
                    '用户名': user['username'],
                    '姓名': user['real_name'] or '未设置',
                    '邮箱': user['email'] or '未设置',
                    '角色': role_names.get(user['role'], user['role']),
                    '状态': '🟢 活跃' if user['status'] == 'active' else '🔴 禁用',
                    '创建时间': user['created_at'][:10] if user['created_at'] else '',
                    '最后登录': user['last_login'][:16] if user['last_login'] else '从未登录'
                })
            
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📦 暂无用户记录")
    
    with tab2:
        st.subheader("➕ 新增用户")
        
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("👤 用户名", help="请输入用户名（用于登录）")
            with col2:
                new_real_name = st.text_input("📝 真实姓名", help="请输入真实姓名")
            
            col1, col2 = st.columns(2)
            with col1:
                new_password = st.text_input("🔑 密码", type="password", help="请输入初始密码")
            with col2:
                new_email = st.text_input("📧 邮箱", help="请输入邮箱地址（可选）")
            
            col1, col2 = st.columns(2)
            with col1:
                new_user_role = st.selectbox("🎭 角色", ["tester", "developer", "pm", "admin", "guest"])
            with col2:
                new_user_status = st.selectbox("📊 状态", ["active", "inactive"])
            
            user_submitted = st.form_submit_button("💾 创建用户", use_container_width=True)
            
            if user_submitted:
                if not new_username or not new_password:
                    st.error("❌ 用户名和密码不能为空")
                else:
                    user_id = create_user(
                        new_username, 
                        new_password, 
                        new_user_role, 
                        new_email if new_email else None, 
                        new_real_name if new_real_name else None
                    )
                    if user_id:
                        st.success(f"✅ 用户 {new_username} 创建成功！ID: #{user_id}")
                        st.rerun()
                    else:
                        st.error("❌ 创建失败，请检查用户名是否已存在")
    
    with tab3:
        st.subheader("🔧 编辑用户")
        
        # 获取所有用户用于选择
        all_users, _ = get_all_users()
        
        if all_users:
            selected_user_id = st.selectbox("选择要编辑的用户", 
                                         [f"ID: {user['id']} - {user['username']} ({user['real_name'] or '未设置'})" for user in all_users])
            
            if selected_user_id:
                edit_user_id = int(selected_user_id.split(" - ")[0].replace("ID: ", ""))
                edit_user = get_user_by_id(edit_user_id)
                
                if edit_user:
                    # 用户信息编辑表单
                    with st.form("edit_user_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_username = st.text_input("👤 用户名", value=edit_user['username'], help="修改用户名")
                        with col2:
                            edit_real_name = st.text_input("📝 真实姓名", value=edit_user['real_name'] or "", help="修改真实姓名")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            edit_email = st.text_input("📧 邮箱", value=edit_user['email'] or "", help="修改邮箱地址")
                        with col2:
                            role_options = ["tester", "developer", "pm", "admin", "guest"]
                            edit_role_index = role_options.index(edit_user['role']) if edit_user['role'] in role_options else 0
                            edit_user_role = st.selectbox("🎭 角色", role_options, index=edit_role_index)
                        
                        status_options = ["active", "inactive"]
                        edit_status_index = status_options.index(edit_user['status']) if edit_user['status'] in status_options else 0
                        edit_user_status = st.selectbox("📊 状态", status_options, index=edit_status_index)
                        
                        user_update_submitted = st.form_submit_button("💾 更新", use_container_width=True)
                        
                        if user_update_submitted:
                            if (edit_username != edit_user['username'] or 
                                edit_real_name != (edit_user['real_name'] or "") or 
                                edit_email != (edit_user['email'] or "") or 
                                edit_user_role != edit_user['role'] or 
                                edit_user_status != edit_user['status']):
                                
                                success = update_user(
                                    edit_user_id, 
                                    edit_username, 
                                    edit_user_role, 
                                    edit_email if edit_email else None, 
                                    edit_real_name if edit_real_name else None, 
                                    edit_user_status
                                )
                                if success:
                                    st.success(f"✅ 用户 {edit_username} 更新成功")
                                    st.rerun()
                                else:
                                    st.error("❌ 更新失败")
                            else:
                                st.info("ℹ️ 没有修改内容")
                    
                    # 密码修改功能（表单外部）
                    st.markdown("---")
                    st.markdown("### 🔑 修改密码")
                    
                    # 初始化密码修改模式的会话状态
                    if f"password_mode_{edit_user_id}" not in st.session_state:
                        st.session_state[f"password_mode_{edit_user_id}"] = False
                    
                    if not st.session_state[f"password_mode_{edit_user_id}"]:
                        # 显示修改密码按钮
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button("🔑 修改密码", key=f"show_password_form_{edit_user_id}", use_container_width=True):
                                st.session_state[f"password_mode_{edit_user_id}"] = True
                                st.rerun()
                    else:
                        # 显示密码修改输入框
                        col1, col2 = st.columns(2)
                        with col1:
                            new_password = st.text_input("新密码", type="password", key=f"new_pwd_{edit_user_id}")
                        with col2:
                            confirm_password = st.text_input("确认密码", type="password", key=f"confirm_pwd_{edit_user_id}")
                        
                        col_a, col_b, col_c = st.columns([1, 1, 1])
                        with col_a:
                            if st.button("✅ 确认修改", key=f"confirm_password_{edit_user_id}", use_container_width=True):
                                if not new_password:
                                    st.error("❌ 密码不能为空")
                                elif new_password != confirm_password:
                                    st.error("❌ 两次密码输入不一致")
                                else:
                                    if change_user_password(edit_user_id, new_password):
                                        st.success("✅ 密码修改成功")
                                        st.session_state[f"password_mode_{edit_user_id}"] = False
                                        st.rerun()
                                    else:
                                        st.error("❌ 密码修改失败")
                        with col_b:
                            if st.button("❌ 取消", key=f"cancel_password_{edit_user_id}", use_container_width=True):
                                st.session_state[f"password_mode_{edit_user_id}"] = False
                                st.rerun()
                    
                    # 删除按钮（表单外部）
                    if edit_user['username'] != 'admin':  # 保护默认管理员账户
                        st.markdown("---")
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button(f"🗑️ 删除用户 {edit_user['username']}", type="secondary", key=f"delete_user_{edit_user_id}"):
                                if delete_user(edit_user_id):
                                    st.success(f"✅ 用户 {edit_user['username']} 已被禁用")
                                    st.rerun()
                                else:
                                    st.error("❌ 删除失败")
                        st.markdown("---")
                    else:
                        st.warning("⚠️ 默认管理员账户不可删除")
                else:
                    st.error("❌ 未找到该用户")
        else:
            st.info("📦 暂无用户")

# 权限不足的页面提示
else:
    if selected_page == "submit" and not check_permission(user_role, 'create_bug'):
        st.error("❌ 您没有提交BUG的权限")
    elif selected_page == "developers" and not check_permission(user_role, 'manage_developers'):
        st.error("❌ 您没有管理研发人员的权限")
    elif selected_page == "users" and user_role != 'admin':
        st.error("❌ 只有管理员才能管理用户")
    else:
        st.info("ℹ️ 请选择一个功能页面")