import glob
import random

import torchvision.datasets as dset


class ImageFolderDataset(dset.ImageFolder):
    """ Custom Dataset compatible with torch.utils.data.DataLoader. """

    def __init__(self, root, transform=None,
                 loader=dset.folder.default_loader):
        """
        Args:
            root: image directory.
            transform: image transformer
        """
        self.root = root
        self.imgs = find_images(root)
        self.transform = transform
        self.loader = loader

    def load(self, path):
        ''' Apply transformations
            - Scale up
            - Perform transforms defined in `main()`
            - Normalization on images from [0, 1] -> [-1, 1]
            - Random croping to desired size
        '''
        img = self.loader(path)
        img = resize(img, (286 * 2, 286))

        if self.transform is not None:
            img = self.transform(img)
        img = normalize(img)

        a, b = split_ab(img)

        a = random_crop(a, (256, 256))
        b = random_crop(b, (256, 256))

        return a, b

    def __getitem__(self, index):
        """ Returns an image pair. """
        return self.load(self.imgs[index])


class ImageMixFolderDatasets(dset.ImageFolder):
    """ Custom Mix Datasets compatible with torch.utils.data.DataLoader. """

    def __init__(self, dataset_a, dataset_b, transform=None,
                 loader=dset.folder.default_loader):
        """
        Args:
            dataset_a: image_A dataset directory.
            dataset_b: image_B dataset directory.
            transform: image transformer
        """
        self.dataset_a = dataset_a
        self.dataset_b = dataset_b
        self.img_as = find_images(dataset_a)
        self.img_bs = find_images(dataset_b)
        self.transform = transform
        self.loader = loader

        assert len(self.img_as) == len(self.img_bs)
        print('Found A and B pairs:', len(self.img_as))

    def load(self, path):
        img = self.loader(path)
        img = resize(img, (286, 286))
        if self.transform is not None:
            img = self.transform(img)
        img = normalize(img)
        img = random_crop(img, (256, 256))

        return img

    def __getitem__(self, index):
        """ Returns an image pair. """
        a = self.load(self.img_as[index])
        b = self.load(self.img_bs[index])
        return a, b

    def __len__(self):
        return len(self.img_as)


def resize(img, shape):
    return img.resize(shape)


def normalize(img):
    return img * 2 - 1


def split_ab(img):
    _, _, w = img.size()
    return img[:, :, :w // 2], img[:, :, w // 2:]


def random_crop(img, shape):
    _, h, w = img.size()
    th, tw = shape
    x1 = random.randint(0, w - tw)
    y1 = random.randint(0, h - th)
    return img[:, x1:x1 + tw, y1:y1 + th]


def find_images(folder):
    return [g for g in glob.glob(folder + '/*.*')
            if dset.folder.is_image_file(g)]
