#
# Standard geni-lib/portal libraries
#
import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.igext as IG

tourDescription = """
This profile sets up a network experiment with three nodes: traffic, cta, and cpf. Each node runs Ubuntu 18 and is connected via specified NIC ports.
"""

tourInstructions = """
To interact with the nodes, ssh into each node using the provided details in the experiment list view.
"""

#
# Globals
#
class GLOBALS(object):
    SITE_URN = "urn:publicid:IDN+powder.utah.edu+authority+cm"
    UBUNTU18_IMG = "urn:publicid:IDN+powder.utah.edu+image+powder-powder:ubuntu-18.04"
    HWTYPE = "m510"
    STORAGE_CAPACITY = "128GB"
    NIC_PORTS = [0, 1, 2, 3]

def invoke_script_str(filename):
    # also redirect all output to /script_output
    run_script = "sudo bash " + GLOBALS.SCRIPT_DIR + filename + " &> ~/install_script_output"
    return run_script

#
# This geni-lib script is designed to run in the POWDER Portal.
#
pc = portal.Context()

#
# Create our in-memory model of the RSpec -- the resources we're going
# to request in our experiment, and their configuration.
#
request = pc.makeRequestRSpec()

# Optional physical type for all nodes.
pc.defineParameter("phystype",  "Optional physical node type",
                   portal.ParameterType.STRING, "m510",
                   longDescription="Specify a physical node type (m510, m400, d710, etc) " +
                   "instead of letting the resource mapper choose for you.")

# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()
pc.verifyParameters()

# Define the nodes
def create_node(name, img, storage, hwtype):
    node = request.RawPC(name)
    node.component_manager_id = GLOBALS.SITE_URN
    node.disk_image = img
    node.hardware_type = hwtype
    bs = node.Blockstore(name + "-bs", "/mnt/data")
    bs.size = storage
    return node

# Traffic Node
traffic = create_node("traffic", GLOBALS.UBUNTU18_IMG, GLOBALS.STORAGE_CAPACITY, params.phystype)

# CTA Node
cta = create_node("cta", GLOBALS.UBUNTU18_IMG, GLOBALS.STORAGE_CAPACITY, params.phystype)

# CPF Node
cpf = create_node("cpf", GLOBALS.UBUNTU18_IMG, GLOBALS.STORAGE_CAPACITY, params.phystype)

# Define the links and add the nodes to the links
def create_link(name, node1, iface1, node2, iface2):
    link = request.Link(name)
    link.addInterface(node1.addInterface(iface1))
    link.addInterface(node2.addInterface(iface2))
    return link

# Create links as specified
create_link("traffic-cta-link1", traffic, "eth2", cta, "eth2")
create_link("traffic-cta-link2", traffic, "eth3", cta, "eth3")
create_link("cta-cpf-link", cta, "eth1", cpf, "eth3")

tour = IG.Tour()
tour.Description(IG.Tour.MARKDOWN, tourDescription)
tour.Instructions(IG.Tour.MARKDOWN, tourInstructions)
request.addTour(tour)

pc.printRequestRSpec(request)
