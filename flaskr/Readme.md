# Video Watermark Remover

A web application that allows users to remove watermarks from video files easily with just a few clicks. This application uses computer vision techniques to remove or blur watermarks, logos, or other unwanted elements from videos.

## Features

- **Drag & Drop Interface** - Easy upload of video files
- **Visual Selection Tool** - Draw a rectangle around the watermark you want to remove
- **Multiple Removal Methods** - Choose between inpainting (better for complex backgrounds) or blur (faster)
- **Real-time Processing Status** - Monitor progress with a visual progress bar
- **Secure File Handling** - Automatic file cleanup after processing
- **Responsive Design** - Works on desktop and mobile devices

## How It Works

1. **Upload** - Upload any video file containing a watermark
2. **Select** - Draw a rectangle around the watermark area you want to remove
3. **Process** - Choose a removal method and process the video
4. **Download** - Get your watermark-free video

## Supported File Formats

- MP4
- AVI
- MOV
- MKV
- WEBM

## Technical Details

This application is built with:

- **Backend**: Flask (Python)
- **Computer Vision**: OpenCV
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Video Processing**: 
  - Inpainting algorithm (TELEA method)
  - Gaussian blur

## Installation

### Prerequisites

- Python 3.6+
- pip

### Setup via venv

1. Clone the repository:
   ```
   git clone https://github.com/donationhands/Python-Video-Watermark-Remover.git
   cd Python-Video-Watermark-Remover
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   flask --app flaskr run --debug or flask --app app.run --debug
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

### Setup via conda

1. Create a new conda environment

```bash
conda create --name flask_env python=3.9
conda activate flask_env
```

2. Clone the repository and navigate to the project directory

```bash
git clone https://github.com/your-github-username/watermark-remover-flask.git
cd watermark-remover-flask
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run the application:
   ```
   flask --app flaskr run --debug or flask --app app.run --debug
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```
   
## Configuration

Contributions are welcome! Please feel free to submit a Pull Request.

- Fork the repository
- Create your feature branch (git checkout -b feature/amazing-feature)
- Commit your changes (git commit -m 'Add some amazing feature')
- Push to the branch (git push origin feature/amazing-feature)
- Open a Pull Request

## Security Considerations

- Files are automatically cleaned up after 1 hour to save disk space
- Input validation prevents directory traversal attacks
- Secure filename handling prevents malicious uploads

## Usage Notes

- Processing time depends on video length, resolution, and your hardware
- For best results, make sure the watermark selection is precise
- The inpainting method works best for static watermarks on complex backgrounds
- The blur method is faster and may look more natural in some cases

## License

This project is licensed under the MIT License.

## Acknowledgements

This project uses:
- [Flask](https://flask.palletsprojects.com/)
- [OpenCV](https://opencv.org/)
- [Bootstrap](https://getbootstrap.com/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
