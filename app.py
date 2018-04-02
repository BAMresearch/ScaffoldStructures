# -*- coding: utf-8*-
import wx
import sys
import os
from math import *
import vtk
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub
import numpy
from numpy import cos, sin,ogrid,pi
from vtk.util import numpy_support
from numpy import*

#from slider_text import SliderText
from FloatSliderText import FloatSliderText

import h5py

wildcard = "(*.stl)|*.stl"

def to_vtk(n_array, spacing, slice_number=0, orientation='AXIAL'):
    try:
        dz, dy, dx = n_array.shape
    except ValueError:
        dy, dx = n_array.shape
        dz = 1

    v_image = numpy_support.numpy_to_vtk(n_array.flat)

    if orientation == 'AXIAL':
        extent = (0, dx -1, 0, dy -1, slice_number, slice_number + dz - 1)
    elif orientation == 'SAGITAL':
        dx, dy, dz = dz, dx, dy
        extent = (slice_number, slice_number + dx - 1, 0, dy - 1, 0, dz - 1)
    elif orientation == 'CORONAL':
        dx, dy, dz = dx, dz, dy
        extent = (0, dx - 1, slice_number, slice_number + dy - 1, 0, dz - 1)

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


def fun_schwartzP(type_surface,tam,spacing,hole_size, ufunc=None):
    tz, ty, tx = tam
    sx, sy, sz = spacing
    pos,neg=hole_size
    
    
    z,y,x=ogrid[-tx/2:tx/2:sx,-ty/2:ty/2:sy,-tz/2:tz/2:sz]

    #print type_surface
    if type_surface=='Schwarz_P':
        f=cos(x)+cos(y)+ cos(z)
    elif type_surface=='Schwarz_D':
        f=sin(x)*sin(y)*sin(z)+sin(x)*cos(y)*cos(z)+cos(x)*sin(y)*cos(z)+cos(x)*cos(y)*sin(z)

    elif type_surface=="Gyroid":
        f=cos (x) * sin(y) + cos (y) * sin (z) + cos (z) * sin (x)
    elif type_surface=="Neovius":
        f=3*(cos (x) + cos (y) + cos (z)) + 4* cos (x) * cos (y) * cos (z)
    elif type_surface=="iWP":
        f=cos (x) * cos (y) + cos (y) * cos (z) + cos (z) * cos (x) - cos (x) * cos (y) * cos (z)
    elif type_surface=='P_W_Hybrid':
        f=4*(cos (x) * cos (y) + cos (y) * cos (z) + cos (z) * cos (x)) -3* cos (x) * cos (y) * cos (z)+2.4
    elif type_surface=='Skeletal_1':
        cx = cos(x)
        cy = cos(y)
        cz = cos(z)
        f=10.0*(cx*cy + cy*cz + cz*cx) -  5.0*(cos(x*2) + cos(y*2) + cos (z*2))- 14.0
    elif type_surface=='Skeletal_2':
        cx = cos(4*x)
        cy = cos(4*y)
        cz = cos(4*z)
        xo = x - pi/4
        yo = y - pi/4
        zo = z - pi/4
        f =10.0*(sin(xo) * sin(yo) * sin(zo)+ sin(xo) * cos(yo) * cos(zo)+ cos(xo) * sin(yo) * cos(zo)+ cos(xo) * cos(yo) * sin(zo))-  0.7*(cx + cy + cz)- 11.0
    elif type_surface=='Skeletal_3':
        cx = cos(2*x)
        cy = cos(2*y)
        cz = cos(2*z)
        f = 10.0*(cos(x) * sin(y) + cos(y) * sin(z) + cos(z) * sin(x))-  0.5*(cx*cy + cy*cz + cz*cx)- 14.0
    elif type_surface=='Skeletal_4':
        cx = cos(x)
        cy = cos(y)
        cz = cos(z)
        f = 10.0*(cx + cy + cz) -  5.1*(cx*cy + cy*cz + cz*cx) - 14.6
        
    elif type_surface=='Ufunc':
        f = eval(ufunc)
        




    #M=numpy.array(f)
    M=numpy.array(((f > -neg) & (f < pos)) * 1.0)

    #print M.shape, (i+2 for i in M.shape)
    N = numpy.zeros([i+2 for i in M.shape])
    N[1:-1, 1:-1, 1:-1] = M
    return N



