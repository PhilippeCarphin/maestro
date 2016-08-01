#!/users/dor/afsi/phc/Testing/testdomain/linux26-x86-64/bin/tclsh


package require Thread

proc readNodeinfoDB { } {

   # Normally, generating this info file would be done when quitting the GUI
   # after changing the experiment.  But for testing purposes, I do it here, and
   # the rest of the function is going to stay.
   exec ../mtest > nodeinfo_keyedlist.tsv

   # Read the file 
   set fp [open nodeinfo_keyedlist.tsv]
   set data_list [read $fp]
   close $fp

   # Temporary, show the content
   puts $data_list

   # Read the content of the file into a keyed list.
   tsv::keylset the_shared_var the_keyed_list {*}$data_list

}

proc getCPU { nodeName } {
   return [tsv::keylget the_shared_var the_keyed_list $nodeName.resources.CPU]
}


proc getResource { nodeName resource } {
   return [tsv::keylget the_shared_var the_keyed_list $nodeName.resources.$resource]
}

proc getInfo { nodeName subkey } {
   return [tsv::keylget the_shared_var the_keyed_list $nodeName.$subkey]
}


readNodeinfoDB

set nodeName /sample_module/Different_Hosts/I.have.aperiod.in.my.name
set value [tsv::keylget the_shared_var the_keyed_list $nodeName.resources.CPU]
puts "resources.CPU of $nodeName : $value"
set value [tsv::keylget the_shared_var the_keyed_list $nodeName.depends.depname1]
puts "depends.depname1 of $nodeName : $value"

set value [getCPU $nodeName]

puts "Value using wrapper function : $value"

set value [getResource $nodeName CPU]
puts "Value using general wrapper function : $value"

set value [getInfo $nodeName resources.CPU]
puts "Value using super wrapper function : $value"

puts "==== INFO FOR $nodeName ===="
puts "CATCHUP [getInfo $nodeName resources.CATCHUP]"
puts "CPU [getInfo $nodeName resources.CPU]"
puts "QUEUE [getInfo $nodeName resources.QUEUE]"
puts "MPI [getInfo $nodeName resources.MPI]"
puts "MEMORY [getInfo $nodeName resources.MEMORY]"
puts "WALLCLOCK [getInfo $nodeName resources.WALLCLOCK]"


set nodeName /sample_module/Loop_Examples/outerloop/innerloop
puts "===== LOOP INFO FOR $nodeName ===== "
set keys [tsv::keylkeys the_shared_var the_keyed_list $nodeName.loop]
puts "Keys: $keys"
foreach key $keys {
   puts "value of $key: [getInfo $nodeName loop.$key]"
}
puts "Loop keyed list [tsv::keylget the_shared_var the_keyed_list $nodeName.loop]"

# proc getLoopInfo




