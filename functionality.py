import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import shapely.geometry as sg

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


def getTextWidthHeight(text, ax=None, force_null_rotation=False, data_coordinate_units=True):
    '''Get the width and height of a text object in data coordinate units
        Based on: jkoal answer to https://stackoverflow.com/questions/5320205/matplotlib-text-dimensions

    Args:
        text (matplotlib.text.Text)
        fig is figure where text belongs.
        ax is axis of figure where text belongs
    '''

    ax = ax or plt.gca()
    fig = ax.get_figure()

    if text.get_rotation()!=0:
        if not force_null_rotation:
            print(f'Warning: text "{text.get_text()}" has rotation={text.get_rotation()}º and it is not being forced')

    if force_null_rotation:
        rot = text.get_rotation()
        text.set_rotation(0)

    # get text bounding box in figure coordinates
    renderer = fig.canvas.get_renderer()
    #bbox_text = text.get_window_extent(renderer=renderer) #old 123
    bbox_text = text.get_window_extent(renderer=renderer)

    # transform bounding box to data coordinates
    #bbox_text = Bbox(ax.transData.inverted().transform(bbox_text))#old 123¿deprecated?
    if data_coordinate_units:
        bbox_text= bbox_text.transformed(ax.transData.inverted())

    #set rotation back
    if force_null_rotation: 
        text.set_rotation(rot)

    return (bbox_text.width, bbox_text.height)

def cornersOfRectangle(xy_position, widthHeight_tuple, rotation, rotation_in_deg = False):
    '''
    Get a list of the 4 points (corners) as tuples (x,y) that define the rectangle.
    Args:
        xy_position is the the tuple (x,y) of the position of the bottom left corner of the rectangle when it has rotation = 0
        widthHeight_tuple is the the tuple (width,height) of the rectangle when it has rotation=0
        rotation is the rotation angle from horizontal position and anti-clockwise
        rotation_in_deg is True is rotation arg is in deg units and False if it is in rad units
    '''
    x=xy_position[0]
    y=xy_position[1]

    width = widthHeight_tuple[0]
    height = widthHeight_tuple[1]
    r = rotation
    if rotation_in_deg:
        r = r*3.1416/180

    corners = [
                (x,y),
                (x+width*np.cos(r), y + width*np.sin(r)),
                (x+width*np.cos(r)+height*np.cos(r+np.pi/2),
                y + width*np.sin(r)+height*np.sin(r+np.pi/2)),
                (x+height*np.cos(r+np.pi/2), y + height*np.sin(r+np.pi/2)),
            ]
    return corners
def cornersOfAxis(axis = None):
    ax = axis or plt.gca()
    corners_axes = [
            (ax.get_window_extent().x0, ax.get_window_extent().y0),
            (ax.get_window_extent().x1, ax.get_window_extent().y1)
        ]

    #print(f'Axis corners:\n {corners_axes}')
    return corners_axes

def indexOfMinimun(list_values):
    '''
    Get the index of the element of minimun value of list_values list.
    If several elements met this condition, the minimun index is return
    '''
    try:
        index_min = int(np.where(list_values==np.min(list_values))[0])
    except (TypeError):
        #index_min = None
        index_min = 0
    
    return index_min

