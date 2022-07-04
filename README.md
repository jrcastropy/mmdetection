# How to set up

### Create a virtual environment
```
python -m venv venv
```

### Activate your Virtual Environment
If you are using Linux (Ubuntu)
```
source venv/bin/activate
```

If you are using Windows
```
venv\Scripts\activate
```

### step by step run the codes below
```
pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
pip install mmcv-full -f https://download.openmmlab.com/mmcv/dist/cu111/torch1.9/index.html
pip install scipy
git clone https://github.com/jrcastropy/mmdetection.git
```

## Download config here for centernet
[Centernet Model](https://download.openmmlab.com/mmdetection/v2.0/centernet/centernet_resnet18_dcnv2_140e_coco/centernet_resnet18_dcnv2_140e_coco_20210702_155131-c8cd631f.pth)
