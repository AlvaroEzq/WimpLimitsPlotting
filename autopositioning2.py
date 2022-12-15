
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import shapely.geometry as sg
from random import shuffle
from scipy.interpolate import interp1d

import LabelClass as lc
import DataClasses as dc
import WimpPlotClass as wp
import functionality as func

REFERENCE_MAX_DISTANCE_VALUE = 1.e6
MANUAL_DEBUG_PRINT = False

def distanceToOtherCurves(wimpPlot, text_label):

    '''
    text_label is LabelClass
    '''

    text_shape = text_label.polygon #sg.Polygon(  func.cornersOfRectangle(xy_label, widthHeight_tuple, rotation_label_rad, rotation_in_deg = False))

    distance, n = 0, 0
    for s in wimpPlot.plotted_shapes:
        if type(s) in [sg.linestring.LineString, sg.polygon.Polygon]:
            d = text_shape.distance(s)
            #print(d)
            #if d == 0:
            #    distance = 0
            #    n = 1
            #    break
            distance += d
            n += 1
    #print(n)
    return distance/n
    
def distance2ToOtherCurves(wimpPlot, text_label):

    '''
    text_label is LabelClass
    '''

    text_shape = text_label.polygon #sg.Polygon(  func.cornersOfRectangle(xy_label, widthHeight_tuple, rotation_label_rad, rotation_in_deg = False))
    #print((text_label.polygon.representative_point().x,text_label.polygon.representative_point().y ))
    normFactorOC = wimpPlot.ax.get_window_extent()
    normFactorOC = ((normFactorOC.x0-normFactorOC.x1)**2 +
             (normFactorOC.y0-normFactorOC.y1)**2)*2
            
    distance, n = 0, 0
    for s in wimpPlot.plotted_shapes:
        if type(s) in [sg.linestring.LineString, sg.polygon.Polygon]:
            d = text_shape.distance(s)
            #print(d)
            #distance += d*d
            distance += np.exp(-d*d/normFactorOC)
            #distance += 1/(d*d/normFactorOC)
            #print(f'd {d}\tdist+= {np.exp(-d*d/normFactorOC)} ')
            n += 1
            
    #print(n)
    return distance/n

def distanceToCurveAndCurves_single(wimpPlot, text_label, xy_display, margin_display=(0,0), below_curve=False, only_other_curves = False, normalize=True, allow_label_intersect_curve=False):
    '''
    text_label is LabelClass
    '''
    x_label, y_label = text_label.get_xy_position(display_coordinates=True)

    above_or_below = +1
    if below_curve:
        above_or_below = -1

    normFactor = 1
    normFactorOC = 1
    if normalize:
        normFactor = max(text_label.width, text_label.height)**2
        normFactorOC = wimpPlot.ax.get_window_extent()
        normFactorOC = (normFactorOC.x0-normFactorOC.x1)**2 + (normFactorOC.y0-normFactorOC.y1)**2
        
    sum1 = 0
    n=0
    #print(f'x_label={x_label}\t\twl*cos={width_label*np.cos(rotation_label*3.1416/180)}={width_label}*cos({rotation_label})')
    sum2 = distance2ToOtherCurves(wimpPlot, text_label)
    for xy in xy_display: #runs through the curve (to run along the x-lenght of the label)
        x, y = func.getPointWithMargin(xy, text_label.height, margin_display, 
            rotation=text_label.rotation_rad, 
            rotation_in_deg=True, below_curve=below_curve)
        
        if x_label < x and x < x_label+ text_label.width*np.cos(text_label.rotation_rad): #along the x-lenght of the label
            x_ = x-x_label #x coordinate with label as origin
            y_ = x_*np.tan(text_label.rotation_rad) + y_label #y coordinate of that point of the label
            #print(f'x_label={x_label}\tx={x}\twl*cos={width_label*np.cos(rotation_label)}={width_label}*cos({rotation_label})')
            if not allow_label_intersect_curve:
                if ((y_ < y) and not below_curve):
                    n=0
                    #print(f'Interseccion en xy= {x_label} {y_label}')
                    break
                if ((y_ > y) and below_curve):
                    n=0
                    #print(f'Interseccion en xy= {x_label} {y_label}')
                    break
            if not only_other_curves:
                sum1 +=  (y_ - y)*(y_ - y) /normFactor
            else:
                sum1=5./100*sum2
            #sum2 += normFactorOC/distance2ToOtherCurves(wimpPlot, text_label)
            #sum2 += np.exp(-distance2ToOtherCurves(wimpPlot, text_label)/normFactorOC)*3 #last ad hoc factor is for weightening purposes
            n += 1
    if MANUAL_DEBUG_PRINT:
        if n>0:
            print(f'xy_label= {text_label.xy}  \trot={text_label.rotation_deg:.3f}\tsum= {(sum1/n+sum2)/2.:.4f}\tdii= {sum1/n/(sum1/n+sum2)*100:.1f}%')
        else:
            print(f'xy_label= {text_label.xy}  \trot={text_label.rotation_deg:.3f}\tsum= {REFERENCE_MAX_DISTANCE_VALUE}')
            
    return (sum1/n+sum2)/2.  if n>0 else REFERENCE_MAX_DISTANCE_VALUE
    

