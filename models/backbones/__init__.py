from .resnet import resnet50, resnet101
from .xception import AlignedXception
from .mobilenetv2 import MobileNetV2
from .mobilenetv3 import MobileNetV3_Small


def build_backbone(backbone, output_stride, BatchNorm):
    if backbone == 'resnet50':
        return resnet50(output_stride, BatchNorm)

    elif backbone == 'resnet101':
        return resnet101(output_stride, BatchNorm)

    elif backbone == 'xception':
        return AlignedXception(output_stride, BatchNorm)

    elif backbone == 'mobilenetv2':
        return MobileNetV2(output_stride, BatchNorm)

    elif backbone == 'mobilenetv3':
        return MobileNetV3_Small()

    else:
        raise NotImplementedError
