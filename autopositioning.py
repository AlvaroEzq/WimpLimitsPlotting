
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.interpolate import interp1d
import numpy as np

import DataClasses as dc
import WimpPlotClass as wp
import time

REFERENCE_MAX_DISTANCE_VALUE = 1.e6

def auto_fit_fontsize(text, width, height, fig=None, ax=None):
    '''Auto-decrease the fontsize of a text object. 
        Source: jkoal answer to https://stackoverflow.com/questions/5320205/matplotlib-text-dimensions

    Args:
        text (matplotlib.text.Text)
        width (float): allowed width in data coordinates
        height (float): allowed height in data coordinates
    '''
    text_size = getTextWidthHeight(text, fig, ax)
    fits_width = text_size[0] < width if width else True
    fits_height = text_size[1] < height if height else True
    if not all((fits_width, fits_height)):
        text.set_fontsize(text.get_fontsize()-1)
        auto_fit_fontsize(text, width, height, fig, ax)


def getTextWidthHeight(text, fig=None, ax=None, data_coordinate_units=True):
    '''Get the width and height of a text object in data coordinate units
        Source: jkoal answer to https://stackoverflow.com/questions/5320205/matplotlib-text-dimensions

    Args:
        text (matplotlib.text.Text)
    '''
    fig = fig or plt.gcf()
    ax = ax or plt.gca()

    if text.get_rotation()!=0:
        print(f'Warning: text "{text.get_text()}" has rotation={text.get_rotation()}º')
    
    # get text bounding box in figure coordinates
    renderer = fig.canvas.get_renderer()
    #bbox_text = text.get_window_extent(renderer=renderer) #old 123
    bbox_text = text.get_window_extent(renderer=renderer)

    # transform bounding box to data coordinates
    #bbox_text = Bbox(ax.transData.inverted().transform(bbox_text))#old 123¿deprecated?
    if data_coordinate_units:
        bbox_text= bbox_text.transformed(ax.transData.inverted())

    return (bbox_text.width, bbox_text.height)

def insideOneAnother( rectangle1, rectangle2):
    
    '''
    rectangle1 and rectangle2 are a list of the 2 (or 4) points tuple(x,y)
     that define the rectangle.

    If the rectangle has no orientation, 2 oposite points or all 4 points are valid
    If the rectangle has a certain rotation, all 4 vertices points are required
    e.g.:

             ______________________ (x5,y5)            
            |                      |
            |                      |
            |           (x0,y0)    |
            |          /\          |
            |         /  \(x1,y1)  |
            |  (x3,y3)\  /         |
            |          \/(x2,y2)   |
            |______________________| 
          (x4,y4)

          insideOneAnother( [(x0,y0),(x1,y1),(x2,y2),(x3,y3)], [(x4,y4),(x5,y5)] )
    '''

    xlim_1 = ( min([point[0] for point in rectangle1]), max([point[0] for point in rectangle1]) )
    ylim_1 = ( min([point[1] for point in rectangle1]), max([point[1] for point in rectangle1]) )

    
    xlim_2 = ( min([point[0] for point in rectangle2]), max([point[0] for point in rectangle2]) )
    ylim_2 = ( min([point[1] for point in rectangle2]), max([point[1] for point in rectangle2]) )

    #rectagle_1 inside rectangle_2
    if xlim_2[0] < xlim_1[0] and xlim_1[1] < xlim_2[1]:
        if ylim_2[1] > ylim_1[1] and ylim_1[0] > ylim_2[0]:
            return True
    
    #rectagle_2 inside rectangle_1
    if xlim_1[0] < xlim_2[0] and xlim_2[1] < xlim_1[1]:
        if ylim_1[1] > ylim_2[1] and ylim_2[0] > ylim_1[0]:
            return True

    return False

def dataToDisplayCoordinates ( x_data, y_data, ax = None):
    ax = ax or plt.gca()

    xy_display = []
    for x,y in zip(x_data,y_data):
        xy_display.append( (x,y) )
    
    xy_display = ax.transData.transform(xy_display)
    #print(np.array(xy_display))
    if len(xy_display) == 1:
        return xy_display[0] #returns the tuple (x_data,y_data) in display units
    return xy_display #returns the list of tuples (x_data,y_data) in display units

