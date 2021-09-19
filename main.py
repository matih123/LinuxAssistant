from utils import Ssh, Website

from kivy.app import App
from kivy.uix.button import Button
from kivy.utils import platform
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import *
from kivy.clock import Clock
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.icon_definitions import md_icons

from matplotlib import pyplot as plt
import configparser
import os

class MainApp(MDApp):

        def update(self, x):
                self.ssh.exec('cpu')
                self.cpu = round(float(self.ssh.get()[0]), 2)
                self.info_values['cpu'].text = f'{self.cpu}%'

                self.ssh.exec('ram_%')
                ram = self.ssh.get()[0]
                self.ram = int(float(ram))
                self.info_values['ram_%'].text = f'{self.dictionary("usage")}: {str(ram)}%'
                self.ssh.exec('ram_total')
                self.info_values['ram_total'].text = f'{self.dictionary("total")}: {str(self.ssh.get()[0])} GB'

                uptime = self.ssh.format_uptime()
                self.info_values['uptime'].text = f'{self.dictionary("days")}: {uptime[0]}\n{self.dictionary("hours")}: {uptime[1]}\n{self.dictionary("minutes")}: {uptime[2]}'

                self.ssh.exec('disk_name')
                self.info_titles['disk'].text = f'{self.dictionary("DISK")} {str(self.ssh.get()[0])}'
                self.ssh.exec('disk_%')
                disk = self.ssh.get()[0]
                self.disk = int(float(disk))
                self.info_values['disk_%'].text = f'{self.dictionary("usage")}: {str(disk)}%'
                self.ssh.exec('disk_total')
                self.info_values['disk_total'].text = f'{self.dictionary("total")}: {str(self.ssh.get()[0])} GB'

                network = self.ssh.calculate_bandwidth()
                self.info_values['network_usage'].text = f'[b]{self.dictionary("received")}:[/b] [size=18dp]{network[0]}[/size]\n[b]{self.dictionary("transmited")}:[/b] [size=18dp]{network[1]}[/size]'

                self.info_progress_bars['ram'].size_hint[0] = self.ram/100
                self.info_progress_bars['disk'].size_hint[0] = self.disk/100
                
                # SCREENSHOT MODULE
                if self.modules['screenshot']: self.main_layout.export_to_png(self.screenshot)

                self.update_plot()
                if self.first_run: self.first_run = False

        def update_plot(self):
                if self.first_run: plt.style.use('bmh')

                self.time += self.refresh_rate
                self.data_x.append(self.time)
                self.data_cpu_y.append(self.cpu)
                self.data_ram_y.append(self.ram)
                self.data_disk_y.append(self.disk)
                plt.plot(self.data_x, self.data_disk_y, '#0492C2', label="disk", linewidth=self.linewidth)
                plt.plot(self.data_x, self.data_ram_y, "-b", label="ram", linewidth=self.linewidth)
                plt.plot(self.data_x, self.data_cpu_y, "-r", label="cpu", linewidth=self.linewidth)

                if self.first_run:
                        plt.rcParams.update({'font.size': self.font_size})
                        plt.legend(loc='upper left')
                        plt.title(f'{self.dictionary("Usage [%] / Time [s]")}')

                try: self.graph_layout.remove_widget(self.graph)
                except: pass
                self.graph = FigureCanvasKivyAgg(plt.gcf())
                self.graph_layout.add_widget(self.graph)

        def update_raspberry(self, x):
                data = self.ssh.format_sensor()

                self.info_values['temperature'].text = f'{data[0]} C'
                self.info_values['pressure'].text = f'{int(float(data[1]))} hPa'
                self.info_values['humidity'].text = f'{round(float(data[2]), 2)}%'

        def hide(self):
                Clock.unschedule(self.update)
                Clock.unschedule(self.update_raspberry)
                try:
                        self.main_layout.remove_widget(self.home_layout)
                        self.main_layout.remove_widget(self.rpi_layout)
                except: pass

        def show_websites(self):
                #self.hide()
                print('websites')

        def show_raspberry(self):
                if not self.modules['raspberry']: return False

                self.hide()
                if self.first_rpi:
                        self.rpi_layout = GridLayout(size_hint=(1, 1))
                        self.info['temperature'] = InfoBox()
                        self.info['pressure'] = InfoBox()
                        self.info['humidity'] = InfoBox()
                        self.info['distance'] = InfoBox()

                        self.info['temperature'].canvas.clear()
                        self.info['pressure'].canvas.clear()
                        self.info['humidity'].canvas.clear()
                        self.info['distance'].canvas.clear()

                        self.info_titles['temperature'] = InfoLabel(text=f'{self.dictionary("TEMPERATURE")}', size_hint=(1, .4))
                        self.info_titles['pressure'] = InfoLabel(text=f'{self.dictionary("PRESSURE")}', size_hint=(1, .4))
                        self.info_titles['humidity'] = InfoLabel(text=f'{self.dictionary("HUMIDITY")}', size_hint=(1, .4))
                        self.info_titles['distance'] = InfoLabel(text=f'{self.dictionary("DISTANCE")}', size_hint=(1, .4))

                        self.info_values['temperature'] = InfoLabel(font_style='H5', size_hint=(1, .5))
                        self.info_values['pressure'] = InfoLabel(font_style='H5', size_hint=(1, .5))
                        self.info_values['humidity'] = InfoLabel(font_style='H5', size_hint=(1, .5))
                        self.info_values['distance'] = InfoLabel(font_style='H5', size_hint=(1, .5))

                        self.info['temperature'].add_widget(self.info_titles['temperature'])
                        self.info['temperature'].add_widget(self.info_values['temperature'])
                        self.info['temperature'].add_widget(Label(size_hint=(1, .25)))
                        self.info['pressure'].add_widget(self.info_titles['pressure'])
                        self.info['pressure'].add_widget(self.info_values['pressure'])
                        self.info['pressure'].add_widget(Label(size_hint=(1, .25)))
                        self.info['humidity'].add_widget(self.info_titles['humidity'])
                        self.info['humidity'].add_widget(self.info_values['humidity'])
                        self.info['humidity'].add_widget(Label(size_hint=(1, .25)))
                        self.info['distance'].add_widget(self.info_titles['distance'])
                        self.info['distance'].add_widget(self.info_values['distance'])
                        self.info['distance'].add_widget(Label(size_hint=(1, .25)))

                        self.rpi_layout.add_widget(self.info['temperature'])
                        self.rpi_layout.add_widget(self.info['pressure'])
                        self.rpi_layout.add_widget(self.info['humidity'])
                        self.rpi_layout.add_widget(self.info['distance'])
                        self.rpi_layout.add_widget(Label(size_hint=(1, .56)))

                        self.first_rpi = False

                self.main_layout.add_widget(self.rpi_layout)
                Clock.schedule_interval(self.update_raspberry, self.refresh_rate)
                
        def show_home(self):
                self.hide()
                self.main_layout.add_widget(self.home_layout)
                Clock.schedule_interval(self.update, self.refresh_rate)

        def dictionary(self, lookup):
                if self.language == 'English':
                        return lookup

                elif self.language == 'Polish':
                        d = dict()
                        d['USAGE'] = 'UŻYCIE'
                        d['usage'] = 'użycie'
                        d['total'] = 'łącznie'
                        d['UPTIME'] = 'CZAS DZIAŁANIA'
                        d['DISK'] = 'DYSK'
                        d['NETWORK'] = 'SIEĆ'
                        d['received'] = 'otrzymano'
                        d['transmited'] = 'transmitowano'
                        d['days'] = 'dni'
                        d['hours'] = 'godziny'
                        d['minutes'] = 'minuty'
                        d['TEMPERATURE'] = 'TEMPERATURA'
                        d['PRESSURE'] = 'CIŚNIENIE'
                        d['HUMIDITY'] = 'WILGOTNOŚĆ'
                        d['DISTANCE'] = 'ODLEGŁOŚĆ'
                        d['Usage [%] / Time [s]'] = 'Użycie [%] / Czas [s]'
                        return d[lookup]

        def create_config(self):
                if platform == 'android':
                        self.config_path = "/storage/emulated/0/Documents/config.ini"
                else:
                        self.config_path = 'config.ini'

                if not os.path.isfile(self.config_path):
                        with open(self.config_path, 'w') as f:
                                default_config = r"""[GENERAL]
REFRESH_RATE = 6
; Available: Polish, English
LANGUAGE = Polish

[SSH]
IP = ssh.server.com
PORT = 22
USER = user
PASSWORD = Password!@123

[MODULES]
RASPBERRY = False
SCREENSHOT = False
; Work in progress
WEBSITES = False

[SCREENSHOT]
; First you need to set SCREENSHOT equal True in MODULES
PATH = /path/to/file.png

; Work in progress
[WEBSITES]
ADDRESSES = google.pl,facebook.com"""
                                f.write(default_config)

        def build(self):
                ###################
                ### LOAD CONFIG ###
                ###################
                self.create_config()
                config = configparser.ConfigParser()
                config.read(self.config_path)

                ###############
                ### GENERAL ###
                ###############
                self.ssh = Ssh(config.get('SSH', 'IP'), config.getint('SSH', 'PORT'), config.get('SSH', 'USER'), config.get('SSH', 'PASSWORD'))
                self.ram = 0
                self.disk = 0
                self.time = 0
                self.first_run = True
                self.first_rpi = True
                self.icon = 'img/icon.png'
                self.modules = dict()
                self.theme_cls.theme_style = "Dark"
                self.title = 'LinuxAssistant'
                self.refresh_rate = config.getint('GENERAL', 'REFRESH_RATE')
                self.language = config.get('GENERAL', 'LANGUAGE')
                
                if platform == 'linux':
                        Window.size = (421, 912)
                        self.font_size = 10
                        self.linewidth = 3
                else:
                        self.font_size = 19
                        self.linewidth = 6

                #########################
                ### SCREENSHOT MODULE ###
                #########################
                self.modules['screenshot'] = config.getboolean('MODULES', 'SCREENSHOT')
                if self.modules['screenshot']: self.screenshot = config.get('SCREENSHOT', 'PATH')

                ########################
                ### RASPBERRY MODULE ###
                ########################
                self.modules['raspberry'] = config.getboolean('MODULES', 'RASPBERRY')

                #######################
                ### WEBSITES MODULE ###
                #######################
                self.modules['websites'] = config.getboolean('MODULES', 'WEBSITES')
                if self.modules['websites']: self.websites = config.get('WEBSITES', 'ADDRESSES').split(',')
                
                ##################
                ### APP LAYOUT ###
                ##################
                self.main_layout = MainLayout()
                self.home_layout = BoxLayout(orientation='vertical')

                ### Title ###
                self.ssh.exec('ip')
                self.ip = str(self.ssh.get()[0])
                self.title_box = TitleBox()

                self.info = dict()
                self.info_titles = dict()
                self.info_values = dict()
                self.info_progress_bars = dict()

                ### GENERAL ###
                self.layout = GridLayout()
                self.info['cpu'] = InfoBox()
                self.info['ram'] = InfoBox()
                self.info['uptime'] = InfoBox()
                self.info['disk'] = InfoBox()

                self.info['cpu'].canvas.clear()
                self.info['uptime'].canvas.clear()

                self.info_titles['cpu'] = InfoLabel(text='CPU')
                self.info_titles['ram'] = InfoLabel(text='RAM', size_hint=(1, 1))
                self.info_titles['uptime'] = InfoLabel(text=f'{self.dictionary("UPTIME")}')
                self.info_titles['disk'] = InfoLabel(text=f'{self.dictionary("DISK")}', size_hint=(1, 1))

                self.info_values['cpu'] = InfoLabel(font_style='H5')
                self.info_values['ram_%'] = InfoLabel(size_hint=(1, .5))
                self.info_values['ram_total'] = InfoLabel(size_hint=(1, .45))
                self.info_values['uptime'] = InfoLabel(size_hint=(1, .3))
                self.info_values['disk_%'] = InfoLabel(size_hint=(1, .5))
                self.info_values['disk_total'] = InfoLabel(size_hint=(1, .45))

                self.info['cpu'].add_widget(self.info_titles['cpu'])
                self.info['cpu'].add_widget(self.info_values['cpu'])
                self.info['cpu'].add_widget(Label(size_hint=(1, .15)))
                self.info['ram'].add_widget(self.info_titles['ram'])
                self.info['ram'].add_widget(self.info_values['ram_%'])
                self.info['ram'].add_widget(self.info_values['ram_total'])
                self.info['uptime'].add_widget(self.info_titles['uptime'])
                self.info['uptime'].add_widget(self.info_values['uptime'])
                self.info['uptime'].add_widget(Label(size_hint=(1, .12)))
                self.info['disk'].add_widget(self.info_titles['disk'])
                self.info['disk'].add_widget(self.info_values['disk_%'])
                self.info['disk'].add_widget(self.info_values['disk_total'])

                self.info_progress_bars['ram'] = ProgressRectangle()
                self.info_progress_bars['disk'] = ProgressRectangle()
                self.info['ram'].add_widget(self.info_progress_bars['ram'])
                self.info['disk'].add_widget(self.info_progress_bars['disk'])

                self.layout.add_widget(self.info['cpu'])
                self.layout.add_widget(self.info['ram'])
                self.layout.add_widget(self.info['uptime'])
                self.layout.add_widget(self.info['disk'])

                ### NETWORK ###
                self.network_layout = NetworkLayout(orientation='vertical')
                self.network_layout_info = BoxLayout(orientation='horizontal', size_hint=(1, .5))

                self.info['network_usage'] = BoxLayout(size_hint=(.5, 1), orientation='vertical')
                self.info['speedtest'] = BoxLayout(size_hint=(.5, 1), orientation='vertical')

                self.info_titles['network'] = MDLabel(text=f'{self.dictionary("NETWORK")}', font_style="H6", halign="center", theme_text_color="Primary", size_hint=(1, .25))
                self.info_titles['network_usage'] = MDLabel(text=f'{self.dictionary("USAGE")}', font_style="H6", halign="center", theme_text_color="Primary")
                self.info_titles['speedtest'] = MDLabel(text='SPEEDTEST', font_style="H6", halign="center", theme_text_color="Primary")

                self.info_values['network_usage'] = InfoLabel(size_hint=(1, 1), font_style='Body2', markup=True, halign='center')

                self.info['network_usage'].add_widget(self.info_titles['network_usage'])
                self.info['network_usage'].add_widget(self.info_values['network_usage'])
                self.info['speedtest'].add_widget(self.info_titles['speedtest'])
                self.info['speedtest'].add_widget(Label(size_hint=(1, .75)))

                self.network_layout_info.add_widget(self.info['network_usage'])
                self.network_layout_info.add_widget(self.info['speedtest'])
                self.network_layout.add_widget(self.info_titles['network'])
                self.network_layout.add_widget(self.network_layout_info)
                self.network_layout.add_widget(Label(size_hint=(1, .25)))

                ### GRAPH ###
                self.graph_layout = BoxLayout(orientation='vertical', size_hint=(1, .3))
                self.data_x = []
                self.data_cpu_y = []
                self.data_ram_y = []
                self.data_disk_y = []

                ### APP END ##
                Clock.unschedule(self.update)
                Clock.schedule_interval(self.update, self.refresh_rate)

                self.main_layout.add_widget(self.title_box)
                self.main_layout.add_widget(self.home_layout)

                self.home_layout.add_widget(self.layout)
                self.home_layout.add_widget(self.network_layout)
                self.home_layout.add_widget(Label(size_hint=(1, .02)))
                self.home_layout.add_widget(self.graph_layout)
                return self.main_layout

class MainLayout(BoxLayout): pass
class NetworkLayout(BoxLayout): pass
class Title(MDLabel): pass
class InfoBox(BoxLayout): pass
class InfoLabel(MDLabel): pass
class ProgressRectangle(BoxLayout): pass
class TitleBox(BoxLayout): pass
class InfoTitle(BoxLayout): pass

if __name__ == '__main__':
        app = MainApp()
        app.run()
