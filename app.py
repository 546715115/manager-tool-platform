"""
Manager Tool - Flask Application
Tool management hub for starting, stopping, and monitoring development tools.
"""

from flask import Flask, jsonify, render_template, request
from models import init_db, get_all_tools, get_tool, create_tool, update_tool, delete_tool, update_tool_status
from process_manager import start_tool as pm_start, stop_tool as pm_stop, is_process_running, get_process_by_port
from port_scanner import is_port_available, find_available_port

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['DATABASE'] = 'tools.db'


# ==================== Tool Management APIs ====================

@app.route('/api/tools', methods=['GET'])
def api_get_tools():
    """Get all tools"""
    tools = get_all_tools()
    return jsonify({"success": True, "data": tools})


@app.route('/api/tools/<int:tool_id>', methods=['GET'])
def api_get_tool(tool_id):
    """Get a single tool by ID"""
    tool = get_tool(tool_id)
    if tool is None:
        return jsonify({"success": False, "error": "Tool not found"})
    return jsonify({"success": True, "data": tool})


@app.route('/api/tools', methods=['POST'])
def api_create_tool():
    """Create a new tool"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"})
    # name, cmd, port required
    if not all(k in data for k in ('name', 'cmd', 'port')):
        return jsonify({"success": False, "error": "name, cmd, port are required"})
    try:
        tool_id = create_tool(
            name=data['name'],
            cmd=data['cmd'],
            port=data['port'],
            url=data.get('url', '')
        )
        return jsonify({"success": True, "data": {"id": tool_id}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/tools/<int:tool_id>', methods=['PUT'])
def api_update_tool(tool_id):
    """Update an existing tool"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"})
    try:
        success = update_tool(tool_id, **data)
        if not success:
            return jsonify({"success": False, "error": "Tool not found or no changes made"})
        return jsonify({"success": True, "data": {"id": tool_id}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/tools/<int:tool_id>', methods=['DELETE'])
def api_delete_tool(tool_id):
    """Delete a tool"""
    try:
        success = delete_tool(tool_id)
        if not success:
            return jsonify({"success": False, "error": "Tool not found"})
        return jsonify({"success": True, "data": {"id": tool_id}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/tools/<int:tool_id>/start', methods=['POST'])
def api_start_tool(tool_id):
    """Start a tool"""
    tool = get_tool(tool_id)
    if not tool:
        return jsonify({"success": False, "error": "Tool not found"})

    if tool['pid'] and is_process_running(tool['pid']):
        return jsonify({"success": False, "error": "Tool already running"})

    success, actual_port, pid, error = pm_start(tool['cmd'], tool['port'])
    if success:
        update_tool_status(tool_id, 'running', pid, actual_port)
        return jsonify({"success": True, "data": {"port": actual_port, "pid": pid}})
    else:
        return jsonify({"success": False, "error": error})


@app.route('/api/tools/<int:tool_id>/stop', methods=['POST'])
def api_stop_tool(tool_id):
    """Stop a tool"""
    tool = get_tool(tool_id)
    if not tool:
        return jsonify({"success": False, "error": "Tool not found"})

    # 即使没有PID，也尝试通过端口停止
    if not tool['pid'] and not tool['port']:
        return jsonify({"success": False, "error": "Tool not running (no PID and no port)"})

    # 通过端口检查进程是否还在运行
    real_pid = get_process_by_port(tool['port']) if tool['port'] else None
    if not real_pid and tool['pid'] and not is_process_running(tool['pid']):
        # 进程已不存在，更新数据库状态
        update_tool_status(tool_id, 'stopped', None)
        return jsonify({"success": True, "data": {"id": tool_id}})

    success = pm_stop(tool['pid'], tool['port'])
    if success:
        update_tool_status(tool_id, 'stopped', None)
        return jsonify({"success": True, "data": {"id": tool_id}})
    else:
        return jsonify({"success": False, "error": "Failed to stop process"})


@app.route('/api/tools/<int:tool_id>/status', methods=['GET'])
def api_get_tool_status(tool_id):
    """Get running status of a tool"""
    tool = get_tool(tool_id)
    if not tool:
        return jsonify({"success": False, "error": "Tool not found"})

    # 检查进程是否仍在运行
    running = tool['pid'] and is_process_running(tool['pid'])

    if running:
        return jsonify({"success": True, "data": {"status": "running", "pid": tool['pid'], "port": tool['port']}})
    else:
        # 进程已停止，同步数据库状态
        if tool['status'] != 'stopped':
            update_tool_status(tool_id, 'stopped', None)
        return jsonify({"success": True, "data": {"status": "stopped", "pid": None, "port": tool['port']}})


# ==================== Port Management APIs ====================

@app.route('/api/ports/check/<int:port>', methods=['GET'])
def api_check_port(port):
    """Check if a port is available"""
    available = is_port_available(port)
    return jsonify({"available": available})


@app.route('/api/ports/find-available/<int:base_port>', methods=['GET'])
def api_find_available_port(base_port):
    """Find an available port starting from base_port"""
    port = find_available_port(base_port)
    return jsonify({"port": port})


# ==================== Frontend Route ====================

@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html')


# ==================== App Entry Point ====================

if __name__ == '__main__':
    init_db()  # Ensure database tables exist
    app.run(debug=False, port=5000)