#def displayToDataCoordinates ( xy_display):
    # to be written...

def getMarginDisplayCoordinates(margin, ax=None):
    ax = ax or plt.gca()

    margin_display =  (ax.get_window_extent().width, ax.get_window_extent().height) 
    margin_display = (margin_display[0]*margin, margin_display[1]*margin) 
    print(f'margin {margin_display}')

    return margin_display

def distanceToCurve_single(xy_label, width_label, rotation_label_rad, xy_display, allow_label_intersect_curve=False):

    x_label, y_label = xy_label[0], xy_label[1]

    sum = 0
    n=0
    #print(f'x_label={x_label}\t\twl*cos={width_label*np.cos(rotation_label*3.1416/180)}={width_label}*cos({rotation_label})')
    for xy in xy_display: #runs through the curve (to run along the x-lenght of the label)
        x=xy[0]
        y=xy[1]
        if x_label < x and x < x_label+ width_label*np.cos(rotation_label_rad): #along the x-lenght of the label
            x_ = x-x_label #x coordinate with label as origin
            y_ = x_*np.tan(rotation_label_rad) + y_label #y coordinate of that point of the label
            #print(f'x_label={x_label}\tx={x}\twl*cos={width_label*np.cos(rotation_label)}={width_label}*cos({rotation_label})')
            if y_ < y and (not allow_label_intersect_curve):
                n=0
                print(f'Interseccion en xy= {x_label} {y_label}')
                break
            sum +=  (y_ - y)*(y_ - y)
            n += 1

    return sum/n if n>0 else REFERENCE_MAX_DISTANCE_VALUE


def distanceToCurve ( x_curve, y_curve, rotation_curve, widthHeight_tuple, ax=None, margin = 0.01, use_every=10, allow_label_intersect_curve = False ):

    width_label, height_label = widthHeight_tuple
    if width_label<=0:
        print('WARNING: width_label<=0 is not valid')
        return [np.zeros(len(x_curve[::use_every]))+REFERENCE_MAX_DISTANCE_VALUE], (0,0)
    ax = ax or plt.gca()
    corners_axes = [
            (ax.get_window_extent().x0, ax.get_window_extent().y0),
            (ax.get_window_extent().x1, ax.get_window_extent().y1)
        ]
    print(corners_axes)
    
    xy_display = dataToDisplayCoordinates(x_curve, y_curve, ax)

    margin_display = getMarginDisplayCoordinates(margin, ax)

    distance=[]
    for xy_label,  rotation_label in zip(xy_display[::use_every], rotation_curve[::use_every]): # runs through curve selecting the position and rotation of label
        
        #print(rotation_label)
        rotation_label = rotation_label *3.1416/180 #deg to rad
        x_label=xy_label[0] + margin_display[0]
        y_label=xy_label[1] + margin_display[1]

        corners_label = [
            (x_label,y_label),
            (x_label+width_label*np.cos(rotation_label), y_label + width_label*np.sin(rotation_label)),
            (x_label+height_label*np.cos(rotation_label+np.pi/2), y_label + height_label*np.sin(rotation_label+np.pi/2)),
            (x_label+width_label*np.cos(rotation_label)+height_label*np.cos(rotation_label+np.pi/2),
             y_label + width_label*np.sin(rotation_label)+height_label*np.sin(rotation_label+np.pi/2))
        ]
        
        if not insideOneAnother( corners_label, corners_axes):
            print(corners_label)
            print('Rectangulos fuera')
            distance.append(REFERENCE_MAX_DISTANCE_VALUE)
            continue

        distance.append(distanceToCurve_single((x_label,y_label), width_label, rotation_label, xy_display, False))
    
    try:
        index_min = int(np.where(distance==np.min(distance))[0])
    except (TypeError):
        index_min = 0
    print(f'indexminDentroFunc {index_min}')

    #get the xy position (with margin) of point of minimun distance
    xy_min = ax.transData.inverted().transform( np.array(xy_display[::use_every][index_min])  +np.array(margin_display)    ) 

    return distance, xy_min
   

