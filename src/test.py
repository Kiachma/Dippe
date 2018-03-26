from __future__ import unicode_literals
from autonomous_vessel import vessel
import matplotlib.patches as patches
from matplotlib import pyplot as plt
import math
import numpy as np
import config
import helpers
import sys
import os
import matplotlib
import design
import string
import fuzzy
import os, shutil
import vesselService
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
import copy
# from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

paths = []
timer = None
fis = None


def createVessel(config, fis):
    return vessel.Vessel(
        config['id'],
        config['heading'], config['position'][0], config['position'][1],
        config['speed'], config['max_speed'], config['rate_of_turn']
        , fis, config['ap'])





def cart2pol(x, y):
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return (rho, phi)


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return (x, y)


def init():
    vesselService.vessels = []
    for vesselConfig in config.vessels:
        vesselService.vessels.append(createVessel(vesselConfig, copy.deepcopy(fis)))

    # for A in vessels:
    #     for B in vessels:
    #         if A == B:
    #             continue
    #         else:
    #             A.ans.sa.add_target_vessel(
    #                 createTargetVessel(B)
    #             )


def animation_manage(ax, i):
    collissionSectors = []
    arrows = []
    ships = []

    def reset_artists():

        for arrow in arrows:
            arrow.remove()
        for sector in collissionSectors:
            sector.remove()
        for ship in ships:
            ship.remove()
        del ships[:]
        del arrows[:]
        del collissionSectors[:]

        # ani = animation.FuncAnimation(fig,
        #                               animation_manage,
        #                               init_func=init,
        #                               frames=50,
        #                               interval=500,
        #                               repeat=True)
        # ani.frame_seq = ani.new_frame_seq()

        plt.show()
        # return ani

    def animate_range(ax, vessel):
        for arrow in ax.patches:
            if plt.getp(arrow, 'gid') == vessel.id + '_circle':
                ax.patches.remove(arrow)
        patch = plt.Circle((vessel.shipstate.position.x,
                            vessel.shipstate.position.y),
                           radius=config.radius['ra'], gid=vessel.id + '_circle1', fill=False)
        ax.add_patch(patch)
        patch = plt.Circle((vessel.shipstate.position.x,
                            vessel.shipstate.position.y),
                           radius=config.radius['rb'], gid=vessel.id + '_circle2', fill=False)
        ax.add_patch(patch)
        patch = plt.Circle((vessel.shipstate.position.x,
                            vessel.shipstate.position.y),
                           radius=config.radius['rvd'], gid=vessel.id + '_circle', fill=False)

        ax.add_patch(patch)

    def animate_sector(ax, currentVessel):
        current = 0
        for i in range(10):
            next = current + config.sectors[i]
            patch = patches.Wedge((
                currentVessel.shipstate.position.x,
                currentVessel.shipstate.position.y),
                config.radius['ra'],
                helpers.nav_to_theta(currentVessel.shipstate.heading + current),
                helpers.nav_to_theta(currentVessel.shipstate.heading + next),
                ls='solid',
                linewidth=1,
                fill=False)

            collissionSectors.append(patch)
            ax.add_patch(patch)
            current = next

    def animate_arrow(ax, vessel):
        shipstate = vessel.shipstate
        # coeff = math.sqrt(
        #     math.pow(config.visibility, 2) / (
        #         math.pow(shipstate.get_headingXY()[0], 2) + math.pow(shipstate.get_headingXY()[1], 2)))
        coeff = 1000 / config.scale
        arrows.append(ax.annotate("", xy=(shipstate.position.x,
                                          shipstate.position.y),
                                  xytext=(
                                      shipstate.position.x + shipstate.get_headingXY()[0] * coeff,
                                      shipstate.position.y + shipstate.get_headingXY()[1] * coeff),
                                  arrowprops=dict(
                                      arrowstyle='<-',
                                      facecolor='blue'),
                                  gid=vessel.id,
                                  alpha=0.4))

    def animate_ship(ax, vessel):
        color = 'green'
        text_string = str(vessel.id) + "\n" + "Heading: " + str(round(vessel.shipstate.heading)) + "\n" + "Speed: " + str(round(
            vessel.shipstate.speed))

        text = ax.text(vessel.shipstate.position.x,
                       vessel.shipstate.position.y, text_string,
                       verticalalignment='bottom', horizontalalignment='center',
                       color='black')
        ships.append(text)

        patch = plt.Circle((vessel.shipstate.position.x,
                            vessel.shipstate.position.y),
                           radius=10,
                           label=vessel.id,
                           color=color)

        ships.append(patch)
        ax.add_patch(patch)

    def animate_lights(ax, currentVessel):
        patch = patches.Wedge((
            currentVessel.shipstate.position.x,
            currentVessel.shipstate.position.y),
            config.visibility,
            helpers.nav_to_theta(currentVessel.shipstate.heading),
            helpers.nav_to_theta(currentVessel.shipstate.heading - 112.5),
            color='red',
            alpha=0.4)

        collissionSectors.append(patch)
        ax.add_patch(patch)
        patch = patches.Wedge((
            currentVessel.shipstate.position.x,
            currentVessel.shipstate.position.y),
            config.visibility,
            helpers.nav_to_theta(currentVessel.shipstate.heading + 112.5),
            helpers.nav_to_theta(currentVessel.shipstate.heading),
            color='green',
            alpha=0.4)

        collissionSectors.append(patch)
        ax.add_patch(patch)

    if config.anim:
        reset_artists()

    for idx, tempvessel in enumerate(vesselService.vessels):
        tempvessel.next_position()
        if i % 1 == 0 or config.anim:
            animate_ship(ax, tempvessel)
            if config.show['arrow']:
                animate_arrow(ax, tempvessel)

            if config.show['sectors'] and idx == 0:
                animate_sector(ax, tempvessel)
            if config.show['visibility'] and idx == 0:
                animate_range(ax, tempvessel)
            # if config.show['paths'] and config.anim:
            #     animate_path(ax, tempvessel)
            # if config.show['lights'] and config.anim:
            #     animate_lights(ax, tempvessel)

    return []


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()
        self.axes.set_xlim([config.dimensions[0], config.dimensions[1]])
        self.axes.set_ylim([config.dimensions[2], config.dimensions[3]])
        self.axes.set_xlabel('NM* ' + str(1000 / config.scale))
        self.axes.set_ylabel('NM* ' + str(1000 / config.scale))
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.index = 1
        if config.anim:
            global timer
            timer = QtCore.QTimer(self)
            timer.timeout.connect(self.update_figure)
            timer.start(config.playback['interval'])

    def compute_initial_figure(self):
        animation_manage(self.axes, 0)
        self.axes.plot()

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        print(self.index)
        if config.anim:
            self.axes.cla()
            self.axes.set_xlim([config.dimensions[0], config.dimensions[1]])
            self.axes.set_ylim([config.dimensions[2], config.dimensions[3]])
        animation_manage(self.axes, self.index)
        if config.anim:
            self.draw()
        self.index = self.index + 1


class ApplicationWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.dc = MyDynamicMplCanvas(self.centralwidget, width=5, height=4, dpi=100)
        self.verticalLayout.addWidget(self.dc)

        self.btnPause.clicked.connect(self.pause)
        self.btnPlay.clicked.connect(self.play)
        self.btnReset.clicked.connect(init)
        self.btnAddVessel.clicked.connect(self.add_vessel)
        self.slider.setTickInterval(2)
        self.slider.setMinimum(-2)
        self.slider.setMaximum(10)
        self.slider.setValue(config.playback['rate'])
        self.slider.valueChanged.connect(self.set_rate)

        self.cbShowArrow.setChecked(config.show['arrow'])
        self.cbShowSector.setChecked(config.show['sectors'])
        self.cbShowVisibility.setChecked(config.show['visibility'])
        self.cbShowPath.setChecked(config.show['paths'])
        self.cbShowLights.setChecked(config.show['lights'])
        self.numVisibility.setValue(config.visibility)
        for tmpVessel in vesselService.vessels:
            self.add_vessel_to_GUI(tmpVessel)

        self.cbShowArrow.stateChanged.connect(self.toggleHeadings)
        self.cbShowSector.stateChanged.connect(self.toggleSectors)
        self.cbShowVisibility.stateChanged.connect(self.toggleVisibility)
        self.cbShowPath.stateChanged.connect(self.togglePaths)
        self.cbShowLights.stateChanged.connect(self.toggleLights)
        self.numVisibility.valueChanged.connect(self.setVisibility)

    def set_rate(self, value):
        config.playback['interval'] = math.pow(2, -1) * 1000
        global timer
        timer.stop()
        timer.setInterval(config.playback['interval'])
        timer.start()

    def add_vessel(self):
        d = dict(enumerate(string.ascii_lowercase, 1))
        newVessel = createVessel(dict(id=d[len(vesselService.vessels) + 1].upper(),
                                      heading=0,
                                      position=(0, 0),
                                      speed=0,
                                      rate_of_turn=2))

        vesselService.vessels.append(newVessel)
        self.add_vessel_to_GUI(newVessel)

    def add_vessel_to_GUI(self, tmpVessel):
        _translate = QtCore.QCoreApplication.translate
        lblVessel = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        lblVessel.setObjectName("lbl_" + tmpVessel.id)
        lblVessel.setText(_translate("MainWindow", tmpVessel.id))
        self.vessels.addWidget(lblVessel)

        # numHeading = QtWidgets.QSpinBox(self.verticalLayoutWidget_2)
        # numHeading.setMaximum(360)
        # numHeading.setMinimum(0)
        # numHeading.setValue(tmpVessel.shipstate.heading)
        # numHeading.setObjectName("numHeading_" + tmpVessel.id)
        # numHeading.valueChanged.connect(lambda value: self.setHeading(value, tmpVessel))
        # self.vessels.addWidget(numHeading)
        #
        # numPosX_ = QtWidgets.QSpinBox(self.verticalLayoutWidget_2)
        # numPosX_.setMaximum(config.dimensions[1])
        # numPosX_.setMinimum(config.dimensions[0])
        # numPosX_.setValue(tmpVessel.shipstate.position.x)
        # numPosX_.setObjectName("numPosX_" + tmpVessel.id)
        # numPosX_.valueChanged.connect(lambda value: self.setX(value, tmpVessel))
        # self.vessels.addWidget(numPosX_)
        #
        # numPosY_ = QtWidgets.QSpinBox(self.verticalLayoutWidget_2)
        # numPosY_.setMaximum(config.dimensions[3])
        # numPosY_.setMinimum(config.dimensions[2])
        # numPosY_.setValue(tmpVessel.shipstate.position.y)
        # numPosY_.setObjectName("numPosY_" + tmpVessel.id)
        # numPosY_.valueChanged.connect(lambda value: self.setY(value, tmpVessel))
        # self.vessels.addWidget(numPosY_)

        numSpeed_ = QtWidgets.QSpinBox(self.verticalLayoutWidget_2)
        numSpeed_.setMaximum(100)
        numSpeed_.setMinimum(0)
        numSpeed_.setValue(tmpVessel.shipstate.speed)
        numSpeed_.setObjectName("numSpeed_" + tmpVessel.id)
        numSpeed_.valueChanged.connect(lambda value: self.setSpeed(value, tmpVessel))
        self.vessels.addWidget(numSpeed_)

        ap = QtWidgets.QCheckBox(self.verticalLayoutWidget_2)
        ap.setChecked(tmpVessel.ans.auto_pilot)
        ap.setObjectName("ap_" + tmpVessel.id)
        ap.stateChanged.connect(lambda value: self.toggleAP(tmpVessel))
        self.vessels.addWidget(ap)

        self.cbShowArrow.setChecked(config.show['arrow'])

    def pause(self):
        global timer
        remaining = timer.remainingTime()
        timer.stop()
        if remaining > 0:
            timer.setInterval(remaining)
        else:
            timer.setInterval(config.playback['interval'])

    def play(self):
        global timer
        timer.start()

    def toggleHeadings(self, state):
        config.show['arrow'] = not config.show['arrow']

    def toggleSectors(self, state):
        config.show['sectors'] = not config.show['sectors']

    def toggleVisibility(self, state):
        config.show['visibility'] = not config.show['visibility']

    def setX(self, value, tmpVessel):
        tmpVessel.shipstate.position.x = value

    def setY(self, value, tmpVessel):
        tmpVessel.shipstate.position.y = value

    def setSpeed(self, value, tmpVessel):
        tmpVessel.shipstate.speed = value

    def setRoT(self, value, tmpVessel):
        tmpVessel.shipstate.rate_of_turn = value

    def setHeading(self, value, tmpVessel):
        tmpVessel.shipstate.heading = value

    def togglePaths(self, state):
        config.show['paths'] = not config.show['paths']

    def toggleLights(self, state):
        config.show['lights'] = not config.show['lights']

    def setVisibility(self, visibility):
        config.visibility = visibility

    def toggleAP(self, tmpVessel):
        tmpVessel.ans.ap = not tmpVessel.ans.ap


def clear_folder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def main():
    global fis
    folder = '/home/eaura/Google Drive/Skola/Dippe/git/src/img'
    if not os.path.exists(folder):
        os.makedirs(folder)
    clear_folder(folder)
    fis = fuzzy.init_fuzzy()
    init()
    qApp = QtWidgets.QApplication(sys.argv)

    aw = ApplicationWindow()
    aw.setWindowTitle("%s" % progname)
    aw.show()
    if not config.anim:
        for i in range(0, 8000):
            aw.dc.update_figure()
            if i % 1 == 0:
                aw.dc.print_figure('img/foo_' + str(i) + '.png')
                aw.dc.axes.cla()
                aw.dc.axes.set_xlim([config.dimensions[0], config.dimensions[1]])
                aw.dc.axes.set_ylim([config.dimensions[2], config.dimensions[3]])
    sys.exit(qApp.exec_())

    # plot()


if __name__ == "__main__":
    main()
