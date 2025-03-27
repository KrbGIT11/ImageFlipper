import os
from flask import Flask, render_template, request
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

# Ensure necessary folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    # Homepage with two buttons
    return render_template('index.html')

@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    static_processed_folder = os.path.join('static', app.config['PROCESSED_FOLDER'])
    processed_images = []  # Store paths of processed images for preview

    if request.method == 'POST':
        uploaded_file = request.files.get('image')
        if uploaded_file:
            input_path = os.path.join(static_processed_folder, uploaded_file.filename)
            os.makedirs(os.path.dirname(input_path), exist_ok=True)
            uploaded_file.save(input_path)
            output_path = os.path.join(static_processed_folder, f"flipped_{uploaded_file.filename}")

            try:
                with Image.open(input_path) as img:
                    # Flip horizontally and vertically
                    flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
                    flipped_img.save(output_path)
                    processed_images.append(output_path)  # Add processed image path for preview
            except Exception as e:
                print(f"Error processing single image: {e}")

        # Render preview and save options
        return render_template('select_images.html', images=processed_images)

    return render_template('upload_image.html')

@app.route('/upload_images', methods=['POST'])
def upload_images():
    static_processed_folder = os.path.join('static', app.config['PROCESSED_FOLDER'])
    os.makedirs(static_processed_folder, exist_ok=True)
    processed_images = []

    uploaded_files = request.files.getlist('images')  # Receive multiple files

    for uploaded_file in uploaded_files:
        if uploaded_file.filename:
            input_path = os.path.join(static_processed_folder, uploaded_file.filename)
            os.makedirs(os.path.dirname(input_path), exist_ok=True)  # Ensure path exists
            uploaded_file.save(input_path)
            output_path = os.path.join(static_processed_folder, f"flipped_{uploaded_file.filename}")

            try:
                with Image.open(input_path) as img:
                    # Flip horizontally and vertically
                    flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
                    flipped_img.save(output_path)
                    processed_images.append(output_path)  # Track processed images
            except Exception as e:
                print(f"Error processing {uploaded_file.filename}: {e}")

    return render_template('select_images.html', images=processed_images)


@app.route('/upload_folder', methods=['GET', 'POST'])
def upload_folder():
    static_processed_folder = os.path.join('static', app.config['PROCESSED_FOLDER'])

    if request.method == 'POST':
        uploaded_files = request.files.getlist('folder')  # Handle multiple files

        if uploaded_files:
            # Extract original folder name
            folder_name = os.path.basename(os.path.dirname(uploaded_files[0].filename.strip()))
            edited_folder_name = f"edited_{folder_name}"
            edited_folder_path = os.path.join(static_processed_folder, edited_folder_name)
            os.makedirs(edited_folder_path, exist_ok=True)

            for uploaded_file in uploaded_files:
                if uploaded_file.filename:
                    # Create temporary directory dynamically
                    temp_folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
                    os.makedirs(temp_folder, exist_ok=True)
                    input_path = os.path.join(temp_folder, os.path.basename(uploaded_file.filename))
                    uploaded_file.save(input_path)

                    # Process and save flipped image to the "edited_" folder
                    output_path = os.path.join(edited_folder_path,
                                               f"flipped_{os.path.basename(uploaded_file.filename)}")

                    try:
                        with Image.open(input_path) as img:
                            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
                            flipped_img.save(output_path)
                    except Exception as e:
                        print(f"Error processing image {uploaded_file.filename}: {e}")

            return f"<h1>Folder processed and saved to {edited_folder_name}!</h1><a href='/'>Go Back</a>"

    return render_template('upload_folder.html')

@app.route('/save_images', methods=['POST'])
def save_images():
    # Get folder name or fallback to "default"
    folder_name = request.form.get('folder_name', '').strip() or 'default'
    selected_images = request.form.getlist('selected_images')  # Allow multi-selection

    # Ensure the folder for saving exists
    save_folder = os.path.join('static', app.config['PROCESSED_FOLDER'], folder_name)
    os.makedirs(save_folder, exist_ok=True)

    # Save selected images
    for image_path in selected_images:
        image_name = os.path.basename(image_path)  # Get just the file name
        input_path = os.path.join(app.root_path, image_path)  # Full path of the source
        output_path = os.path.join(save_folder, image_name)  # Save to the target folder

        try:
            os.replace(input_path, output_path)  # Move file to the save folder
            print(f"Saved {image_name} to {save_folder}")
        except Exception as e:
            print(f"Error saving image {image_name}: {e}")

    # Display success message
    return (f"<h1>Selected images have been saved to the folder: {folder_name}</h1>"
            f"<a href='/'>Go Back</a>")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
