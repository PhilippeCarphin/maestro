namespace eval Dialogs {
         variable msg
}

proc Dialogs::setDlg {} {
         
	 variable XPM_ApplicationName

	 variable Dlg_NoExpPath
         variable Dlg_NoValExpPath
         variable Dlg_ProvideExpPath
         variable Dlg_ExpPathInList
         variable Dlg_UpdateExpBrowser
         variable Dlg_BrowserUpdated
         variable Dlg_NoAsciiFile
         variable Dlg_DefineExpPath
         variable Dlg_NodeNotExists
	 variable Dlg_TreeNotExists
	 variable Dlg_NonRecognizedPref
	 variable Dlg_ErrorParseConfigOP
	 variable Dlg_PathDeep
	 variable Dlg_DefaultBrowser
	 variable Dlg_DefaultKonsole
	 variable Dlg_ErrorAudit2Exp
	 variable Dlg_AddPath
	 variable Dlg_CreatePath
	 variable Dlg_PathNotOwned
	 variable Dlg_Error_parsing_user_file
	 variable Dlg_NotUnderHOME
	 variable Dlg_DepotNotExist
	 
	 variable Gui_selectedExp
	 variable Gui_ControlExp
	 variable Gui_ExpName
	 variable Gui_ExDatep
	 variable Gui_ExpCatchup

	 variable Nbk_MyExp
	 variable Nbk_OpExp
	 variable Nbk_PaExp
	 variable Nbk_PrExp
	 
	 variable New_ExpTitle
	 variable New_ExpName
	 variable New_ExpSubD
	 variable New_ExpDest
	 variable New_ExpEnMo
	 variable New_Dirs
	 variable New_DirName
	 variable New_Pointto
	 variable New_Parametres
	 
	 variable Aud_title
	 variable Aud_Exp1
	 variable Aud_Exp2
	 variable Aud_button
	 variable Aud_filtre

	 variable Imp_title
	 variable Imp_selected
	 variable Imp_ExpName
	 variable Imp_ExpSubD
	 variable Imp_ExpDest
	 variable Imp_ExpGit
	 variable Imp_Parametres
	 variable Imp_Overwrite
	 variable Imp_Ok
	 variable Imp_Ko
	 variable Imp_NoConstants
	 
	 variable Pref_title
	 variable Pref_depot_title
	 variable Pref_window_size
	 variable Pref_exp_icon
	 variable Pref_wallpaper
	 
	 variable NotB_ExpDepot
	 variable NotB_TextEdit
	 variable NotB_Browsers
	 variable NotB_Konsole
	 variable NotB_Events
	 variable NotB_WallIco

         variable XpB_flowmgr 
         variable XpB_xflow 
         variable XpB_import 
         variable XpB_audit
         variable XpB_exptime
         variable XpB_overv
         variable XpB_xpbrowser
         
	 variable XpB_MyExp
	 variable XpB_OpExp
	 variable XpB_PaExp
	 variable XpB_PoExp
         
	 variable Bug_message
	 variable Bug_title 

         variable All_experience
         
          if {[info exists ::env(CMCLNG)] == 0 || $::env(CMCLNG) == "english" } {
	          set XPM_ApplicationName "Experiment manager"
	          set Dlg_NoExpPath "The Path You provided does not contain any valid Experiments!"
	          set Dlg_NoValExpPath "The Path You provided is not Valid!"
	          set Dlg_ExpPathInList "The Path You provided is already in the list!"
	          set Dlg_UpdateExpBrowser "Do you want to Update the Experiment Browser?"
		  set Dlg_NoAsciiFile "Not An Ascii File"
		  set Dlg_DefineExpPath "Define Your Experiment Depot if you have one: Preferences->SetUp Preferences->Experiments Depot\nor create a New Exp."
		  set Dlg_NodeNotExists "Node Do not Exists !"
		  set Dlg_TreeNotExists "Tree Do Not Exists !"
		  set Dlg_NonRecognizedPref "You have a non-recognized Preference in your  $::env(HOME)/.maestrorc"
		  set Dlg_ErrorParseConfigOP "Please ask CMOI to check the syntax in file ../etc/config/Operational_Exp.cfg"
		  set Dlg_PathDeep "This path is too Deep to look for Experiments"
		  set Dlg_DefaultBrowser "You Default browser has been configured to Firefox"
		  set Dlg_DefaultKonsole "You Default konsole has been configured to xterm"
		  set Dlg_ErrorAudit2Exp "You must give 2 Experiments"
		  set Dlg_AddPath "Your should consider adding another directory level to you path to easely find Experiments" 
		  set Dlg_CreatePath "Directory will be created "
		  set Dlg_Error_parsing_user_file "There is an Error in your ~/.maestrorc file ... please check"
		  set Dlg_PathNotOwned "You ont have the permission to write into this path"
		  set Dlg_BrowserUpdated "Experiment Browser Updated !"
		  set Dlg_NotUnderHOME "Expriment depot must not be directly under \$HOME"
		  set Dlg_DepotNotExist "Your Experiment depot does not exist!"
	          set Gui_selectedExp "Selected Experiment"
	          set Gui_ControlExp "Experiment Control"
	          set Gui_ExpName "Name"
	          set Gui_ExDatep "Date"
	          set Gui_ExpCatchup "Catchup"
	          set Nbk_MyExp "My_Experiments"
	          set Nbk_OpExp "Operational"
	          set Nbk_PaExp "Parallel"
	          set Nbk_PrExp "Pre-operational"
	          set New_ExpTitle "Create New Experiment"
	          set New_ExpName "Experiment Name"
	          set New_ExpSubD "Experiment Sub-directories"
	          set New_ExpDest "Experiment destination path"
	          set New_ExpEnMo "Experiment Entry Module Name"
	          set New_Dirs "Experiment Directories"
	          set New_DirName "Directory name"
	          set New_Pointto "Point to"
	          set New_Parametres "New Experiment Parametres"
	          set Aud_title "Audit Experiments"
	          set Aud_Exp1 "Experiment 1"
	          set Aud_Exp2 "Experiment 2"
	          set Aud_button "Audit All"
		  set Aud_filtre "Filter"
	          set Imp_title "Import One Experiment"
	          set Imp_selected "Experiment to Import"
	          set Imp_ExpName "New Experiment name"
	          set Imp_ExpSubD "Experiment Sub-directories"
	          set Imp_ExpDest "Experiment destination path"
		  set Imp_ExpGit  "Import Git/Constante Files"
	          set Imp_Parametres "Experiment(s) to import"
		  set Imp_NoConstants "There is No Constants files!"
		  set All_experience "Experiment" 
		  set Imp_Overwrite "An experience already exist with this name .Do you want to overwrite it?"
		  set Imp_Ok "Import Succesfull"
		  set Imp_Ko "There are Error in the Import action .. examine listing"
		  set Pref_title "Preferences Setting"
	          set NotB_ExpDepot "Experiments Depot"
	          set NotB_TextEdit "Text Editors"
	          set NotB_Browsers "Browsers"
	          set NotB_Konsole "Konsoles"
	          set NotB_Events  "Events"
	          set NotB_WallIco "Wallpapers and icons"
                  set XpB_flowmgr "Flow manager"
                  set XpB_xflow "Run time flow"
                  set XpB_import "Import"
                  set XpB_audit "Audit with"
                  set XpB_exptime "Exp. Timing"
                  set XpB_overv "Add to Overview"
		  set Bug_message "Launch Bugzilla"
		  set Bug_title "Submit a bug Report"
	          set Pref_window_size "Xflow window size"
	          set Pref_exp_icon "Experiment icon"
	          set Pref_wallpaper "Wallpaper image for Xflow"
		  set Pref_depot_title "Experiments Depot Configuration"
		  set XpB_xpbrowser "Experiment Browser"
	          set XpB_MyExp "My_Experiments"
	          set XpB_OpExp "Operational"
	          set XpB_PaExp "Parallel"
	          set XpB_PoExp "Pre-operational"
		  set Dlg_ProvideExpPath "You must Provide the path of an Experiment"
          } else {
	          set XPM_ApplicationName "Gestionnaire d'experiences"
	          set Dlg_NoExpPath "Le Chemin que vous avez fournis ne contient aucune Experience valide!"
	          set Dlg_NoValExpPath "Le Chemin que vous avez fournis n'est pas Valid!"
	          set Dlg_ExpPathInList "Le Chemin que vous avez fournis est deja dans la liste!"
	          set Dlg_UpdateExpBrowser "Voulez-vous updater le navigateur des Experiences ?"
		  set Dlg_NoAsciiFile "Le fichier n'est pas Ascii"
		  set Dlg_DefineExpPath "Definir Votre depot d'Experiences si vous en avez: Preferences->Configurer les Preferences->Depot des Experiences ou\ncreer une Nouvelle Experience"
		  set Dlg_NodeNotExists "Le noeud n'existe pas !"
		  set Dlg_TreeNotExists "L'arbre n'existe pas !"
		  set Dlg_NonRecognizedPref "Vouz avez une variable de Preference qui n'est pas reconnue dans $::env(HOME)/.maestrorc"
		  set Dlg_ErrorParseConfigOP "SVP demander a CMOI de verifier la syntaxe du fichier ../etc/config/Operational_Exp.cfg"
		  set Dlg_PathDeep "Ce Repertoire est trop profond pour trouver les Experiences"
		  set Dlg_DefaultBrowser "Votre Fureteur par Default a ete configuer a Firefox"
		  set Dlg_DefaultKonsole "Votre konsole par Default a ete configuer a xterm"
		  set Dlg_ErrorAudit2Exp "Vous devez fournir 2 Experiences"
		  set Dlg_AddPath "Vous devriez ajouter un autre repertoire pour faciliter la recherche des experiences" 
		  set Dlg_CreatePath "Le repertoire va etre creer "
		  set Dlg_Error_parsing_user_file "Il y'a une erreure dans votre fichier  ~/.maestrorc  ... svp verifier"
		  set Dlg_PathNotOwned "Vous n'avez pas la permission d'ecrire dans ce repertoire"
		  set Dlg_BrowserUpdated "Le Navigateur d'experiences est mis a jour!"
		  set Dlg_NotUnderHOME "Le depot des Experiences ne doit pas se situer directement sous le \$HOME"
		  set Dlg_DepotNotExist "Votre depot des Experiences n'existe pas!"
	          set Gui_selectedExp "Experience Selectionnee"
	          set Gui_ControlExp "Controls de l'Experience"
	          set Gui_ExpName "Nom"
	          set Gui_ExDatep "Date"
	          set Gui_ExpCatchup "Catchup"
	          set Nbk_MyExp "My_Experiments"
	          set Nbk_OpExp "Operational"
	          set Nbk_PaExp "Parallel"
	          set Nbk_PrExp "Pre-operational"
	          set New_ExpTitle "Creer Une Nouvelle experience"
	          set New_ExpName "Nom de L'experiences"
	          set New_ExpSubD "Sous-repertoires de l'exprience"
	          set New_ExpDest "Chemin de Destination de l'experience"
	          set New_ExpEnMo "Module d'entre de l'experience"
	          set New_Dirs "Repertoires de l'experience"
	          set New_DirName "Nom du repertoire"
	          set New_Pointto "Pointe a"
	          set New_Parametres "Parametres de la nouvelle Experience"
	          set Aud_title "Audit des experiences"
	          set Aud_Exp1 "Experience 1"
	          set Aud_Exp2 "Experience 2"
	          set Aud_button "Audit tous"
		  set Aud_filtre "Filtre"
	          set Imp_title "Importer Une experience"
	          set Imp_selected "Experience a Importer"
	          set Imp_ExpName "Nouveau Nom de l'experience"
	          set Imp_ExpSubD "Sous-repertoire de l'experience"
	          set Imp_ExpDest "Destination de l'experience"
		  set Imp_ExpGit  "Importer Git/Fichiers des constantes"
	          set Imp_Parametres "Experience(s) a Importer"
		  set Imp_NoConstants "Il n'y a pas de fichiers de constantes!"
		  set All_experience "Experience" 
		  set Imp_Overwrite "Une Experience Existe deja avec ce nom. Voudriez vous l'effacer ?"
		  set Imp_Ok "Experience(s) Importe(es) avec succes!"
		  set Imp_Ko "Il y'a des erreurs dans l'operation d'import ... examinez le listing"
		  set Pref_title "Configuration des preferences"
	          set NotB_ExpDepot "Depot des Experiences"
	          set NotB_TextEdit "Editeurs text"
	          set NotB_Browsers "Fureteurs"
	          set NotB_Konsole "Consoles"
	          set NotB_Events  "Evenements"
	          set NotB_WallIco "Fond d'ecran et icones"
                  set XpB_flowmgr "Gestionnaire du flow"
                  set XpB_xflow "Execution du flow"
                  set XpB_import "Importer"
                  set XpB_audit "Audit avec"
                  set XpB_exptime "Temps Exp."
                  set XpB_overv "Ajouter dans l'Overview"
		  set Bug_message "Lancer bugzilla"
		  set Bug_title "Soumettre un bogue"
		  set Pref_depot_title "Configuration du depot des Experiences"
	          set Pref_window_size "Taille d'ecran de Xflow"
	          set Pref_exp_icon "Icone d'une experience"
	          set Pref_wallpaper "Image de fond pour Xflow"
		  set XpB_xpbrowser "Navigateur d'Experiences"
	          set XpB_MyExp "Mes_Experiences"
	          set XpB_OpExp "Operationel"
	          set XpB_PaExp "Parallel"
	          set XpB_PoExp "Pre-operational"
		  set Dlg_ProvideExpPath "Vous devriez fournir le chemin d'une Experience"
	  }
}

#icons --> error, info, question or warning. 
#type -> abortretryignore 3 buttons : abort, retry and ignore.
#        ok
#        okcancel -> 2 but  ok , cnacle
#        retrycancel -> 2 but 
#        yesno    -. 2 but 
#        yesnocancel  -> 3 but 
#        user  -> Displays buttons of -buttons option.
proc Dialogs::show_msgdlg { Mess type icon butt parent } {
    variable msg

    destroy .msgdlg_win
    MessageDlg .msgdlg_win -parent $parent \
        -message $Mess \
        -type    $type \
        -icon    $icon \
        -buttons $butt

}

