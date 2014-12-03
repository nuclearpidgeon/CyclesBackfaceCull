import bpy

# Plugin info for registration
bl_info = {
    "name": "Cycles Backface Culling Shader",
    "description": "Script for setting up backface-culling shader materials.",
    "author": "Stewart Webb",
    "version": (1, 0),
    "blender": (2, 71, 0),
    "location": "Properties > Material > Convert to Cycles",
    "warning": "beta", # used for warning icon and text in addons panel
    # "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"
    #             "Scripts/My_Script",
    "category": "System"
}

def print_links(node_id):
    """
    Prints all links connected to a given node id's node.

    Useful for debugging
    """
    mat = bpy.data.materials[node_id]
    if verify(mat):
        print("valid")
    else:
        print("invalid")
    print("Link data for material #"+str(node_id)+":")
    print(mat.name)
    for link in mat.node_tree.links:
        print("    Link from \""+link.from_node.name+"\"'s "+link.from_socket.name+
              " to \""+link.to_node.name+"\"'s "+link.to_socket.name)

def verify(mat):
    """
    Returns boolean value of whether a given material is in the correct
    format for conversion.
    """
    valid = mat.use_nodes == True and \
            mat.node_tree.nodes.__len__() == 4 and \
            mat.node_tree.nodes.get("Diffuse BSDF") != None
    return valid

def process(mat):
    print("Processing material "+mat.name+"...")
    ### Define existing node/collection variables
    # alias collections for easier reference
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    # find existing nodes
    mat_out = nodes['Material Output']
    diffuse = nodes['Diffuse BSDF']
    texture = nodes['Image Texture.001']
    ### Preprocessing
    # remove diffuse shader (not needed)
    nodes.remove(diffuse)
    ### Create new nodes
    # create and place required new nodes
    emission = nodes.new('ShaderNodeEmission')
    emission.location = 0, 300
    lightpath = nodes.new('ShaderNodeLightPath')
    lightpath.location = 0, 700
    geo = nodes.new('ShaderNodeNewGeometry')
    geo.location = 200, 700
    trans = nodes.new('ShaderNodeBsdfTransparent')
    trans.location = 0, 400
    emissmix = nodes.new('ShaderNodeMixShader')
    emissmix.name = 'Emission Mix Shader'
    emissmix.location = 200, 400
    backfmix = nodes.new('ShaderNodeMixShader')
    backfmix.name = 'Backface Mix Shader'
    backfmix.location = 400, 500
    # move output and texture to more visually logical spots
    mat_out.location = 600, 500
    texture.location = -200, 250
    ### Connect all the nodes
    ## note: connection format is 'reversed' due to argument order:
    ## links.new(input/destination, output/source)
    # (1/8) 
    # connect texture output -> emission shader input
    links.new(emission.inputs['Color'],
              texture.outputs['Color'])
    # (2/8)
    # connect emission output -> emission mix shader input 2
    links.new(emissmix.inputs[2], 
              emission.outputs['Emission'])
    # (3/8)
    # connect transparent output -> emission mix shader input 1
    links.new(emissmix.inputs[1], 
              trans.outputs['BSDF'])
    # (4/8)
    # connect camera light path -> emission mix shader fac
    links.new(emissmix.inputs[0], 
              lightpath.outputs['Is Camera Ray'])
    # (5/8)
    # connect transparent output -> backface mix input 2
    links.new(backfmix.inputs[2], 
              trans.outputs['BSDF'])
    # (6/8)
    # connect emission mix out -> backface mix input 1
    links.new(backfmix.inputs[1], 
              emissmix.outputs[0])
    # (7/8)
    # connect geometry backfacing -> backface mix fac
    links.new(backfmix.inputs[0], 
              geo.outputs['Backfacing'])
    # (8/8)
    # connect backface mix out -> material output
    links.new(mat_out.inputs['Surface'],
              backfmix.outputs[0])
    ### Finished processing :)

def check_and_process(mat):
    """
    Checks to see if a given material is able to be processed and, 
    if it is, processes it.
    """
    print("\nChecking material "+mat.name)
    if verify(mat):
        print("Material is valid")
        # All clear, process material
        process(mat)
    else:
        print("ERROR - material is invalid")
        
def process_all():
    """
    Attempts to process all materials in the current file.
    """
    for mat in bpy.data.materials:
        check_and_process(mat)

def process_from_index(index):
    mat = bpy.data.materials[index]
    check_and_process(mat)
        
print("---Start of script---\n")
#process_all()
#print_links(48)
#process_from_index(48)
print("\n---End of script---\n")