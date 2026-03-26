from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Gig, Order
from forms import RegistrationForm, LoginForm, GigForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    gigs = Gig.query.filter_by(active=True).order_by(Gig.created_at.desc()).all()
    return render_template('index.html', gigs=gigs)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Регистрация успешна!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.username.data)
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Добро пожаловать, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверные данные', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли', 'info')
    return redirect(url_for('index'))


@app.route('/gig/create', methods=['GET', 'POST'])
@login_required
def create_gig():
    if current_user.role != 'seller':
        flash('Только продавцы могут создавать услуги', 'danger')
        return redirect(url_for('index'))

    form = GigForm()
    if form.validate_on_submit():
        gig = Gig(
            seller_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            basic_price=form.basic_price.data,
            basic_delivery=form.basic_delivery.data,
            basic_features=form.basic_features.data
        )

        db.session.add(gig)
        db.session.commit()

        flash('Услуга создана!', 'success')
        return redirect(url_for('index'))

    return render_template('create_gig.html', form=form)


# ВАЖНО: ПРАВИЛЬНОЕ НАЗВАНИЕ ФУНКЦИИ - gig_detail
@app.route('/gig/<int:gig_id>')
def gig_detail(gig_id):
    gig = Gig.query.get_or_404(gig_id)
    return render_template('gig_detail.html', gig=gig)  # ПРАВИЛЬНОЕ ИМЯ ШАБЛОНА


@app.route('/gig/<int:gig_id>/order', methods=['POST'])
@login_required
def create_order(gig_id):
    gig = Gig.query.get_or_404(gig_id)

    if current_user.id == gig.seller_id:
        flash('Нельзя заказать свою услугу', 'danger')
        return redirect(url_for('gig_detail', gig_id=gig_id))

    order = Order(
        gig_id=gig.id,
        buyer_id=current_user.id,
        seller_id=gig.seller_id,
        price=gig.basic_price,
        status='completed'
    )

    db.session.add(order)
    db.session.commit()

    seller = User.query.get(gig.seller_id)
    seller.completed_orders += 1
    db.session.commit()

    flash('Заказ создан!', 'success')
    return redirect(url_for('my_orders'))


@app.route('/orders')
@login_required
def my_orders():
    orders = Order.query.filter(
        (Order.buyer_id == current_user.id) | (Order.seller_id == current_user.id)
    ).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)


@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', profile_user=user)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Создаем тестовые данные
        if not User.query.filter_by(username='seller').first():
            seller = User(username='seller', email='seller@test.com', role='seller', bio='Дизайнер')
            seller.set_password('123')
            db.session.add(seller)

        if not User.query.filter_by(username='buyer').first():
            buyer = User(username='buyer', email='buyer@test.com', role='buyer', bio='Покупатель')
            buyer.set_password('123')
            db.session.add(buyer)
            db.session.commit()

        seller = User.query.filter_by(username='seller').first()
        if seller and Gig.query.count() == 0:
            gig = Gig(
                seller_id=seller.id,
                title='Создание логотипа',
                description='Создам уникальный логотип для вашего бизнеса',
                basic_price=50,
                basic_delivery=3,
                basic_features='Дизайн логотипа, 3 варианта, 2 правки'
            )
            db.session.add(gig)
            db.session.commit()

        print('=' * 50)
        print('✅ Сервер запущен!')
        print('📝 Тестовые данные:')
        print('   Продавец: seller / 123')
        print('   Покупатель: buyer / 123')
        print('   Услуга: Создание логотипа')
        print('=' * 50)

    app.run(debug=True)