def insideOneAnother( rectangle1, rectangle2):
    
    '''
    rectangle1 and rectangle2 are a list of the 2 (or 4) points tuple(x,y)
     that define the rectangle.

    If the rectangle has no rotation, 2 oposite points or all 4 points are valid
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

def amountLabelOffCurve ( xy_label, rotation_label_rad, width_label, xy_display):
    '''
    Get the fraction of the label (rotated rectangle) that has no curve (xy_display) below
    '''
    x_label = xy_label[0]

    x_beginning_display = xy_display[0][0]

    x_end_label = x_label+ width_label*np.cos(rotation_label_rad)
    x_end_display = xy_display[-1][0]

    amount_outside = 0
    # label outside of curve by its ends
    if x_end_display < x_end_label:
        amount_outside += (x_end_label - x_end_display)/(x_end_label-x_label)

    #label outside of curve by its beginning
    if x_label < x_beginning_display:
        amount_outside += (x_beginning_display-x_label)/(x_end_label-x_label)
    
    return amount_outside


def dataToDisplayCoordinates ( x_data, y_data, ax = None):
    '''
    Transform data from data coordinates to display coordinates.
    Args:
        x_data: list of x values
        y_data: list of y values
        ax: mpl.axis.Axis in which this data is plotted
    '''
    ax = ax or plt.gca()

    xy_display = []
    for x,y in zip(x_data,y_data):
        xy_display.append( (x,y) )
    
    xy_display = ax.transData.transform(xy_display)
    #print(np.array(xy_display))
    if len(xy_display) == 1:
        return xy_display[0] #returns the tuple (x_data,y_data) in display units
    return xy_display #returns the list of tuples (x_data,y_data) in display units

def displayToDataCoordinates ( x_display, y_display, ax = None):
    '''
    Transform data from display coordinates to data coordinates.
    Args:
        x_data: list of x values or list of (x,y) tuples if y_data=None
        y_data: list of y values (if y_data = None then x_data must be list of (x,y) tuples)
        ax: mpl.axis.Axis in which this data is plotted
    '''
    ax = ax or plt.gca()

    xy_data = []
    for x,y in zip(x_display,y_display):
        xy_data.append( (x,y) )
    
    xy_data = ax.transData.inverted().transform(xy_data) #ax.transData.transform(xy_display)
    #print(np.array(xy_display))
    if len(xy_data) == 1:
        return xy_data[0] #returns the tuple (x_display,y_display) in display units
    return xy_data #returns the list of tuples (x_display,y_display) in data units


def getMarginDisplayCoordinates(margin, ax=None):
    '''
    Get margin in display coordinates
    Args:
        margin: fraction of axis size to be taken as margin
        ax: mpl.axes.Axes of the plot
    '''
    ax = ax or plt.gca()

    margin_display =  (ax.get_window_extent().width, ax.get_window_extent().height) 
    margin_display = (margin_display[0]*margin, margin_display[1]*margin) 
    #print(f'margin {margin_display}')

    return margin_display

def getPointWithMargin(xy_position, height, margin_tuple, rotation=0, rotation_in_deg=True, below_curve=False ):
    above_or_below = +1
    if below_curve:
        above_or_below = -1
    
    rot_unit_factor = 1
    if rotation_in_deg:
        rot_unit_factor = 3.1416/180

    x_position=xy_position[0] + above_or_below*margin_tuple[0]*2./3
    y_position=xy_position[1] + above_or_below*margin_tuple[1]
    if below_curve: #(x,y) is position of bottom-left corner (when label has null rotation)
        #x_position = x_position - height*np.sin(rotation*rot_unit_factor) 
        y_position = y_position - height*0.67#*np.cos(rotation*rot_unit_factor)

    return (x_position, y_position)

def getRotation(x_curve, y_curve, fig=None ,ax=None, degree_as_unit=True):
    '''
    Get rotation (tangent of slope) along the data curve in display coordinates
    '''
    
    fig = fig or plt.gcf()
    ax = ax or plt.gca()
    if fig is not ax.get_figure():
        print('WARNING: fig is not ax.get_figure() in getRotation function')
        fig = ax.get_figure()

    factor = 1
    if degree_as_unit:
        factor = 180.0/3.14159265

    # --- retrieve the 'abstract' size
    fig_x, fig_y = fig.get_size_inches()

    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    
    # change data to log if used
    if ax.get_xscale() == 'log':
        x_min, x_max = np.log10((x_min,x_max))
        x_curve = np.log10(x_curve) 

    if ax.get_yscale() == 'log':
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
            #print(f'Dx= {Dx}\t= {(x_curve[i+1]-x_curve[i])}\t*\t{fig_x / (x_max - x_min)}')
            #print(f'Dx={Dx}/\tDy= {Dy}\t= {(y_curve[i+1]-y_curve[i])}\t*\t{fig_y / (y_max - y_min)}')
        else:
            r = rotation[-1]  
        rotation.append(r)

    return rotation

'''#Fancy??
def intersectsAnyCurve (wimpPlot, xy_label, rotation_label_rad, widthHeight_tuple, include_text_labels=False):

    text_shape = sg.Polygon(  cornersOfRectangle(xy_label, widthHeight_tuple, rotation_label_rad, rotation_in_deg = False))

    for s in wimpPlot.plotted_shapes:
        if type(s) == sg.linestring.LineString or (type(s) == sg.polygon.Polygon and include_text_labels):
            if s.intersects(text_shape):
                return True
    return False
'''

def intersectsAnyCurve (wimpPlot, xy_label, rotation_label_rad, widthHeight_tuple):

    text_shape = sg.Polygon(  cornersOfRectangle(xy_label, widthHeight_tuple, rotation_label_rad, rotation_in_deg = False))

    for s in wimpPlot.plotted_shapes:
        if type(s) == sg.linestring.LineString:
            if s.intersects(text_shape):
                return True
    return False
def intersectsAnyCurveOrText (wimpPlot, xy_label, rotation_label_rad, widthHeight_tuple):

    text_shape = sg.Polygon(  cornersOfRectangle(xy_label, widthHeight_tuple, rotation_label_rad, rotation_in_deg = False))

    for s in wimpPlot.plotted_shapes:
        if type(s) == sg.linestring.LineString or type(s) == sg.polygon.Polygon:
            if s.intersects(text_shape):
                return True
    return False

def deleteTextLabelFromPlot(wimpPlot, label):
    #label can be the key of wimpPlot.DB or the label str
    #clear the mpl.text.Text of labels in list_labels before autopositioning 
    item = None
    for k,v in wimpPlot.DB.items():
        if k == label or v.label == label:
            item = v
            break
    for child in wimpPlot.ax.get_children():
        if type(child) == mpl.text.Text:
            if child.get_text() == item.label:
                mpl.artist.Artist.remove(child)
    
    return item

def findTextObjectOnAxis(ax = None, text_str='', full_coincidence_of_str=True):
    ax = ax or plt.gca()

    text_element = None
    for child in ax.get_children():
        if type(child) == mpl.text.Text:
            if (child.get_text() == text_str or 
            ((text_str in child.get_text() or child.get_text() in text_str)
              and child.get_text() != ''
              and not full_coincidence_of_str)
            ):
                text_element = child
    return text_element
    

