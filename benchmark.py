import time
import random
import statistics
from typing import List, Tuple, Dict
from sliding_window import StreamingFeatureExtractor


def generate_benchmark_data(num_samples: int) -> List[float]:

    random.seed(42)  # Reproducible results
    return [random.gauss(0, 10.0) for _ in range(num_samples)]


def benchmark_window_size(
    window_size: int,
    num_samples: int = 50000,
    warmup_samples: int = 1000
) -> Dict[str, float]:

    data = generate_benchmark_data(num_samples + warmup_samples)
    extractor = StreamingFeatureExtractor(window_size)
    
    latencies = []
    
    for i in range(warmup_samples):
        extractor.process_sample(data[i])
    
    for i in range(warmup_samples, warmup_samples + num_samples):
        start = time.perf_counter()
        extractor.process_sample(data[i])
        end = time.perf_counter()
        
        latencies.append((end - start) * 1_000_000)  
    
    return {
        "window_size": window_size,
        "samples": num_samples,
        "mean_us": statistics.mean(latencies),
        "median_us": statistics.median(latencies),
        "min_us": min(latencies),
        "max_us": max(latencies),
        "p95_us": statistics.quantiles(latencies, n=20)[18],  
        "p99_us": statistics.quantiles(latencies, n=100)[98],  
        "stdev_us": statistics.stdev(latencies)
    }


def benchmark_suite() -> List[Dict[str, float]]:
    """
    Run comprehensive benchmark suite across multiple window sizes.
    
    Returns:
        List of benchmark results for each window size
    """
    window_sizes = [10, 50, 100, 500, 1000, 5000]
    num_samples = 50000
    
    print("=" * 70)
    print("STREAMING FEATURE EXTRACTION BENCHMARK SUITE")
    print("=" * 70)
    print(f"Samples per test: {num_samples:,}")
    print(f"Warmup samples: 1,000")
    print(f"Timer: time.perf_counter() (nanosecond resolution)")
    print("=" * 70)
    print()
    
    results = []
    
    for window_size in window_sizes:
        print(f"Benchmarking window size: {window_size:,}...", end=" ", flush=True)
        
        start_time = time.time()
        result = benchmark_window_size(window_size, num_samples)
        elapsed = time.time() - start_time
        
        results.append(result)
        
        print(f"Done ({elapsed:.2f}s)")
    
    return results


def print_benchmark_results(results: List[Dict[str, float]]) -> None:
    print()
    print("=" * 70)
    print("BENCHMARK RESULTS")
    print("=" * 70)
    print()
    
    print(f"{'Window Size':<12} {'Mean (μs)':<12} {'Median (μs)':<12} "
          f"{'Min (μs)':<10} {'Max (μs)':<10} {'P95 (μs)':<10} {'P99 (μs)':<10}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['window_size']:<12,} "
              f"{r['mean_us']:<12.3f} "
              f"{r['median_us']:<12.3f} "
              f"{r['min_us']:<10.3f} "
              f"{r['max_us']:<10.3f} "
              f"{r['p95_us']:<10.3f} "
              f"{r['p99_us']:<10.3f}")
    
    print()
    print("=" * 70)
    print("THROUGHPUT ANALYSIS")
    print("=" * 70)
    print()
    
    for r in results:
        samples_per_sec = 1_000_000 / r['mean_us']  
        print(f"Window {r['window_size']:<6,}: "
              f"{samples_per_sec:>12,.0f} samples/sec  "
              f"({r['mean_us']:.3f} μs/sample)")
    
    print()


def analyze_complexity(results: List[Dict[str, float]]) -> None:
    print("=" * 70)
    print("COMPLEXITY ANALYSIS")
    print("=" * 70)
    print()
    
    print("Expected Complexity: O(1) per sample (constant time)")
    print()
    print("Verification:")
    
    # Check if latency is roughly constant regardless of window size
    latencies = [r['mean_us'] for r in results]
    window_sizes = [r['window_size'] for r in results]
    
    min_latency = min(latencies)
    max_latency = max(latencies)
    ratio = max_latency / min_latency
    
    print(f"  Minimum mean latency: {min_latency:.3f} μs (window={window_sizes[latencies.index(min_latency)]})")
    print(f"  Maximum mean latency: {max_latency:.3f} μs (window={window_sizes[latencies.index(max_latency)]})")
    print(f"  Ratio (max/min): {ratio:.2f}x")
    print()
    
    if ratio < 2.0:
        print("✓ CONFIRMED: Latency remains roughly constant across window sizes")
        print("  This validates O(1) per-sample complexity")
    else:
        print("⚠ WARNING: Latency varies significantly with window size")
        print("  This may indicate O(N) behavior or cache effects")
    
    print()


def stress_test() -> None:
    print("=" * 70)
    print("STRESS TEST: Large Window")
    print("=" * 70)
    print()
    
    window_size = 100000
    num_samples = 10000
    
    print(f"Window size: {window_size:,}")
    print(f"Samples: {num_samples:,}")
    print()
    print("Running...", end=" ", flush=True)
    
    result = benchmark_window_size(window_size, num_samples, warmup_samples=100)
    
    print("Done")
    print()
    print(f"Mean latency: {result['mean_us']:.3f} μs")
    print(f"Throughput: {1_000_000 / result['mean_us']:,.0f} samples/sec")
    print()


if __name__ == "__main__":
    results = benchmark_suite()
    print_benchmark_results(results)
    analyze_complexity(results)
    
    stress_test()
    
    print("=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)