"""
Image Generation Module
Uses local Stable Diffusion models via diffusers library
Supports text-to-image, image-to-image, and image editing
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
import time


class ImageGenerator:
    """Local image generation using Stable Diffusion"""

    def __init__(self, model_id: str = "stabilityai/stable-diffusion-2-1",
                 output_dir: str = "./data/generated_images"):
        """
        Initialize image generator

        Args:
            model_id: HuggingFace model ID for Stable Diffusion
            output_dir: Directory to save generated images
        """
        self.model_id = model_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.pipe = None
        self.device = None
        self.initialized = False

    def initialize(self):
        """Initialize Stable Diffusion pipeline"""
        try:
            import torch
            from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

            print(f"Loading Stable Diffusion model: {self.model_id}")
            print("This may take a while on first run...")

            # Determine device
            if torch.cuda.is_available():
                self.device = "cuda"
                print("Using CUDA GPU")
            elif torch.backends.mps.is_available():
                self.device = "mps"
                print("Using Apple Silicon GPU")
            else:
                self.device = "cpu"
                print("Warning: No GPU detected, using CPU (will be slow)")

            # Load pipeline
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
                safety_checker=None  # Disable for local use
            )

            # Use faster scheduler
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )

            # Move to device
            self.pipe = self.pipe.to(self.device)

            # Enable memory optimizations
            if self.device != "cpu":
                self.pipe.enable_attention_slicing()

            self.initialized = True
            print("Image generator ready!")

        except ImportError as e:
            raise ImportError(f"Required dependencies not installed: {e}")

    def generate_image(self,
                      prompt: str,
                      negative_prompt: Optional[str] = None,
                      width: int = 512,
                      height: int = 512,
                      num_inference_steps: int = 25,
                      guidance_scale: float = 7.5,
                      seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate image from text prompt

        Args:
            prompt: Text description of desired image
            negative_prompt: What to avoid in the image
            width: Image width (must be multiple of 8)
            height: Image height (must be multiple of 8)
            num_inference_steps: Number of denoising steps (higher = better quality, slower)
            guidance_scale: How closely to follow prompt (7-15 recommended)
            seed: Random seed for reproducibility

        Returns:
            Dict with image path and metadata
        """
        if not self.initialized:
            raise RuntimeError("Image generator not initialized. Call initialize() first")

        # Set seed for reproducibility
        if seed is not None:
            import torch
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = None
            seed = int(time.time())

        print(f"Generating image: '{prompt[:50]}...'")
        start_time = time.time()

        # Generate
        result = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt or "blurry, low quality, distorted",
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator
        )

        image = result.images[0]
        generation_time = time.time() - start_time

        # Save image
        timestamp = int(time.time())
        filename = f"img_{timestamp}_{seed}.png"
        output_path = self.output_dir / filename
        image.save(output_path)

        print(f"Image generated in {generation_time:.2f}s: {output_path}")

        return {
            'success': True,
            'image_path': str(output_path),
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'width': width,
            'height': height,
            'steps': num_inference_steps,
            'guidance_scale': guidance_scale,
            'seed': seed,
            'generation_time': generation_time,
            'model': self.model_id
        }

    def generate_variations(self,
                           prompt: str,
                           num_variations: int = 4,
                           **kwargs) -> Dict[str, Any]:
        """
        Generate multiple variations of an image

        Args:
            prompt: Text description
            num_variations: Number of variations to generate
            **kwargs: Additional parameters for generate_image

        Returns:
            Dict with list of generated images
        """
        if not self.initialized:
            raise RuntimeError("Image generator not initialized")

        images = []
        print(f"Generating {num_variations} variations...")

        for i in range(num_variations):
            # Use different seed for each variation
            result = self.generate_image(prompt, seed=i, **kwargs)
            images.append(result)

        return {
            'success': True,
            'num_images': len(images),
            'images': images,
            'prompt': prompt
        }


class ImageEditor:
    """Image editing and manipulation tools"""

    def __init__(self):
        self.initialized = False

    def initialize(self):
        """Initialize image editing tools"""
        try:
            import torch
            from diffusers import StableDiffusionImg2ImgPipeline

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print("Image editor initialized")
            self.initialized = True

        except ImportError as e:
            raise ImportError(f"Required dependencies not installed: {e}")

    def resize_image(self, image_path: str, width: int, height: int) -> Dict[str, Any]:
        """Resize image to specified dimensions"""
        try:
            from PIL import Image

            img = Image.open(image_path)
            resized = img.resize((width, height), Image.Resampling.LANCZOS)

            # Save resized image
            output_path = str(Path(image_path).with_stem(f"{Path(image_path).stem}_resized"))
            resized.save(output_path)

            return {
                'success': True,
                'original_path': image_path,
                'output_path': output_path,
                'original_size': img.size,
                'new_size': (width, height)
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def convert_format(self, image_path: str, format: str) -> Dict[str, Any]:
        """Convert image to different format (PNG, JPEG, WebP, etc.)"""
        try:
            from PIL import Image

            img = Image.open(image_path)
            output_path = str(Path(image_path).with_suffix(f".{format.lower()}"))
            img.save(output_path, format=format.upper())

            return {
                'success': True,
                'original_path': image_path,
                'output_path': output_path,
                'format': format
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """Get detailed information about an image"""
        try:
            from PIL import Image
            import os

            img = Image.open(image_path)

            return {
                'path': image_path,
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
                'file_size': os.path.getsize(image_path),
                'info': img.info
            }

        except Exception as e:
            return {'error': str(e)}
