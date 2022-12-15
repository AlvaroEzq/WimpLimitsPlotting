import numpy as n
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import matplotlib as mpl

import LabelClass as lc
import functionality as func
PATH_DATA_FOLDER = "./limit_data/"

def readHeaderAndDelimiter(path):
    ## Read in the markup part of the file. The character ':' MUST be part of header lines
    head = []
    delimiter = ','
    previousIsNumber = False
    with open(path) as file:
        for line in file:
            if ':' in line:
                head.append( line.strip().replace(": ",":") )
            else:
                for char in line:
                    if not ( char.isnumeric() or char in ['.','+','-'] or (char=='e' and previousIsNumber) ):
                        delimiter = char
                        break
                    previousIsNumber = char.isnumeric() or char=='.'
                break   
    #print(delimiter)
    return head, delimiter

def is_number(string):
    """ Returns True if string is a number. """
    try:
        float(string)
        return True
    except ValueError:
        return False

class DataClass:
    
    def __init__( self            , 
                  file_name	      ,
                  **options ):

        self.full_file_path = PATH_DATA_FOLDER + file_name
        self.head=[]
        self.style = '-'
        self.source = ''
        self.year   = ''
        self.color  = 'black'
        self.label  = ''
        self.label_xpos  = None
        self.label_ypos  = None
        self.label_rotation = 0 #degrees
        self.label_color = None #None means same color as self.color
        self.Label = None #If None means that label is not plotted

        #self.drawopt = options
        #print('\ninit DataClass')
        #print(self.__dict__)
        ## Read in the markup part of the file. The character ':' MUST be part of header lines
        #print(options)
        self.head, delimiter = readHeaderAndDelimiter(self.full_file_path)
        self.setParametersByHeader()
        self.setParameters(**options)
        
        ## Add more text to label
        if not (self.style=='projection') and is_number(self.year):
            self.label = f'{self.label} ({self.year:.0f})'
            
        if self.label_color == None: #label_color has not been introduced explicitly via file header neither **options
            self.label_color = self.color
            
        ## Read in the data part of the file
        data = n.loadtxt(self.full_file_path ,
            skiprows  = len(self.head)    ,
            delimiter =  delimiter   )
        
        self.mass = data[:,0]
        self.xsec = data[:,1]	#'''
        
        #print(self.__dict__)
        #print('final init DataClass')
    def setParametersByHeader(self):
        for h in self.head:
            parts = h.split(':')
            if not (len(parts)==2):
                continue
            if parts[0].lower() in self.__dict__:
                self.__dict__.__setitem__(parts[0].lower(), float(parts[1]) if is_number(parts[1]) else parts[1])
            else:
                print(f'Warning: {parts[0].lower()} at {self.full_file_path} does not match any class member variable.')

    def setParameters(self, **options):
        for k, v in options.items():
            if k in self.__dict__:
                self.__dict__.__setitem__(k,v)
            else:
                print(f'Warning: parameter {k} is not a valid class member variable.')
    
    def set_Label(self, ax=None, text_mpl_element=None ):
        if ax is None:
            try:
                ax = self.Label.ax
            except (AttributeError):
                print('Warning: ax parameter is not given in first set_Label. Using plt.gca()')
                ax = plt.gca()
                
        if text_mpl_element is None:
            text_mpl_element = func.findTextObjectOnAxis(ax, self.label, full_coincidence_of_str=True)
        
        if text_mpl_element is None:
            self.Label = None
            return None

        wh = func.getTextWidthHeight(text_mpl_element, ax, force_null_rotation=True,
            data_coordinate_units=False)
        lbl = lc.LabelClass((self.label_xpos, self.label_ypos),
              self.label_rotation, wh, axis = ax,
               xy_curve=[(x,y) for x,y in zip(self.mass,self.xsec)],
               xy_in_display_coordinates=False,
                rotation_in_deg=True  
                )
        self.Label = lbl
        
        if text_mpl_element != func.findTextObjectOnAxis(ax, self.label, full_coincidence_of_str=True):
            print(f'Warning: set_Label has been called but the Label is not found in plot axis: {ax}')

        return lbl

    def plot_label(self, ax = None):
        ax = ax or plt.gca()
        
        ## Draw the text
        txt = ax.text( self.label_xpos, self.label_ypos ,
            self.label,
            color    = self.label_color,
            fontsize = self.fontsize,
            rotation = self.label_rotation)
        txt.set_rotation_mode('anchor')#.set_rotation_mode(None) #normal

        self.set_Label(ax, txt) 
        
        return txt 

    def unplot_label(self, ax = None):
        ax = ax or plt.gca()

        txt = func.findTextObjectOnAxis(ax, self.label)
        if txt is not None:
            mpl.artist.Artist.remove(txt)
            self.Label = None
            return True
        return False

