from flask import render_template, url_for, flash, redirect, request, abort, current_app
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, ProductForm, FeedbackForm, UpdateFarmerProfileForm, UpdateVendorProfileForm
from app.models import User, Product, Feedback, Farmer, Order
from app.utils import hash_password, verify_password, save_image, generate_order_id, is_farmer, is_vendor
import logging

# Create a Blueprint
from flask import Blueprint

bp = Blueprint('main', __name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Home route
@bp.route('/')
@bp.route('/home')
def home():
    logger.info('Home page accessed')
    return render_template('home.html')
@bp.route('/farmer/add_product', methods=['GET', 'POST'])
@login_required
def farmer_add_product():
    form = ProductForm()
    
    if form.validate_on_submit():
        try:
            # Create a new product instance
            product = Product(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                quantity_available=form.quantity.data,
                farmer_id=current_user.id  # Assuming there's a foreign key to link to the farmer
            )
            # Add the product to the database
            db.session.add(product)
            db.session.commit()
            logger.info(f'New product added by {current_user.username}: {form.name.data}')
            flash('Product added successfully!', 'success')
            return redirect(url_for('main.farmer_dashboard'))  # Redirect to the farmer dashboard
        except Exception as e:
            logger.error(f"Error adding product: {e}")
            flash('An error occurred while adding the product. Please try again.', 'danger')
    
    logger.info('Farmer add product form accessed')
    return render_template('farmer_add_product.html', title='Add Product', form=form)

@bp.route('/farmer/orders', methods=['GET'])
@login_required
def farmer_orders():
    try:
        # Fetch all products for the current farmer
        farmer_products = Product.query.filter_by(farmer_id=current_user.id).all()

        # If no products exist, show a message and redirect
        if not farmer_products:
            flash('You do not have any products listed.', 'info')
            return redirect(url_for('farmer.dashboard'))
        
        # Get the IDs of all the farmer's products
        product_ids = [product.id for product in farmer_products]

        # Fetch all orders that involve any of the farmer's products
        orders = Order.query.filter(Order.product_id.in_(product_ids)).all()

        # Log that the farmer accessed their orders
        logger.info(f'Farmer {current_user.username} accessed their orders.')
        
        # Render the farmer orders page
        return render_template('farmer_orders.html', title='Farmer Orders', orders=orders)
    
    except Exception as e:
        logger.error(f"Error retrieving farmer orders: {e}")
        flash('An error occurred while retrieving your orders. Please try again.', 'danger')
        return redirect(url_for('farmer.dashboard'))
@bp.route('/farmer/product/<int:product_id>', methods=['GET'])
@login_required
def view_product(product_id):
    try:
        # Fetch the product by its ID
        product = Product.query.get(product_id)
        
        # Ensure that the current user is the owner of the product
        if product is None or product.farmer_id != current_user.id:
            logger.warning(f"Unauthorized access attempt by user {current_user.username} to view product {product_id}")
            flash('You do not have permission to view this product.', 'danger')
            return redirect(url_for('farmer.dashboard'))
        
        # Log successful access to the product details
        logger.info(f'Farmer {current_user.username} viewed product {product.name} (ID: {product.id})')
        
        # Render the product detail page
        return render_template('view_product.html', title='View Product', product=product)
    
    except Exception as e:
        logger.error(f"Error viewing product: {e}")
        flash('An error occurred while trying to view the product.', 'danger')
        return redirect(url_for('farmer.dashboard'))
# Product list route
@bp.route('/products')
def product_list():
    try:
        products = Product.query.all()  # Adjust your query based on your database model
        logger.info(f'Fetched {len(products)} products')
        return render_template('product_list.html', products=products)
    except Exception as e:
        logger.error(f"Error fetching product list: {e}")
        flash('An error occurred while fetching products. Please try again.', 'danger')
        return redirect(url_for('main.home'))

# User registration route
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        logger.info(f'Authenticated user {current_user.username} attempted to register again')
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Hash the password before saving
            hashed_pw = hash_password(form.password.data)
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_pw,
                role='farmer',  # Assuming role is 'farmer'; adjust as necessary
                county=form.county.data,          # New county field
                sub_county=form.sub_county.data,  # New sub-county field
                town=form.town.data                # New town field
            )
            db.session.add(user)
            db.session.commit()  # Commit to get the user ID for the farmer profile

            # Create the corresponding Farmer profile
            farmer_profile = Farmer(
                user_id=user.id,
                farm_name=form.farm_name.data,  # Ensure this field is in the RegistrationForm
                location=form.location.data       # Ensure this field is in the RegistrationForm
            )
            db.session.add(farmer_profile)
            db.session.commit()  # Commit to save the Farmer profile

            logger.info(f'New user registered: {form.username.data}')
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            flash('An error occurred while creating your account. Please try again.', 'danger')
    
    logger.info('User registration form accessed')
    return render_template('register.html', title='Register', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logger.info(f'User {current_user.username} attempted to log in again')
        return redirect(url_for('main.home'))  # Redirect to home if already logged in

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and verify_password(user.password, form.password.data):
                login_user(user)
                logger.info(f'User logged in: {user.username} with role: {user.role}')
                flash('You have been logged in!', 'success')

                # Redirect based on user role
                if user.role == 'vendor':
                    logger.info(f'Redirecting vendor {user.username} to the vendor dashboard')
                    return redirect(url_for('main.vendor_dashboard'))  # Adjust this as needed
                elif user.role == 'farmer':
                    logger.info(f'Redirecting farmer {user.username} to the farmer dashboard')
                    return redirect(url_for('main.farmer_dashboard'))  # Adjust this as needed

                logger.warning(f'User {user.username} has an unrecognized role: {user.role}. Redirecting to home.')
                return redirect(url_for('main.home'))  # Fallback for unknown roles
            else:
                logger.warning(f'Failed login attempt for email: {form.email.data}')
                flash('Login failed. Check email and password.', 'danger')
        except Exception as e:
            logger.error(f"Error during login: {e}")
            flash('An error occurred during login. Please try again.', 'danger')
    else:
        logger.warning(f'Login form validation failed: {form.errors}')  # Log validation errors

    logger.info('User login form accessed')
    return render_template('login.html', title='Login', form=form)
# Farmer dashboard route
@bp.route('/farmer/dashboard')
@login_required
def farmer_dashboard():
    try:
        # Retrieve the farmer profile
        farmer = Farmer.query.filter_by(user_id=current_user.id).first()
        if farmer is None:
            logger.error(f'No farmer profile found for user {current_user.username}.')
            flash('No farmer profile found. Please complete your registration.', 'warning')
            return redirect(url_for('main.home'))
        
        # Retrieve products associated with the farmer
        products = Product.query.filter_by(farmer_id=farmer.id).all()

        logger.info(f'Farmer dashboard accessed for user {current_user.username}.')
        return render_template('farmer_dashboard.html', products=products)
    except Exception as e:
        logger.error(f"Error accessing farmer dashboard: {e}")
        flash('An error occurred while accessing the dashboard. Please try again.', 'danger')
        return redirect(url_for('main.home'))




# User logout route
@bp.route('/logout')
@login_required
def logout():
    logger.info(f'User {current_user.username} logged out')
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('main.home'))

