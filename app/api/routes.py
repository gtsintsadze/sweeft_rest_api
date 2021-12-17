from app import app, db, auth
from flask import request, jsonify, g
from app.models import Urls
import time
from datetime import date
from app.models import Users, Roles


@app.before_first_request
def create_tables():
    default_role = Roles(label='default')
    admin_role = Roles(label='admin')

    db.create_all()

    db.session.add(default_role)
    db.session.add(admin_role)

    db.session.commit()


@auth.verify_password
def verify_password(username_or_token, password):
    user = Users.verify_auth_token(username_or_token)

    if not user:
        user = Users.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False

    g.user = user
    return True


@app.route('/api/v1/links/premium/create', methods=['POST'])
@auth.login_required
def create_short_premium_link():
    username = g.user.username
    user = Users.query.filter_by(username=username).first_or_404()

    if user.is_subscribed():
        t = time.localtime()
        add_time = time.strftime("%H:%M:%S", t)
        add_date = date.today().strftime("%d/%m/%Y")

        url_received = request.form.get('target_url', None)
        shortcode = request.form.get('shortcode', None)

        if url_received is None or shortcode is None:
            return jsonify({'message': 'target url and shortcode are required'})

        url_received = 'https://' + url_received if not url_received.startswith('https://') else url_received
        shortcode_exists = Urls.query.filter_by(short=shortcode).first()

        if shortcode_exists:
            return jsonify({'message': 'shortocde already exists', 'url': shortcode_exists.shortened_url})

        new_url = Urls(long=url_received,
                       short=shortcode,
                       add_time=add_time,
                       add_date=add_date)

        db.session.add(new_url)
        db.session.commit()

        return jsonify({'message': 'short url created', 'url': new_url.shortened_url}), 201

    return jsonify({'message': 'user is not subscribed'})


@app.route('/api/v1/links/create', methods=['POST'])
def create_short_link():
    t = time.localtime()
    url_received = request.form.get('target_url', None)
    add_time = time.strftime("%H:%M:%S", t)
    add_date = date.today().strftime("%d/%m/%Y")

    if url_received is not None:
        url_received = 'https://' + url_received if not url_received.startswith('https://') else url_received

        short_url = Urls.shorten_url()
        new_url = Urls(long=url_received,
                       short=short_url,
                       add_time=add_time,
                       add_date=add_date)

        db.session.add(new_url)
        db.session.commit()

        return jsonify({'message': 'shortcode created', 'url': new_url.shortened_url}), 201

    return jsonify({'message': 'target url is required'})


@app.route('/api/v1/links/get', methods=['GET'])
def get_all_links():
    urls = [{"short": i.shortened_url, "long": i.long} for i in Urls.query.all()]

    return jsonify(urls)


@app.route('/api/v1/links/get/<int:url_id>', methods=['POST'])
def get_link_by_id(url_id):
    url_obj = Urls.query.filter_by(url_id=url_id).first_or_404()

    return jsonify({'result': url_obj.shortened_url})


@app.route('/api/v1/links/get/<string:short_url>', methods=['GET'])
def get_link_by_short_url(short_url):
    url_obj = Urls.query.filter_by(short=short_url).first_or_404()

    return jsonify({'result': url_obj.shortened_url})


@app.route('/api/v1/token/get')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route("/api/v1/users/create", methods=["POST"])
def create_new_user():
    username = request.form.get("username", None)
    password = request.form.get("password", None)

    if username is None or password is None:
        return jsonify({'message': 'either username or password is missing'})

    if username == "" or password == "":
        return jsonify({'message': 'username and password are required'})

    if Users.query.filter_by(username=username).first() is not None:
        return jsonify('message', 'username is already exists')

    user = Users(username=username)
    user.hash_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "user created", "username": user.username}), 201


@app.route("/api/v1/users/subscribe/premium")
@auth.login_required
def subscribe_to_premium():
    username = g.user.username
    user = Users.query.filter_by(username=username).first()

    if not user.is_subscribed():
        user.subscribe_to_premium()
        return jsonify({'message': f'{username} successfully subscribed to premium membership'})

    return jsonify({'message': f'{username} is already subscribed to premium membership'})
