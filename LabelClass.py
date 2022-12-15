import shapely.geometry as sg
import matplotlib.pyplot as plt
import matplotlib as mpl
import functionality as func


class LabelClass:
    
    def __init__(self, xy_position, rotation_deg, widthHeight_tuple, axis=None, xy_curve=None, xy_in_display_coordinates=False, rotation_in_deg=True):
        self.ax = axis or plt.gca()
        self.fig = self.ax.get_figure()
        self.xy = None
        self.rotation_deg=None
        self.rotation_rad=None
        self.width=None
        self.height=None

        self.set_xy_position(xy_position, xy_in_display_coordinates)
        self.set_width_height (widthHeight_tuple)
        self.set_rotation(rotation_deg, unit_is_degrees=rotation_in_deg)
        self.set_xy_curve(xy_curve, xy_in_display_coordinates)
        #self.set_polygon() #done inside set_rotation
    @classmethod
    def from_string(cls, text_string, xy_position, rotation,  fontsize=10.,xy_in_display_coordinates=False, rotation_in_deg=True, axis=None ):
        ax = axis or plt.gca()

        if xy_in_display_coordinates:
            xy_data_coord = func.displayToDataCoordinates([xy_position[0]],[xy_position[1]], ax)
        else:
            xy_data_coord = xy_position

        txt_el = ax.text( xy_data_coord[0], xy_data_coord[1],
                     text_string, fontsize=fontsize)
        wh = func.getTextWidthHeight(txt_el, ax,  
            force_null_rotation=True, data_coordinate_units=False)
        if func.findTextObjectOnAxis(ax, text_string, 
                full_coincidence_of_str=True) == txt_el:
            mpl.artist.Artist.remove(txt_el)

        return cls(xy_position, rotation, wh, axis=ax, 
                xy_in_display_coordinates=xy_in_display_coordinates, 
                rotation_in_deg=rotation_in_deg )

    @classmethod #needs update to fill new attributes
    def from_mplText(cls, text_element, axis = None):
        ax = axis or plt.gca()
        wh = func.getTextWidthHeight(text_element, ax,
                 force_null_rotation=True, data_coordinate_units=False)
        
        xy_position = text_element.get_position() #¿Pasar a display coordinates?
        rotation_deg = text_element.get_rotation()

        return cls(xy_position, rotation_deg, wh, axis = ax)

    def set_xy_position(self, xy_position, position_in_display_coordinates = False):
        try:
            if len(xy_position)==2:
                if position_in_display_coordinates:#transform xy_position from display coordinates to data coordinates
                    self.xy = self.ax.transData.inverted().transform(xy_position) 
                else: 
                    self.xy = xy_position
            else:
                print(f"ERROR42: {xy_position} must be a list or tuple of length 2 (x,y) but it has length={len(xy_position)}")
        except (TypeError):
            print(f"ERROR42: {xy_position} must be a list or tuple (x,y) but it is {type(xy_position)}")
        self.set_polygon()

    def get_xy_position(self, display_coordinates = False):
        if display_coordinates: ##transform xy_position from data coordinates to display coordinates
            return self.ax.transData.transform(self.xy)
        return self.xy
    
    
    def set_rotation(self, rotation, unit_is_degrees = True):
        if unit_is_degrees:
            self.rotation_deg = rotation
            self.rotation_rad = rotation * 3.14159265358979/180
        else:
            self.rotation_rad = rotation
            self.rotation_deg = rotation * 180./ 3.14159265358979
        self.set_polygon()
    def get_rotation(self, radians = False):
        if radians:
            return self.rotation_rad
        return self.rotation_deg

    def set_width_height(self, widthHeight_tuple):
        if type(widthHeight_tuple) in [list, tuple]:
            if len(widthHeight_tuple)>=2:
                self.set_width (widthHeight_tuple[0])
                self.set_height(widthHeight_tuple[1])

            else:
                print(f"ERROR: {widthHeight_tuple} must be a list or tuple of length 2 (width,height)")
        else:
            print(f"ERROR: {widthHeight_tuple} must be a list or tuple (width,height)")
        self.set_polygon()
    def set_width (self, width):
        self.width = width
    def set_height (self, height):
        self.height = height
    def set_xy_curve(self,xy_curve, xy_in_display_coordinates=False):
        if xy_curve is None:
            self.xy_curve = None
            self.rotation_curve_deg = None
            return None
        try:
            len(xy_curve)>0
            try:
                len(xy_curve[0])
            except (TypeError):
                print(f"ERROR123: {xy_curve} must must be a list of TUPLES [(x0,y0), (x1,y1), ...]")
                self.xy_curve = None
                self.rotation_curve_deg = None
                return None

        except (TypeError):
            print(f"ERROR123: {xy_curve} must must be a LIST of tuples [(x0,y0), (x1,y1), ...]")
            self.xy_curve = None
            self.rotation_curve_deg = None
            return None         

        if not xy_in_display_coordinates:
            xy_curve = func.dataToDisplayCoordinates([x for x,y in xy_curve],[y for x,y in xy_curve], self.ax)

        self.xy_curve = xy_curve

        x = [ x for x,y in xy_curve]
        y = [ y for x,y in xy_curve]
        self.rotation_curve_deg = func.getRotation(x,y,fig=self.fig,ax=self.ax, degree_as_unit=True)
        
    def set_polygon(self):
        if all(i is not None for i in [self.xy, self.rotation_rad, self.width, self.height]):
            self.polygon = sg.Polygon(  
                func.cornersOfRectangle(self.get_xy_position(display_coordinates=True), (self.width,self.height),
                self.rotation_rad, rotation_in_deg = False) 
                )
    
    def make_corners(self, display_coordinates = False):
        return func.cornersOfRectangle(self.get_xy_position(display_coordinates=display_coordinates), (self.width,self.height),
            self.rotation_rad, rotation_in_deg = False) 
    
    def amountOffCurve(self, xy_curve, display_coordinates = False):
        return func.amountLabelOffCurve( self.get_xy_position(display_coordinates) , self.rotation_rad, 
                                        self.width, xy_curve)

    def inside(self, rectangle_corners, display_coordinates = False):
        return func.insideOneAnother(rectangle_corners, 
                self.make_corners(display_coordinates))
    def intersectsAnyCurve(self, wimpPlot):
        return func.intersectsAnyCurve(wimpPlot, self.get_xy_position(display_coordinates=True), self.rotation_rad, 
                                        (self.width,self.height))
    def intersectsAnyCurveOrText(self, wimpPlot):
        return func.intersectsAnyCurveOrText(wimpPlot, self.get_xy_position(display_coordinates=True), 
                                self.rotation_rad, (self.width,self.height))
    #def intersectsItsCurve(self,wimpPlot):
    #    return 
