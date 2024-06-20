import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import gaussian_kde
import numpy as np
import pyautogui
import datetime
import imageio
import pickle
import queue
import glob
import time
import csv
import cv2
import os

from pathlib import Path
from PIL import Image

class Storage:

    def __init__(self):
        timestamp = datetime.datetime.now().timestamp()
        self.directory = f"data_{timestamp}"
        self.directory_raw = f"{self.directory}/raw"
        Path(f"./{self.directory}").mkdir(parents=True, exist_ok=True)
        Path(f"./{self.directory_raw}").mkdir(parents=True, exist_ok=True)

        self.headers = ["unix_timestamp","point_x", "point_y"]
        self.data=[]

        self.spf = 30 # seconds per frame
        self.time_start = time.time()
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.directory_raw}/{int(timestamp)}.png")
        self.first_timestamp = timestamp

    def append(self,x,y):
        timestamp = datetime.datetime.now().timestamp()
        self.data.append([timestamp,x,y])

        if self.spf < time.time() - self.time_start:
            self.time_start = time.time()
            screenshot = pyautogui.screenshot()
            screenshot.save(f"{self.directory_raw}/{int(timestamp)}.png")

    def post_process(self):

        filename = f"./{self.directory}/data.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.headers)
            writer.writerows(self.data)

        self.make_gifs()

    def make_gifs(self):

        prev_timestamp = self.first_timestamp
        batch_size = 30
        np_data = np.array(self.data)
        number = 0
        for i in range(0, len(np_data), batch_size):
            data_batch = np_data[i:i+batch_size]

            if((data_batch[0][0]) > prev_timestamp + 30):
                if os.path.isfile(f"{self.directory_raw}/{int(prev_timestamp+30)}.png"):
                    prev_timestamp += 30

            map_image = plt.imread(f"{self.directory_raw}/{int(prev_timestamp)}.png")
            height, width, _ = map_image.shape

            plt.figure(figsize=(8, 6))
            plt.imshow(map_image)  # Display the screenshot as the background
            plt.axis('off')

            x_range = [0, width]
            y_range = [0,height]
            heatmap, xedges, yedges = np.histogram2d(data_batch[:,1], data_batch[:,2], bins = 30, range=[x_range, y_range])
            extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]
            alpha = 0.5

            # get colormap
            ncolors = 256
            color_array = plt.get_cmap('hot')(range(ncolors))

            # change alpha values
            color_array[:,-1] = np.linspace(1.0,0.0,ncolors)

            # create a colormap object
            map_object = LinearSegmentedColormap.from_list(name='hot',colors=color_array)


            plt.imshow(heatmap.T, extent=extent, origin='lower', alpha=alpha, cmap=map_object)
            plt.axis('off')
            # Save the combined image with heatmap overlay
            plt.savefig(f"{self.directory_raw}/heatmap_{number}_{int(prev_timestamp)}.png", bbox_inches='tight')
            number+=1

        images = []
        for filename in glob.glob(f"{self.directory_raw}/heatmap_*.png"):
            img = cv2.imread(filename)
            images.append(img)

        # Adjust delay and loop count as desired
        fps = 10  # milliseconds
        imageio.mimsave(f'{self.directory_raw}/heatmap_animation.gif', images, fps=fps)
        print("GIF created successfully!")