import os
import cv2
import fire
import h5py
import numpy as np
import os.path as osp
from tqdm import tqdm
import matplotlib.pyplot as plt

from configs.crgnet_double_float import opt
# from configs.deeplabv3_density import opt

from models import DeepLab
# from models import CSRNet
from dataloaders import deeplab_transforms as dtf
# from utils import Saver

import torch
from torchvision import transforms
import multiprocessing
multiprocessing.set_start_method('spawn', True)

show = False
results_dir = osp.join(opt.test_dir, "test_mask")
images_dir = osp.join(opt.test_dir, "images")


def test(**kwargs):
    opt._parse(kwargs)
    if not osp.exists(results_dir):
        os.makedirs(results_dir)

    # data
    imgs_name = os.listdir(images_dir)
    transform = transforms.Compose([
        dtf.FixedNoMaskResize(size=opt.input_size),  # 513
        dtf.Normalize(opt.mean, opt.std),
        dtf.ToTensor()])

    # model
    model = DeepLab(opt).to(opt.device)

    # resume
    if osp.isfile(opt.pre):
        print("=> loading checkpoint '{}'".format(opt.pre))
        checkpoint = torch.load(opt.pre)
        model.load_state_dict(checkpoint['state_dict'])
        print("=> loaded checkpoint '{}' (epoch {})"
              .format(opt.pre, checkpoint['epoch']))
    else:
        raise FileNotFoundError

    model.eval()
    with torch.no_grad():
        for ii, img_name in enumerate(tqdm(imgs_name)):
            img_path = osp.join(images_dir, img_name)
            img = cv2.imread(img_path)[:, :, ::-1]  # BGR2RGB
            sample = {"image": img, "label": None}
            sample = transform(sample)

            # predict
            region_pred, density_pred = model(sample['image'].unsqueeze(0).to(opt.device))

            region_pred = np.argmax(region_pred.cpu().numpy(), axis=1).reshape(30, 40)
            density_pred = torch.clamp(density_pred, min=0.00018).cpu().numpy().reshape(30, 40)
            pred = region_pred * density_pred * opt.norm_cfg['para']

            file_name = osp.join(
                results_dir, osp.splitext(img_name)[0] + ".hdf5")
            with h5py.File(file_name, 'w') as hf:
                hf['label'] = pred

            if show:
                plt.figure(figsize=(10, 10))
                plt.subplot(2, 1, 1).imshow(img)
                plt.subplot(2, 1, 2).imshow(pred)
                plt.show()

    # with open(os.path.join( + '.txt'), 'w') as f:
    #     temp = [osp.splitext(img_name)[0]+'\n' for img_name in imgs_name]
    #     f.writelines(temp)


if __name__ == '__main__':
    fire.Fire(test)