def calculateRotation(x_curve, y_curve, fig=None ,ax=None, log_xscale=False, log_yscale=False, degree_as_unit=True):
    
    fig = fig or plt.gcf()
    ax = ax or plt.gca()
    
    factor = 1
    if degree_as_unit:
        factor = 180.0/3.14159265

    # --- retrieve the 'abstract' size
    fig_x, fig_y = fig.get_size_inches()

    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    
    # change data to log if used
    if log_xscale:
        x_min, x_max = np.log10((x_min,x_max))
        x_curve = np.log10(x_curve) 
    if log_yscale:
        y_min, y_max = np.log10((y_min,y_max))
        y_curve = np.log10(y_curve) 
    
    rotation = []
    for i in range(len(x_curve)):
        if i < len(x_curve)-1:
            # --- apply the proportional conversion
            Dx = (x_curve[i+1]-x_curve[i]) * fig_x / (x_max - x_min)
            Dy = (y_curve[i+1]-y_curve[i] )* fig_y  / (y_max - y_min)
            # --- convert gaps into an angle
            r = np.arctan( Dy / Dx) *factor
        else:
            r = rotation[-1]  
        rotation.append(r)

    return rotation


def scoreDueToParallelism( wimpPlot):

    print(wimpPlot.DB)
    for i in wimpPlot.DB.values():
        item = i
    print(f'item label: {item.label}')
    text_element = None
    for child in wimpPlot.ax.get_children():
        if type(child) == mpl.text.Text:
            if child.get_text() in [item.label, f'{item.label} ({item.year:.0f})']:
                text_element = child
    
    if text_element == None:
        print(wimpPlot.ax.get_children())
        return 0
    #text_element = w.ax.get_children()[1]
    print(text_element)
    print(text_element.get_text())


    width_label = getTextWidthHeight(text_element, fig = wimpPlot.fig, ax = wimpPlot.ax, data_coordinate_units=False)[0]

    interpolator = interp1d(item.mass, item.xsec, bounds_error=False, fill_value=1e-10)

    dummy = item.xsec[-1]
    stop =   np.min(  [ wimpPlot.ax.transData.transform((item.mass[-1],dummy))[0],
                        wimpPlot.ax.transData.transform((wimpPlot.ax.get_xlim()[1],dummy))[0] ]  ) 

    x_interpolated    = np.logspace( start = np.log10(np.max([item.mass[0],wimpPlot.ax.get_xlim()[0]])),
                                    stop  = np.log10(wimpPlot.ax.transData.inverted().transform((stop, dummy))[0]),
                                    num   = 1000)
    y_interpolated = interpolator(x_interpolated) 
    
    rotation = calculateRotation(x_interpolated, y_interpolated, wimpPlot.fig, wimpPlot.ax, True,True,True)
    wh_label = getTextWidthHeight(text_element, fig = wimpPlot.fig, ax = wimpPlot.ax, data_coordinate_units=False)
    
    #x_interpolated = np.log10(x_interpolated)
    #y_interpolated = np.log10(y_interpolated)
    print(f'text{text_element.get_text()} width= {wh_label[0]}')
    
    usePointsEvery = 50
    #scores = distanceToCurve(x_interpolated, y_interpolated, rotation,width_label, ax=wimpPlot.ax, margin=0.1, use_every=usePointsEvery, allow_label_intersect_curve=False)
    
    for n in range(10):
        print(f'n= {n}')
        rotation = np.array(rotation) + 1 * n #paso de 2 grados (positivo si se pone label encima y negativo si se pone el label debajo)
        scores, xy_min = distanceToCurve(x_interpolated, y_interpolated, rotation,wh_label, ax=wimpPlot.ax, margin=0.01, use_every=usePointsEvery, allow_label_intersect_curve=False)
        print(scores)
        if np.abs(np.min(scores) - REFERENCE_MAX_DISTANCE_VALUE) > 0.001:
            break
        
    #scores = distanceToCurve(x_interpolated, y_interpolated, rotation, text_element.get_size )
    
    fig, axax = plt.subplots()
    axax.scatter(x_interpolated[::usePointsEvery],scores)
    axax.set_yscale('log')
    axax.set_xscale('log')
    fig.savefig('borrar.png')
    

   

    print(f'minimun score: {np.min(scores)}')
    try:
        index_min = int(np.where(scores==np.min(scores))[0])*usePointsEvery
    except (TypeError):
        index_min = 0
    print(f'minimun score indexmin: {index_min}')

    wimpPlot.ax.scatter(x_interpolated[::usePointsEvery], np.array(scores)* 1.e-38)
    #for x,y,r in zip(x_interpolated, y_interpolated, rotation):
    wimpPlot.ax.text( xy_min[0], xy_min[1] ,
                item.label,
                color    = item.label_color,
                fontsize = item.fontsize,
                rotation = rotation[index_min],#*180/3.141,
                rotation_mode = 'anchor')#.set_transform_rotates_text(True)
    if False:
        for x,y,r in zip(x_interpolated[::usePointsEvery], y_interpolated[::usePointsEvery], rotation[::usePointsEvery]):
            wimpPlot.ax.text( x, y ,
                        item.label,
                        color    = item.label_color,
                        fontsize = item.fontsize,
                        rotation = r,#*180/3.141,
                        rotation_mode = 'anchor')#.set_transform_rotates_text(True)

    wimpPlot.showPlot()
    #print(scores)
    return scores
    

    




