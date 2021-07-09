#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 18:19:40 2020

@author: parodesch

N.B: not usif Jython because jython does not exist for python3
"""

import os
import argparse
import itk 
import numpy as np

parser = argparse.ArgumentParser(description='Convert conventional folder and open coresponding imagej')
parser.add_argument('filename', metavar='path to dicom', type=str, help='h5 file to read', nargs="+")
args = parser.parse_args()

import imagej
ij = imagej.init(headless=False)
ij.getVersion()
ij.ui().showUI()
macro = """ run("Install...", "install=/home/prodesch/Documents/Python/ImageJ/macrosPAR.txt");"""
ij.py.run_macro(macro) 

for index_read,filename in enumerate(args.filename):
    print("Reading file " + filename + "\n")
    try:
        imageItk = itk.imread(filename)
        readingOK = True
    except:
        readingOK = False
        print("\t can't read file " + filename + "\n")
        
        
    if readingOK:
        
        imageArray = itk.GetArrayFromImage(imageItk)
        if len(imageArray.shape)== 2:
            volumeDimensions = imageItk.GetLargestPossibleRegion().GetSize()
            volumeSpacing    = imageItk.GetSpacing()
            volumeOrigin     = imageItk.GetOrigin()
            volumeOriginVoxel = (np.array(volumeOrigin)//np.array(volumeSpacing)).astype(np.int32)
            width  = volumeDimensions[0]
            height = volumeDimensions[1]
            
            ij.ui().show(filename,ij.py.to_java(imageArray))
                
            macro = " "
            macro += """run("Properties...", "channels=1 slices=1 """
            macro += """frames=1 pixel_width=%.3f pixel_height=%.3f voxel_depth=1 """%(volumeSpacing[0],volumeSpacing[1])
            macro += """origin=%d,%d");"""%(-1*volumeOriginVoxel[0],-1*volumeOriginVoxel[1])
            ij.py.run_macro(macro) 
            
            macro = """run("Brightness/Contrast...");"""
            macro += """run("Enhance Contrast", "saturated=0.35");"""
            ij.py.run_macro(macro)
            
        elif len(imageArray.shape)== 3:
            volumeDimensions = imageItk.GetLargestPossibleRegion().GetSize()
            volumeSpacing    = imageItk.GetSpacing()
            volumeOrigin     = imageItk.GetOrigin()
            volumeOriginVoxel = (np.array(volumeOrigin)//np.array(volumeSpacing)).astype(np.int32)
            width  = volumeDimensions[0]
            height = volumeDimensions[2]
            number = volumeDimensions[1]

            ij.ui().show(filename,ij.py.to_java(np.transpose(imageArray,[1,0,2])))
                
            macro = " "
            macro += """run("Properties...", "channels=1 slices=%d """%number
            macro += """frames=1 pixel_width=%.3f pixel_height=%.3f voxel_depth=%.3f """%(volumeSpacing[0],volumeSpacing[2],volumeSpacing[1])
            macro += """origin=%d,%d,%d");"""%(-1*volumeOriginVoxel[0],-1*volumeOriginVoxel[2],-1*volumeOriginVoxel[1])
            ij.py.run_macro(macro) 
            
            macro = """setSlice(%d);"""%(number//2)
            macro += """run("Brightness/Contrast...");"""
            macro += """run("Enhance Contrast", "saturated=0.35");"""
            ij.py.run_macro(macro)
            
        elif len(imageArray.shape)== 4:
            volumeDimensions = imageItk.GetLargestPossibleRegion().GetSize()
            volumeSpacing    = imageItk.GetSpacing()
            volumeOrigin     = imageItk.GetOrigin()
            volumeOriginVoxel = (np.array(volumeOrigin)//np.array(volumeSpacing)).astype(np.int32)
            width  = volumeDimensions[0]
            height = volumeDimensions[2]
            number = volumeDimensions[1]

            nMaterials = imageArray.shape[3]
            
            for index_mat in range(nMaterials):
                ij.ui().show(filename+"-Material %d"%(index_mat+1),ij.py.to_java(np.transpose(imageArray[:,:,:,index_mat],[1,0,2])))
                
                macro = " "
                macro += """run("Properties...", "channels=1 slices=%d """%number
                macro += """frames=1 pixel_width=%.3f pixel_height=%.3f voxel_depth=%.3f """%(volumeSpacing[0],volumeSpacing[2],volumeSpacing[1])
                macro += """origin=%d,%d,%d");"""%(-1*volumeOriginVoxel[0],-1*volumeOriginVoxel[2],-1*volumeOriginVoxel[1])
                ij.py.run_macro(macro)
                
            macro = """ run("Concatenate...", "  title=%s open"""%filename
            for index_mat in range(nMaterials):
                macro+= """ image%d=[%s]"""%(index_mat+1,filename+"-Material %d"%(index_mat+1))
            macro+= """");"""
            ij.py.run_macro(macro)
            
            macro = """setSlice(%d);"""%(number//2)
            macro += """run("Brightness/Contrast...");"""
            macro += """run("Enhance Contrast", "saturated=0.35");"""
            ij.py.run_macro(macro)
            
ij.py.run_macro(macro)
ij.py.run_macro(""" setTool("hand");""")