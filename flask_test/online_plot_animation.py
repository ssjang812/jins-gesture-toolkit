# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 23:44:15 2020

@author: JY
"""

import sys
sys.path.append("../libs")
from sensorUDP import imus_UDP
import JinsSocket
import queue

import time
from matplotlib import pyplot as plt
import numpy as np
from pynput import keyboard
import pandas as pd
from threading import Thread

current_milli_time = lambda: int(round(time.time() * 1000))


jins_client = JinsSocket.JinsSocket(isUDP=True, Port=12562, w_size=100*60*5)
jins_client.setConnection()
jins_client.start()
jins_data_q = queue.Queue(maxsize=10)


# TARGET_IMU_IP = ['192.168.0.12']
TARGET_IMU_IP = ['192.168.0.186']

imu_get = imus_UDP(Port=12563)
imu_get.setConnection()
imu_get.start()
imu_data_q = queue.Queue(maxsize=10)
#%%

STOP_LOOP = False

a_pressed = False
def on_press(key):
    global STOP_LOOP, a_pressed, pressed_df, jins_client, imu_get
    try:
        if key.char == 'a' and not a_pressed:
            a_pressed = True
            
            pressed_df.loc[len(pressed_df)] = [key.char, 'pressed',
                                               jins_client.getLast_dict_one()['TIME'],
                                               imu_get.getDATA(1)[TARGET_IMU_IP][-1,11]]
        
        # print('alphanumeric key {0} pressed'.format(key.char))
    except AttributeError:
        _tmp = 1
        # print('special key {0} pressed'.format(key))

def on_release(key):
    global STOP_LOOP, a_pressed, pressed_df, anim
    # print('{0} released'.format(
    #     key))
    
    try:
        if key.char == 'a' and a_pressed:
            a_pressed = False
            pressed_df.loc[len(pressed_df)] = [key.char, 'released',
                                               jins_client.getLast_dict_one()['TIME'],
                                               imu_get.getDATA(1)[TARGET_IMU_IP][-1,11]]
        elif key.char == '1':
            print("run device sync")
    except AttributeError:
        if key == keyboard.Key.esc:
            STOP_LOOP = True
            terminate_all()
            
            
            # Stop listener
            return False

    
    
pressed_df = pd.DataFrame(columns=['key', 'event', 'jins_time', 'imu_time'])

# ...or, in a non-blocking fashion:
listener = keyboard.Listener(on_press=on_press,
                             on_release=on_release)
listener.start()


PRESS_NUM = 200
pressed_log = np.zeros(PRESS_NUM)
def press_counter(threadname):
    global STOP_LOOP, a_pressed, pressed_log
    
    while True:
        if STOP_LOOP:
            break
        
        pressed_log = np.roll(pressed_log, -1)
        if a_pressed:
            pressed_log[-1] = 1
        else:
            pressed_log[-1] = 0
        time.sleep(0.02)
thread1 = Thread( target=press_counter, args=("Thread-1", ) )
thread1.start()
#%%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


ROW, COL = 5, 2+len(TARGET_IMU_IP)
fig, axes = plt.subplots(ROW,COL, figsize=(15,10))

if COL==1:
    axes = axes.reshape(5, 1)
    
def terminate_all():
    global ani, jins_client, imu_get
    try:
        ani.event_source.stop()
    except:
        print("cannot detect 'anim'")    
    
    jins_client.close()
    imu_get.close()
    # plt.close()

# basic Jins

JINS_NUM = 400
JINS_X = np.arange(JINS_NUM)
default_val = np.zeros(JINS_NUM)

jins_lines = dict()
for key in ["EOG_L","EOG_R","EOG_H","EOG_V"]:
    line, = axes[0,0].plot(default_val, lw=3, label=key)
    jins_lines[key] = ((0,0), line)
axes[0,0].set_xlim(0,JINS_NUM)
axes[0,0].set_ylim([-2000,2000])
axes[0,0].set_title("Jins EOG")
axes[0,0].legend(loc=2)
    
for key in ["GYRO_X","GYRO_Y","GYRO_Z"]:
    line, = axes[1,0].plot(default_val, lw=3, label=key)
    jins_lines[key] = ((1,0), line)
axes[1,0].set_xlim(0,JINS_NUM)
axes[1,0].set_ylim([-36000,36000])
axes[1,0].set_title("Jins Gyro")
axes[1,0].legend(loc=2)   

for key in ["ACC_X","ACC_Y","ACC_Z"]:
    line, = axes[2,0].plot(default_val, lw=3, label=key)
    jins_lines[key] = ((2,0), line)
axes[2,0].set_xlim(0,JINS_NUM)
axes[2,0].set_ylim([-36000,36000])
axes[2,0].set_title("Jins ACC")
axes[2,0].legend(loc=2)


# basic IMU

IMU_NUM = 200
IMU_X = np.arange(IMU_NUM)


imu_lines_all = {}
for i_, ip in enumerate(TARGET_IMU_IP):
    imu_lines = dict()
    
    COL_NUM = i_+1
    
    target_ax = (0,COL_NUM)
    default_val = np.zeros(IMU_NUM)
    line, = axes[target_ax].plot(default_val, lw=3, label="MagX")
    imu_lines['MagX'] = (target_ax,line)
    line, = axes[target_ax].plot(default_val, lw=3, label="MagY")
    imu_lines['MagY'] = (target_ax,line)
    line, = axes[target_ax].plot(default_val, lw=3, label="MagZ")
    imu_lines['MagZ'] = (target_ax,line)
    axes[target_ax].set_xlim(0,IMU_NUM)
    axes[target_ax].set_ylim([-5000,5000])
    axes[target_ax].set_title("{}|Watch MAG".format(ip))
    axes[target_ax].legend(loc=2)
    
    target_ax = (1,COL_NUM)
    line, = axes[target_ax].plot(default_val, lw=3, label="Gx")
    imu_lines['Gx'] = (target_ax,line)
    line, = axes[target_ax].plot(default_val, lw=3, label="Gy")
    imu_lines['Gy'] = (target_ax,line)
    line, = axes[target_ax].plot(default_val, lw=3, label="Gz")
    imu_lines['Gz'] = (target_ax,line)
    axes[target_ax].set_xlim(0,IMU_NUM)
    axes[target_ax].set_ylim([-20,20])
    axes[target_ax].set_title("{}|Watch Gyro".format(ip))
    axes[target_ax].legend(loc=2)
    
    target_ax = (2,COL_NUM)
    line, = axes[target_ax].plot(default_val, lw=3, label="Ax")
    imu_lines['Ax'] = (target_ax,line)
    line, = axes[target_ax].plot(default_val, lw=3, label="Ay")
    imu_lines['Ay'] = (target_ax,line)
    line, = axes[target_ax].plot(default_val, lw=3, label="Az")
    imu_lines['Az'] = (target_ax,line)
    axes[target_ax].set_xlim(0,IMU_NUM)
    axes[target_ax].set_ylim([-20,20])
    axes[target_ax].set_title("{}|Watch ACC".format(ip))
    axes[target_ax].legend(loc=2)
    
    target_ax = (3,COL_NUM)
    line, = axes[target_ax].plot(np.zeros(IMU_NUM-1), lw=3, label="MagSUM")
    imu_lines['MagSUM'] = (target_ax,line)
    axes[target_ax].set_xlim(0,IMU_NUM)
    axes[target_ax].set_ylim([-1,1500])
    axes[target_ax].set_title("{}|Watch MAG SUM".format(ip))
    axes[target_ax].legend(loc=2)
    
    imu_lines_all[ip] = (imu_lines)

# Additional info
pressed_line, = axes[4,0].plot(pressed_log, lw=3, label="pressed")
axes[4,0].set_xlim(0,IMU_NUM)
axes[4,0].set_ylim([0,1.2])
axes[4,0].set_title("Pressed")
axes[4,0].legend(loc=2)


text = axes[4,0].text(0.8,0.5, "")


cur_time = 0
def update(frame, *factor):
    global cur_time
    jins_client, imu_get = factor[0], factor[1]
    
    new_time = current_milli_time()
    TEXT = "dt:{:03}ms |a_pressed: {}\n".format(new_time-cur_time,a_pressed)
    
    
    try:
    # jins_data = jins_client.getLast_dict(JINS_NUM)
        jins_client.getLast_dict(JINS_NUM, q=jins_data_q)
        jins_data = jins_data_q.get()
        jins_data_q.task_done()
    
        for key, val in jins_lines.items():
            val[1].set_data(JINS_X, jins_data[key])
    except:
        TEXT += "Error on Jins\n"
    
    
    imu_get.getDATA(IMU_NUM, imu_data_q)
    imu_data_all_dict = imu_data_q.get()
    imu_data_q.task_done()
    
    artists = []
    for ip in TARGET_IMU_IP:
        if not ip in imu_data_all_dict.keys():
            TEXT += "Error on {}\n".format(ip)
            continue
        
        imu_data_1 = imu_data_all_dict[ip]
        imu_lines_all[ip]['MagX'][1].set_data(IMU_X, imu_data_1[:,13])
        imu_lines_all[ip]['MagY'][1].set_data(IMU_X, imu_data_1[:,14])
        imu_lines_all[ip]['MagZ'][1].set_data(IMU_X, imu_data_1[:,15])
        imu_lines_all[ip]['Gx'][1].set_data(IMU_X, imu_data_1[:,1])
        imu_lines_all[ip]['Gy'][1].set_data(IMU_X, imu_data_1[:,2])
        imu_lines_all[ip]['Gz'][1].set_data(IMU_X, imu_data_1[:,3])
        imu_lines_all[ip]['Ax'][1].set_data(IMU_X, imu_data_1[:,4])
        imu_lines_all[ip]['Ay'][1].set_data(IMU_X, imu_data_1[:,5])
        imu_lines_all[ip]['Az'][1].set_data(IMU_X, imu_data_1[:,6])
        
        sum_ = np.abs(np.diff(imu_data_1[:,13:16], axis=0)).sum(axis=1)
    
        imu_lines_all[ip]['MagSUM'][1].set_data(IMU_X[:-1], sum_)
        
        artists += [one_[1] for one_ in imu_lines_all[ip].values()]
    
    
    pressed_line.set_data(IMU_X, pressed_log)
    text.set_text(TEXT)
    cur_time = new_time
    
    
    artists += [one_[1] for one_ in jins_lines.values()] +\
                [text, pressed_line]
    return tuple(artists)

ani = FuncAnimation(fig, update, frames=np.linspace(0, 2*np.pi, 128),
                    fargs=(jins_client, imu_get),
                    interval=10,
                    blit=True)
plt.tight_layout()
plt.show(block=False)