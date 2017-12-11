from __future__ import unicode_literals
from autonomous_vessel import vessel
from autonomous_vessel.autonomous_navigation_system import shipstate, position
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

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets

# from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

vessels = []
paths = []
timer = None
fis=None

def createVessel(config, fis):
    return vessel.Vessel(
        config['id'],
        shipstate.ShipState(config['heading'], position.Position(config['position'][0], config['position'][1]),
                            config['speed'], config['rate_of_turn']), fis)


def createKnownVessel(tmpVessel):
    return vessel.KnownVessel(
        tmpVessel.id,
        tmpVessel.ans.shipstate)


def cart2pol(x, y):
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return (rho, phi)


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return (x, y)


def init():
    global vessels, paths
    vessels = []
    paths = []
    for vesselConfig in config.vessels:
        vessels.append(createVessel(vesselConfig, fis))

    for A in vessels:
        for B in vessels:
            if A == B:
                continue
            else:
                A.ans.sa.add_observed_vessel(
                    createKnownVessel(B)
                )


def animation_manage(ax):
    opraLines = []
    collissionSectors = []
    arrows = []
    ships = []

    def reset_artists():
        for line in opraLines:
            line.remove()
        for arrow in arrows:
            arrow.remove()
        for sector in collissionSectors:
            sector.remove()
        for ship in ships:
            ship.remove()
        del ships[:]
        del opraLines[:]
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
        patch = plt.Circle((vessel.ans.shipstate.position.get_x(),
                            vessel.ans.shipstate.position.get_y()),
                           radius=config.visibility, gid=vessel.id + '_circle', fill=False)
        ax.add_patch(patch)

        return patch,

    def animate_sector(ax, currentVessel):
        for head_on in currentVessel.ans.ca.risks['head_on']:
            patch = patches.Wedge((
                currentVessel.ans.shipstate.position.get_x(),
                currentVessel.ans.shipstate.position.get_y()),
                config.visibility,
                helpers.nav_to_theta(currentVessel.ans.shipstate.heading + config.sectors['headOn'][1]),
                helpers.nav_to_theta(currentVessel.ans.shipstate.heading + config.sectors['headOn'][0]),
                color='red',
                alpha=0.4,
                ls='solid',
                linewidth=4)

            collissionSectors.append(patch)
            ax.add_patch(patch)
        for head_on in currentVessel.ans.ca.risks['overtaking']:
            patch = patches.Wedge((
                currentVessel.ans.shipstate.position.get_x(),
                currentVessel.ans.shipstate.position.get_y()),
                config.visibility,
                helpers.nav_to_theta(currentVessel.ans.shipstate.heading + config.sectors['over_take_give_way'][1]),
                helpers.nav_to_theta(currentVessel.ans.shipstate.heading + config.sectors['over_take_give_way'][0]),
                color='red',
                alpha=0.4,
                ls='solid',
                linewidth=4)

            collissionSectors.append(patch)
            ax.add_patch(patch)
        for head_on in currentVessel.ans.ca.risks['crossing']:
            patch = patches.Wedge((
                currentVessel.ans.shipstate.position.get_x(),
                currentVessel.ans.shipstate.position.get_y()),
                config.visibility,
                helpers.nav_to_theta(currentVessel.ans.shipstate.heading + config.sectors['crossing_give_way'][1]),
                helpers.nav_to_theta(currentVessel.ans.shipstate.heading + config.sectors['crossing_give_way'][0]),
                color='red',
                alpha=0.4,
                ls='solid',
                linewidth=4)

            collissionSectors.append(patch)
            ax.add_patch(patch)

    def animate_arrow(ax, vessel):
        shipstate = vessel.ans.shipstate
        # coeff = math.sqrt(
        #     math.pow(config.visibility, 2) / (
        #         math.pow(shipstate.get_headingXY()[0], 2) + math.pow(shipstate.get_headingXY()[1], 2)))
        coeff = 50
        arrows.append(ax.annotate("", xy=(shipstate.position.get_x(),
                                          shipstate.position.get_y()),
                                  xytext=(
                                      shipstate.position.get_x() + shipstate.get_headingXY()[0] * coeff,
                                      shipstate.position.get_y() + shipstate.get_headingXY()[1] * coeff),
                                  arrowprops=dict(
                                      arrowstyle='<-',
                                      facecolor='blue'),
                                  gid=vessel.id,
                                  alpha=0.4))

    def animate_ship(ax, vessel):
        color = 'green'
        risk_string = ""
        if vessel.ans.ca.risks['crossing']:
            risk_string = risk_string + "C"
        if vessel.ans.ca.risks['overtaking']:
            risk_string = risk_string + "O"
        if vessel.ans.ca.risks['head_on']:
            risk_string = risk_string + "H"
        if vessel.ans.ca.risks['crossing'] or vessel.ans.ca.risks['overtaking'] or vessel.ans.ca.risks['head_on']:
            color = 'red'
            text = ax.text(vessel.ans.shipstate.position.get_x(),
                           vessel.ans.shipstate.position.get_y(), risk_string,
                           verticalalignment='top', horizontalalignment='center',
                           color='black')
            # ax.add_patch(text)
            ships.append(text)
        text2 = ax.text(vessel.ans.shipstate.position.get_x(),
                        vessel.ans.shipstate.position.get_y(), vessel.id,
                        verticalalignment='bottom', horizontalalignment='center',
                        color='black')
        # ax.add_patch(text)
        ships.append(text2)

        patch = plt.Circle((vessel.ans.shipstate.position.get_x(),
                            vessel.ans.shipstate.position.get_y()),
                           radius=10,
                           label=vessel.id,
                           color=color)

        ships.append(patch)
        ax.add_patch(patch)

    def animate_path(ax, vessel):
        patch = patches.ConnectionPatch(
            (vessel.ans.shipstate.position.x, vessel.ans.shipstate.position.y),
            (vessel.ans.shipstate.snapShotself.positionx, vessel.ans.shipstate.snapShot.position.y),
            "data",
            arrowstyle="-")

        paths.append(patch)
        for tempPatch in paths:
            ax.add_patch(tempPatch)

    def animate_lights(ax, currentVessel):
        patch = patches.Wedge((
            currentVessel.ans.shipstate.position.get_x(),
            currentVessel.ans.shipstate.position.get_y()),
            config.visibility,
            helpers.nav_to_theta(currentVessel.ans.shipstate.heading),
            helpers.nav_to_theta(currentVessel.ans.shipstate.heading - 112.5),
            color='red',
            alpha=0.4)

        collissionSectors.append(patch)
        ax.add_patch(patch)
        patch = patches.Wedge((
            currentVessel.ans.shipstate.position.get_x(),
            currentVessel.ans.shipstate.position.get_y()),
            config.visibility,
            helpers.nav_to_theta(currentVessel.ans.shipstate.heading + 112.5),
            helpers.nav_to_theta(currentVessel.ans.shipstate.heading),
            color='green',
            alpha=0.4)

        collissionSectors.append(patch)
        ax.add_patch(patch)

    reset_artists()
    for tempvessel in vessels:
        tempvessel.ans.next_position()
        animate_ship(ax, tempvessel)
        if config.show['arrow']:
            animate_arrow(ax, tempvessel)
        if config.show['visibility']:
            animate_range(ax, tempvessel)
        if config.show['sectors']:
            animate_sector(ax, tempvessel)
        if config.show['paths']:
            animate_path(ax, tempvessel)
        if config.show['lights']:
            animate_lights(ax, tempvessel)

    return []


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()
        self.axes.set_xlim([config.dimensions[0], config.dimensions[1]])
        self.axes.set_ylim([config.dimensions[2], config.dimensions[3]])

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
        global timer
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        animation_manage(self.axes)
        self.axes.plot()

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)

        self.axes.cla()
        self.axes.set_xlim([config.dimensions[0], config.dimensions[1]])
        self.axes.set_ylim([config.dimensions[2], config.dimensions[3]])
        animation_manage(self.axes)
        self.draw()


