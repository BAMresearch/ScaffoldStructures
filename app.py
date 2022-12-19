# Copyright (C) 2016 Jairson Dinis 
# Copyright (C) 2018, 2019 Sven Fritzsche <sven.fritzsche@bam.de> - Bundesanstalt fuer Materialforschung und -pruefung
# 
#
#
# -*- coding: utf-8*-
#This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.

#
# This program creates 3D-dimensional low surfaces structures and allows
# the export into the .stl-format.
#


import sys
import os
import wx
import h5py
import numpy as np
import tempfile

from TPMS import TPMS, to_vtk

from vtkmodules.vtkCommonCore import vtkObject
from vtkmodules.vtkFiltersSources import vtkConeSource, vtkSphereSource
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow
)
from vtkmodules.vtkFiltersCore import (
    vtkMarchingCubes, vtkWindowedSincPolyDataFilter
)

from vtkmodules.vtkIOGeometry import vtkSTLWriter

from vtkmodules.vtkCommonDataModel import vtkImageData
import vtkmodules.vtkRenderingOpenGL2




from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
from vtk.util import numpy_support
from pubsub import pub
from numpy import cos, sin, ogrid, pi


#from slider_text import SliderText
from FloatSliderText import FloatSliderText



class LeftPanel(wx.Panel):

    """
    Builds the left panel - with the sliders and options
    """


    def __init__(self, parent, id, style):
        wx.Panel.__init__(self, parent, id, style=style)
        self.build_gui()
        self.__bind_events_wx()
        self.__bind_events_pb()

        self.Show()

        # Error description
        #log_path = os.path.join('.', 'vtkoutput.txt')
        #fow = vtkFileOutputWindow()
        #fow.SetFileName(log_path)
        #ow = vtkOutputWindow()
        #ow.SetInstance(fow)
        #-----------------------


    def build_gui(self):

        """
        Defines the GUI and sliders with wx
        """

        self.choose_scaffold = wx.ComboBox(self, -1, "Schwarz P",\
                                         choices=(
                                             "Schwarz P",\
                                             "Schwarz D",\
                                             "Gyroid",\
                                             "F-RD",\
                                             "Neovius",\
                                             "iWP",\
                                             'P_W_Hybrid',\
                                             "L-Type",\
                                             'Skeletal 1',\
                                             'Skeletal 2',\
                                             'Tubular G',\
                                             'Tubular P',\
                                             "I2-Y",\
                                             "G'",\
                                             "Double Gyroid",\
                                             "Double Schwarz P",\
                                             "Double Diamond",\
                                             "Fischer-Koch S"        
                                             ),
                                           style=wx.CB_READONLY)




        self.Reset_scaffold = wx.Button(self, -1, "Rendering")

        self.porosity_value_x = wx.SpinCtrl(self, -1, '')
        self.porosity_value_x.SetRange(1, 20)
        self.porosity_value_x.SetValue(1)
        
        self.porosity_value_y = wx.SpinCtrl(self, -1, '')
        self.porosity_value_y.SetRange(1, 20)
        self.porosity_value_y.SetValue(1)
        
        self.porosity_value_z = wx.SpinCtrl(self, -1, '')
        self.porosity_value_z.SetRange(1, 20)
        self.porosity_value_z.SetValue(1)
        
        self.spacing_value_x = FloatSliderText(self, -1, '', 0.2, 0.02, 0.5, 0.02)
        self.hole_dimension_value1 = FloatSliderText(self, -1, 'Positive Direction', 0.3, 0.1, 3.14, 0.1)
        self.hole_dimension_value2 = FloatSliderText(self, -1, 'Negative Direction', 0.3, 0.1, 3.14, 0.1)

        self.v_porosity = wx.StaticText(self, -1, "")
        self.Lx = wx.StaticText(self, -1, "")
        self.Ly = wx.StaticText(self, -1, "")
        self.Lz = wx.StaticText(self, -1, "")


        b_sizer = wx.BoxSizer(wx.VERTICAL)


        b_sizer.Add(wx.StaticText(self, -1, "Type of Minimal Surface"), 0, wx.CENTRE | wx.ALL, 10)
        b_sizer.Add(self.choose_scaffold, 0, wx.CENTRE)
        b_sizer.Add(wx.StaticText(self, -1, "Number of primitive cells in X-direction"), 0, wx.CENTRE | wx.ALL, 10)
        b_sizer.Add(self.porosity_value_x, 0, wx.CENTRE)
        b_sizer.Add(wx.StaticText(self, -1, "Number of primitive cells in Y-direction"), 0, wx.CENTRE | wx.ALL, 10)
        b_sizer.Add(self.porosity_value_y, 0, wx.CENTRE)
        b_sizer.Add(wx.StaticText(self, -1, "Number of primitive cells in Z-direction"), 0, wx.CENTRE | wx.ALL, 10)
        b_sizer.Add(self.porosity_value_z, 0, wx.CENTRE)
        b_sizer.Add(wx.StaticText(self, -1, "Quality factor (lower is better)"), 0, wx.CENTRE | wx.ALL, 10)
        b_sizer.Add(self.spacing_value_x, 0, wx.EXPAND)
        b_sizer.Add(wx.StaticText(self, -1, "Wall Thickness"), 0, wx.CENTRE | wx.ALL, 10)
        b_sizer.Add(self.hole_dimension_value1, 0, wx.EXPAND)
        b_sizer.Add(self.hole_dimension_value2, 0, wx.EXPAND)
        b_sizer.Add(self.Reset_scaffold, 0)
        
        
        

        b_sizer.Add(self.v_porosity, 0, wx.EXPAND)
        b_sizer.Add(self.Lx, 0, wx.EXPAND)
        b_sizer.Add(self.Ly, 0, wx.EXPAND)
        b_sizer.Add(self.Lz, 0, wx.EXPAND)



        hbox = wx.BoxSizer(wx.VERTICAL)
        hbox.Add(b_sizer, 1, wx.EXPAND)


        self.SetSizer(hbox)

    def __bind_events_wx(self):
        self.Reset_scaffold.Bind(wx.EVT_BUTTON, self.renderer)



    def __bind_events_pb(self):
        pub.subscribe(self._show_info, 'show info')

    def renderer(self, evt):
        tipo = self.choose_scaffold.GetValue()
        X = 2 * pi * self.porosity_value_x.GetValue()
        Y = 2 * pi * self.porosity_value_y.GetValue()
        Z = 2 * pi * self.porosity_value_z.GetValue()
        sX = self.spacing_value_x.GetValue()
        sY = self.spacing_value_x.GetValue()
        sZ = self.spacing_value_x.GetValue()
        pos = self.hole_dimension_value1.GetValue()
        neg = self.hole_dimension_value2.GetValue()


        tam = X, Y, Z
        spacing = sX, sY, sZ
        hole_size = neg, pos


        pub.sendMessage('Recalculating surface', msg=(tipo, tam, spacing, hole_size))
        pub.sendMessage('Calculating porosity')

    def _show_info(self, msg3):
        p, lx, ly, lz = msg3
        self.v_porosity.SetLabel('Porosity: %.2f %%' % p)
        self.Lx.SetLabel('Length X-direction: %.2f units' % lx)
        self.Ly.SetLabel('Length Y-direction: %.2f units' % ly)
        self.Lz.SetLabel('Length Z-direction: %.2f units' % lz)




