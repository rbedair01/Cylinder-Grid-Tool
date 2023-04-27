# 23456789+123456789+123456789+123456789+123456789+123456789+123456789+1@345678|
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance

def get_maya_main_win():
    """Return the Maya main window widget"""
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QWidget)

class CylinderFaceGrid(QtWidgets.QDialog):
    """Grid out cylinder face class"""
    """window tool class"""

    def __init__(self):
        """Initialise the object"""
        super(CylinderFaceGrid, self).__init__(parent=get_maya_main_win())
        self._set_win()
        self._define_widgets()
        self._layout_widgets()
        self._connect_signals_slots()

    def _set_win(self):
        """Window Settings"""
        self.setWindowTitle("Grid Cylinder Face")
        self.resize(400, 200)

    def _define_widgets(self):
        self._cylinderAttr_widgets()
        self.createCylinder_btn = QtWidgets.QPushButton("Create Cylinder")
        self.grid_btn = QtWidgets.QPushButton("Grid Out")

    def _cylinderAttr_widgets(self):
        self.num_radius_lbl = QtWidgets.QLabel("Radius:")
        self.num_radius = QtWidgets.QSpinBox()
        self.num_radius.setValue(1)
        self.num_height_lbl = QtWidgets.QLabel("Height:")
        self.num_height = QtWidgets.QSpinBox()
        self.num_height.setValue(2)
        self.num_ASubdiv_lbl = QtWidgets.QLabel("Sub. Axis:")
        self.num_ASubdiv = QtWidgets.QSpinBox()
        self.num_ASubdiv.setValue(12)
        self.num_HSubdiv_lbl = QtWidgets.QLabel("Sub. Height:")
        self.num_HSubdiv = QtWidgets.QSpinBox()
        self.num_HSubdiv.setValue(1)
        self.num_CSubdiv_lbl = QtWidgets.QLabel("Sub. Caps:")
        self.num_CSubdiv = QtWidgets.QSpinBox()
        self.num_CSubdiv.setValue(2)


    def _cylinderAttr_layout(self):
        self.cylAttr_1 = QtWidgets.QHBoxLayout()
        self.cylAttr_1.addWidget(self.num_radius_lbl)
        self.cylAttr_1.addWidget(self.num_radius)
        self.cylAttr_1.addWidget(self.num_height_lbl)
        self.cylAttr_1.addWidget(self.num_height)
        self.cylAttr_2 = QtWidgets.QHBoxLayout()
        self.cylAttr_2.addWidget(self.num_ASubdiv_lbl)
        self.cylAttr_2.addWidget(self.num_ASubdiv)
        self.cylAttr_2.addWidget(self.num_HSubdiv_lbl)
        self.cylAttr_2.addWidget(self.num_HSubdiv)
        self.cylAttr_2.addWidget(self.num_CSubdiv_lbl)
        self.cylAttr_2.addWidget(self.num_CSubdiv)

    def _layout_widgets(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self._cylinderAttr_layout()
        self.main_layout.addLayout(self.cylAttr_1)
        self.main_layout.addLayout(self.cylAttr_2)
        self.main_layout.addWidget(self.createCylinder_btn)
        self.main_layout.addWidget(self.grid_btn)
        self.setLayout(self.main_layout)

    def _connect_signals_slots(self):
        self.createCylinder_btn.clicked.connect(self.createCylinder)
        self.grid_btn.clicked.connect(self.grid)

    @QtCore.Slot()
    def createCylinder(self):
        create_cylinder(radius=self.num_radius.value(), height=self.num_height.value(),
                        subDivAxis=self.num_ASubdiv.value(), subDivHeight=self.num_HSubdiv.value(),
                        subDivCaps=self.num_CSubdiv.value())
        remove_edge(subDivAxis=self.num_ASubdiv.value())
        create_edge(subDivAxis=self.num_ASubdiv.value(), subDivCaps=self.num_CSubdiv.value())


    @QtCore.Slot()
    def grid(self):
        remove_edge(subDivAxis=self.num_ASubdiv.value())
        create_edge(subDivAxis=self.num_ASubdiv.value(), subDivCaps=self.num_CSubdiv.value())


def create_cylinder(obj="", radius=1, height=2, subDivAxis=12, subDivHeight=1, subDivCaps=2):
    cmds.polyCylinder(radius=radius, height=height, subdivisionsAxis=subDivAxis,
                      subdivisionsCaps=subDivCaps, subdivisionsHeight=subDivHeight)


def remove_edge(subDivAxis=12):
    select_obj = cmds.ls(selection=True)[0]

    # total number of edges
    num_edges = cmds.polyEvaluate("pCylinder1", edge=True)
    # Define the range of edges to be deleted
    edge_range = (num_edges-(subDivAxis*2), num_edges-1)
    # select range of edges previously defined
    cmds.select(f'{select_obj}.e[{edge_range[0]}:{edge_range[1]}]')
    # Delete Edges
    cmds.polyDelEdge(cv=True)


def create_edge(subDivAxis=12, subDivCaps=2):
    # total verts after edges have been removed
    total_verts = cmds.polyEvaluate(v=True)
    num_edges = cmds.polyEvaluate(edge=True)
    half_SubAxis = subDivAxis/2
    last_CompID = total_verts - 2

    if subDivAxis <= 4:
        return -1

    counter = 0

    # For Cylinders in which their subdivisions are divisible by 4
    if subDivAxis%4 == 0:
        # 1st Edge (Middle)
        cmds.polySplit(ch=False, ip=[(last_CompID, 1), (last_CompID - half_SubAxis, 1)])
        cmds.polySplit(ch=False, ip=[(0, 0), (half_SubAxis, 0)])
        edgeAmount = (subDivAxis-4)/2
        cross_vert = half_SubAxis / 2

        counter=counter+1

        # if subdivision axis is 8 - no need for loop (its just 2 main lines)
        if edgeAmount == 2:
            if subDivCaps > 1:
                cmds.polySplit(ch=False, sma=180.0, ip=[(last_CompID-cross_vert, 1), ((last_CompID-cross_vert)-half_SubAxis, 1)])
                cmds.polySplit(ch=False, sma=180.0, ip=[((half_SubAxis / 2) - 1, 1), (((half_SubAxis / 2) - 1) + half_SubAxis, 1)])
                return -1
            elif subDivCaps == 1:
                cmds.polySplit(ch=False, sma=180.0, ip=[((last_CompID - cross_vert)+1, 1), (((last_CompID - cross_vert) - half_SubAxis)+1, 1)])
                cmds.polySplit(ch=False, sma=180.0, ip=[(((half_SubAxis / 2)-1) + half_SubAxis, 0), ((half_SubAxis / 2)-1, 0)])
                return -1


        # if subdivision axis is greater than 8
        i = 0
        while i < edgeAmount/2-1:
            # Left Side
            counter = counter + 1
            if (total_verts-1)-i == last_CompID+1:
                cmds.polySplit(ch=False, sma=180.0, ip=[((total_verts-1), 1), (((last_CompID - (subDivAxis-1))+edgeAmount), 1)])
            else:
                cmds.polySplit(ch=False, sma=180.0, ip=[(((total_verts-1) - subDivAxis)+i, 1), (((last_CompID - (subDivAxis-1))+edgeAmount)-i, 1)])
            cmds.polySplit(ch=False, ip=[(1+i, 0), ((half_SubAxis - 1)-i, 0)])
            # Right Side
            counter = counter + 1
            cmds.polySplit(ch=False, ip=[((last_CompID-1)-i, 1), (((last_CompID-1)-edgeAmount)+i, 1)])
            cmds.polySplit(ch=False, ip=[((subDivAxis - 1)-i, 0), ((half_SubAxis + 1)+i, 0)])

            i = i+1

        #Last Edge (Cross Over other edges in opposite direction)
        total_verts = cmds.polyEvaluate(v=True)
        last_CompID_2 = total_verts - 2

        if subDivCaps > 1:
            cmds.polySplit(ch=False, sma=180.0, ip=[(last_CompID_2-cross_vert, 1), ((last_CompID_2-cross_vert)-half_SubAxis, 1)])
            cmds.polySplit(ch=False, sma=180.0, ip=[((half_SubAxis/2)-1, 1), (((half_SubAxis/2)-1)+half_SubAxis, 1)])
        elif subDivCaps == 1:
            if subDivAxis == 12:
                cmds.polySplit(ch=False, sma=180.0, ip=[(last_CompID_2-cross_vert, 1), ((last_CompID_2-cross_vert)-half_SubAxis, 1)])
                cmds.polySplit(ch=False, sma=180.0, ip=[(((half_SubAxis/2))+half_SubAxis, 0), (41, 0.5), (37, 0.5), (39, 0.5), ((half_SubAxis/2), 0)])
            else:
                return -1
    elif subDivAxis%2 == 0:
        # 1st Edge (Middle)
        cmds.polySplit(ch=False, ip=[(last_CompID, 1), (last_CompID - half_SubAxis, 1)])
        cmds.polySplit(ch=False, ip=[(0, 0), (half_SubAxis, 0)])
        edgeAmount = (subDivAxis-4)/2

        i = 0
        while i < edgeAmount/2-1:
            # Left Side
            counter = counter + 1
            if (total_verts-1)-i == last_CompID+1:
                cmds.polySplit(ch=False, sma=180.0, ip=[((total_verts-1), 1), (((last_CompID - (subDivAxis-1))+edgeAmount), 1)])
            else:
                cmds.polySplit(ch=False, sma=180.0, ip=[(((total_verts-1) - subDivAxis)+i, 1), (((last_CompID - (subDivAxis-1))+edgeAmount)-i, 1)])
            cmds.polySplit(ch=False, ip=[(1+i, 0), ((half_SubAxis - 1)-i, 0)])
            # Right Side
            counter = counter + 1
            cmds.polySplit(ch=False, ip=[((last_CompID-1)-i, 1), (((last_CompID-1)-edgeAmount)+i, 1)])
            cmds.polySplit(ch=False, ip=[((subDivAxis - 1)-i, 0), ((half_SubAxis + 1)+i, 0)])

            i = i+1


window = CylinderFaceGrid()
window.show()

if __name__ == "__main__":
    pass
