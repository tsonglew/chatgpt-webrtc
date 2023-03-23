# 生成一个抽奖页面的后端服务，这些功能：
# - 首页，返回 index.html
# - 录入用户的接口 /add_user，用户在页面上填写用户信息，点击提交后，将使用 json 格式把用户的信息提交到这个接口，将用户信息保存到 users_list 列表中。需要录入的信息包括用户的名字和手机号，收到请求后检查手机号是否时中国的，如果不是，返回错误信息，如果是，将用户信息保存到列表中，返回成功的 JSON 信息。
# - 抽奖的接口 /draw_winner，从列表中随机抽取一个用户，返回抽取到的用户的信息。
# - 抽奖页面的路由，兼容包含 .html 后缀和不包含后缀两种请求方式，返回 lottery.html
# - 录入用户信息的路由，兼容包含 .html 后缀和不包含后缀两种请求方式，返回 user_info.html
# - 查询所有已经录入的用户信息的路由，兼容包含 .html 后缀和不包含后缀两种请求方式，返回 show_users.html
# - 开启服务热更新，监听 8888 端口，不限制访问的 ip


from flask import Flask, request, jsonify, render_template
import random

app = Flask(__name__)

users_list = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.json.get('name')
    phone = request.json.get('phone')
    if not phone.startswith('86'):
        return jsonify({'error': 'Invalid phone number'})
    users_list.append({'name': name, 'phone': phone})
    return jsonify({'success': True})

@app.route('/draw_winner')
def draw_winner():
    if not users:
        return jsonify({'error': 'No users found'})
    winner = random.choice(users_list)
    return jsonify(winner)

@app.route('/lottery')
@app.route('/lottery.html')
def lottery():
    return render_template('lottery.html')

@app.route('/user_info')
@app.route('/user_info.html')
def user_info():
    return render_template('user_info.html')

@app.route('/show_users')
@app.route('/show_users.html')
def show_users():
    return render_template('show_users.html', users=users_list)


@app.route('/users')
def users():
    return jsonify(users_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
