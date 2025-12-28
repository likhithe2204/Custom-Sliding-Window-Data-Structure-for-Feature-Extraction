from typing import List, Optional, Tuple
import math

class CircularBuffer:
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError(f"Capacity must be >= 1, got {capacity}")
            
        self.capacity: int = capacity
        self.buffer: List[float] = [0.0] * capacity  
        self.head: int = 0  
        self.size: int = 0  
        
    def append(self, value: float) -> Optional[float]:
        evicted = None
        
        if self.size == self.capacity:
            evicted = self.buffer[self.head]
        else:
            self.size += 1
            
        self.buffer[self.head] = value
        self.head = (self.head + 1) % self.capacity  
        
        return evicted
    
    def get_window(self) -> List[float]:
        if self.size == 0:
            return []
        
        if self.size < self.capacity:
            return self.buffer[:self.size]
        else:
            return self.buffer[self.head:] + self.buffer[:self.head]
    
    def is_full(self) -> bool:
        return self.size == self.capacity
    
    def __len__(self) -> int:
        return self.size
    
    def __repr__(self) -> str:
        return f"CircularBuffer(capacity={self.capacity}, size={self.size})"


class StreamingStatistics:
    def __init__(self, window_size: int) -> None:
        if window_size < 1:
            raise ValueError(f"Window size must be >= 1, got {window_size}")
            
        self.window_size: int = window_size
        self.mean: float = 0.0
        self.M2: float = 0.0  
        self._initialized: bool = False
        
    def initialize(self, initial_values: List[float]) -> None:
        if len(initial_values) != self.window_size:
            raise ValueError(
                f"Expected {self.window_size} values, got {len(initial_values)}"
            )

        self.mean = sum(initial_values) / self.window_size

        self.M2 = sum((x - self.mean) ** 2 for x in initial_values)
        
        self._initialized = True
        
    def update(self, new_value: float, old_value: float) -> None:
        if not self._initialized:
            raise RuntimeError 

        old_mean = self.mean

        self.mean += (new_value - old_value) / self.window_size
        
        self.M2 -= (old_value - old_mean) * (old_value - self.mean)
 
        self.M2 += (new_value - old_mean) * (new_value - self.mean)
        
    def get_mean(self) -> float:
        return self.mean
    
    def get_variance(self) -> float:
        if self.window_size == 0:
            return 0.0
        return self.M2 / self.window_size
    
    def get_std(self) -> float:
        return math.sqrt(self.get_variance())
    
    def get_statistics(self) -> Tuple[float, float]:
        return (self.mean, self.get_variance())


class StreamingFeatureExtractor:
    def __init__(self, window_size: int) -> None:
        self.window_size = window_size
        self.buffer = CircularBuffer(window_size)
        self.stats = StreamingStatistics(window_size)
        self._ready = False
        
    def process_sample(self, value: float) -> Optional[Tuple[float, float]]:
        evicted = self.buffer.append(value)
        
        if not self._ready:
            if self.buffer.is_full():
                self.stats.initialize(self.buffer.get_window())
                self._ready = True
                return self.stats.get_statistics()
            return None
        else:
            if evicted is not None:
                self.stats.update(value, evicted)
            return self.stats.get_statistics()
    
    def is_ready(self) -> bool:
        return self._ready
    
    def get_window(self) -> List[float]:
        return self.buffer.get_window()