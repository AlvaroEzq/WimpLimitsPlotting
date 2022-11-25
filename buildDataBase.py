import DataClasses as dc

def buildDataBase():
    '''Add here the different experiment data.
        Plotting options (e.g. label position, color, etc.) can be defined 
        in the data file or in Curve initialization (second has preference over first)
    '''
    ## ====== ADD THE DIFFERENT EXPERIMENT DATA ====== ##
    # label data can be defined in the data file or in ResultCurve initialization (second has preference over first)
    
    db = {}
    ## Result curves
    #db['CDEX10']    = dc.Curve("CDEX10_2018.dat")
    db['CDMSLite']   = dc.Curve("CDMSLite_2016.dat")
    db['CRESSTII']   = dc.Curve("CRESSTII_2015.dat", label='CRESST-II\n(2015)',label_xpos=0.27)
    #db['CRESSTIII']  = dc.Curve("CRESSTIII_2017.dat")
    db['CRESSTIII_2019']  = dc.Curve("CRESTIII_2019.txt",label='CRESST-III\n(2019)', label_xpos=0.2, label_ypos=1.35e-35)
    #db['CRESSTsrf'] = dc.Curve("CRESSTsurface_2017.dat")
    #db['DAMIC100']  = dc.Curve("DAMIC_SNOLAB_2016.dat")
    db['DAMIC2020']  = dc.Curve("DAMIC_2020.dat", label_xpos=4.2, label_ypos=1.2e-40, label_rotation= -10)
    db['DarkSide']   = dc.Curve("DarkSide50_S2only_2018.dat", label_xpos=1.45, label_ypos=2.4e-41, label_rotation= -15)
    #db['DEAP3600']   = dc.Curve("DEAP3600_2019.dat")
    #db['LUX']       = dc.Curve("LUX_completeExposure_2016.dat")
    db['NEWSG']      = dc.Curve("NEWS_G_2018.dat", label_xpos=4, label_ypos=6.5e-39)
    #db['PANDAX']    = dc.Curve("PandaX_2017.dat")
    db['PICO_C3F8']  = dc.Curve("PICO_C3F8_2017.dat")
    db['PICO_CF3I']  = dc.Curve("PICO_CF3I_2015.dat", label_xpos=7)
    #db['X1T_MIG']    = dc.Curve("X1T_MIGDAL_2020.dat", style = 'projection', label='XENON1T\nMigdal', label_xpos=1.02, label_ypos=1.2e-40)
    db['X1T_MIG']    = dc.Curve("X1T_MIGDAL_2020.dat", style = 'projection', label_xpos=0.75, label_ypos=4.55e-39,label_rotation= -22 )
    db['XENON1T']    = dc.Curve("XENON1T_2018.dat", label_xpos=5.8, label_ypos=4.5e-45, label_rotation= -45)
    db['XENON1T2']   = dc.Curve("XENON1T_lowmass.dat", label_xpos=6.1, label_ypos=5.8e-44, label_rotation= -30)
    #db['XENON100']  = dc.Curve("XENON100S2_2016.dat")
    #db['XMASS']     = dc.Curve("XMASS_2018.dat")

    ## Result Contours
    db['DAMA_I']     = dc.Contour("DAMA_I.dat")
    #db['DAMA_Na']    = Contour("DAMA_Na.dat")

    ## Projection curves
    #db['DAMICM']    = dc.Curve("DAMIC_M_2020.dat", style = 'projection')
    #db['LZ']        = dc.Curve("LZ_projection_2018.dat", style = 'projection')
    #db['SuperCDMS'] = dc.Curve("SuperCDMS_SNOLAB_projection_2017.dat", style = 'projection')
    #db['XENONnT ']  = dc.Curve("XENONnT_projection_2020.dat", style = 'projection')

    '''
    db['TREXDM_Z']   = dc.Curve("TREX_escenarios/WimpSensitivity_Ne_0.9446_C_0.0459_H_0.0095_WD_0.3_Vel_232_220_544_Bck_10_Exp_109.5_RecEn_0_2_0.01_EnRange_0.4_1.4_usingQF.dat",
                                label = 'Z',style = 'projection',  color = 'red', label_xpos=0.485 , label_ypos=4.1e-35)
    db['TREXDM_B']   = dc.Curve("TREX_escenarios/WimpSensitivity_Ne_0.9446_C_0.0459_H_0.0095_WD_0.3_Vel_232_220_544_Bck_1_Exp_109.5_RecEn_0_2_0.01_EnRange_0.1_1.1_usingQF.dat",
                                label ='B',style = 'projection',  color = 'red', label_xpos= 0.167 , label_ypos=1.46e-35)

    db['TREXDM_D']   = dc.Curve("TREX_escenarios/WimpSensitivity_Ne_0.9446_C_0.0459_H_0.0095_WD_0.3_Vel_232_220_544_Bck_1_Exp_1095_RecEn_0_2_0.01_EnRange_0.05_1.05_usingQF.dat",
                                label = 'D',style = 'projection',  color = 'red', label_xpos= 0.19, label_ypos=3.65e-38)							 

    db['TREXDM_F']   = dc.Curve("TREX_escenarios/WimpSensitivity_Ne_0.9446_C_0.0459_H_0.0095_WD_0.3_Vel_232_220_544_Bck_10_Exp_109.5_RecEn_0_2_0.01_EnRange_0.05_1.05_usingQF.dat",
                                label = 'F',style = 'projection',  color = 'red', label_xpos= 0.135, label_ypos=1.75e-35)	
    '''


    db['TREXDM_A']   = dc.Curve("TREX_escenarios/WimpSensitivity_Ne_0.9446_C_0.0459_H_0.0095_WD_0.3_Vel_232_220_544_Bck_1_Exp_109.5_RecEn_0_2_0.01_EnRange_0.4_1.4_usingQF.dat",
                                label = 'A',style = 'projection',  color = 'orange', label_xpos=0.45 , label_ypos=1.05e-35)
    db['TREXDM_C']   = dc.Curve("TREX_escenarios/WimpSensitivity_Ne_0.9446_C_0.0459_H_0.0095_WD_0.3_Vel_232_220_544_Bck_0.1_Exp_1095_RecEn_0_2_0.01_EnRange_0.05_1.05_usingQF.dat",
                                label = 'C',style = 'projection',  color = 'red', label_xpos= 0.26 , label_ypos=1.9e-39)

    db['TREXDM_E']   = dc.Curve("TREX_escenarios/WimpSensitivity_Ne_0.9446_C_0.0459_H_0.0095_WD_0.3_Vel_232_220_544_Bck_1_Exp_109.5_RecEn_0_2_0.01_EnRange_0.05_1.05_usingQF.dat",
                                label = 'B',style = 'projection',  color = 'black', label_xpos= 0.212, label_ypos=9.45e-38)		

    db['TREXDM_E90-10']   = dc.Curve("TREX_escenarios/WimpSensitivity_Ne_0.7575_C_0.2003_H_0.0422_WD_0.3_Vel_232_220_544_Bck_1_Exp_109.5_RecEn_0_2_0.01_EnRange_0.05_1.05_usingQF.dat",
                                label = 'B10',style = '-.',  color = 'black', label_xpos= 0.255, label_ypos=1.2e-38)
    db['TREXDM_C90-10']   = dc.Curve("TREX_escenarios/WimpSensitivity_Ne_0.7575_C_0.2003_H_0.0422_WD_0.3_Vel_232_220_544_Bck_0.1_Exp_1095_RecEn_0_2_0.01_EnRange_0.05_1.05_usingQF.dat",
                                label = 'C10',style = '-.',  color = 'red', label_xpos= 0.18, label_ypos=9.3e-40)		

    ## Neutrino Fog curves
    # db['NuFog']     = dc.NeutrinoFog("SI_NeutrinoFloor_Ruppin_LZ_Fig3_1000ty.dat")#
    db['NuFloor']  = dc.NeutrinoFog("NuFloorXe.dat", color = 'gray')
    return db
