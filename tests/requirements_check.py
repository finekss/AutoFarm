"""
Dependency checker for AutoFarm.
Validates Python version, PyTorch/CUDA, CV/RL packages, and optional components.
"""
import sys
import subprocess
import importlib
from pathlib import Path
from typing import Optional

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def check_python_version(required: str = "3.12") -> bool:
    """Check Python version compatibility."""
    current = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info.major == 3 and sys.version_info.minor >= 12:
        print(f"{Colors.GREEN}✓{Colors.END} Python: {sys.version.split()[0]} (≥{required})")
        return True
    print(f"{Colors.RED}✗{Colors.END} Python: {current} (required ≥{required})")
    return False


def check_package(name: str, min_version: Optional[str] = None,
                  import_name: Optional[str] = None, optional: bool = False) -> bool:
    """
    Check if package is installed and meets version requirements.

    Args:
        name: Package name as in /requirements.txt
        min_version: Minimum required version (e.g., "2.3.0")
        import_name: Module name for import (if different from package name)
        optional: If True, failure shows warning instead of error
    """
    import_name = import_name or name

    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')

        # Basic version check (simple semver comparison)
        if min_version and version != 'unknown':
            def parse_ver(v: str) -> tuple:
                return tuple(map(int, v.split('+')[0].split('.')[:3]))

            if parse_ver(version) < parse_ver(min_version):
                prefix = Colors.YELLOW if optional else Colors.RED
                symbol = "⚠" if optional else "✗"
                print(f"{prefix}{symbol}{Colors.END} {name}: {version} (required ≥{min_version})")
                return not optional

        prefix = Colors.GREEN if not optional else Colors.YELLOW
        symbol = "✓" if not optional else "⚠"
        print(f"{prefix}{symbol}{Colors.END} {name}: {version}")
        return True

    except ImportError as e:
        prefix = Colors.YELLOW if optional else Colors.RED
        symbol = "⊘" if optional else "✗"
        print(f"{prefix}{symbol}{Colors.END} {name}: NOT INSTALLED")
        if not optional:
            print(f"   {Colors.BLUE}→ Fix:{Colors.END} pip install {name}")
        return optional  # Return True if optional


def check_torch_cuda() -> bool:
    """Comprehensive PyTorch + CUDA check with performance test."""
    try:
        import torch

        print(f"\n{Colors.BOLD}🔬 PyTorch & CUDA:{Colors.END}")
        print(f"  Version: {torch.__version__}")

        if not torch.cuda.is_available():
            print(f"  {Colors.RED}✗ CUDA: Not available{Colors.END}")
            print(f"  {Colors.BLUE}→ Fix:{Colors.END} Reinstall PyTorch with CUDA:")
            print(f"     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124")
            return False

        print(f"  {Colors.GREEN}✓ CUDA: Available{Colors.END}")
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  CUDA runtime: {torch.version.cuda}")
        print(f"  cuDNN: {torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else 'N/A'}")

        # Quick performance test
        try:
            x = torch.rand(1000, 1000, device='cuda')
            y = torch.mm(x, x.T)
            torch.cuda.synchronize()
            print(f"  {Colors.GREEN}✓ GPU compute test: PASSED{Colors.END}")
            return True
        except Exception as e:
            print(f"  {Colors.RED}✗ GPU compute test: FAILED ({e}){Colors.END}")
            return False

    except ImportError:
        print(f"  {Colors.RED}✗ PyTorch: NOT INSTALLED{Colors.END}")
        return False


def check_optional_components() -> None:
    """Check optional/extended dependencies."""
    print(f"\n{Colors.BOLD}🔌 Optional Components:{Colors.END}")

    # Computer Vision extensions
    check_package('opencv-python', import_name='cv2', optional=True)
    check_package('ultralytics', min_version='8.2', optional=True)

    # OCR (for UI text recognition)
    check_package('easyocr', optional=True)
    check_package('pytesseract', optional=True)

    # Input emulation
    check_package('mss', optional=True)
    check_package('pydirectinput', optional=True)
    check_package('pynput', optional=True)

    # Experiment tracking
    check_package('wandb', optional=True)
    check_package('mlflow', optional=True)

def print_summary(all_checks: list[bool]) -> None:
    """Print final summary with actionable next steps."""
    print(f"\n{Colors.BOLD}{'=' * 60}{Colors.END}")

    if all(all_checks):
        print(f"{Colors.GREEN}🎉 All critical dependencies are ready!{Colors.END}")
    else:
        print(f"{Colors.RED}❌ Some dependencies are missing or misconfigured.{Colors.END}")
        print(f"\n{Colors.BOLD}To fix:{Colors.END}")
        print(f"  1. Activate virtual environment: .venv\\Scripts\\activate")
        print(f"  2. Install remaining deps: pip install -r requirements.txt")
        print(f"  3. Re-run this check: python .\\tests\\requirements_check.py")
        print(f" If it still not pass this test check .\\README.md")

    print(f"{Colors.BOLD}{'=' * 60}{Colors.END}")


def main() -> int:
    """Main entry point. Returns exit code (0=success, 1=failure)."""
    print(f"{Colors.BOLD}🔍 Dependency Checker{Colors.END}")
    print(f"Python: {sys.executable}\n")

    checks = []

    # Core checks (must pass)
    print(f"{Colors.BOLD}🔑 Critical Dependencies:{Colors.END}")
    checks.append(check_python_version("3.12"))
    checks.append(check_package('pydantic', min_version='2.8'))
    checks.append(check_package('numpy', min_version='1.26'))
    checks.append(check_package('gymnasium', min_version='0.29'))
    checks.append(check_package('stable_baselines3', min_version='2.3', import_name='stable_baselines3'))

    # PyTorch/CUDA (critical for performance)
    checks.append(check_torch_cuda())

    # Core architecture deps
    checks.append(check_package('omegaconf'))
    checks.append(check_package('loguru'))

    # Optional components (warnings only)
    check_optional_components()

    # Summary
    print_summary(checks)

    return 0 if all(checks) else 1


if __name__ == '__main__':
    sys.exit(main())