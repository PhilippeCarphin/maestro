#!/users/dor/afsi/phc/Testing/testdomain/linux26-x86-64/bin/tclsh

# Note that this test will require
# - A path to a valid experiment
# (unused at this point because I have not made an interface for the C
# executable yet)
set testExpPath /home/ops/afsi/phc/Documents/sample
# - A node path (with leading slash and no trailing slash)
set testNode /sample_module/Different_Hosts/I.have.aperiod.in.my.name
# - A node path to a loop node (with leading slash and no trailing slash)
set testLoopNode /sample_module/Loop_Examples/outerloop/innerloop
#
# Eventually, an experiment for testing should be packaged with the maestro
# source.

# This test serves to test and document the interaction between the maestro
# executable ${NAME_COMING_SOON} and the TCL part that will read the output of
# ${NAME_COMING_SOON} into a tsv::keyed_list.
#
# This test should be run to check validity of changes to the maestro
# executable.  If any changes are made that make this test fail, either there
# was an error in the change, or this test should be updated to stay valid.
#
# If this is done errors will be caught faster, their source will be easier to
# find and if the test passes, we have more confidence that we're all good.
#
# If the TCL portion is modified and expects to use the list differently, this
# test should be modified to reflect this, then the maestro portion should be
# modified to make the test pass.

package require Thread

# The TCL portion expects to find a file with the data for a tsv keyed list.  It
# will read this data into a keyed list using tsv::keylset.
proc readNodeinfoDB { } {

   # Normally, generating this info file would be done when quitting the GUI
   # after changing the experiment.  But for testing purposes, I do it here, and
   # the rest of the function is going to stay.
   exec ../mtest > nodeinfo_keyedlist.tsv

   # Read the file (The file path will need to be constructed with the
   # experiment path, and a static path within the experiment). Something like
   # ${testExpPath}/resources/nodeinfo_keyed_list.tsv
   set fp [open nodeinfo_keyedlist.tsv]
   set data_list [read $fp]
   close $fp

   # Temporary, show the content
   puts $data_list

   # Read the content of the file into a keyed list.
   tsv::keylset the_shared_var the_keyed_list {*}$data_list

}


# Different possiblities for wrapper functions

# Having multiple wrapper functions, one for each field.  I don't like this one
# so much because it gives lots of places where we have to make changes if we
# decide to change the structure of the keyed list.
proc getCPU { nodeName } {
   return [tsv::keylget the_shared_var the_keyed_list $nodeName.resources.CPU]
}


# A good intermediate is having one function for all the the categories, like
# [getResource $nodeName CPU], [getLoop $nodeName START], [getXYZ $nodeName $key]
proc getResource { nodeName resource } {
   return [tsv::keylget the_shared_var the_keyed_list $nodeName.resources.$resource]
}


# I like this one the best, it simply hides the syntax of tsv::keylget and makes
# the code easier to read:
# getInfo $nodeName resource.CPU
# is easier to read than
# tsv::keylget the_shared_var the_keyed_list $nodeName.resource.CPU
# Of course, a more explicit name than getInfo will be required
proc getInfo { nodeName subkey } {
   return [tsv::keylget the_shared_var the_keyed_list $nodeName.$subkey]
}


# THE TEST ITSELF BEGINS HERE:

# Read the file into the keyed list
readNodeinfoDB

# Try out the syntax with a random node.

set value [tsv::keylget the_shared_var the_keyed_list $testNode.resources.CPU]
puts "resources.CPU of $testNode : $value"

set value [tsv::keylget the_shared_var the_keyed_list $testNode.depends.depname1]
puts "depends.depname1 of $testNode : $value"

# Try out the wrapper functions
set value [getCPU $testNode]
puts "Value using wrapper function : $value"

set value [getResource $testNode CPU]
puts "Value using general wrapper function : $value"

set value [getInfo $testNode resources.CPU]
puts "Value using super wrapper function : $value"

# Check that all the fields in resource are available
puts "==== INFO FOR $testNode ===="
puts "CATCHUP [getInfo $testNode resources.CATCHUP]"
puts "CPU [getInfo $testNode resources.CPU]"
puts "QUEUE [getInfo $testNode resources.QUEUE]"
puts "MPI [getInfo $testNode resources.MPI]"
puts "MEMORY [getInfo $testNode resources.MEMORY]"
puts "WALLCLOCK [getInfo $testNode resources.WALLCLOCK]"

# Check that loop information is available
puts "===== LOOP INFO FOR $testLoopNode ===== "
set keys [tsv::keylkeys the_shared_var the_keyed_list $testLoopNode.loop]
puts "Keys: $keys"
foreach key $keys {
   puts "value of $key: [getInfo $testLoopNode loop.$key]"
}

# Try getting a sub-keyed-list with the loop info
puts "Loop keyed list [tsv::keylget the_shared_var the_keyed_list $testLoopNode.loop]"




