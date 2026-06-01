import os
import sys
import torch
from ultralytics import YOLO

def main():
    print("==================================================")
    print("   Robotic Platform TensorRT Optimizer Utility    ")
    print("==================================================")
    
    # Check CUDA availability
    cuda_available = torch.cuda.is_available()
    print(f"[SYSTEM] CUDA Available: {cuda_available}")
    
    if not cuda_available:
        print("[ERROR] CUDA is not available on this system. TensorRT compilation requires an NVIDIA GPU.")
        sys.exit(1)
        
    # Get current backend folder path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    pt_model_path = os.path.join(backend_dir, "yolov8s-world.pt")
    engine_model_path = os.path.join(backend_dir, "yolov8s-world.engine")
    
    print(f"[INFO] Backend directory: {backend_dir}")
    print(f"[INFO] Target PyTorch model: {pt_model_path}")
    print(f"[INFO] Output TensorRT engine: {engine_model_path}")
    
    if not os.path.exists(pt_model_path):
        print(f"[ERROR] Could not find PyTorch model file: {pt_model_path}")
        print("[INFO] Please ensure 'yolov8s-world.pt' is present in the backend directory.")
        sys.exit(1)
        
    print("[INFO] Loading PyTorch model...")
    try:
        model = YOLO(pt_model_path)
    except Exception as e:
        print(f"[ERROR] Failed to load PyTorch model: {e}")
        sys.exit(1)
        
    print("[INFO] Starting compilation to TensorRT engine...")
    print("[INFO] NOTE: This process compiles the model using FP16 (half-precision).")
    print("[INFO] This may take a few minutes on the first run...")
    
    try:
        # Export the model to TensorRT format
        # format="engine" generates a TensorRT .engine file
        # half=True compiles the model using FP16 mode
        # device=0 selects the first GPU device
        # dynamic=True allows variable shape handling
        exported_path = model.export(
            format="engine",
            device=0,
            half=True,
            dynamic=False,
            simplify=False,
            opset=18,
            imgsz=672
        )
        print(f"[SUCCESS] Export completed. Model path: {exported_path}")
        
        # Verify the file was created and name it appropriately if needed
        expected_output = pt_model_path.replace(".pt", ".engine")
        if os.path.exists(expected_output):
            print(f"[SUCCESS] TensorRT engine compiled successfully at: {expected_output}")
        else:
            print(f"[WARN] Completed without errors, but expected engine file not found at: {expected_output}")
            
    except Exception as e:
        print(f"[ERROR] Compilation failed: {e}")
        print("[TIP] Verify that the 'tensorrt' python module and system level TensorRT libraries are installed correctly.")
        sys.exit(1)

if __name__ == "__main__":
    main()