# Add a product (Farmer only)
@bp.route('/product/new', methods=['GET', 'POST'])
@login_required
def new_product():
    if not is_farmer(current_user):
        logger.warning(f'Unauthorized access attempt by user {current_user.username} to add a product')
        abort(403)
    
    form = ProductForm()
    if form.validate_on_submit():
        try:
            product = Product(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                quantity_available=form.quantity_available.data,
                farmer=current_user
            )
            db.session.add(product)
            db.session.commit()
            logger.info(f'New product added: {form.name.data} by {current_user.username}')
            flash('Your product has been added!', 'success')
            return redirect(url_for('main.product_list'))
        except Exception as e:
            logger.error(f"Error adding new product: {e}")
            flash('An error occurred while adding your product. Please try again.', 'danger')
    
    logger.info('New product form accessed')
    return render_template('create_product.html', title='New Product', form=form)

# View a single product
@bp.route('/product/<int:product_id>')
def product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        logger.info(f'Product details accessed for product ID: {product_id}')
        return render_template('product_detail.html', product=product)
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        flash('An error occurred while fetching the product. Please try again.', 'danger')
        return redirect(url_for('main.product_list'))

# Update farmer profile route
@bp.route('/farmer/profile', methods=['GET', 'POST'])
@login_required
def update_farmer_profile():
    if not is_farmer(current_user):
        logger.warning(f'Unauthorized access attempt by user {current_user.username} to update farmer profile')
        abort(403)
    
    form = UpdateFarmerProfileForm()
    if form.validate_on_submit():
        try:
            current_user.farm_name = form.farm_name.data
            current_user.location = form.location.data
            db.session.commit()
            logger.info(f'Farmer profile updated for user: {current_user.username}')
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('main.update_farmer_profile'))
        except Exception as e:
            logger.error(f"Error updating farmer profile: {e}")
            flash('An error occurred while updating your profile. Please try again.', 'danger')
    
    elif request.method == 'GET':
        form.farm_name.data = current_user.farm_name
        form.location.data = current_user.location
    
    logger.info('Farmer profile update form accessed')
    return render_template('update_farmer_profile.html', title='Update Farmer Profile', form=form)

