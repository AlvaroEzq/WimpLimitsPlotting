
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.interpolate import interp1d
import numpy as np
import shapely.geometry as sg

import LabelClass as lc
import DataClasses as dc
import WimpPlotClass as wp
import functionality as func

REFERENCE_MAX_DISTANCE_VALUE = 1.e6

def distanceToOtherCurves(wimpPlot, xy_label, rotation_label_rad, widthHeight_tuple):

    text_shape = sg.Polygon(  func.cornersOfRectangle(xy_label, widthHeight_tuple, rotation_label_rad, rotation_in_deg = False))

    distance, n = 0, 0
    for s in wimpPlot.plotted_shapes:
        if type(s) == sg.linestring.LineString:
            d = text_shape.distance(s)
            #if d == 0:
            #    distance = 0
            #    n = 1
            #    break
            distance += d
            n += 1
    return d/n
    
def intersectsAnyCurve (wimpPlot, xy_label, rotation_label_rad, widthHeight_tuple):

    text_shape = sg.Polygon(  func.cornersOfRectangle(xy_label, widthHeight_tuple, rotation_label_rad, rotation_in_deg = False))

    for s in wimpPlot.plotted_shapes:
        if type(s) == sg.linestring.LineString:
            if s.intersects(text_shape):
                return True
    return False

def distanceToCurve_single(text_label, xy_display, margin_display=(0,0), allow_label_intersect_curve=False):

    x_label, y_label = text_label.xy

    sum = 0
    n=0
    #print(f'x_label={x_label}\t\twl*cos={width_label*np.cos(rotation_label*3.1416/180)}={width_label}*cos({rotation_label})')
    for xy in xy_display: #runs through the curve (to run along the x-lenght of the label)
        x=xy[0] + margin_display[0]
        y=xy[1] + margin_display[1]
        if x_label < x and x < x_label+ text_label.width*np.cos(text_label.rotation_rad): #along the x-lenght of the label
            x_ = x-x_label #x coordinate with label as origin
            y_ = x_*np.tan(text_label.rotation_rad) + y_label #y coordinate of that point of the label
            #print(f'x_label={x_label}\tx={x}\twl*cos={width_label*np.cos(rotation_label)}={width_label}*cos({rotation_label})')
            if y_ < y and (not allow_label_intersect_curve):
                n=0
                #print(f'Interseccion en xy= {x_label} {y_label}')
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
    
    xy_display = func.dataToDisplayCoordinates(x_curve, y_curve, ax)

    margin_display = func.getMarginDisplayCoordinates(margin, ax)

    distance_best, rotation_best = [], []
    for xy_label,  rotation_label in zip(xy_display[::use_every], rotation_curve[::use_every]): # runs through curve selecting the position and rotation of label
        
        x_label=xy_label[0] + margin_display[0]
        y_label=xy_label[1] + margin_display[1]
        rotation_label = rotation_label 

        text_label = lc.LabelClass( (x_label,y_label), rotation_label, widthHeight_tuple)

        dist, rot = [], []
        for n in range(10):
            r = (rotation_label + 1.0*n) #*3.1416/180 #deg to rad
            text_label.set_rotation(r, unit_is_degrees=True)

            corners_label = text_label.make_corners()
            
            if not func.insideOneAnother( corners_label, corners_axes):
                #print(corners_label)
                #print('Rectangulos fuera')
                dist.append(REFERENCE_MAX_DISTANCE_VALUE)
                rot.append(r)
                continue

            if text_label.amountOffCurve(xy_display) > 2./3:
                dist.append(REFERENCE_MAX_DISTANCE_VALUE)
                rot.append(r)
                continue

            dist.append(distanceToCurve_single(text_label, xy_display,margin_display, allow_label_intersect_curve = False))
            rot.append(r)
        distance_best.append( np.min(dist) )
        rotation_best.append( rot[func.indexOfMinimun(dist)] )
    
    index_min = func.indexOfMinimun(distance_best)

    #get the xy position (with margin) and rotation of point of minimun distance
    xy_min = ax.transData.inverted().transform( np.array(xy_display[::use_every][index_min])  +np.array(margin_display)    ) 
    rotation  = rotation_best[index_min] #*180./3.1416 #rad to deg 
    return xy_min, rotation