'''
fig, ax = plt.subplots()
ax.bar(0.5, 0.5, width=0.5)
text = ax.text(0.5, 0.5, 
                "0.5 (50.00 percent)", 
                va='top', ha='center', 
                fontsize=12,
                rotation = 0)
ax.set_xlim(-0.5, 1.5)

print(f'Antes de rotar: {getTextWidthHeight(text, fig, ax)}')
text.set_rotation(45)
print(f'Despues de rotar: {getTextWidthHeight(text, fig, ax)}')
auto_fit_fontsize(text, 0.5, None, fig=fig, ax=ax)
print(getTextWidthHeight(text, fig, ax))

plt.show()
'''
db = {}
#db['TREXDM_E']   = dc.Curve("TREX_escenarios/WimpSensitivity_Ne_0.9446_C_0.0459_H_0.0095_WD_0.3_Vel_232_220_544_Bck_1_Exp_109.5_RecEn_0_2_0.01_EnRange_0.05_1.05_usingQF.dat",
#                               label = 'Bholaquebjhkvhjvj',style = 'projection',  color = 'black', label_xpos= 0.212, label_ypos=9.45e-38)
#db['X1T_MIG']    = dc.Curve("X1T_MIGDAL_2020.dat", style = 'projection', label_xpos=0.75, label_ypos=4.55e-44,label_rotation= -22 )	
#db['CRESSTIII_2019']  = dc.Curve("CRESTIII_2019.txt", label_xpos=0.2, label_ypos=1.35e-35)
#db['PICO_C3F8']  = dc.Curve("PICO_C3F8_2017.dat", label = 'PICO C3F8')
#db['NEWSG']      = dc.Curve("NEWS_G_2018.dat", label_xpos=4, label_ypos=6.5e-39)
#db['DAMIC2020']  = dc.Curve("DAMIC_2020.dat", label_xpos=4.2, label_ypos=1.2e-40, label_rotation= -10)
db['CRESSTII']   = dc.Curve("CRESSTII_2015.dat")
w=wp.WimpPlot(database=db, show_plot=False)
scores= scoreDueToParallelism(w)

print(f'minimun score: {np.min(scores)}')
#print(f'minimun score index: {np.where(scores==np.min(scores))}')
#print(getTextWidthHeight(w.ax.get_children()[1]))