class PanelRight(wx.Panel):

    """
    Builds the image panel that shows the TPMS
    """
    
    def __init__(self, parent, id, style):
        wx.Panel.__init__(self, parent, id, style=style)

        self.frontview = FrontView(self, id=-1, style=wx.BORDER_SUNKEN)



        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.frontview, 1, wx.EXPAND)
        #vbox.Add(self.visaotop, 1, wx.EXPAND)



        hbox = wx.BoxSizer()
        hbox.Add(vbox, 1, wx.EXPAND)

        self.SetSizer(hbox)



class FrontView(wx.Panel):
    def __init__(self, parent, id, style):
        wx.Panel.__init__(self, parent, id, style=style)

        self.renderer = vtkRenderer()
        self.Interactor = wxVTKRenderWindowInteractor(self, -1, size=self.GetSize())
        self.Interactor.GetRenderWindow().AddRenderer(self.renderer)
        self.Interactor.Render()



        istyle = vtkInteractorStyleTrackballCamera()

        self.Interactor.SetInteractorStyle(istyle)



        hbox = wx.BoxSizer(wx.VERTICAL)
        hbox.Add(wx.StaticText(self, -1, 'Global Structure of Scaffold'))


        hbox.Add(self.Interactor, 1, wx.EXPAND)
        self.SetSizer(hbox)


        self.init_actor()
        self.add_axes()
        self.draw_surface()
        self.renderer.ResetCamera()

        pub.subscribe(self._draw_surface, 'Recalculating surface')
        pub.subscribe(self._calculate_porosity, 'Calculating porosity')

    def init_actor(self):
        self.mapper = vtkPolyDataMapper()


        self.SurfaceActor = vtkActor()
        self.SurfaceActor.SetMapper(self.mapper)

        self.renderer.AddActor(self.SurfaceActor)

        self.renderer.ResetCamera()

        self.Interactor.Render()



    def _draw_surface(self, msg):
        tipo, tam, spacing, hole_size = msg

        self.draw_surface(tipo, tam, spacing, hole_size)


    def draw_surface(self, tipo='Schwarz P', tam=None,
                     spacing=None, hole_size=None):
        if tam is None:
            tam = 2*pi, 2*pi, 2*pi
        if spacing is None:
            spacing = 0.1, 0.1, 0.1
        if hole_size is None:
            hole_size = 0.3, 0.3
        #print hole_size

        M = TPMS(tipo, tam, spacing, hole_size)

        tf = tempfile.TemporaryFile()
        f = h5py.File(tf, "w")

        f['data'] = M
        f['spacing'] = np.array(spacing)

        self.M = M
        self.spacing = spacing


        image = to_vtk(M, spacing)

        surf = vtkMarchingCubes()
        surf.SetInputData(image)
        #surf.SetValue(0,0.5)
        surf.SetValue(0, 0.1)
        surf.ComputeNormalsOn()
        surf.ComputeGradientsOn()
        surf.Update()

        subdiv = vtkWindowedSincPolyDataFilter()
        subdiv.SetInputData(surf.GetOutput())
        subdiv.SetNumberOfIterations(100)
        subdiv.SetFeatureAngle(120)
        subdiv.SetBoundarySmoothing(60)
        subdiv.BoundarySmoothingOn()
        subdiv.SetEdgeAngle(90)
        subdiv.Update()

