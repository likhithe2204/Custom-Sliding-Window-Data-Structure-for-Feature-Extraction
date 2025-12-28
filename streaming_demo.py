import asyncio
import math
import random
from typing import AsyncGenerator
from sliding_window import StreamingFeatureExtractor


async def generate_synthetic_stream(
    num_samples: int,
    sample_rate_hz: float = 100.0,
    pattern: str = "noisy_sine"
) -> AsyncGenerator[float, None]:
    
    delay = 1.0 / sample_rate_hz  

    if pattern == "random_walk":
        value = 0.0
    elif pattern == "noisy_sine":
        frequency = 2.0  # Hz
        amplitude = 10.0
        phase = 0.0
    
    for i in range(num_samples):
        if pattern == "noisy_sine":
            t = i / sample_rate_hz
            signal = amplitude * math.sin(2 * math.pi * frequency * t + phase)
            noise = random.gauss(0, 1.0)
            sample = signal + noise
            
        elif pattern == "random_walk":
            step = random.gauss(0, 0.5)
            value += step
            sample = value
            
        elif pattern == "white_noise":
            sample = random.gauss(0, 5.0)
            
        else:
            raise ValueError(f"Unknown pattern: {pattern}")
        
        yield sample


async def run_streaming_demo(
    window_size: int = 50,
    num_samples: int = 500,
    sample_rate_hz: float = 100.0,
    verbose: bool = True
) -> None:
    
    print(f"=== Streaming Feature Extraction Demo ===")
    print(f"Window Size: {window_size}")
    print(f"Total Samples: {num_samples}")
    print(f"Sample Rate: {sample_rate_hz} Hz")
    print(f"Pattern: Noisy Sine Wave")
    print("=" * 50)
    print()
    
    extractor = StreamingFeatureExtractor(window_size)
    stream = generate_synthetic_stream(
        num_samples, 
        sample_rate_hz, 
        pattern="noisy_sine"
    )
    
    sample_count = 0
    
    async for value in stream:
        sample_count += 1

        features = extractor.process_sample(value)

        if features is not None:
            mean, variance = features
            std = math.sqrt(variance)
            
            if verbose or sample_count % 50 == 0:
                print(f"Sample {sample_count:4d} | "
                      f"Value: {value:7.3f} | "
                      f"Mean: {mean:7.3f} | "
                      f"Std: {std:6.3f} | "
                      f"Var: {variance:7.3f}")
        else:
            if verbose or sample_count % 10 == 0:
                print(f"Sample {sample_count:4d} | "
                      f"Value: {value:7.3f} | "
                      f"[Warming up... {sample_count}/{window_size}]")
    
    print()
    print(f"=== Demo Complete: Processed {sample_count} samples ===")


async def run_validation_demo(window_size: int = 50, num_samples: int = 1000) -> None:

    import numpy as np
    
    print(f"=== Validation Demo ===")
    print(f"Window Size: {window_size}")
    print(f"Comparing against NumPy ground truth...")
    print()
    
    extractor = StreamingFeatureExtractor(window_size)
    stream = generate_synthetic_stream(num_samples, 1000.0, "white_noise")
    
    all_samples = []
    max_error_mean = 0.0
    max_error_var = 0.0
    validation_count = 0
    
    async for value in stream:
        all_samples.append(value)
        features = extractor.process_sample(value)
        
        if features is not None and len(all_samples) >= window_size:

            our_mean, our_var = features
            
            window = all_samples[-window_size:]
            numpy_mean = np.mean(window)
            numpy_var = np.var(window)          
            
            error_mean = abs(our_mean - numpy_mean)
            error_var = abs(our_var - numpy_var)
            
            max_error_mean = max(max_error_mean, error_mean)
            max_error_var = max(max_error_var, error_var)
            
            validation_count += 1
            
            if validation_count % 100 == 0:
                print(f"Validated {validation_count} windows | "
                      f"Max Mean Error: {max_error_mean:.2e} | "
                      f"Max Var Error: {max_error_var:.2e}")
    
    print()
    print(f"=== Validation Results ===")
    print(f"Validated Windows: {validation_count}")
    print(f"Maximum Mean Error: {max_error_mean:.2e}")
    print(f"Maximum Variance Error: {max_error_var:.2e}")
    
    tolerance = 1e-9
    if max_error_mean < tolerance and max_error_var < tolerance:
        print(f"✓ PASSED: All errors below tolerance ({tolerance:.2e})")
    else:
        print(f"✗ FAILED: Errors exceed tolerance ({tolerance:.2e})")


if __name__ == "__main__":
    asyncio.run(run_streaming_demo(
        window_size=50,
        num_samples=200,
        sample_rate_hz=100.0,
        verbose=False  
    ))
    
    print("\n" + "=" * 50 + "\n")

    asyncio.run(run_validation_demo(
        window_size=50,
        num_samples=1000
    ))