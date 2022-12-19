import numpy as np
from numpy import cos, sin, ogrid, pi

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
    image = vtkImageData()
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


def TPMS(type_surface, tam, spacing, hole_size):

    """
    Definition of the different TPMS.
    """



    tz, ty, tx = tam
    sx, sy, sz = spacing
    pos, neg = hole_size



    z, y, x = ogrid[-tx/2:tx/2:sx, -ty/2:ty/2:sy, -tz/2:tz/2:sz]

    #print type_surface
    if type_surface == 'Schwarz P':
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
        f = cos(x) * cos(y) + cos(y) * cos(z) + cos(z) * cos(x) - cos(x) * cos(y) * cos(z)
    elif type_surface == 'P_W_Hybrid':
        f = 4*(cos(x) * cos(y) + cos(y) * cos(z) + cos(z) * cos(x)) - 3* cos(x) * cos(y) * cos(z) + 2.4
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
        f = 0.5*(sin(2*x) * cy * sz + sin(2*y) * cz * sx + sin(2*z) * cx * sy) - 0.5 * (cxx * cyy + cyy * czz + czz * cxx) + 0.15
    elif type_surface == 'Skeletal 1':
        cx = cos(x)
        cy = cos(y)
        cz = cos(z)
        f = 10.0*(cx*cy + cy*cz + cz*cx) - 5.0*(cos(x*2) + cos(y*2) + cos(z*2)) - 14.0
    elif type_surface == 'Skeletal 2':
        cx = cos(4*x)
        cy = cos(4*y)
        cz = cos(4*z)
        xo = x - pi/4
        yo = y - pi/4
        zo = z - pi/4
        f = 10.0 * (sin(xo) * sin(yo) * sin(zo) + sin(xo) * cos(yo) * cos(zo) + cos(xo) * sin(yo) * cos(zo)+ cos(xo) * cos(yo) * sin(zo)) -  0.7*(cx + cy + cz) - 11.0
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
    M = np.array(((f > -neg) & (f < pos)) * 1.0)

    #print M.shape, (i+2 for i in M.shape)
    N = np.zeros([i+2 for i in M.shape])
    N[1:-1, 1:-1, 1:-1] = M
    return N