# -*- coding: utf-8 -*-
"""

@author: hannes.rotzinger@kit.edu @ 2015
"""


from PyQt4.QtCore import *
from PyQt4.QtGui import *


from plot_view import Ui_Form
import pyqtgraph as pg

#import argparse
#import ConfigParser
import numpy as np
#import h5py


#class PlotWindow(QMainWindow, Ui_MainWindow):
class PlotWindow(QWidget,Ui_Form):
    def myquit(self):
        exit()

    def __init__(self,parent,data,dataset_url):
        self.DATA = data
        self.dataset_url = dataset_url
        self.obj_parent = parent
        super(PlotWindow , self).__init__() 
        Ui_Form.__init__(self)
        # set up User Interface (widgets, layout...)
        self.setupUi(self)
        self.graphicsView = None
        window_title = str(dataset_url.split('/')[-1]) +" "+ str(self.DATA.filename)
        self.setWindowTitle(window_title)
        self._init_XY_add()
        #self.menubar.setNativeMenuBar(False)
        #self._setPlotDefaults()

        self._setup_signal_slots()
        #self.update_plots()
        
    def _setup_signal_slots(self): 
        self.obj_parent.refresh_signal.connect(self.update_plots)
        #QObject.connect(self.PlotTypeSelector,SIGNAL("currentIndexChanged(int)"),self._onPlotTypeChange)
        #QObject.connect(self,SIGNAL("aboutToQuit()"),self._close_plot_window)
        QObject.connect(self.addXPlotSelector,SIGNAL("currentIndexChanged(int)"),self._addXPlotChange)
        QObject.connect(self.addYPlotSelector,SIGNAL("currentIndexChanged(int)"),self._addYPlotChange)
        
        
    def _setPlotDefaults(self):
        self.ds = self.obj_parent.h5file[self.dataset_url]
        if len(self.ds.shape) == 1:
            self.PlotTypeSelector.setCurrentIndex(0)
            self.PlotType = 0
        if len(self.ds.shape) == 2:
            self.PlotTypeSelector.setCurrentIndex(1)
            self.PlotType = 1
            #self.PlotTypeSelector.
    
    def _addXPlotChange(self):
        pass
    def _addYPlotChange(self):
        pass

    def _init_XY_add(self):
        for i,key in enumerate(self.DATA.ds_tree_items.iterkeys()):
            keys = key.split("/")[-2:]
            key = "/".join(key for key in keys)
            self.addXPlotSelector.addItem("")
            self.addYPlotSelector.addItem("")
            self.addXPlotSelector.setItemText(i, str(key))
            self.addYPlotSelector.setItemText(i, str(key))
            #print i,key
           
        
    def _onPlotTypeChange(self, index):
        if index == 0:
            self.PlotType = 0
        if index == 1:
            self.PlotType = 1
        #print self.PlotTypeSelector.currentText()
    
    def closeEvent(self, event):
        "overwrite the closeEvent handler"
        self.deleteLater()
        self.DATA._toBe_deleted(self.dataset_url)
        event.accept()
        

    @pyqtSlot()   
    def update_plots(self):
        #print "update_plots"
        try:
            self.ds = self.obj_parent.h5file[self.dataset_url]
            self.view_type = self.ds.attrs.get("view_type",0)
            if self.view_type == 1:
                if not self.graphicsView:
                    self.graphicsView = pg.PlotWidget(name=self.dataset_url)
                    self.graphicsView.setObjectName(self.dataset_url)
                    self.gridLayout.addWidget(self.graphicsView)
                    #self.plot = self.graphicsView.plot()
                #self._display_1D_view(self.plot, self.graphicsView)
                self._display_1D_view(self.graphicsView)
                
            elif len(self.ds.shape) == 1:
                if not self.graphicsView:
                    self.graphicsView = pg.PlotWidget(name=self.dataset_url)# pg.ImageView(self.centralwidget,view=pg.PlotItem())
                    self.graphicsView.setObjectName(self.dataset_url)
                    #self.graphicsView.setBackground(None)
                    #self.graphicsView.view.setAspectLocked(False)
                    self.gridLayout.addWidget(self.graphicsView)
                    self.plot = self.graphicsView.plot()
                self._display_1D_data(self.plot, self.graphicsView)
                    
            elif len(self.ds.shape) == 2:
                if not self.graphicsView:
                    self.graphicsView = pg.ImageView(self.obj_parent,view=pg.PlotItem())
                    self.graphicsView.setObjectName(self.dataset_url)
                    self.graphicsView.view.setAspectLocked(False)
                    self.gridLayout.addWidget(self.graphicsView)
                self._display_2D_data(self.graphicsView)
            else:
                pass
        except IOError:
        #except ValueError:
            #pass
            print "PlotWindow: Value Error; Dataset not yet available", self.dataset_url


    def _display_1D_view(self,graphicsView):
        ds = self.ds
        overlay_num = ds.attrs.get("overlays",0)
        overlay_urls = []
        for i in range(overlay_num+1):
            ov= ds.attrs.get("xy_"+str(i),0)
            overlay_urls.append(ov.split(":"))
        ds_xs = []
        ds_ys = []
        for xy in overlay_urls:
            ds_xs.append(self.obj_parent.h5file[xy[0]])
            ds_ys.append(self.obj_parent.h5file[xy[1]])
        
        
        ### for compatibility ...
        ds_x_url = ds.attrs.get("x","")
        ds_y_url = ds.attrs.get("y","")
        if ds_x_url and ds_y_url:
            ds_xs.append(self.obj_parent.h5file[ds_x_url])
            ds_ys.append(self.obj_parent.h5file[ds_y_url])
        ###
            
        for i, x_ds in enumerate(ds_xs):
            y_ds = ds_ys[i]
            if len(x_ds.shape) == 1 and len(y_ds.shape) == 1:
                
                x_data = np.array(x_ds)
                y_data = np.array(y_ds)
                #print len(x_data)
                #print len(y_data)
                x_name = x_ds.attrs.get("name","_none_")                
                y_name = y_ds.attrs.get("name","_none_")
                
                x_unit = x_ds.attrs.get("unit","_none_")
                y_unit = y_ds.attrs.get("unit","_none_")
                #print x_name, y_name, x_unit, y_unit
                #plot.setPen((200,200,100))
                graphicsView.setLabel('left', y_name, units=y_unit)
                graphicsView.setLabel('bottom', x_name , units=x_unit)
                #plot.setData(y=y_data, x=x_data)
                graphicsView.plot(y=y_data, x=x_data,pen=(i,3))
                
    def _display_1D_data(self,plot,graphicsView):
        ds = self.ds
        
        #fill = ds.attrs.get("fill",1)
        ydata = np.array(ds)
        
        x0 = ds.attrs.get("x0",0)
        dx = ds.attrs.get("dx",1)
        x_data = [x0+dx*i for i in xrange(len(ydata))]
        
        x_name = ds.attrs.get("x_name","_none_")
        name = ds.attrs.get("name","_none_")
        x_unit = ds.attrs.get("x_unit","_none_")
        unit = ds.attrs.get("unit","_none_")
        
        #plot.clear()
        plot.setPen((200,200,100))
        graphicsView.setLabel('left', name, units=unit)
        graphicsView.setLabel('bottom', x_name , units=x_unit)
        plot.setData(y=ydata, x=x_data)
        
    def _display_2D_data(self,graphicsView):
        #load the dataset:
        ds = self.ds
        #fill = ds.attrs.get("fill",1)
        fill_x = ds.shape[0]
        fill_y = ds.shape[1]
        #data = np.array(ds[:fill])
        data = np.array(ds)
        
        x0 = ds.attrs.get("x0",0)
        dx = ds.attrs.get("dx",1)
        y0 = ds.attrs.get("y0",0)
        dy = ds.attrs.get("dy",1)
        
        xmin = x0
        xmax = x0+fill_x*dx
        ymin = y0
        ymax = y0+fill_y*dy

        x_name = ds.attrs.get("x_name","_none_")        
        y_name = ds.attrs.get("y_name","_none_")
        name = ds.attrs.get("name","_none_")

        x_unit = ds.attrs.get("x_unit","_none_")
        y_unit = ds.attrs.get("y_unit","_none_")
        unit = ds.attrs.get("unit","_none_")
        
        
        pos = (xmin,ymin)
        
        #scale=(xmax/float(data.shape[0]),ymax/float(data.shape[1]))
        scale=((abs(xmax-xmin))/float(data.shape[0]),(ymax-ymin)/float(data.shape[1]))
        graphicsView.view.setLabel('left', y_name, units=y_unit)
        graphicsView.view.setLabel('bottom', x_name, units=x_unit)
        graphicsView.view.setTitle(name+" ("+unit+")")
        graphicsView.view.invertY(False)
        
        graphicsView.setImage(data,pos=pos,scale=scale)
        graphicsView.show()
        
        # Fixme roi ...
        graphicsView.roi.setPos([xmin,ymin])
        graphicsView.roi.setSize([xmax-xmin,ymax-ymin])
        
        #graphicsView.setImage(data)
        #graphicsView.show()
        
        
 