def distanceToCurveAndCurves (wimpPlot, x_curve, y_curve, widthHeight_tuple, ax=None, below_curve=False, margin = 0.01, use_every=10, allow_label_intersect_curve = False ):

    width_label, height_label = widthHeight_tuple
    if width_label<=0:
        print('WARNING: width_label<=0 is not valid')
        return [np.zeros(len(x_curve[::use_every]))+REFERENCE_MAX_DISTANCE_VALUE], (0,0)

    rotation_curve = func.getRotation(x_curve, y_curve, fig= wimpPlot.fig,
                                     ax= wimpPlot.ax, degree_as_unit=True)
    

    corners_axis = func.cornersOfAxis(ax)
    
    xy_display = func.dataToDisplayCoordinates(x_curve, y_curve, ax)

    margin_display = func.getMarginDisplayCoordinates(margin, ax)

    distance_best, rotation_best = [], []
    for xy_label,  rotation_label in zip(xy_display[::use_every], rotation_curve[::use_every]): # runs through curve selecting the position and rotation of label
        
        x_label, y_label = func.getPointWithMargin(xy_label, height_label, 
                margin_display, rotation= rotation_label, 
                rotation_in_deg=True, below_curve=below_curve)
    
        dist, rot = [], []
        Nmax = 10
        for n in range(Nmax):
            
            if n < Nmax/3.:
                r = (rotation_label -2 + 0.5*n) if not below_curve else (rotation_label +2 - 0.5*n) #*3.1416/180 #deg to rad
            elif n < Nmax*2./3:
                r = (rotation_label -2 + 1*n) if not below_curve else (rotation_label +2 - 1*n) #*3.1416/180 #deg to rad
            else:
                r = (rotation_label -2 + 5*n) if not below_curve else (rotation_label +2 - 5*n)#*3.1416/180 #deg to rad
            if n == 0:
                r = 0
                x_label = x_label - width_label - margin_display[0] if below_curve else x_label
                only_other_curves = True
            else:
                only_other_curves = False
            text_label = lc.LabelClass( (x_label,y_label), r, widthHeight_tuple, rotation_in_deg=True, xy_in_display_coordinates=True)
            #text_label.set_rotation(r, unit_is_degrees=True)

            corners_label = text_label.make_corners()
            
            if (not text_label.inside(corners_axis, display_coordinates=True)
            #not func.insideOneAnother( corners_label, corners_axis)
            or text_label.amountOffCurve(xy_display, display_coordinates=True) > 2./3
            or text_label.intersectsAnyCurveOrText(wimpPlot)
            ):
                if MANUAL_DEBUG_PRINT:
                    print(f'xy_label= {text_label.xy}  \trot={text_label.rotation_deg:.3f}\tfueraAx={not text_label.inside(corners_axis, display_coordinates=True)}\taOff={text_label.amountOffCurve(xy_display, display_coordinates=True):.2f}\tint={text_label.intersectsAnyCurveOrText(wimpPlot)}')
                dist.append(REFERENCE_MAX_DISTANCE_VALUE)
                rot.append(r)
                continue
            
           

            dist.append(distanceToCurveAndCurves_single(wimpPlot,text_label,
                  xy_display,margin_display, below_curve = below_curve, 
                  only_other_curves = only_other_curves, 
                  allow_label_intersect_curve = False)
                  )
            rot.append(r)
        '''
        wimpPlot.ax.text( func.displayToDataCoordinates([x_label],[y_label], wimpPlot.ax)[0],
             func.displayToDataCoordinates([x_label],[y_label], wimpPlot.ax)[1],
                        str(dist[-1]),
                        fontsize=5,
                        rotation = rot[-1],#*180/3.141,
                        rotation_mode = 'anchor')#.set_transform_rotates_text(True)
        '''
        distance_best.append( np.min(dist) )
        rotation_best.append( rot[func.indexOfMinimun(dist)] )
        '''
        wimpPlot.ax.text( func.displayToDataCoordinates([x_label],[y_label], wimpPlot.ax)[0],
             func.displayToDataCoordinates([x_label],[y_label], wimpPlot.ax)[1],
                        str(distanc[-1]),
                        fontsize=5,
                        rotation = rot[-1],#*180/3.141,
                        rotation_mode = 'anchor')#.set_transform_rotates_text(True)
        '''

    '''
    wimpPlot.ax.text( xy_min[0], xy_min[1] ,
                item.label,
                color    = item.label_color,
                fontsize = item.fontsize,
                rotation = rot,#*180/3.141,
                rotation_mode = 'anchor')#.set_transform_rotates_text(True)
    
    if True:
        for x,y,r in zip(x_interpolated[::usePointsEvery], y_interpolated[::usePointsEvery], rotation[::usePointsEvery]):
            wimpPlot.ax.text( x, y ,
                        item.label,
                        color    = item.label_color,
                        fontsize = item.fontsize,
                        rotation = r,#*180/3.141,
                        rotation_mode = 'anchor')#.set_transform_rotates_text(True)
    '''


    index_min = func.indexOfMinimun(distance_best)

    #print(distance_best)

    #get the xy position (with margin) and rotation of point of minimun distance
    rotation  = rotation_best[index_min] #*180./3.1416 #rad to deg 
    xy_min = ax.transData.inverted().transform( func.getPointWithMargin(
        np.array(xy_display[::use_every][index_min]), height_label,  
        margin_display, rotation = rotation, rotation_in_deg=True, 
        below_curve=below_curve )
        )
    
    label_min = lc.LabelClass( xy_min, rotation, widthHeight_tuple, rotation_in_deg=True )
    print(f'Label_min: xy= {label_min.get_xy_position(False)}\trot= {label_min.get_rotation(False):.1f} º')
    print(f'distance_best = {distance_best}')
    print(f'distance_best = {distance_best[index_min]:.5f}')

    return label_min, distance_best[index_min]

