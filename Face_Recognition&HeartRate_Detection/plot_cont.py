import matplotlib
import datetime
import pymysql
import matplotlib
import time

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from utils import *
from scipy.signal import decimate

heartrate = np.zeros(60, int)
num: int = 0
hr_sum: int = 0
plt.ion()


class DynamicPlot():
    def __init__(self, signal_size, bs):
        self.batch_size = bs
        self.signal_size = signal_size
        self.launched = False

    def launch_fig(self):
        self.fig, (self.pulse_ax, self.hr_axis) = plt.subplots(2, 1)

        self.pulse_to_plot = np.zeros(self.signal_size)
        self.hrs_to_plot = np.zeros(self.signal_size)

        self.hr_texts = self.pulse_ax.text(0.1, 0.9, '0', ha='center', va='center', transform=self.pulse_ax.transAxes)
        self.pulse_ax.set_title('BVP')
        self.hr_axis.set_title('Heart Rate')
        self.pulse_ax.set_autoscaley_on(True)

        self.pulse_ax.plot(self.pulse_to_plot)
        self.hr_axis.plot(self.hrs_to_plot)

        self.pulse_ax.set_ylim(-3, 3)
        self.hr_axis.set_ylim(0, 180)
        self.launched = True

        plt.tight_layout()
        plt.show()

    def __call__(self, pipe):
        if self.launched == False: self.launch_fig()
        self.pipe = pipe
        self.call_back()

    def call_back(self):
        while True:
            data = self.pipe.recv()
            if data is None:
                self.terminate()
                break
            elif data == 'no face detected':
                self.update_no_face()
            else:
                self.update_data(data[0], data[1])

    def update_no_face(self):
        hr_text = 'HR: NaN'
        self.hr_texts.set_text(hr_text)
        scaled = np.zeros(10)
        for i in range(0, len(scaled)):
            self.pulse_to_plot[0:self.signal_size - 1] = self.pulse_to_plot[1:]
            self.pulse_to_plot[-1] = scaled[i]
            self.update_plot(self.pulse_ax, self.pulse_to_plot)

            self.hrs_to_plot[0:self.signal_size - 1] = self.hrs_to_plot[1:]
            self.hrs_to_plot[-1] = 0
            self.update_plot(self.hr_axis, self.hrs_to_plot)
            self.re_draw()

    # Get HR & Send to mysql
    def update_data(self, p, hrs):
        global heartrate
        global hr_sum
        global num
        ele = 0
        hr_fft = moving_avg(hrs, 3)[-1] if len(hrs) > 5 else hrs[-1]
        hr_text = 'HR: ' + str(int(hr_fft))
        # current = datetime.datetime.today()
        # if current.hour >= 8:  # & now.minute % 10 == 9:
        if num < 10:
            heartrate[num] = str(int(hr_fft))
            num = num + 1
            print("yes" + str(num))
        if num == 10:
            for ele in range(0, len(heartrate)):
                hr_sum = hr_sum + heartrate[ele]
            result = int(hr_sum / 10)
            userID = open('name.txt').read()
            heartRateStr = str(result)
            day = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            sql = "insert into heartRate values('" + userID + "'," + heartRateStr + ",'" + day + "')"
            # 连接数据库
            conn = pymysql.connect(
                host="139.9.142.29",
                port=3306,  # 端口号
                user="allQualified",  # 数据库用户
                password="1q2w3e4r",  # 数据库密码
                database="heartRateDB"  # 要连接的数据库名称
            )
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()  # 提交请求，不然不会插入数据
            conn.close()
            num = 0
            hr_sum = 0
        self.hr_texts.set_text(hr_text)
        batch = p[-self.batch_size:]
        decimated_p = decimate(batch, 3)
        scaled = scale_pulse(decimated_p)
        for i in range(0, len(scaled)):
            self.pulse_to_plot[0:self.signal_size - 1] = self.pulse_to_plot[1:]
            self.pulse_to_plot[-1] = scaled[i]
            self.update_plot(self.pulse_ax, self.pulse_to_plot)
            self.hrs_to_plot[0:self.signal_size - 1] = self.hrs_to_plot[1:]
            self.hrs_to_plot[-1] = hr_fft
            self.update_plot(self.hr_axis, self.hrs_to_plot)
            self.re_draw()

    def update_plot(self, axis, y_values):
        line = axis.lines[0]
        line.set_xdata(np.arange(len(y_values)))
        line.set_ydata(y_values)
        axis.relim()
        axis.autoscale_view()

    def re_draw(self):
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def terminate(self):
        """
        saves numpy array of rPPG signal as pulse
        """
        np.save('pulse', self.pulse_to_plot)
        plt.close('all')
