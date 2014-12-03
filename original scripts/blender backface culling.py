import bpy

def print_links(node_id):
    print("Link data for material #"+str(node_id)+":")
    for link in bpy.data.materials[node_id].node_tree.links:
        print("    Link from \""+link.from_node.name+"\"'s "+link.from_socket.name+
              " to \""+link.to_node.name+"\"'s "+link.to_socket.name)

def verify(mat):
    valid = mat.use_nodes == True and \
            mat.node_tree.nodes.__len__() == 4 and \
            mat.node_tree.nodes.get("Diffuse BSDF") != None
    return valid

def process(mat):
    print("Processing material "+mat.name+"...")
    # alias some stuff for easier reference
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    # find existing nodes
    mat_out = nodes['Material Output']
    diffuse = nodes['Diffuse BSDF']
    # create required new nodes
    geo = nodes.new('ShaderNodeNewGeometry')
    geo.location = 0, 700
    trans = nodes.new('ShaderNodeBsdfTransparent')
    trans.location = 0, 300
    mix = nodes.new('ShaderNodeMixShader')
    mix.location = 200, 500
    # move output to more visually logical spot
    mat_out.location = 400, 500
    # find link from diffuse -> output...
    del_link = diffuse.outputs[0].links[0]
    # ...and delete it
    links.remove(del_link)
    # connect geometry backfacing -> mix shader fac
    links.new(mix.inputs['Fac'],
              geo.outputs['Backfacing'])
    # connect diffuse output -> mix input 1
    links.new(mix.inputs[1],
              diffuse.outputs['BSDF'])
    # connect transparent output -> mix input 2
    links.new(mix.inputs[2],
              trans.outputs['BSDF'])
    # connect mix shader output -> material output
    links.new(mat_out.inputs['Surface'],
              mix.outputs[0])


def main():
#    mat_id = "073"
#    mat_name = "53731b0711b8465794de430a8081667b_"+mat_id+".jpg.001"
#
#    # Test if material exists:
#    mat = bpy.data.materials.get(mat_name)
#
#    if mat is None:
#        print("ERROR - could not find material")
#    else:
    for mat in bpy.data.materials:
        print("\nChecking material "+mat.name)
        # Check to see if this material 
        # confines to the right format for processing
        if verify(mat):
            print("Material is valid")
            # All clear, process material
            process(mat)
        else:
            print("ERROR - material is invalid")

print("---Start of script---\n")
main()
#print_links(48)
print("\n---End of script---\n")