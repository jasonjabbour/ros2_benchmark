import GPUtil
import cpuinfo

class DeviceInfo:
    
    def get_gpu_names(self) -> str:
        """Get the GPU names."""
        GPUs = GPUtil.getGPUs()
        if not GPUs:
            return "No GPU detected"
        
        return ', '.join(gpu.name for gpu in GPUs)
    
    def get_cpu_name(self) -> str:
        """Get the CPU info."""
        cpu_info = cpuinfo.get_cpu_info()
        return cpu_info.get('brand_raw', 'Unknown CPU')
    
    def get_device_name(self) -> str:
        """Get combined CPU and GPU info."""
        cpu_name = self.get_cpu_name()
        gpu_names = self.get_gpu_names()

        return f"CPU_Name {cpu_name}, GPU_Name {gpu_names}"

# Example usage
if __name__ == "__main__":
    device_info = DeviceInfo()
    print(device_info.get_device_name())