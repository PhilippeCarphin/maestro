


global stdin stdout

namespace eval Import {
    
      variable ImportW 
      variable ImportW2
      variable _selected "no-selection"
      variable _ExpDir "no-selection" 
      variable _FromWhere "browser" 
      variable initdir 
      variable post_import
}

proc Import::ImportExp { exp } {
      
      global ListAllExperiments
      
      variable _importGit 
      variable _importCte 
      variable _Makelinks 
      variable ImportCte 
      variable Makelinks 
      variable ImportW 
      variable initdir 
      variable Destination 

      if {[winfo exists .import]} {
              destroy .import
      }
      
      set ImportW [toplevel .import] 
      wm title $ImportW $Dialogs::Imp_title 
      wm minsize $ImportW 600 340

      # -- Initialize 
      set Import::initdir "" 
      set Import::_importGit 0 
      set Import::_Makelinks 0 
      set Import::_importCte 0 

      # -- What if depot is not given
      # -- Get everything for now
      set Import::initdir [Preferences::GetTabListDepots "none" "w"]
      if {[string compare $Import::initdir "" ] == 0 } {
                     set Import::initdir $::env(HOME)/
      }

      set frm [frame .import.frame -border 2 -relief groove]

      set iexp  [TitleFrame $frm.iexp -text $Dialogs::Imp_selected]
      set nexp  [TitleFrame $frm.nexp -text $Dialogs::Imp_ExpName]
      set hexp  [TitleFrame $frm.hexp -text $Dialogs::Imp_ExpSubD]
      set dexp  [TitleFrame $frm.dexp -text $Dialogs::Imp_ExpDest]
      set gexp  [TitleFrame $frm.gexp -text $Dialogs::Imp_ExpGit]

      set subf1 [$iexp getframe]
      set subf2 [$nexp getframe]
      set subf3 [$hexp getframe]
      set subf4 [$dexp getframe]
      set subf5 [$gexp getframe]

      set ImpExpName [ComboBox $subf1.list -textvariable Import::_selected \
                    -width 60 \
		    -autocomplete false \
		    -entrybg  #FFFFFF \
                    -values $ListAllExperiments \
		    -modifycmd "Import::UpdateIMportWidget $subf1 $subf5" \
		    -selectforeground black \
		    -justify left \
		    -insertborderwidth 0 \
		    -hottrack 1 \
		    -helptext "List of Available Experiments"]

      set NewExpName [Entry $subf2.entrys  -textvariable Import::_importname \
                -width 60\
		-bg #FFFFFF \
                -command  "Import::CheckName $subf2.entrys" \
		-helptext "Import Name "]
      
      set ListPath [ComboBox $subf4.list -textvariable Import::Destination \
                    -width 60 \
		    -editable true \
		    -autocomplete false \
		    -entrybg  #FFFFFF \
                    -values $Import::initdir \
		    -modifycmd {} \
		    -selectforeground black \
		    -justify left \
		    -insertborderwidth 0 \
		    -helptext "List of Available Paths"]

      set ImportGit [checkbutton $subf5.radgit -text "Import Git" -font 8 -variable Import::_ImportGit -onvalue 1 -offvalue 0]
      set Makelinks [checkbutton $subf5.radmkl -text "Makelinks after importation" -font 8 -variable Import::_Makelinks -onvalue 1 -offvalue 0]
      set ImportCte [checkbutton $subf5.radcte -text "Copy Constants Locally (MB)" -font 8 -variable Import::_ImportCte -onvalue 1 -offvalue 0 \
                      -command {Import::GetConstantsSize $Import::_selected} ]

      set ImportSize [Entry  $subf5.size -textvariable Import::_Importsize \
                      -width 10\
		      -bg #FFFFFF \
		      -helptext "Total Size of constants to import "]



      set XpBrBut [Button $subf1.but1 -text "..." \
                 -image $XPManager::img_XpSel \
                 -command {
		
		      set xp [tk_chooseDirectory -initialdir $env(HOME)/ -title "Choose a directory" -parent $Import::ImportW]
		      if {$xp ne ""} {
		            # use nativename to resolve tilde expansion
		            set xp [file nativename ${xp}]
			    set kris [catch {file type $xp/EntryModule} ftype]
			    if {$kris != 0} {
			           Dialogs::show_msgdlg $Dialogs::Dlg_ProvideExpPath ok warning "" $Import::ImportW
			    } else {
		                   set Import::_selected $xp
			    }
		      } 
		      }]


      label $frm.lab -text $Dialogs::Imp_title -font "ansi 12 "
      frame $frm.btn -height 2 -borderwidth 1 -relief flat

      set CancelB [button $frm.btn.cancel -text "Cancel" -image $XPManager::img_Cancel -command {destroy $Import::ImportW}]
      set NextB   [button $frm.btn.next   -text "Next"   -image $XPManager::img_Next   -command {\
                                               if { ! [regexp {^[A-Za-z0-9_\-\.]+$} $Import::_importname ]} {
					                 Dialogs::show_msgdlg $Dialogs::Dlg_ExpInvalidName  ok warning "" $Import::ImportW
							 return
					       }
                                               Import::NextButton}]

      set HelpB   [button $frm.btn.help -text "Help" -image $XPManager::img_Help -command {\
                   Dialogs::show_msgdlg "This will Show Help " ok info "" $Import::ImportW}]

      frame $frm.sep1 -height 2 -borderwidth 1 -relief sunken
      frame $frm.sep2 -height 2 -borderwidth 1 -relief sunken


      # -- Pack everything
      pack $frm.lab -fill x

      pack $frm.btn -side bottom
      pack $NextB -side right  -padx 4
      pack $CancelB -side right 
      pack $HelpB -side left 

      pack $frm.sep1 -side bottom -fill x -pady 4

      pack $iexp -anchor w -pady 2 -padx 2
      pack $ImpExpName -side left -padx 4

      if {[string compare $exp ""] == 0} {
               pack $XpBrBut -side left -padx 4
	       set Import::_importname ""
      } else {
              # -- Is User wanting only one Exp.?
	      set kris [catch {file type $exp/EntryModule} ftype]
	      if {$kris == 0 && $ftype eq "link"} {
                      set Import::_importname [file tail $exp] 
              } else {
                      set Import::_importname "" 
	      }
      }


      pack $nexp -anchor w -pady 2 -padx 2
      pack $NewExpName -side left -padx 4

      pack $dexp -anchor w -pady 2 -padx 2
      pack $ListPath -side left -padx 4

      pack $gexp -anchor w -pady 2 -padx 2
      pack $ImportGit -side left -padx 4
      pack $Makelinks -side left -padx 4
      pack $ImportCte -side left -padx 4
      pack $ImportSize -side left -padx 4

      pack $frm -fill x

      # -- Set values
      set Import::_selected $exp
      set Import::_Importsize ""

      # -- deselected 
      $ImportCte deselect

      # -- disable Exp name if not an experiment



}
proc Import::NextButton { } {

      if { $Import::_selected != "" } {
         set Import::_selected [file nativename $Import::_selected]
      }

      if {[string compare $Import::_selected ""] == 0} {
		    Dialogs::show_msgdlg "You Must Choose an Experiment"  ok warning "" $Import::ImportW
		    return
      }

      set Import::Destination [file nativename $Import::Destination]
      if {[regexp {[ \r\n\t]+} $Import::Destination] || [string compare $Import::Destination ""] == 0} {
		    Dialogs::show_msgdlg "You Must give a Valid Destination path"  ok warning "" $Import::ImportW
		    return
      }

      if {[file isdirectory $Import::Destination] == 0 } {
		    Dialogs::show_msgdlg $Dialogs::Dlg_CreatePath  ok warning "" $Import::ImportW
		    if [ catch { exec mkdir -p $Import::Destination } ] {
		                   Dialogs::show_msgdlg "Could not create Directory:$Import::Destination"  ok error "" $Import::ImportW
		     	           return
                    }
                      
       } elseif {[file writable $Import::Destination] == 0 } {
		            Dialogs::show_msgdlg $Dialogs::Dlg_PathNotOwned  ok warning "" $Import::ImportW
			    return
       }

      # Take a detour through the ExpDirectoriesConfig dialog
      NewExp::ExpDirectoriesConfig $Import::ImportW path name entrymod true false $Import::_selected



}