# Update vendor profile route
@bp.route('/vendor/profile', methods=['GET', 'POST'])
@login_required
def update_vendor_profile():
    if not is_vendor(current_user):
        logger.warning(f'Unauthorized access attempt by user {current_user.username} to update vendor profile')
        abort(403)
    
    form = UpdateVendorProfileForm()
    if form.validate_on_submit():
        try:
            current_user.full_name = form.full_name.data
            current_user.shipping_address = form.shipping_address.data
            db.session.commit()
            logger.info(f'Vendor profile updated for user: {current_user.username}')
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('main.update_vendor_profile'))
        except Exception as e:
            logger.error(f"Error updating vendor profile: {e}")
            flash('An error occurred while updating your profile. Please try again.', 'danger')
    
    elif request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.shipping_address.data = current_user.shipping_address
    
    logger.info('Vendor profile update form accessed')
    return render_template('update_vendor_profile.html', title='Update Vendor Profile', form=form)

# Feedback route (Vendors provide feedback on farmers)
@bp.route('/product/<int:product_id>/feedback', methods=['GET', 'POST'])
@login_required
def feedback(product_id):
    product = Product.query.get_or_404(product_id)
    if not is_vendor(current_user):
        logger.warning(f'Unauthorized access attempt by user {current_user.username} to provide feedback')
        abort(403)
    
    form = FeedbackForm()
    if form.validate_on_submit():
        try:
            feedback = Feedback(
                rating=form.rating.data,
                comment=form.comment.data,
                vendor=current_user,
                farmer_id=product.farmer.id,  # Assuming feedback is linked to the farmer
                product=product
            )
            db.session.add(feedback)
            db.session.commit()
            logger.info(f'Feedback submitted for product {product_id} by vendor {current_user.username}')
            flash('Your feedback has been submitted!', 'success')
            return redirect(url_for('main.product', product_id=product.id))
        except Exception as e:
            logger.error(f"Error submitting feedback for product {product_id}: {e}")
            flash('An error occurred while submitting your feedback. Please try again.', 'danger')
    
    logger.info('Feedback form accessed for product ID: {product_id}')
    return render_template('feedback.html', title='Provide Feedback', form=form, product=product)

# Order product route (Vendor places order)
@bp.route('/product/<int:product_id>/order', methods=['POST'])
@login_required
def order_product(product_id):
    product = Product.query.get_or_404(product_id)
    if not is_vendor(current_user):
        logger.warning(f'Unauthorized access attempt by user {current_user.username} to order a product')
        abort(403)
    
    try:
        # Generate a unique order ID and handle order logic here
        order_id = generate_order_id()
        # Implement order model and logic to save the order to the database here
        logger.info(f'Order placed for product ID: {product_id} by vendor {current_user.username}, Order ID: {order_id}')
        flash(f'Order {order_id} has been placed!', 'success')
        return redirect(url_for('main.product', product_id=product.id))
    except Exception as e:
        logger.error(f"Error placing order for product {product_id}: {e}")
        flash('An error occurred while placing your order. Please try again.', 'danger')

# Farmer's list of products
@bp.route('/my-products')
@login_required
def my_products():
    if not is_farmer(current_user):
        logger.warning(f'Unauthorized access attempt by user {current_user.username} to view their products')
        abort(403)
    
    try:
        products = Product.query.filter_by(farmer_id=current_user.id).all()
        logger.info(f'Fetched {len(products)} products for farmer {current_user.username}')
        return render_template('my_products.html', products=products)
    except Exception as e:
        logger.error(f"Error fetching farmer's products: {e}")
        flash('An error occurred while fetching your products. Please try again.', 'danger')
        return redirect(url_for('main.home'))

# View cart route
@bp.route('/cart')
@login_required
def cart():
    cart_items = []  # Fetch cart items from session or database
    total = sum(item.product.price * item.quantity for item in cart_items)
    logger.info(f'Cart accessed for user {current_user.username}, total: {total}')
    return render_template('cart.html', cart_items=cart_items, total=total)

# Checkout route
@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        address = request.form['address']
        payment_method = request.form['payment_method']
        # Implement order processing logic here
        logger.info(f'Checkout completed for user {current_user.username}')
        flash('Your order has been placed!', 'success')
        return redirect(url_for('main.home'))
    
    logger.info('Checkout form accessed')
    return render_template('checkout.html', title='Checkout')

# Profile route
@bp.route('/profile')
@login_required
def profile():
    logger.info(f'Profile accessed for user {current_user.username}')
    return render_template('profile.html', title='Your Profile', user=current_user)
