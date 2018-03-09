class find_references:

    def __init__(self, kwargs):
           self.kwargs = kwargs

    # MAIN FUNCTION FOR FINDING NODES REFERENCING THE CURRENT NODE
    def findReferences(self, sel):   
        
        # INITIALIZE VARIABLES
        z = 0
        node_ref_list = []
        parm_ref_list = []
        root = hou.node("/")

        # CHECK PARAMETERS OF ALL NODES FOR REFERENCES TO THIS NODE
        for n in root.allSubChildren():
            # IGNORE HIDDEN IPR CAMERA
            if n.path() != "/obj/ipr_camera":
                
                # CHECK ALL PARMS, AND PROCEED IF PARM TYPE IS STRING AND IS A NODE REFERENCE, AND HAS ANY SET VALUE
                for p in n.parms():
                    if p.parmTemplate().type() == hou.parmTemplateType.String:
                        if p.parmTemplate().stringType() == hou.stringParmType.NodeReference:
                            if p.eval():
                                
                                # GET PATH CURRENT PARM IS REFERENCING
                                try:
                                    full_path = p.node().node(p.eval()).path()
                                except:
                                    full_path = p.eval()
                                    
                                # USE GLOB TO ACCOUNT FOR PATTERNS SUCH AS WILDCARDS
                                for node_match in root.glob(full_path):
                                    
                                    # CHECK IF THERE IS A MATCH WITH THE QUERY NODE, AND IF SO, APPEND TO LIST
                                    if sel.path() == node_match.path(): 
                                        node_ref_list.append( p.path() )  
        
        # CHECK ALL PARAMETERS OF THIS NODE TO SEE IF OTHER PARAMETERS ARE REFERENCING THEM
        for p in sel.parms():
            parm_list = []
            
            # CHECK IF ANY EXTERNAL PARMS ARE REFERENCING THE CURRENT PARM, EXCLUDING THE SELF NODE
            if p.parmsReferencingThis():
                for parm_ref in p.parmsReferencingThis():                      
                    if parm_ref.node() != p.node():
                        
                        # APPEND TO LIST
                        parm_list.append(p)
                        parm_list.append(p.parmsReferencingThis())
                        parm_ref_list.append( parm_list )

        return node_ref_list, parm_ref_list


    # DELETES THE SELECTED NODES, WITH A CONFIRMATION POP-UP IF ANY REFERENCES ARE FOUND
    def deleteNodeWithReferenceCheck(self):
        
        # INITIALIZE VARIABLES        
        sels = hou.selectedNodes()
        
        for sel in sels:
            # FIND REFERENCES
            node_ref_list, parm_ref_list = self.findReferences(sel)
            
            # IF NO REFERENCES ARE FOUND, DESTROY NODE
            if node_ref_list == [] and parm_ref_list == []:
                sel.destroy()
                
            # IF REFERENCES ARE FOUND, BUILD DISPLAY MESSAGE
            else:
                list_str = ""
                
                # LIST NODE REFERENCES
                if node_ref_list:
                    list_str = "\nNode References:\n"
                    for node in node_ref_list:
                        list_str = "%s %s\n" % (list_str, node)
                    
                # LIST PARAMETER REFERENCES
                if parm_ref_list:
                    list_str += "\n\nParameter References:\n"
                    for parm in parm_ref_list:
                        for ref_parm in parm[1]:
                            list_str = "%s %s\n" % (list_str, ref_parm.path())
                            
                # DISPLAY CONFIRMATION MESSAGE
                do_destroy = hou.ui.displayMessage("%s contains the following references:\n%s\nAre you sure you want to delete it?" % (sel.name(), list_str) , buttons=('Cancel','OK'),close_choice=0)
                
                # IF CONFIRMED, DESTROY NODE
                if do_destroy:
                    sel.destroy()
    
    # PRINT REFERENCES IN SHELL/TERMINAL
    def printReferences(self):  
        
        # INITIALIZE VARIABLES        
        sels = hou.selectedNodes()        
        
        # PRINT START
        print "\n----------------------------------------------------"
        print "CHECKING SELECTED NODES FOR NODE AND PARAMETER REFERENCES"

        for sel in sels:
            # PRINT NODE PATH
            print "\n##### %s #####" % sel.path()
            
            # FIND REFERENCES
            node_ref_list, parm_ref_list = self.findReferences(sel)
            
            # PRINT NODE REFERENCES
            if node_ref_list:
                print '\n--THE FOLLOWING NODE PARAMETERS ARE REFERENCING "%s":' % sel.path()
                for node in node_ref_list:
                    print node

            # PRINT PARAMETER REFERENCES
            if parm_ref_list:
                print '\n--THE FOLLOWING PARAMETERS ARE BEING REFERENCED FROM "%s":' % sel.path()
                for parm in parm_ref_list:
                    ref_parm_paths = []
                    for ref_parm in parm[1]:
                        ref_parm_paths.append(ref_parm.path())
                    print '"%s" is being referenced by: "%s"' % (parm[0].name(), str(', '.join(ref_parm_paths)))    
                    
            # IF NO NODE OR PARAMETER REFERENCES
            if not node_ref_list and not parm_ref_list:
                print '--NO NODE OR PARAMETER REFERENCES DETECTED ON "%s"' % sel.path()

        # PRINT END
        print "\n----------------------------------------------------"     

    # RUN, CHECKING FOR MODIFIERS
    def run(self):
        
        # IF CTRL-CLICKED
        if self.kwargs['ctrlclick']:
               self.deleteNodeWithReferenceCheck()
        
        # IF CLICKED WITH NO MODIFIER
        else:
               self.printReferences()
               
fr = find_references(kwargs)
fr.run()