proc Import::GetConstantsSize { selected } {
 # -- If this is Only one exp
 if {[string compare $selected "" ] == 0 } {
		Dialogs::show_msgdlg $Dialogs::Imp_NoExpSel  ok warning "" $Import::ImportW
                $Import::ImportCte deselect
                return
 }
 set kris [catch {file type $selected/EntryModule} ftype]
 if {$kris == 0 && $ftype eq "link"} {
        if {[file exist $selected/hub/constants/]} { 
                 set size [exec du -ms $selected/hub/constants/ | tr \011 \040]
	         set vsize [split $size " "]
	         set Import::_Importsize [lindex $vsize 0]
        } else {
		Dialogs::show_msgdlg $Dialogs::Imp_NoConstants  ok warning "" $Import::ImportW
                $Import::ImportCte deselect
	        set Import::_Importsize 0 
	}
 } else {
	Dialogs::show_msgdlg "For Now the size is not avaliable but you can\nalways en(dis)able the import of constant files" ok warning "" $Import::ImportW
 }
}

proc Import::UpdateIMportWidget { wid1 wid2 } {


      Import::UpdateExpName $wid1.list
      $wid2.radcte deselect
      set Import::_Importsize ""
}

proc Import::ImportNext { win newname srcexp dest git cte arlocation arvalues mklinks} {
      
      upvar  $arlocation arloc
      upvar  $arvalues   arval
      variable ImportW2
     
      if {[winfo exists $win]} {
            destroy $win
      }

      if {[winfo exists .import2]} {
            destroy .import2
      }

      set ImportW2 [toplevel .import2]

      wm title $ImportW2 "$Dialogs::Imp_title : continuing with import ... "
      wm minsize $ImportW2 600 400

      # -- check how Many Exps
      # -- need changes to tclfind to return a list
      set listExp {}

      
      # -- if a multitude of exps
      set kris [catch {file type $srcexp/EntryModule} ftype]
      if {$kris == 0 && $ftype eq "link"} {
             lappend listExp $srcexp
      } else {
             set listExp [XTree::FindExps $srcexp]
      }


      set Ctrlfrm2 [frame $ImportW2.ctrf]

      set dptexp [TitleFrame $Ctrlfrm2.iexp -text $Dialogs::Imp_Parametres]
      set subf [$dptexp getframe]

      set swkt [ScrolledWindow $subf.sw  -relief sunken -borderwidth 1]

      set dpexp [ListBox::create $swkt.lb \
                -relief sunken -borderwidth 1 \
		-dragevent 1 \
		-height 30 \
                -width 70 -highlightthickness 0 -selectmode single -selectforeground black\
		-bg #FFFFFF \
		-padx 25]

      $swkt setwidget $dpexp

      set ButFrame [frame $Ctrlfrm2.bfrm]
      set CancelB2 [button $ButFrame.cancel -text "Cancel"  -command {destroy $Import::ImportW2}]
      set NextB2   [button $ButFrame.next   -text "Proceed" -command [list Import::ExecImport $Import::ImportW2 $newname $srcexp $dest $git $cte $mklinks]]
    

      pack $NextB2   -side right  -padx 5 -pady 5
      pack $CancelB2 -side right  -pady 5

      pack $ButFrame -side bottom 
      pack $dptexp   -fill x
      #pack $dpexp   $subf.ysb  -anchor w
      
      pack $swkt -fill both -expand true
      pack $Ctrlfrm2


      # -- Ok insert xps in list
      foreach exp $listExp {
            $dpexp insert end $exp -text $exp  
      }

      # -- Add info about Name and Git
      # -- Check git
      if { $git == 1 } {
             $dpexp insert end "Git" -text "Import Experiment Git" 
      } else {
             $dpexp insert end "Git" -text "Experiment Git will not be Imported" 
      }

      # -- Check Constants
      if { $cte == 1 } {
             $dpexp insert end "Const" -text "Constants Files will be copied locally" 
      } else {
             $dpexp insert end "Const" -text "Constants will not be Imported ... You must create links to the original constant files." 
      }

      # -- Destination 
      $dpexp insert end "dist" -text "Destination=$dest" 

      if {[string compare "$newname" ""] != 0} {
             $dpexp insert end "Name" -text "Experiment Name will be : $newname " 
      }

      # -- Put linking info in the information dialog
      $dpexp insert end "link" -text "Directory information"
      array set namesWithTabs {
            bin "bin \t\t"
            res "resources\t"
            hub "hub \t\t"
            lis "listings\t\t"
            mod "modules\t"
            seq "sequencing\t"
            log "logs\t\t"
      }
      foreach dir {bin hub res lis log} {
         set dirInfo "   $namesWithTabs($dir): "
         if { [string equal $arloc($dir) "local" ] } {
            append dirInfo "Directory will be copied"
         } else {
            append dirInfo "Link to $arval($dir)"
         }
         $dpexp insert end "$dir linking" -text $dirInfo
      }
      set dirInfo "   $namesWithTabs(seq): "
      if { [string equal $arloc($dir) "local"] } {
         append dirInfo "Empty directory will be created"
      } else {
         append dirInfo "Link to $arval($dir)"
      }
      $dpexp insert end "seq linking" -text $dirInfo

      # -- Write post import script to make the links
      set Import::post_import $::env(TMPDIR)/post_import.sh
      set outfile [open $Import::post_import w+ 0766]
      puts $outfile "#!/bin/ksh"
      puts $outfile "echo \"Redirecting linked directories\""
      foreach dir {bin res mod hub lis log seq} {
         if { [string equal $arloc($dir) "remote" ] } {
            puts $outfile "\necho \"Redirecting $::DirFullName($dir) to $arval($dir)\""
            variable destExpName
            if { [string equal $newname "" ] } {
               set destExpName $Import::_selected
            } else {
               set destExpName $newname
            }
            # Remove directory in new experiment
            puts $outfile "rm -rf $dest/$destExpName/$::DirFullName($dir)"
            # Replace by a link to the path supplied by the user
            puts $outfile "ln -s $arval($dir) $dest/$destExpName/$::DirFullName($dir)"
         }
      }
      close $outfile

      # -- Warn if User will have dangling links in his xp.
      set i 0
      set tsrcexp [exec true_path -n $srcexp]
      foreach exp $listExp {
	  # Find links under ExpHome
	  foreach lnk [glob -nocomplain -type {l r} -path $exp/ *] {
		set compo [file tail $lnk]
		if {[string equal $compo "EntryModule"]} {
		      continue
		}
		# -- check if link point to local (under experiment path)
		set truepath [exec true_path -n $lnk]
		if {[string first $tsrcexp $truepath] == -1} {
                         $dpexp insert end "warnbase$i" -text "WARNING: Under Experiment:$exp $compo is a link pointing outside of experiment" -fill red
		         incr i
		}
	  }
	  # Find links under modules if modules is directory
	  set ftype  [file type $exp/modules]
	  if {[string compare $ftype "directory"] == 0 } {
	       foreach lnk [glob -nocomplain -type {l r} -path $exp/modules/ *] {
		         set compo [file tail $lnk]
		         # -- check if link point to local (under experiment path)
		         set truepath [exec true_path -n $lnk]
		         if {[string first $tsrcexp $truepath] == -1} {
                                  $dpexp insert end "warnmod$i" -text "WARNING: Under modules:$exp/modules  $compo is a link pointing outside of experiment" -fill red 
			          incr i
                         }
		}
          }
      }

}