class LeftPanel(wx.Panel):
    def __init__(self, parent, id, style):
        wx.Panel.__init__(self, parent, id, style=style)
        self.build_gui()
        self.__bind_events_wx()
        self.__bind_events_pb()
        
        self.Show()

        # funcão para escrever o erro
        log_path = os.path.join('.' , 'vtkoutput.txt')
        fow = vtk.vtkFileOutputWindow()
        fow.SetFileName(log_path)
        ow = vtk.vtkOutputWindow()
        ow.SetInstance(fow)
        #-----------------------
    

    def build_gui(self):


        self.autores_densidade=wx.ComboBox(self, -1, "Schwarz_P", choices=("Schwarz_P",
                                                                            "Schwarz_D","Gyroid","Neovius","iWP",'P_W_Hybrid','Skeletal_1','Skeletal_2','Skeletal_3','Skeletal_4',
                                                                          'Ufunc'),
                                    style=wx.CB_READONLY)

        
        
        self.editfunct = wx.TextCtrl(self, size=(240, -1))
        

       


        self.Reset_scaffold=wx.Button(self,-1,"Rendering")

        self.valor_porosidade_x = FloatSliderText(self, -1, 'X', 6, 0, 100, 1)
        self.valor_porosidade_y = FloatSliderText(self, -1, 'Y', 6, 0, 100, 1)
        self.valor_porosidade_z = FloatSliderText(self, -1, 'Z', 6, 0, 100, 1)
        
        self.valor_spacing_x = FloatSliderText(self, -1, 'X_spacing', 1, 0.01, 1, 0.01)
        self.valor_spacing_y = FloatSliderText(self, -1, 'Y_spacing', 1, 0.01, 1, 0.01)
        self.valor_spacing_z = FloatSliderText(self, -1, 'Z_spacing', 1, 0.01, 1, 0.01)
        self.valor_demensao_buraco1=FloatSliderText(self, -1, ' + Hole size', 0.1, 0.1, 1, 0.1)
        self.valor_demensao_buraco2=FloatSliderText(self, -1, ' - Hole size', 1, 0.1, 1, 0.1)

        self.vporosidade=wx.StaticText(self, -1, "")
        self.Lx=wx.StaticText(self, -1, "")
        self.Ly=wx.StaticText(self, -1, "")
        self.Lz=wx.StaticText(self, -1, "")
        

        b_sizer = wx.BoxSizer(wx.VERTICAL)


        b_sizer.Add(wx.StaticText(self, -1, u"Type of Minimal Surface") , 0, wx.EXPAND | wx.ALL, 10)
        b_sizer.Add(self.autores_densidade, 0)
        
        b_sizer.Add(wx.StaticText(self, -1,"Enter your function (use sin, cos,x,y,z,+,-,*):"), 0, wx.EXPAND | wx.ALL, 10)
        b_sizer.Add(self.editfunct, 0)

        
        b_sizer.Add(wx.StaticText(self, -1, u"Element Number X-direction") , 0, wx.EXPAND | wx.ALL, 10)
        b_sizer.Add(self.valor_porosidade_x, 0, wx.EXPAND)
        b_sizer.Add(wx.StaticText(self, -1, u"Size of spacing between each element in X direction") , 0, wx.EXPAND | wx.ALL, 10)
        b_sizer.Add(self.valor_spacing_x, 0, wx.EXPAND)
        b_sizer.Add(wx.StaticText(self, -1, u"Element Number Y-direction") , 0, wx.EXPAND | wx.ALL, 10)
        b_sizer.Add(self.valor_porosidade_y, 0, wx.EXPAND)
        b_sizer.Add(wx.StaticText(self, -1, u"Size of spacing between each element in Y direction") , 0, wx.EXPAND | wx.ALL, 10)
        b_sizer.Add(self.valor_spacing_y, 0, wx.EXPAND)
        b_sizer.Add(wx.StaticText(self, -1, u"Element Number Z-direction") , 0, wx.EXPAND | wx.ALL, 10)
        b_sizer.Add(self.valor_porosidade_z, 0, wx.EXPAND)
        b_sizer.Add(wx.StaticText(self, -1, u"Size of spacing between each element in Z direction") , 0, wx.EXPAND | wx.ALL, 10)
        b_sizer.Add(self.valor_spacing_z, 0, wx.EXPAND)
        b_sizer.Add(wx.StaticText(self, -1, u" Hole Size") , 0, wx.EXPAND | wx.ALL, 10)
        b_sizer.Add(self.valor_demensao_buraco1, 0, wx.EXPAND)
        b_sizer.Add(self.valor_demensao_buraco2, 0, wx.EXPAND)
        b_sizer.Add(self.Reset_scaffold, 0)
        
        b_sizer.Add(self.vporosidade, 0,wx.EXPAND)
        b_sizer.Add(self.Lx, 0,wx.EXPAND)
        b_sizer.Add(self.Ly, 0,wx.EXPAND)
        b_sizer.Add(self.Lz, 0,wx.EXPAND)

        
        
        hbox=wx.BoxSizer(wx.VERTICAL)
        hbox.Add(b_sizer, 1, wx.EXPAND)


        self.SetSizer(hbox)

    def __bind_events_wx(self):
        self.Reset_scaffold.Bind(wx.EVT_BUTTON,self.renderiza)
        


    def __bind_events_pb(self):
        pub.subscribe(self._show_info, 'show info')

    def renderiza(self, evt):
        tipo=self.autores_densidade.GetValue()
        X=self.valor_porosidade_x.GetValue()
        Y=self.valor_porosidade_y.GetValue()
        Z=self.valor_porosidade_z.GetValue()
        sX=self.valor_spacing_x.GetValue()
        sY=self.valor_spacing_y.GetValue()
        sZ=self.valor_spacing_z.GetValue()
        pos=self.valor_demensao_buraco1.GetValue()
        neg=self.valor_demensao_buraco2.GetValue()

        #funt=raw_input("type a function: p = ",eval(self.editfunct.GetValue()))
        ufunc = self.editfunct.GetValue()
        #print funt
        
        

        

        tam = X, Y, Z
        spacing = sX, sY, sZ
        hole_size= neg,pos

        #print tam, spacing, tipo
        
        pub.sendMessage('recalcula surface', (tipo, tam, spacing,hole_size,
                                              ufunc))
        pub.sendMessage('calcular porosidade')

    def _show_info(self, pubsub_evt):
        p, lx, ly, lz = pubsub_evt.data
        self.vporosidade.SetLabel(u'Porosity: %.5f %%' % p)
        self.Lx.SetLabel(u'Length X-direction: %.5f µm' % lx)
        self.Ly.SetLabel(u'Length Y-direction: %.5f µm' % ly)
        self.Lz.SetLabel(u'Length Z-direction: %.5f µm' % lz)
        


 

