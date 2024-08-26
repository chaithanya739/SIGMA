import math
import scipy as sp
import numpy as np
import multiprocessing as mp
from multiprocessing import Pool
from multiprocessing import Pool
from scipy.sparse import random
from scipy import stats
from numpy.random import default_rng
import os
#Initialization of number of multipliers per each DPE (which is processing element in SIGMA terms), total cycles determine the total number of cycles required for the total processing.
global No_of_multiplier_perDPE,totalcycle 
No_of_multiplier_perDPE = 4 # Number of multipliers per DPE is initialized to four.
totalcycle=0

sparse_matrix = sp.io.mmread('M10PI_n1.mtx') #loading the suite sparse matrix.
Stationary = sparse_matrix.toarray().astype(int) 
Streaming = Stationary



class FlexDPU_multiplier:
    def __init__(self,stationary_holder) -> None: # this meant that init should always return none
        self.stationary_holder = stationary_holder
    def multiplier(self,streaming):
        multiplier_result =self.stationary_holder * streaming
        return multiplier_result

def src_dest_pair(bitmap_Stationary_useful,bitmap_Streaming,Stationary_per_flex_DPU,non_zeroes_Streaming,non_zeroes_Stationary_entire,totalcycle):
    totalcycle = totalcycle + (len(bitmap_Streaming[0])*len(bitmap_Stationary_useful))
    count_stationary = 0 # to make the counter for the stationary as demonstrated in the paper
    count_streaming = 0
    count_placement = 0
    Mul_utilization = 0
    count_placement_per_flex_DPE = []
    #print("non_zeroes_Streaming_peppepeee",non_zeroes_Streaming)
    Flex_DPE_table = []
    PE_utilization = [0 for i in range(No_of_FlexDPE)]
    #print(PE_utilization)
    
    for j in range(len(bitmap_Streaming[0])): #no of rows of streaming matrix. Imagine the diagram in SIGMA where the stationary is and corresponding streamings has to parallelized since we cannot do that in Python we are using loops   
        totalcycle = totalcycle+2
        totalcycle = totalcycle+No_of_FlexDPE
    print("total",totalcycle)
    for j in range(len(bitmap_Streaming[0])): #no of rows of streaming matrix. Imagine the diagram in SIGMA where the stationary is and corresponding streamings has to parallelized since we cannot do that in Python we are using loops   
        count_streaming = 0
        count_stationary = 0
        multiplier_results = []
        for i in range(len(bitmap_Stationary_useful)): #no of coulumns of streaming matrix
            count_streaming = 0
            for k in range(len(bitmap_Stationary_useful[0])):
                if ((count_stationary%No_of_multiplier_perDPE == 0) and count_stationary !=0):
                    count_placement_per_flex_DPE.append(count_placement) ## will be used in step vi
                    count_placement = 0
                if (bitmap_Stationary_useful[i][k] == 1):
                    count_stationary = count_stationary+1
                
                if ((bitmap_Stationary_useful[i][k] and bitmap_Streaming[k][j])==1):
                    current_Flex_DPE = ((count_stationary-1)//No_of_multiplier_perDPE) # this count is different from count_stationary this count provides us the which FlexDPE
                    PE_utilization[current_Flex_DPE] = PE_utilization[current_Flex_DPE]  + 1
    for i in range(len(PE_utilization)):    
        Mul_utilization = Mul_utilization+PE_utilization[i]/((len(bitmap_Streaming[0])*No_of_multiplier_perDPE))
    
    if len(PE_utilization) == 0:
        print ("Mul_utilization", 0)
    else:
        print("Mul_utilization",Mul_utilization/(len(PE_utilization)*totalcycle))
    return totalcycle


def NumberofFlexDPE(non_zeroes_Stationary, Stationary_useful,Stationary_useles,totalcycle): #step iii
    Stationary_per_flex_DPU = []
    count = 0
    count_per_DPE = 0
    cycle_count_inside_flexDPE = 0
    for i in range (len(Stationary_useful)):  #This is the only parallelizing loop
        count = 0
        for j in range(len(Stationary_useful[i])): # cycle count = j
            cycle_count_inside_flexDPE = cycle_count_inside_flexDPE + 1
            if (Stationary_useful[i][j] == 0 and Stationary_useles[i][j] !=0):
                count = count+1
                del non_zeroes_Stationary[i][count-1]

            if(Stationary_useful[i][j] != 0 and Stationary_useles[i][j] !=0):
                count = count + 1
    cycle_count_inside_flexDPE = cycle_count_inside_flexDPE/len(Stationary_useful)
    totalcycle = totalcycle + cycle_count_inside_flexDPE

    non_zeroes_Stationary_entire = []
    for i in range(len(non_zeroes_Stationary)):
        for j in range(len(non_zeroes_Stationary[i])):
            non_zeroes_Stationary_entire.append(non_zeroes_Stationary[i][j])
    No_of_FlexDPE = math.ceil(len(non_zeroes_Stationary_entire)/No_of_multiplier_perDPE)
    for i in range(No_of_FlexDPE): # here we don't how many cycle count we should take for now lets suppose it 1
        Stationary_per_flex_DPU.append(non_zeroes_Stationary_entire[count_per_DPE : count_per_DPE+No_of_multiplier_perDPE])
        count_per_DPE = (count_per_DPE + No_of_multiplier_perDPE-1)+1
    
    totalcycle = totalcycle + No_of_FlexDPE
    #print("non_zeroes_Stationary_entire", len(non_zeroes_Stationary_entire))
    print("No_of flex DPE",No_of_FlexDPE)
    return Stationary_per_flex_DPU, No_of_FlexDPE, non_zeroes_Stationary_entire,totalcycle



def uselesselimination(bitmap_Stationary, bitmap_Streaming, totalcycle): #step ii ## only bitmap elements are eliminated and the non_zero elements are being eliminated in Number of Flex DPE
    Streaming_REGOR = []
    bitmap_Stationary_new = []
    REGOR_temp = 0    # this loop implements the Stationary matrix of step2 This will take only one cycle as they are executed in parallel.
    for i in range(len(bitmap_Streaming)):
        REGOR_temp = 0
        for j in range(len(bitmap_Streaming[0])):
            totalcycle = totalcycle+1
            REGOR_temp = REGOR_temp or bitmap_Streaming[i][j]
        Streaming_REGOR.append(REGOR_temp)
    
    
    for i in range(len(bitmap_Stationary)):
        bitmap_Stationary_temp_fornew = []
        for j in range(len(Streaming_REGOR)):
            bitmap_Stationary_temp_fornew.append(Streaming_REGOR[j] and bitmap_Stationary[i][j])
        bitmap_Stationary_new.append(bitmap_Stationary_temp_fornew)
    totalcycle = totalcycle + len(bitmap_Stationary)
    return bitmap_Stationary_new, totalcycle

def non_zeroes_per_row(A,bitmap_A):
    count=0
    non_zero_per_row = []
    for i in range(len(bitmap_A)):
        non_zero_per_row_temp = []
        for j in range(len(bitmap_A[0])):
            if(bitmap_A[i][j] != 0):
                non_zero_per_row_temp.append(A[count])
                count=count+1
        non_zero_per_row.append(non_zero_per_row_temp)
    return non_zero_per_row



def bitmap_generator(A): ##normal bitmap generator
    rows= len(A)
    columns = len(A[0])
    Bitmap_A = [[0]*columns for i in range(rows)]
    non_zero_A = []

    #for bitmap conversion
    for i in range(len(A)):
        for j in range(len(A[i])):
            if A[i][j] != 0:
                Bitmap_A[i][j] = 1

            else:
                Bitmap_A[i][j] = 0

    #for non zero in bitmap conversion
    for i in range(len(A)):
        for j in range(len(A[i])):
            if A[i][j] != 0:
                non_zero_A.append(A[i][j])

    
    return non_zero_A, Bitmap_A

def nonzero_columnwise(A):
    rows= len(A)
    columns = len(A[0])
    Bitmap_A = [[0]*columns for i in range(rows)]
    non_zero_A = []

    #for bitmap conversion
    for i in range(len(A)):
        for j in range(len(A[i])):
            if A[i][j] != 0:
                Bitmap_A[i][j] = 1

            else:
                Bitmap_A[i][j] = 0

    #for non zero in bitmap conversion
    for j in range(len(A[i])):
        for i in range(len(A)):
            if A[i][j] != 0:
                non_zero_A.append(A[i][j])

    
    return non_zero_A

def Transpose(B):
    rows = len(B)
    columns = len(B[0])
    Col_stor = [[0]*rows for i in range(columns)]
    for j in range(columns):
        for i in range(rows):
            Col_stor[j][i] = B[i][j]
    
    return Col_stor
print(totalcycle)

non_zeroes_Stationary, bitmap_Stationary = bitmap_generator(Stationary)
non_zeroes_Streaming, bitmap_Streaming = bitmap_generator(Streaming)
#print("There are non_zeroes_Stationary, bitmap_Stationary\n",non_zeroes_Stationary, bitmap_Stationary)
non_zeroes_Stationary_per_row= non_zeroes_per_row(non_zeroes_Stationary,bitmap_Stationary)
non_zeroes_column_Streaming = nonzero_columnwise(Streaming)
bitmap_streaming_transpose = Transpose(bitmap_Streaming)
non_zeroes_column_Streaming_per_row = non_zeroes_per_row(non_zeroes_column_Streaming,bitmap_streaming_transpose)


bitmap_Stationary_useful, totalcycle = uselesselimination(bitmap_Stationary,bitmap_Streaming, totalcycle) #step ii
Stationary_per_flex_DPU,No_of_FlexDPE, non_zeroes_Stationary_entire, totalcycle = NumberofFlexDPE(non_zeroes_Stationary_per_row,bitmap_Stationary_useful,bitmap_Stationary, totalcycle) #step iii
src_dest_pair(bitmap_Stationary_useful,bitmap_Streaming,Stationary_per_flex_DPU,non_zeroes_column_Streaming_per_row,non_zeroes_Stationary_entire,totalcycle) #step iv
