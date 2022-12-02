import shapely.geometry as sg
import matplotlib.pyplot as plt
import functionality as func


class LabelClass:
    
    def __init__(self, xy_position, rotation_deg, widthHeight_tuple):
        self.set_xy_position(xy_position)
        self.set_rotation(rotation_deg)
        self.set_width_height (widthHeight_tuple)
        self.make_polygon()

    @classmethod
    def from_mplText(cls, text_element, fig = None, ax = None):
        fig = fig or plt.gcf()
        ax = ax or plt.gca()

        wh = func.getTextWidthHeight(text_element, fig, ax,
                 force_null_rotation=True, data_coordinate_units=False)
        
        xy_position = text_element.get_position() #¿Pasar a display coordinates?
        rotation_deg = text_element.get_rotation()

        return cls(xy_position, rotation_deg, wh)

    def set_xy_position(self, xy_position):
        if type(xy_position) in [list, tuple]:
            if len(xy_position)>=2:
                self.xy = xy_position
            else:
                print(f"ERROR: {xy_position} must be a list or tuple of length 2 (x,y)")
        else:
            print(f"ERROR: {xy_position} must be a list or tuple (x,y)")
    
    def set_rotation(self, rotation, unit_is_degrees = True):
        if unit_is_degrees:
            self.rotation_deg = rotation
            self.rotation_rad = self.rotation_deg * 3.14159265358979/180
        else:
            self.rotation_rad = rotation
            self.rotation_deg = self.rotation_rad * 180./ 3.14159265358979

    def set_width_height(self, widthHeight_tuple):
        if type(widthHeight_tuple) in [list, tuple]:
            if len(widthHeight_tuple)>=2:
                self.set_width (widthHeight_tuple[0])
                self.set_height(widthHeight_tuple[1])

            else:
                print(f"ERROR: {widthHeight_tuple} must be a list or tuple of length 2 (width,height)")
        else:
            print(f"ERROR: {widthHeight_tuple} must be a list or tuple (width,height)")
    
    def set_width (self, width):
        self.width = width
    def set_height (self, height):
        self.height = height
    
    def make_polygon(self):
        self.polygon = sg.Polygon(  
            func.cornersOfRectangle(self.xy, (self.width,self.height),
             self.rotation_rad, rotation_in_deg = False) 
             )
    
    def make_corners(self):
        return func.cornersOfRectangle(self.xy, (self.width,self.height),
             self.rotation_rad, rotation_in_deg = False) 

    def amountOffCurve(self, xy_display):
        return func.amountLabelOffCurve( self.xy , self.rotation_rad, self.width, xy_display)

            
