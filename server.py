import os
import argparse
import shutil
import datetime
import re
import zipfile
import io
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, abort, flash, jsonify, Response, send_file, session
import logging

# --- 配置 ---
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)
# 使用一个固定的、更安全的密钥，或者保持 os.urandom(24)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.permanent_session_lifetime = datetime.timedelta(days=7)  # session 有效期

SHARED_DIRECTORY = ""
PASSWORD = None # 全局变量，用于存储密码

# --- 辅助函数 (无变动) ---
def secure_filename_custom(filename):
    allowed_chars = re.compile(r'[^a-zA-Z0-9\u4e00-\u9fa5_.\- ]')
    cleaned_filename = allowed_chars.sub('', filename).strip(' .')
    if not cleaned_filename:
        cleaned_filename = "unnamed_file_" + str(int(datetime.datetime.now().timestamp()))
    return cleaned_filename

def get_safe_path(path_str):
    base_path = os.path.abspath(SHARED_DIRECTORY)
    requested_path = os.path.join(base_path, path_str)
    safe_path = os.path.abspath(requested_path)
    if not safe_path.startswith(base_path):
        abort(404, "Path Traversal Attack Detected!")
    return safe_path

def get_file_info(dir_path, name):
    path = os.path.join(dir_path, name)
    try:
        stat = os.stat(path)
        is_previewable, is_image, is_text = False, False, False
        ext = os.path.splitext(name)[1].lower()
        if ext in ['.txt', '.md', '.log', '.py', '.js', '.css', '.html', '.sh', '.bat', '.json', '.xml']:
            is_previewable, is_text = True, True
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']:
            is_previewable, is_image = True, True
        return {"name": name, "is_dir": os.path.isdir(path), "size": stat.st_size, "modified_dt": stat.st_mtime, "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'), "is_previewable": is_previewable, "is_image": is_image, "is_text": is_text}
    except FileNotFoundError:
        return None

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0: break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

# --- 新增：认证和授权路由 ---
@app.before_request
def require_login():
    # 如果定义了密码，则启用认证
    if PASSWORD:
        allowed_routes = ['login', 'static']
        if request.endpoint not in allowed_routes and 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_password = request.form.get('password')
        if entered_password == PASSWORD:
            session['logged_in'] = True
            session.permanent = True # 使用永久会话
            flash('登录成功！', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('index'))
        else:
            flash('密码错误，请重试。', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('您已成功登出。', 'success')
    return redirect(url_for('login'))

# --- 核心文件操作路由 ---
@app.route('/')
@app.route('/<path:subpath>')
def index(subpath=''):
    sort_by, order = request.args.get('sort_by', 'name'), request.args.get('order', 'asc')
    current_path_str = subpath
    safe_current_path = get_safe_path(current_path_str)
    if not os.path.isdir(safe_current_path): abort(404)
    items = []
    try:
        for name in os.listdir(safe_current_path):
            info = get_file_info(safe_current_path, name)
            if info: 
                info["human_size"] = human_readable_size(info["size"]) if not info['is_dir'] else '-'
                items.append(info)
    except Exception as e: flash(f"读取目录出错: {e}", "danger")
    reverse = (order == 'desc')
    items.sort(key=lambda x: x['name'].lower() if sort_by == 'name' else (x['size'] if sort_by == 'size' else x['modified_dt']), reverse=reverse)
    items.sort(key=lambda x: x['is_dir'], reverse=True)
    breadcrumbs = [{'name': '主目录', 'path': ''}]; path_parts = current_path_str.split('/') if current_path_str else []
    for i, part in enumerate(path_parts):
        if part: breadcrumbs.append({'name': part, 'path': '/'.join(path_parts[:i+1])})
    return render_template('index.html', items=items, current_path=current_path_str, breadcrumbs=breadcrumbs, sort_by=sort_by, order=order)

# --- 新增：全局搜索路由 ---
@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    search_path_str = request.args.get('path', '')
    
    if not query:
        flash('请输入搜索关键词。', 'warning')
        return redirect(url_for('index', subpath=search_path_str))

    search_root_path = get_safe_path(search_path_str)
    results = []
    
    for root, dirs, files in os.walk(search_root_path):
        # 搜索子文件夹
        for name in dirs:
            if query.lower() in name.lower():
                full_path = os.path.join(root, name)
                relative_path = os.path.relpath(full_path, SHARED_DIRECTORY)
                results.append({
                    'name': name,
                    'path': relative_path.replace('\\', '/'),
                    'is_dir': True,
                    'parent': os.path.relpath(root, SHARED_DIRECTORY).replace('\\', '/') if root != search_root_path else '当前目录'
                })
        # 搜索文件
        for name in files:
            if query.lower() in name.lower():
                full_path = os.path.join(root, name)
                relative_path = os.path.relpath(full_path, SHARED_DIRECTORY)
                info = get_file_info(root, name)
                if info:
                    info['path'] = relative_path.replace('\\', '/')
                    info['parent'] = os.path.relpath(root, SHARED_DIRECTORY).replace('\\', '/') if root != search_root_path else '当前目录'
                    results.append(info)

    return render_template('search_results.html', query=query, results=results, current_path=search_path_str)

# --- 其他路由（基本无变动） ---
@app.route('/view/<path:filepath>')
def view_file(filepath):
    safe_path = get_safe_path(filepath)
    if not os.path.isfile(safe_path): abort(404)
    return send_from_directory(os.path.dirname(safe_path), os.path.basename(safe_path))

@app.route('/get_text_content/<path:filepath>')
def get_text_content(filepath):
    safe_path = get_safe_path(filepath)
    if not os.path.isfile(safe_path): abort(404)
    try:
        for encoding in ['utf-8', 'gbk', 'gb2312']:
            try:
                with open(safe_path, 'r', encoding=encoding) as f: content = f.read()
                return Response(content, mimetype='text/plain')
            except UnicodeDecodeError: continue
        return Response("无法解码文件内容，可能是不支持的文本编码。", status=400, mimetype='text/plain')
    except Exception as e: return Response(f"读取文件出错: {e}", status=500, mimetype='text/plain')

@app.route('/zip_download', methods=['POST'])
def zip_download():
    items_to_zip = request.form.getlist('selected_items'); current_path = request.form.get('current_path', '')
    if not items_to_zip: flash('未选择任何文件或文件夹。', 'warning'); return redirect(url_for('index', subpath=current_path))
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for item_path in items_to_zip:
            safe_path = get_safe_path(item_path)
            if os.path.isfile(safe_path): zf.write(safe_path, os.path.basename(item_path))
            elif os.path.isdir(safe_path):
                for root, _, files in os.walk(safe_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        archive_path = os.path.relpath(file_path, get_safe_path(current_path)); zf.write(file_path, archive_path)
    memory_file.seek(0); zip_name = f"archive_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
    return send_file(memory_file, download_name=zip_name, as_attachment=True, mimetype='application/zip')

@app.route('/delete_multiple', methods=['POST'])
def delete_multiple():
    items_to_delete, current_path = request.form.getlist('selected_items'), request.form.get('current_path', '')
    deleted_count, error_count = 0, 0
    for item_path in items_to_delete:
        safe_path = get_safe_path(item_path)
        try: (os.remove if os.path.isfile(safe_path) else shutil.rmtree)(safe_path); deleted_count += 1
        except Exception: error_count += 1
    if deleted_count > 0: flash(f'成功删除 {deleted_count} 个项目。', 'success')
    if error_count > 0: flash(f'有 {error_count} 个项目删除失败。', 'danger')
    return redirect(url_for('index', subpath=current_path))

@app.route('/upload',methods=['POST'])
def upload():subpath=request.args.get('path','');target_dir=get_safe_path(subpath);os.makedirs(target_dir,exist_ok=True);f=request.files.get('file');filename=secure_filename_custom(f.filename);f.save(os.path.join(target_dir,filename));return jsonify({'status':'success','filename':filename}),200
@app.route('/download/<path:filepath>')
def download(filepath):return send_from_directory(os.path.dirname(get_safe_path(filepath)),os.path.basename(get_safe_path(filepath)),as_attachment=True)
@app.route('/create_folder',methods=['POST'])
def create_folder():current_path,folder_name=request.form.get('path',''),request.form.get('folder_name');os.makedirs(os.path.join(get_safe_path(current_path),secure_filename_custom(folder_name)));flash('文件夹创建成功','success');return redirect(url_for('index',subpath=current_path))
@app.route('/delete',methods=['POST'])
def delete():item_path_str=request.form.get('path');safe_path=get_safe_path(item_path_str);parent_dir=os.path.dirname(item_path_str);(os.remove if os.path.isfile(safe_path)else shutil.rmtree)(safe_path);flash('项目已删除','success');return redirect(url_for('index',subpath=parent_dir))
@app.route('/rename',methods=['POST'])
def rename():current_path,old,new=request.form.get('path',''),request.form.get('old_name'),request.form.get('new_name');os.rename(get_safe_path(old),get_safe_path(os.path.join(os.path.dirname(old),new)));flash('重命名成功','success');return redirect(url_for('index',subpath=current_path))

# --- 主程序入口 ---
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="一个功能强大的中文文件服务器。");
    parser.add_argument('directory', help='要分享的根目录');
    parser.add_argument('-p', '--port', type=int, help='服务运行的端口');
    parser.add_argument('--password', type=str, help='为服务器设置访问密码（可选）');
    parser.add_argument('--host', type=str, default='0.0.0.0', help='绑定的主机地址');
    args = parser.parse_args();
    
    SHARED_DIRECTORY=os.path.abspath(args.directory);
    if args.password:
        PASSWORD = args.password
    
    if not os.path.isdir(SHARED_DIRECTORY): print(f"错误: 目录 '{args.directory}' 不存在。"); exit(1)
    
    print("="*60 + f"\n🚀 中文文件服务器已启动！\n" + f"📂 分享目录: {SHARED_DIRECTORY}\n" +
          f"🌐 本机访问: http://127.0.0.1:{args.port}\n" + f"📡 局域网访问: http://<你的IP地址>:{args.port}\n" +
          ("🔐 密码保护: 已启用\n" if PASSWORD else "🔓 密码保护: 未启用\n") +
          "🔴 按 CTRL+C 停止服务。\n" + "="*60)
    app.run(host=args.host, port=args.port, debug=False)
