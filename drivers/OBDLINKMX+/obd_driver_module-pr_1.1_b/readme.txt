*********************************************************************
   OBD Driver Module, Rev 1.1/B
   Copyright (C) 2013 OBD Solutions, All Rights Reserved
*********************************************************************


======================================
============== Contents ==============
======================================

   eagle_files			Contains the EAGLE source files
   assy.gbr			Top assembly drawing (Gerber RS-274X)
   bom.xls			Bill of materials
   mount.mnt			SMD centroid file (XYRS)
   obd_driver_module.pdf	PDF of the schematic
   pcb.zip			Main PCB production files
   readme.txt			This file


======================================
=============== Notes ================
======================================

 - The gerber files provided are viewed from the top side.
 - Hole sizes are the finished hole sizes.
 - Excellon Format: 1.4 Leading, Absolute, Imperial
 - The board should be routed to the outline in fab.gbr


======================================
========= Revision History ===========
======================================

Rev 1.0	- David D (2012.10.27)
	  Initial release

Rev 1.1 - Jason (2013.09.17)
	  Connected all VOUT pins of regulator,reversed ISO comparator inputs
	  Updated PCB Rev to B