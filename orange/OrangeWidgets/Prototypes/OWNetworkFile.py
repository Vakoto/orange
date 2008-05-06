"""
<name>Network File</name>
<description>Reads data from a graf file (Pajek networks (.net) files).</description>
<icon>icons/NetworkFile.png</icon>
<contact>Miha Stajdohar (miha.stajdohar(@at@)gmail.com)</contact> 
<priority>3010</priority>
"""

#
# OWGrafFile.py
# The File Widget
# A widget for opening orange data files
#
import orngOrangeFoldersQt4
import OWGUI, string, os.path, user, sys

from OWWidget import *
from orngNetwork import *

from orange import Graph
from orange import GraphAsList
from orange import ExampleTable
from orangeom import Network

class OWNetworkFile(OWWidget):
    
    settingsList=["recentFiles", "recentDataFiles"]
    
    def __init__(self,parent=None, signalManager = None):
        OWWidget.__init__(self, parent, signalManager, "Network File")

        self.inputs = []
        self.outputs = [("Network", Network)]
    
        #set default settings
        self.recentFiles = ["(none)"]
        self.recentDataFiles = ["(none)"]
        self.domain = None
        self.graph = None
        #get settings from the ini file, if they exist
        self.loadSettings()
        #print self.recentFiles
        print "before gui"
        #GUI
        self.controlArea.layout().setMargin(4)
        self.box = OWGUI.widgetBox(self.controlArea, box = "Graph File", orientation = "horizontal")
        self.filecombo = OWGUI.comboBox(self.box, self, "filename")
        self.filecombo.setMinimumWidth(250)
        button = OWGUI.button(self.box, self, '...', callback = self.browseFile, disabled=0, width=25)
        print "info 1"
        self.databox = OWGUI.widgetBox(self.controlArea, box = "Data File", orientation = "horizontal")
        self.datacombo = OWGUI.comboBox(self.databox, self, "dataname")
        self.datacombo.setMinimumWidth(250)
        button = OWGUI.button(self.databox, self, '...', callback = self.browseDataFile, disabled=0, width=25)
        print "info 2"
        # info
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data loaded.')
        self.infob = OWGUI.widgetLabel(box, ' ')
        self.infoc = OWGUI.widgetLabel(box, ' ')
        
        self.resize(150,100)
        print "before activate"
        self.activateLoadedSettings()
        print "before connect"
        # connecting GUI to code
        #self.connect(self.filecombo, SIGNAL('activated(int)'), self.selectFile)
        #self.connect(self.datacombo, SIGNAL('activated(int)'), self.selectDataFile)
        print "after  gui"
        # set the file combo box
    def setFileList(self):
        self.filecombo.clear()
        if not self.recentFiles:
            self.filecombo.addItem("(none)")
        for file in self.recentFiles:
            if file == "(none)":
                self.filecombo.addItem("(none)")
            else:
                self.filecombo.addItem(os.path.split(file)[1])
        
        self.datacombo.clear()
        if not self.recentDataFiles:
            self.datacombo.addItem("(none)")
        for file in self.recentDataFiles:
            if file == "(none)":
                self.datacombo.addItem("(none)")
            else:
                self.datacombo.addItem(os.path.split(file)[1])
        
        self.filecombo.updateGeometry()
        self.datacombo.updateGeometry()
     
    def activateLoadedSettings(self):
        # remove missing data set names
        self.recentFiles = filter(os.path.exists, self.recentFiles)
        self.recentDataFiles = filter(os.path.exists, self.recentDataFiles)
        self.setFileList()
        
        if len(self.recentFiles) > 0 and os.path.exists(self.recentFiles[0]):
            self.openFile(self.recentFiles[0])
        
        if len(self.recentDataFiles) > 0 and os.path.exists(self.recentDataFiles[0]):
            self.addDataFile(self.recentDataFiles[0])
        
    # user selected a graph file from the combo box
    def selectFile(self, n):
        if n < len(self.recentFiles) :
            name = self.recentFiles[n]
            self.recentFiles.remove(name)
            self.recentFiles.insert(0, name)

        if len(self.recentFiles) > 0:
            self.setFileList()
            self.openFile(self.recentFiles[0])
    
    # user selected a data file from the combo box
    def selectDataFile(self, n):
        if n < len(self.recentDataFiles) :
            name = self.recentDataFiles[n]
            self.recentDataFiles.remove(name)
            self.recentDataFiles.insert(0, name)

        if len(self.recentDataFiles) > 0:
            self.setFileList()
            self.addDataFile(self.recentDataFiles[0])
    
    def openFile(self, fn):
        print "before openFileBase"
        self.openFileBase(fn)
        print "after openFileBase"
        if '(none)' in self.recentDataFiles: 
            self.recentDataFiles.remove('(none)')
            
        self.recentDataFiles.insert(0, '(none)')
        print "before list"
        self.setFileList()
        print "after list"
        
    def addDataFile(self, fn):
        if fn == "(none)" or self.graph == None:
            self.infoc.setText("No data file specified.")
            return
         
        table = ExampleTable(fn)
        
        if len(table) != self.graph.nVertices:
            self.infoc.setText("Data length does not match number of vertices.")
            
            if '(none)' in self.recentDataFiles: 
                self.recentDataFiles.remove('(none)')
                
            self.recentDataFiles.insert(0, '(none)')
            self.setFileList()
            return
        
        self.graph.setattr("items", table)
        self.infoc.setText("Data file added.")
        self.send("Network", self.graph)
        
    def browseDataFile(self, inDemos=0):
        if self.graph == None:
            return
        
        "Display a FileDialog and select a file"
        if len(self.recentDataFiles) == 0 or self.recentDataFiles[0] == "(none)":
            if sys.platform == "darwin":
                startfile = user.home
            else:
                startfile="."
        else:
            startfile = self.recentDataFiles[0]
                
        filename = str(QFileDialog.getOpenFileName(self, 'Open a Data File', startfile, 'Data files (*.tab)\nAll files(*.*)'))
    
        if filename == "": return
        if filename in self.recentDataFiles: self.recentDataFiles.remove(filename)
        self.recentDataFiles.insert(0, filename)
        self.setFileList()
        self.addDataFile(self.recentDataFiles[0])
    
    # user pressed the "..." button to manually select a file to load
    def browseFile(self, inDemos=0):
        "Display a FileDialog and select a file"
        if len(self.recentFiles) == 0 or self.recentFiles[0] == "(none)":
            if sys.platform == "darwin":
                startfile = user.home
            else:
                startfile = "."
        else:
            startfile = self.recentFiles[0]
                
        filename = str(QFileDialog.getOpenFileName(self, 'Open a Network File', startfile, "Pajek files (*.net)\nAll files (*.*)"))
        if filename == "": return
        if filename in self.recentFiles: self.recentFiles.remove(filename)
        self.recentFiles.insert(0, filename)
        self.setFileList()
        self.openFile(self.recentFiles[0])

    def setInfo(self, info):
        for (i, s) in enumerate(info):
            self.info[i].setText(s)            

     # Open a file, create data from it and send it over the data channel
    def openFileBase(self, fn):
        if fn != "(none)":
            fileExt = lower(os.path.splitext(fn)[1])
            if fileExt in (".net"):
                pass
            else:
                return

            data = self.readNetFile(fn)
            
            if data == None:
                self.send("Network", None)
                return

            self.infoa.setText("%d nodes" % data.nVertices)
            
            if data.directed:
                self.infob.setText("Directed graph")
            else:
                self.infob.setText("Undirected graph")
            
            # make new data and send it
            fName = os.path.split(fn)[1]
            if "." in fName:
                data.name = string.join(string.split(fName, '.')[:-1], '.')
            else:
                data.name = fName
                
            #print "nVertices graph: " + str(data.nVertices)
            self.graph = data
            self.send("Network", data)
#            drawer = OWGraphDrawer()
#            drawer.setGraph(data)
#            drawer.show()
        else:
            print "None"
            self.send("Network", data)

    def readNetFile(self, fn):
        print "in read net"
        network = NetworkOptimization()
        print "network opt"
        try:
            network.readNetwork(fn)
            self.infoc.setText("Data generated and added automatically.")
        except:
            self.infoa.setText("Could not read file.")
            self.infob.setText("")
            return None
        
        print "after read net"
        return network.graph

if __name__ == "__main__":
    a=QApplication(sys.argv)
    owf=OWNetworkFile()
    owf.activateLoadedSettings()
    owf.show()  
    a.exec_()
    owf.saveSettings()
