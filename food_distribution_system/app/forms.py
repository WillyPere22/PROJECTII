from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from app.models import User

# Sample data for counties, sub-counties, and towns/wards (replace with your data source)
counties = [
    ('nairobi', 'Nairobi'),
    ('kiambu', 'Kiambu'),
    ('machakos', 'Machakos'),
]

# User registration form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('farmer', 'Farmer'), ('vendor', 'Vendor')], validators=[DataRequired()])
    
    county = SelectField('County', choices=[(county[0], county[1]) for county in counties], validators=[DataRequired()])
    
    # Changed from SelectField to StringField for manual input
    sub_county = StringField('Sub-County', validators=[DataRequired(), Length(min=1)])
    town = StringField('Town/Ward', validators=[DataRequired(), Length(min=1)])

    # Added fields for farmer-specific information
    farm_name = StringField('Farm Name', validators=[DataRequired(), Length(min=1, max=100)])  # New field for farm name
    location = StringField('Farm Location', validators=[DataRequired(), Length(min=1, max=100)])  # New field for location

    submit = SubmitField('Sign Up')

    # Custom validator to check if the username is already taken
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose another.')

    # Custom validator to check if the email is already registered
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different email.')
# User login form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Product creation form for farmers
class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Product Description', validators=[DataRequired(), Length(min=10)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    quantity_available = IntegerField('Quantity Available', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Product')

# Feedback form for vendors to submit feedback for farmers
class FeedbackForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comment', validators=[Length(max=200)])
    submit = SubmitField('Submit Feedback')

# Update farmer profile form
class UpdateFarmerProfileForm(FlaskForm):
    farm_name = StringField('Farm Name', validators=[DataRequired(), Length(min=2, max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Update Profile')

# Update vendor profile form
class UpdateVendorProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    shipping_address = TextAreaField('Shipping Address', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Update Profile')
