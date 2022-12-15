
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import shapely.geometry as sg

import DataClasses as dc
from buildDataBase import buildDataBase
import functionality as func

PATH_FIGURE_FOLDER = './plots/'
PREVIOUS_CLICK = None

class WimpPlot:

    def __init__(self,
                x_limits=(0.1,20),
                y_limits=(1e-46, 1e-34),
                database = None,
                add_curves = True,
                show_excludedregion = True,
                show_plot = True,
                save_plotname = None
                ):
        
        self.x_limits=x_limits #tuple (x_min, x_max)
        self.y_limits=y_limits #tuple (y_min, y_max)
        self.DB = database #dictionary containing DataClass objects
        self.plotted_shapes=[] #for label autopositioning purposes

        ## ===== Define the plotting style options =====

        # plt.rcParams['axes.grid'] = True ## Turn the grid on for all plots
        plt.rcParams.update({'font.size': 18}) ## Set the global font size for the plots
        plt.rc('text', usetex=True)  ## Use the LaTeX engine to draw text
        plt.rc('font', family='serif')  ## Select the typeface

        self.fig, self.ax = plt.subplots(1,1, figsize = (9,7))

        ## Set the plot scales
        self.ax.set_xscale('log')
        self.ax.set_yscale('log')

        ## Set the plot limits
        self.ax.set_xlim(x_limits)
        self.ax.set_ylim(y_limits)

        ## Set the axis labels
        #ax0.set_xlabel('DM mass [GeV/c$^{2}$]')
        self.ax.set_xlabel('WIMP mass [GeV/c$^{2}$]')
        self.ax.set_ylabel(r'SI WIMP-nucleon cross section $\sigma_{\chi n}^\mathrm{SI}$ [cm$^{2}$]')

        ## Turn on some extra tick marks
        self.ax.xaxis.set_tick_params(top = 'True', which='minor')
        self.ax.xaxis.set_tick_params(top = 'True', which='major')
        self.ax.yaxis.set_tick_params(top = 'True', which='major')

        if self.DB == None:
            self.DB = buildDataBase()

        if add_curves:
            self.addCurves(show_excludedregion)

        self.setPlottedObjects(reset = True)
        
        if show_plot:
            self.showPlot()

        if type(save_plotname)==str:
            if len(save_plotname) > 0:
                print('saving...')
                self.savePlot(save_plotname)
                print('done')

    def getExcludedRegion(self):    
        ## -------- CALCULATE THE EXCLUDED PARAMETER SPACE -------- 
        x_val_arr     = np.logspace( start = np.log10(self.x_limits[0]),
                                    stop  = np.log10(self.x_limits[1]),
                                    num   = 1000)

        interp_array=[]
        for item in self.DB.values():
            if type(item) != dc.Curve: #use only curves
                continue
            if item.style not in ['-', 'solid']: #exclude projections
                continue
            interp_array.append(  item.interpolator(np.power(x_val_arr,1)) )
        if len(interp_array)<=0:
            print('Warning: no available curves (not projection) for computing excluded region.')
            return (x_val_arr, [])
        exp_upper_lim  = np.min(interp_array, axis=0) #minimun value of cross section across all above included curves for each mass
        return (x_val_arr, exp_upper_lim)
    
    def addCurves(self, excludedRegion = True):
                
        ## Add all items of dataBase to the plot
        for item in self.DB.values():
            item.plot(self.fig, self.ax)

        # ## Add some lines (tree-level scattering through Z0)
        # ax0.plot(plot_x_limits, 1e-39*np.ones(2), 'r--', linewidth=3.0)

        ## Fill in the exclusion curve
        if excludedRegion:
            (x_excluded, y_excluded) = self.getExcludedRegion() 
            if len(y_excluded)>0:
                self.ax.fill_between(x_excluded, y_excluded, self.y_limits[1], 
                    color  = '#aaffc3', 
                    zorder = 0, 
                    alpha  = 0.5, 
                    lw     = 0)

    
    def setPlottedObjects(self, reset = True):

        if reset:
            self.plotted_shapes = []

        for child in self.ax.get_children():

            if type(child) == mpl.lines.Line2D:
                x = child.get_data()[0]
                y = child.get_data()[1]
                xy = func.dataToDisplayCoordinates(x,y, self.ax)
                self.plotted_shapes.append(sg.LineString( xy ))
                #self.plotted_shapes.append(sg.LineString( [(xx,yy) for xx,yy in zip(x,y)]  ))

            if type(child) == mpl.text.Text:
                if child.get_text() != '':
                    xy = self.ax.transData.transform(child.get_position())   
                    wh = func.getTextWidthHeight(child,self.ax,force_null_rotation=True, data_coordinate_units=False) 
                    self.plotted_shapes.append(sg.Polygon(func.cornersOfRectangle(xy, wh, child.get_rotation(), rotation_in_deg = True)))

    # ==============================================================================#
    # switch to interactive mode and shows the plot on screen
    #
    def showPlot(self):
        cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        plt.ioff()
        plt.show()
        self.fig.canvas.mpl_disconnect(cid)

    def onclick(self, event):
        
        print('%s click: button=%d, x=%d, y=%d, xdata=%g, ydata=%gf' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))
        
        #Rotation angle to help finding a suitable rotation of labels
        global PREVIOUS_CLICK
        if PREVIOUS_CLICK is not None:
            print('Rotation angle: %.1f deg' 
                %np.rad2deg(np.arctan(
                (event.y-PREVIOUS_CLICK[1])/(event.x-PREVIOUS_CLICK[0]) ))
                if event.x-PREVIOUS_CLICK[0]!=0 else '')
        PREVIOUS_CLICK = (event.x, event.y)

    # ==============================================================================#
    # saves the plot on a file
    #
    def savePlot(self, plotname):
        filename = PATH_FIGURE_FOLDER + plotname
        
        if not (plotname.endswith('.pdf') or plotname.endswith('.png')):
            filename = filename + '.pdf'
       
        try:
            self.fig.savefig(filename , bbox_inches='tight')
        except (FileNotFoundError):
            filename=filename.replace(PATH_FIGURE_FOLDER,'')
        print(filename + " saved.")




