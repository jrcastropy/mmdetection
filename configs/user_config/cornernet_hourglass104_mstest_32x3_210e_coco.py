import main_config

_base_ = [
    '../_base_/default_runtime.py', '../_base_/datasets/coco_detection.py'
]

# model settings
model = dict(
    type='CornerNet',
    backbone=dict(
        type='HourglassNet',
        downsample_times=5,
        num_stacks=2,
        stage_channels=[256, 256, 384, 384, 384, 512],
        stage_blocks=[2, 2, 2, 2, 2, 4],
        norm_cfg=dict(type='BN', requires_grad=True)),
    neck=None,
    bbox_head=dict(
        type='CornerHead',
        num_classes=main_config.num_class,
        in_channels=256,
        num_feat_levels=2,
        corner_emb_channels=1,
        loss_heatmap=dict(
            type='GaussianFocalLoss', alpha=2.0, gamma=4.0, loss_weight=1),
        loss_embedding=dict(
            type='AssociativeEmbeddingLoss',
            pull_weight=0.10,
            push_weight=0.10),
        loss_offset=dict(type='SmoothL1Loss', beta=1.0, loss_weight=1)),
    # training and testing settings
    train_cfg=None,
    test_cfg=dict(
        corner_topk=100,
        local_maximum_kernel=3,
        distance_threshold=0.5,
        score_thr=0.05,
        max_per_img=100,
        nms=dict(type='soft_nms', iou_threshold=0.5, method='gaussian')))
# data settings
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
train_pipeline = [
    dict(type='LoadImageFromFile', to_float32=True),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(
        type='PhotoMetricDistortion',
        brightness_delta=32,
        contrast_range=(0.5, 1.5),
        saturation_range=(0.5, 1.5),
        hue_delta=18),
    dict(
        type='RandomCenterCropPad',
        crop_size=(511, 511),
        ratios=(0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3),
        test_mode=False,
        test_pad_mode=None,
        **img_norm_cfg),
    dict(type='Resize', img_scale=(511, 511), keep_ratio=False),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
]
test_pipeline = [
    dict(type='LoadImageFromFile', to_float32=True),
    dict(
        type='MultiScaleFlipAug',
        scale_factor=1.0,
        flip=True,
        transforms=[
            dict(type='Resize'),
            dict(
                type='RandomCenterCropPad',
                crop_size=None,
                ratios=None,
                border=None,
                test_mode=True,
                test_pad_mode=['logical_or', 127],
                **img_norm_cfg),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='ImageToTensor', keys=['img']),
            dict(
                type='Collect',
                keys=['img'],
                meta_keys=('filename', 'ori_shape', 'img_shape', 'pad_shape',
                           'scale_factor', 'flip', 'img_norm_cfg', 'border')),
        ])
]


dataset_type = 'CocoDataset'

# path to coco annotations in json file
ann_file_train = main_config.coco_train
ann_file_test = main_config.coco_eval
ann_file_val = main_config.coco_val
# path to images
image_folder = main_config.images_path
data_root = main_config.images_path
# Use RepeatDataset to speed up training

data = dict(
    samples_per_gpu=3,
    workers_per_gpu=3,
    train=dict(pipeline=train_pipeline,
                type=dataset_type,
                ann_file=ann_file_train,
                img_prefix=image_folder,),
    val=dict(pipeline=test_pipeline,
                type=dataset_type,
                ann_file=ann_file_val,
                img_prefix=image_folder,),
    test=dict(pipeline=test_pipeline,
                type=dataset_type,
                ann_file=ann_file_test,
                img_prefix=image_folder,))
# optimizer
optimizer = dict(type='Adam', lr=0.0005)
optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))
# learning policy
lr_config = dict(
    policy='step',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=1.0 / 3,
    step=[180])
runner = dict(type='EpochBasedRunner', max_epochs=210)

# NOTE: `auto_scale_lr` is for automatically scaling LR,
# USER SHOULD NOT CHANGE ITS VALUES.
# base_batch_size = (32 GPUs) x (3 samples per GPU)
auto_scale_lr = dict(base_batch_size=96)
load_from = main_config.pretrained_model_path
