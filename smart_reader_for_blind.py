import cv2
import pytesseract
import RPi.GPIO as GPIO
import os
import subprocess

# Set up GPIO pins for buttons
CAPTURE_BUTTON_PIN = 5
PLAY_PAUSE_BUTTON_PIN = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(CAPTURE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PLAY_PAUSE_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize camera
camera = cv2.VideoCapture(0)

# Function to capture image
def capture_image(channel):
    ret, frame = camera.read()
    if ret:  # Check if the frame is captured successfully
        cv2.imwrite("captured_image.jpg", frame)
        print("Image captured successfully!")
        process_image()  # Process the captured image
    else:
        print("Error: Failed to capture image")

# Function to play/pause audio
def play_pause_audio(channel):
    subprocess.run(["pactl", "set-sink-mute", "alsa_output.platform-bcm2835_audio.analog-stereo", "toggle"])

# Function to process image
def process_image():
    # Read the captured image
    captured_image = cv2.imread("captured_image.jpg")
    
    # Apply contrast enhancement
    captured_image = cv2.cvtColor(captured_image, cv2.COLOR_BGR2GRAY)
    captured_image = cv2.equalizeHist(captured_image)
    
    # Apply blurring
    captured_image = cv2.GaussianBlur(captured_image, (5, 5), 0)  # Gaussian blur    
    
def text_to_speech(text):
    """Converts text to speech using Festival."""
    # Adjust Festival parameters for clearer speech
    festival_command = ["festival", "--tts", "--language", "english", "--tts_command", "espeak"]
    
    # Create a subprocess to run Festival with adjusted parameters
    process = subprocess.Popen(festival_command, stdin=subprocess.PIPE)

    # Send the text to Festival
    process.stdin.write(text.encode("utf-8"))
    process.stdin.close()

    # Wait for Festival to finish
    process.wait()
    
# Callbacks for button presses
GPIO.add_event_detect(CAPTURE_BUTTON_PIN, GPIO.FALLING, callback=capture_image, bouncetime=300)
GPIO.add_event_detect(PLAY_PAUSE_BUTTON_PIN, GPIO.FALLING, callback=play_pause_audio, bouncetime=300)

# Main loop
while True:
    # Perform OCR on captured image if it exists
    if os.path.exists("captured_image.jpg"):
        captured_image = cv2.imread("captured_image.jpg")
        if captured_image is not None and captured_image.size > 0:
            gray_image = cv2.cvtColor(captured_image, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(captured_image)
            print("OCR Text:", text)
            
            # Convert text to speech and output to audio jack
            text_to_speech(text)
            
            # Remove the captured image after processing
            os.remove("captured_image.jpg")
        else:
            print("Error: Failed to load captured image")
