import matplotlib.pyplot as plt
import numpy as np

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


def getTextWidthHeight(text, fig=None, ax=None, force_null_rotation=False, data_coordinate_units=True):
    '''Get the width and height of a text object in data coordinate units
        Based on: jkoal answer to https://stackoverflow.com/questions/5320205/matplotlib-text-dimensions

    Args:
        text (matplotlib.text.Text)
    '''
    fig = fig or plt.gcf()
    ax = ax or plt.gca()

    if text.get_rotation()!=0:
        print(f'Warning: text "{text.get_text()}" has rotation={text.get_rotation()}º')

    if force_null_rotation:
        if text.get_rotation()!=0:
            print('Calculating width and height with null rotation...')
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
                (x+height*np.cos(r+np.pi/2), y + height*np.sin(r+np.pi/2)),
                (x+width*np.cos(r)+height*np.cos(r+np.pi/2),
                y + width*np.sin(r)+height*np.sin(r+np.pi/2))
            ]
    return corners


def indexOfMinimun(list_values):
    '''
    Get the index of the element of minimun value of list_values list.
    If several elements met this condition, the minimun index is return
    '''
    try:
        index_min = int(np.where(list_values==np.min(list_values))[0])
    except (TypeError):
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

#def displayToDataCoordinates ( xy_display):
    # to be written...

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
    print(f'margin {margin_display}')

    return margin_display


def getRotation(x_curve, y_curve, fig=None ,ax=None, log_xscale=False, log_yscale=False, degree_as_unit=True):
    '''
    Get rotation (tangent of slope) along the data curve in display coordinates
    '''
    
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
