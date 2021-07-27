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
import vtk
import h5py
import numpy


from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
from vtk.util import numpy_support
from pubsub import pub
from numpy import cos, sin, ogrid, pi


#from slider_text import SliderText
from FloatSliderText import FloatSliderText



def to_vtk(n_array, spacing, slice_number=0, orientation='AXIAL'):

    """
    This function defines orientation or the TPMS.
    Starts vtk.
    """


    try:
        dz, dy, dx = n_array.shape
    except ValueError:
        dy, dx = n_array.shape
        dz = 1

    v_image = numpy_support.numpy_to_vtk(n_array.flat)

    if orientation == 'AXIAL':
        extent = (0, dx -1, 0, dy -1, slice_number, slice_number + dz - 1)
    #elif orientation == 'SAGITAL':
    #     dx, dy, dz = dz, dx, dy
    #     extent = (slice_number, slice_number + dx - 1, 0, dy - 1, 0, dz - 1)
    #elif orientation == 'CORONAL':
    #     dx, dy, dz = dx, dz, dy
    #     extent = (0, dx - 1, slice_number, slice_number + dy - 1, 0, dz - 1)

    # Generating the vtkImageData
    image = vtk.vtkImageData()
    image.SetOrigin(0, 0, 0)
    image.SetSpacing(spacing)
    #  image.SetNumberOfScalarComponents(1)
    image.SetDimensions(dx, dy, dz)
    image.SetExtent(extent)
    #  image.SetScalarType(numpy_support.get_vtk_array_type(n_array.dtype))
    image.AllocateScalars(numpy_support.get_vtk_array_type(n_array.dtype), 1)
    image.GetPointData().SetScalars(v_image)
    #  image.Update()
    #  image.UpdateInformation()

    #  image_copy = vtk.vtkImageData()
    #  image_copy.DeepCopy(image)
    #  image_copy.Update()

    return image


