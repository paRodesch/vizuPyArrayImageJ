#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 18:19:40 2020

@author: parodesch

N.B: not usif Jython because jython does not exist for python3
"""

import glob
import argparse
import numpy as np
import pydicom

parser = argparse.ArgumentParser(description='read DICOM in selected folder and open coresponding imagej')
parser.add_argument('filename', metavar='path to dicom', type=str, help='h5 file to read', nargs="+")
args = parser.parse_args()

import imagej
ij = imagej.init(headless=False)
ij.getVersion()
ij.ui().showUI()
macro = """ run("Install...", "install=/home/prodesch/Documents/Python/ImageJ/macrosPAR.txt");"""
ij.py.run_macro(macro) 

for index_read,filename in enumerate(args.filename):
    print("Reading Folder " + filename + "\n")
    
    try:
        listDicom = np.sort(glob.glob(filename+'/*.dcm'))
        Nslices = len(listDicom)
        ds = pydicom.dcmread(filename+'/0001.dcm')
        Nx = ds.Columns
        Nz = ds.Rows
        print('---- %d slices found with Matrix %d'%(Nslices,Nx))
        volumeDimensions = np.array([Nx,Nslices,Nz])
        volumeSpacing    = np.array([ds.PixelSpacing[0],float(ds.SliceThickness),ds.PixelSpacing[1]],dtype = np.float32)
        print('---- Voxels size = (%.3f,%.3f) and Slice Thickness = %.3f'%(ds.PixelSpacing[0],ds.PixelSpacing[1],float(ds.SliceThickness)))
        volumeOrigin     = np.array([ds.ImagePositionPatient[0],ds.ImagePositionPatient[2],ds.ImagePositionPatient[1]],dtype = np.float32)
        print('---- Volume Origin is (%.3f,%.3f,%.3f)'%(volumeOrigin[0],volumeOrigin[1],volumeOrigin[2]))
         
        imageArray = np.zeros((Nx,Nslices,Nz))
        for index_slice,value_slice in enumerate(listDicom):
            ds = pydicom.dcmread(value_slice)
            imageArray[:,index_slice,:] = (ds.pixel_array*ds.RescaleSlope+ds.RescaleIntercept).astype(np.float32)
            
        name_Reco = filename.split('/')[-1]
        readingOK = True
    except:
        readingOK = False
        print("\t can't read file " + filename + "\n")
        
        
    if readingOK:
        
        if len(imageArray.shape) == 3:
            volumeOriginVoxel = (np.array(volumeOrigin)//np.array(volumeSpacing)).astype(np.int32)
            width  = volumeDimensions[0]
            height = volumeDimensions[2]
            number = volumeDimensions[1]

            ij.ui().show(filename,ij.py.to_java(np.transpose(imageArray,[1,0,2])))
                
            macro = " "
            macro += """run("Properties...", "channels=1 slices=%d """%number
            macro += """frames=1 pixel_width=%.3f pixel_height=%.3f voxel_depth=%.3f """%(volumeSpacing[0],volumeSpacing[2],volumeSpacing[1])
            macro += """origin=%d,%d,%d");"""%(np.abs(volumeOriginVoxel[0]),np.abs(volumeOriginVoxel[2]),np.abs(volumeOriginVoxel[1]))
            ij.py.run_macro(macro) 
            
            macro = """setSlice(%d);"""%(number//2)
            macro += """run("Brightness/Contrast...");"""
            macro += """run("Enhance Contrast", "saturated=0.35");"""
            ij.py.run_macro(macro)
            
            
ij.py.run_macro(macro)
ij.py.run_macro(""" setTool("hand");""")