##        subdiv= vtk.vtkLoopSubdivisionFilter()
##        subdiv.SetInput(surf.GetOutput())
##        subdiv.Update()

        #self.mapper.SetInput(surf.GetOutput())

        self.mapper.SetInputData(subdiv.GetOutput())
        self.Interactor.Render()

    def _calculate_porosity(self):
        p = self.calculate_porosity()
        lx, ly, lz = self.measure_distance()

        pub.sendMessage('show info', msg3=(p, lx, ly, lz))





    def calculate_porosity(self):
        M = self.M
        sx, sy, sz = self.spacing
        z, y, x = M.shape

        v_total = x*sx * y*sy * z*sz
        #v_walls = ((M > -0.1) & (M < 0.1)).sum() * sx*sy*sz
        v_walls = M.sum() * sx*sy*sz

        vporos = v_total - v_walls

        return 100.0*vporos/v_total



    def measure_distance(self):
        M = self.M
        sx, sy, sz = self.spacing
        z, y, x = M.shape

        Lx = x*sx
        Ly = y*sy
        Lz = z*sz
        return Lz, Ly, Lx




    def add_axes(self):
        axes = vtkAxesActor()
        self.marker = vtkOrientationMarkerWidget()
        self.marker.SetInteractor(self.Interactor)
        self.marker.SetOrientationMarker(axes)
        self.marker.SetViewport(0.75, 0, 1, 0.25)
        self.marker.SetEnabled(1)



    def write_model_stl(self, path):
        write = vtkSTLWriter()
        write.SetInputData(self.mapper.GetInput())
        write.SetFileTypeToBinary()
        write.SetFileName(path)
        write.Write()
        write.Update()




class MainWindow(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(700, 650))

        #----------------------------------

        panel = wx.Panel(self, -1)

        self.currentDirectory = os.getcwd()

        self.RightPanel = PanelRight(self, id=-1, style=wx.BORDER_SUNKEN)
        self.LeftPanel = LeftPanel(self, id=-1, style=wx.BORDER_SUNKEN)


        hbox = wx.BoxSizer()
        hbox.Add(self.RightPanel, 1, wx.EXPAND)
        hbox.Add(self.LeftPanel, 1, wx.EXPAND)



        self.SetSizer(hbox)

        #criar menu

        MenuBar = wx.MenuBar()
        menu = wx.Menu()


        save = menu.Append(-1, "&Save ")
        close = menu.Append(-1, "&Exit")
        MenuBar.Append(menu, "File")

        self.SetMenuBar(MenuBar)

        # tratar os eventos
        self.Bind(wx.EVT_MENU, self.close_program, close)
        self.Bind(wx.EVT_MENU, self.save_model_stl, save)


        self.Show()


    def close_program(self, event):
        dial = wx.MessageDialog(None, 'Do you really want to close this program?', 'Question', wx.YES_NO |wx.NO_DEFAULT | wx.ICON_QUESTION)
        ret = dial.ShowModal()
        if ret == wx.ID_YES:
            self.Destroy()



    def save_model_stl(self, evt):
        wildcard = "(*.stl)|*.stl"
        dlg = wx.FileDialog(
            self, message="Save file as ...",
            defaultDir=self.currentDirectory,
            defaultFile="", wildcard=wildcard, style=wx.FD_SAVE
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.RightPanel.frontview.write_model_stl(path)
        dlg.Destroy()




if __name__ == '__main__':
    App = wx.App(0)
    W = MainWindow(None, -1, 'Interface Scaffold ')
    W.Show()
    App.MainLoop()