class ApplicationWindow(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        dc = MyDynamicMplCanvas(self.centralwidget, width=5, height=4, dpi=100)
        self.verticalLayout.addWidget(dc)

        self.btnPause.clicked.connect(self.pause)
        self.btnPlay.clicked.connect(self.play)
        self.btnReset.clicked.connect(init)
        self.btnAddVessel.clicked.connect(self.add_vessel)
        self.slider.setTickInterval(2)
        self.slider.setMinimum(-2)
        self.slider.setMaximum(2)
        self.slider.setValue(config.playback['rate'])
        self.slider.valueChanged.connect(self.set_rate)

        self.cbShowArrow.setChecked(config.show['arrow'])
        self.cbShowSector.setChecked(config.show['sectors'])
        self.cbShowVisibility.setChecked(config.show['visibility'])
        self.cbShowPath.setChecked(config.show['paths'])
        self.cbShowLights.setChecked(config.show['lights'])
        self.numVisibility.setValue(config.visibility)
        global vessels
        for tmpVessel in vessels:
            self.add_vessel_to_GUI(tmpVessel)

        self.cbShowArrow.stateChanged.connect(self.toggleHeadings)
        self.cbShowSector.stateChanged.connect(self.toggleSectors)
        self.cbShowVisibility.stateChanged.connect(self.toggleVisibility)
        self.cbShowPath.stateChanged.connect(self.togglePaths)
        self.cbShowLights.stateChanged.connect(self.toggleLights)
        self.numVisibility.valueChanged.connect(self.setVisibility)

    def set_rate(self, value):
        config.playback['rate'] = math.pow(2, value)

    def add_vessel(self):
        d = dict(enumerate(string.ascii_lowercase, 1))
        newVessel = createVessel(dict(id=d[len(vessels) + 1].upper(),
                                      heading=0,
                                      position=(0, 0),
                                      speed=0,
                                      rate_of_turn=2))
        for vessel in vessels:
            newVessel.ans.sa.add_observed_vessel(vessel)
            vessel.ans.sa.add_observed_vessel(newVessel)
        vessels.append(newVessel)
        self.add_vessel_to_GUI(newVessel)

    def add_vessel_to_GUI(self, tmpVessel):
        _translate = QtCore.QCoreApplication.translate
        lblVessel = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        lblVessel.setObjectName("lbl_" + tmpVessel.id)
        lblVessel.setText(_translate("MainWindow", tmpVessel.id))
        self.vessels.addWidget(lblVessel)

        numHeading = QtWidgets.QSpinBox(self.verticalLayoutWidget_2)
        numHeading.setMaximum(360)
        numHeading.setMinimum(0)
        numHeading.setValue(tmpVessel.ans.shipstate.heading)
        numHeading.setObjectName("numHeading_" + tmpVessel.id)
        numHeading.valueChanged.connect(lambda value: self.setHeading(value, tmpVessel))
        self.vessels.addWidget(numHeading)

        numPosX_ = QtWidgets.QSpinBox(self.verticalLayoutWidget_2)
        numPosX_.setMaximum(config.dimensions[1])
        numPosX_.setMinimum(config.dimensions[0])
        numPosX_.setValue(tmpVessel.ans.shipstate.position.x)
        numPosX_.setObjectName("numPosX_" + tmpVessel.id)
        numPosX_.valueChanged.connect(lambda value: self.setX(value, tmpVessel))
        self.vessels.addWidget(numPosX_)

        numPosY_ = QtWidgets.QSpinBox(self.verticalLayoutWidget_2)
        numPosY_.setMaximum(config.dimensions[3])
        numPosY_.setMinimum(config.dimensions[2])
        numPosY_.setValue(tmpVessel.ans.shipstate.position.y)
        numPosY_.setObjectName("numPosY_" + tmpVessel.id)
        numPosY_.valueChanged.connect(lambda value: self.setY(value, tmpVessel))
        self.vessels.addWidget(numPosY_)

        numSpeed_ = QtWidgets.QSpinBox(self.verticalLayoutWidget_2)
        numSpeed_.setMaximum(100)
        numSpeed_.setMinimum(0)
        numSpeed_.setValue(tmpVessel.ans.shipstate.speed)
        numSpeed_.setObjectName("numSpeed_" + tmpVessel.id)
        numSpeed_.valueChanged.connect(lambda value: self.setSpeed(value, tmpVessel))
        self.vessels.addWidget(numSpeed_)

        numRoT = QtWidgets.QSpinBox(self.verticalLayoutWidget_2)
        numRoT.setMaximum(180)
        numRoT.setMinimum(0)
        numRoT.setValue(tmpVessel.ans.shipstate.rate_of_turn)
        numRoT.setObjectName("numRoT_" + tmpVessel.id)
        numRoT.valueChanged.connect(lambda value: self.setRoT(value, tmpVessel))
        self.vessels.addWidget(numRoT)

    def pause(self):
        global timer
        remaining = timer.remainingTime()
        timer.stop()
        if remaining > 0:
            timer.setInterval(remaining)
        else:
            timer.setInterval(1000)

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
        tmpVessel.ans.shipstate.position.x = value

    def setY(self, value, tmpVessel):
        tmpVessel.ans.shipstate.position.y = value

    def setSpeed(self, value, tmpVessel):
        tmpVessel.ans.shipstate.speed = value

    def setRoT(self, value, tmpVessel):
        tmpVessel.ans.shipstate.rate_of_turn = value

    def setHeading(self, value, tmpVessel):
        tmpVessel.ans.shipstate.heading = value

    def togglePaths(self, state):
        config.show['paths'] = not config.show['paths']

    def toggleLights(self, state):
        config.show['lights'] = not config.show['lights']

    def setVisibility(self, visibility):
        config.visibility = visibility


def main():
    global fis
    fis = fuzzy.init_fuzzy()
    init()
    qApp = QtWidgets.QApplication(sys.argv)

    aw = ApplicationWindow()
    aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())
    # plot()


if __name__ == "__main__":
    main()