def bestLabel ( wimpPlot, curve_data = None, below_curve=False, update=True ):
     #print(wimpPlot.DB)
    
    #----PARAMETERS----
    margin = 0.01
    usePointsEvery = 50
    #------------------
    
    
    if curve_data is None:
        item = wimpPlot.DB.values()[len(wimpPlot.DB)]
        item_key = wimpPlot.DB.keys()[len(wimpPlot.DB)]
    for k,v in wimpPlot.DB.items():
        if k == curve_data or v == curve_data:
            item = v
            item_key = k
            break
    '''
    # Search the text element (mpl.text.Text) that corresponds to curve_data label. If it is not found, plot it
    func.deleteTextLabelFromPlot(wimpPlot, item_key)
    text_element = None
    while (text_element == None):
        func.findTextObjectOnAxis(wimpPlot.ax, item.label, full_coincidence_of_str=True)
        if text_element == None:
            item.plot_label(wimpPlot.ax)
    w.setPlottedObjects(True)
    '''
    item.unplot_label(wimpPlot.ax)
    text_element = item.plot_label(wimpPlot.ax)
    print(f'\nAutopositioning label: "{text_element.get_text()}" from initial position (x,y)={text_element.get_position()} with fs= {text_element.get_fontsize()}')

    

    dummy = item.xsec[-1]
    stop =   np.min(  [ wimpPlot.ax.transData.transform((item.mass[-1],dummy))[0],
                        wimpPlot.ax.transData.transform((wimpPlot.ax.get_xlim()[1],dummy))[0] ]  ) 

    x_interp    = np.logspace( start = np.log10(np.max([item.mass[0],wimpPlot.ax.get_xlim()[0]])),
                                    stop  = np.log10(wimpPlot.ax.transData.inverted().transform((stop, dummy))[0]),
                                    num   = 1000)
    interpolator = interp1d(item.mass, item.xsec, bounds_error=False, fill_value=1e-10)
    y_interp = interpolator(x_interp) 
    
    #remove points where label gets pushed out of plot axis
    x_interpolated, y_interpolated = [], []
    for x, y in zip(x_interp,y_interp):
        xy_display = func.dataToDisplayCoordinates([x],[y], wimpPlot.ax)
        xy_label = func.getPointWithMargin(xy_display, 15., 
                func.getMarginDisplayCoordinates(margin, wimpPlot.ax), 
                below_curve=below_curve)
        text_label = lc.LabelClass.from_string(item.label, xy_label, 0,
                 item.fontsize, xy_in_display_coordinates=True, 
                 axis=wimpPlot.ax)
        if text_label.inside(func.cornersOfAxis(wimpPlot.ax), display_coordinates=True):
            x_interpolated.append(x)
            y_interpolated.append(y)
    '''
    print(f'Primer punto:\t( {x_interpolated[0]}, {y_interpolated[0]} )')
    print(f'Ultimo punto:\t( {x_interpolated[-1]}, {y_interpolated[-1]} )')
    '''     
    #wh_label = func.getTextWidthHeight(text_element,  ax = wimpPlot.ax, force_null_rotation=True, data_coordinate_units=False)
   
    '''print(x_interpolated[::usePointsEvery])
    print(y_interpolated[::usePointsEvery])'''
    '''
    wimpPlot.ax.scatter(x_interpolated[::usePointsEvery], y_interpolated[::usePointsEvery],
        color = item.color)
    '''
    
    label_min, distance = distanceToCurveAndCurves(wimpPlot, x_interpolated,
            y_interpolated, (item.Label.width,item.Label.height),
            ax=wimpPlot.ax, below_curve = below_curve, margin=margin,
            use_every = usePointsEvery, allow_label_intersect_curve = False)

    
    if update:
        item.label_xpos = label_min.xy[0]
        item.label_ypos = label_min.xy[1]
        item.label_rotation = label_min.rotation_deg
        item.unplot_label(wimpPlot.ax)
        item.plot_label(wimpPlot.ax)

    return distance


