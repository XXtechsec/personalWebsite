from base import app
from flask import render_template, flash, redirect, request, url_for, session, send_from_directory
from models import blogPost, db
from datetime import datetime
from config import *
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import os, json, boto3

password_hash = generate_password_hash(Config.PASSWORD)

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

### Logic for Info Pages:

# home
@app.route('/')
@app.route('/index')
def index():
    return render_template('InfoPages/index.html')


# about
@app.route('/about')
def about():
    return render_template('InfoPages/about.html')


# Contact page
@app.route('/contact')
def contact():
    return render_template('InfoPages/contact.html')


###Logic for Blog:

# show post
@app.route('/post/<int:post_id>')
def post(post_id):
    post = blogPost.query.filter_by(id=post_id).first()

    return render_template('BlogPages/post.html', post=post)


# blogSelect
@app.route('/blog')
def blog():
    posts = blogPost.query.order_by(blogPost.date_posted.desc()).all()
    return render_template('BlogPages/blogSelect.html', posts=posts)


###Logic for making and managing Blog:

##Modifying

# Select To Modify
@app.route('/modify/<int:post_id>')
def modify(post_id):
    post = blogPost.query.filter_by(id=post_id).one()
    return render_template('BlogAdminPages/postMaker.html', post=post, modify=True)


# Actually Modify
@app.route('/modifypost/<int:post_id>', methods=['POST'])
def modifypost(post_id):
    password = request.form['password']
    post = blogPost.query.filter_by(id=post_id).one()
    post.title = request.form['title']
    post.subtitle = request.form['subtitle']
    post.author = request.form['author']
    post.content = request.form['content']
    if check_password_hash(password_hash, password):
        db.session.commit()

        flash('Modified Correctly', category="success")
        return redirect(url_for('post', post_id=post_id))
    else:
        flash('wrong password', category="danger")
        return render_template('BlogAdminPages/postMaker.html', post=post, modify=True)


##Add Posts

# Enter to add Post
@app.route('/add')
def add():
    return render_template('BlogAdminPages/postMaker.html', post=blogPost(title='', subtitle='', author='', content=''),
                           modify=False)


# Actually make Post
@app.route('/addpost', methods=['POST'])
def addpost():
    password = request.form['password']
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    content = request.form['content']
    post = blogPost(title=title, subtitle=subtitle, author=author, content=content, date_posted=datetime.now())
    if check_password_hash(password_hash, password):

        db.session.add(post)
        db.session.commit()

        flash('Blog Post Created', category="success")
        return redirect(url_for('post', post_id=post.id))
    else:
        flash('wrong password', category="danger")
        return render_template('BlogAdminPages/postMaker.html', post=post, modify=False)


##Delete from Blog

# Choose to Delete
@app.route('/delete/<int:post_id>')
def delete(post_id):
    post = blogPost.query.filter_by(id=post_id).one()
    return render_template('BlogAdminPages/delete.html', post=post)


# Confirm with Password
@app.route('/deletepost/<int:post_id>', methods=['POST'])
def deletepost(post_id):
    password = request.form['password']
    post = blogPost.query.filter_by(id=post_id).one()
    if check_password_hash(password_hash, password):

        db.session.delete(post)
        db.session.commit()
        flash('Successfully Deleted Off the Face of This Earth', category="success")
        return redirect(url_for('blog'))
    else:
        flash('wrong password', category="danger")
        return render_template('BlogAdminPages/delete.html', post=post)


### File Managing Logic

# Define valid files
def allowed_image(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False




# Retrieve from uploads, very useful
@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config["IMAGE_UPLOADS"], filename)




@app.route('/mail/')
def mail():
    mail = Mail(app)
    msg = Message('Twilio SendGrid Test Email', sender="tony.lazar.mi@gmail.com",
                  recipients=['tony.lazar.mi@gmail.com'])
    msg.body = 'This is a test email!'
    msg.html = '<p>This is a test email!</p>'
    mail.send(msg)
    return "email sent"



###s3 stuff

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
@app.route('/files/')
def sign_s3():
    s3_resources = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    bucket = s3_resources.Bucket(AWS_STORAGE_BUCKET_NAME)
    summaries = bucket.objects.all()

    return render_template('BlogAdminPages/files.html', my_bucket=bucket, files=summaries)

# choose to upload
@app.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":

        if request.files:

            image = request.files["image"]

            if image.filename == "":
                flash('No Filename', category="danger")
                return render_template('webLogicPages/userInfo.html')

            if allowed_image(image.filename):
                s3_resources = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                bucket = s3_resources.Bucket(AWS_STORAGE_BUCKET_NAME)

                bucket.Object(image.filename).put(Body=image)
                flash('object uploaded', category="success")
                return render_template('webLogicPages/userInfo.html')

            else:
                flash('File Extension Not Allowed', category="danger")
                return render_template('webLogicPages/userInfo.html')

    flash('You messed up bad', category="danger")
    return redirect(url_for('index'))
