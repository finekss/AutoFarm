# ISSUES
This block is necessary if you encounter errors or issues.
## CUDA: False
There are two ways of this problem first is cpu version of torch. 
Firstly you need to check your CUDA drivers. 
If it's correct, and it still don't work, check *torch* version it could be CPU version. 
If it's true follow the *"Solution for incorrect version"*. 
### Solution for incorrect version
***1. Delete all versions of torch***
```bash
pip uninstall torch torchvision torchaudio torchtext -y
```
***2. Cleaning cache***
```bash
pip cache purge
```
***3. Install torch from Web***
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```