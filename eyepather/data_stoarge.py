import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import gaussian_kde
from sklearn.decomposition import PCA
from threading import Thread
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
import re
import os

from pathlib import Path
from PIL import Image

class DirectoryManager:

    def __init__(self, path, dirname):
        self.path = path
        self.dirname = dirname
        self.directories = {}
        self.directory_counter = 0
        self.max_size = 150
        Path(f"./{self.path}").mkdir(parents=True, exist_ok=True)

    def save(self, save, filename):
        if(not self.directories):
            self.directories[len(self.directories)] =  Directory(self.path,f"{self.dirname}_{self.directory_counter}")
            self.directory_counter+=1

        if self.directories[len(self.directories) - 1].getSize() > self.max_size:
            self.directories[len(self.directories)] = Directory(self.path,f"{self.dirname}_{self.directory_counter}")
            self.directory_counter+=1

        self.directories[len(self.directories) - 1].save(save,filename)

    def getDirs(self):
        return self.directories

class Directory:

    def __init__(self, path, dirname):
        self.files_list = []
        self.path = path
        self.dirname = dirname
        self.directory_raw = f"{path}/{dirname}"
        Path(f"./{self.directory_raw}").mkdir(parents=True, exist_ok=True)

    def save(self,save,filename):
        self.files_list.append(filename)
        save(f"{self.directory_raw}/{filename}")

    def getPath(self):
        return self.directory_raw

    def getFiles(self):
        return self.files_list

    def getSize(self):
        return len(self.files_list)

class Storage:

    def __init__(self):
        timestamp = datetime.datetime.now().timestamp()
        self.directory = f"data_{timestamp}"
        self.dirs = DirectoryManager(self.directory,"raw")

        self.headers = ["unix_timestamp","point_x", "point_y"]
        self.data=[]

        self.spf = 10 # seconds per frame
        self.time_start = time.time()
        self.dirs.save(
                pyautogui.screenshot().save,
                f"{int(timestamp)}.png"
            )
        self.first_timestamp = timestamp
        self.last_heatmapped_timestamp = self.first_timestamp
        self.last_timestamp = self.first_timestamp

    def append(self,x,y):
        timestamp = datetime.datetime.now().timestamp()
        self.last_timestamp = timestamp
        self.data.append([timestamp,x,y])

        if self.spf < time.time() - self.time_start:
            self.time_start = time.time()
            self.dirs.save(
                pyautogui.screenshot().save,
                f"{int(timestamp)}.png"
            )

            # TODO: this will have to be changed into nicer code
            dirsList = self.dirs.getDirs()

            Thread(target=self.make_heatmap,args=(self.data,
                self.last_heatmapped_timestamp,
                self.last_timestamp,
                dirsList[len(dirsList) - 1].getPath(),
                f"{dirsList[len(dirsList) - 1].getPath()}_heatmaps",
                dirsList[len(dirsList) - 1])).start()

            self.last_heatmapped_timestamp = self.last_timestamp

    def post_process(self):

        filename = f"./{self.directory}/data.csv"
        Path(self.directory).mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.headers)
            writer.writerows(self.data)

        # TODO: this will have to be changed into nicer code
        dirsList = self.dirs.getDirs()
        Thread(target=self.make_heatmap,args=(self.data,
            self.last_heatmapped_timestamp,
            self.last_timestamp,
            dirsList[len(dirsList) - 1].getPath(),
            f"{dirsList[len(dirsList) - 1].getPath()}_heatmaps",
            dirsList[len(dirsList) - 1])).start()


    def make_heatmap(self,data,start_timestamp,end_timestamp,directory,save_to_dir,files):

        files = files.getFiles()
        files_timestamps = []
        for filenames in files:
            # Convert the extracted string to an integer
            files_timestamps.append(int(filenames.split('.')[0]))


        save_to_dir_png = f"{save_to_dir}_{int(start_timestamp)}_{int(end_timestamp)}"
        Path(save_to_dir).mkdir(parents=True, exist_ok=True)
        Path(save_to_dir_png).mkdir(parents=True, exist_ok=True)
        prev_timestamp = start_timestamp
        batch_size = 30
        np_data = np.array(data)
        number = 0

        cv_images = []

        start_index =  np.argmin(np.abs(np_data[:,0] - start_timestamp))
        end_index =  np.argmin(np.abs(np_data[:,0] - end_timestamp))
        for i in range(start_index, end_index, batch_size):

            data_batch = np_data[i:i+batch_size*2]

            if((data_batch[0][0]) > prev_timestamp + 30):
                new_timestamp_index = np.argmin(np.abs(np.array(files_timestamps) - int(prev_timestamp + 30)))
                if os.path.isfile(f"{directory}/{int(new_timestamp_index)}.png"):
                    prev_timestamp = new_timestamp_index

            if not os.path.isfile(f"{directory}/{int(prev_timestamp)}.png"):
                new_timestamp_index = np.argmin(np.abs(np.array(files_timestamps) - int(prev_timestamp)))
                if os.path.isfile(f"{directory}/{int(new_timestamp_index)}.png"):
                    prev_timestamp = new_timestamp_index

            map_image = plt.imread(f"{directory}/{int(prev_timestamp)}.png")
            height, width, _ = map_image.shape


            x = np.array(data_batch[:,1])
            y = np.array(data_batch[:,2])
            y = np.array([height - y_i for y_i in y])

            # Define grid for the heatmap
            xmin, xmax = 0, width
            ymin, ymax = 0, height

            # Calculate pairwise distances between points
            data = np.column_stack((x, y))
            distances = np.sqrt(np.sum((data[:, np.newaxis, :] - data[np.newaxis, :, :]) ** 2, axis=-1))
            # Calculate density based on inverse of distances (adjust scale factor as needed)
            density = 1 / (distances.sum(axis=1) + 1e-6)  # Adding small value to avoid division by zero

            plt.figure(figsize=(8, 6))
            plt.imshow(map_image,  extent=[xmin, xmax, ymin, ymax])  # Display the screenshot as the background
            plt.axis('off')

            # get colormap
            ncolors = 256
            color_array = plt.get_cmap('hot')(range(ncolors))

            # change alpha values
            color_array[:,-1] = np.linspace(1.0,0.0,ncolors)

            # create a colormap object
            map_object = LinearSegmentedColormap.from_list(name='hot',colors=color_array)

            # filter scatter data before plotting
            mask = (x >= xmin) & (x <= xmax) & (y >= ymin) & (y <= ymax)
            x_filtered = x[mask]
            y_filtered = y[mask]
            density_filtered = density[mask]
            plt.scatter(x_filtered, y_filtered, c=density_filtered, s=50, alpha=0.2, cmap=map_object)
            plt.axis('off')
            # Save the combined image with heatmap overlay
            temp_filename=f"{save_to_dir_png}/heatmap_{start_timestamp}_{end_timestamp}_{start_index}_{end_index}_{number}.png"
            plt.savefig(temp_filename, bbox_inches='tight')

            # opencv processing
            img = cv2.imread(temp_filename)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cv_images.append(img)
            number+=1

        # Adjust delay and loop count as desired
        fps = 10  # milliseconds
        imageio.mimsave(f'{save_to_dir}/heatmap_animation_{start_timestamp}_{end_timestamp}.gif', cv_images, fps=fps)