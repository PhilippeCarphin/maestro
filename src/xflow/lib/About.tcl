proc About_show { parent } {
   global env
   set topW .abouttop
   destroy ${topW}
   toplevel ${topW}
   Utils_positionWindow ${topW} ${parent} 
   wm title ${topW} "About Xflow"

   # create text widget
   set scrolledW [ScrolledWindow ${topW}.sw]
   set textW [text ${scrolledW}.txt -wrap word -height 15 -relief flat -width 75]

   ${scrolledW} setwidget ${textW}

   set maestroVersion "unknown"
   if { [info exists env(SEQ_MAESTRO_VERSION)] } {
      set maestroVersion $env(SEQ_MAESTRO_VERSION)
   }
   ${textW} insert end "\n\nMaestro version: ${maestroVersion}" BOLD_TXT

   ${textW} insert end "\n\nMaestro resources and training:\n" BOLD_TXT

   # should create an app properties file in next version
   set docUrl "https://wiki.cmc.ec.gc.ca/wiki/Maestro"

   set docLabel [label ${textW}.doc_label -text ${docUrl} -fg blue]
   ${textW} window create end -window ${docLabel}

   bind ${docLabel} <Double-Button-1> [list Utils_goBrowser ${docUrl}]
    
   ${textW} configure -state disabled
   pack ${scrolledW} -fill both -expand yes -padx 5 -pady 5 -ipadx 2 -ipady 2
}

