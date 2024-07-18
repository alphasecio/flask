import instaloader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from collections import defaultdict
import requests
from io import BytesIO
from PIL import Image
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

def login_and_download(username, password, target_user):
    try:
        L = instaloader.Instaloader()
        L.login(username, password)
        profile = instaloader.Profile.from_username(L.context, target_user)
        posts = profile.get_posts()
        return posts, profile
    except instaloader.exceptions.ConnectionException as e:
        print(f"Connection error: {e}")
    except instaloader.exceptions.BadCredentialsException:
        print("Bad credentials. Please check your username and password.")
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        print("Two-factor authentication is required. Please handle it manually.")
    except instaloader.exceptions.InvalidArgumentException as e:
        print(f"Invalid argument: {e}")
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"Profile {target_user} does not exist.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None, None

def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return BytesIO(response.content)
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

def draw_wrapped_text(c, text, x, y, max_width):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    lines = []
    words = text.split()
    current_line = words[0]
    for word in words[1:]:
        if stringWidth(current_line + ' ' + word, 'Helvetica', 12) < max_width:
            current_line += ' ' + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    for line in lines:
        c.drawString(x, y, line)
        y -= 15  # Move y position for the next line
    return y

def determine_report_type(start_date, end_date):
    if start_date.month == 4 and end_date.month == 6:
        return 'First Quarterly'
    elif start_date.month == 7 and end_date.month == 9:
        return 'Second Quarterly'
    elif start_date.month == 10 and end_date.month == 12:
        return 'Third Quarterly'
    elif start_date.month == 1 and end_date.month == 3:
        return 'Fourth Quarterly'
    elif start_date.month == 4 and end_date.month == 9:
        return 'Half-yearly'
    elif start_date.month == 4 and end_date.month == 3:
        return 'Annual'
    else:
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

def add_page_number(c, page_number):
    c.drawString(500, 20, str(page_number))

def generate_annual_report(posts, profile, pdf_filename, start_date, end_date):
    report_type = determine_report_type(start_date, end_date)
    report = defaultdict(list)
    for post in posts:
        try:
            date = post.date
            if start_date <= date <= end_date:
                caption = post.caption if post.caption else "No Caption"
                if post.is_video:
                    continue
                if post.typename == 'GraphSidecar':
                    image_urls = [node.display_url for node in post.get_sidecar_nodes()]
                    report[date.year].append((date, caption, image_urls))
                else:
                    image_url = post.url
                    report[date.year].append((date, caption, [image_url]))
        except Exception as e:
            print(f"Error processing post: {e}")

    c = canvas.Canvas(pdf_filename, pagesize=letter)
    page_number = 1
    c.drawString(100, 730, f"Account: {profile.username}")
    c.drawString(100, 710, f"Full Name: {profile.full_name}")
    add_page_number(c, page_number)

    y_position = 670
    for year, posts in sorted(report.items()):
        if y_position < 100:
            c.showPage()
            page_number += 1
            add_page_number(c, page_number)
            y_position = 750
        c.drawString(100, y_position, f"{report_type} Report for {year}")
        y_position -= 20
        c.drawString(100, y_position, f"Total Posts: {len(posts)}")
        y_position -= 20

        for date, caption, image_urls in posts:
            try:
                if len(image_urls) == 1:
                    image_url = image_urls[0]
                    image_data = download_image(image_url)
                    if not image_data:
                        continue
                    img = Image.open(image_data)
                    img_width, img_height = 200, 200
                    post_height = img_height + 140
                    if y_position - post_height < 50:
                        c.showPage()
                        page_number += 1
                        add_page_number(c, page_number)
                        y_position = 750
                        c.drawString(100, y_position, f"{report_type} Report for {year}")
                        y_position -= 20
                    c.drawImage(ImageReader(img), 100, y_position - img_height, width=img_width, height=img_height)
                    y_position -= img_height + 20
                    if y_position - 60 < 0:
                        c.showPage()
                        page_number += 1
                        add_page_number(c, page_number)
                        y_position = 750
                    y_position = draw_wrapped_text(c, f"Date: {date}", 100, y_position - 15, 450)
                    y_position = draw_wrapped_text(c, f"{caption}", 100, y_position - 15, 450)  # Display caption directly
                    y_position -= 20  # Add additional space after each post
                else:
                    image_heights = []
                    for i, image_url in enumerate(image_urls):
                        image_data = download_image(image_url)
                        if not image_data:
                            continue
                        img = Image.open(image_data)
                        img_width, img_height = 200, 200
                        image_heights.append(img_height)
                        x_position = 100 + (i % 2) * (img_width + 10)
                        if i % 2 == 0 and i > 0:
                            y_position -= img_height + 20
                        if y_position - img_height < 50:
                            c.showPage()
                            page_number += 1
                            add_page_number(c, page_number)
                            y_position = 750
                            c.drawString(100, y_position, f"{report_type} Report for {year}")
                            y_position -= 20
                        c.drawImage(ImageReader(img), x_position, y_position - img_height, width=img_width, height=img_height)
                    y_position -= max(image_heights) + 20
                    caption_height = (len(caption) // 60 + 1) * 15 + 60  # Roughly estimate height needed for caption
                    if y_position - caption_height < 0:
                        c.showPage()
                        page_number += 1
                        add_page_number(c, page_number)
                        y_position = 750
                        c.drawString(100, y_position, f"{report_type} Report for {year}")
                        y_position -= 20
                    y_position = draw_wrapped_text(c, f"{caption}", 100, y_position - 15, 450)  # Display caption directly
                    y_position -= 20  # Add additional space after each post
            except Exception as e:
                print(f"Error processing image: {e}")
        y_position -= 40
    c.save()
    print(f'PDF report generated: {pdf_filename}')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        target_user = request.form['target_user']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        posts, profile = login_and_download(username, password, target_user)
        if posts and profile:
            pdf_filename = f"{target_user}_annual_report.pdf"
            generate_annual_report(posts, profile, pdf_filename, start_date, end_date)
            return f'Report generated: {pdf_filename}'
        else:
            return 'Failed to download posts. Please check your credentials and try again.'
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