class PanelRight(wx.Panel):
    def __init__(self, parent, id, style):
        wx.Panel.__init__(self, parent, id,style=style)

        self.visaofrontal=VisaoFrontal(self, id=-1, style=wx.BORDER_SUNKEN)
        #self.visaotop=VisaoTop(self, id=-1, style=wx.BORDER_SUNKEN)


        vbox=wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.visaofrontal, 1, wx.EXPAND)
        #vbox.Add(self.visaotop, 1, wx.EXPAND)
        


        hbox=wx.BoxSizer()
        hbox.Add(vbox, 1, wx.EXPAND)
        
        self.SetSizer(hbox)



class VisaoFrontal(wx.Panel):
    def __init__(self, parent, id,style):
        wx.Panel.__init__(self, parent, id, style=style)

        self.renderer = vtk.vtkRenderer()
        self.Interactor = wxVTKRenderWindowInteractor(self,-1, size = self.GetSize())
        self.Interactor.GetRenderWindow().AddRenderer(self.renderer)
        self.Interactor.Render()

       

        istyle = vtk.vtkInteractorStyleTrackballCamera()

        self.Interactor.SetInteractorStyle(istyle)

        

        hbox=wx.BoxSizer(wx.VERTICAL)
        hbox.Add(wx.StaticText(self,-1, u'Global Structure of Scaffold'))
        
        
        hbox.Add(self.Interactor,1, wx.EXPAND)
        self.SetSizer(hbox)
        
        
        self.init_actor()
        self.adicionaeixos()        
        self.desenha_surface()
        self.renderer.ResetCamera()

        pub.subscribe(self._desenha_surface, 'recalcula surface')
        pub.subscribe(self._calculo_porosidade, 'calcular porosidade')

    def init_actor(self):
        self.mapper = vtk.vtkPolyDataMapper()
    

        self.SurfaceActor=vtk.vtkActor()
        self.SurfaceActor.SetMapper(self.mapper)
        #ultimo para adionar actor
        #exemplo
        self.renderer.AddActor(self.SurfaceActor)

        self.renderer.ResetCamera()

        self.Interactor.Render()

        

    def _desenha_surface(self, pubsub_evt):
        tipo, tam, spacing,hole_size, ufunc = pubsub_evt.data

        self.desenha_surface(tipo, tam, spacing,hole_size, ufunc)
        

    def desenha_surface(self, tipo='Schwarz_P', tam=None,
                        spacing=None,hole_size=None, ufunc=None):
        if tam is None:
            tam = 6, 6, 6
        if spacing is None:
            spacing = 1.0, 1.0, 1.0
        if hole_size is None:
            hole_size=0.1,0.3
        #print hole_size
            
        M = fun_schwartzP(tipo,tam,spacing,hole_size, ufunc)

        f = h5py.File("/tmp/camboja_ufunc.hdf5", "w")
        f['data'] = M
        f['spacing'] = numpy.array(spacing)
        
        self.M = M
        self.spacing = spacing

       
        image=to_vtk(M,spacing)

        surf=vtk.vtkMarchingCubes()
        surf.SetInputData(image)
        #surf.SetValue(0,0.5)
        surf.SetValue(0,0.02)
        surf.ComputeNormalsOn()
        surf.ComputeGradientsOn()
        surf.Update()

        subdiv= vtk.vtkWindowedSincPolyDataFilter()
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

    def _calculo_porosidade(self, pubsub_evt):
        p = self.calculo_porosidade()
        lx, ly, lz = self.medir_distancia()
        pub.sendMessage('show info', (p, lx, ly, lz))
        
        
        

        

    def calculo_porosidade(self):
        M = self.M
        sx, sy, sz = self.spacing
        z, y, x = M.shape

        vtotal = x*sx * y*sy * z*sz
        #vparede = ((M > -0.1) & (M < 0.1)).sum() * sx*sy*sz
        vparede = M.sum() * sx*sy*sz

        vporos = vtotal - vparede

        return 100.0*vporos/vtotal

        

    def medir_distancia(self):
        M=self.M
        sx, sy, sz = self.spacing
        z, y, x = M.shape

        Lx=x*sx
        Ly=y*sy
        Lz=z*sz
        return Lz,Ly,Lx
        
        


    def adicionaeixos(self):
        axes = vtk.vtkAxesActor()
        self.marker = vtk.vtkOrientationMarkerWidget()
        self.marker.SetInteractor( self.Interactor )
        self.marker.SetOrientationMarker( axes )
        self.marker.SetViewport(0.75,0,1,0.25)
        self.marker.SetEnabled(1)



    def gravar_Modelo_stl(self, path):
        write = vtk.vtkSTLWriter()
        write.SetInputData(self.mapper.GetInput())
        write.SetFileTypeToBinary()
        write.SetFileName(path)
        write.Write()
        write.Update()