proc Import::UpdateExpName { widgt } {
       set nom [file tail [$widgt get]]
       set Import::_importname $nom
}

proc Import::CheckName { widgt } {

     set Name [$widgt get]
     
     # -- validated by the Enter command
     if { ! [regexp {^[A-Za-z0-9_\-\.]+$} $Name]} {
              Dialogs::show_msgdlg $Dialogs::Dlg_ExpInvalidName  ok warning "" $Import::::ImportW
              return
     }

}


proc Import::ExecImport {win newname srcexp dest git cte mklinks} {
      
      global MAESTRO_BIN

      variable ExeImport
      variable ERROR  0
      variable SUCCES 0

      if {[winfo exists $win]} {
             destroy $win
      }

      if {[winfo exists .execimport]} {
               destroy .execimport
      }

      set ExeImport [toplevel .execimport] 
      wm title $ExeImport "$Dialogs::Imp_title : proceed with the import ... "
      wm minsize $ExeImport 600 200

      set frm [frame $ExeImport.ctrf]
      set scrolledW [ScrolledWindow ${frm}.scroll_w -relief sunken -borderwidth 1] 

      set WinInfoWidget [text $frm.txt -xscrollcommand "$frm.xscroll set" -yscrollcommand "$frm.yscroll set"  \
                         -width 80 -height 30 -bg #FFFFFF -font 12 -wrap word]
      
      ${scrolledW} setwidget ${WinInfoWidget}

      set CancelB  [button $frm.cancel -text "Quit" -bg gray -command {destroy $Import::ExeImport}]

      pack ${scrolledW} -fill both -expand true -padx 5 -pady 5
      pack  $CancelB -padx 5 -pady 5
      pack $frm -fill both -expand true 



      
      $WinInfoWidget insert end "New Name=$newname \n"
      $WinInfoWidget insert end "Source=$srcexp \n"
      $WinInfoWidget insert end "Destination=$dest \n"

      set ImportScript "${MAESTRO_BIN}/import_maestro_exp"

      if { $git == 1 } {
              set arg_git "-g"
      } else {
              set arg_git ""
      }
      
      if { $cte == 1 } {
              set arg_cte ""
      } else {
              set arg_cte "-c"
      }
  
      if { $mklinks == 1 } {
              set arg_mklinks "-m"
      } else {
              set arg_mklinks ""
      }

      # -- Notes : import will put the target name of link 
      if {[string compare "$newname" ""] != 0 } {
		set cmdargs "-s $srcexp -d $dest/$newname -n $arg_git $arg_cte $arg_mklinks"
      } else {
		set cmdargs "-s $srcexp -d $dest $arg_git $arg_cte $arg_mklinks"
      }
      
      $WinInfoWidget insert end "cmd:import_maestro_exp $cmdargs\n"

      update 
      if [ catch {
         ${WinInfoWidget} configure -cursor watch
      
         set fid [open "|$ImportScript $cmdargs 2>@ stdout" r+]

         fconfigure $fid -buffering line -translation auto 
         fileevent  $fid readable "Import::GetImportScriptOutputs $fid $WinInfoWidget $ExeImport"
      } message ] {
         ${ExeImport} configure -cursor {}
         error ${message}
      }      

      
 
}

proc Import::GetImportScriptOutputs {fid Winfo win} {

      if [ catch {
         if {[gets $fid line] >= 0 } {

		$Winfo insert end "$line \n"
		$Winfo see end

		if {[regexp  {Overwrite} $line]} {
		         set ret [Dialogs::show_msgdlg $Dialogs::Imp_Overwrite  yesno question "" $win] 
			 if { $ret == 0 } {
		               puts $fid "y"
                         } else {
		               puts $fid "n"
			 }
			 flush $fid
		} elseif {[regexp {(error|ERROR)} $line]} {
		         set Import::ERROR 1
			
		} elseif {[regexp {Done importing} $line]} {
		         set Import::SUCCES 1
			
		} elseif {[regexp {Import[ +]Cancelled} $line]} {
		         close $fid
			 return
		}

         } else {
                close $fid
		if { $Import::SUCCES == 1 } {
		         Dialogs::show_msgdlg $Dialogs::Imp_Ok  ok info "" $win]

         # Run post import script
         # (Replace some directories by links)
         set postFid [open "|$Import::post_import 2>@ stdout" r+]

			 # Refresh exp browser window
			 set nbk [$XpBrowser::notebook raise]
			 set listxp [Preferences::GetTabListDepots $nbk "r"]
			 XTree::reinit $::TreesWidgets([string trim $nbk " "])  {*}$listxp
		} else  {
		         Dialogs::show_msgdlg $Dialogs::Imp_Ko  ok warning "" $win] 
		}
                ${Winfo} configure -cursor {}
         }
      } message ] {
         ${Winfo} configure -cursor {}
         error ${message}
      }

}


