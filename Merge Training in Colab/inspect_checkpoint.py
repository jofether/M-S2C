"""
PyTorch Checkpoint Inspector
============================
This script loads a .pt checkpoint file and displays:
- Model layer names
- Parameter shapes
- Total parameters
- Memory size
"""

import torch
import os

def inspect_checkpoint(checkpoint_path):
    """Load and display checkpoint contents"""
    
    if not os.path.exists(checkpoint_path):
        print(f"❌ File not found: {checkpoint_path}")
        return
    
    print(f"\n{'='*70}")
    print(f"📦 CHECKPOINT INSPECTOR: {os.path.basename(checkpoint_path)}")
    print(f"{'='*70}\n")
    
    # Get file size
    file_size_mb = os.path.getsize(checkpoint_path) / (1024 * 1024)
    print(f"📊 File Size: {file_size_mb:.2f} MB\n")
    
    # Load checkpoint
    try:
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
    except Exception as e:
        print(f"❌ Error loading checkpoint: {e}")
        return
    
    # Check what's in the checkpoint
    print(f"📋 Checkpoint Type: {type(checkpoint)}\n")
    
    # If it's a dictionary (most common - state_dict)
    if isinstance(checkpoint, dict):
        print(f"📂 Keys in checkpoint: {list(checkpoint.keys())}\n")
        
        # If it contains 'state_dict' key (common format)
        if 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
        else:
            # Otherwise treat entire dict as state_dict
            state_dict = checkpoint
        
        print(f"🔍 MODEL STRUCTURE:\n")
        print(f"{'Layer Name':<50} {'Shape':<30} {'Parameters':<15}")
        print("-" * 95)
        
        total_params = 0
        for name, param in state_dict.items():
            param_count = param.numel()
            total_params += param_count
            shape_str = str(list(param.shape))
            print(f"{name:<50} {shape_str:<30} {param_count:>14,d}")
        
        print("-" * 95)
        print(f"{'TOTAL':<50} {'':<30} {total_params:>14,d}")
        print(f"\n✅ Total Parameters: {total_params:,} ({total_params/1e6:.2f}M)\n")
        
        # Estimate memory used
        memory_mb = (total_params * 4) / (1024 * 1024)  # 4 bytes per float32
        print(f"💾 Estimated Model Memory: {memory_mb:.2f} MB\n")
        
        # Show model components
        print(f"📦 MODEL COMPONENTS:\n")
        
        components = {
            'codebert': [],
            'vit': [],
            'projection': [],
            'gating': [],
            'other': []
        }
        
        for name in state_dict.keys():
            if 'codebert' in name.lower():
                components['codebert'].append(name)
            elif 'vit' in name.lower():
                components['vit'].append(name)
            elif 'projection' in name.lower():
                components['projection'].append(name)
            elif 'gating' in name.lower():
                components['gating'].append(name)
            else:
                components['other'].append(name)
        
        for component, layers in components.items():
            if layers:
                print(f"  🔹 {component.upper()}: {len(layers)} layers")
                for layer in layers[:3]:  # Show first 3
                    print(f"      - {layer}")
                if len(layers) > 3:
                    print(f"      ... and {len(layers) - 3} more")
        
        print("\n" + "="*70 + "\n")
    
    else:
        # It's a state_dict directly
        print(f"🔍 MODEL LAYERS:\n")
        print(f"{'Layer Name':<50} {'Shape':<30} {'Parameters':<15}")
        print("-" * 95)
        
        total_params = 0
        for name, param in checkpoint.items():
            param_count = param.numel()
            total_params += param_count
            shape_str = str(list(param.shape))
            print(f"{name:<50} {shape_str:<30} {param_count:>14,d}")
        
        print(f"\n✅ Total trainable parameters: {total_params:,}\n")


if __name__ == "__main__":
    
    # Try to find .pt files in current directory
    current_dir = os.getcwd()
    pt_files = [f for f in os.listdir(current_dir) if f.endswith('.pt')]
    
    if pt_files:
        print(f"\n🔎 Found {len(pt_files)} checkpoint file(s) in current directory:\n")
        for pt_file in pt_files:
            print(f"  • {pt_file}")
        print()
        
        # Inspect each one
        for pt_file in pt_files:
            inspect_checkpoint(pt_file)
    else:
        print(f"⚠️  No .pt files found in {current_dir}")
        print("\nUsage: python inspect_checkpoint.py")
        print("\nOr modify the script to inspect a specific file:")
        print("  inspect_checkpoint('path/to/checkpoint.pt')")
