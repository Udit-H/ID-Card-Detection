from ultralytics import YOLO
def main():
    model = YOLO('yolov8s.pt') # Changed from yolov8n.pt to yolov8s.pt
    model.train(
    data='data.yaml',
    epochs=100, # Good starting point for ~700 images
    imgsz=640, # Standard size for YOLOv8
    batch=32, # Optional: adjust depending on CPU threads
    )
if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    main()
