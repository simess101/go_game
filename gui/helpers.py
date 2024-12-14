from PIL import Image, ImageTk

def load_image(file_path, size):
    """Load and resize an image."""
    img = Image.open(file_path)
    img = img.resize(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)