class Curve (DataClass):
    def __init__(self, filename, **options):
        self.interpolator = None
        self.linewidth = 1.5
        self.fontsize = 10.
    
        #print('\ninit Curve')
        #print(self.__dict__)
        DataClass.__init__(self, filename, **options)
        #self.setParameters(**options)
        self.interpolator = interp1d(self.mass, self.xsec, bounds_error=False, fill_value=1e-10)
        #print('sigue init Curve')
        #print(self.__dict__)


    def plot( self, fig=None, ax=None,
                    show_label=True
                    ):
        
        fig = fig or plt.gcf()
        ax = ax or fig.gca()
        
        ## Draw the curve
        ax.plot(self.mass, self.xsec,
            linestyle = ( '--' if (self.style=='projection') else self.style),
            linewidth = self.linewidth,
            color     = self.color,
            label     = self.label,
            zorder    = 3)
        if (show_label and self.label_xpos!=None and self.label_ypos!=None ):
            self.plot_label(ax)
       
    

class Contour (DataClass):
    def __init__(self, filename, **options):
        self.linewidth = 1
        self.fontsize = 10.
        self.alpha = 0.5

        #print('\ninit Curve')
        #print(self.__dict__)
        DataClass.__init__(self, filename, **options)
        #self.setParameters(**options)
        if self.label_color == None: #label_color has not been introduced explicitly via file header neither **options
            self.label_color = self.color
        #print('sigue init Curve')
        #print(self.__dict__)


    def plot( self, fig, ax=None,
                    show_label=True,
                    style=None):
        ax = ax or fig.gca()

        ## Draw the blob
        ax.fill(self.mass, self.xsec, 
            color = self.color,
            linewidth = self.linewidth, 
            alpha = self.alpha, 
            label = self.label,
            zorder    = 3)

        ## Draw the text
        if (show_label and self.label_xpos!=None and self.label_ypos!=None ):
            self.plot_label(ax)



class NeutrinoFog (DataClass):
    def __init__(self, filename, **options):
        self.linewidth = 1.5
        self.fontsize = 10.
        self.alpha = 0.5

        #print('\ninit Curve')
        #print(self.__dict__)
        DataClass.__init__(self, filename, **options)
        
        if self.label_color == None: #label_color has not been introduced explicitly via file header neither **options
            self.label_color = self.color
        #print('sigue init Curve')
        #print(self.__dict__)

    def plot( self, fig, ax=None,
                    show_label=True,
                    style=None):
        ax = ax or fig.gca()

        ## Draw the curve
        ax.plot(self.mass, self.xsec,
            linestyle = '--',
            linewidth = 2.5,
            color     = self.color,
            label     = self.label,
            zorder    = 2)

        bottom = n.min([1e-55, n.min(self.xsec)/1e-5])
        ax.fill_between(self.mass, self.xsec, bottom,
            color  = self.color,
            zorder = 2,
            alpha  = self.alpha, 
            lw     = 0)

        ## Draw the text
        if (show_label and self.label_xpos!=None and self.label_ypos!=None ):
            self.plot_label(ax)



'''
#d = DataClass("CDEX10_2018.dat", year = 2030)
c = Curve("CDEX10_2018.dat", year=2040, solo_curva = 2, fontsize=20)
c.setParameters(solo_curva=3)
print(c.__dict__)
'''