def autopositionLabels(wimpPlot, list_labels = None, save_plotname=None, number_attempts = 1 ):
    if list_labels is None:
        list_labels=[]
        for k in wimpPlot.DB.keys():
            if type(wimpPlot.DB[k])!= dc.Contour:
                list_labels.append(k)

    print(f'List_labels: {list_labels}')
    #clear the mpl.text.Text of labels in list_labels before autopositioning 

    for l in list_labels:
        wimpPlot.DB[l].unplot_label(wimpPlot.ax)
    
    for i in range(number_attempts):
        #shuffle(list_labels)
        for l in list_labels:
            
            d = REFERENCE_MAX_DISTANCE_VALUE
            while d == REFERENCE_MAX_DISTANCE_VALUE and wimpPlot.DB[l].fontsize > 8:
                d = bestLabel(wimpPlot, wimpPlot.DB[l], below_curve=False, update=True)
                '''
                if d > bestLabel(wimpPlot, wimpPlot.DB[l], below_curve=True, update=False):
                    bestLabel(wimpPlot, wimpPlot.DB[l], below_curve=True, update=True)
'''
                if d == REFERENCE_MAX_DISTANCE_VALUE:
                    wimpPlot.DB[l].fontsize = wimpPlot.DB[l].fontsize - 1
            
            wimpPlot.setPlottedObjects(True)
            if save_plotname is not None:
                wimpPlot.savePlot(f'{save_plotname}_{i}')
            #wimpPlot.showPlot()
      

db = {}
#db['TREXDM_E']   = dc.Curve("TREX_escenarios/WimpSensitivity_Ne_0.9446_C_0.0459_H_0.0095_WD_0.3_Vel_232_220_544_Bck_1_Exp_109.5_RecEn_0_2_0.01_EnRange_0.05_1.05_usingQF.dat",
#                               label = 'B escenario',style = 'projection',  color = 'black', label_xpos= 0.212, label_ypos=9.45e-38)
db['CRESSTIII_2019']  = dc.Curve("CRESTIII_2019.txt", label_xpos=0.2, label_ypos=1.35e-35)
db['X1T_MIG']    = dc.Curve("X1T_MIGDAL_2020.dat", style = 'projection', label_xpos=0.75, label_ypos=4.55e-44,label_rotation= -22 )	
db['PICO_C3F8']  = dc.Curve("PICO_C3F8_2017.dat", label = 'PICO C3F8')
db['NEWSG']      = dc.Curve("NEWS_G_2018.dat", label_xpos=4, label_ypos=6.5e-39)
db['DAMIC2020']  = dc.Curve("DAMIC_2020.dat", label_xpos=4.2, label_ypos=1.2e-40, label_rotation= -10)
db['CRESSTII']   = dc.Curve("CRESSTII_2015.dat")
w=wp.WimpPlot(database=None, show_plot=False)
'''
for i in w.DB.values():
    bestLabel(w, i)
    w.setPlottedObjects(True)
    print('\n')
w.setPlottedObjects(True)
'''
autopositionLabels(w)

w.showPlot()
#print(getTextWidthHeight(w.ax.get_children()[1]))