def fun_schwarzP(type_surface, tam, spacing, hole_size):

    """
    Definition of the different TPMS.
    """



    tz, ty, tx = tam
    sx, sy, sz = spacing
    pos, neg = hole_size



    z, y, x = ogrid[-tx/2:tx/2:sx, -ty/2:ty/2:sy, -tz/2:tz/2:sz]

    #print type_surface
    if type_surface == 'Schwarz_P':
        f = cos(x) + cos(y) + cos(z)
    elif type_surface == 'Schwarz D':
        f = sin(x) * sin(y) * sin(z) + sin(x) * cos(y) * cos(z) \
        + cos(x) * sin(y) * cos(z) + cos(x) * cos(y) * sin(z)
    elif type_surface == "Gyroid":
        f = cos(x) * sin(y) + cos(y) * sin(z) + cos(z) * sin(x)
    elif type_surface == "F-RD":
        cx = cos(2*x)
        cy = cos(2*y)
        cz = cos(2*z)
        f = 4 * cos(x) * cos(y) * cos(z) - (cx * cy + cx * cz + cy * cz)
    elif type_surface == "Neovius":
        f = 3*(cos(x) + cos(y) + cos(z)) + 4* cos(x) * cos(y) * cos(z)
    elif type_surface == "iWP":
        f = cos(x) * cos(y) + cos(y) * cos(z) + cos(z) * cos(x) \
        - cos(x) * cos(y) * cos(z)
    elif type_surface == 'P_W_Hybrid':
        f = 4*(cos(x) * cos(y) + cos(y) * cos(z) + cos(z) * cos(x)) \
        -3* cos(x) * cos(y) * cos(z) + 2.4
    elif type_surface == "L-Type":
        cxx = cos(2*x)
        cyy = cos(2*y)
        czz = cos(2*z)
        cx = cos(x)
        cy = cos(y)
        cz = cos(z)
        sx = sin(x)
        sy = sin(y)
        sz = sin(z)
        f = 0.5*(sin(2*x) * cy * sz + sin(2*y) * cz * sx \
            + sin(2*z) * cx * sy) - \
            0.5 * (cxx * cyy + cyy * czz + czz * cxx) + 0.15
    elif type_surface == 'Skeletal 1':
        cx = cos(x)
        cy = cos(y)
        cz = cos(z)
        f = 10.0*(cx*cy + cy*cz + cz*cx) \
        - 5.0*(cos(x*2) + cos(y*2) + cos(z*2)) - 14.0
    elif type_surface == 'Skeletal 2':
        cx = cos(4*x)
        cy = cos(4*y)
        cz = cos(4*z)
        xo = x - pi/4
        yo = y - pi/4
        zo = z - pi/4
        f = 10.0 * (sin(xo) * sin(yo) * sin(zo) + sin(xo) * cos(yo) * cos(zo) \
            + cos(xo) * sin(yo) * cos(zo)+ cos(xo) * cos(yo) * sin(zo)) \
            -  0.7*(cx + cy + cz) - 11.0
    elif type_surface == 'Tubular G':
        cx = cos(2*x)
        cy = cos(2*y)
        cz = cos(2*z)
        f = 10.0*(cos(x) * sin(y) + cos(y) * sin(z) + cos(z) * sin(x)) \
        -  0.5*(cx*cy + cy*cz + cz*cx) - 14.0
    elif type_surface == 'Tubular P':
        cx = cos(x)
        cy = cos(y)
        cz = cos(z)
        f = 10.0*(cx + cy + cz) -  5.1*(cx*cy + cy*cz + cz*cx) - 14.6
    elif type_surface == "I2-Y":
        cx = cos(2*x)
        cy = cos(2*y)
        cz = cos(2*z)
        f = -2 * (sin(2*x) * cos(y) * sin(z) + sin(x) * sin(2*y) * cos(z) \
            + cos(x) * sin(y) * sin(2*z)) + cx * cy + cy * cz + cx * cz
    elif type_surface == "G'":
        sx = sin(2*x)
        sy = sin(2*y)
        sz = sin(2*z)
        cxx = cos(2*x)
        cyy = cos(2*y)
        czz = cos(2*z)
        s4x = sin(4*x)
        s4y = sin(4*y)
        s4z = sin(4*z)
        c4x = cos(4*x)
        c4y = cos(4*y)
        c4z = cos(4*z)
        f = 0.8*(s4x * sz * cyy + s4y * sx * czz + s4z * sy * cxx) \
            - 0.2 * (c4x * c4y + c4y * c4z + c4z * c4x)
    elif  type_surface == "Double Diamond":
        sx = sin(2*x)
        sy = sin(2*y)
        sz = sin(2*y)
        cx = cos(2*x)
        cy = cos(2*y)
        cz = cos(2*z)
        f = sx * sy + sy * sz + sx * sz + cx * cy * cz- 0.35
    
    elif  type_surface == "Double Gyroid":
        sx = sin(2*x)
        sy = sin(2*y)
        sz = sin(2*y)
        cx = cos(2*x)
        cy = cos(2*y)
        cz = cos(2*z)
        f = 2.75 * ( sx * sin(z) * cos(y) + sy * sin(x) * cos(z) + sz * sin(y) * cos(x)) - (cx * cy + cy * cz  + cx * cz) - 0.35
    
    elif  type_surface == "Fischer-Koch S":
        cx = cos(2*x)
        cy = cos(2*y)
        cz = cos(2*z)
        f =  cx * sin(y) * cos(z) + cx * sin(z) * cos(x) + cz * sin(x) * cos(y) - 0.375

    elif  type_surface == "Double Schwarz P":
        cx = cos(2*x)
        cy = cos(2*y)
        cz = cos(2*z)
        f =  0.5 * (cos(x) * cos(y) + cos(y) * cos(z) + cos(z) * cos(x)) + 0.2 * (cx + cy + cz) 



    #M=numpy.array(f)
    M = numpy.array(((f > -neg) & (f < pos)) * 1.0)

    #print M.shape, (i+2 for i in M.shape)
    N = numpy.zeros([i+2 for i in M.shape])
    N[1:-1, 1:-1, 1:-1] = M
    return N



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
        log_path = os.path.join('.', 'vtkoutput.txt')
        fow = vtk.vtkFileOutputWindow()
        fow.SetFileName(log_path)
        ow = vtk.vtkOutputWindow()
        ow.SetInstance(fow)
        #-----------------------


    def build_gui(self):

        """
        Defines the GUI and sliders with wx
        """

        self.choose_scaffold = wx.ComboBox(self, -1, "Schwarz_P",\
                                         choices=(
                                             "Schwarz_P",\
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
        self.hole_dimension_value1 = FloatSliderText(self, -1, 'Positive Direction', 0.3, 0.1, 1.1, 0.1)
        self.hole_dimension_value2 = FloatSliderText(self, -1, 'Negative Direction', 0.3, 0.1, 1.1, 0.1)

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

        self.renderer = vtk.vtkRenderer()
        self.Interactor = wxVTKRenderWindowInteractor(self, -1, size=self.GetSize())
        self.Interactor.GetRenderWindow().AddRenderer(self.renderer)
        self.Interactor.Render()



        istyle = vtk.vtkInteractorStyleTrackballCamera()

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
        self.mapper = vtk.vtkPolyDataMapper()


        self.SurfaceActor = vtk.vtkActor()
        self.SurfaceActor.SetMapper(self.mapper)
        #ultimo para adionar actor
        #exemplo
        self.renderer.AddActor(self.SurfaceActor)

        self.renderer.ResetCamera()

        self.Interactor.Render()



    def _draw_surface(self, msg):
        tipo, tam, spacing, hole_size = msg

        self.draw_surface(tipo, tam, spacing, hole_size)


    def draw_surface(self, tipo='Schwarz_P', tam=None,
                     spacing=None, hole_size=None):
        if tam is None:
            tam = 4*pi, 4*pi, 4*pi
        if spacing is None:
            spacing = 0.2, 0.2, 0.2
        if hole_size is None:
            hole_size = 0.3, 0.3
        #print hole_size

        M = fun_schwarzP(tipo, tam, spacing, hole_size)

        f = h5py.File("1.hdf5", "w")
        f['data'] = M
        f['spacing'] = numpy.array(spacing)

        self.M = M
        self.spacing = spacing


        image = to_vtk(M, spacing)

        surf = vtk.vtkMarchingCubes()
        surf.SetInputData(image)
        #surf.SetValue(0,0.5)
        surf.SetValue(0, 0.1)
        surf.ComputeNormalsOn()
        surf.ComputeGradientsOn()
        surf.Update()

        subdiv = vtk.vtkWindowedSincPolyDataFilter()
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
        axes = vtk.vtkAxesActor()
        self.marker = vtk.vtkOrientationMarkerWidget()
        self.marker.SetInteractor(self.Interactor)
        self.marker.SetOrientationMarker(axes)
        self.marker.SetViewport(0.75, 0, 1, 0.25)
        self.marker.SetEnabled(1)



    def write_model_stl(self, path):
        write = vtk.vtkSTLWriter()
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
