import os

from data.data_loader import CreateDataLoader
from models.models import create_model
from options.test_options import TestOptions
from util import html
from util.visualizer import Visualizer
from util.metrics import PSNR
from ssim import compute_ssim
from PIL import Image

opt = TestOptions().parse()
opt.nThreads = 0  # test code only supports nThreads = 1
opt.batchSize = 1  # test code only supports batchSize = 1
opt.serial_batches = True  # no shuffle
opt.no_flip = True  # no flip

data_loader = CreateDataLoader(opt)
dataset = data_loader.load_data()
model = create_model(opt)
visualizer = Visualizer(opt)
# create website
web_dir = os.path.join(opt.results_dir, opt.name, '%s_%s' % (opt.phase, opt.which_epoch))
webpage = html.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.which_epoch))
# test
avgPSNR = 0.0
avgSSIM = 0.0
counter = 0

for i, data in enumerate(dataset):
    if i >= opt.how_many:
        break
    counter += 1
    model.set_input(data)
    model.test()
    visuals = model.get_current_visuals()
    avgPSNR += PSNR(visuals['Sharp_Train'], visuals['Restored_Train'])
    pilReal = Image.fromarray(visuals['Sharp_Train'])
    pilFake = Image.fromarray(visuals['Restored_Train'])
    avgSSIM += compute_ssim(pilReal, pilFake)
    img_path = model.get_image_paths()
    print('process image... %s' % img_path)
    visualizer.save_images(webpage, visuals, img_path)

avgPSNR /= counter
avgSSIM /= counter
print('PSNR = %f, SSIM = %f' % (avgPSNR, avgSSIM))

webpage.save()