class JanelaPrincipal(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(700, 650))

        #----------------------------------

        panel = wx.Panel(self, -1)

        self.currentDirectory = os.getcwd()
        
        self.RightPanel =PanelRight(self, id=-1, style=wx.BORDER_SUNKEN)
        self.LeftPanel =LeftPanel(self, id=-1, style=wx.BORDER_SUNKEN)
        

        hbox=wx.BoxSizer()
        hbox.Add(self.RightPanel, 1, wx.EXPAND)
        hbox.Add(self.LeftPanel, 1, wx.EXPAND)
        

        
        self.SetSizer(hbox)

        #criar menu

        MenuBar=wx.MenuBar()
        menu=wx.Menu()
        
        
        guardar=menu.Append(-1, "&Save ")
        sair=menu.Append(-1, "&Exit")
        MenuBar.Append(menu, "File")

        self.SetMenuBar(MenuBar)

        # tratar os eventos
        self.Bind(wx.EVT_MENU, self.SairPrograma, sair)
        self.Bind(wx.EVT_MENU, self.guardar_stl_format, guardar)


        self.Show()


    def SairPrograma(self,event):
         dial=wx.MessageDialog(None, 'Pretende sair do Programa ?',u'Questão', wx.YES_NO |wx.NO_DEFAULT | wx.ICON_QUESTION)
         ret=dial.ShowModal()
         if ret==wx.ID_YES:
             self.Destroy()



    def guardar_stl_format(self, evt):
        dlg = wx.FileDialog(
            self, message="Save file as ...", 
            defaultDir=self.currentDirectory, 
            defaultFile="", wildcard=wildcard, style=wx.SAVE
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.RightPanel.visaofrontal.gravar_Modelo_stl(path)
        dlg.Destroy()
        



if __name__ == '__main__':
    app = wx.App(0)
    w = JanelaPrincipal(None, -1, 'Interface Scaffold ')
    w.Show()
    app.MainLoop()