def bestLabelDueToParallelism( wimpPlot, curve_data = None ):

    #print(wimpPlot.DB)
    if curve_data == None:
        item = wimpPlot.DB.values()[len(wimpPlot.DB)]
    for i in wimpPlot.DB.values():
        if i == curve_data:
            item = i
            break
    

    # Search the text element (mpl.text.Text) that corresponds to curve_data label
    text_element = None
    for child in wimpPlot.ax.get_children():
        if type(child) == mpl.text.Text:
            if child.get_text() == item.label or  f'{item.label} (' in child.get_text():
                text_element = child
    
    if text_element == None:
        print(wimpPlot.ax.get_children())
        return None, None
    
    print(text_element)
    print(f'Autopositioning label: "{text_element.get_text()}" from')

    interpolator = interp1d(item.mass, item.xsec, bounds_error=False, fill_value=1e-10)

    dummy = item.xsec[-1]
    stop =   np.min(  [ wimpPlot.ax.transData.transform((item.mass[-1],dummy))[0],
                        wimpPlot.ax.transData.transform((wimpPlot.ax.get_xlim()[1],dummy))[0] ]  ) 

    x_interpolated    = np.logspace( start = np.log10(np.max([item.mass[0],wimpPlot.ax.get_xlim()[0]])),
                                    stop  = np.log10(wimpPlot.ax.transData.inverted().transform((stop, dummy))[0]),
                                    num   = 1000)
    y_interpolated = interpolator(x_interpolated) 
    
    rotation = func.getRotation(x_interpolated, y_interpolated, wimpPlot.fig, wimpPlot.ax, True,True,True)
    wh_label = func.getTextWidthHeight(text_element, fig = wimpPlot.fig, ax = wimpPlot.ax, force_null_rotation=True, data_coordinate_units=False)
    
    usePointsEvery = 50
    
    xy_min, rot = distanceToCurve(x_interpolated, y_interpolated, rotation,wh_label, ax=wimpPlot.ax, margin=0.01, use_every=usePointsEvery, allow_label_intersect_curve=False)
    
    '''
    wimpPlot.ax.text( xy_min[0], xy_min[1] ,
                item.label,
                color    = item.label_color,
                fontsize = item.fontsize,
                rotation = rot,#*180/3.141,
                rotation_mode = 'anchor')#.set_transform_rotates_text(True)
    if False:
        for x,y,r in zip(x_interpolated[::usePointsEvery], y_interpolated[::usePointsEvery], rotation[::usePointsEvery]):
            wimpPlot.ax.text( x, y ,
                        item.label,
                        color    = item.label_color,
                        fontsize = item.fontsize,
                        rotation = r,#*180/3.141,
                        rotation_mode = 'anchor')#.set_transform_rotates_text(True)
    '''
    for child in wimpPlot.ax.get_children():
        if child == text_element:
            child.set_position(xy_min)
            child.set_rotation(rot)

    return xy_min, rot

db = {}
db['TREXDM_E']   = dc.Curve("TREX_escenarios/WimpSensitivity_Ne_0.9446_C_0.0459_H_0.0095_WD_0.3_Vel_232_220_544_Bck_1_Exp_109.5_RecEn_0_2_0.01_EnRange_0.05_1.05_usingQF.dat",
                               label = 'Bholaquebjhkvhjvj',style = 'projection',  color = 'black', label_xpos= 0.212, label_ypos=9.45e-38)
db['X1T_MIG']    = dc.Curve("X1T_MIGDAL_2020.dat", style = 'projection', label_xpos=0.75, label_ypos=4.55e-44,label_rotation= -22 )	
db['CRESSTIII_2019']  = dc.Curve("CRESTIII_2019.txt", label_xpos=0.2, label_ypos=1.35e-35)
db['PICO_C3F8']  = dc.Curve("PICO_C3F8_2017.dat", label = 'PICO C3F8')
db['NEWSG']      = dc.Curve("NEWS_G_2018.dat", label_xpos=4, label_ypos=6.5e-39)
db['DAMIC2020']  = dc.Curve("DAMIC_2020.dat", label_xpos=4.2, label_ypos=1.2e-40, label_rotation= -10)
#db['CRESSTII']   = dc.Curve("CRESSTII_2015.dat")
w=wp.WimpPlot(database=db, show_plot=False)
for i in w.DB.values():
    (i.label_xpos, i.label_ypos), i.label_rotation = bestLabelDueToParallelism(w, i)

w.showPlot()
#print(getTextWidthHeight(w.ax.get_children()[1]))