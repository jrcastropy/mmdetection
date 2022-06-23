## How to set up
```
python -m venv venv

source venv/bin/activate
venv\Scripts\activate

pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html

pip install mmcv-full -f https://download.openmmlab.com/mmcv/dist/cu111/torch1.9/index.html

pip install scipy
```