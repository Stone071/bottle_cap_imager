# bottle_cap_imager

## Background

On a cross-country drive from Connecticut to Seattle, my girlfriend and I found ourselves in Crescent City, CA. We got some coffee and stopped for a walk on the beach, where we ran into an incredible mural of an ocean wave made entirely of repurposed plastic lids, bottle caps, and other similar items. I had been enjoying the trip very much, but was in need of a bit of a project to think about, and the inspiration was immediate. I wanted to write a program to do something similar -- create murals of discrete circular elements from an image.

## Overview

The goal of transforming an input image into a discrete set of circular "bottle caps" is achieved through a couple steps.

1. Simplify the coloration of the image. There may be hundreds or thousands of unique colors in an image. This should be reduced to a couple dozen or fewer for any hope of constructing this image out of bottle caps.
2. Mask off the pixels between the bottle caps, and ensure that the pixels occupying the position of the same bottle cap have the same color.

Step (1.) is handled by pix_sort.py, and step (2.) is handled by lens_mask.py. To simplify execution of the process, image_pipeline.py runs these two steps after each other.

Additionally, gif_pipeline.py creates many images from a single input with different levels of detail due to different sized bottle caps being used. These images are then composed into a single gif, which has the appearance of details fading in and out of abstract forms. In my opinion this is the most interesting output of the program.

## Dependencies

- Pillow
- numpy

### Acquiring Dependencies

`$ apt install python3-pil python3-numpy`

## Usage

### pix_sort.py

`python3 pix_sort.py` will run the program with default options and display the resultant image

### lens_mask.py

`python3 lens_mask.py` will run the program with default options and display the resultant image

### image_pipeline.py

`python3 image_pipeline.py` runs the two prior commands and saves the output in the output_images directory.

### gif_pipeline.py

`python3 gif_pipeline.py` creates an interesting gif representation of the input image using different sized bottle caps.

### Arguments

-f [filename] allows the user to select a file from the input_images directory to use.

-t [integer] allows the user to specify a threshold to use when simplifying the colors in the image.

-b [true or false] allows the user to add a preprocessing blur before the image colors are updated.

-l [integer] allows the user to select what size lens to use when making the bottlecaps.
